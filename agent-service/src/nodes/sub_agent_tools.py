"""Sub-Agent Tools - Wrapper tools that allow Supervisor to call sub-agents.

These tools wrap the research and transform agents so they can be called
as tools by the supervisor agent.
"""

import logging
from typing import Any

from langchain_core.tools import tool

from .research_agent import research_agent
from .transform_agent import transform_agent

logger = logging.getLogger(__name__)


@tool
async def call_research_agent(task: str) -> dict[str, Any]:
    """Delegate a research task to the Research Agent.

    Use this tool when you need to:
    - Gather information from external sources
    - Analyze data and extract insights
    - Research a topic in depth
    - Collect contextual information

    The Research Agent has specialized tools for web search, data analysis,
    and context gathering.

    Args:
        task: A clear description of the research task

    Returns:
        Dictionary containing research results with findings and analysis
    """
    logger.info(f"Supervisor calling Research Agent with task: {task}")

    try:
        # Invoke the research agent
        result = await research_agent.ainvoke({"messages": [("human", task)]})

        # Extract messages from result
        messages = result.get("messages", [])
        final_message = messages[-1] if messages else None

        response = {
            "status": "success",
            "agent": "research_agent",
            "task": task,
            "result": final_message.content if final_message else "Research completed",
            "message_history": [
                {"role": msg.type, "content": msg.content}
                for msg in messages[-3:]  # Last 3 messages for context
            ],
        }

        logger.info("Research Agent completed successfully")
        return response

    except Exception as e:
        logger.error(f"Research Agent failed: {e}")
        return {
            "status": "error",
            "agent": "research_agent",
            "task": task,
            "error": str(e),
            "result": f"Research task failed: {str(e)}",
        }


@tool
async def call_transform_agent(task: str, input_data: str = None) -> dict[str, Any]:
    """Delegate a transformation task to the Transform Agent.

    Use this tool when you need to:
    - Format data into different formats (JSON, markdown, HTML)
    - Summarize content
    - Restructure information
    - Extract entities from text

    The Transform Agent has specialized tools for data transformation,
    formatting, and content manipulation.

    Args:
        task: A clear description of the transformation task
        input_data: Optional data to transform (if not included in task description)

    Returns:
        Dictionary containing transformation results
    """
    logger.info(f"Supervisor calling Transform Agent with task: {task}")

    try:
        # Build the full task description
        full_task = task
        if input_data:
            full_task = f"{task}\n\nInput data:\n{input_data}"

        # Invoke the transform agent
        result = await transform_agent.ainvoke({"messages": [("human", full_task)]})

        # Extract messages from result
        messages = result.get("messages", [])
        final_message = messages[-1] if messages else None

        response = {
            "status": "success",
            "agent": "transform_agent",
            "task": task,
            "result": final_message.content if final_message else "Transformation completed",
            "message_history": [
                {"role": msg.type, "content": msg.content}
                for msg in messages[-3:]  # Last 3 messages for context
            ],
        }

        logger.info("Transform Agent completed successfully")
        return response

    except Exception as e:
        logger.error(f"Transform Agent failed: {e}")
        return {
            "status": "error",
            "agent": "transform_agent",
            "task": task,
            "error": str(e),
            "result": f"Transformation task failed: {str(e)}",
        }
