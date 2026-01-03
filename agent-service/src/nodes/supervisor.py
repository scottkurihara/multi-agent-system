import json
import re
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from ..models.state import GraphState

SUPERVISOR_PROMPT = """You are the Supervisor in a multi-agent system. Your role is to:
1. Break down user tasks into actionable ToDo items
2. Assign ToDos to specialist agents
3. Route execution to the appropriate agent
4. Monitor progress and coordinate workflow

Available specialist agents:
- research_agent: Gathers information, performs research
- transform_agent: Transforms, processes, or manipulates data

CRITICAL RULES:
- You MUST NOT call tools directly
- You MUST NOT modify AgentState
- You MUST output valid JSON only
- You MUST set active_agent to route to the next agent, or null to finalize

When planning, output JSON in this format:
{
  "plan": [
    {"id": "uuid", "description": "task description", "status": "PENDING", "owner_agent": "research_agent"}
  ],
  "active_agent": "research_agent" | null,
  "notes": "your reasoning"
}

If all work is complete, set active_agent to null to trigger finalization."""


async def supervisor_node(state: GraphState) -> dict:
    llm = ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        temperature=0,
    )

    is_initial_planning = len(state["supervisor"].get("plan", [])) == 0

    if is_initial_planning:
        user_message = f"""User task: {state['supervisor'].get('notes', 'No task provided')}

Please create a plan to accomplish this task. Break it into ToDo items and assign them to appropriate agents."""
    else:
        last_summary = state["supervisor"]["history"][-1]
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

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            parsed = json.loads(json_match.group(0))
        else:
            raise ValueError("Supervisor failed to output valid JSON")

    updated_plan = parsed.get("plan", state["supervisor"].get("plan", []))
    active_agent = parsed.get("active_agent")

    return {
        "supervisor": {
            **state["supervisor"],
            "plan": updated_plan,
            "active_agent": active_agent if active_agent else None,
            "notes": parsed.get("notes", state["supervisor"].get("notes")),
            "status": "DONE" if active_agent is None else "RUNNING",
        }
    }
