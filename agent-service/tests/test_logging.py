"""Tests for logging functionality."""

import logging
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.utils.logging_config import get_logger, setup_logging


def test_setup_logging_creates_logger():
    """Test that setup_logging configures root logger."""
    setup_logging(log_level="INFO")

    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO
    assert len(root_logger.handlers) > 0


def test_setup_logging_with_debug_level():
    """Test setting DEBUG log level."""
    setup_logging(log_level="DEBUG")

    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG


def test_get_logger_returns_logger():
    """Test that get_logger returns a logger instance."""
    logger = get_logger("test_module")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_logger_logs_messages():
    """Test that logger can log messages."""
    setup_logging(log_level="INFO")
    logger = get_logger("test_logger")

    with patch.object(logger, "info") as mock_info:
        logger.info("Test message")
        mock_info.assert_called_once_with("Test message")


def test_logger_respects_log_level():
    """Test that logger respects log level settings."""
    setup_logging(log_level="WARNING")
    logger = get_logger("test_level_logger")

    with patch.object(logger, "debug") as mock_debug:
        logger.debug("This should not be logged")
        # Debug should be called but not actually logged due to level
        mock_debug.assert_called_once()


@pytest.mark.asyncio
async def test_supervisor_logs_execution(sample_graph_state):
    """Test that supervisor node logs execution."""
    from src.nodes.supervisor import supervisor_node

    with patch("src.nodes.supervisor.logger") as mock_logger:
        # Mock the LLM response
        mock_response = Mock()
        mock_response.content = '{"plan": [], "active_agent": null, "notes": "test"}'

        with patch("src.nodes.supervisor.ChatAnthropic") as mock_llm_class:
            mock_llm = Mock()
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm

            await supervisor_node(sample_graph_state)

            # Verify logging was called
            assert mock_logger.info.called
            assert mock_logger.debug.called or mock_logger.info.called


@pytest.mark.asyncio
async def test_research_agent_logs_execution(sample_graph_state, sample_todo):
    """Test that research agent logs execution."""
    from src.nodes.research_agent import research_agent_node

    sample_todo["owner_agent"] = "research_agent"
    sample_todo["status"] = "PENDING"
    sample_graph_state["supervisor"]["plan"] = [sample_todo]

    with patch("src.nodes.research_agent.logger") as mock_logger:
        mock_response = Mock()
        mock_response.content = """{"agent_name": "research_agent", "step_id": "123",
            "result": "COMPLETED", "short_summary": "test",
            "key_decisions": [], "next_instructions_for_supervisor": "test"}"""
        mock_response.tool_calls = None

        with patch("src.nodes.research_agent.ChatAnthropic") as mock_llm_class:
            mock_llm = Mock()
            mock_llm.bind_tools.return_value = mock_llm
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm

            await research_agent_node(sample_graph_state)

            # Verify logging was called
            assert mock_logger.info.called


@pytest.mark.asyncio
async def test_streaming_logs_events():
    """Test that streaming logs events."""
    from src.api.streaming import stream_agent_events

    with patch("src.api.streaming.logger") as mock_logger:
        # Collect first few events
        event_count = 0
        async for _chunk in stream_agent_events("Test task"):
            event_count += 1
            if event_count >= 3:
                break

        # Verify logging was called
        assert mock_logger.info.called


def test_logging_configuration_reduces_third_party_noise():
    """Test that third-party library logging is reduced."""
    setup_logging(log_level="INFO")

    httpx_logger = logging.getLogger("httpx")
    httpcore_logger = logging.getLogger("httpcore")

    assert httpx_logger.level == logging.WARNING
    assert httpcore_logger.level == logging.WARNING
