import operator
from typing import Annotated, Sequence, TypedDict


class AgentState(TypedDict):
    """
    Representação do estado do LangGraph para o Bot Júlio (WhatsApp).
    """
    # Identificação da sessão e mensagem atual
    session_id: str
    user_id: str          # número WhatsApp (phone)
    user_input: str

    # Perfil e Contexto do participante
    participant_id: str
    participant_profile: dict   # name, company, role, upsell_category, etc.
    participant_diagnosis: dict # pain_label, pain_description, score

    # Modo de atendimento
    user_type: str       # 'lead' | 'participant' | 'mentored' | 'staff'
    has_event_access: bool  # True se tem acesso ao conteúdo do evento (relevante para mentorados)

    # Contexto Situacional (Totem) e RAG
    totem_id: str | None
    rag_context: str | None

    # Memória de conversação
    messages: Annotated[Sequence[dict], operator.add]

    # Controle de Roteamento (LangGraph State)
    current_intent: str  # 'chat_livre', 'contexto_totem', 'alerta_humano', 'bloqueado'

    # Segurança
    is_authenticated: bool
    blocked_reason: str | None

    # Output final do LLM
    final_response: str | None

    # Controle de alerta de Upsell
    needs_team_alert: bool
    alert_reason: str | None

    # Campo auxiliar de prompt renderizado
    system_prompt_rendered: str | None
