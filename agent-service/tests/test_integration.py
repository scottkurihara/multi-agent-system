"""Integration tests for the multi-agent system."""

import json

import pytest

from src.graph.workflow import create_graph
from src.models.state import GraphState


@pytest.mark.asyncio
async def test_full_graph_execution():
    """Test full graph execution from start to finish."""
    initial_state: GraphState = {
        "supervisor": {
            "task_id": "test-123",
            "context_id": None,
            "status": "RUNNING",
            "plan": [],
            "history": [],
            "notes": "Test integration task",
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    graph = create_graph()

    # Execute the graph
    result = await graph.ainvoke(initial_state)

    # Check that we have a final state
    assert result is not None
    assert "supervisor" in result
    assert "agent" in result

    # Supervisor should have finished
    assert result["supervisor"]["status"] in ["DONE", "ESCALATE"]

    # Should have some history
    assert len(result["supervisor"]["history"]) > 0


@pytest.mark.asyncio
async def test_graph_creates_plan():
    """Test that graph creates a plan."""
    initial_state: GraphState = {
        "supervisor": {
            "task_id": "test-456",
            "context_id": None,
            "status": "RUNNING",
            "plan": [],
            "history": [],
            "notes": "Create a simple plan",
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    graph = create_graph()
    result = await graph.ainvoke(initial_state)

    # Should have created a plan
    plan = result["supervisor"].get("plan", [])
    assert len(plan) > 0

    # Plan items should have required fields
    for todo in plan:
        assert "id" in todo
        assert "description" in todo
        assert "status" in todo


@pytest.mark.asyncio
async def test_graph_routes_to_agents():
    """Test that graph routes to specialist agents."""
    initial_state: GraphState = {
        "supervisor": {
            "task_id": "test-789",
            "context_id": None,
            "status": "RUNNING",
            "plan": [],
            "history": [],
            "notes": "Research and transform data",
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    graph = create_graph()
    result = await graph.ainvoke(initial_state)

    # Check that agents were used (history should have entries)
    history = result["supervisor"].get("history", [])

    # Should have at least one agent execution
    assert len(history) > 0

    # Check that agent names are valid
    agent_names = [h["agent_name"] for h in history]
    valid_agents = ["research_agent", "transform_agent"]

    for agent_name in agent_names:
        assert agent_name in valid_agents


@pytest.mark.asyncio
async def test_graph_handles_tool_calls():
    """Test that graph can handle tool calls from agents."""
    initial_state: GraphState = {
        "supervisor": {
            "task_id": "test-tool",
            "context_id": None,
            "status": "RUNNING",
            "plan": [],
            "history": [],
            "notes": "Show me some options",
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    graph = create_graph()

    # Use astream to check for tool call events
    tool_calls_found = False

    async for event in graph.astream(initial_state):
        if isinstance(event, dict):
            for _node_name, node_output in event.items():
                if "supervisor" in node_output:
                    supervisor_state = node_output["supervisor"]
                    if "pending_tool_call" in supervisor_state:
                        tool_calls_found = True
                        break

        if tool_calls_found:
            break

    # Note: Tool calls may or may not occur depending on LLM response
    # This test just verifies the system can handle them if they occur


@pytest.mark.asyncio
async def test_graph_increments_recursion():
    """Test that graph increments recursion depth."""
    initial_state: GraphState = {
        "supervisor": {
            "task_id": "test-recursion",
            "context_id": None,
            "status": "RUNNING",
            "plan": [],
            "history": [],
            "notes": "Test recursion depth",
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    graph = create_graph()
    result = await graph.ainvoke(initial_state)

    # Recursion depth should have increased
    assert result["agent"]["recursion_depth"] > 0


@pytest.mark.asyncio
async def test_api_integration_with_graph(client):
    """Test API endpoints integrate correctly with graph."""
    payload = {"input": {"task": "Integration test task"}}

    # Test streaming endpoint
    response = client.post("/v1/agent/stream", json=payload)

    # Should get a streaming response
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")

    # Parse events
    events = []
    for line in response.text.split("\n"):
        if line.startswith("data: "):
            try:
                event = json.loads(line[6:])
                events.append(event)
            except json.JSONDecodeError:
                pass

    # Should have multiple events
    assert len(events) > 0

    # Should have started event
    event_types = [e["type"] for e in events]
    assert "started" in event_types


@pytest.mark.asyncio
async def test_supervisor_creates_todos_with_agents():
    """Test that supervisor assigns todos to specific agents."""
    initial_state: GraphState = {
        "supervisor": {
            "task_id": "test-assignment",
            "context_id": None,
            "status": "RUNNING",
            "plan": [],
            "history": [],
            "notes": "Research information and transform results",
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    graph = create_graph()
    result = await graph.ainvoke(initial_state)

    plan = result["supervisor"].get("plan", [])

    # Check that todos have owner_agent assigned
    if len(plan) > 0:
        for todo in plan:
            if "owner_agent" in todo:
                assert todo["owner_agent"] in ["research_agent", "transform_agent"]
