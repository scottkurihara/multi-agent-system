"""Supervisor Agent - Orchestrates sub-agents and manages task execution.

This agent uses create_react_agent from LangGraph and calls sub-agents as tools.
The supervisor is responsible for:
1. Understanding user requests
2. Delegating work to specialist sub-agents (research, transform)
3. Managing todo operations
4. Coordinating the overall workflow
"""

import logging

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from ..models.state import GraphState
from .agent_tools import breakdown_task, generate_task_guidance, prioritize_tasks, schedule_task
from .sub_agent_tools import call_research_agent, call_transform_agent

logger = logging.getLogger(__name__)

SUPERVISOR_SYSTEM_MESSAGE = """You are the Supervisor Agent in a multi-agent system.

Your responsibilities:
1. Understand user requests and break them down into steps
2. Delegate work to specialist sub-agents when needed
3. Manage todo operations (breakdown, prioritize, schedule, guide)
4. Coordinate the overall workflow

## Available Sub-Agents (call as tools):

**call_research_agent**: Delegate research tasks
- Use for: information gathering, data analysis, topic research
- Example: "Research the latest developments in AI"

**call_transform_agent**: Delegate transformation tasks
- Use for: data formatting, summarization, restructuring, entity extraction
- Example: "Summarize this research and format as markdown"

## Available Todo Management Tools:

**breakdown_task**: Break down complex tasks into subtasks with time estimates
**prioritize_tasks**: Analyze and suggest task priorities
**schedule_task**: Suggest optimal task scheduling
**generate_task_guidance**: Provide step-by-step task completion guidance

## Workflow:

1. Analyze the user's request
2. Determine if sub-agents are needed:
   - Research needed? → call_research_agent
   - Transformation needed? → call_transform_agent
3. Use todo management tools for task organization
4. Provide clear, helpful responses

You can call multiple tools in sequence. Delegate complex work to sub-agents rather than trying to do everything yourself."""


# Create the supervisor agent using create_react_agent
def create_supervisor_agent():
    """Create the supervisor agent using LangGraph's create_react_agent.

    The supervisor has access to:
    - Sub-agent tools (call_research_agent, call_transform_agent)
    - Todo management tools (breakdown_task, prioritize_tasks, etc.)

    Returns:
        A configured supervisor agent
    """
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0,
    )

    # Combine all available tools
    tools = [
        # Sub-agent tools
        call_research_agent,
        call_transform_agent,
        # Todo management tools
        breakdown_task,
        prioritize_tasks,
        schedule_task,
        generate_task_guidance,
    ]

    # create_react_agent doesn't take state_modifier, we'll add system message in messages
    agent = create_react_agent(
        llm,
        tools=tools,
    )

    logger.info("Supervisor agent created successfully with access to sub-agents and todo tools")
    return agent


# Create the supervisor agent instance
supervisor_agent = create_supervisor_agent()


async def supervisor_node(state: GraphState) -> dict:
    """Node function that wraps the supervisor agent for use in LangGraph.

    Args:
        state: Graph state containing supervisor and agent states

    Returns:
        Updated state with supervisor's decisions and routing
    """
    logger.info("Supervisor node started")
    logger.debug(f"Supervisor status: {state['supervisor'].get('status')}")

    # Get the user's task/request
    user_task = state["supervisor"].get("notes", "")
    history = state["supervisor"].get("history", [])

    # Build the message for the supervisor
    if not history:
        # Initial planning
        logger.info("Initial planning phase")
        message = f"User request: {user_task}"
    else:
        # Re-planning after sub-agent execution
        logger.info(f"Re-planning phase with {len(history)} history entries")
        last_summary = history[-1]
        message = f"""User request: {user_task}

Latest update from {last_summary['agent_name']}:
- Result: {last_summary['result']}
- Summary: {last_summary['short_summary']}
- Instructions: {last_summary['next_instructions_for_supervisor']}

Please continue processing or finalize if complete."""

    try:
        # Invoke the supervisor agent with system message
        result = await supervisor_agent.ainvoke(
            {"messages": [("system", SUPERVISOR_SYSTEM_MESSAGE), ("human", message)]}
        )

        # Extract the final response
        messages = result.get("messages", [])
        final_message = messages[-1] if messages else None

        logger.info("Supervisor agent completed successfully")
        logger.debug(f"Supervisor generated {len(messages)} messages")

        # For now, mark as DONE after supervisor processes
        # In a full implementation, you'd parse the response to determine next steps
        return {
            "supervisor": {
                **state["supervisor"],
                "status": "DONE",
                "active_agent": None,
                "notes": final_message.content if final_message else "Processing complete",
            }
        }

    except Exception as e:
        logger.error(f"Supervisor agent failed: {e}")
        return {
            "supervisor": {
                **state["supervisor"],
                "status": "ESCALATE",
                "notes": f"Supervisor encountered an error: {str(e)}",
            }
        }
