import json
import logging
import re

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from ..models.state import GraphState
from .agent_tools import breakdown_task, generate_task_guidance, prioritize_tasks, schedule_task

logger = logging.getLogger(__name__)

SUPERVISOR_PROMPT = """You are the Supervisor in an AI-powered to-do management system. Your role is to:
1. Understand user requests about their to-dos
2. Help users manage tasks using available tools
3. Provide intelligent assistance for task breakdown, prioritization, scheduling, and guidance

You have access to these specialized tools:
- breakdown_task: Break down complex tasks into smaller, manageable subtasks with time estimates
- prioritize_tasks: Analyze multiple tasks and suggest priorities based on urgency and importance
- schedule_task: Suggest optimal scheduling for a task based on duration, deadline, and constraints
- generate_task_guidance: Provide step-by-step instructions and tips for completing a task

When a user asks to:
- "Break down X" or "Split X into subtasks" → call breakdown_task
- "Prioritize my tasks" or "What should I do first?" → call prioritize_tasks
- "Schedule X" or "When should I do X?" → call schedule_task
- "How do I do X?" or "Guide me through X" → call generate_task_guidance

You can call multiple tools in sequence as needed. Always confirm actions with the user and explain the results in a clear, helpful manner.

IMPORTANT: When you're done processing and have provided a final response to the user, output JSON in this format:
{
  "plan": [{"id": "uuid", "description": "task description", "status": "DONE"}],
  "active_agent": null,
  "notes": "your final response to the user"
}

This signals completion of the request."""


async def supervisor_node(state: GraphState) -> dict:
    logger.info("Supervisor node started")
    logger.debug(f"Supervisor state: {state['supervisor'].get('status')}")

    # Initialize LLM with tools
    llm = ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        temperature=0,
    )

    # Bind tools to LLM
    tools = [
        breakdown_task,
        prioritize_tasks,
        schedule_task,
        generate_task_guidance,
    ]
    llm_with_tools = llm.bind_tools(tools)

    is_initial_planning = len(state["supervisor"].get("plan", [])) == 0
    history = state["supervisor"].get("history", [])
    tool_results = state["supervisor"].get("tool_results", [])

    # Build message list
    messages = [SystemMessage(content=SUPERVISOR_PROMPT)]

    if is_initial_planning or not history:
        logger.info("Initial planning phase - processing user request")
        user_message = f"""User request: {state['supervisor'].get('notes', 'No task provided')}

Please help the user with their request using the available tools if needed, or respond directly."""
        messages.append(HumanMessage(content=user_message))
    else:
        logger.info(f"Re-planning phase - {len(history)} history entries")
        last_summary = history[-1]
        current_plan = json.dumps(state["supervisor"]["plan"], indent=2)

        user_message = f"""Current plan:
{current_plan}

Last agent update:
- Agent: {last_summary['agent_name']}
- Result: {last_summary['result']}
- Summary: {last_summary['short_summary']}
- Next instructions: {last_summary['next_instructions_for_supervisor']}

Continue processing or finalize."""
        messages.append(HumanMessage(content=user_message))

    # Add tool results to message history if any
    if tool_results:
        for tool_result in tool_results:
            messages.append(AIMessage(content="", tool_calls=[tool_result["call"]]))
            messages.append(
                ToolMessage(
                    content=json.dumps(tool_result["result"]),
                    tool_call_id=tool_result["call"]["id"],
                )
            )

    # Invoke LLM
    response = await llm_with_tools.ainvoke(messages)
    logger.debug(f"Supervisor response: {response}")

    # Check if there are tool calls
    if hasattr(response, "tool_calls") and response.tool_calls:
        logger.info(f"Supervisor requested {len(response.tool_calls)} tool calls")

        # Execute tool calls
        new_tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

            # Find and execute the tool
            tool_map = {
                "breakdown_task": breakdown_task,
                "prioritize_tasks": prioritize_tasks,
                "schedule_task": schedule_task,
                "generate_task_guidance": generate_task_guidance,
            }

            if tool_name in tool_map:
                try:
                    result = await tool_map[tool_name].ainvoke(tool_args)
                    logger.info(f"Tool {tool_name} executed successfully")
                    new_tool_results.append({"call": tool_call, "result": result})
                except Exception as e:
                    logger.error(f"Tool {tool_name} failed: {e}")
                    new_tool_results.append(
                        {
                            "call": tool_call,
                            "result": {"error": str(e)},
                        }
                    )
            else:
                logger.warning(f"Unknown tool: {tool_name}")

        # Update state with tool results and continue processing
        return {
            "supervisor": {
                **state["supervisor"],
                "tool_results": new_tool_results,
                "status": "RUNNING",  # Continue looping to process results
            }
        }

    # No tool calls - parse final JSON response
    content = response.content
    logger.debug(f"Supervisor response length: {len(content)} chars")

    try:
        parsed = json.loads(content)
        logger.debug("Successfully parsed supervisor JSON response")
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse JSON, attempting regex extraction")
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            parsed = json.loads(json_match.group(0))
            logger.info("Successfully extracted JSON via regex")
        else:
            logger.error("Supervisor failed to output valid JSON")
            raise ValueError("Supervisor failed to output valid JSON") from e

    updated_plan = parsed.get("plan", state["supervisor"].get("plan", []))
    active_agent = parsed.get("active_agent")

    logger.info(f"Supervisor routing to: {active_agent or 'FINALIZER'}")
    logger.info(f"Plan has {len(updated_plan)} tasks")

    return {
        "supervisor": {
            **state["supervisor"],
            "plan": updated_plan,
            "active_agent": active_agent if active_agent else None,
            "notes": parsed.get("notes", state["supervisor"].get("notes")),
            "status": "DONE" if active_agent is None else "RUNNING",
            "tool_results": [],  # Clear tool results after processing
        }
    }
