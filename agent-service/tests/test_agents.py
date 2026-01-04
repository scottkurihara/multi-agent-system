"""Tests for agent nodes with tool calling."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.nodes.research_agent import research_agent_node
from src.nodes.transform_agent import transform_agent_node


@pytest.mark.asyncio
async def test_research_agent_handles_no_tasks(sample_graph_state):
    """Test research agent handles case with no assigned tasks."""
    result = await research_agent_node(sample_graph_state)

    assert result["supervisor"]["active_agent"] is None
    assert len(result["supervisor"]["history"]) == 1

    summary = result["supervisor"]["history"][0]
    assert summary["agent_name"] == "research_agent"
    assert summary["result"] == "COMPLETED"
    assert "No tasks assigned" in summary["short_summary"]


@pytest.mark.asyncio
async def test_transform_agent_handles_no_tasks(sample_graph_state):
    """Test transform agent handles case with no assigned tasks."""
    result = await transform_agent_node(sample_graph_state)

    assert result["supervisor"]["active_agent"] is None
    assert len(result["supervisor"]["history"]) == 1

    summary = result["supervisor"]["history"][0]
    assert summary["agent_name"] == "transform_agent"
    assert summary["result"] == "COMPLETED"
    assert "No tasks assigned" in summary["short_summary"]


@pytest.mark.asyncio
async def test_research_agent_processes_pending_task(sample_graph_state, sample_todo):
    """Test research agent processes a pending task."""
    # Add a pending task for research_agent
    sample_todo["owner_agent"] = "research_agent"
    sample_todo["status"] = "PENDING"
    sample_graph_state["supervisor"]["plan"] = [sample_todo]

    # Mock the LLM response
    mock_response = Mock()
    mock_response.content = '{"agent_name": "research_agent", "step_id": "123", "result": "COMPLETED", "short_summary": "Task completed", "key_decisions": [], "next_instructions_for_supervisor": "Continue"}'
    mock_response.tool_calls = None

    with patch("src.nodes.research_agent.ChatAnthropic") as mock_llm_class:
        mock_llm = Mock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm

        result = await research_agent_node(sample_graph_state)

    # Check that task was marked as DONE
    updated_plan = result["supervisor"]["plan"]
    assert updated_plan[0]["status"] == "DONE"

    # Check that summary was added to history
    assert len(result["supervisor"]["history"]) == 1


@pytest.mark.asyncio
async def test_transform_agent_processes_pending_task(sample_graph_state, sample_todo):
    """Test transform agent processes a pending task."""
    # Add a pending task for transform_agent
    sample_todo["owner_agent"] = "transform_agent"
    sample_todo["status"] = "PENDING"
    sample_graph_state["supervisor"]["plan"] = [sample_todo]

    # Mock the LLM response
    mock_response = Mock()
    mock_response.content = '{"agent_name": "transform_agent", "step_id": "123", "result": "COMPLETED", "short_summary": "Task completed", "key_decisions": [], "next_instructions_for_supervisor": "Continue"}'
    mock_response.tool_calls = None

    with patch("src.nodes.transform_agent.ChatAnthropic") as mock_llm_class:
        mock_llm = Mock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm

        result = await transform_agent_node(sample_graph_state)

    # Check that task was marked as DONE
    updated_plan = result["supervisor"]["plan"]
    assert updated_plan[0]["status"] == "DONE"


@pytest.mark.asyncio
async def test_research_agent_calls_ui_tool(sample_graph_state, sample_todo, mock_tool_call):
    """Test research agent can call a UI tool."""
    # Add a pending task for research_agent
    sample_todo["owner_agent"] = "research_agent"
    sample_todo["status"] = "PENDING"
    sample_graph_state["supervisor"]["plan"] = [sample_todo]

    # Mock the LLM response with tool call
    mock_response = Mock()
    mock_response.tool_calls = [mock_tool_call]

    with patch("src.nodes.research_agent.ChatAnthropic") as mock_llm_class:
        mock_llm = Mock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm

        result = await research_agent_node(sample_graph_state)

    # Check that tool call was stored in state
    assert "pending_tool_call" in result["supervisor"]
    tool_call = result["supervisor"]["pending_tool_call"]

    assert tool_call["agent"] == "research_agent"
    assert tool_call["tool"] == "show_approval_card"
    assert "args" in tool_call
    assert "tool_call_id" in tool_call

    # Check that tool event was added to agent state
    tool_events = result["agent"]["tool_events"]
    assert len(tool_events) == 1
    assert tool_events[0]["type"] == "tool_call"
    assert tool_events[0]["agent"] == "research_agent"


@pytest.mark.asyncio
async def test_transform_agent_calls_ui_tool(sample_graph_state, sample_todo, mock_tool_call):
    """Test transform agent can call a UI tool."""
    # Add a pending task for transform_agent
    sample_todo["owner_agent"] = "transform_agent"
    sample_todo["status"] = "PENDING"
    sample_graph_state["supervisor"]["plan"] = [sample_todo]

    # Mock the LLM response with tool call
    mock_response = Mock()
    mock_response.tool_calls = [mock_tool_call]

    with patch("src.nodes.transform_agent.ChatAnthropic") as mock_llm_class:
        mock_llm = Mock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm

        result = await transform_agent_node(sample_graph_state)

    # Check that tool call was stored in state
    assert "pending_tool_call" in result["supervisor"]
    tool_call = result["supervisor"]["pending_tool_call"]

    assert tool_call["agent"] == "transform_agent"
    assert tool_call["tool"] == "show_approval_card"


@pytest.mark.asyncio
async def test_agent_handles_malformed_json_response(sample_graph_state, sample_todo):
    """Test that agent handles malformed JSON in LLM response."""
    # Add a pending task
    sample_todo["owner_agent"] = "research_agent"
    sample_todo["status"] = "PENDING"
    sample_graph_state["supervisor"]["plan"] = [sample_todo]

    # Mock response with malformed JSON
    mock_response = Mock()
    mock_response.content = "This is not valid JSON"
    mock_response.tool_calls = None

    with patch("src.nodes.research_agent.ChatAnthropic") as mock_llm_class:
        mock_llm = Mock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm

        result = await research_agent_node(sample_graph_state)

    # Check that a FAILED summary was created
    history = result["supervisor"]["history"]
    assert len(history) == 1
    assert history[0]["result"] == "FAILED"
    assert "Failed to parse" in history[0]["short_summary"]


@pytest.mark.asyncio
async def test_agent_increments_recursion_depth(sample_graph_state, sample_todo):
    """Test that agents increment recursion depth."""
    initial_depth = sample_graph_state["agent"]["recursion_depth"]

    result = await research_agent_node(sample_graph_state)

    assert result["agent"]["recursion_depth"] == initial_depth + 1
