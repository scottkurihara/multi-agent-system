import json
import logging
import re

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from ..models.state import GraphState

logger = logging.getLogger(__name__)

SUPERVISOR_PROMPT = """You are the Supervisor in a multi-agent to-do management system. Your role is to:
1. Understand user requests about their to-dos
2. Break down tasks into actionable ToDo items for internal planning
3. Route execution to the appropriate specialist agent
4. Monitor progress and coordinate workflow

Available specialist agents:
(Note: Specialized agents will be added in Phase 2 - currently routing directly to finalizer)

CRITICAL RULES:
- You MUST NOT call tools directly
- You MUST NOT modify AgentState
- You MUST output valid JSON only
- You MUST set active_agent to null to finalize (no agents available yet)

When planning, output JSON in this format:
{
  "plan": [
    {"id": "uuid", "description": "task description", "status": "DONE"}
  ],
  "active_agent": null,
  "notes": "your response to the user"
}

For now, simply acknowledge user requests and set active_agent to null."""


async def supervisor_node(state: GraphState) -> dict:
    logger.info("Supervisor node started")
    logger.debug(f"Supervisor state: {state['supervisor'].get('status')}")

    llm = ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        temperature=0,
    )

    is_initial_planning = len(state["supervisor"].get("plan", [])) == 0
    history = state["supervisor"].get("history", [])

    if is_initial_planning or not history:
        logger.info("Initial planning phase - creating new plan")
        user_message = f"""User task: {state['supervisor'].get('notes', 'No task provided')}

Please create a plan to accomplish this task. Break it into ToDo items and assign them to appropriate agents."""
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

Update the plan and decide the next agent to route to, or set active_agent to null if done."""

    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = await llm.ainvoke(messages)
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
        }
    }
