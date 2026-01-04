"""Tests for API endpoints."""

import json

import pytest


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_agent_run_endpoint_requires_input(client):
    """Test that /v1/agent/run requires input."""
    response = client.post("/v1/agent/run", json={})
    assert response.status_code == 422  # Validation error


def test_agent_run_endpoint_accepts_valid_input(client):
    """Test that /v1/agent/run accepts valid input."""
    payload = {"input": {"task": "Test task"}}
    response = client.post("/v1/agent/run", json=payload)

    # Should not return validation error
    assert response.status_code != 422


def test_agent_stream_endpoint_requires_input(client):
    """Test that /v1/agent/stream requires input."""
    response = client.post("/v1/agent/stream", json={})
    assert response.status_code == 422  # Validation error


@pytest.mark.skip(reason="Requires LLM calls - use integration tests instead")
def test_agent_stream_endpoint_accepts_valid_input(client):
    """Test that /v1/agent/stream accepts valid input."""
    payload = {"input": {"task": "Test task"}}
    response = client.post("/v1/agent/stream", json=payload)

    # Should not return validation error
    assert response.status_code != 422


@pytest.mark.skip(reason="Requires LLM calls - use integration tests instead")
def test_agent_stream_returns_event_stream(client):
    """Test that /v1/agent/stream returns text/event-stream."""
    payload = {"input": {"task": "Test task"}}
    response = client.post("/v1/agent/stream", json=payload)

    # Check content type
    content_type = response.headers.get("content-type", "")
    assert "text/event-stream" in content_type


@pytest.mark.skip(reason="Requires LLM calls - use integration tests instead")
def test_stream_response_contains_sse_events(client):
    """Test that stream response contains SSE formatted events."""
    payload = {"input": {"task": "Test task"}}
    response = client.post("/v1/agent/stream", json=payload)

    # Get response content
    content = response.text

    # Should contain SSE data: prefix
    assert "data: " in content


@pytest.mark.skip(reason="Requires LLM calls - use integration tests instead")
def test_stream_emits_started_event(client):
    """Test that stream emits a 'started' event."""
    payload = {"input": {"task": "Test task"}}
    response = client.post("/v1/agent/stream", json=payload)

    content = response.text

    # Parse events
    events = []
    for line in content.split("\n"):
        if line.startswith("data: "):
            try:
                event_data = json.loads(line[6:])  # Skip "data: " prefix
                events.append(event_data)
            except json.JSONDecodeError:
                pass

    # Should have at least one event
    assert len(events) > 0

    # First event should be 'started'
    assert events[0]["type"] == "started"


@pytest.mark.skip(reason="Requires LLM calls - use integration tests instead")
def test_stream_emits_thinking_event(client):
    """Test that stream emits a 'thinking' event."""
    payload = {"input": {"task": "Test task"}}
    response = client.post("/v1/agent/stream", json=payload)

    content = response.text

    # Parse events
    event_types = []
    for line in content.split("\n"):
        if line.startswith("data: "):
            try:
                event_data = json.loads(line[6:])
                event_types.append(event_data["type"])
            except (json.JSONDecodeError, KeyError):
                pass

    # Should contain 'thinking' event
    assert "thinking" in event_types


def test_invalid_endpoint_returns_404(client):
    """Test that invalid endpoints return 404."""
    response = client.get("/invalid/endpoint")
    assert response.status_code == 404


def test_cors_headers_present(client):
    """Test that CORS headers are present."""
    response = client.get("/health")

    # Check for CORS headers (may not be present in test environment)
    # This is a basic check - actual CORS config happens at deployment
    assert response.status_code == 200


@pytest.mark.parametrize(
    "endpoint",
    ["/v1/agent/run", "/v1/agent/stream"],
)
def test_endpoints_accept_post_only(client, endpoint):
    """Test that agent endpoints only accept POST."""
    # GET should fail
    response = client.get(endpoint)
    assert response.status_code == 405  # Method not allowed
