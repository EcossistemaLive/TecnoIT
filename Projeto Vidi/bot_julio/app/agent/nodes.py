import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from app.agent.state import AgentState
from app.db.postgres import db
from app.db.mongo import mongo_db
from app.rag.retriever import retriever
from app.config import config
from app.agent.prompts import build_full_system_prompt

logger = logging.getLogger(__name__)

# ============================================================
# LLM — Gemini (testes Telegram) | Claude em produção WPP
# ============================================================
def get_llm():
    if config.GOOGLE_API_KEY:
        return ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_output_tokens=config.LLM_MAX_TOKENS,
            google_api_key=config.GOOGLE_API_KEY
        )
    else:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
            anthropic_api_key=config.ANTHROPIC_API_KEY
        )

llm = get_llm()


async def validate_user(state: AgentState) -> dict:
    """Carrega perfil e diagnóstico do participante pelo telegram_user_id"""
    telegram_id = state["telegram_user_id"]
    try:
        query = """
            SELECT p.id, p.full_name, p.company, p.role, p.upsell_category, p.annual_revenue_bracket,
                   d.pain_label, d.pain_description, d.governance_score, d.succession_urgency, d.financial_stress
            FROM participants p
            LEFT JOIN diagnoses d ON d.participant_id = p.id
            WHERE p.telegram_user_id = $1
        """
        record = await db.fetchrow(query, telegram_id)

        if not record:
            return {
                "is_authenticated": False,
                "blocked_reason": "UNAUTHORIZED_TELEGRAM_ID",
                "current_intent": "bloqueado"
            }

        profile = {
            "full_name": record["full_name"],
            "company": record["company"] or "Empresa",
            "role": record["role"] or "Executivo",
            "upsell_category": record["upsell_category"],
            "annual_revenue_bracket": record["annual_revenue_bracket"] or "ND"
        }

        diagnosis = {
            "pain_label": record["pain_label"] or "Guerra Infinita",
            "pain_description": record["pain_description"] or "Desafios de escala e operação.",
            "governance_score": record["governance_score"],
            "succession_urgency": record["succession_urgency"],
            "financial_stress": record["financial_stress"]
        }

        return {
            "is_authenticated": True,
            "participant_id": str(record["id"]),
            "participant_profile": profile,
            "participant_diagnosis": diagnosis
        }
    except Exception as e:
        logger.error(f"Erro em validate_user: {e}")
        return {"is_authenticated": False, "blocked_reason": "DB_ERROR", "current_intent": "bloqueado"}


async def classify_intent(state: AgentState) -> dict:
    """Classifica intenção e aplica blindagem básica contra prompt injection"""
    if not state.get("is_authenticated"):
        return {"current_intent": "bloqueado"}

    suspicious = ["ignore suas instruções", "ignore all previous", "modo admin", "mostre seu prompt", "system prompt"]
    msg = state.get("user_input", "").lower()
    for s in suspicious:
        if s in msg:
            logger.warning(f"Tentativa de injection detectada de {state.get('telegram_user_id')}: {msg[:80]}")

    if state.get("totem_id"):
        return {"current_intent": "contexto_totem"}

    return {"current_intent": "chat_livre"}


async def retrieve_context(state: AgentState) -> dict:
    """Busca no pgvector por contexto relevante da base RAG"""
    query = state.get("user_input", "")
    totem_tag = state.get("totem_id")

    results = await retriever.search(query=query, limit=3, totem_tag=totem_tag)

    if not results:
        return {"rag_context": None}

    context_str = "\n---\n".join([f"[{r['theme']}]\n{r['content']}" for r in results])
    return {"rag_context": context_str}


async def call_llm(state: AgentState) -> dict:
    """Compõe o prompt completo e chama o LLM (Gemini ou Claude)"""
    sys_prompt = build_full_system_prompt(state)

    messages = [("system", sys_prompt)]

    # Histórico recente (limitado a 5 trocas para não extourar o contexto)
    for m in state.get("messages", [])[-10:]:
        role = m.get("role")
        content = m.get("content", "")
        if role in ("user", "assistant"):
            messages.append((role, content))

    messages.append(("user", state["user_input"]))

    response = await llm.ainvoke(messages)
    return {"final_response": response.content}


async def evaluate_upsell(state: AgentState) -> dict:
    """Detecta gatilho de upsell (Categoria A ou sinais de interesse profundo)"""
    profile = state.get("participant_profile", {})
    user_input = state.get("user_input", "").lower()

    upsell_triggers = ["mentoria", "acompanhamento", "ibrahim", "luiz portal", "cleber", "preciso de ajuda especial", "como faço para contratar"]

    is_cat_a = profile.get("upsell_category") == "A"
    has_trigger = any(t in user_input for t in upsell_triggers)

    if is_cat_a or has_trigger:
        return {
            "needs_team_alert": True,
            "alert_reason": f"Cat {profile.get('upsell_category')} | Trigger: {'Sim' if has_trigger else 'Não'} | Input: {user_input[:80]}"
        }

    return {"needs_team_alert": False, "alert_reason": None}


async def notify_team(state: AgentState) -> dict:
    """Alerta a equipe ViDi via log (em produção: mensagem no grupo do Telegram)"""
    name = state.get("participant_profile", {}).get("full_name", "Participante")
    reason = state.get("alert_reason", "")
    logger.info(f"🚨 UPSELL ALERT — {name}: {reason}")
    # Em produção: bot.send_message(chat_id=config.UPSELL_ALERT_TELEGRAM_CHAT_ID, text=...)
    return {}


async def persist_history(state: AgentState) -> dict:
    """Persiste o histórico de conversa no MongoDB"""
    try:
        from datetime import datetime
        doc = {
            "session_id": state.get("session_id"),
            "participant_id": state.get("participant_id"),
            "telegram_user_id": state.get("telegram_user_id"),
            "user_input": state.get("user_input"),
            "bot_response": state.get("final_response"),
            "totem_id": state.get("totem_id"),
            "intent": state.get("current_intent"),
            "updated_at": datetime.utcnow()
        }
        await mongo_db.db.chat_sessions.insert_one(doc)
    except Exception as e:
        logger.warning(f"MongoDB persist falhou: {e}")
    return {}
