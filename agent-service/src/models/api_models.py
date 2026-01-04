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
