"""
Chat Integration for the RegulAIte Agent Framework.

This module provides integration between the chat router and the agent framework.
"""
from typing import Dict, List, Optional, Any, Union, Callable
import logging
import sys
from pathlib import Path
import json
import time
import asyncio

# Set up logging
logger = logging.getLogger(__name__)

# Import at the module level
from ..factory import get_agent_instance
from ..agent import Query, AgentResponse, QueryContext, Agent, IterationMode
from ..response_generator import ResponseGenerator, ResponseFormat
from ..rag_agent import RAGAgent

class ChatIntegration:
    """
    Integration layer between the chat system and agent framework.
    
    This class handles the communication between the chat API and
    the various agents, managing request routing and response formatting.
    """
    
    def __init__(self):
        """Initialize the chat integration."""
        self.response_generator = ResponseGenerator()
        self.logger = logging.getLogger("chat_integration")
        
        # Available agent types
        self.agent_types = {
            "rag": RAGAgent,
            "general": Agent
        }
        
        # Step streaming callback
        self.step_callback = None
        
    def set_step_callback(self, callback: Callable):
        """
        Set a callback function to receive agent processing steps.
        
        Args:
            callback: Function to call with step updates
        """
        self.step_callback = callback
        
    async def _emit_agent_step(self, step_data: Dict[str, Any]):
        """
        Emit an agent processing step.
        
        Args:
            step_data: Step information to emit
        """
        if self.step_callback:
            try:
                if asyncio.iscoroutinefunction(self.step_callback):
                    await self.step_callback(step_data)
                else:
                    self.step_callback(step_data)
            except Exception as e:
                self.logger.error(f"Error in step callback: {e}")
        
    async def process_chat_request(
        self, 
        request_data: Dict[str, Any], 
        use_agent: bool = True,  # Always True - agents are always enabled
        agent_type: str = "rag"
    ) -> Dict[str, Any]:
        """
        Process a chat request using the agent framework.
        
        Args:
            request_data: The chat request data
            use_agent: Whether to use agent processing (always True)
            agent_type: Type of agent to use
            
        Returns:
            Dict containing the response and metadata
        """
        # Force agent usage - agents are always enabled
        use_agent = True
        
        try:
            # Extract request information
            messages = request_data.get("messages", [])
            model = request_data.get("model", "gpt-4")
            session_id = request_data.get("session_id")
            include_context = request_data.get("include_context", True)
            context_query = request_data.get("context_query")
            response_format = request_data.get("response_format", "markdown")
            
            # Get the user message (last message should be from user)
            user_message = ""
            if messages:
                user_message = messages[-1].get("content", "")
            
            if not user_message:
                return {
                    "message": "No user message found in the request.",
                    "error": True,
                    "model": model,
                    "agent_type": "orchestrator",
                    "agent_used": False,
                    "context_used": False,
                    "session_id": session_id,
                    "timestamp": time.time()
                }
            
            # Record start time for performance measurement
            start_time = time.time()
            
            # Emit initial step
            await self._emit_agent_step({
                "step": "initialization",
                "message": "Initializing agent processing...",
                "details": f"Using {agent_type} agent with {model} model",
                "progress": 5,
                "timestamp": time.time()
            })
            
            # Use the global orchestrator that has all agents registered
            # This ensures we use the orchestrator with all specialized agents
            
            # Create a detailed log callback for the agent
            async def detailed_log_callback(log_data):
                """Forward detailed logs as specific detailed log events."""
                # Create a detailed log event
                detailed_log_event = {
                    "type": "agent_detailed_log",
                    "log_entry": log_data,
                    "timestamp": time.time()
                }
                await self._emit_agent_step(detailed_log_event)
            
            # Get the global orchestrator instance (the one with registered agents)
            try:
                from main import get_global_orchestrator
                agent = await get_global_orchestrator()
                if not agent:
                    raise Exception("Global orchestrator not available")
                # Set the log callback on the orchestrator
                if hasattr(agent, 'set_log_callback'):
                    agent.set_log_callback(detailed_log_callback)
            except Exception as e:
                logger.warning(f"Could not get global orchestrator: {e}. Creating fallback agent.")
                # Fallback to creating a new orchestrator as before
                agent = await get_agent_instance(
                    agent_type="orchestrator",
                    model=model,
                    log_callback=detailed_log_callback
                )
            
            # Generate execution ID for tracking
            execution_id = f"exec_{int(time.time())}_{session_id}"
            
            # Create query context
            query_context = QueryContext(
                session_id=session_id,
                metadata={"previous_messages": messages[:-1] if len(messages) > 1 else []}
            )
            
            # Create the query with iteration mode for detailed analysis
            query = Query(
                query_text=user_message,
                context=query_context,
                iteration_mode=IterationMode.ITERATIVE  # Enable iterative processing for detailed logging
            )
            
            # Emit agent start step
            await self._emit_agent_step({
                "step": "agent_start",
                "message": f"Starting orchestrator agent processing...",
                "details": f"Query: {user_message[:100]}{'...' if len(user_message) > 100 else ''}",
                "progress": 15,
                "timestamp": time.time(),
                "execution_id": execution_id
            })
            
            # Process the query
            agent_response = await agent.process_query(query)
            
            # Ensure we have a valid response
            if not agent_response or not agent_response.content:
                await self._emit_agent_step({
                    "step": "agent_error",
                    "message": "Agent failed to generate a response",
                    "details": "No content returned from agent",
                    "timestamp": time.time(),
                    "execution_id": execution_id
                })
                
                return {
                    "message": "I apologize, but I wasn't able to generate a response to your query. Please try rephrasing your question.",
                    "error": False,
                    "model": model,
                    "agent_type": "orchestrator",
                    "agent_used": True,  # Always True since agents are always enabled
                    "context_used": False,
                    "session_id": session_id,
                    "timestamp": time.time()
                }
            
            # Format the response
            await self._emit_agent_step({
                "step": "response_formatting",
                "message": "Formatting response...",
                "details": f"Response length: {len(agent_response.content)} characters",
                "progress": 95,
                "timestamp": time.time(),
                "execution_id": execution_id
            })
            
            formatted_response = await self.response_generator.generate(
                response=agent_response,
                query=query,
                format=response_format
            )
            
            # Extract the content string from the FormattedResponse object
            if hasattr(formatted_response, 'content'):
                response_content = formatted_response.content
            elif isinstance(formatted_response, str):
                response_content = formatted_response
            else:
                # Fallback: convert to string
                response_content = str(formatted_response)
                
            # Ensure we have a valid string
            if not isinstance(response_content, str):
                response_content = str(response_content)
                
            # Ensure the response is not empty
            if not response_content.strip():
                response_content = "I apologize, but I wasn't able to generate a meaningful response to your query. Please try rephrasing your question."
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Final completion step
            await self._emit_agent_step({
                "step": "completion",
                "message": "Agent processing completed successfully!",
                "details": f"Total execution time: {execution_time:.2f}s",
                "progress": 100,
                "timestamp": time.time(),
                "execution_id": execution_id
            })
            
            # Process and format sources to match the expected SourceInfo structure
            formatted_sources = []
            raw_sources = getattr(agent_response, 'sources', [])
            
            self.logger.info(f"Processing {len(raw_sources)} raw sources from agent response")
            
            if raw_sources:
                for i, source in enumerate(raw_sources):
                    try:
                        if isinstance(source, dict):
                            self.logger.debug(f"Source {i} keys: {list(source.keys())}")
                            self.logger.debug(f"Source {i} sample values: filename='{source.get('filename')}', title='{source.get('title')}', doc_id='{source.get('doc_id')}', score={source.get('score')}")
                            
                            # Handle different source formats
                            if 'source' in source:
                                # Format: {'source': {...}, 'agent': '...', 'iteration': ...}
                                source_data = source['source']
                                self.logger.debug(f"Nested source data keys: {list(source_data.keys())}")
                                
                                formatted_source = {
                                    "doc_id": source_data.get('id') or source_data.get('doc_id', 'unknown'),
                                    "title": (source_data.get('title') or 
                                            source_data.get('filename') or 
                                            source_data.get('original_filename') or 
                                            source_data.get('name') or 
                                            f"Document {source_data.get('id', 'unknown')}"),
                                    "filename": source_data.get('filename') or source_data.get('original_filename'),
                                    "original_filename": source_data.get('original_filename'),
                                    "page_number": source_data.get('page_number', 1),
                                    "score": source_data.get('score') or source_data.get('relevance_score'),
                                    "relevance_score": source_data.get('relevance_score') or source_data.get('score'),
                                    "match_percentage": source_data.get('match_percentage'),
                                    "retrieval_method": source_data.get('retrieval_method', 'SEMANTIC'),
                                    "content": source_data.get('content') or source_data.get('chunk_text') or source_data.get('text'),
                                    "chunk_text": source_data.get('chunk_text') or source_data.get('content') or source_data.get('text'),
                                    "chunk_id": source_data.get('chunk_id'),
                                    "chunk_index": source_data.get('chunk_index'),
                                    "node_id": source_data.get('node_id'),
                                    "file_type": source_data.get('file_type'),
                                    "category": source_data.get('category'),
                                    "language": source_data.get('language'),
                                    "author": source_data.get('author'),
                                    "created_at": source_data.get('created_at'),
                                    "size": source_data.get('size'),
                                    "page_count": source_data.get('page_count'),
                                    "matched_via": source_data.get('matched_via'),
                                    "text_content_type": source_data.get('text_content_type'),
                                    "is_question": source_data.get('is_question')
                                }
                            else:
                                # Direct source format - this is the most common case for RAG sources
                                formatted_source = {
                                    "doc_id": source.get('doc_id') or source.get('id', 'unknown'),
                                    "title": (source.get('title') or 
                                            source.get('filename') or 
                                            source.get('original_filename') or 
                                            source.get('name') or 
                                            f"Document {source.get('doc_id', source.get('id', 'unknown'))}"),
                                    "filename": source.get('filename') or source.get('original_filename'),
                                    "original_filename": source.get('original_filename'),
                                    "page_number": source.get('page_number', 1),
                                    "score": source.get('score') or source.get('relevance_score'),
                                    "relevance_score": source.get('relevance_score') or source.get('score'),
                                    "match_percentage": source.get('match_percentage'),
                                    "retrieval_method": source.get('retrieval_method', 'SEMANTIC'),
                                    "content": source.get('content') or source.get('chunk_text') or source.get('text'),
                                    "chunk_text": source.get('chunk_text') or source.get('content') or source.get('text'),
                                    "chunk_id": source.get('chunk_id'),
                                    "chunk_index": source.get('chunk_index'),
                                    "node_id": source.get('node_id'),
                                    "file_type": source.get('file_type'),
                                    "category": source.get('category'),
                                    "language": source.get('language'),
                                    "author": source.get('author'),
                                    "created_at": source.get('created_at'),
                                    "size": source.get('size'),
                                    "page_count": source.get('page_count'),
                                    "matched_via": source.get('matched_via'),
                                    "text_content_type": source.get('text_content_type'),
                                    "is_question": source.get('is_question')
                                }
                            
                            # Calculate match percentage from score if not already present
                            if not formatted_source.get('match_percentage') and formatted_source.get('score'):
                                try:
                                    score = float(formatted_source['score'])
                                    formatted_source['match_percentage'] = round(score * 100, 1)
                                except (ValueError, TypeError):
                                    pass
                            
                            # Ensure we have a valid title (not "Unknown Source")
                            if not formatted_source.get('title') or formatted_source['title'] == 'Unknown Source':
                                # Try to extract a meaningful title from content or doc_id
                                if formatted_source.get('content'):
                                    # Use first 50 characters of content as title
                                    content_preview = formatted_source['content'][:50].strip()
                                    if content_preview:
                                        formatted_source['title'] = content_preview + "..."
                                elif formatted_source.get('doc_id') and formatted_source['doc_id'] != 'unknown':
                                    formatted_source['title'] = f"Document {formatted_source['doc_id'][:8]}"
                                else:
                                    formatted_source['title'] = f"Source {i+1}"
                            
                            # Ensure we have content for display
                            if not formatted_source.get('content') and not formatted_source.get('chunk_text'):
                                formatted_source['content'] = "Contenu non disponible"
                                formatted_source['chunk_text'] = "Contenu non disponible"
                            
                            # Set a default score if none is available
                            if not formatted_source.get('score') and not formatted_source.get('relevance_score'):
                                formatted_source['score'] = 0.5  # Default to medium relevance
                                formatted_source['relevance_score'] = 0.5
                                formatted_source['match_percentage'] = 50.0
                            
                            self.logger.debug(f"Formatted source {i}: title='{formatted_source['title']}', doc_id='{formatted_source['doc_id']}', score={formatted_source.get('score')}")
                            formatted_sources.append(formatted_source)
                        else:
                            # Handle string sources
                            formatted_sources.append({
                                "doc_id": "unknown",
                                "title": str(source),
                                "page_number": 1,
                                "score": None,
                                "retrieval_method": "SEMANTIC",
                                "content": None
                            })
                    except Exception as source_error:
                        self.logger.warning(f"Error formatting source {i} ({source}): {source_error}")
                        import traceback
                        self.logger.debug(f"Source formatting error traceback: {traceback.format_exc()}")
                        
                        # Add a fallback source with more debugging info
                        fallback_source = {
                            "doc_id": "unknown",
                            "title": f"Source information unavailable (error: {str(source_error)})",
                            "page_number": 1,
                            "score": None,
                            "retrieval_method": "SEMANTIC",
                            "content": None
                        }
                        
                        # Try to extract at least some information if the source is a dict
                        if isinstance(source, dict):
                            fallback_source["doc_id"] = source.get('doc_id', source.get('id', 'unknown'))
                            if source.get('title') or source.get('filename'):
                                fallback_source["title"] = source.get('title') or source.get('filename')
                        
                        formatted_sources.append(fallback_source)
            
            self.logger.info(f"Successfully formatted {len(formatted_sources)} sources for frontend display")
            
            # Log a summary of the formatted sources for debugging
            if formatted_sources:
                titles = [s.get('title', 'No title') for s in formatted_sources[:3]]  # First 3 titles
                self.logger.debug(f"Sample source titles: {titles}")
                scores = [s.get('score') for s in formatted_sources if s.get('score')]
                if scores:
                    avg_score = sum(scores) / len(scores)
                    self.logger.debug(f"Average relevance score: {avg_score:.3f}")
            else:
                self.logger.warning("No sources were successfully formatted")

            # Return the formatted response with metadata
            return {
                "message": response_content,  # Use the extracted content string
                "error": False,
                "model": model,
                "agent_type": "orchestrator",
                "agent_used": True,  # Always True since agents are always enabled
                "context_used": agent_response.context_used,
                "tools_used": agent_response.tools_used,
                "sources": formatted_sources,
                "metadata": getattr(agent_response, 'metadata', {}),
                "session_id": session_id,
                "execution_time": execution_time,
                "execution_id": execution_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in agent processing: {str(e)}")
            
            # Emit error step
            await self._emit_agent_step({
                "step": "error",
                "message": f"Agent processing failed: {str(e)}",
                "details": str(e),
                "timestamp": time.time()
            })
            
            return {
                "message": f"I encountered an error while processing your request: {str(e)}",
                "error": True,
                "model": model,
                "agent_type": "orchestrator",
                "agent_used": True,  # Always True since agents are always enabled
                "context_used": False,
                "session_id": session_id,
                "timestamp": time.time()
            }
    
    async def get_agent_for_chat(self, model: str) -> Dict[str, Any]:
        """
        Get information about the autonomous agent for the chat UI.
        
        Args:
            model: Model to use
            
        Returns:
            Information about the agent
        """
        # Import get_agent_instance lazily to avoid circular imports
        from ..factory import get_agent_instance
        
        try:
            # Autonomously determine the best agent type
            agent_type = "rag"
            
            # Get the agent instance
            agent = await get_agent_instance(
                agent_type=agent_type,
                model=model,
                log_callback=None  # No logging callback needed for agent info
            )
            
            # Get information about the agent
            return {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "type": agent_type,
                "model": model,
                "available": True
            }
            
        except Exception as e:
            logger.error(f"Error getting agent information: {str(e)}")
            return {
                "agent_id": "unknown",
                "name": "Autonomous Agent",
                "type": "autonomous",
                "model": model,
                "available": False,
                "error": str(e)
            }

# Global instance
_chat_integration = None

def get_chat_integration() -> ChatIntegration:
    """Get the global chat integration instance."""
    global _chat_integration
    if _chat_integration is None:
        _chat_integration = ChatIntegration()
    return _chat_integration

async def get_agent_instance(agent_type: str = "rag", model: str = "gpt-4", log_callback=None) -> Agent:
    """
    Get an agent instance of the specified type.
    
    Args:
        agent_type: Type of agent to create
        model: Model to use with the agent
        log_callback: Callback function for detailed logging
        
    Returns:
        Agent instance
    """
    # Import the factory function to properly create agents with all integrations
    from ..factory import get_agent_instance as factory_get_agent_instance
    
    # Use the factory function which properly initializes all integrations
    return await factory_get_agent_instance(
        agent_type=agent_type,
        model=model,
        log_callback=log_callback
    ) 