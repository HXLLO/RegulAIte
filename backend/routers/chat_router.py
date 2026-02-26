"""
FastAPI router for chat endpoints, chat history management and agent integration.
"""
import logging
import json
import uuid
import time
from typing import List, Dict, Any, Optional, Literal, Union
from fastapi import APIRouter, Depends, HTTPException, Body, Request, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
import os
from fastapi.responses import StreamingResponse
import mariadb
from datetime import timedelta
import re
import asyncio

# Import agent framework integrations
from agent_framework.integrations.chat_integration import get_chat_integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

# Models for API
class ChatMessage(BaseModel):
    """Message in a chat conversation."""
    role: Literal["user", "assistant", "system"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for chat completion."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    stream: bool = Field(False, description="Whether to stream the response")
    model: str = Field("gpt-4", description="Model to use for generation")
    temperature: float = Field(0.7, description="Temperature for generation")
    max_tokens: int = Field(2048, description="Maximum tokens in response")
    include_context: bool = Field(True, description="Whether to include RAG context")
    context_query: Optional[str] = Field(None, description="Query to use for retrieving context")
    retrieval_type: Optional[str] = Field("auto", description="Type of retrieval to use: 'hybrid', 'vector', or 'auto' (default)")
    use_agent: bool = Field(True, description="Whether to use an agent for processing (always enabled)")
    use_tree_reasoning: bool = Field(False, description="Whether to use tree-based reasoning")
    tree_template: Optional[str] = Field(None, description="ID of the decision tree template to use")
    custom_tree: Optional[Dict[str, Any]] = Field(None, description="Custom decision tree for reasoning")
    session_id: Optional[str] = Field(None, description="Session ID for chat history")


class SourceInfo(BaseModel):
    """Information about a source used in RAG retrieval."""
    doc_id: Optional[str] = Field(None, description="Document ID")
    page_number: Optional[int] = Field(1, description="Page number in document")
    score: Optional[float] = Field(None, description="Relevance score")
    retrieval_method: Optional[str] = Field("HyPE", description="Method used for retrieval")
    title: Optional[str] = Field(None, description="Document title if available")
    content: Optional[str] = Field(None, description="Actual text content from the document chunk")


class ChatResponse(BaseModel):
    """Response for a chat completion."""
    message: str = Field(..., description="Assistant response message")
    model: str = Field(..., description="Model used for generation")
    agent_used: bool = Field(True, description="Whether an agent was used (always true)")
    tree_reasoning_used: bool = Field(False, description="Whether tree reasoning was used")
    context_used: bool = Field(False, description="Whether context was used")
    session_id: str = Field(..., description="Session ID for chat history")
    timestamp: str = Field(..., description="Timestamp of the response")
    execution_id: Optional[str] = Field(None, description="ID of the execution for tracking progress")
    sources: Optional[List[SourceInfo]] = Field(None, description="Sources used in the response")
    context_quality: Optional[str] = Field(None, description="Quality assessment of the context")
    hallucination_risk: Optional[float] = Field(None, description="Risk of hallucination in the response")
    internal_thoughts: Optional[str] = Field(None, description="Internal thoughts and reasoning process")
    tools_used: Optional[List[str]] = Field(None, description="List of tools used by the agent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata from agent processing")


class ChatHistoryEntry(BaseModel):
    """Entry in chat history."""
    message_text: str = Field(..., description="Message text")
    message_role: str = Field(..., description="Message role (user or assistant)")
    timestamp: str = Field(..., description="Timestamp of the message")


class ChatHistoryResponse(BaseModel):
    """Response for chat history."""
    session_id: str = Field(..., description="Session ID")
    messages: List[ChatHistoryEntry] = Field(..., description="Chat messages")
    count: int = Field(..., description="Number of messages")


class ChatSessionsResponse(BaseModel):
    """Response for listing chat sessions."""
    sessions: List[Dict[str, Any]] = Field(..., description="List of chat sessions")
    count: int = Field(..., description="Number of sessions")


class AgentProgressResponse(BaseModel):
    """Response for agent execution progress."""
    execution_id: str = Field(..., description="ID of the execution")
    agent_id: str = Field(..., description="ID of the agent")
    progress_percent: float = Field(..., description="Percentage of completion (0-100)")
    status: str = Field(..., description="Status of the execution (running, completed, failed)")
    status_message: Optional[str] = Field(None, description="Status message or description")
    timestamp: str = Field(..., description="Timestamp of the progress update")


# Dependency to get the database connection
async def get_db_connection():
    """Get the MariaDB database connection from main application."""
    from main import get_mariadb_connection
    return get_mariadb_connection()


# Dependency to get the RAG system
async def get_rag_system():
    """Get the RAG system from main application."""
    from main import rag_system
    return rag_system


# Dependency to get the query engine
async def get_rag_query_engine():
    """Get the RAG query engine from main application."""
    from main import rag_query_engine
    return rag_query_engine


# Utility function to track agent execution
async def track_agent_execution(
    agent_id: str,
    session_id: str,
    task: str,
    model: str,
    start_time: float,
    tokens: Optional[Dict[str, int]] = None,
    error: bool = False,
    error_message: str = None
) -> int:
    """
    Track agent execution in the database.
    
    Args:
        agent_id: ID of the agent
        session_id: ID of the chat session
        task: The task or query for the agent
        model: Model used for the agent
        start_time: Start time of execution (as returned by time.time())
        tokens: Optional dictionary with token counts
        error: Whether an error occurred
        error_message: Error message if an error occurred
        
    Returns:
        ID of the execution record
    """
    try:
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Get token counts if available
        prompt_tokens = tokens.get("prompt_tokens", 0) if tokens else 0
        completion_tokens = tokens.get("completion_tokens", 0) if tokens else 0
        total_tokens = tokens.get("total_tokens", 0) if tokens else 0
        
        # Get database connection
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        # Insert execution record
        cursor.execute(
            """
            INSERT INTO agent_executions (
                agent_id, session_id, task, model,
                response_time_ms, token_count, prompt_token_count,
                completion_token_count, error, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                agent_id, session_id, task, model,
                response_time_ms, total_tokens, prompt_tokens,
                completion_tokens, error, error_message
            )
        )
        
        conn.commit()
        execution_id = cursor.lastrowid
        
        # Initialize progress at 100% if already completed
        if not error:
            cursor.execute(
                """
                INSERT INTO agent_progress (
                    execution_id, progress_percent, status, status_message
                ) VALUES (?, ?, ?, ?)
                """,
                (execution_id, 100.0, "completed", "Task completed successfully")
            )
        else:
            cursor.execute(
                """
                INSERT INTO agent_progress (
                    execution_id, progress_percent, status, status_message
                ) VALUES (?, ?, ?, ?)
                """,
                (execution_id, 0.0, "failed", error_message or "Task failed")
            )
            
        conn.commit()
        conn.close()
        
        return execution_id
    except Exception as e:
        logger.error(f"Error tracking agent execution: {str(e)}")
        return None


# Background task for updating analytics
async def update_agent_analytics(agent_id: str, execution_id: int, rating: Optional[int] = None):
    """
    Update agent analytics based on execution data.
    
    Args:
        agent_id: ID of the agent
        execution_id: ID of the execution
        rating: Optional rating from feedback
    """
    try:
        # Get database connection
        conn = await get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get execution data
        cursor.execute(
            """
            SELECT 
                response_time_ms, error,
                DATE(timestamp) as execution_date,
                user_id
            FROM agent_executions ae
            JOIN chat_history ch ON ae.session_id = ch.session_id
            WHERE ae.id = ?
            LIMIT 1
            """,
            (execution_id,)
        )
        
        execution = cursor.fetchone()
        if not execution:
            conn.close()
            return
            
        # Get or create analytics record for the day
        cursor.execute(
            """
            SELECT * FROM agent_analytics
            WHERE agent_id = ? AND day = ?
            """,
            (agent_id, execution["execution_date"])
        )
        
        analytics = cursor.fetchone()
        
        if analytics:
            # Update existing record
            cursor.execute(
                """
                UPDATE agent_analytics SET
                    execution_count = execution_count + 1,
                    avg_response_time_ms = ((avg_response_time_ms * execution_count) + ?) / (execution_count + 1),
                    error_rate = ((error_rate * execution_count) + ?) / (execution_count + 1)
                WHERE id = ?
                """,
                (
                    execution["response_time_ms"] or 0,
                    1 if execution["error"] else 0,
                    analytics["id"]
                )
            )
        else:
            # Create new record
            cursor.execute(
                """
                INSERT INTO agent_analytics (
                    agent_id, day, execution_count, avg_response_time_ms, error_rate
                ) VALUES (?, ?, 1, ?, ?)
                """,
                (
                    agent_id,
                    execution["execution_date"],
                    execution["response_time_ms"] or 0,
                    1 if execution["error"] else 0
                )
            )
            
        # Update rating if provided
        if rating is not None and analytics:
            cursor.execute(
                """
                UPDATE agent_analytics SET
                    avg_rating = ((avg_rating * IFNULL(rating_count, 0)) + ?) / (IFNULL(rating_count, 0) + 1),
                    rating_count = IFNULL(rating_count, 0) + 1
                WHERE id = ?
                """,
                (rating, analytics["id"])
            )
            
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error updating agent analytics: {str(e)}")


# Helper function to extract user ID from request
async def extract_user_id_from_request(req: Request, provided_user_id: Optional[str] = None):
    """Extract user ID from request headers or provided user_id parameter.
    
    Args:
        req: FastAPI Request object
        provided_user_id: User ID directly provided to the endpoint
        
    Returns:
        User ID if found, None otherwise
    """
    user_id = provided_user_id
    
    # If no user_id is provided, try to get it from the request header
    if not user_id and req:
        user_id = req.headers.get("X-User-ID")
        
        # If still no user_id, try to extract from Authorization header
        if not user_id and "Authorization" in req.headers:
            auth_header = req.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                try:
                    token = auth_header.replace("Bearer ", "")
                    # Import here to avoid circular imports
                    import jwt
                    from routers.auth_router import SECRET_KEY, ALGORITHM
                    
                    # Decode token and extract user ID
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    user_id = payload.get("sub") or payload.get("user_id")
                except jwt.ExpiredSignatureError:
                    logger.warning(f"JWT token has expired - user will need to refresh")
                    # Don't fail completely, just return None to indicate no valid auth
                    user_id = None
                except jwt.InvalidTokenError:
                    logger.warning(f"Invalid JWT token provided")
                    # Don't fail completely, just return None to indicate no valid auth
                    user_id = None
                except Exception as e:
                    logger.error(f"Error extracting user ID from token: {str(e)}")
                    # Don't fail completely, just return None to indicate no valid auth
                    user_id = None
    
    return user_id


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request, background_tasks: BackgroundTasks):
    """
    Process a chat request and generate a response.
    
    Optionally include context from the RAG system and/or use an agent for processing.
    """
    # Check if OpenAI API key is available
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    
    # Extract user ID from request if available
    user_id = await extract_user_id_from_request(req)
    
    # Generate session ID if not provided
    session_id = request.session_id or f"session_{uuid.uuid4()}"
    
    # Context retrieval - DISABLED: Agents handle their own RAG retrieval
    # Manual context retrieval is redundant since agents are always enabled
    # and they perform more sophisticated context retrieval with tools integration
    context_used = False
    context_result = None
    
    # Initialize response tracking variables
    try:
        execution_id = None
        execution_start_time = time.time()
        assistant_message = ""
        internal_thoughts = None
        agent_tools_used = []
        agent_metadata = {}

        # Get messages from request
        messages = request.messages

        # Get the last user message
        user_message = next((m.content for m in reversed(messages) if m.role == "user"), None)
        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No user message found in the chat history"
            )
            
        # Handle short follow-up messages (like "20", "yes", etc.) by adding context
        if len(user_message.strip()) <= 20 and len(messages) >= 2:
            # Find the previous user and assistant messages
            previous_messages = list(messages)
            previous_messages.reverse()
            
            # Skip the current user message
            previous_messages = previous_messages[1:]
            
            # Look for the previous user message and assistant response
            prev_user_message = next((m.content for m in previous_messages if m.role == "user"), None)
            prev_assistant_message = next((m.content for m in previous_messages if m.role == "assistant"), None)
            
            # If we found both, add a system message with context
            if prev_user_message and prev_assistant_message:
                context_message = ChatMessage(
                    role="system",
                    content=f"The user previously asked: \"{prev_user_message}\". You responded with: \"{prev_assistant_message}\". The user's follow-up message is: \"{user_message}\". Remember to maintain context from the previous exchange, especially if the follow-up message is short or ambiguous."
                )
                messages.insert(0, context_message)

        # Initialize database connection for chat history
        try:
            conn = await get_db_connection()
            cursor = conn.cursor()
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error connecting to database: {str(e)}"
            )

        # Authentication is always required for chat functionality
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Authentication required for chat functionality"
            )

        # Store user message in chat history
        try:
            cursor.execute(
                """
                INSERT INTO chat_history (user_id, session_id, message_text, message_role)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, session_id, user_message, "user")
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error storing user message in chat history: {str(e)}")
            # Continue anyway, as this is not critical

        # Get the RAG system
        rag_system = await get_rag_system()
        
        # Track token usage
        token_usage = {}
        execution_id = None
        context_used = False
        sources = None
        internal_thoughts = None
        assistant_message = ""  # Initialize to ensure it always has a value

        # Force agent usage - agents are always enabled
        request.use_agent = True
        
        # If agent-based processing is requested (which is always now)
        if request.use_agent and not request.stream:
            # Agent processing only works with non-streaming requests for now
            try:
                # Use the chat integration for agent processing
                chat_integration = get_chat_integration()
                
                # Prepare request data for the chat integration
                request_data = {
                    "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
                    "model": request.model,
                    "session_id": session_id,
                    "include_context": request.include_context,
                    "context_query": request.context_query,
                    "response_format": "markdown"
                }
                
                # Process with the agent framework
                agent_response = await chat_integration.process_chat_request(
                    request_data=request_data,
                    use_agent=True
                )
                
                if agent_response.get("error"):
                    raise Exception(agent_response.get("message", "Agent processing failed"))
                
                assistant_message = agent_response.get("message", "")
                context_used = agent_response.get("context_used", False)
                sources = agent_response.get("sources")
                
                # Extract agent metadata
                agent_tools_used = agent_response.get("tools_used")
                agent_metadata = agent_response.get("metadata", {})
                
                # If we have sources from the agent, format them for the response
                if sources:
                    # Create a compatible context_result structure for the return statement
                    context_result = {
                        "sources": sources,
                        "context_quality": "agent_processed",
                        "hallucination_risk": None
                    }
                
                # Create agent execution tracking
                cursor.execute(
                    """
                    INSERT INTO agent_executions (
                        agent_id, session_id, task, model, error
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (request.model, session_id, user_message, request.model, False)
                )
                conn.commit()
                execution_id = cursor.lastrowid
                
                # Initialize and complete progress
                cursor.execute(
                    """
                    INSERT INTO agent_progress (
                        execution_id, progress_percent, status, status_message
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (execution_id, 100.0, "completed", "Agent processing completed")
                )
                conn.commit()
                
            except Exception as e:
                logger.error(f"Error in agent processing: {str(e)}")
                
                # Update execution record with error if exists
                if execution_id:
                    cursor.execute(
                        """
                        UPDATE agent_executions SET
                            error = 1, error_message = ?
                        WHERE id = ?
                        """,
                        (str(e), execution_id)
                    )
                    
                    cursor.execute(
                        """
                        UPDATE agent_progress SET
                            status = 'failed', status_message = ?, progress_percent = 0
                        WHERE execution_id = ?
                        """,
                        (f"Error: {str(e)}", execution_id)
                    )
                    conn.commit()
                    
                # Set a fallback error message and fall through to standard RAG processing
                logger.info("Falling back to standard RAG processing due to agent error")
                assistant_message = ""  # Reset to trigger standard processing
                
        # Enhanced agent streaming support (always enabled)
        if request.use_agent and request.stream:
            # Handle streaming agent processing
            async def generate_agent_stream():
                try:
                    # Start streaming response with request tracking
                    request_start = time.time()
                    request_id = f"agent_stream_{int(request_start)}_{uuid.uuid4().hex[:8]}"
                    
                    yield json.dumps({
                        "type": "start",
                        "timestamp": datetime.now().isoformat(),
                        "request_id": request_id,
                        "agent_mode": True
                    }) + "\n"
                    
                    # Use the chat integration for agent processing with streaming
                    chat_integration = get_chat_integration()
                    
                    # Set up step callback to stream agent steps
                    async def step_callback(step_data):
                        # This callback will be called by the agent during processing
                        # We need to yield the step data through the generator
                        nonlocal step_queue
                        await step_queue.put(step_data)
                    
                    # Create a queue to handle step data from the callback
                    step_queue = asyncio.Queue()
                    chat_integration.set_step_callback(step_callback)
                    
                    # Prepare request data for the chat integration
                    request_data = {
                        "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
                        "model": request.model,
                        "session_id": session_id,
                        "include_context": request.include_context,
                        "context_query": request.context_query,
                        "response_format": "markdown"
                    }
                    
                    # Start agent processing in a task
                    async def process_agent():
                        try:
                            agent_response = await chat_integration.process_chat_request(
                                request_data=request_data,
                                use_agent=True
                            )
                            await step_queue.put({"type": "agent_complete", "response": agent_response})
                        except Exception as e:
                            await step_queue.put({"type": "agent_error", "error": str(e)})
                    
                    # Start the agent processing task
                    agent_task = asyncio.create_task(process_agent())
                    
                    # Stream steps as they come in
                    agent_response = None
                    while True:
                        try:
                            # Wait for step data with timeout
                            step_data = await asyncio.wait_for(step_queue.get(), timeout=1.0)
                            
                            if step_data.get("type") == "agent_complete":
                                agent_response = step_data.get("response")
                                break
                            elif step_data.get("type") == "agent_error":
                                yield json.dumps({
                                    "type": "error",
                                    "message": f"Agent processing failed: {step_data.get('error')}",
                                    "error_code": "AGENT_ERROR"
                                }) + "\n"
                                return
                            else:
                                # Check if this is a detailed log event
                                if step_data.get("type") == "agent_detailed_log":
                                    # Forward detailed log events directly
                                    yield json.dumps(step_data) + "\n"
                                else:
                                    # Regular step data
                                    yield json.dumps({
                                        "type": "agent_step",
                                        "step": step_data.get("step"),
                                        "message": step_data.get("message"),
                                        "details": step_data.get("details"),
                                        "progress": step_data.get("progress"),
                                        "execution_id": step_data.get("execution_id"),
                                        "timestamp": datetime.now().isoformat()
                                    }) + "\n"
                                
                        except asyncio.TimeoutError:
                            # Check if agent task is still running
                            if agent_task.done():
                                break
                            # Send heartbeat
                            yield json.dumps({
                                "type": "processing",
                                "state": "Agent processing in progress...",
                                "step": "heartbeat",
                                "timestamp": datetime.now().isoformat()
                            }) + "\n"
                    
                    # Wait for agent task to complete if not already done
                    if not agent_task.done():
                        await agent_task
                    
                    if not agent_response:
                        yield json.dumps({
                            "type": "error",
                            "message": "Agent processing completed but no response received",
                            "error_code": "NO_RESPONSE"
                        }) + "\n"
                        return
                    
                    if agent_response.get("error"):
                        yield json.dumps({
                            "type": "error",
                            "message": agent_response.get("message", "Agent processing failed"),
                            "error_code": "AGENT_ERROR"
                        }) + "\n"
                        return
                    
                    # Stream the final response
                    assistant_message = agent_response.get("message", "")
                    
                    # Ensure assistant_message is a string (handle FormattedResponse objects)
                    if hasattr(assistant_message, 'content'):
                        # If it's a FormattedResponse object, extract the content
                        assistant_message = assistant_message.content
                    elif not isinstance(assistant_message, str):
                        # If it's any other type, convert to string
                        assistant_message = str(assistant_message)
                    
                    # Ensure we have a valid string
                    if not assistant_message:
                        assistant_message = "I apologize, but I wasn't able to generate a response to your query."
                    
                    # Send the response as tokens for consistent UI handling
                    if assistant_message:
                        # Split into chunks for streaming effect
                        chunk_size = 10
                        for i in range(0, len(assistant_message), chunk_size):
                            chunk = assistant_message[i:i + chunk_size]
                            yield json.dumps({
                                "type": "token",
                                "content": chunk
                            }) + "\n"
                            await asyncio.sleep(0.01)  # Small delay for streaming effect
                    
                    # Store the assistant response in chat history
                    try:
                        # Create a new database connection for storing the response
                        stream_conn = await get_db_connection()
                        stream_cursor = stream_conn.cursor()
                        
                        stream_cursor.execute(
                            """
                            INSERT INTO chat_history (user_id, session_id, message_text, message_role)
                            VALUES (?, ?, ?, ?)
                            """,
                            (user_id, session_id, assistant_message, "assistant")
                        )
                        stream_conn.commit()
                        stream_cursor.close()
                        stream_conn.close()
                        logger.info(f"Stored agent streaming response in chat history for session {session_id}")
                    except Exception as e:
                        logger.error(f"Error storing agent streaming response in chat history: {str(e)}")
                        # Continue anyway, as this is not critical
                    
                    # Send completion event
                    yield json.dumps({
                        "type": "end",
                        "message": assistant_message,
                        "model": request.model,
                        "context_used": agent_response.get("context_used", False),
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "sources": agent_response.get("sources", []),
                        "tools_used": agent_response.get("tools_used", []),
                        "agent_used": True,  # Always true since agents are always enabled
                        "execution_id": agent_response.get("execution_id")
                    }) + "\n"
                    
                except Exception as e:
                    logger.error(f"Error in agent streaming: {str(e)}")
                    yield json.dumps({
                        "type": "error",
                        "message": f"Agent streaming error: {str(e)}",
                        "error_code": "AGENT_STREAM_ERROR"
                    }) + "\n"
            
            return StreamingResponse(generate_agent_stream(), media_type="text/event-stream")
            
        # If we reach here without an assistant_message, it means agent processing failed
        # Provide a simple error response instead of complex fallback processing
        if not assistant_message:
            assistant_message = "I apologize, but I encountered an issue while processing your request. Please try again or rephrase your question."
            logger.warning("Agent processing completed but no assistant message was generated")

        # Store assistant response in chat history (only for non-streaming responses)
        if not request.stream:
            try:
                cursor.execute(
                    """
                    INSERT INTO chat_history (user_id, session_id, message_text, message_role)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, session_id, assistant_message, "assistant")
                )
                conn.commit()
            except Exception as e:
                logger.error(f"Error storing assistant response in chat history: {str(e)}")
                # Continue anyway, as this is not critical

            # Close database connection
            conn.close()
            
            # Ensure assistant_message is not empty
            if not assistant_message or assistant_message.strip() == "":
                assistant_message = "I apologize, but I wasn't able to generate a response to your query. Please try rephrasing your question or try again."
            
            # Return final chat response
            return ChatResponse(
                message=assistant_message,
                model=request.model,
                agent_used=True,  # Always true since agents are always enabled
                tree_reasoning_used=request.use_tree_reasoning,
                context_used=context_used,
                session_id=session_id,
                timestamp=datetime.now().isoformat(),
                execution_id=str(execution_id) if execution_id else None,
                sources=context_result.get("sources") if context_result else None,
                context_quality=context_result.get("context_quality") if context_result else None,
                hallucination_risk=context_result.get("hallucination_risk") if context_result else None,
                internal_thoughts=internal_thoughts,
                tools_used=agent_tools_used if 'agent_tools_used' in locals() else None,
                metadata=agent_metadata if 'agent_metadata' in locals() else None
            )
        # For streaming responses, we've already returned a StreamingResponse

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in chat endpoint: {str(e)}"
        )


async def process_history_entries(entries):
    """Process chat history entries to ensure proper format.
    
    Args:
        entries: List of chat history entries from database
        
    Returns:
        Processed list of entries with correct data types
    """
    processed_entries = []
    for entry in entries:
        # Convert datetime timestamp to ISO format string
        if isinstance(entry["timestamp"], datetime):
            entry["timestamp"] = entry["timestamp"].isoformat()
        processed_entries.append(entry)
    return processed_entries


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    skip_old: bool = False,
    max_age_days: Optional[int] = None,
    req: Request = None
):
    """Get chat history for a session.
    
    Args:
        session_id: ID of the chat session
        limit: Maximum number of messages to return (default: 50)
        skip_old: If true, only return messages within max_age_days
        max_age_days: Maximum age of messages to retrieve
    """
    try:
        # Authentication might be required for accessing chat history
        user_id = await extract_user_id_from_request(req)
        
        # Get database connection
        conn = await get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verify the session belongs to the user if user_id is provided
        if user_id and os.getenv("REQUIRE_AUTH", "false").lower() == "true":
            cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM chat_history 
                WHERE session_id = ? AND user_id = ?
                LIMIT 1
                """,
                (session_id, user_id)
            )
            
            result = cursor.fetchone()
            if result and result["count"] == 0:
                conn.close()
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to access this chat session"
                )

        # Base query
        query = """
            SELECT message_text, message_role, timestamp
            FROM chat_history
            WHERE session_id = ?
        """
        params = [session_id]

        # Add user check if user_id is available
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        # Add age filter if requested
        if skip_old or max_age_days:
            if max_age_days:
                query += " AND timestamp >= DATE_SUB(NOW(), INTERVAL ? DAY)"
                params.append(max_age_days)
            elif skip_old:
                query += " AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)"

        # Add ordering and limit
        query += " ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        history = cursor.fetchall()
        conn.close()

        # Process the timestamps to ensure they are strings
        processed_history = await process_history_entries(history)

        return ChatHistoryResponse(
            session_id=session_id,
            messages=processed_history,
            count=len(processed_history)
        )
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )


@router.get("/sessions", response_model=ChatSessionsResponse)
async def get_chat_sessions(
    user_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    req: Request = None
):
    """Get chat sessions for the current user.
    
    Args:
        user_id: Optional user ID to filter sessions
        limit: Maximum number of sessions to return
        offset: Offset for pagination
    """
    try:
        # Authentication is preferred but not required for viewing sessions
        user_id = await extract_user_id_from_request(req, user_id)
        
        # If no user_id is available, try to continue with a warning but don't fail
        if not user_id:
            logger.warning("No user authentication available for viewing chat sessions")
            # Return empty sessions list instead of failing
            return ChatSessionsResponse(
                sessions=[],
                count=0
            )

        conn = await get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if the chat_sessions table exists
        try:
            cursor.execute("SHOW TABLES LIKE 'chat_sessions'")
            table_exists = cursor.fetchone() is not None
        except:
            table_exists = False
            
        if table_exists:
            # Query the dedicated sessions table if it exists
            query = """
                SELECT 
                    session_id, 
                    user_id,
                    title,
                    created_at,
                    last_message_time,
                    preview,
                    message_count
                FROM chat_sessions
                WHERE user_id = ?
                ORDER BY last_message_time DESC
                LIMIT ? OFFSET ?
            """
            params = [user_id, limit, offset]
            
            cursor.execute(query, params)
            sessions = cursor.fetchall()
        else:
            # Fallback to aggregating from chat_history (legacy approach)
            query = """
                SELECT session_id, user_id,
                       MAX(timestamp) as last_message_time,
                       COUNT(*) as message_count
                FROM chat_history
                WHERE user_id = ?
                GROUP BY session_id, user_id
                ORDER BY last_message_time DESC
                LIMIT ? OFFSET ?
            """
            params = [user_id, limit, offset]

            cursor.execute(query, params)
            sessions = cursor.fetchall()

            # For each session, fetch the first message to use as a title
            for session in sessions:
                # Convert datetime to string
                if isinstance(session["last_message_time"], datetime):
                    session["last_message_time"] = session["last_message_time"].isoformat()
                    
                title_query = """
                    SELECT message_text
                    FROM chat_history
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                    LIMIT 1
                """
                cursor.execute(title_query, [session["session_id"]])
                first_message = cursor.fetchone()

                if first_message:
                    # Truncate long messages and use as session title
                    title = first_message["message_text"]
                    if len(title) > 100:
                        title = title[:97] + "..."
                    session["title"] = title
                else:
                    session["title"] = "Untitled Session"

        # Convert all datetime objects to ISO format strings
        for session in sessions:
            for key, value in session.items():
                if isinstance(value, datetime):
                    session[key] = value.isoformat()

        conn.close()

        return ChatSessionsResponse(
            sessions=sessions,
            count=len(sessions)
        )
    except Exception as e:
        logger.error(f"Error retrieving chat sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat sessions: {str(e)}"
        )


@router.delete("/history/{session_id}")
async def delete_chat_history(
    session_id: str, 
    before_days: Optional[int] = None,
    req: Request = None
):
    """Delete chat history for a specific session.
    
    Args:
        session_id: ID of the chat session to delete
        before_days: Optional number of days to keep (delete everything older)
    """
    try:
        # Authentication might be required for deleting chat history
        user_id = await extract_user_id_from_request(req)
        
        # Log the deletion request with detailed information
        logger.info(f"Received request to delete chat history. session_id={session_id}, user_id={user_id}, before_days={before_days}")
        
        # Get database connection
        conn = await get_db_connection()
        cursor = conn.cursor()
        logger.info(f"Database connection established for history deletion. session_id={session_id}")

        # If auth is required or user_id is available, verify ownership
        if user_id:
            # First check if the session belongs to the user or if it exists at all
            verify_cursor = conn.cursor(dictionary=True)
            verify_cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM chat_history 
                WHERE session_id = ? AND user_id = ?
                LIMIT 1
                """,
                (session_id, user_id)
            )
            
            result = verify_cursor.fetchone()
            logger.info(f"Ownership verification: found {result['count']} messages for user. session_id={session_id}, user_id={user_id}")
            
            # Also check if the session exists at all (for any user)
            verify_cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM chat_history 
                WHERE session_id = ?
                LIMIT 1
                """,
                (session_id,)
            )
            
            session_exists = verify_cursor.fetchone()
            verify_cursor.close()
            logger.info(f"Session verification: found {session_exists['count']} total messages. session_id={session_id}")
            
            # If the session exists but doesn't belong to the user, deny access
            if session_exists and session_exists["count"] > 0 and result and result["count"] == 0:
                logger.warning(f"Unauthorized attempt to delete chat history. session_id={session_id}, requesting_user={user_id}")
                conn.close()
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to delete this chat session"
                )
            
            # If session doesn't exist for anyone, it might be a new session without messages yet
            # We'll consider this a successful deletion (since there's nothing to delete)
            if session_exists and session_exists["count"] == 0:
                logger.info(f"No messages found for session. session_id={session_id}, user_id={user_id}")
                conn.close()
                return {
                    "session_id": session_id,
                    "deleted_count": 0,
                    "message": "Session had no messages to delete"
                }

            logger.info(f"Authorized chat history deletion. session_id={session_id}, user_id={user_id}")
            
            # Base delete query with user check
            query = "DELETE FROM chat_history WHERE session_id = ? AND user_id = ?"
            params = [session_id, user_id]
        else:
            # Base delete query without user check
            query = "DELETE FROM chat_history WHERE session_id = ?"
            params = [session_id]

        # Add age filter if requested
        if before_days is not None:
            query += " AND timestamp < DATE_SUB(NOW(), INTERVAL ? DAY)"
            params.append(before_days)
            logger.info(f"Deleting messages older than {before_days} days for session_id={session_id}")

        logger.info(f"Executing history deletion query. session_id={session_id}")
        cursor.execute(query, params)
        deleted_count = cursor.rowcount
        logger.info(f"Deleted {deleted_count} messages from chat history. session_id={session_id}")
        
        conn.commit()
        logger.info(f"Database transaction committed. session_id={session_id}")
        
        conn.close()
        logger.info(f"Database connection closed after history deletion. session_id={session_id}")

        return {
            "session_id": session_id,
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} messages from chat history"
        }
    except HTTPException as e:
        # Re-raise HTTP exceptions with proper status codes
        logger.warning(f"HTTP exception while deleting chat history: {str(e)}, session_id={session_id}")
        raise
    except Exception as e:
        logger.error(f"Error deleting chat history: {str(e)}, session_id={session_id}, user_id={user_id if 'user_id' in locals() else None}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting chat history: {str(e)}"
        )


@router.delete("/history")
async def delete_all_chat_history(
    before_days: Optional[int] = None, 
    user_id: Optional[str] = None,
    req: Request = None
):
    """Delete all chat history for the current user.
    
    Args:
        before_days: Optional number of days to keep (delete everything older)
        user_id: Optional user ID to filter sessions
    """
    try:
        # Authentication is required for deleting chat history
        user_id = await extract_user_id_from_request(req, user_id)
        
        if not user_id:
            raise HTTPException(
                status_code=401, 
                detail="Authentication required to delete chat history"
            )
            
        conn = await get_db_connection()
        cursor = conn.cursor()

        # Base delete query
        query = "DELETE FROM chat_history WHERE 1=1"
        params = []

        # Add filters if requested
        if before_days is not None:
            query += " AND timestamp < DATE_SUB(NOW(), INTERVAL ? DAY)"
            params.append(before_days)

        # Only allow users to delete their own messages
        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)

        cursor.execute(query, params)
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return {
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} messages from chat history"
        }
    except Exception as e:
        logger.error(f"Error deleting chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting chat history: {str(e)}"
        )


@router.get("/messages", response_model=ChatHistoryResponse)
async def get_chat_messages(
    session_id: str,
    limit: int = 50,
    skip_old: bool = False,
    max_age_days: Optional[int] = None,
    req: Request = None
):
    """Get messages for a chat session (alias for get_chat_history).
    
    Args:
        session_id: ID of the chat session
        limit: Maximum number of messages to return (default: 50)
        skip_old: If true, only return messages within max_age_days 
        max_age_days: Maximum age of messages to retrieve
    """
    try:
        # Authentication might be required for accessing chat history
        user_id = await extract_user_id_from_request(req)
        
        # Get database connection
        conn = await get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Base query
        query = """
            SELECT message_text, message_role, timestamp
            FROM chat_history
            WHERE session_id = ?
        """
        params = [session_id]

        # Add user check if user_id is available
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        # Add age filter if requested
        if skip_old or max_age_days:
            if max_age_days:
                query += " AND timestamp >= DATE_SUB(NOW(), INTERVAL ? DAY)"
                params.append(max_age_days)
            elif skip_old:
                query += " AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)"

        # Add ordering and limit
        query += " ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        history = cursor.fetchall()
        conn.close()

        # Process the timestamps to ensure they are strings
        processed_history = await process_history_entries(history)

        return ChatHistoryResponse(
            session_id=session_id,
            messages=processed_history,
            count=len(processed_history)
        )
    except Exception as e:
        logger.error(f"Error retrieving chat messages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat messages: {str(e)}"
        )


@router.post("/sessions", response_model=dict)
async def create_chat_session(
    user_id: Optional[str] = None,
    req: Request = None
):
    """Create a new chat session.
    
    Args:
        user_id: The user ID to associate with the session (optional)
    """
    try:
        # Authentication is always required for creating new chat sessions
        user_id = await extract_user_id_from_request(req, user_id)
        
        # If no user_id is available, return error
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Authentication required to create chat sessions"
            )
        
        # Generate a unique session ID
        session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Insert session into the chat_sessions table if it exists
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if the chat_sessions table exists
            cursor.execute("SHOW TABLES LIKE 'chat_sessions'")
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Insert into the dedicated sessions table
                cursor.execute(
                    """
                    INSERT INTO chat_sessions 
                    (session_id, user_id, title, created_at, last_message_time)
                    VALUES (?, ?, ?, NOW(), NOW())
                    """,
                    (session_id, user_id, "New Conversation")
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to insert into chat_sessions table: {str(e)}")
        finally:
            conn.close()
        
        # Return the session ID
        return {
            "session_id": session_id,
            "user_id": user_id,
            "message": "Session created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating chat session: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=ChatHistoryResponse)
async def get_session_messages(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    skip_old: bool = False,
    max_age_days: Optional[int] = None,
    req: Request = None
):
    """Get messages for a specific chat session.
    
    Args:
        session_id: ID of the chat session
        limit: Maximum number of messages to return (default: 50)
        offset: Offset for pagination
        skip_old: If true, only return messages within max_age_days
        max_age_days: Maximum age of messages to retrieve
    """
    try:
        # Authentication might be required for accessing chat history
        user_id = await extract_user_id_from_request(req)
        
        # Get database connection
        conn = await get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verify the session belongs to the user if user_id is provided
        if user_id and os.getenv("REQUIRE_AUTH", "false").lower() == "true":
            cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM chat_history 
                WHERE session_id = ? AND user_id = ?
                LIMIT 1
                """,
                (session_id, user_id)
            )
            
            result = cursor.fetchone()
            
            # Also check if the session exists at all (for any user)
            cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM chat_history 
                WHERE session_id = ?
                LIMIT 1
                """,
                (session_id,)
            )
            
            session_exists = cursor.fetchone()
            
            # If session doesn't exist at all
            if not session_exists or session_exists["count"] == 0:
                conn.close()
                raise HTTPException(
                    status_code=404,
                    detail="Chat session not found. It may have been deleted."
                )
            
            # If the session exists but doesn't belong to the user, deny access
            if result and result["count"] == 0:
                conn.close()
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to access this chat session"
                )

        # Base query
        query = """
            SELECT message_text, message_role, timestamp
            FROM chat_history
            WHERE session_id = ?
        """
        params = [session_id]

        # Add user check if user_id is available
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        # Add age filter if requested
        if skip_old or max_age_days:
            if max_age_days:
                query += " AND timestamp >= DATE_SUB(NOW(), INTERVAL ? DAY)"
                params.append(max_age_days)
            elif skip_old:
                query += " AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)"

        # Add ordering and limit
        query += " ORDER BY timestamp ASC"
        
        # Add pagination if offset is provided
        if offset > 0:
            query += " LIMIT ?, ?"
            params.extend([offset, limit])
        else:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        history = cursor.fetchall()
        conn.close()

        # If no history found, check if session actually exists
        if not history:
            # For an existing session with no messages, return empty list
            return ChatHistoryResponse(
                session_id=session_id,
                messages=[],
                count=0
            )

        # Process the timestamps to ensure they are strings
        processed_history = await process_history_entries(history)

        return ChatHistoryResponse(
            session_id=session_id,
            messages=processed_history,
            count=len(processed_history)
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving session messages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session messages: {str(e)}"
        )


@router.get("/progress/{execution_id}", response_model=AgentProgressResponse)
async def get_agent_progress(execution_id: str):
    """Get progress information for an agent execution."""
    try:
        # Get database connection
        conn = await get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query execution info
        cursor.execute(
            """
            SELECT 
                ae.agent_id,
                ap.progress_percent,
                ap.status,
                ap.status_message,
                ap.timestamp
            FROM agent_progress ap
            JOIN agent_executions ae ON ap.execution_id = ae.id
            WHERE ap.execution_id = ?
            ORDER BY ap.timestamp DESC
            LIMIT 1
            """,
            (execution_id,)
        )
        
        progress = cursor.fetchone()
        
        if not progress:
            raise HTTPException(
                status_code=404,
                detail=f"Progress information not found for execution: {execution_id}"
            )
            
        conn.close()
        
        return AgentProgressResponse(
            execution_id=execution_id,
            agent_id=progress["agent_id"],
            progress_percent=progress["progress_percent"],
            status=progress["status"],
            status_message=progress["status_message"],
            timestamp=progress["timestamp"].isoformat() if isinstance(progress["timestamp"], datetime) else progress["timestamp"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent progress: {str(e)}"
        )


@router.delete("/sessions/{session_id}", response_model=dict)
async def delete_chat_session(
    session_id: str,
    before_days: Optional[int] = None,
    req: Request = None
):
    """Delete a chat session and its messages."""
    # Extract user ID from request
    user_id = await extract_user_id_from_request(req)
    
    # Log the deletion request with more details
    logger.info(f"Received request to delete chat session. session_id={session_id}, user_id={user_id}, before_days={before_days}")
    
    # Initialize database connection
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        logger.info(f"Database connection established for session deletion. session_id={session_id}")
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to database: {str(e)}"
        )
        
    # Check if session exists
    try:
        cursor.execute(
            """
            SELECT session_id, user_id FROM chat_sessions 
            WHERE session_id = ?
            """,
            (session_id,)
        )
        session = cursor.fetchone()
        
        # If session not found in chat_sessions, check chat_history as fallback
        if not session:
            logger.info(f"Session not found in chat_sessions, checking chat_history. session_id={session_id}")
            cursor.execute(
                """
                SELECT session_id, user_id FROM chat_history 
                WHERE session_id = ?
                GROUP BY session_id, user_id
                """,
                (session_id,)
            )
            session = cursor.fetchone()
            
        if not session:
            logger.warning(f"Session not found for deletion. session_id={session_id}, user_id={user_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Session with ID {session_id} not found"
            )
            
        # Verify ownership
        if session[1] != user_id:
            logger.warning(f"Unauthorized attempt to delete session. session_id={session_id}, requesting_user={user_id}, owner_user={session[1]}")
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this session"
            )
            
        logger.info(f"Authorized session deletion. session_id={session_id}, user_id={user_id}")
            
        # Construct date filter if before_days is provided
        date_filter = ""
        date_filter_params = ()
        if before_days is not None:
            # Use MariaDB date syntax instead of SQLite
            date_filter = "AND timestamp < DATE_SUB(NOW(), INTERVAL ? DAY)"
            date_filter_params = (before_days,)
            logger.info(f"Deleting messages older than {before_days} days for session_id={session_id}")
            
        # Delete messages
        logger.info(f"Executing message deletion for session_id={session_id}")
        cursor.execute(
            f"""
            DELETE FROM chat_history 
            WHERE session_id = ? {date_filter}
            """,
            (session_id,) + date_filter_params
        )
        messages_deleted = cursor.rowcount
        logger.info(f"Deleted {messages_deleted} messages from session_id={session_id}")
        
        # If deleting all messages (no date filter or all messages match filter)
        if before_days is None or messages_deleted > 0:
            # Check if any messages remain
            cursor.execute(
                """
                SELECT COUNT(*) FROM chat_history 
                WHERE session_id = ?
                """,
                (session_id,)
            )
            remaining_messages = cursor.fetchone()[0]
            logger.info(f"Remaining messages after deletion: {remaining_messages}, session_id={session_id}")
            
            # If no messages remain, delete the session record
            if remaining_messages == 0:
                logger.info(f"No messages remain, deleting session record. session_id={session_id}")
                try:
                    cursor.execute(
                        """
                        DELETE FROM chat_sessions 
                        WHERE session_id = ?
                        """,
                        (session_id,)
                    )
                    logger.info(f"Session record deleted successfully. session_id={session_id}")
                except Exception as e:
                    # Log but continue if deleting from chat_sessions fails
                    logger.warning(f"Could not delete from chat_sessions: {str(e)}, session_id={session_id}")
                
        conn.commit()
        logger.info(f"Chat session deletion completed successfully. session_id={session_id}, messages_deleted={messages_deleted}")
        
        return {
            "status": "success",
            "message": f"Chat session {session_id} deleted successfully",
            "messages_deleted": messages_deleted
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {str(e)}, session_id={session_id}, user_id={user_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting chat session: {str(e)}"
        )
    finally:
        # Close database connection
        if conn:
            conn.close()
            logger.info(f"Database connection closed after session deletion. session_id={session_id}")
