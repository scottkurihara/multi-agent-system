import logging

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..models.state import GraphState
from ..nodes.finalizer import finalizer_node
from ..nodes.supervisor import supervisor_node

logger = logging.getLogger(__name__)


def route_after_supervisor(state: GraphState) -> str:
    """Route after supervisor node based on status and active_agent."""
    status = state["supervisor"].get("status")

    if status == "DONE":
        logger.debug("Routing to finalizer (status=DONE)")
        return "finalizer"

    if status == "ESCALATE":
        logger.warning("Routing to hitl_escalation (status=ESCALATE)")
        return "hitl_escalation"

    active_agent = state["supervisor"].get("active_agent")
    if active_agent:
        # Validate that the active_agent is a valid route
        # In the refactored architecture, sub-agents are called as tools,
        # not as separate nodes, so active_agent should always be None
        logger.warning(
            f"Active agent '{active_agent}' requested but sub-agents are now tools. "
            "Routing to finalizer instead."
        )
        return "finalizer"

    logger.debug("Routing back to supervisor")
    return "supervisor"


def route_after_agent(state: GraphState) -> str:
    """Route back to supervisor after agent execution."""
    logger.debug("Agent completed, routing back to supervisor")
    return "supervisor"


def create_graph():
    """Create and compile the LangGraph workflow."""
    logger.info("Creating agent workflow graph")
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("finalizer", finalizer_node)
    logger.debug("Added 2 nodes to workflow: supervisor, finalizer")

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Add conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "supervisor": "supervisor",
            "finalizer": "finalizer",
            "hitl_escalation": END,
        },
    )

    # Finalizer goes to END
    workflow.add_edge("finalizer", END)

    # Compile with checkpointer
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    logger.info("Workflow graph compiled successfully")

    return app
