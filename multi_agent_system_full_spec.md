# multi_agent_system_full_spec.md

## PURPOSE
This file consolidates all specifications into ONE document:
- Multi-Agent System Spec (architecture, phases, routing, state)
- Agent-Service API Contract
- Streaming + genUI Integration
- Prompt Library Service Spec

This document is **machine-oriented**, for coding agents and engineers.

---

# 1️⃣ MULTI-AGENT SYSTEM SPEC

## 1.1 Architecture Overview
- Deterministic LangGraph multi-agent architecture.
- Nodes:
  - Supervisor (control, planning, routing)
  - Specialist Agents (execution units)
  - Finalizer (terminal DONE)
  - HITL Escalation (terminal ESCALATE)
- Checkpointer (Phase 0)
- Single HTTP endpoint → agent-service
- Prompts externalized via Prompt Library (Phase 3+)
- Streaming output (Phase 3+)
- Blue/Green system variants (Phase 4)
- Middleware layer for safety/policy checks (e.g., recursion limits)

---

## 1.2 State Model (MUST IMPLEMENT)

```ts
type Status = "RUNNING" | "DONE" | "ESCALATE";
type ToDoStatus = "PENDING" | "IN_PROGRESS" | "DONE" | "BLOCKED";
type AgentResult = "COMPLETED" | "NEEDS_ASSISTANCE" | "FAILED";
```

```ts
interface ToDo {
  id: string;
  description: string;
  status: ToDoStatus;
  owner_agent?: string;
  parent_id?: string;
  metadata?: Record<string, any>;
}
```

```ts
interface AgentSummary {
  agent_name: string;
  step_id: string;
  result: AgentResult;
  short_summary: string;
  key_decisions: string[];
  next_instructions_for_supervisor: string;
}
```

```ts
interface SupervisorState {
  task_id?: string;
  context_id?: string;
  status: Status;
  plan: ToDo[];
  history: AgentSummary[];
  active_agent?: string;
  notes?: string;
}
```

```ts
interface AgentState {
  messages: any[];
  tool_events: any[];
  recursion_depth: number;
  scratchpad: Record<string, any>;
}
```

```ts
interface GraphState {
  supervisor: SupervisorState;
  agent: AgentState;
}
```

---

## 1.3 Node Rules

### Supervisor Node
- Maintains plan, routing, status
- MUST NOT call tools
- MUST NOT mutate AgentState

### Specialist Agents
- Execute work
- MUST output one AgentSummary
- MUST NOT mutate SupervisorState
- MUST respect recursion limits (enforced by middleware)

### Finalizer
- MUST set status="DONE"
- MUST construct final response

### HITL Escalation
- MUST set status="ESCALATE"
- Terminates execution

---

## 1.5 Middleware (New)

### Concept
Middleware intercepts agent execution steps to enforce policies, safety checks, or transformations before/after LLM calls or tool executions.

### Recursion Limit Middleware
- **Purpose**: Prevent infinite loops in tool calling (e.g., Call Tool A → Error → Call Tool A → Error...).
- **Logic**:
  ```ts
  const MAX_RECURSION_LIMIT = 5; // Configurable
  
  function checkRecursionLimit(state: AgentState): AgentState {
    if (state.recursion_depth > MAX_RECURSION_LIMIT) {
      throw new Error("RECURSION_LIMIT_EXCEEDED: Agent exceeded max allowed consecutive tool calls.");
      // OR return a "FAILED" AgentSummary to Supervisor depending on error handling strategy
    }
    return state;
  }
  ```

---

## 1.4 Routing Contract

```
IF supervisor.status == "DONE" → finalizer
IF supervisor.status == "ESCALATE" → hitl_escalation
IF supervisor.active_agent == null → supervisor
ELSE → node named supervisor.active_agent
```

No implicit routing.

---

# 2️⃣ DEPLOYMENT VIA DOCKER-COMPOSE

```yaml
services:
  agent-service:
    build: ./agent-service
    container_name: agent-service
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
      - SYSTEM_VARIANT=${SYSTEM_VARIANT:-blue}
    restart: unless-stopped
```

Phase 3+ adds:
- frontend-ui
- prompt-library-service
- optional genui-service

---

# 3️⃣ API CONTRACT (`POST /v1/agent/run`)

### Request
```json
{
  "input": {
    "task": "string",
    "context": {"context_id": "optional", "metadata": {}}
  },
  "options": {
    "system_variant": "blue",
    "stream": false,
    "run_id": null
  }
}
```

### Non-Streaming Response
```json
{
  "result": {
    "status": "DONE",
    "output": {"type": "text","content": "final answer"},
    "supervisor_state": {...}
  },
  "metadata": {
    "run_id": "id",
    "system_variant": "blue",
    "trace_url": "optional"
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "STRING_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

Valid error codes:
- INVALID_REQUEST
- PROMPT_MISSING
- RUN_NOT_FOUND
- INTERNAL_ERROR
- STREAM_NOT_SUPPORTED

---

# 4️⃣ STREAMING (PHASE 3+)

### Enable
```json
"options": {"stream": true}
```

### Event Schema (NDJSON/SSE)

```json
{"event_type":"token","data":{"text":"hello"}}
{"event_type":"status_update","data":{"active_agent":"research_agent"}}
{"event_type":"final","data":{"status":"DONE","output":{"type":"text","content":"hi"},"run_id":"id"}}
```

Rules:
- MUST end with `final`
- MUST close connection after final

---

# 5️⃣ AI-SDK FRONTEND INTEGRATION (PHASE 3+)

### For Streaming
```ts
import { streamText } from "ai";

const stream = await streamText("/api/agent", { task: "do this" });
for await (const event of stream) {
  console.log(event.delta);
}
```

### FE Route (pseudo)
```ts
return streamText(fetch("http://agent-service:8080/v1/agent/run", {
  method: "POST",
  body: JSON.stringify({input, options:{stream:true}})
}));
```

---

# 6️⃣ genUI SERVICE (OPTIONAL PHASE 3+)

### Endpoint
`POST /v1/genui/layout`

### Request
```json
{"context": {"scenario":"generic"}}
```

### Response
```json
{
  "components":[
    {"type":"text","id":"t1","value":"Title"},
    {"type":"input","id":"i1","label":"Field"}
  ]
}
```

---

# 7️⃣ PROMPT LIBRARY SERVICE (REQUIRED PHASE 3+)

Service name: `prompt-library-service`

### Fetch Prompt
`POST /v1/prompts/get`

```json
{"prompt_id":"supervisor_planner","variant_id":"blue"}
```

### Response
```json
{
  "prompt":{
    "id":"supervisor_planner",
    "variant":{
      "id":"blue",
      "messages":[
        {"role":"system","content":"..."},
        {"role":"user","content":"User: {{USER_INPUT}}"}
      ]
    }
  }
}
```

### Variables
- `{{USER_INPUT}}`
- `{{PLAN_JSON}}`
- `{{HISTORY_JSON}}`
- `{{CONTEXT_METADATA}}`

### Required Prompt IDs
- supervisor_planner
- research_agent
- transform_agent
- finalizer_agent
- hitl_escalation_handler

---

# 8️⃣ PHASE PLAN (SEQUENTIAL)

| Phase | Deliverables |
|-------|---------------|
| 0 | Skeleton, 1 agent, no streaming, Checkpointer |
| 1 | Multi-agent, ToDo planning |
| 2 | HITL |
| 3 | Streaming, AI-SDK FE, genUI, Prompt Library |
| 4 | Blue–Green variant execution + eval comparison |

---

# 9️⃣ TESTING REQUIREMENTS

### Unit Tests
- Routing correctness
- ToDo lifecycle
- AgentSummary schema

### Integration Tests
- DONE path
- ESCALATE path (Phase 2+)
- Streaming parity (Phase 3+)

### Eval Requirements
- correctness: statuses, routing, escalation
- Phase 4+: cross-variant deltas

---

# 🔟 PROHIBITED BEHAVIOR

❌ implicit routing via LLM output  
❌ inline long prompts post-Phase 3  
❌ storing non-serializables in state  
❌ modifying SupervisorState from agents  
❌ silent failures on missing prompts  
❌ infinite tool recursion (enforced by middleware)  

---

# END OF SPEC
