import json
import re
import uuid

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from ..models.state import AgentSummary, GraphState
from .ui_tools import UI_TOOLS

RESEARCH_AGENT_PROMPT = """You are a Research Agent with UI capabilities. Your job is to:
1. Analyze the assigned ToDo task
2. Perform research or gather information
3. Show interactive UI components to the user when you need to present findings or get input
4. Return a structured summary

You have access to UI tools:
- show_approval_card: Show options for user to approve/edit/reject
- show_editable_value: Let user edit a value
- show_document: Display formatted content
- show_options: Show multiple choice options
- show_research_summary: Display formatted research findings

Use these tools when you need to present research findings or get user input.

After completing your task, output JSON in this format:
{
  "agent_name": "research_agent",
  "step_id": "uuid",
  "result": "COMPLETED" | "NEEDS_ASSISTANCE" | "FAILED",
  "short_summary": "brief summary of what you did",
  "key_decisions": ["decision 1", "decision 2"],
  "next_instructions_for_supervisor": "what should happen next"
}"""


async def research_agent_node(state: GraphState) -> dict:
    llm = ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        temperature=0.7,
    ).bind_tools(UI_TOOLS)

    my_tasks = [
        todo
        for todo in state["supervisor"].get("plan", [])
        if todo.get("owner_agent") == "research_agent" and todo.get("status") == "PENDING"
    ]

    if not my_tasks:
        summary: AgentSummary = {
            "agent_name": "research_agent",
            "step_id": str(uuid.uuid4()),
            "result": "COMPLETED",
            "short_summary": "No tasks assigned to research_agent",
            "key_decisions": [],
            "next_instructions_for_supervisor": "Route to another agent or finalize",
        }

        return {
            "supervisor": {
                **state["supervisor"],
                "history": state["supervisor"].get("history", []) + [summary],
                "active_agent": None,
            },
            "agent": {
                **state["agent"],
                "recursion_depth": state["agent"]["recursion_depth"] + 1,
            },
        }

    current_task = my_tasks[0]
    history_summary = "\n".join(
        [
            f"- {h['agent_name']}: {h['short_summary']}"
            for h in state["supervisor"].get("history", [])
        ]
    )

    task_description = f"""Task: {current_task['description']}

Context from supervisor:
{state['supervisor'].get('notes', 'No additional context')}

Previous work done:
{history_summary}

Complete this task and provide a summary."""

    messages = [
        SystemMessage(content=RESEARCH_AGENT_PROMPT),
        HumanMessage(content=task_description),
    ]

    response = await llm.ainvoke(messages)

    # Check if agent is calling a UI tool
    if hasattr(response, "tool_calls") and response.tool_calls:
        tool_call = response.tool_calls[0]
        # Store tool call in state for streaming to pick up
        return {
            "supervisor": {
                **state["supervisor"],
                "pending_tool_call": {
                    "agent": "research_agent",
                    "tool": tool_call["name"],
                    "args": tool_call["args"],
                    "tool_call_id": tool_call.get("id", str(uuid.uuid4())),
                },
            },
            "agent": {
                **state["agent"],
                "tool_events": state["agent"].get("tool_events", [])
                + [
                    {
                        "type": "tool_call",
                        "agent": "research_agent",
                        "tool": tool_call["name"],
                        "args": tool_call["args"],
                    }
                ],
                "recursion_depth": state["agent"]["recursion_depth"] + 1,
            },
        }

    content = response.content

    try:
        summary = json.loads(content)
    except json.JSONDecodeError:
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            summary = json.loads(json_match.group(0))
        else:
            summary = {
                "agent_name": "research_agent",
                "step_id": str(uuid.uuid4()),
                "result": "FAILED",
                "short_summary": "Failed to parse agent output",
                "key_decisions": [],
                "next_instructions_for_supervisor": "Retry or escalate",
            }

    updated_plan = [
        {**todo, "status": "DONE"} if todo["id"] == current_task["id"] else todo
        for todo in state["supervisor"].get("plan", [])
    ]

    return {
        "supervisor": {
            **state["supervisor"],
            "plan": updated_plan,
            "history": state["supervisor"].get("history", []) + [summary],
            "active_agent": None,
        },
        "agent": {
            **state["agent"],
            "recursion_depth": state["agent"]["recursion_depth"] + 1,
        },
    }
