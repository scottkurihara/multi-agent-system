from typing import Literal, Optional

from pydantic import BaseModel, Field

ErrorCode = Literal[
    "INVALID_REQUEST",
    "PROMPT_MISSING",
    "RUN_NOT_FOUND",
    "INTERNAL_ERROR",
    "STREAM_NOT_SUPPORTED",
]


class AgentInput(BaseModel):
    task: str
    context: Optional[dict] = Field(default_factory=dict)


class AgentOptions(BaseModel):
    system_variant: str = "blue"
    stream: bool = False
    run_id: Optional[str] = None


class AgentRequest(BaseModel):
    input: AgentInput
    options: Optional[AgentOptions] = Field(default_factory=AgentOptions)


class OutputData(BaseModel):
    type: str = "text"
    content: str


class ResultData(BaseModel):
    status: str
    output: OutputData
    supervisor_state: dict


class Metadata(BaseModel):
    run_id: str
    system_variant: str
    trace_url: Optional[str] = None


class AgentResponse(BaseModel):
    result: ResultData
    metadata: Metadata


class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ============================================================================
# Todo API Models
# ============================================================================


class CreateTodoRequest(BaseModel):
    """Request model for creating a todo."""

    title: str = Field(..., min_length=1, max_length=500, description="Todo title")
    description: Optional[str] = Field(None, description="Detailed description")
    priority: Optional[str] = Field("medium", description="Priority: low, medium, high, urgent")
    due_date: Optional[str] = Field(None, description="Due date (ISO 8601 format)")
    scheduled_for: Optional[str] = Field(None, description="Scheduled time (ISO 8601 format)")
    estimated_duration: Optional[int] = Field(
        None, description="Estimated duration in minutes", ge=0
    )
    tags: Optional[list[str]] = Field(default_factory=list, description="List of tags")
    parent_id: Optional[str] = Field(None, description="Parent todo ID for subtasks")


class UpdateTodoRequest(BaseModel):
    """Request model for updating a todo."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    scheduled_for: Optional[str] = None
    estimated_duration: Optional[int] = Field(None, ge=0)
    tags: Optional[list[str]] = None


class UpdateStatusRequest(BaseModel):
    """Request model for updating just the status."""

    status: str = Field(..., description="New status: todo, in_progress, done, archived")


class SubtaskResponse(BaseModel):
    """Response model for a subtask (simplified, no nested subtasks)."""

    id: str
    title: str
    status: str
    priority: str
    completed_at: Optional[str] = None


class UserTodoResponse(BaseModel):
    """Response model for a user todo."""

    id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    ai_generated: bool
    ai_breakdown: Optional[dict] = None
    due_date: Optional[str] = None
    scheduled_for: Optional[str] = None
    estimated_duration: Optional[int] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    parent_id: Optional[str] = None
    subtasks: Optional[list[SubtaskResponse]] = None

    class Config:
        from_attributes = True
