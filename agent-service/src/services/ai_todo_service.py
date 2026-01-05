"""AI-powered todo service that bridges CRUD operations with the agent system.

This service orchestrates interactions between the TodoService (database CRUD)
and the LangGraph multi-agent system to provide AI-assisted features.
"""

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..graph.workflow import create_graph
from ..models.state import GraphState
from .todo_service import TodoService

logger = logging.getLogger(__name__)


class AITodoService:
    """Bridge service between TodoService and multi-agent system."""

    def __init__(self, db: AsyncSession):
        """Initialize AI todo service.

        Args:
            db: Database session for CRUD operations
        """
        self.db = db
        self.todo_service = TodoService(db)
        self.graph = create_graph()

    async def breakdown_task(self, todo_id: str) -> dict[str, Any]:
        """Break down a complex task into subtasks using AI.

        Args:
            todo_id: ID of the todo to break down

        Returns:
            Dictionary containing:
            - subtasks: List of suggested subtasks
            - total_estimate_minutes: Total time estimate
            - reasoning: AI's explanation
            - todo_id: Original todo ID

        Raises:
            ValueError: If todo not found
        """
        logger.info(f"AI breakdown requested for todo: {todo_id}")

        # 1. Fetch todo from database
        todo = await self.todo_service.get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} not found")

        # 2. Prepare GraphState with context
        run_id = str(uuid.uuid4())
        initial_state: GraphState = {
            "supervisor": {
                "status": "RUNNING",
                "plan": [],
                "history": [],
                "notes": f"Break down this task: {todo.title}. "
                f"Description: {todo.description or 'No description provided'}",
                "active_agent": None,
                "context_id": todo_id,
                "tool_results": [],
            },
            "agent": {
                "messages": [],
                "tool_events": [],
                "recursion_depth": 0,
                "scratchpad": {},
            },
        }

        # 3. Invoke graph
        logger.debug(f"Invoking graph for breakdown with run_id: {run_id}")
        result = await self.graph.ainvoke(
            initial_state, config={"configurable": {"thread_id": run_id}}
        )

        # 4. Parse result from supervisor state
        supervisor_state = result["supervisor"]
        notes = supervisor_state.get("notes", "")

        # The breakdown_task tool should have been called and results stored
        # We'll return the notes which contain the AI's response
        logger.info(f"Breakdown completed for todo: {todo_id}")

        return {
            "todo_id": todo_id,
            "breakdown": notes,
            "status": supervisor_state.get("status"),
        }

    async def prioritize_tasks(self, todo_ids: list[str]) -> dict[str, Any]:
        """Suggest priorities for multiple tasks using AI.

        Args:
            todo_ids: List of todo IDs to prioritize

        Returns:
            Dictionary containing:
            - priority_suggestions: List of priority suggestions
            - recommended_order: Suggested order to work on tasks
            - reasoning: AI's explanation
        """
        logger.info(f"AI prioritization requested for {len(todo_ids)} todos")

        # 1. Fetch todos from database
        todos = []
        for todo_id in todo_ids:
            todo = await self.todo_service.get_todo(todo_id)
            if todo:
                todos.append(todo)

        if not todos:
            raise ValueError("No valid todos found")

        # 2. Prepare task data for AI
        todos_text = "\n".join(
            [
                f"- [{todo.id}] {todo.title} "
                f"(Priority: {todo.priority.value}, Status: {todo.status.value}, "
                f"Due: {todo.due_date or 'none'})"
                for todo in todos
            ]
        )

        # 3. Prepare GraphState
        run_id = str(uuid.uuid4())
        initial_state: GraphState = {
            "supervisor": {
                "status": "RUNNING",
                "plan": [],
                "history": [],
                "notes": f"Prioritize these tasks:\n{todos_text}",
                "active_agent": None,
                "tool_results": [],
            },
            "agent": {
                "messages": [],
                "tool_events": [],
                "recursion_depth": 0,
                "scratchpad": {},
            },
        }

        # 4. Invoke graph
        logger.debug(f"Invoking graph for prioritization with run_id: {run_id}")
        result = await self.graph.ainvoke(
            initial_state, config={"configurable": {"thread_id": run_id}}
        )

        # 5. Parse result
        supervisor_state = result["supervisor"]
        notes = supervisor_state.get("notes", "")

        logger.info(f"Prioritization completed for {len(todos)} todos")

        return {
            "todo_ids": todo_ids,
            "suggestions": notes,
            "status": supervisor_state.get("status"),
        }

    async def schedule_task(
        self, todo_id: str, constraints: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Suggest optimal scheduling for a task using AI.

        Args:
            todo_id: ID of the todo to schedule
            constraints: Optional user constraints (working_hours, busy_times, etc.)

        Returns:
            Dictionary containing:
            - suggested_schedule: Recommended time blocks
            - scheduling_strategy: AI's approach explanation
            - tips: Tips for completing on time
        """
        logger.info(f"AI scheduling requested for todo: {todo_id}")

        # 1. Fetch todo from database
        todo = await self.todo_service.get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} not found")

        # 2. Prepare context
        constraints_text = ""
        if constraints:
            constraints_text = f"\nUser constraints: {constraints}"

        notes = (
            f"Schedule this task: {todo.title}\n"
            f"Description: {todo.description or 'No description'}\n"
            f"Estimated duration: {todo.estimated_duration or 'unknown'} minutes\n"
            f"Due date: {todo.due_date or 'not set'}"
            f"{constraints_text}"
        )

        # 3. Prepare GraphState
        run_id = str(uuid.uuid4())
        initial_state: GraphState = {
            "supervisor": {
                "status": "RUNNING",
                "plan": [],
                "history": [],
                "notes": notes,
                "active_agent": None,
                "context_id": todo_id,
                "tool_results": [],
            },
            "agent": {
                "messages": [],
                "tool_events": [],
                "recursion_depth": 0,
                "scratchpad": {},
            },
        }

        # 4. Invoke graph
        logger.debug(f"Invoking graph for scheduling with run_id: {run_id}")
        result = await self.graph.ainvoke(
            initial_state, config={"configurable": {"thread_id": run_id}}
        )

        # 5. Parse result
        supervisor_state = result["supervisor"]
        notes_result = supervisor_state.get("notes", "")

        logger.info(f"Scheduling completed for todo: {todo_id}")

        return {
            "todo_id": todo_id,
            "schedule": notes_result,
            "status": supervisor_state.get("status"),
        }

    async def generate_task_guidance(self, todo_id: str) -> dict[str, Any]:
        """Generate step-by-step guidance for completing a task using AI.

        Args:
            todo_id: ID of the todo

        Returns:
            Dictionary containing:
            - steps: Step-by-step instructions
            - tips: Helpful tips
            - resources: Suggested resources
        """
        logger.info(f"AI guidance requested for todo: {todo_id}")

        # 1. Fetch todo from database
        todo = await self.todo_service.get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} not found")

        # 2. Prepare GraphState
        run_id = str(uuid.uuid4())
        initial_state: GraphState = {
            "supervisor": {
                "status": "RUNNING",
                "plan": [],
                "history": [],
                "notes": f"Provide step-by-step guidance for this task: {todo.title}. "
                f"Description: {todo.description or 'No description provided'}",
                "active_agent": None,
                "context_id": todo_id,
                "tool_results": [],
            },
            "agent": {
                "messages": [],
                "tool_events": [],
                "recursion_depth": 0,
                "scratchpad": {},
            },
        }

        # 3. Invoke graph
        logger.debug(f"Invoking graph for guidance with run_id: {run_id}")
        result = await self.graph.ainvoke(
            initial_state, config={"configurable": {"thread_id": run_id}}
        )

        # 4. Parse result
        supervisor_state = result["supervisor"]
        notes = supervisor_state.get("notes", "")

        logger.info(f"Guidance generation completed for todo: {todo_id}")

        return {
            "todo_id": todo_id,
            "guidance": notes,
            "status": supervisor_state.get("status"),
        }
