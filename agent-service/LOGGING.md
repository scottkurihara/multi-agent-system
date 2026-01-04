# Logging Configuration

Comprehensive logging setup for debugging and monitoring the multi-agent system.

## Overview

The system uses Python's `logging` module with structured logging throughout all components:
- Supervisor node
- Agent nodes (research, transform)
- API streaming
- Graph workflow
- Server initialization

## Configuration

### Environment Variables

Set logging level via environment variable:
```bash
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
export LOG_FILE=/path/to/logfile.log  # Optional file logging
```

### Default Settings

- **Log Level**: INFO
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Date Format**: `YYYY-MM-DD HH:MM:SS`
- **Output**: stdout (and optional file)

### Third-Party Library Logging

The following libraries have reduced logging to WARNING level to minimize noise:
- `httpx`
- `httpcore`
- `anthropic` (INFO level)
- `langgraph` (INFO level)

## Usage

### In Application Code

```python
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

### Starting the Server with Logging

```bash
# Default INFO level
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8080

# Debug level
LOG_LEVEL=DEBUG python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8080

# With file logging
LOG_LEVEL=INFO LOG_FILE=agent.log python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8080
```

## Log Levels by Component

### Supervisor Node (`src/nodes/supervisor.py`)
- **INFO**: Node start, planning phase, routing decisions, plan size
- **DEBUG**: Current status, response length, JSON parsing status
- **WARNING**: Failed JSON parsing with regex fallback
- **ERROR**: Supervisor failed to output valid JSON

### Research Agent (`src/nodes/research_agent.py`)
- **INFO**: Node start, task count, LLM invocation, UI tool calls
- **DEBUG**: Current task being processed
- **WARNING**: No pending tasks assigned

### Transform Agent (`src/nodes/transform_agent.py`)
- **INFO**: Node start, task count, LLM invocation, UI tool calls
- **DEBUG**: Current task being processed
- **WARNING**: No pending tasks assigned

### Streaming API (`src/api/streaming.py`)
- **INFO**: Stream start, run ID creation, graph execution start, tool calls, completion status
- **DEBUG**: Step-by-step processing (each graph step)
- **WARNING**: No final state captured (fallback used)

### Workflow (`src/graph/workflow.py`)
- **INFO**: Graph creation, routing decisions (which agent)
- **DEBUG**: Routing details (finalizer, supervisor loops)
- **WARNING**: Escalation to HITL

### Server (`src/api/server.py`)
- **INFO**: Service startup, graph creation, request received (run/stream)

## Log Output Examples

### Normal Operation (INFO level)
```
2024-01-04 11:00:00 - src.api.server - INFO - Starting Agent Service with log level: INFO
2024-01-04 11:00:01 - src.graph.workflow - INFO - Creating agent workflow graph
2024-01-04 11:00:01 - src.graph.workflow - INFO - Workflow graph compiled successfully
2024-01-04 11:00:01 - src.api.server - INFO - Agent graph created successfully
2024-01-04 11:00:05 - src.api.server - INFO - Received stream request: Test task...
2024-01-04 11:00:05 - src.api.streaming - INFO - Starting stream for task: Test task...
2024-01-04 11:00:05 - src.api.streaming - INFO - Created run ID: abc-123-def
2024-01-04 11:00:05 - src.api.streaming - INFO - Starting graph stream execution
2024-01-04 11:00:06 - src.nodes.supervisor - INFO - Supervisor node started
2024-01-04 11:00:06 - src.nodes.supervisor - INFO - Initial planning phase - creating new plan
2024-01-04 11:00:08 - src.nodes.supervisor - INFO - Supervisor routing to: research_agent
2024-01-04 11:00:08 - src.nodes.supervisor - INFO - Plan has 2 tasks
2024-01-04 11:00:08 - src.graph.workflow - INFO - Routing to research_agent
2024-01-04 11:00:08 - src.nodes.research_agent - INFO - Research agent node started
2024-01-04 11:00:08 - src.nodes.research_agent - INFO - Research agent found 1 pending tasks
2024-01-04 11:00:08 - src.nodes.research_agent - INFO - Invoking research agent LLM
2024-01-04 11:00:10 - src.nodes.research_agent - INFO - Research agent calling UI tool: show_research_summary
2024-01-04 11:00:10 - src.api.streaming - INFO - Streaming tool call: show_research_summary
2024-01-04 11:00:11 - src.api.streaming - INFO - Stream completed after 8 steps
2024-01-04 11:00:11 - src.api.streaming - INFO - Final status: DONE
```

### Debug Level
Includes all INFO messages plus:
```
2024-01-04 11:00:06 - src.nodes.supervisor - DEBUG - Supervisor state: RUNNING
2024-01-04 11:00:08 - src.nodes.supervisor - DEBUG - Supervisor response length: 245 chars
2024-01-04 11:00:08 - src.nodes.supervisor - DEBUG - Successfully parsed supervisor JSON response
2024-01-04 11:00:08 - src.nodes.research_agent - DEBUG - Processing task: Perform research on...
2024-01-04 11:00:09 - src.api.streaming - DEBUG - Processing step 3
2024-01-04 11:00:10 - src.graph.workflow - DEBUG - Routing to finalizer (status=DONE)
```

### Error Scenarios
```
2024-01-04 11:00:08 - src.nodes.supervisor - ERROR - Supervisor failed to output valid JSON
2024-01-04 11:00:08 - src.nodes.research_agent - WARNING - Research agent has no pending tasks, returning immediately
```

## Debugging Tips

### Enable Debug Logging
```bash
LOG_LEVEL=DEBUG python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8080
```

### Log to File for Analysis
```bash
LOG_FILE=debug.log LOG_LEVEL=DEBUG python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8080
```

Then analyze:
```bash
# Filter by component
grep "src.nodes.supervisor" debug.log

# Filter by level
grep "ERROR" debug.log

# Follow live logs
tail -f debug.log
```

### Common Debug Patterns

**Track a specific run:**
```bash
grep "abc-123-def" debug.log  # Using run_id
```

**Find errors:**
```bash
grep -E "ERROR|WARNING" debug.log
```

**Agent execution flow:**
```bash
grep -E "Routing to|node started" debug.log
```

**LLM invocations:**
```bash
grep "Invoking.*LLM" debug.log
```

**Tool calls:**
```bash
grep "calling UI tool" debug.log
```

## Testing

Run logging tests:
```bash
cd agent-service
source .venv/bin/activate
pytest tests/test_logging.py -v
```

Test coverage includes:
- Logging configuration setup
- Log level enforcement
- Logger creation
- Component-level logging verification
- Third-party library log level reduction

## Performance Considerations

- **INFO level** (recommended for production): Minimal performance impact
- **DEBUG level**: Higher log volume, may impact performance in high-throughput scenarios
- **File logging**: Asynchronous handlers recommended for production use

## Best Practices

1. **Use appropriate log levels**
   - DEBUG: Detailed diagnostic information
   - INFO: Confirmation that things are working as expected
   - WARNING: Something unexpected but the system continues
   - ERROR: A serious problem occurred
   - CRITICAL: System may be unable to continue

2. **Include context in log messages**
   ```python
   logger.info(f"Processing task: {task_id}")  # Good
   logger.info("Processing task")  # Not helpful
   ```

3. **Don't log sensitive data**
   - Avoid logging API keys, passwords, or PII
   - Redact sensitive information if necessary

4. **Use structured logging for complex data**
   ```python
   logger.info(f"Agent completed: status={status}, tasks={len(tasks)}")
   ```

5. **Log at decision points**
   - Routing decisions
   - State transitions
   - External API calls
   - Error handling

## Future Enhancements

Potential improvements:
- Structured JSON logging for log aggregation systems
- Request ID tracking across all components
- Performance metrics logging
- Log rotation configuration
- Distributed tracing integration (OpenTelemetry)
