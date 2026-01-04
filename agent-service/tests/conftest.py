"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app
from src.models.state import AgentSummary, GraphState, ToDo


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_graph_state() -> GraphState:
    """Sample GraphState for testing."""
    return {
        "supervisor": {
            "task_id": "test-task-123",
            "context_id": None,
            "status": "RUNNING",
            "plan": [],
            "history": [],
            "notes": "Test task notes",
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }


@pytest.fixture
def sample_todo() -> ToDo:
    """Sample ToDo for testing."""
    return {
        "id": "todo-123",
        "description": "Test task description",
        "status": "PENDING",
        "owner_agent": "research_agent",
    }


@pytest.fixture
def sample_agent_summary() -> AgentSummary:
    """Sample AgentSummary for testing."""
    return {
        "agent_name": "research_agent",
        "step_id": "step-123",
        "result": "COMPLETED",
        "short_summary": "Completed research task",
        "key_decisions": ["Decision 1", "Decision 2"],
        "next_instructions_for_supervisor": "Route to transform_agent",
    }


@pytest.fixture
def mock_tool_call():
    """Mock tool call response."""

    class MockToolCall:
        def __init__(self):
            self.name = "show_approval_card"
            self.args = {
                "title": "Test Approval",
                "description": "Test description",
                "options": ["Approve", "Reject"],
            }
            self.id = "tool-call-123"

        def get(self, key, default=None):
            return getattr(self, key, default)

        def __getitem__(self, key):
            return getattr(self, key)

    return MockToolCall()


@pytest.fixture
def graph_state_with_tool_call(sample_graph_state, mock_tool_call) -> GraphState:
    """GraphState with a pending tool call."""
    state = sample_graph_state.copy()
    state["supervisor"]["pending_tool_call"] = {
        "agent": "research_agent",
        "tool": mock_tool_call.name,
        "args": mock_tool_call.args,
        "tool_call_id": mock_tool_call.id,
    }
    return state
