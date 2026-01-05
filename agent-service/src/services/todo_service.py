"""Service layer for todo CRUD operations."""

import logging
import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.db_models import Priority, UserTodo, UserTodoStatus

logger = logging.getLogger(__name__)


class TodoFilters:
    """Filters for querying todos."""

    def __init__(
        self,
        status: Optional[UserTodoStatus] = None,
        priority: Optional[Priority] = None,
        tags: Optional[list[str]] = None,
        parent_id: Optional[str] = None,
    ):
        self.status = status
        self.priority = priority
        self.tags = tags
        self.parent_id = parent_id


class TodoService:
    """Service for managing user todos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_todo(
        self,
        title: str,
        description: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        due_date: Optional[datetime] = None,
        scheduled_for: Optional[datetime] = None,
        estimated_duration: Optional[int] = None,
        tags: Optional[list[str]] = None,
        parent_id: Optional[str] = None,
        ai_generated: bool = False,
    ) -> UserTodo:
        """
        Create a new todo.

        Args:
            title: Todo title (required)
            description: Detailed description
            priority: Priority level (default: MEDIUM)
            due_date: When the todo is due
            scheduled_for: When the todo is scheduled
            estimated_duration: Estimated time in minutes
            tags: List of tags
            parent_id: Parent todo ID for subtasks
            ai_generated: Whether this todo was AI-generated

        Returns:
            Created UserTodo instance
        """
        logger.info(f"Creating todo: {title}")

        todo = UserTodo(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            status=UserTodoStatus.TODO,
            priority=priority,
            due_date=due_date,
            scheduled_for=scheduled_for,
            estimated_duration=estimated_duration,
            tags=tags or [],
            parent_id=parent_id,
            ai_generated=ai_generated,
        )

        self.db.add(todo)
        await self.db.commit()
        await self.db.refresh(todo)

        logger.info(f"Todo created successfully: {todo.id}")
        return todo

    async def get_todos(self, filters: Optional[TodoFilters] = None) -> list[UserTodo]:
        """
        Get list of todos with optional filters.

        Args:
            filters: Optional filters to apply

        Returns:
            List of UserTodo instances matching filters
        """
        logger.info("Fetching todos with filters")

        query = select(UserTodo).options(selectinload(UserTodo.subtasks))

        if filters:
            if filters.status:
                query = query.where(UserTodo.status == filters.status)
            if filters.priority:
                query = query.where(UserTodo.priority == filters.priority)
            if filters.parent_id is not None:
                query = query.where(UserTodo.parent_id == filters.parent_id)
            # For tags, we need to check if any of the filter tags are in the todo's tags
            if filters.tags:
                # This will match any todo that has at least one of the requested tags
                for tag in filters.tags:
                    query = query.where(UserTodo.tags.contains([tag]))

        # Order by created_at descending (newest first)
        query = query.order_by(UserTodo.created_at.desc())

        result = await self.db.execute(query)
        todos = result.scalars().all()

        logger.info(f"Found {len(todos)} todos")
        return list(todos)

    async def get_todo(self, todo_id: str) -> Optional[UserTodo]:
        """
        Get a single todo by ID.

        Args:
            todo_id: Todo ID

        Returns:
            UserTodo instance or None if not found
        """
        logger.info(f"Fetching todo: {todo_id}")

        query = (
            select(UserTodo)
            .where(UserTodo.id == todo_id)
            .options(selectinload(UserTodo.subtasks), selectinload(UserTodo.parent))
        )

        result = await self.db.execute(query)
        todo = result.scalar_one_or_none()

        if todo:
            logger.info(f"Todo found: {todo_id}")
        else:
            logger.warning(f"Todo not found: {todo_id}")

        return todo

    async def update_todo(
        self,
        todo_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority] = None,
        status: Optional[UserTodoStatus] = None,
        due_date: Optional[datetime] = None,
        scheduled_for: Optional[datetime] = None,
        estimated_duration: Optional[int] = None,
        tags: Optional[list[str]] = None,
    ) -> Optional[UserTodo]:
        """
        Update an existing todo.

        Args:
            todo_id: Todo ID
            title: New title
            description: New description
            priority: New priority
            status: New status
            due_date: New due date
            scheduled_for: New scheduled time
            estimated_duration: New estimated duration
            tags: New tags list

        Returns:
            Updated UserTodo instance or None if not found
        """
        logger.info(f"Updating todo: {todo_id}")

        todo = await self.get_todo(todo_id)
        if not todo:
            return None

        if title is not None:
            todo.title = title
        if description is not None:
            todo.description = description
        if priority is not None:
            todo.priority = priority
        if status is not None:
            todo.status = status
            # Set completed_at timestamp if status changed to DONE
            if status == UserTodoStatus.DONE and todo.completed_at is None:
                todo.completed_at = datetime.now(UTC)
            # Clear completed_at if status changed away from DONE
            elif status != UserTodoStatus.DONE:
                todo.completed_at = None
        if due_date is not None:
            todo.due_date = due_date
        if scheduled_for is not None:
            todo.scheduled_for = scheduled_for
        if estimated_duration is not None:
            todo.estimated_duration = estimated_duration
        if tags is not None:
            todo.tags = tags

        todo.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(todo)

        logger.info(f"Todo updated successfully: {todo_id}")
        return todo

    async def update_status(self, todo_id: str, status: UserTodoStatus) -> Optional[UserTodo]:
        """
        Quick update of just the todo status.

        Args:
            todo_id: Todo ID
            status: New status

        Returns:
            Updated UserTodo instance or None if not found
        """
        return await self.update_todo(todo_id, status=status)

    async def delete_todo(self, todo_id: str) -> bool:
        """
        Delete a todo.

        Args:
            todo_id: Todo ID

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting todo: {todo_id}")

        todo = await self.get_todo(todo_id)
        if not todo:
            logger.warning(f"Cannot delete - todo not found: {todo_id}")
            return False

        await self.db.delete(todo)
        await self.db.commit()

        logger.info(f"Todo deleted successfully: {todo_id}")
        return True
