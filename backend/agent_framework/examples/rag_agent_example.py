"""
Example script demonstrating the use of the RAG agent.

This script shows how to create and use a RAG agent to process queries.
"""
import sys
import os
import asyncio
import json
import logging
from pathlib import Path

# Add the backend directory to the path so we can import the agent framework
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Import the agent framework
from agent_framework.factory import create_rag_agent
from agent_framework.agent import Query, AgentResponse
from agent_framework.query_parser import QueryParser
from agent_framework.tool_registry import ToolRegistry
from agent_framework.integrations.rag_integration import get_rag_integration
from agent_framework.integrations.llm_integration import get_llm_integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Run the RAG agent example."""
    # Create the RAG agent
    agent = await create_rag_agent(
        agent_id="example_rag_agent",
        name="Example RAG Agent",
        model="gpt-4",
        max_sources=3
    )
    
    # Print agent information
    logger.info(f"Created agent: {agent.agent_id} ({agent.name})")
    
    # Example queries
    example_queries = [
        "What are the key requirements of GDPR compliance?",
        "Explain the concept of strong customer authentication in PSD2.",
        "What penalties can be imposed for violating financial regulations?",
        "What is RegulAIte?",
    ]
    
    # Process each query
    for query_text in example_queries:
        logger.info(f"\n\n--- Processing query: {query_text} ---")
        
        # Create a query object
        query = Query(query_text=query_text)
        
        # Process the query
        response = await agent.process_query(query)
        
        # Print the response
        logger.info(f"Response: {response.content}")
        logger.info(f"Tools used: {response.tools_used}")
        logger.info(f"Context used: {response.context_used}")
        
        # If there are sources, print them
        if "sources" in response.metadata and response.metadata["sources"]:
            logger.info("Sources:")
            for i, source in enumerate(response.metadata["sources"]):
                logger.info(f"  Source {i+1}: {source.get('title', f'Source {i+1}')}")
        
        # Wait a bit between queries
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 