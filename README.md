# Multi-Agent System

A production-ready LangGraph-based multi-agent system with real-time streaming, interactive UI, and PostgreSQL-backed todo management. Built with Claude 3.5 Sonnet (via Anthropic API), FastAPI backend, and Next.js frontend.

## Features

### Backend
- ✅ Multi-agent architecture with Supervisor node
- ✅ PostgreSQL database with async SQLAlchemy
- ✅ Todo CRUD API with lifecycle management
- ✅ AI-assisted todo planning and execution
- ✅ Real-time streaming with Server-Sent Events (SSE)
- ✅ Multiple specialist agents (research_agent, transform_agent)
- ✅ Finalizer node for task completion
- ✅ Deterministic routing logic
- ✅ State management (SupervisorState, AgentState, GraphState)
- ✅ Memory checkpointer
- ✅ RESTful API endpoints (`/v1/agent/*`, `/v1/todos/*`, `/v1/ai-todos/*`)
- ✅ Health check endpoint
- ✅ Docker deployment with PostgreSQL
- ✅ Python 3.11+ with uv package manager
- ✅ Pre-commit hooks (prettier, eslint, black, ruff, detect-secrets)

### Frontend
- ✅ Next.js 14 with React 18
- ✅ TypeScript support
- ✅ Real-time streaming UI with SSE
- ✅ Interactive chat interface for multi-agent system
- ✅ Technical-editorial dark theme design
- ✅ Custom fonts (Syne, Manrope, JetBrains Mono)
- ✅ Component library (ApprovalCard, EditableValue, DocumentViewer, etc.)
- ✅ Responsive design with animations
- ✅ Jest testing setup

## Architecture

```
┌──────────────────┐
│  Next.js Frontend│
│  (Port 3000)     │
└────────┬─────────┘
         │ HTTP/SSE
         ▼
┌──────────────────┐     ┌──────────────┐
│   FastAPI        │────►│  PostgreSQL  │
│   Backend        │     │  Database    │
│   (Port 8080)    │◄────│  (Port 5432) │
└────────┬─────────┘     └──────────────┘
         │
         ▼
┌─────────────────────┐
│   LangGraph Agent   │
│                     │
│  ┌──────────────┐   │
│  │  Supervisor  │   │
│  └──────┬───────┘   │
│         │           │
│    ┌────┴────┐      │
│    │         │      │
│    ▼         ▼      │
│  research  transform│
│   agent     agent   │
│    │         │      │
│    └────┬────┘      │
│         │           │
│    ┌────▼────┐      │
│    │Finalizer│      │
│    └─────────┘      │
└─────────────────────┘
```

## Project Structure

```
agent/
├── agent-service/              # Backend FastAPI service
│   ├── src/
│   │   ├── api/
│   │   │   ├── server.py       # FastAPI app & main endpoints
│   │   │   ├── todos.py        # Todo CRUD endpoints
│   │   │   ├── ai_todos.py     # AI-assisted todo endpoints
│   │   │   └── streaming.py    # SSE streaming logic
│   │   ├── models/
│   │   │   ├── state.py        # LangGraph state models
│   │   │   ├── api_models.py   # API request/response models
│   │   │   └── database.py     # SQLAlchemy models
│   │   ├── nodes/
│   │   │   ├── supervisor.py   # Supervisor agent
│   │   │   ├── research_agent.py
│   │   │   ├── transform_agent.py
│   │   │   └── finalizer.py
│   │   ├── graph/
│   │   │   └── workflow.py     # LangGraph setup & routing
│   │   ├── services/
│   │   │   ├── todo_crud.py    # Todo business logic
│   │   │   └── ai_todo.py      # AI integration service
│   │   ├── database.py         # Database connection
│   │   ├── utils/
│   │   │   └── logging_config.py
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .python-version
├── frontend-ui/                # Next.js frontend
│   ├── app/
│   │   ├── page.tsx            # Main chat interface
│   │   ├── layout.tsx          # Root layout
│   │   ├── globals.css         # Global styles & animations
│   │   ├── components/
│   │   │   ├── ApprovalCard.tsx
│   │   │   ├── EditableValue.tsx
│   │   │   ├── DocumentViewer.tsx
│   │   │   ├── OptionsSelector.tsx
│   │   │   └── ResearchSummary.tsx
│   │   └── api/
│   │       └── stream/
│   │           └── route.ts    # SSE proxy endpoint
│   ├── __tests__/              # Jest tests
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── jest.config.js
├── .pre-commit-config.yaml     # Pre-commit hooks config
├── .secrets.baseline           # Detect-secrets baseline
├── docker-compose.yml          # PostgreSQL + agent-service
├── .env.example
└── README.md
```

## Tech Stack

### Backend
- **Python 3.11+** - Core language
- **uv** - Fast Python package manager
- **FastAPI** - Modern async web framework
- **LangGraph** - Multi-agent orchestration
- **LangChain** - LLM framework
- **Anthropic Claude 3.5 Sonnet** - Language model
- **PostgreSQL** - Primary database
- **SQLAlchemy** - Async ORM
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type safety
- **Server-Sent Events (SSE)** - Real-time streaming
- **Custom CSS** - No UI frameworks, pure styling

### DevOps
- **Docker & Docker Compose** - Containerization
- **Pre-commit hooks** - Code quality (prettier, eslint, black, ruff)
- **detect-secrets** - Security scanning
- **Jest** - Frontend testing
- **pytest** - Backend testing

## Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package installer
- **Docker & Docker Compose** (recommended)
- **Anthropic API key**
- **PostgreSQL** (or use Docker Compose)

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

### Quick Start with Docker (Recommended)

1. **Create `.env` file** in the root directory:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

2. **Start all services** (PostgreSQL + Backend):
```bash
docker-compose up --build
```

3. **Start the frontend** (in a separate terminal):
```bash
cd frontend-ui
npm install
npm run dev
```

**Services will be available at:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8080`
- PostgreSQL: `localhost:5432`

## API Usage

### Endpoints

#### Agent Endpoints
- `POST /v1/agent/run` - Run multi-agent system (non-streaming)
- `POST /v1/agent/stream` - Run multi-agent system with SSE streaming

#### Todo Endpoints
- `GET /v1/todos` - List all todos
- `POST /v1/todos` - Create a new todo
- `GET /v1/todos/{id}` - Get a specific todo
- `PUT /v1/todos/{id}` - Update a todo
- `DELETE /v1/todos/{id}` - Delete a todo

#### AI-Assisted Todo Endpoints
- `POST /v1/ai-todos/create` - AI creates todos from task description
- `POST /v1/ai-todos/execute` - AI executes a specific todo

#### Health Check
- `GET /health` - Service health status

### Agent Run (Non-Streaming)

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

### Agent Stream (Server-Sent Events)

The streaming endpoint provides real-time updates as the agent executes:

```bash
curl -X POST http://localhost:8080/v1/agent/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "task": "Research AI developments"
    }
  }'
```

**SSE Event Types:**
- `started` - Agent execution begins
- `thinking` - Supervisor is planning
- `plan_created` - Plan has been created
- `routing` - Routing to an agent
- `agent_working` - Agent is executing
- `agent_completed` - Agent finished with summary
- `tool_call` - Agent requesting tool use (HITL)
- `finalizing` - Creating final output
- `done` - Task complete with result

**Frontend Integration:**

The frontend uses the `/api/stream` endpoint which proxies to the backend:

```typescript
const response = await fetch('/api/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ task: 'Your task here' })
});

const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const event = JSON.parse(line.substring(6));
      // Handle event...
    }
  }
}
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

### Backend Commands

```bash
cd agent-service

# Install dependencies
uv pip install -e .

# Install dev dependencies
uv pip install -e ".[dev]"

# Run server
python src/main.py

# Run with auto-reload
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8080

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Format code
black src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

### Frontend Commands

```bash
cd frontend-ui

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Run tests in watch mode
npm test -- --watch
```

### Pre-commit Hooks

```bash
# Install hooks
./pre-commit-install.sh

# Run manually on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
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

Create a `.env` file in the root directory:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database (use Docker Compose or local PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todos  # pragma: allowlist secret

# Optional
SYSTEM_VARIANT=blue
PORT=8080
LOG_LEVEL=INFO
ENV=development  # or production
```

**Note:** If using Docker Compose, the `DATABASE_URL` will automatically point to the containerized PostgreSQL instance.

## Frontend Design

The frontend features a **technical-editorial dark theme** designed to be distinctive and avoid generic AI aesthetics:

- **Color Palette**: Deep navy backgrounds with neon cyan (#00f5d4) and electric yellow (#fee440) accents
- **Typography**:
  - Syne (bold display font for headers)
  - Manrope (clean body font)
  - JetBrains Mono (technical/monospace elements)
- **Visual Style**: Angular geometry with octagonal avatars, diagonal cuts, and clip-path shapes
- **Effects**: Grid background patterns, backdrop blur, glow animations, and smooth transitions
- **Components**: Custom-designed cards for approval, editable values, documents, options, and research summaries

## Pre-commit Hooks

The project uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
./pre-commit-install.sh

# Or manually
pip install pre-commit
pre-commit install
```

**Hooks include:**
- **prettier** - Frontend code formatting
- **eslint** - Frontend linting
- **black** - Python code formatting
- **ruff** - Python linting
- **detect-secrets** - Prevent committing secrets

## What's Next

**Planned Features:**
- HITL (Human-in-the-Loop) escalation for complex decisions
- Enhanced error handling and retry logic
- Additional specialist agents (code_agent, data_agent, etc.)
- Prompt Library service for template management
- genUI service for dynamic component generation
- Blue-Green variant execution for A/B testing
- Cross-variant evaluation and metrics

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

### Database Connection Errors

If you see database connection errors:

1. **Check PostgreSQL is running:**
```bash
docker-compose ps
```

2. **Verify DATABASE_URL** in `.env` matches your setup

3. **Reset database:**
```bash
docker-compose down -v
docker-compose up --build
```

### Frontend Not Loading

If the frontend shows errors:

1. **Install dependencies:**
```bash
cd frontend-ui
npm install
```

2. **Check backend is running** at `http://localhost:8080`

3. **Clear Next.js cache:**
```bash
rm -rf .next
npm run dev
```

### Pre-commit Hooks Failing

If pre-commit hooks block your commits:

```bash
# Format code manually
cd agent-service && black src tests
cd ../frontend-ui && npx prettier --write .

# Then commit again
```
