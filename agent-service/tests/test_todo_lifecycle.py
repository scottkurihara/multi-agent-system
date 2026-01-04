from src.models.state import ToDo


def test_create_todo_with_pending_status():
    """Test creating a ToDo with PENDING status."""
    todo: ToDo = {
        "id": "test-id",
        "description": "Test task",
        "status": "PENDING",
        "owner_agent": "research_agent",
    }

    assert todo["status"] == "PENDING"
    assert todo["owner_agent"] == "research_agent"


def test_transition_todo_to_in_progress():
    """Test transitioning ToDo from PENDING to IN_PROGRESS."""
    todo: ToDo = {
        "id": "test-id",
        "description": "Test task",
        "status": "PENDING",
    }

    updated_todo = {**todo, "status": "IN_PROGRESS"}

    assert updated_todo["status"] == "IN_PROGRESS"


def test_transition_todo_to_done():
    """Test transitioning ToDo to DONE."""
    todo: ToDo = {
        "id": "test-id",
        "description": "Test task",
        "status": "IN_PROGRESS",
    }

    updated_todo = {**todo, "status": "DONE"}

    assert updated_todo["status"] == "DONE"


def test_todo_with_metadata():
    """Test ToDo with optional metadata."""
    todo: ToDo = {
        "id": "test-id",
        "description": "Test task",
        "status": "PENDING",
        "metadata": {"priority": "high", "tags": ["urgent"]},
    }

    assert todo["metadata"]["priority"] == "high"
    assert "urgent" in todo["metadata"]["tags"]
