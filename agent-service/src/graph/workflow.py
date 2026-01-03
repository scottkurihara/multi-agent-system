from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from ..models.state import GraphState
from ..nodes.supervisor import supervisor_node
from ..nodes.research_agent import research_agent_node
from ..nodes.transform_agent import transform_agent_node
from ..nodes.finalizer import finalizer_node


def route_after_supervisor(state: GraphState) -> str:
    """Route after supervisor node based on status and active_agent."""
    status = state["supervisor"].get("status")

    if status == "DONE":
        return "finalizer"

    if status == "ESCALATE":
        return "hitl_escalation"

    active_agent = state["supervisor"].get("active_agent")
    if active_agent:
        return active_agent

    return "supervisor"


def route_after_agent(state: GraphState) -> str:
    """Route back to supervisor after agent execution."""
    return "supervisor"


def create_graph():
    """Create and compile the LangGraph workflow."""
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research_agent", research_agent_node)
    workflow.add_node("transform_agent", transform_agent_node)
    workflow.add_node("finalizer", finalizer_node)

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Add conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "supervisor": "supervisor",
            "research_agent": "research_agent",
            "transform_agent": "transform_agent",
            "finalizer": "finalizer",
            "hitl_escalation": END,
        },
    )

    # Add conditional edges from agents back to supervisor
    workflow.add_conditional_edges(
        "research_agent",
        route_after_agent,
        {"supervisor": "supervisor"},
    )

    workflow.add_conditional_edges(
        "transform_agent",
        route_after_agent,
        {"supervisor": "supervisor"},
    )

    # Finalizer goes to END
    workflow.add_edge("finalizer", END)

    # Compile with checkpointer
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    return app
