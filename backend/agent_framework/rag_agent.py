"""
RAG Agent implementation for the RegulAIte Agent Framework.

This module provides a Retrieval-Augmented Generation (RAG) agent that combines
the agent foundation with retrieval capabilities.
"""
from typing import Dict, List, Optional, Any, Union, Callable
import logging
import json
import asyncio
import time

from .agent import Agent, AgentResponse, Query
from .query_parser import ParsedQuery, QueryParser
from .tool_registry import ToolRegistry
from .response_generator import ResponseGenerator

# Set up logging
logger = logging.getLogger(__name__)

class RAGAgent(Agent):
    """
    Retrieval-Augmented Generation agent that combines query processing
    with document retrieval capabilities.
    """
    
    def __init__(self, 
                agent_id: str = "rag_agent", 
                name: str = "RAG Agent",
                tool_registry: Optional[ToolRegistry] = None,
                query_parser: Optional[QueryParser] = None,
                retrieval_system=None,
                llm_client=None,
                max_sources: int = 5):
        """
        Initialize the RAG agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
            tool_registry: Registry of tools available to this agent
            query_parser: Parser for processing queries
            retrieval_system: System for retrieving documents
            llm_client: Client for LLM-based generation
            max_sources: Maximum number of sources to retrieve
        """
        super().__init__(agent_id, name)
        
        self.tool_registry = tool_registry or ToolRegistry()
        self.query_parser = query_parser or QueryParser()
        self.retrieval_system = retrieval_system
        self.llm_client = llm_client
        self.max_sources = max_sources
        
        # Register standard RAG tools
        self._register_standard_tools()
        
        # Step tracking for streaming
        self.step_callback = None
        self.current_execution_id = None
        
    def set_step_callback(self, callback: Callable, execution_id: str = None):
        """
        Set a callback function to receive step updates during processing.
        
        Args:
            callback: Function to call with step updates
            execution_id: Optional execution ID for tracking
        """
        self.step_callback = callback
        self.current_execution_id = execution_id
        
    async def _emit_step(self, step_name: str, message: str, details: str = None, progress: float = None):
        """
        Emit a processing step update.
        
        Args:
            step_name: Name/ID of the processing step
            message: Human-readable message describing the step
            details: Optional additional details
            progress: Optional progress percentage (0-100)
        """
        if self.step_callback:
            step_data = {
                "step": step_name,
                "message": message,
                "details": details,
                "progress": progress,
                "timestamp": time.time(),
                "execution_id": self.current_execution_id
            }
            
            try:
                if asyncio.iscoroutinefunction(self.step_callback):
                    await self.step_callback(step_data)
                else:
                    self.step_callback(step_data)
            except Exception as e:
                self.logger.error(f"Error in step callback: {e}")
        
    def _register_standard_tools(self):
        """Register standard tools for the RAG agent."""
        # This would register tools like document retrieval, query reformulation, etc.
        # For now, just a placeholder
        pass
        
    async def process_query(self, query: Union[str, Query, ParsedQuery]) -> AgentResponse:
        """
        Process a user query and generate a response with RAG capabilities.
        
        Args:
            query: The query to process
            
        Returns:
            An AgentResponse with the agent's response
        """
        # Parse the query if it's not already parsed
        if isinstance(query, str):
            query = Query(query_text=query)
        
        if not isinstance(query, ParsedQuery):
            await self._emit_step("query_parsing", "Parsing and analyzing your query...")
            parsed_query = await self.query_parser.parse(query)
        else:
            parsed_query = query
            
        self.logger.info(f"Processing query with RAG agent: {parsed_query.query_text}")
        self.logger.info(f"Query category: {getattr(parsed_query, 'category', 'unknown')}")
        
        # Initialize response objects
        context = []
        tool_results = []
        sources = []
        enhanced_query = parsed_query.query_text
        
        # Step 1: Select and execute relevant tools FIRST (before RAG)
        await self._emit_step("tool_selection", "Selecting appropriate tools for your query...", progress=10)
        
        # Tools can help enhance the query, extract entities, or provide additional context
        tool_ids = await self.tool_registry.select_tools(parsed_query.query_text)
        self.logger.info(f"Selected tools: {tool_ids}")
        
        if tool_ids:
            await self._emit_step("tool_execution", f"Executing {len(tool_ids)} specialized tools...", 
                                f"Tools: {', '.join(tool_ids)}", progress=25)
        
        for i, tool_id in enumerate(tool_ids):
            tool = self.tool_registry.get_tool(tool_id)
            if tool:
                try:
                    # Execute the tool with just the query parameter
                    # Most tools expect a 'query' parameter
                    self.logger.info(f"Executing tool: {tool_id}")
                    await self._emit_step("tool_execution", f"Running {tool_id}...", 
                                        f"Tool {i+1} of {len(tool_ids)}")
                    
                    # All tools in our system are async, so await them properly
                    result = await tool(query=parsed_query.query_text)
                    
                    # Store successful tool results (ensure JSON serializable)
                    serializable_result = result
                    try:
                        json.dumps(result)  # Test if result is JSON serializable
                    except (TypeError, ValueError):
                        # Convert non-serializable result to string
                        serializable_result = str(result)
                    
                    tool_results.append({
                        "tool_id": tool_id,
                        "result": serializable_result,
                        "success": True
                    })
                    
                    self.logger.info(f"Tool {tool_id} execution successful")
                    
                    # If the tool returned context or sources, add them
                    if isinstance(result, dict):
                        if "context" in result:
                            context.extend(result["context"])
                        if "sources" in result:
                            tool_sources = result["sources"]
                            self.logger.info(f"Tool {tool_id} returned {len(tool_sources)} sources")
                            sources.extend(tool_sources)
                        if "enhanced_query" in result:
                            enhanced_query = result["enhanced_query"]
                            
                except Exception as e:
                    self.logger.error(f"Error executing tool {tool_id}: {str(e)}")
                    tool_results.append({
                        "tool_id": tool_id,
                        "error": str(e),
                        "success": False
                    })
                    await self._emit_step("tool_error", f"Tool {tool_id} encountered an error", str(e))
        
        # Step 2: RAG Processing - Retrieve relevant context
        await self._emit_step("context_retrieval", "Searching knowledge base for relevant information...", 
                            progress=50)
        
        try:
            # Use the enhanced query for better retrieval
            retrieval_query = enhanced_query if enhanced_query != parsed_query.query_text else parsed_query.query_text
            
            # Actually call the RAG retrieval system
            if self.retrieval_system:
                self.logger.info(f"Calling RAG retrieval system with query: {retrieval_query}")
                retrieval_result = await self.retrieval_system.retrieve(
                    query=retrieval_query,
                    top_k=self.max_sources
                )
                
                # Extract context and sources from retrieval result
                rag_context = retrieval_result.get("results", [])
                rag_sources = retrieval_result.get("sources", [])
                
                self.logger.info(f"RAG retrieval returned {len(rag_context)} context items and {len(rag_sources)} sources")
            else:
                self.logger.warning("No retrieval system available, using empty context")
                rag_context = []
                rag_sources = []
            
            # Add any context from tools
            if context:
                rag_context.extend(context)
            if sources:
                self.logger.info(f"Merging {len(sources)} tool sources with {len(rag_sources)} RAG sources")
                # Deduplicate sources before extending
                existing_source_ids = set()
                for existing_source in rag_sources:
                    # Create a unique identifier for each source
                    source_id = f"{existing_source.get('doc_id', '')}_{existing_source.get('chunk_index', '')}_{existing_source.get('content', '')[:50]}"
                    existing_source_ids.add(source_id)
                
                # Only add sources that aren't already present
                for source in sources:
                    source_id = f"{source.get('doc_id', '')}_{source.get('chunk_index', '')}_{source.get('content', '')[:50]}"
                    if source_id not in existing_source_ids:
                        rag_sources.append(source)
                        existing_source_ids.add(source_id)
                    else:
                        self.logger.debug(f"Skipping duplicate source: {source.get('doc_id', 'unknown')}")
                
                self.logger.info(f"After deduplication: {len(rag_sources)} total unique sources")
            
            await self._emit_step("context_analysis", f"Analyzing {len(rag_context)} relevant documents...", 
                                f"Found {len(rag_sources)} sources", progress=70)
            
        except Exception as e:
            self.logger.error(f"Error in RAG retrieval: {str(e)}")
            await self._emit_step("retrieval_error", "Error during knowledge base search", str(e))
            rag_context = []
            rag_sources = []
        
        # Step 3: Response Generation
        await self._emit_step("response_generation", "Generating comprehensive response...", 
                            "Combining retrieved information with AI reasoning", progress=85)
        
        try:
            # Log query expansion usage if available
            if hasattr(self.retrieval_system, 'use_query_expansion') and self.retrieval_system.use_query_expansion:
                if hasattr(self.retrieval_system, 'query_expander') and self.retrieval_system.query_expander:
                    expansion_stats = self.retrieval_system.query_expander.get_expansion_statistics()
                    self.logger.info(
                        f"Query expansion stats: {expansion_stats['successful_expansions']}"
                        f"/{expansion_stats['total_expansions']} successful, "
                        f"avg ratio: {expansion_stats['average_expansion_ratio']:.2f}"
                    )
            
            # Import LLM integration
            from .integrations.llm_integration import get_llm_integration
            
            # Get LLM client
            llm_client = get_llm_integration(model="gpt-4")
            
            # Prepare context for the LLM
            context_text = ""
            if rag_context:
                context_text = "\n\n".join([str(ctx) for ctx in rag_context])
            
            # Prepare tool results summary
            tools_summary = ""
            if tool_results:
                successful_tools = [r for r in tool_results if r.get('success')]
                if successful_tools:
                    tools_summary = f"\n\nI used {len(successful_tools)} specialized tools: {', '.join([r['tool_id'] for r in successful_tools])}"
            
            # Create a comprehensive prompt for the LLM
            system_prompt = """You are RegulAIte, an AI assistant specialized in regulatory compliance, cybersecurity, and governance. 

Your role is to provide accurate, helpful, and comprehensive responses based on the user's query and any available context or tool results.

CRITICAL FORMATTING REQUIREMENTS:
- ALWAYS start your response with a markdown header (## or ###), never with plain text
- Use proper markdown syntax throughout your entire response
- Ensure clean separation between sections with proper spacing
- Never mix plain text with markdown headers in the same paragraph

Response Structure Guidelines:
- Always structure your responses with clear sections using markdown headers (##)
- Start with a brief summary or key points if the topic is complex
- Use bullet points, numbered lists, and formatting to improve readability
- Include specific examples or actionable recommendations when relevant
- If discussing regulations or compliance, organize by categories or requirements
- For technical topics, provide both high-level overview and detailed explanations

Content Guidelines:
- Be precise and professional in your responses
- If you have relevant context or sources, reference them appropriately
- If you used specialized tools, mention how they helped inform your response
- Provide actionable insights when possible
- If you're uncertain about something, acknowledge it clearly
- Respond in the same language as the user's query
- Use proper markdown formatting for better readability

This is example of a good structure for ALL responses:
## [Main Topic/Summary]
[Brief overview or key points]

## [Detailed Analysis/Requirements/Content]
[Main content with subsections as needed]

## [Recommendations/Next Steps]
[Actionable recommendations when applicable]

## [Important Considerations/Limitations]
[Risks, limitations, or additional factors when relevant]

Remember: NEVER start with plain text - ALWAYS begin with a markdown header (##)."""

            # Build the user prompt with context
            user_prompt = f"User Query: {parsed_query.query_text}"
            
            if context_text:
                user_prompt += f"\n\nRelevant Context:\n{context_text}"
            
            if tools_summary:
                user_prompt += f"\n\nTool Analysis:{tools_summary}"
                
            if tool_results:
                # Add detailed tool results if available
                tool_details = []
                for result in tool_results:
                    if result.get('success') and result.get('result'):
                        tool_details.append(f"- {result['tool_id']}: {str(result['result'])[:200]}...")
                if tool_details:
                    user_prompt += f"\n\nDetailed Tool Results:\n" + "\n".join(tool_details)
            
            user_prompt += f"\n\nPlease provide a comprehensive, well-structured response to the user's query using proper markdown formatting with clear sections and organization."
            
            # Generate response using LLM
            await self._emit_step("llm_generation", "Generating AI response...", 
                                f"Using {llm_client.model} to process query and context")
            
            response_content = await llm_client.generate(
                prompt=user_prompt,
                system_message=system_prompt,
                temperature=0.7,
                max_tokens=2048
            )
            
            # Ensure we have a valid response
            if not response_content or not response_content.strip():
                response_content = "I apologize, but I wasn't able to generate a meaningful response to your query. Please try rephrasing your question."
            
            # Create the agent response with all collected information
            agent_response = AgentResponse(
                content=response_content,
                tools_used=[r["tool_id"] for r in tool_results if r.get("success")],
                context_used=len(rag_context) > 0,
                sources=rag_sources,
                metadata={
                    "tool_results": tool_results,
                    "context_count": len(rag_context),
                    "enhanced_query": enhanced_query,
                    "processing_time": time.time(),
                    "llm_model": llm_client.model
                }
            )
            
            await self._emit_step("completion", "Response generation completed successfully!", 
                                f"Generated {len(response_content)} character response", progress=100)
            
            return agent_response
            
        except Exception as e:
            self.logger.error(f"Error in response generation: {str(e)}")
            await self._emit_step("generation_error", "Error during response generation", str(e))
            
            # Return a fallback response
            return AgentResponse(
                content=f"I apologize, but I encountered an error while processing your query: {str(e)}",
                tools_used=[],
                context_used=False,
                error=True
            ) 