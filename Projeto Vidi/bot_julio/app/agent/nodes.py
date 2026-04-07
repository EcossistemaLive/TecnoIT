import logging
import anthropic

from app.agent.state import AgentState
from app.db.postgres import db
from app.rag.retriever import retriever
from app.config import config
from app.agent.prompts import build_full_system_prompt

logger = logging.getLogger(__name__)

# ============================================================
# LLM — Gemini (primário, Cat. B e C) + Claude (upsell Cat. A)
# ============================================================
try:
    import google.generativeai as genai
    genai.configure(api_key=config.GOOGLE_API_KEY)
    _gemini_model = genai.GenerativeModel(config.GEMINI_MODEL)
    _use_gemini = True
except Exception as e:
    logger.warning(f"Gemini indisponível, usando Mock: {e}")
    _gemini_model = None
    _use_gemini = False

try:
    _anthropic_client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
    _use_claude = True
except Exception as e:
    logger.warning(f"Claude indisponível: {e}")
    _anthropic_client = None
    _use_claude = False


async def validate_user(state: AgentState) -> dict:
    """Carrega perfil e diagnóstico do participante pelo número WhatsApp."""
    phone = state["user_id"]
    try:
        query = """
            SELECT p.id, p.full_name, p.company, p.role, p.upsell_category, p.annual_revenue_bracket,
                   p.user_type, p.has_event_access,
                   d.pain_label, d.pain_description, d.governance_score, d.succession_urgency, d.financial_stress
            FROM participants p
            LEFT JOIN diagnoses d ON d.participant_id = p.id
            WHERE p.whatsapp_phone = $1
        """
        record = await db.fetchrow(query, phone)

        if not record:
            return {
                "is_authenticated": False,
                "blocked_reason": "UNAUTHORIZED_PHONE",
                "current_intent": "bloqueado",
            }

        user_type = record["user_type"] or "participant"
        has_event_access = record["has_event_access"] if record["has_event_access"] is not None else True

        profile = {
            "full_name": record["full_name"],
            "company": record["company"] or "Empresa",
            "role": record["role"] or "Executivo",
            "upsell_category": record["upsell_category"],
            "annual_revenue_bracket": record["annual_revenue_bracket"] or "ND",
        }

        diagnosis = {
            "pain_label": record["pain_label"] or "Guerra Infinita",
            "pain_description": record["pain_description"] or "Desafios de escala e operação.",
            "governance_score": record["governance_score"],
            "succession_urgency": record["succession_urgency"],
            "financial_stress": record["financial_stress"],
        }

        return {
            "is_authenticated": True,
            "participant_id": str(record["id"]),
            "participant_profile": profile,
            "participant_diagnosis": diagnosis,
            "user_type": user_type,
            "has_event_access": has_event_access,
        }
    except Exception as e:
        logger.error(f"Erro em validate_user: {e}")
        return {"is_authenticated": False, "blocked_reason": "DB_ERROR", "current_intent": "bloqueado"}


async def classify_intent(state: AgentState) -> dict:
    """Classifica intenção e aplica blindagem básica contra prompt injection."""
    if not state.get("is_authenticated"):
        return {"current_intent": "bloqueado"}

    suspicious = [
        "ignore suas instruções", "ignore all previous",
        "modo admin", "mostre seu prompt", "system prompt",
        "esqueça o que foi dito", "forget previous", "novo papel",
        "act as", "pretend you are", "jailbreak",
    ]
    msg = state.get("user_input", "").lower()
    for s in suspicious:
        if s in msg:
            logger.warning(f"Tentativa de injection detectada de {state.get('user_id')}: {msg[:80]}")
            return {
                "current_intent": "bloqueado",
                "blocked_reason": "INJECTION_ATTEMPT",
            }

    if state.get("totem_id"):
        return {"current_intent": "contexto_totem"}

    return {"current_intent": "chat_livre"}


async def retrieve_context(state: AgentState) -> dict:
    """Busca no pgvector por contexto relevante da base RAG, filtrado por user_type."""
    query = state.get("user_input", "")
    totem_tag = state.get("totem_id")
    user_type = state.get("user_type", "participant")
    has_event_access = state.get("has_event_access", True)

    results = await retriever.search(
        query=query,
        limit=3,
        totem_tag=totem_tag,
        user_type=user_type,
        has_event_access=has_event_access,
    )

    if not results:
        return {"rag_context": None}

    context_str = "\n---\n".join([f"[{r['theme']}]\n{r['content']}" for r in results])
    return {"rag_context": context_str}


async def call_llm(state: AgentState) -> dict:
    """Compõe o prompt completo e chama o LLM."""
    sys_prompt = build_full_system_prompt(state)
    user_input = state["user_input"]

    # Histórico recente (últimas 5 trocas = 10 mensagens)
    history = state.get("messages", [])[-10:]

    profile = state.get("participant_profile", {})
    upsell_cat = profile.get("upsell_category", "B")

    # Cat. A → Claude (resposta premium de upsell)
    if upsell_cat == "A" and _use_claude and _anthropic_client:
        try:
            messages = []
            for m in history:
                role = m.get("role")
                content = m.get("content", "")
                if role in ("user", "assistant"):
                    messages.append({"role": role, "content": content})
            messages.append({"role": "user", "content": user_input})

            response = await _anthropic_client.messages.create(
                model=config.LLM_MODEL,
                max_tokens=config.LLM_MAX_TOKENS,
                temperature=config.LLM_TEMPERATURE,
                system=sys_prompt,
                messages=messages,
            )
            return {"final_response": response.content[0].text}
        except Exception as e:
            logger.error(f"[call_llm] Claude ERRO — {type(e).__name__}: {e}")

    # Cat. B/C → Gemini Flash (primário)
    if _use_gemini and _gemini_model:
        try:
            history_str = ""
            if history:
                lines = []
                for m in history:
                    role = m.get("role")
                    content = m.get("content", "")
                    if role == "user":
                        lines.append(f"Executivo: {content}")
                    elif role == "assistant":
                        lines.append(f"Júlio: {content}")
                if lines:
                    history_str = "\n[Histórico da conversa]\n" + "\n".join(lines) + "\n"
            full_prompt = f"{sys_prompt}{history_str}\nExecutivo agora: {user_input}"
            response = await _gemini_model.generate_content_async(full_prompt)
            return {"final_response": response.text}
        except Exception as e:
            logger.error(f"[call_llm] Gemini ERRO — {type(e).__name__}: {e}")

    # Fallback mock
    user_lower = user_input.lower()
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


async def evaluate_upsell(state: AgentState) -> dict:
    """Detecta gatilho de upsell ou interesse de lead com base no user_type."""
    profile = state.get("participant_profile", {})
    user_input = state.get("user_input", "").lower()
    user_type = state.get("user_type", "participant")

    # Staff: nunca gera alerta de upsell
    if user_type == "staff":
        return {"needs_team_alert": False, "alert_reason": None}

    # Lead: alerta de interesse (funil diferente)
    if user_type == "lead":
        lead_interest_triggers = [
            "quero participar", "como faço", "inscrição", "próximo passo",
            "ibrahim", "luiz portal", "cúpula", "evento", "interesse",
            "me conta mais", "quero saber mais",
        ]
        has_interest = any(t in user_input for t in lead_interest_triggers)
        if has_interest:
            return {
                "needs_team_alert": True,
                "alert_reason": (
                    f"LEAD_INTEREST | "
                    f"Nome: {profile.get('full_name', 'Lead')} | "
                    f"Input: {user_input[:80]}"
                ),
            }
        return {"needs_team_alert": False, "alert_reason": None}

    # Participant e Mentored: lógica de upsell padrão
    upsell_triggers = [
        "mentoria", "acompanhamento", "ibrahim", "luiz portal",
        "preciso de ajuda especial", "como faço para contratar",
    ]

    is_cat_a = profile.get("upsell_category") == "A"
    has_trigger = any(t in user_input for t in upsell_triggers)

    if is_cat_a or has_trigger:
        return {
            "needs_team_alert": True,
            "alert_reason": (
                f"UPSELL | Cat {profile.get('upsell_category')} | "
                f"Trigger: {'Sim' if has_trigger else 'Não'} | "
                f"Input: {user_input[:80]}"
            ),
        }

    return {"needs_team_alert": False, "alert_reason": None}


async def notify_team(state: AgentState) -> dict:
    """Alerta a equipe ViDi via WhatsApp (admin)."""
    from app.whatsapp_handlers.sender import send_whatsapp_message
    from app.config import config

    name = state.get("participant_profile", {}).get("full_name", "Participante")
    reason = state.get("alert_reason", "")
    msg = f"🚨 ALERTA UPSELL\nParticipante: {name}\n{reason}"

    logger.info(f"[UPSELL ALERT] {name}: {reason}")

    if config.ADMIN_WHATSAPP:
        try:
            await send_whatsapp_message(config.ADMIN_WHATSAPP, msg)
        except Exception as e:
            logger.error(f"Falha ao enviar alerta admin: {e}")

    return {}


async def persist_history(state: AgentState) -> dict:
    """Persiste o histórico de conversa no PostgreSQL."""
    try:
        from datetime import datetime, timezone
        await db.execute(
            """
            INSERT INTO chat_history
                (session_id, participant_id, user_phone, user_input, bot_response,
                 totem_id, intent, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT DO NOTHING
            """,
            state.get("session_id"),
            state.get("participant_id"),
            state.get("user_id"),
            state.get("user_input"),
            state.get("final_response"),
            state.get("totem_id"),
            state.get("current_intent"),
            datetime.now(timezone.utc),
        )
    except Exception as e:
        logger.warning(f"persist_history falhou (tabela pode não existir ainda): {e}")
    return {}
