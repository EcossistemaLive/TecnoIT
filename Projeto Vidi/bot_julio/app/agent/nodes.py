import logging
from langchain_anthropic import ChatAnthropic
from app.agent.state import AgentState
from app.db.postgres import db
from app.db.mongo import mongo_db
from app.rag.retriever import retriever
from app.config import config
from app.agent.prompts import build_full_system_prompt

logger = logging.getLogger(__name__)

# ============================================================
# LLM — Claude (Anthropic) com fallback para Mock
# ============================================================
try:
    llm = ChatAnthropic(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
        anthropic_api_key=config.ANTHROPIC_API_KEY
    )
    _use_mock = False
except Exception as e:
    import logging as _log
    _log.getLogger(__name__).warning(f"Claude indisponivel, usando Mock: {e}")
    llm = None
    _use_mock = True


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
    """Compõe o prompt completo e chama o LLM (Mock)"""
    sys_prompt = build_full_system_prompt(state)

    messages = [("system", sys_prompt)]

    # Histórico recente (limitado a 5 trocas para não extourar o contexto)
    for m in state.get("messages", [])[-10:]:
        role = m.get("role")
        content = m.get("content", "")
        if role in ("user", "assistant"):
            messages.append((role, content))

    messages.append(("user", state["user_input"]))

    if _use_mock or llm is None:
        user_lower = state["user_input"].lower()
        if any(w in user_lower for w in ["quando", "evento", "data", "horário"]):
            resp = "A Cúpula CEO 2026 será um evento transformador. Os detalhes finais de agenda estão sendo definidos. Quer saber mais sobre os temas?"
        elif any(w in user_lower for w in ["mentor", "ibrahim", "luiz", "cleber"]):
            resp = "Os mentores da Cúpula são referências nacionais em escala empresarial. Vou sinalizar seu interesse para a equipe."
        elif any(w in user_lower for w in ["fazer", "ajudar", "dor", "desafio", "problema"]):
            resp = "Entendo seu desafio. Na Cúpula conectamos você com especialistas que já passaram por isso. Qual é seu principal gargalo?"
        elif any(w in user_lower for w in ["sucessão", "governança", "gestão"]):
            resp = "Sucessão e governança são pilares da Cúpula CEO. Temos cases reais de empresas que escalaram com essa estrutura."
        elif any(w in user_lower for w in ["financeiro", "caixa", "crédito", "fidc"]):
            resp = "Arsenal Financeiro é um dos temas centrais. Discutimos FIDC e alternativas ao crédito bancário tradicional."
        elif any(w in user_lower for w in ["internacional", "exportação", "zona franca"]):
            resp = "Internacionalização via Zonas Francas reduz carga tributária significativamente. Posso detalhar mais?"
        else:
            resp = "Ótima pergunta! Esse é exatamente o tipo de tema que abordamos na Cúpula CEO 2026. Qual é seu principal interesse?"
        return {"final_response": resp}

    try:
        response = await llm.ainvoke(messages)
        return {"final_response": response.content}
    except Exception as e:
        logger.error(f"[call_llm] ERRO LLM — {type(e).__name__}: {e}")
        return {"final_response": "Um momento, estou verificando as informações. Pode repetir?"}


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
    logger.info(f"[UPSELL ALERT] {name}: {reason}")
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
