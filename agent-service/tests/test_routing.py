from src.graph.workflow import route_after_agent, route_after_supervisor
from src.models.state import GraphState


def test_route_to_finalizer_when_done():
    """Test routing to finalizer when status is DONE."""
    state: GraphState = {
        "supervisor": {
            "status": "DONE",
            "plan": [],
            "history": [],
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    next_node = route_after_supervisor(state)
    assert next_node == "finalizer"


def test_route_to_active_agent():
    """Test routing to active_agent when set."""
    state: GraphState = {
        "supervisor": {
            "status": "RUNNING",
            "plan": [],
            "history": [],
            "active_agent": "research_agent",
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    next_node = route_after_supervisor(state)
    assert next_node == "research_agent"


def test_route_back_to_supervisor_when_no_active_agent():
    """Test routing back to supervisor when active_agent is None."""
    state: GraphState = {
        "supervisor": {
            "status": "RUNNING",
            "plan": [],
            "history": [],
            "active_agent": None,
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    next_node = route_after_supervisor(state)
    assert next_node == "supervisor"


def test_agent_routes_back_to_supervisor():
    """Test that agents route back to supervisor."""
    state: GraphState = {
        "supervisor": {
            "status": "RUNNING",
            "plan": [],
            "history": [],
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    next_node = route_after_agent(state)
    assert next_node == "supervisor"
