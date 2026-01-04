# Test Suite

Comprehensive test suite for the multi-agent system.

## Test Coverage

### Unit Tests

**test_routing.py** - Routing logic
- Supervisor routing to finalizer, agents, and self
- Agent routing back to supervisor

**test_todo_lifecycle.py** - ToDo state management
- Creating todos with different statuses
- Transitioning between states
- Handling metadata

**test_ui_tools.py** - UI tool definitions
- Tool schema validation
- Required fields checking
- Tool uniqueness
- JSON Schema compliance

**test_agents.py** - Agent behavior with tool calling
- Processing tasks with no assignments
- Handling pending tasks
- Calling UI tools
- Managing tool call state
- Error handling for malformed responses
- Recursion depth tracking

**test_api.py** - API endpoints
- Health check endpoint
- Agent run endpoint validation
- Agent stream endpoint validation
- SSE format verification
- Event emission
- CORS headers
- HTTP method restrictions

**test_streaming.py** - Streaming functionality
- SSE format compliance
- Event structure validation
- Tool call event handling
- Plan creation events
- Routing events
- Agent completion events
- Done event structure

### Integration Tests

**test_integration.py** - End-to-end workflows
- Full graph execution
- Plan creation
- Agent routing
- Tool call handling
- Recursion tracking
- API-graph integration

## Running Tests

### Run All Tests
```bash
cd agent-service
source .venv/bin/activate
pytest
```

### Run Specific Test File
```bash
pytest tests/test_api.py
pytest tests/test_agents.py
```

### Run Specific Test
```bash
pytest tests/test_api.py::test_health_endpoint
pytest tests/test_agents.py::test_research_agent_calls_ui_tool
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Only Fast Tests (Skip Integration)
```bash
pytest -m "not integration"
```

### Run Only Integration Tests
```bash
pytest tests/test_integration.py
```

## Test Configuration

**conftest.py** - Shared fixtures
- FastAPI test client
- Sample GraphState
- Sample ToDo
- Sample AgentSummary
- Mock tool calls
- GraphState with tool calls

**pyproject.toml** - Test settings
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## Fixtures

### Available Fixtures

- `client` - FastAPI TestClient for API testing
- `sample_graph_state` - Basic GraphState for testing
- `sample_todo` - Sample ToDo item
- `sample_agent_summary` - Sample agent result summary
- `mock_tool_call` - Mock UI tool call
- `graph_state_with_tool_call` - GraphState with pending tool call

### Using Fixtures

```python
def test_example(client, sample_graph_state):
    # Use client to test API
    response = client.get("/health")

    # Use sample_graph_state for testing
    assert sample_graph_state["supervisor"]["status"] == "RUNNING"
```

## Writing Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test functions: `test_*`
- Use descriptive names that explain what is being tested

### Async Tests
Use `@pytest.mark.asyncio` for async functions:
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Mocking LLM Calls
```python
from unittest.mock import Mock, AsyncMock, patch

@pytest.mark.asyncio
async def test_agent_with_mock(sample_graph_state):
    mock_response = Mock()
    mock_response.content = '{"result": "COMPLETED"}'
    mock_response.tool_calls = None

    with patch("src.nodes.research_agent.ChatAnthropic") as mock_llm:
        mock_llm.return_value.bind_tools.return_value.ainvoke = AsyncMock(
            return_value=mock_response
        )

        result = await research_agent_node(sample_graph_state)
        assert result is not None
```

## CI/CD Integration

Tests run automatically via pre-commit hooks and should be included in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    cd agent-service
    source .venv/bin/activate
    pytest --cov=src --cov-report=xml
```

## Troubleshooting

### Import Errors
Make sure you're in the agent-service directory and virtual environment is activated:
```bash
cd agent-service
source .venv/bin/activate
```

### Async Warnings
If you see warnings about async tests, ensure `pytest-asyncio` is installed:
```bash
uv pip install pytest-asyncio
```

### Test Timeouts
For tests that take too long, adjust timeout settings:
```python
@pytest.mark.timeout(30)  # 30 second timeout
async def test_long_running():
    ...
```

## Test Statistics

Run this to see test statistics:
```bash
pytest --collect-only
```

Current test count:
- **Unit Tests**: ~50+ tests
- **Integration Tests**: ~10+ tests
- **Total Coverage**: High coverage of core functionality
