import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from ..graph.workflow import create_graph
from ..models.state import GraphState

logger = logging.getLogger(__name__)


async def stream_agent_events(task: str) -> AsyncGenerator[str, None]:
    """Stream events as the agent system processes the task."""
    logger.info(f"Starting stream for task: {task[:50]}...")

    # Initial event
    yield f"data: {json.dumps({'type': 'started', 'message': 'Starting multi-agent system...'})}\n\n"
    await asyncio.sleep(0.1)

    # Planning phase
    yield f"data: {json.dumps({'type': 'thinking', 'message': 'Supervisor is analyzing the task and creating a plan...'})}\n\n"
    await asyncio.sleep(0.1)

    # Create initial state
    import uuid

    run_id = str(uuid.uuid4())
    logger.info(f"Created run ID: {run_id}")

    initial_state: GraphState = {
        "supervisor": {
            "task_id": run_id,
            "context_id": None,
            "status": "RUNNING",
            "plan": [],
            "history": [],
            "notes": task,
        },
        "agent": {
            "messages": [],
            "tool_events": [],
            "recursion_depth": 0,
            "scratchpad": {},
        },
    }

    graph = create_graph()
    config = {"configurable": {"thread_id": run_id}}

    # Stream the graph execution
    step_count = 0
    final_state = None
    logger.info("Starting graph stream execution")
    async for event in graph.astream(initial_state, config):
        step_count += 1
        logger.debug(f"Processing step {step_count}")

        # Parse the event
        if isinstance(event, dict):
            for node_name, node_output in event.items():
                # Capture the final state from each event
                if "supervisor" in node_output:
                    final_state = node_output

                if node_name == "supervisor":
                    supervisor_state = node_output.get("supervisor", {})
                    plan = supervisor_state.get("plan", [])

                    if plan:
                        plan_data = {
                            "type": "plan_created",
                            "message": f"Plan created with {len(plan)} tasks",
                            "plan": plan,
                        }
                        yield f"data: {json.dumps(plan_data)}\n\n"

                    active_agent = supervisor_state.get("active_agent")
                    if active_agent:
                        routing_data = {
                            "type": "routing",
                            "message": f"Routing to {active_agent}...",
                            "agent": active_agent,
                        }
                        yield f"data: {json.dumps(routing_data)}\n\n"

                elif node_name == "research_agent":
                    yield f"data: {json.dumps({'type': 'agent_working', 'message': 'Research agent is gathering information...', 'agent': 'research_agent'})}\n\n"

                    supervisor_state = node_output.get("supervisor", {})

                    # Check for tool calls
                    pending_tool_call = supervisor_state.get("pending_tool_call")
                    if pending_tool_call:
                        logger.info(f"Streaming tool call: {pending_tool_call['tool']}")
                        tool_call_data = {
                            "type": "tool_call",
                            "message": f'Research agent is showing UI component: {pending_tool_call["tool"]}',
                            "agent": pending_tool_call.get("agent", "research_agent"),
                            "tool": pending_tool_call["tool"],
                            "args": pending_tool_call["args"],
                            "tool_call_id": pending_tool_call.get("tool_call_id"),
                        }
                        yield f"data: {json.dumps(tool_call_data)}\n\n"

                    history = supervisor_state.get("history", [])
                    if history:
                        last_summary = history[-1]
                        summary_text = last_summary.get("short_summary", "")
                        event_data = {
                            "type": "agent_completed",
                            "message": f"Research agent completed: {summary_text}",
                            "agent": "research_agent",
                            "summary": last_summary,
                        }
                        yield f"data: {json.dumps(event_data)}\n\n"

                elif node_name == "transform_agent":
                    yield f"data: {json.dumps({'type': 'agent_working', 'message': 'Transform agent is processing data...', 'agent': 'transform_agent'})}\n\n"

                    supervisor_state = node_output.get("supervisor", {})

                    # Check for tool calls
                    pending_tool_call = supervisor_state.get("pending_tool_call")
                    if pending_tool_call:
                        tool_call_data = {
                            "type": "tool_call",
                            "message": f'Transform agent is showing UI component: {pending_tool_call["tool"]}',
                            "agent": pending_tool_call.get("agent", "transform_agent"),
                            "tool": pending_tool_call["tool"],
                            "args": pending_tool_call["args"],
                            "tool_call_id": pending_tool_call.get("tool_call_id"),
                        }
                        yield f"data: {json.dumps(tool_call_data)}\n\n"

                    history = supervisor_state.get("history", [])
                    if history:
                        last_summary = history[-1]
                        summary_text = last_summary.get("short_summary", "")
                        event_data = {
                            "type": "agent_completed",
                            "message": f"Transform agent completed: {summary_text}",
                            "agent": "transform_agent",
                            "summary": last_summary,
                        }
                        yield f"data: {json.dumps(event_data)}\n\n"

                elif node_name == "finalizer":
                    yield f"data: {json.dumps({'type': 'finalizing', 'message': 'Finalizing response...'})}\n\n"

        await asyncio.sleep(0.1)

    # Send final event using the captured state
    logger.info(f"Stream completed after {step_count} steps")
    if final_state and "supervisor" in final_state:
        supervisor_final = final_state["supervisor"]
        logger.info(f"Final status: {supervisor_final['status']}")
        yield f"data: {json.dumps({'type': 'done', 'message': 'Task completed!', 'result': {'status': supervisor_final['status'], 'output': supervisor_final.get('notes', ''), 'supervisor_state': supervisor_final}})}\n\n"
    else:
        # Fallback if no state was captured
        logger.warning("No final state captured, using fallback")
        yield f"data: {json.dumps({'type': 'done', 'message': 'Task completed!', 'result': {'status': 'DONE', 'output': '', 'supervisor_state': {}}})}\n\n"
