"""Tests for Todo CRUD API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.server import app
from src.models.db_models import Priority, UserTodo, UserTodoStatus


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def sample_todo():
    """Create a sample UserTodo for testing."""
    todo = UserTodo(
        id="test-id-123",
        title="Test todo",
        description="Test description",
        status=UserTodoStatus.TODO,
        priority=Priority.MEDIUM,
        ai_generated=False,
        tags=["test"],
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
    )
    todo.subtasks = []
    return todo


class TestListTodos:
    """Tests for GET /v1/todos/"""

    @patch("src.api.todos.TodoService")
    def test_list_todos_empty(self, mock_service_class, client, mock_db_session):
        """Test listing todos when database is empty."""
        mock_service = AsyncMock()
        mock_service.get_todos = AsyncMock(return_value=[])
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.get("/v1/todos/")

        assert response.status_code == 200
        assert response.json() == []

    @patch("src.api.todos.TodoService")
    def test_list_todos_with_data(self, mock_service_class, client, mock_db_session, sample_todo):
        """Test listing todos returns data."""
        mock_service = AsyncMock()
        mock_service.get_todos = AsyncMock(return_value=[sample_todo])
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.get("/v1/todos/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "test-id-123"
        assert data[0]["title"] == "Test todo"

    @patch("src.api.todos.TodoService")
    def test_list_todos_with_status_filter(self, mock_service_class, client, mock_db_session):
        """Test filtering todos by status."""
        mock_service = AsyncMock()
        mock_service.get_todos = AsyncMock(return_value=[])
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.get("/v1/todos/?status=done")

        assert response.status_code == 200
        # Verify the filter was applied
        mock_service.get_todos.assert_called_once()

    def test_list_todos_with_invalid_status(self, client):
        """Test that invalid status returns 400."""
        response = client.get("/v1/todos/?status=invalid_status")
        assert response.status_code == 400
        assert "Invalid status" in response.json()["detail"]

    def test_list_todos_with_invalid_priority(self, client):
        """Test that invalid priority returns 400."""
        response = client.get("/v1/todos/?priority=invalid_priority")
        assert response.status_code == 400
        assert "Invalid priority" in response.json()["detail"]


class TestCreateTodo:
    """Tests for POST /v1/todos/"""

    @patch("src.api.todos.TodoService")
    def test_create_todo_minimal(self, mock_service_class, client, mock_db_session, sample_todo):
        """Test creating a todo with minimal fields."""
        mock_service = AsyncMock()
        mock_service.create_todo = AsyncMock(return_value=sample_todo)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.post(
                "/v1/todos/",
                json={"title": "Test todo"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test todo"

    @patch("src.api.todos.TodoService")
    def test_create_todo_with_all_fields(
        self, mock_service_class, client, mock_db_session, sample_todo
    ):
        """Test creating a todo with all fields."""
        mock_service = AsyncMock()
        mock_service.create_todo = AsyncMock(return_value=sample_todo)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.post(
                "/v1/todos/",
                json={
                    "title": "Complete project",
                    "description": "Finish the app",
                    "priority": "high",
                    "due_date": "2026-01-10T15:00:00+00:00",
                    "scheduled_for": "2026-01-09T09:00:00+00:00",
                    "estimated_duration": 120,
                    "tags": ["work", "urgent"],
                },
            )

        assert response.status_code == 201

    def test_create_todo_missing_title(self, client):
        """Test that missing title returns 422."""
        response = client.post("/v1/todos/", json={})
        assert response.status_code == 422

    def test_create_todo_invalid_priority(self, client):
        """Test that invalid priority returns 400."""
        response = client.post(
            "/v1/todos/",
            json={"title": "Test", "priority": "invalid"},
        )
        assert response.status_code == 400
        assert "Invalid priority" in response.json()["detail"]

    def test_create_todo_invalid_date_format(self, client):
        """Test that invalid date format returns 400."""
        response = client.post(
            "/v1/todos/",
            json={"title": "Test", "due_date": "not-a-date"},
        )
        assert response.status_code == 400


class TestGetTodo:
    """Tests for GET /v1/todos/{todo_id}"""

    @patch("src.api.todos.TodoService")
    def test_get_todo_found(self, mock_service_class, client, mock_db_session, sample_todo):
        """Test getting an existing todo."""
        mock_service = AsyncMock()
        mock_service.get_todo = AsyncMock(return_value=sample_todo)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.get("/v1/todos/test-id-123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-id-123"
        assert data["title"] == "Test todo"

    @patch("src.api.todos.TodoService")
    def test_get_todo_not_found(self, mock_service_class, client, mock_db_session):
        """Test getting a non-existent todo returns 404."""
        mock_service = AsyncMock()
        mock_service.get_todo = AsyncMock(return_value=None)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.get("/v1/todos/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUpdateTodo:
    """Tests for PUT /v1/todos/{todo_id}"""

    @patch("src.api.todos.TodoService")
    def test_update_todo_title(self, mock_service_class, client, mock_db_session, sample_todo):
        """Test updating todo title."""
        updated_todo = sample_todo
        updated_todo.title = "Updated title"

        mock_service = AsyncMock()
        mock_service.update_todo = AsyncMock(return_value=updated_todo)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.put(
                "/v1/todos/test-id-123",
                json={"title": "Updated title"},
            )

        assert response.status_code == 200
        assert response.json()["title"] == "Updated title"

    @patch("src.api.todos.TodoService")
    def test_update_todo_status(self, mock_service_class, client, mock_db_session, sample_todo):
        """Test updating todo status."""
        updated_todo = sample_todo
        updated_todo.status = UserTodoStatus.DONE

        mock_service = AsyncMock()
        mock_service.update_todo = AsyncMock(return_value=updated_todo)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.put(
                "/v1/todos/test-id-123",
                json={"status": "done"},
            )

        assert response.status_code == 200

    @patch("src.api.todos.TodoService")
    def test_update_todo_not_found(self, mock_service_class, client, mock_db_session):
        """Test updating non-existent todo returns 404."""
        mock_service = AsyncMock()
        mock_service.update_todo = AsyncMock(return_value=None)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.put(
                "/v1/todos/nonexistent",
                json={"title": "New title"},
            )

        assert response.status_code == 404

    def test_update_todo_invalid_status(self, client):
        """Test that invalid status returns 400."""
        response = client.put(
            "/v1/todos/test-id",
            json={"status": "invalid_status"},
        )
        assert response.status_code == 400


class TestUpdateTodoStatus:
    """Tests for PATCH /v1/todos/{todo_id}/status"""

    @patch("src.api.todos.TodoService")
    def test_update_status(self, mock_service_class, client, mock_db_session, sample_todo):
        """Test updating only the status."""
        updated_todo = sample_todo
        updated_todo.status = UserTodoStatus.IN_PROGRESS

        mock_service = AsyncMock()
        mock_service.update_status = AsyncMock(return_value=updated_todo)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.patch(
                "/v1/todos/test-id-123/status",
                json={"status": "in_progress"},
            )

        assert response.status_code == 200

    @patch("src.api.todos.TodoService")
    def test_update_status_not_found(self, mock_service_class, client, mock_db_session):
        """Test updating status of non-existent todo returns 404."""
        mock_service = AsyncMock()
        mock_service.update_status = AsyncMock(return_value=None)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.patch(
                "/v1/todos/nonexistent/status",
                json={"status": "done"},
            )

        assert response.status_code == 404

    def test_update_status_invalid(self, client):
        """Test that invalid status returns 400."""
        response = client.patch(
            "/v1/todos/test-id/status",
            json={"status": "invalid_status"},
        )
        assert response.status_code == 400


class TestDeleteTodo:
    """Tests for DELETE /v1/todos/{todo_id}"""

    @patch("src.api.todos.TodoService")
    def test_delete_todo(self, mock_service_class, client, mock_db_session):
        """Test deleting a todo."""
        mock_service = AsyncMock()
        mock_service.delete_todo = AsyncMock(return_value=True)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.delete("/v1/todos/test-id-123")

        assert response.status_code == 204

    @patch("src.api.todos.TodoService")
    def test_delete_todo_not_found(self, mock_service_class, client, mock_db_session):
        """Test deleting non-existent todo returns 404."""
        mock_service = AsyncMock()
        mock_service.delete_todo = AsyncMock(return_value=False)
        mock_service_class.return_value = mock_service

        with patch("src.api.todos.get_db", return_value=mock_db_session):
            response = client.delete("/v1/todos/nonexistent")

        assert response.status_code == 404
