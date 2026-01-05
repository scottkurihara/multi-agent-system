"""Tool functions that can be called by the supervisor agent.

These tools enable AI-assisted operations on todos, including breakdown,
prioritization, scheduling, and step-by-step guidance.
"""

import json
import logging
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


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


# Note: CRUD tools (create_todo, update_todo, list_todos) will be added
# when we integrate with the TodoService in the supervisor node.
# The supervisor will handle database operations directly or via a service layer.
