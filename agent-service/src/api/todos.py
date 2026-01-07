"""API endpoints for todo CRUD operations."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.api_models import (
    CreateTodoRequest,
    SubtaskResponse,
    UpdateStatusRequest,
    UpdateTodoRequest,
    UserTodoResponse,
)
from ..models.db_models import Priority, UserTodo, UserTodoStatus
from ..services.todo_service import TodoFilters, TodoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/todos", tags=["todos"])


def _parse_priority(priority_str: str) -> Priority:
    """Parse priority string to Priority enum."""
    try:
        return Priority[priority_str.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: {priority_str}. Must be one of: low, medium, high, urgent",
        )


def _parse_status(status_str: str) -> UserTodoStatus:
    """Parse status string to UserTodoStatus enum."""
    try:
        return UserTodoStatus[status_str.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {status_str}. Must be one of: todo, in_progress, done, archived",
        )


def _todo_to_response(todo: UserTodo) -> UserTodoResponse:
    """Convert UserTodo DB model to API response model."""
    subtasks_response = None
    if todo.subtasks:
        subtasks_response = [
            SubtaskResponse(
                id=subtask.id,
                title=subtask.title,
                status=subtask.status.value,
                priority=subtask.priority.value,
                completed_at=(subtask.completed_at.isoformat() if subtask.completed_at else None),
            )
            for subtask in todo.subtasks
        ]

    return UserTodoResponse(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        status=todo.status.value,
        priority=todo.priority.value,
        ai_generated=todo.ai_generated,
        ai_breakdown=todo.ai_breakdown,
        due_date=todo.due_date.isoformat() if todo.due_date else None,
        scheduled_for=todo.scheduled_for.isoformat() if todo.scheduled_for else None,
        estimated_duration=todo.estimated_duration,
        tags=todo.tags,
        metadata=todo.extra_data,  # DB model uses extra_data, API uses metadata
        created_at=todo.created_at.isoformat(),
        updated_at=todo.updated_at.isoformat(),
        completed_at=todo.completed_at.isoformat() if todo.completed_at else None,
        parent_id=todo.parent_id,
        subtasks=subtasks_response,
    )


@router.get("/", response_model=list[UserTodoResponse])
async def list_todos(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    tags: Optional[list[str]] = Query(None, description="Filter by tags"),
    parent_id: Optional[str] = Query(None, description="Filter by parent_id (null for top-level)"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all todos with optional filters.

    Args:
        status: Filter by status (todo, in_progress, done, archived)
        priority: Filter by priority (low, medium, high, urgent)
        tags: Filter by tags (matches any)
        parent_id: Filter by parent_id (use 'null' string for top-level todos)
        db: Database session

    Returns:
        List of todos matching filters
    """
    logger.info(f"GET /v1/todos - status={status}, priority={priority}, tags={tags}")

    filters = TodoFilters()

    if status:
        filters.status = _parse_status(status)

    if priority:
        filters.priority = _parse_priority(priority)

    if tags:
        filters.tags = tags

    if parent_id == "null":
        filters.parent_id = None
    elif parent_id:
        filters.parent_id = parent_id

    service = TodoService(db)
    todos = await service.get_todos(filters)

    return [_todo_to_response(todo) for todo in todos]


@router.post("/", response_model=UserTodoResponse, status_code=201)
async def create_todo(
    request: CreateTodoRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new todo.

    Args:
        request: Todo creation request
        db: Database session

    Returns:
        Created todo
    """
    logger.info(f"POST /v1/todos - title={request.title}")

    # Parse priority
    priority = _parse_priority(request.priority) if request.priority else Priority.MEDIUM

    # Parse dates
    due_date = None
    if request.due_date:
        try:
            due_date = datetime.fromisoformat(request.due_date)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid due_date format: {request.due_date}"
            )

    scheduled_for = None
    if request.scheduled_for:
        try:
            scheduled_for = datetime.fromisoformat(request.scheduled_for)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scheduled_for format: {request.scheduled_for}",
            )

    service = TodoService(db)
    todo = await service.create_todo(
        title=request.title,
        description=request.description,
        priority=priority,
        due_date=due_date,
        scheduled_for=scheduled_for,
        estimated_duration=request.estimated_duration,
        tags=request.tags,
        parent_id=request.parent_id,
    )

    return _todo_to_response(todo)


@router.get("/{todo_id}", response_model=UserTodoResponse)
async def get_todo(
    todo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single todo by ID.

    Args:
        todo_id: Todo ID
        db: Database session

    Returns:
        Todo details
    """
    logger.info(f"GET /v1/todos/{todo_id}")

    service = TodoService(db)
    todo = await service.get_todo(todo_id)

    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo not found: {todo_id}")

    return _todo_to_response(todo)


@router.put("/{todo_id}", response_model=UserTodoResponse)
async def update_todo(
    todo_id: str,
    request: UpdateTodoRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing todo.

    Args:
        todo_id: Todo ID
        request: Todo update request
        db: Database session

    Returns:
        Updated todo
    """
    logger.info(f"PUT /v1/todos/{todo_id}")

    # Parse priority if provided
    priority = None
    if request.priority:
        priority = _parse_priority(request.priority)

    # Parse status if provided
    status = None
    if request.status:
        status = _parse_status(request.status)

    # Parse dates
    due_date = None
    if request.due_date:
        try:
            due_date = datetime.fromisoformat(request.due_date)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid due_date format: {request.due_date}"
            )

    scheduled_for = None
    if request.scheduled_for:
        try:
            scheduled_for = datetime.fromisoformat(request.scheduled_for)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scheduled_for format: {request.scheduled_for}",
            )

    service = TodoService(db)
    todo = await service.update_todo(
        todo_id=todo_id,
        title=request.title,
        description=request.description,
        priority=priority,
        status=status,
        due_date=due_date,
        scheduled_for=scheduled_for,
        estimated_duration=request.estimated_duration,
        tags=request.tags,
    )

    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo not found: {todo_id}")

    return _todo_to_response(todo)


@router.patch("/{todo_id}/status", response_model=UserTodoResponse)
async def update_todo_status(
    todo_id: str,
    request: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update just the status of a todo.

    Args:
        todo_id: Todo ID
        request: Status update request
        db: Database session

    Returns:
        Updated todo
    """
    logger.info(f"PATCH /v1/todos/{todo_id}/status - status={request.status}")

    status = _parse_status(request.status)

    service = TodoService(db)
    todo = await service.update_status(todo_id, status)

    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo not found: {todo_id}")

    return _todo_to_response(todo)


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a todo.

    Args:
        todo_id: Todo ID
        db: Database session

    Returns:
        No content
    """
    logger.info(f"DELETE /v1/todos/{todo_id}")

    service = TodoService(db)
    deleted = await service.delete_todo(todo_id)

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Todo not found: {todo_id}")

    return None
