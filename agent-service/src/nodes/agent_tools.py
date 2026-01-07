"""Tool functions that can be called by the supervisor agent.

These tools enable AI-assisted operations on todos, including breakdown,
prioritization, scheduling, and step-by-step guidance.
"""

import json
import logging
from collections import defaultdict
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Tool call tracking to detect loops
_tool_call_counts = defaultdict(int)
MAX_TOOL_CALLS = 3  # Maximum times a tool can be called in one session


def track_tool_call(tool_name: str) -> bool:
    """Track tool calls and return False if limit exceeded.

    Returns:
        True if call is allowed, False if limit exceeded
    """
    _tool_call_counts[tool_name] += 1
    count = _tool_call_counts[tool_name]

    logger.info(f"Tool '{tool_name}' called {count} time(s)")

    if count > MAX_TOOL_CALLS:
        logger.warning(
            f"Tool '{tool_name}' exceeded call limit ({MAX_TOOL_CALLS}). "
            f"This may indicate an infinite loop."
        )
        return False

    return True


def reset_tool_tracking():
    """Reset tool call tracking (call at start of new session)."""
    _tool_call_counts.clear()
    logger.debug("Tool call tracking reset")


# Initialize LLM for tool use
def get_llm(temperature: float = 0.7) -> ChatAnthropic:
    """Get Claude LLM instance for tool operations."""
    return ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        temperature=temperature,
    )


@tool
async def breakdown_task(
    todo_id: str,
    todo_title: str,
    todo_description: str | None = None,
) -> dict[str, Any]:
    """Break down a complex task into smaller, manageable subtasks.

    Use this tool when a user wants to break down a large or complex todo
    into smaller actionable steps. The AI will analyze the task and suggest
    subtasks with time estimates.

    Args:
        todo_id: The ID of the todo to break down
        todo_title: The title of the todo
        todo_description: Optional detailed description of the todo

    Returns:
        Dictionary containing:
        - subtasks: List of suggested subtasks with titles and descriptions
        - estimates: Time estimates in minutes for each subtask
        - total_estimate: Total estimated time
        - reasoning: Explanation of the breakdown approach
    """
    logger.info(f"Breaking down task: {todo_title}")

    llm = get_llm(temperature=0.7)

    prompt = f"""You are helping break down a complex task into manageable subtasks.

Task: {todo_title}
{f"Description: {todo_description}" if todo_description else ""}

Please analyze this task and break it down into 3-7 smaller, actionable subtasks.
For each subtask, provide:
1. A clear, action-oriented title
2. A brief description of what needs to be done
3. An estimated duration in minutes

Return your response as a JSON object with this structure:
{{
    "subtasks": [
        {{"title": "...", "description": "...", "estimated_minutes": 30}},
        ...
    ],
    "total_estimate_minutes": 120,
    "reasoning": "Brief explanation of how you broke down the task"
}}

Focus on making subtasks specific, achievable, and in logical order."""

    messages = [
        SystemMessage(content="You are a helpful task planning assistant."),
        HumanMessage(content=prompt),
    ]

    response = await llm.ainvoke(messages)
    content = response.content

    try:
        result = json.loads(content)
        result["todo_id"] = todo_id
        logger.info(f"Generated {len(result.get('subtasks', []))} subtasks")
        return result
    except json.JSONDecodeError:
        logger.warning("Failed to parse breakdown response as JSON")
        # Fallback response
        return {
            "todo_id": todo_id,
            "subtasks": [],
            "total_estimate_minutes": 0,
            "reasoning": "Failed to generate breakdown",
            "error": "Could not parse AI response",
        }


@tool
async def prioritize_tasks(
    todos: list[dict[str, Any]],
) -> dict[str, Any]:
    """Analyze multiple todos and suggest priorities based on urgency and importance.

    Use this tool when a user wants help prioritizing their tasks. The AI will
    use the Eisenhower Matrix (urgent/important) to suggest priorities.

    Args:
        todos: List of todo dictionaries with keys: id, title, description, due_date, current_priority

    Returns:
        Dictionary containing:
        - priority_suggestions: List of todos with suggested priorities
        - reasoning: Explanation for each priority suggestion
        - recommended_order: Suggested order to work on tasks
    """
    logger.info(f"Prioritizing {len(todos)} tasks")

    llm = get_llm(temperature=0.5)

    todos_text = "\n".join(
        [
            f"- [{todo.get('id')}] {todo.get('title')} "
            f"(Current: {todo.get('priority', 'medium')}, "
            f"Due: {todo.get('due_date', 'none')})"
            for todo in todos
        ]
    )

    prompt = f"""You are helping prioritize a list of tasks using the Eisenhower Matrix.

Tasks:
{todos_text}

Analyze each task and assign a priority level:
- urgent: Critical, needs immediate attention
- high: Important, should be done soon
- medium: Regular priority
- low: Can be done later

Return your response as a JSON object:
{{
    "priority_suggestions": [
        {{
            "todo_id": "...",
            "suggested_priority": "urgent|high|medium|low",
            "reasoning": "Why this priority"
        }},
        ...
    ],
    "recommended_order": ["todo_id1", "todo_id2", ...],
    "overall_reasoning": "General prioritization strategy explanation"
}}"""

    messages = [
        SystemMessage(content="You are a helpful task prioritization assistant."),
        HumanMessage(content=prompt),
    ]

    response = await llm.ainvoke(messages)
    content = response.content

    try:
        result = json.loads(content)
        logger.info(f"Generated priority suggestions for {len(todos)} tasks")
        return result
    except json.JSONDecodeError:
        logger.warning("Failed to parse prioritization response as JSON")
        return {
            "priority_suggestions": [],
            "recommended_order": [todo["id"] for todo in todos],
            "overall_reasoning": "Failed to generate suggestions",
            "error": "Could not parse AI response",
        }


@tool
async def schedule_task(
    todo_id: str,
    todo_title: str,
    estimated_duration: int | None = None,
    due_date: str | None = None,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Suggest optimal scheduling for a task based on duration, deadline, and constraints.

    Use this tool when a user wants help scheduling a task. The AI will suggest
    time blocks and scheduling strategies.

    Args:
        todo_id: The ID of the todo to schedule
        todo_title: The title of the todo
        estimated_duration: Estimated duration in minutes
        due_date: When the task is due (ISO format)
        constraints: Optional dict with user's schedule constraints (working_hours, busy_times, etc.)

    Returns:
        Dictionary containing:
        - suggested_schedule: Recommended time blocks
        - scheduling_strategy: Explanation of the approach
        - tips: Tips for completing the task on time
    """
    logger.info(f"Scheduling task: {todo_title}")

    llm = get_llm(temperature=0.5)

    constraints_text = ""
    if constraints:
        constraints_text = f"\nUser constraints: {json.dumps(constraints, indent=2)}"

    prompt = f"""You are helping schedule a task.

Task: {todo_title}
Estimated duration: {estimated_duration or 'unknown'} minutes
Due date: {due_date or 'not set'}
{constraints_text}

Provide scheduling recommendations in JSON format:
{{
    "suggested_schedule": [
        {{
            "timeframe": "Morning / Afternoon / Evening / Specific date-time",
            "duration_minutes": 30,
            "reasoning": "Why this time works"
        }}
    ],
    "scheduling_strategy": "Overall approach (e.g., 'Break into 2 sessions', 'Complete in one block')",
    "tips": ["Tip 1 for completing on time", "Tip 2", ...],
    "buffer_time": "Recommended buffer time in minutes"
}}"""

    messages = [
        SystemMessage(content="You are a helpful scheduling assistant."),
        HumanMessage(content=prompt),
    ]

    response = await llm.ainvoke(messages)
    content = response.content

    try:
        result = json.loads(content)
        result["todo_id"] = todo_id
        logger.info(f"Generated schedule for task: {todo_title}")
        return result
    except json.JSONDecodeError:
        logger.warning("Failed to parse scheduling response as JSON")
        return {
            "todo_id": todo_id,
            "suggested_schedule": [],
            "scheduling_strategy": "Failed to generate schedule",
            "tips": [],
            "error": "Could not parse AI response",
        }


@tool
async def generate_task_guidance(
    todo_id: str,
    todo_title: str,
    todo_description: str | None = None,
) -> dict[str, Any]:
    """Generate detailed step-by-step guidance for completing a task.

    Use this tool when a user wants help understanding how to complete a task.
    The AI will provide actionable steps, tips, and resources.

    Args:
        todo_id: The ID of the todo
        todo_title: The title of the todo
        todo_description: Optional detailed description

    Returns:
        Dictionary containing:
        - steps: List of step-by-step instructions
        - tips: Helpful tips for each step
        - resources: Suggested resources or tools
        - estimated_time: Time estimate for each step
    """
    logger.info(f"Generating guidance for: {todo_title}")

    llm = get_llm(temperature=0.7)

    prompt = f"""You are helping someone complete a task by providing step-by-step guidance.

Task: {todo_title}
{f"Description: {todo_description}" if todo_description else ""}

Provide detailed, actionable guidance in JSON format:
{{
    "steps": [
        {{
            "step_number": 1,
            "title": "Clear action-oriented step title",
            "description": "Detailed explanation of what to do",
            "tips": ["Helpful tip 1", "Helpful tip 2"],
            "estimated_minutes": 15,
            "resources": ["Optional: Tool/website that helps", ...]
        }},
        ...
    ],
    "prerequisites": ["Thing you need before starting", ...],
    "common_pitfalls": ["Common mistake to avoid", ...],
    "success_criteria": "How to know you've completed this successfully"
}}

Make the guidance practical, specific, and encouraging."""

    messages = [
        SystemMessage(content="You are a helpful task completion assistant."),
        HumanMessage(content=prompt),
    ]

    response = await llm.ainvoke(messages)
    content = response.content

    try:
        result = json.loads(content)
        result["todo_id"] = todo_id
        logger.info(f"Generated {len(result.get('steps', []))} guidance steps")
        return result
    except json.JSONDecodeError:
        logger.warning("Failed to parse guidance response as JSON")
        return {
            "todo_id": todo_id,
            "steps": [],
            "prerequisites": [],
            "common_pitfalls": [],
            "success_criteria": "Failed to generate guidance",
            "error": "Could not parse AI response",
        }


@tool
async def create_todo(
    title: str,
    description: str | None = None,
    priority: str = "medium",
    estimated_duration: int | None = None,
) -> dict[str, Any]:
    """Create a new todo in the database.

    Use this tool when the user wants to create a task or todo item.
    This will actually save the todo to the database so the user can see it.

    Args:
        title: The title of the todo (required)
        description: Optional detailed description
        priority: Priority level: low, medium, high, or urgent (default: medium)
        estimated_duration: Estimated time in minutes to complete

    Returns:
        Dictionary with the created todo's ID and details
    """
    # Track tool calls to detect loops
    if not track_tool_call("create_todo"):
        return {
            "success": False,
            "error": "Tool call limit exceeded",
            "message": "This tool has been called too many times. Please review your approach.",
        }

    from ..database import get_db
    from ..models.db_models import Priority
    from ..services.todo_service import TodoService

    logger.info(f"Creating todo: {title}")

    # Map string priority to enum
    priority_map = {
        "low": Priority.LOW,
        "medium": Priority.MEDIUM,
        "high": Priority.HIGH,
        "urgent": Priority.URGENT,
    }
    priority_enum = priority_map.get(priority.lower(), Priority.MEDIUM)

    try:
        async for db in get_db():
            service = TodoService(db)
            todo = await service.create_todo(
                title=title,
                description=description,
                priority=priority_enum,
                estimated_duration=estimated_duration,
                ai_generated=True,
            )

            return {
                "success": True,
                "todo_id": todo.id,
                "title": todo.title,
                "status": todo.status.value,
                "priority": todo.priority.value,
                "message": f"Successfully created todo: {title}",
            }
    except Exception as e:
        logger.error(f"Failed to create todo: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create todo: {str(e)}",
        }


@tool
async def create_subtasks_from_breakdown(
    parent_title: str,
    subtasks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create multiple subtasks from a task breakdown.

    Use this tool after calling breakdown_task to actually create the subtasks
    in the database as individual todos.

    Args:
        parent_title: The title of the parent task
        subtasks: List of subtask dictionaries with 'title', 'description', and 'estimated_minutes'

    Returns:
        Dictionary with created subtask IDs and summary
    """
    from ..database import get_db
    from ..models.db_models import Priority
    from ..services.todo_service import TodoService

    logger.info(f"Creating {len(subtasks)} subtasks for: {parent_title}")

    try:
        created_todos = []
        async for db in get_db():
            service = TodoService(db)

            # Create parent todo first
            parent = await service.create_todo(
                title=parent_title,
                description=f"Parent task with {len(subtasks)} subtasks",
                priority=Priority.MEDIUM,
                ai_generated=True,
            )

            # Create each subtask
            for idx, subtask in enumerate(subtasks):
                todo = await service.create_todo(
                    title=subtask.get("title", f"Subtask {idx + 1}"),
                    description=subtask.get("description"),
                    estimated_duration=subtask.get("estimated_minutes"),
                    priority=Priority.MEDIUM,
                    parent_id=parent.id,
                    ai_generated=True,
                )
                created_todos.append(
                    {
                        "id": todo.id,
                        "title": todo.title,
                        "estimated_minutes": todo.estimated_duration,
                    }
                )

            return {
                "success": True,
                "parent_id": parent.id,
                "parent_title": parent.title,
                "subtasks_created": len(created_todos),
                "subtasks": created_todos,
                "message": f"Successfully created {len(created_todos)} subtasks for '{parent_title}'",
            }
    except Exception as e:
        logger.error(f"Failed to create subtasks: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create subtasks: {str(e)}",
        }
