"""AI-assisted todo API endpoints.

These endpoints provide AI-powered features for todo management including
task breakdown, prioritization, scheduling, and completion guidance.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.ai_todo_service import AITodoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/todos/ai", tags=["ai-todos"])


# Request/Response Models


class BreakdownRequest(BaseModel):
    """Request to break down a task."""

    todo_id: str = Field(..., description="ID of the todo to break down")


class BreakdownResponse(BaseModel):
    """Response containing task breakdown."""

    todo_id: str
    breakdown: str
    status: str


class PrioritizeRequest(BaseModel):
    """Request to prioritize multiple tasks."""

    todo_ids: list[str] = Field(..., min_length=1, description="List of todo IDs to prioritize")


class PrioritizeResponse(BaseModel):
    """Response containing prioritization suggestions."""

    todo_ids: list[str]
    suggestions: str
    status: str


class ScheduleRequest(BaseModel):
    """Request to schedule a task."""

    todo_id: str = Field(..., description="ID of the todo to schedule")
    constraints: dict[str, Any] | None = Field(
        None, description="Optional scheduling constraints (working_hours, busy_times, etc.)"
    )


class ScheduleResponse(BaseModel):
    """Response containing scheduling suggestions."""

    todo_id: str
    schedule: str
    status: str


class GuidanceRequest(BaseModel):
    """Request for task completion guidance."""

    todo_id: str = Field(..., description="ID of the todo")


class GuidanceResponse(BaseModel):
    """Response containing step-by-step guidance."""

    todo_id: str
    guidance: str
    status: str


# Endpoints


@router.post("/breakdown", response_model=BreakdownResponse, status_code=200)
async def breakdown_task(
    request: BreakdownRequest,
    db: AsyncSession = Depends(get_db),
) -> BreakdownResponse:
    """Break down a complex task into smaller subtasks using AI.

    This endpoint analyzes a task and provides:
    - Suggested subtasks with clear descriptions
    - Time estimates for each subtask
    - Overall breakdown reasoning

    Args:
        request: Breakdown request with todo_id
        db: Database session

    Returns:
        BreakdownResponse with AI-generated breakdown

    Raises:
        HTTPException: 404 if todo not found, 500 if breakdown fails
    """
    logger.info(f"POST /ai/breakdown - todo_id: {request.todo_id}")

    try:
        ai_service = AITodoService(db)
        result = await ai_service.breakdown_task(request.todo_id)
        return BreakdownResponse(**result)
    except ValueError as e:
        logger.warning(f"Todo not found: {e}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Breakdown failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to break down task") from e


@router.post("/prioritize", response_model=PrioritizeResponse, status_code=200)
async def prioritize_tasks(
    request: PrioritizeRequest,
    db: AsyncSession = Depends(get_db),
) -> PrioritizeResponse:
    """Analyze and suggest priorities for multiple tasks using AI.

    This endpoint uses the Eisenhower Matrix (urgent/important) to suggest
    priorities and provides:
    - Priority suggestions for each task
    - Recommended order to work on tasks
    - Reasoning for prioritization decisions

    Args:
        request: Prioritize request with list of todo_ids
        db: Database session

    Returns:
        PrioritizeResponse with AI-generated priority suggestions

    Raises:
        HTTPException: 404 if no valid todos found, 500 if prioritization fails
    """
    logger.info(f"POST /ai/prioritize - {len(request.todo_ids)} todos")

    try:
        ai_service = AITodoService(db)
        result = await ai_service.prioritize_tasks(request.todo_ids)
        return PrioritizeResponse(**result)
    except ValueError as e:
        logger.warning(f"Invalid todos: {e}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Prioritization failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to prioritize tasks") from e


@router.post("/schedule", response_model=ScheduleResponse, status_code=200)
async def schedule_task(
    request: ScheduleRequest,
    db: AsyncSession = Depends(get_db),
) -> ScheduleResponse:
    """Suggest optimal scheduling for a task using AI.

    This endpoint considers duration, deadline, and user constraints to suggest:
    - Recommended time blocks for the task
    - Scheduling strategy (e.g., single block vs. multiple sessions)
    - Tips for completing on time

    Args:
        request: Schedule request with todo_id and optional constraints
        db: Database session

    Returns:
        ScheduleResponse with AI-generated scheduling suggestions

    Raises:
        HTTPException: 404 if todo not found, 500 if scheduling fails
    """
    logger.info(f"POST /ai/schedule - todo_id: {request.todo_id}")

    try:
        ai_service = AITodoService(db)
        result = await ai_service.schedule_task(request.todo_id, request.constraints)
        return ScheduleResponse(**result)
    except ValueError as e:
        logger.warning(f"Todo not found: {e}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Scheduling failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to schedule task") from e


@router.post("/guidance", response_model=GuidanceResponse, status_code=200)
async def generate_guidance(
    request: GuidanceRequest,
    db: AsyncSession = Depends(get_db),
) -> GuidanceResponse:
    """Generate step-by-step guidance for completing a task using AI.

    This endpoint provides detailed, actionable guidance including:
    - Step-by-step instructions with descriptions
    - Helpful tips for each step
    - Suggested resources or tools
    - Common pitfalls to avoid

    Args:
        request: Guidance request with todo_id
        db: Database session

    Returns:
        GuidanceResponse with AI-generated completion guidance

    Raises:
        HTTPException: 404 if todo not found, 500 if guidance generation fails
    """
    logger.info(f"POST /ai/guidance - todo_id: {request.todo_id}")

    try:
        ai_service = AITodoService(db)
        result = await ai_service.generate_task_guidance(request.todo_id)
        return GuidanceResponse(**result)
    except ValueError as e:
        logger.warning(f"Todo not found: {e}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Guidance generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate task guidance") from e


@router.post("/suggest-next", status_code=200)
async def suggest_next_task(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Suggest the next task to work on based on priorities and context.

    This endpoint analyzes all active todos and suggests which task to work
    on next, considering:
    - Priorities and deadlines
    - Task dependencies
    - User's current context
    - Time availability

    Args:
        db: Database session

    Returns:
        Dictionary with suggested task and reasoning

    Raises:
        HTTPException: 500 if suggestion fails
    """
    logger.info("POST /ai/suggest-next")

    try:
        ai_service = AITodoService(db)

        # Get all active todos
        from ..models.db_models import UserTodoStatus
        from ..services.todo_service import TodoFilters

        filters = TodoFilters(status=UserTodoStatus.TODO)
        active_todos = await ai_service.todo_service.get_todos(filters)

        if not active_todos:
            return {
                "suggestion": "No active tasks found. Create a new task to get started!",
                "todo_id": None,
            }

        # Get prioritization for all active tasks
        todo_ids = [todo.id for todo in active_todos]
        result = await ai_service.prioritize_tasks(todo_ids)

        return {
            "suggestion": result["suggestions"],
            "todo_ids": result["todo_ids"],
            "status": result["status"],
        }
    except Exception as e:
        logger.error(f"Next task suggestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to suggest next task") from e
