"""Tests for streaming functionality."""

import json

import pytest

from src.api.streaming import stream_agent_events


@pytest.mark.asyncio
async def test_stream_emits_started_event():
    """Test that stream emits a started event."""
    events = []

    async for chunk in stream_agent_events("Test task"):
        if chunk.startswith("data: "):
            try:
                event = json.loads(chunk[6:])
                events.append(event)
            except json.JSONDecodeError:
                pass

        # Collect first few events for testing
        if len(events) >= 3:
            break

    # First event should be 'started'
    assert len(events) > 0
    assert events[0]["type"] == "started"
    assert "Starting" in events[0]["message"]


@pytest.mark.asyncio
async def test_stream_emits_thinking_event():
    """Test that stream emits a thinking event."""
    events = []

    async for chunk in stream_agent_events("Test task"):
        if chunk.startswith("data: "):
            try:
                event = json.loads(chunk[6:])
                events.append(event)
            except json.JSONDecodeError:
                pass

        # Collect first few events
        if len(events) >= 3:
            break

    # Should contain thinking event
    event_types = [e["type"] for e in events]
    assert "thinking" in event_types


@pytest.mark.asyncio
async def test_stream_format_is_sse():
    """Test that stream follows SSE format."""
    async for chunk in stream_agent_events("Test task"):
        # Each chunk should either be data: or empty line
        if chunk.strip():
            assert chunk.startswith("data: ")

        # Only test first chunk
        break


@pytest.mark.asyncio
async def test_stream_events_have_type_and_message():
    """Test that all stream events have type and message."""
    events = []

    async for chunk in stream_agent_events("Test task"):
        if chunk.startswith("data: "):
            try:
                event = json.loads(chunk[6:])
                events.append(event)
            except json.JSONDecodeError:
                pass

        if len(events) >= 5:
            break

    # All events should have type and message
    for event in events:
        assert "type" in event
        assert "message" in event
        assert isinstance(event["type"], str)
        assert isinstance(event["message"], str)


@pytest.mark.asyncio
async def test_stream_tool_call_event_structure():
    """Test tool_call event structure when present."""
    events = []

    async for chunk in stream_agent_events("Show me options"):
        if chunk.startswith("data: "):
            try:
                event = json.loads(chunk[6:])
                events.append(event)

                # If we find a tool_call event, check its structure
                if event.get("type") == "tool_call":
                    assert "agent" in event
                    assert "tool" in event
                    assert "args" in event
                    assert "tool_call_id" in event
                    assert isinstance(event["args"], dict)
                    break
            except json.JSONDecodeError:
                pass

        # Limit iterations for testing
        if len(events) >= 20:
            break


@pytest.mark.asyncio
async def test_stream_plan_created_event_has_plan():
    """Test that plan_created event includes plan data."""
    events = []

    async for chunk in stream_agent_events("Test task"):
        if chunk.startswith("data: "):
            try:
                event = json.loads(chunk[6:])
                events.append(event)

                # Check plan_created event
                if event.get("type") == "plan_created":
                    assert "plan" in event
                    assert isinstance(event["plan"], list)
                    break
            except json.JSONDecodeError:
                pass

        if len(events) >= 20:
            break


@pytest.mark.asyncio
async def test_stream_routing_event_has_agent():
    """Test that routing event includes agent name."""
    events = []

    async for chunk in stream_agent_events("Test task"):
        if chunk.startswith("data: "):
            try:
                event = json.loads(chunk[6:])
                events.append(event)

                # Check routing event
                if event.get("type") == "routing":
                    assert "agent" in event
                    assert isinstance(event["agent"], str)
                    break
            except json.JSONDecodeError:
                pass

        if len(events) >= 20:
            break


@pytest.mark.asyncio
async def test_stream_agent_completed_has_summary():
    """Test that agent_completed event includes summary."""
    events = []

    async for chunk in stream_agent_events("Test task"):
        if chunk.startswith("data: "):
            try:
                event = json.loads(chunk[6:])
                events.append(event)

                # Check agent_completed event
                if event.get("type") == "agent_completed":
                    assert "agent" in event
                    assert "summary" in event
                    assert isinstance(event["summary"], dict)
                    break
            except json.JSONDecodeError:
                pass

        if len(events) >= 30:
            break


@pytest.mark.asyncio
async def test_stream_done_event_has_result():
    """Test that done event includes result."""
    events = []
    done_event = None

    async for chunk in stream_agent_events("Test task"):
        if chunk.startswith("data: "):
            try:
                event = json.loads(chunk[6:])
                events.append(event)

                if event.get("type") == "done":
                    done_event = event
                    break
            except json.JSONDecodeError:
                pass

        # Limit iterations
        if len(events) >= 50:
            break

    # If we got a done event, check its structure
    if done_event:
        assert "result" in done_event
        assert isinstance(done_event["result"], dict)
        assert "status" in done_event["result"]


@pytest.mark.asyncio
async def test_stream_handles_empty_task():
    """Test that stream handles empty task string."""
    events = []

    async for chunk in stream_agent_events(""):
        if chunk.startswith("data: "):
            try:
                event = json.loads(chunk[6:])
                events.append(event)
            except json.JSONDecodeError:
                pass

        # Collect first few events
        if len(events) >= 3:
            break

    # Should still emit events
    assert len(events) > 0
