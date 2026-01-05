"""Database models for user-facing todos and agent interactions."""

import enum
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Priority(enum.Enum):
    """Priority levels for todos."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class UserTodoStatus(enum.Enum):
    """Status values for user todos."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ARCHIVED = "archived"


class UserTodo(Base):
    """
    User-facing todo items.

    This is separate from the internal ToDo class used by agents for planning.
    UserTodos are persisted in the database and represent actual user tasks.
    """

    __tablename__ = "user_todos"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[UserTodoStatus] = mapped_column(
        Enum(UserTodoStatus), default=UserTodoStatus.TODO
    )
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.MEDIUM)

    # AI-assisted fields
    ai_generated: Mapped[bool] = mapped_column(default=False)
    ai_breakdown: Mapped[Optional[dict]] = mapped_column(JSON)  # Stores sub-tasks suggested by AI
    ai_context: Mapped[Optional[dict]] = mapped_column(JSON)  # Stores agent interaction history

    # Scheduling
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer)  # minutes

    # Metadata
    tags: Mapped[Optional[list]] = mapped_column(JSON)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships - self-referential for subtasks
    parent_id: Mapped[Optional[str]] = mapped_column(ForeignKey("user_todos.id"))
    parent: Mapped[Optional["UserTodo"]] = relationship(
        "UserTodo", remote_side=[id], back_populates="subtasks"
    )
    subtasks: Mapped[list["UserTodo"]] = relationship("UserTodo", back_populates="parent")

    def __repr__(self) -> str:
        return f"<UserTodo(id={self.id}, title={self.title}, status={self.status})>"


class AgentInteraction(Base):
    """
    Tracks interactions between users and AI agents for todos.

    Stores the history of AI operations performed on todos, including
    breakdowns, prioritizations, scheduling suggestions, etc.
    """

    __tablename__ = "agent_interactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    todo_id: Mapped[Optional[str]] = mapped_column(ForeignKey("user_todos.id"))
    interaction_type: Mapped[str] = mapped_column(
        String
    )  # "breakdown", "prioritize", "schedule", "suggest"
    user_message: Mapped[str] = mapped_column(String)
    agent_response: Mapped[dict] = mapped_column(JSON)
    supervisor_state: Mapped[Optional[dict]] = mapped_column(JSON)  # Snapshot of supervisor state
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    def __repr__(self) -> str:
        return f"<AgentInteraction(id={self.id}, type={self.interaction_type}, todo_id={self.todo_id})>"
