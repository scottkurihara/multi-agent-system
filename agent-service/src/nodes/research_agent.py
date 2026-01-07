"""Research Agent - Specialist for gathering and analyzing information.

This agent uses create_agent from LangGraph and is called as a tool by the Supervisor.
"""

import logging
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)


# Research-specific tools
@tool
async def web_search(query: str) -> dict[str, Any]:
    """Search the web for information about a topic.

    Args:
        query: The search query

    Returns:
        Dictionary with search results
    """
    logger.info(f"Web search for: {query}")
    # Placeholder implementation - in production would use actual search API
    return {
        "query": query,
        "results": [
            {
                "title": f"Article about {query}",
                "snippet": f"Information related to {query}...",
                "url": "https://example.com",
            }
        ],
        "summary": f"Found relevant information about {query}",
    }


@tool
async def analyze_data(data: str, analysis_type: str = "summary") -> dict[str, Any]:
    """Analyze provided data and extract insights.

    Args:
        data: The data to analyze
        analysis_type: Type of analysis (summary, trends, statistics)

    Returns:
        Dictionary with analysis results
    """
    logger.info(f"Analyzing data: {analysis_type}")
    # Placeholder implementation
    return {
        "analysis_type": analysis_type,
        "insights": [
            "Key finding 1",
            "Key finding 2",
            "Key finding 3",
        ],
        "summary": f"Analysis of type '{analysis_type}' completed",
    }


@tool
async def gather_context(topic: str, depth: str = "moderate") -> dict[str, Any]:
    """Gather contextual information about a topic.

    Args:
        topic: The topic to research
        depth: Depth of research (shallow, moderate, deep)

    Returns:
        Dictionary with contextual information
    """
    logger.info(f"Gathering context about: {topic} (depth: {depth})")
    return {
        "topic": topic,
        "depth": depth,
        "context": {
            "background": f"Background information about {topic}",
            "key_concepts": ["Concept 1", "Concept 2", "Concept 3"],
            "related_topics": ["Related topic 1", "Related topic 2"],
        },
        "summary": f"Gathered {depth} context about {topic}",
    }


# Create the research agent
def create_research_agent():
    """Create a research agent using LangGraph's create_react_agent.

    Returns:
        A configured research agent
    """
    llm = ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        temperature=0,
    )

    tools = [web_search, analyze_data, gather_context]

    # create_react_agent doesn't take state_modifier, we'll add system message in messages
    agent = create_react_agent(
        llm,
        tools=tools,
    )

    logger.info("Research agent created successfully")
    return agent


# Create the agent instance
research_agent = create_research_agent()


RESEARCH_SYSTEM_MESSAGE = """You are a Research Agent specialized in gathering and analyzing information.

Your capabilities:
- web_search: Search for information on the web
- analyze_data: Analyze data and extract insights
- gather_context: Gather contextual information about topics

When given a research task:
1. Determine what information is needed
2. Use appropriate tools to gather information
3. Analyze and synthesize findings
4. Provide clear, well-organized results

Be thorough but concise. Focus on actionable insights."""


async def research_agent_node(state: dict) -> dict:
    """Node function that wraps the research agent for use in LangGraph.

    Args:
        state: Graph state containing the task/messages

    Returns:
        Updated state with research results
    """
    logger.info("Research agent node started")

    # Extract the task from supervisor notes or active task
    task = state.get("supervisor", {}).get("notes", "")

    # Invoke the research agent with system message
    result = await research_agent.ainvoke(
        {"messages": [("system", RESEARCH_SYSTEM_MESSAGE), ("human", task)]}
    )

    # Extract the final response
    messages = result.get("messages", [])
    final_message = messages[-1] if messages else None

    summary = {
        "agent_name": "research_agent",
        "step_id": "research_1",
        "result": "COMPLETED",
        "short_summary": final_message.content if final_message else "Research completed",
        "key_decisions": ["Gathered information", "Analyzed data"],
        "next_instructions_for_supervisor": "Research complete. Proceed with next step or finalize.",
    }

    logger.info("Research agent completed successfully")

    return {
        "supervisor": {
            **state.get("supervisor", {}),
            "history": [*state.get("supervisor", {}).get("history", []), summary],
            "active_agent": None,
        }
    }
