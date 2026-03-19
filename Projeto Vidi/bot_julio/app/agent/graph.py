from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    validate_user,
    classify_intent,
    retrieve_context,
    call_llm,
    evaluate_upsell,
    notify_team,
    persist_history
)

def create_agent_graph():
    """Constrói e compila o StateGraph do LangGraph."""
    workflow = StateGraph(AgentState)

    # 1. Adicionar os Nós
    workflow.add_node("validate_user", validate_user)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("evaluate_upsell", evaluate_upsell)
    workflow.add_node("notify_team", notify_team)
    workflow.add_node("persist_history", persist_history)
    
    # 2. Definir Ponto de Entrada
    workflow.set_entry_point("validate_user")

    # 3. Adicionar Arestas e Condicionais
    def check_auth(state: AgentState):
        if not state.get("is_authenticated"):
            return "bloqueado"
        return "classificar"

    # Se validate_user falhar, vai pro fim (bloqueado)
    workflow.add_conditional_edges(
        "validate_user",
        check_auth,
        {
            "bloqueado": END,
            "classificar": "classify_intent"
        }
    )

    # De classificar, todos vão puxar contexto RAG do evento
    workflow.add_edge("classify_intent", "retrieve_context")
    workflow.add_edge("retrieve_context", "call_llm")
    
    # Apos LLM responder, avaliamos upsell em paralelo com persistencia
    workflow.add_edge("call_llm", "evaluate_upsell")
    workflow.add_edge("call_llm", "persist_history")
    
    # De Evaluate Upsell, decide se alerta a equipe
    def check_upsell(state: AgentState):
        if state.get("needs_team_alert"):
            return "notificar"
        return "fim"
        
    workflow.add_conditional_edges(
        "evaluate_upsell",
        check_upsell,
        {
            "notificar": "notify_team",
            "fim": END
        }
    )
    
    workflow.add_edge("notify_team", END)
    workflow.add_edge("persist_history", END)

    # Compilar Grafo
    return workflow.compile()

# Instância global do grafo copilado
app_graph = create_agent_graph()
