import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from ..graph.workflow import create_graph
from ..models.api_models import AgentRequest, AgentResponse, Metadata, OutputData, ResultData
from ..models.state import GraphState
from .streaming import stream_agent_events

# Load environment variables
load_dotenv()

app = FastAPI(title="Agent Service", version="1.0.0")

# Create the graph
graph = create_graph()


@app.post("/v1/agent/run")
async def run_agent(request: AgentRequest) -> AgentResponse:
    """Run the multi-agent system."""
    try:
        if not request.input.task:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_REQUEST",
                        "message": "Missing required field: input.task",
                    }
                },
            )

        if request.options and request.options.stream:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "STREAM_NOT_SUPPORTED",
                        "message": "Streaming is not supported in Phase 1",
                    }
                },
            )

        run_id = (
            request.options.run_id
            if request.options and request.options.run_id
            else str(uuid.uuid4())
        )
        system_variant = request.options.system_variant if request.options else "blue"

        # Initialize state
        initial_state: GraphState = {
            "supervisor": {
                "task_id": run_id,
                "context_id": request.input.context.get("context_id")
                if request.input.context
                else None,
                "status": "RUNNING",
                "plan": [],
                "history": [],
                "notes": request.input.task,
            },
            "agent": {
                "messages": [],
                "tool_events": [],
                "recursion_depth": 0,
                "scratchpad": {},
            },
        }

        # Run the graph
        config = {"configurable": {"thread_id": run_id}}
        result = await graph.ainvoke(initial_state, config)

        # Build response
        response = AgentResponse(
            result=ResultData(
                status=result["supervisor"]["status"],
                output=OutputData(
                    type="text",
                    content=result["supervisor"].get("notes", "Task completed"),
                ),
                supervisor_state=result["supervisor"],
            ),
            metadata=Metadata(
                run_id=run_id,
                system_variant=system_variant,
            ),
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e),
                    "details": {
                        "stack": str(e) if os.getenv("NODE_ENV") == "development" else None
                    },
                }
            },
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/v1/agent/stream")
async def stream_agent(request: AgentRequest):
    """Stream agent execution events in real-time."""
    try:
        if not request.input.task:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_REQUEST",
                        "message": "Missing required field: input.task",
                    }
                },
            )

        return StreamingResponse(
            stream_agent_events(request.input.task),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e),
                }
            },
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
