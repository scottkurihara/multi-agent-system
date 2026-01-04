import operator
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage

# Type aliases
Status = Literal["RUNNING", "DONE", "ESCALATE"]
ToDoStatus = Literal["PENDING", "IN_PROGRESS", "DONE", "BLOCKED"]
AgentResult = Literal["COMPLETED", "NEEDS_ASSISTANCE", "FAILED"]


class ToDo(TypedDict, total=False):
    id: str
    description: str
    status: ToDoStatus
    owner_agent: str
    parent_id: str
    metadata: dict


class AgentSummary(TypedDict):
    agent_name: str
    step_id: str
    result: AgentResult
    short_summary: str
    key_decisions: list[str]
    next_instructions_for_supervisor: str


class SupervisorState(TypedDict, total=False):
    task_id: str
    context_id: str
    status: Status
    plan: list[ToDo]
    history: list[AgentSummary]
    active_agent: str
    notes: str


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    tool_events: Annotated[list, operator.add]
    recursion_depth: int
    scratchpad: dict


class GraphState(TypedDict):
    supervisor: SupervisorState
    agent: AgentState
