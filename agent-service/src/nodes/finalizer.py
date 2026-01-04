from ..models.state import GraphState


async def finalizer_node(state: GraphState) -> dict:
    all_work_completed = all(
        todo.get("status") in ["DONE", "BLOCKED"] for todo in state["supervisor"].get("plan", [])
    )

    if all_work_completed:
        work_summary = "\n".join(
            [
                f"{h['agent_name']}: {h['short_summary']}"
                for h in state["supervisor"].get("history", [])
            ]
        )
        final_output = f"Task completed successfully.\n\nWork done:\n{work_summary}"
    else:
        final_output = f"Task processing completed with status: {state['supervisor']['status']}"

    return {
        "supervisor": {
            **state["supervisor"],
            "status": "DONE",
            "active_agent": None,
            "notes": final_output,
        }
    }
