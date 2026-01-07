"""Transform Agent - Specialist for data transformation and formatting.

This agent uses create_agent from LangGraph and is called as a tool by the Supervisor.
"""

import logging
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)


# Transform-specific tools
@tool
async def format_data(data: str, format_type: str = "markdown") -> dict[str, Any]:
    """Format data into a specified format.

    Args:
        data: The data to format
        format_type: Target format (markdown, json, html, plain)

    Returns:
        Dictionary with formatted data
    """
    logger.info(f"Formatting data to: {format_type}")
    # Placeholder implementation
    formatted = f"# Formatted as {format_type}\n\n{data}"
    return {
        "format_type": format_type,
        "formatted_data": formatted,
        "summary": f"Data formatted as {format_type}",
    }


@tool
async def summarize_content(content: str, length: str = "medium") -> dict[str, Any]:
    """Summarize content to a specified length.

    Args:
        content: The content to summarize
        length: Target length (brief, medium, detailed)

    Returns:
        Dictionary with summary
    """
    logger.info(f"Summarizing content: {length}")
    # In production, this would use LLM for actual summarization
    return {
        "original_length": len(content),
        "summary_length": length,
        "summary": f"Summary of the content ({length} version): {content[:100]}...",
        "key_points": [
            "Key point 1",
            "Key point 2",
            "Key point 3",
        ],
    }


@tool
async def restructure_information(
    information: str, structure: str = "hierarchical"
) -> dict[str, Any]:
    """Restructure information into a different organizational structure.

    Args:
        information: The information to restructure
        structure: Target structure (hierarchical, chronological, topical)

    Returns:
        Dictionary with restructured information
    """
    logger.info(f"Restructuring information: {structure}")
    return {
        "structure_type": structure,
        "restructured_data": {
            "section_1": "Restructured content part 1",
            "section_2": "Restructured content part 2",
            "section_3": "Restructured content part 3",
        },
        "summary": f"Information restructured in {structure} format",
    }


@tool
async def extract_entities(text: str, entity_types: list[str] = None) -> dict[str, Any]:
    """Extract specific entities from text.

    Args:
        text: The text to analyze
        entity_types: Types of entities to extract (names, dates, locations, etc.)

    Returns:
        Dictionary with extracted entities
    """
    logger.info("Extracting entities from text")
    entity_types = entity_types or ["names", "dates", "locations"]
    return {
        "entity_types": entity_types,
        "entities": {
            "names": ["Entity 1", "Entity 2"],
            "dates": ["2024-01-01", "2024-12-31"],
            "locations": ["Location 1", "Location 2"],
        },
        "summary": f"Extracted {len(entity_types)} types of entities",
    }


# Create the transform agent
def create_transform_agent():
    """Create a transform agent using LangGraph's create_react_agent.

    Returns:
        A configured transform agent
    """
    llm = ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        temperature=0,
    )

    tools = [format_data, summarize_content, restructure_information, extract_entities]

    # create_react_agent doesn't take state_modifier, we'll add system message in messages
    agent = create_react_agent(
        llm,
        tools=tools,
    )

    logger.info("Transform agent created successfully")
    return agent


# Create the agent instance
transform_agent = create_transform_agent()


TRANSFORM_SYSTEM_MESSAGE = """You are a Transform Agent specialized in data transformation and formatting.

Your capabilities:
- format_data: Convert data into different formats (markdown, JSON, HTML, etc.)
- summarize_content: Create summaries of varying lengths
- restructure_information: Reorganize information into different structures
- extract_entities: Extract specific entities from text

When given a transformation task:
1. Understand the input data and desired output
2. Choose appropriate transformation tools
3. Process the data systematically
4. Ensure output quality and format correctness

Be precise and maintain data integrity during transformations."""


async def transform_agent_node(state: dict) -> dict:
    """Node function that wraps the transform agent for use in LangGraph.

    Args:
        state: Graph state containing the task/messages

    Returns:
        Updated state with transformation results
    """
    logger.info("Transform agent node started")

    # Extract the task from supervisor notes or active task
    task = state.get("supervisor", {}).get("notes", "")

    # Invoke the transform agent with system message
    result = await transform_agent.ainvoke(
        {"messages": [("system", TRANSFORM_SYSTEM_MESSAGE), ("human", task)]}
    )

    # Extract the final response
    messages = result.get("messages", [])
    final_message = messages[-1] if messages else None

    summary = {
        "agent_name": "transform_agent",
        "step_id": "transform_1",
        "result": "COMPLETED",
        "short_summary": final_message.content if final_message else "Transformation completed",
        "key_decisions": ["Transformed data", "Applied formatting"],
        "next_instructions_for_supervisor": "Transformation complete. Proceed with next step or finalize.",
    }

    logger.info("Transform agent completed successfully")

    return {
        "supervisor": {
            **state.get("supervisor", {}),
            "history": [*state.get("supervisor", {}).get("history", []), summary],
            "active_agent": None,
        }
    }
