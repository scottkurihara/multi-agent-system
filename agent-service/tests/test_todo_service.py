"""Tests for TodoService CRUD operations."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models.db_models import Base, Priority, UserTodoStatus
from src.services.todo_service import TodoFilters, TodoService

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create a test database session."""
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


@pytest.fixture
def todo_service(db_session):
    """Create a TodoService instance with test database."""
    return TodoService(db_session)


class TestTodoServiceCreate:
    """Tests for creating todos."""

    @pytest.mark.asyncio
    async def test_create_todo_minimal(self, todo_service):
        """Test creating a todo with only required fields."""
        todo = await todo_service.create_todo(title="Buy milk")

        assert todo.id is not None
        assert todo.title == "Buy milk"
        assert todo.status == UserTodoStatus.TODO
        assert todo.priority == Priority.MEDIUM
        assert todo.ai_generated is False
        assert todo.created_at is not None

    @pytest.mark.asyncio
    async def test_create_todo_with_all_fields(self, todo_service):
        """Test creating a todo with all fields populated."""
        due_date = datetime(2026, 1, 10, 15, 0, tzinfo=UTC)
        scheduled_for = datetime(2026, 1, 9, 9, 0, tzinfo=UTC)

        todo = await todo_service.create_todo(
            title="Complete project",
            description="Finish the todo app",
            priority=Priority.HIGH,
            due_date=due_date,
            scheduled_for=scheduled_for,
            estimated_duration=120,
            tags=["work", "urgent"],
            ai_generated=True,
        )

        assert todo.title == "Complete project"
        assert todo.description == "Finish the todo app"
        assert todo.priority == Priority.HIGH
        assert todo.due_date == due_date
        assert todo.scheduled_for == scheduled_for
        assert todo.estimated_duration == 120
        assert todo.tags == ["work", "urgent"]
        assert todo.ai_generated is True

    @pytest.mark.asyncio
    async def test_create_subtask(self, todo_service):
        """Test creating a subtask with parent_id."""
        parent = await todo_service.create_todo(title="Parent task")
        subtask = await todo_service.create_todo(
            title="Subtask",
            parent_id=parent.id,
        )

        assert subtask.parent_id == parent.id


class TestTodoServiceRead:
    """Tests for reading todos."""

    @pytest.mark.asyncio
    async def test_get_todo_by_id(self, todo_service):
        """Test getting a single todo by ID."""
        created = await todo_service.create_todo(title="Test todo")
        fetched = await todo_service.get_todo(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.title == created.title

    @pytest.mark.asyncio
    async def test_get_todo_not_found(self, todo_service):
        """Test getting a non-existent todo returns None."""
        result = await todo_service.get_todo("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_todos_empty(self, todo_service):
        """Test getting todos when database is empty."""
        todos = await todo_service.get_todos()
        assert todos == []

    @pytest.mark.asyncio
    async def test_get_todos_returns_all(self, todo_service):
        """Test getting all todos."""
        await todo_service.create_todo(title="Todo 1")
        await todo_service.create_todo(title="Todo 2")
        await todo_service.create_todo(title="Todo 3")

        todos = await todo_service.get_todos()
        assert len(todos) == 3

    @pytest.mark.asyncio
    async def test_get_todos_filter_by_status(self, todo_service):
        """Test filtering todos by status."""
        todo1 = await todo_service.create_todo(title="Todo 1")
        await todo_service.create_todo(title="Todo 2")
        await todo_service.update_status(todo1.id, UserTodoStatus.DONE)

        filters = TodoFilters(status=UserTodoStatus.DONE)
        todos = await todo_service.get_todos(filters)

        assert len(todos) == 1
        assert todos[0].id == todo1.id

    @pytest.mark.asyncio
    async def test_get_todos_filter_by_priority(self, todo_service):
        """Test filtering todos by priority."""
        await todo_service.create_todo(title="Low priority", priority=Priority.LOW)
        urgent = await todo_service.create_todo(title="Urgent", priority=Priority.URGENT)

        filters = TodoFilters(priority=Priority.URGENT)
        todos = await todo_service.get_todos(filters)

        assert len(todos) == 1
        assert todos[0].id == urgent.id

    @pytest.mark.asyncio
    async def test_get_todos_filter_by_tags(self, todo_service):
        """Test filtering todos by tags."""
        await todo_service.create_todo(title="Work todo", tags=["work"])
        personal = await todo_service.create_todo(title="Personal todo", tags=["personal"])

        filters = TodoFilters(tags=["personal"])
        todos = await todo_service.get_todos(filters)

        assert len(todos) == 1
        assert todos[0].id == personal.id

    @pytest.mark.asyncio
    async def test_get_todos_with_subtasks(self, todo_service):
        """Test that fetching todos includes subtasks."""
        parent = await todo_service.create_todo(title="Parent")
        await todo_service.create_todo(title="Child 1", parent_id=parent.id)
        await todo_service.create_todo(title="Child 2", parent_id=parent.id)

        fetched = await todo_service.get_todo(parent.id)

        assert fetched is not None
        assert len(fetched.subtasks) == 2


class TestTodoServiceUpdate:
    """Tests for updating todos."""

    @pytest.mark.asyncio
    async def test_update_todo_title(self, todo_service):
        """Test updating todo title."""
        todo = await todo_service.create_todo(title="Original title")
        updated = await todo_service.update_todo(todo.id, title="New title")

        assert updated is not None
        assert updated.title == "New title"

    @pytest.mark.asyncio
    async def test_update_todo_description(self, todo_service):
        """Test updating todo description."""
        todo = await todo_service.create_todo(title="Todo")
        updated = await todo_service.update_todo(todo.id, description="New description")

        assert updated.description == "New description"

    @pytest.mark.asyncio
    async def test_update_todo_priority(self, todo_service):
        """Test updating todo priority."""
        todo = await todo_service.create_todo(title="Todo")
        updated = await todo_service.update_todo(todo.id, priority=Priority.URGENT)

        assert updated.priority == Priority.URGENT

    @pytest.mark.asyncio
    async def test_update_todo_status(self, todo_service):
        """Test updating todo status."""
        todo = await todo_service.create_todo(title="Todo")
        updated = await todo_service.update_todo(todo.id, status=UserTodoStatus.DONE)

        assert updated.status == UserTodoStatus.DONE
        assert updated.completed_at is not None

    @pytest.mark.asyncio
    async def test_update_status_sets_completed_at(self, todo_service):
        """Test that updating to DONE sets completed_at timestamp."""
        todo = await todo_service.create_todo(title="Todo")
        updated = await todo_service.update_status(todo.id, UserTodoStatus.DONE)

        assert updated.completed_at is not None

    @pytest.mark.asyncio
    async def test_update_status_clears_completed_at(self, todo_service):
        """Test that updating away from DONE clears completed_at."""
        todo = await todo_service.create_todo(title="Todo")
        # First mark as done
        await todo_service.update_status(todo.id, UserTodoStatus.DONE)
        # Then mark as in_progress
        updated = await todo_service.update_status(todo.id, UserTodoStatus.IN_PROGRESS)

        assert updated.completed_at is None

    @pytest.mark.asyncio
    async def test_update_todo_tags(self, todo_service):
        """Test updating todo tags."""
        todo = await todo_service.create_todo(title="Todo", tags=["old"])
        updated = await todo_service.update_todo(todo.id, tags=["new", "tags"])

        assert updated.tags == ["new", "tags"]

    @pytest.mark.asyncio
    async def test_update_todo_not_found(self, todo_service):
        """Test updating non-existent todo returns None."""
        result = await todo_service.update_todo("nonexistent-id", title="New title")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_todo_multiple_fields(self, todo_service):
        """Test updating multiple fields at once."""
        todo = await todo_service.create_todo(title="Todo")
        updated = await todo_service.update_todo(
            todo.id,
            title="New title",
            description="New description",
            priority=Priority.HIGH,
            status=UserTodoStatus.IN_PROGRESS,
        )

        assert updated.title == "New title"
        assert updated.description == "New description"
        assert updated.priority == Priority.HIGH
        assert updated.status == UserTodoStatus.IN_PROGRESS


class TestTodoServiceDelete:
    """Tests for deleting todos."""

    @pytest.mark.asyncio
    async def test_delete_todo(self, todo_service):
        """Test deleting a todo."""
        todo = await todo_service.create_todo(title="Todo to delete")
        result = await todo_service.delete_todo(todo.id)

        assert result is True

        # Verify it's gone
        fetched = await todo_service.get_todo(todo.id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_todo_not_found(self, todo_service):
        """Test deleting non-existent todo returns False."""
        result = await todo_service.delete_todo("nonexistent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_todo_with_subtasks(self, todo_service):
        """Test deleting a todo with subtasks."""
        parent = await todo_service.create_todo(title="Parent")
        child = await todo_service.create_todo(title="Child", parent_id=parent.id)

        # Delete parent
        result = await todo_service.delete_todo(parent.id)
        assert result is True

        # Child should also be deleted (cascade)
        fetched_child = await todo_service.get_todo(child.id)
        assert fetched_child is None
