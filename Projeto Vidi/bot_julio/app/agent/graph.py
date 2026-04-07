from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    validate_user,
    classify_intent,
    retrieve_context,
    call_llm,
    evaluate_upsell,
    notify_team,
    persist_history,
)


def create_agent_graph():
    """Constrói e compila o StateGraph do LangGraph."""
    workflow = StateGraph(AgentState)

    # Nós
    workflow.add_node("validate_user", validate_user)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("evaluate_upsell", evaluate_upsell)
    workflow.add_node("notify_team", notify_team)
    workflow.add_node("persist_history", persist_history)

    # Ponto de entrada
    workflow.set_entry_point("validate_user")

    # Fluxo principal
    def check_auth(state: AgentState):
        return "classificar" if state.get("is_authenticated") else "bloqueado"

    workflow.add_conditional_edges(
        "validate_user",
        check_auth,
        {"bloqueado": END, "classificar": "classify_intent"},
    )

    workflow.add_edge("classify_intent", "retrieve_context")
    workflow.add_edge("retrieve_context", "call_llm")

    # Após LLM: avalia upsell e persiste histórico em paralelo
    workflow.add_edge("call_llm", "evaluate_upsell")
    workflow.add_edge("call_llm", "persist_history")

    def check_upsell(state: AgentState):
        return "notificar" if state.get("needs_team_alert") else "fim"

    workflow.add_conditional_edges(
        "evaluate_upsell",
        check_upsell,
        {"notificar": "notify_team", "fim": END},
    )

    workflow.add_edge("notify_team", END)
    workflow.add_edge("persist_history", END)

    return workflow.compile()


app_graph = create_agent_graph()
