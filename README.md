# Multi-Agent System - Phase 1

This is a LangGraph-based multi-agent system implementing Phase 1 of the specification. The system uses Claude 3.5 Sonnet (via Anthropic API) for all LLM operations and is built with Python using `uv` for package management.

## Phase 1 Features

- ✅ Multi-agent architecture with Supervisor node
- ✅ ToDo planning and lifecycle management
- ✅ Multiple specialist agents (research_agent, transform_agent)
- ✅ Finalizer node
- ✅ Deterministic routing logic
- ✅ State management (SupervisorState, AgentState, GraphState)
- ✅ Memory checkpointer
- ✅ HTTP API endpoint (`POST /v1/agent/run`)
- ✅ Docker deployment
- ✅ Python 3.11+ with uv package manager

## Architecture

```
┌─────────────┐
│  Supervisor │ ◄─── Entry point
└──────┬──────┘
       │
       ├──► research_agent
       │         │
       ├──► transform_agent
       │         │
       └──────┬──┘
              │
       ┌──────▼──────┐
       │  Finalizer  │
       └─────────────┘
```

## Project Structure

```
agent/
├── agent-service/
│   ├── src/
│   │   ├── types/
│   │   │   ├── state.py           # State models
│   │   │   └── api_models.py      # API types
│   │   ├── nodes/
│   │   │   ├── supervisor.py      # Supervisor node
│   │   │   ├── research_agent.py  # Research agent
│   │   │   ├── transform_agent.py # Transform agent
│   │   │   └── finalizer.py       # Finalizer
│   │   ├── graph/
│   │   │   └── workflow.py        # Graph setup & routing
│   │   ├── api/
│   │   │   └── server.py          # FastAPI server
│   │   └── main.py                # Entry point
│   ├── tests/
│   │   ├── test_routing.py
│   │   └── test_todo_lifecycle.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .python-version
├── docker-compose.yml
└── multi_agent_system_full_spec.md
```

## Tech Stack

- **Python 3.11+**
- **uv** - Fast Python package manager
- **FastAPI** - Modern async web framework
- **LangGraph** - Multi-agent orchestration
- **LangChain** - LLM framework
- **Anthropic Claude 3.5 Sonnet** - Language model
- **Pydantic** - Data validation

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Docker & Docker Compose (optional)
- Anthropic API key

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Local Development

1. Navigate to the service directory:
```bash
cd agent-service
```

2. Create virtual environment and install dependencies with uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

3. Create `.env` file in the root directory:
```bash
cd ..
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

4. Run in development mode:
```bash
cd agent-service
python src/main.py
```

Or use uvicorn directly:
```bash
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8080
```

### Docker Deployment

1. Create `.env` file in the root directory with your API key

2. Build and run:
```bash
docker-compose up --build
```

The service will be available at `http://localhost:8080`

## API Usage

### Endpoint

`POST /v1/agent/run`

### Request Example

```json
{
  "input": {
    "task": "Research the latest developments in AI and summarize the key findings",
    "context": {
      "context_id": "optional-context-id",
      "metadata": {}
    }
  },
  "options": {
    "system_variant": "blue",
    "stream": false
  }
}
```

### Response Example

```json
{
  "result": {
    "status": "DONE",
    "output": {
      "type": "text",
      "content": "Task completed successfully.\n\nWork done:\nresearch_agent: Completed research on AI developments\ntransform_agent: Summarized findings into key points"
    },
    "supervisor_state": {
      "task_id": "uuid",
      "status": "DONE",
      "plan": [...],
      "history": [...]
    }
  },
  "metadata": {
    "run_id": "uuid",
    "system_variant": "blue"
  }
}
```

### Test with curl

```bash
curl -X POST http://localhost:8080/v1/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "task": "Analyze the benefits of TypeScript"
    }
  }'
```

### Test with Python

```python
import httpx

async def test_agent():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8080/v1/agent/run",
            json={
                "input": {
                    "task": "Analyze the benefits of TypeScript"
                }
            }
        )
        print(response.json())
```

## Testing

Run tests with pytest:

```bash
cd agent-service
uv pip install -e ".[dev]"
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=html
```

## Development Commands

```bash
# Install dependencies
uv pip install -e .

# Install dev dependencies
uv pip install -e ".[dev]"

# Run server
python src/main.py

# Run with auto-reload
uvicorn src.api.server:app --reload

# Run tests
pytest

# Format code (after installing black)
uv pip install black
black src tests

# Type checking (after installing mypy)
uv pip install mypy
mypy src
```

## State Model

The system uses a hierarchical state model:

- **GraphState**: Root state containing supervisor and agent states
- **SupervisorState**: Planning, routing, and coordination
- **AgentState**: Agent execution context
- **ToDo**: Task items with lifecycle tracking (PENDING → IN_PROGRESS → DONE)
- **AgentSummary**: Agent execution results

## Routing Logic

Per specification:
```
IF supervisor.status == "DONE" → finalizer
IF supervisor.status == "ESCALATE" → hitl_escalation (Phase 2)
IF supervisor.active_agent == null → supervisor
ELSE → node named supervisor.active_agent
```

## Environment Variables

```bash
ANTHROPIC_API_KEY=your_key_here
SYSTEM_VARIANT=blue
PORT=8080
ENV=development  # or production
```

## What's Next

**Phase 2** will add:
- HITL (Human-in-the-Loop) escalation
- Enhanced error handling
- Additional specialist agents

**Phase 3** will add:
- Streaming support with Server-Sent Events
- AI-SDK frontend integration
- Prompt Library service
- genUI service

**Phase 4** will add:
- Blue-Green variant execution
- Cross-variant evaluation

## Spec Compliance

This implementation follows the specification in `multi_agent_system_full_spec.md`:
- ✅ Deterministic routing (no implicit LLM routing)
- ✅ State model (GraphState, SupervisorState, AgentState)
- ✅ ToDo planning with status tracking
- ✅ AgentSummary reporting
- ✅ Supervisor does not call tools
- ✅ Agents do not modify SupervisorState
- ✅ Memory checkpointer
- ✅ API contract compliance
- ✅ Phase 1 feature complete

## Troubleshooting

### Import Errors

Make sure you're running from the agent-service directory and have activated the virtual environment:
```bash
cd agent-service
source .venv/bin/activate
```

### Port Already in Use

Change the port in `.env`:
```bash
PORT=8081
```

### Anthropic API Errors

Verify your API key is correctly set in `.env` and has sufficient credits.
