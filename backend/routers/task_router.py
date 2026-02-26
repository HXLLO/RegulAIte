from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from typing import List, Dict, Any, Optional, Set, Literal

from queuing_sys.task_router import router as queuing_task_router
# Re-export the queue_document_processing function
from queuing_sys.task_router import queue_document_processing

from pydantic import BaseModel, Field
from datetime import datetime
import logging
import uuid
import json
from fastapi.encoders import jsonable_encoder
import mariadb
import os
from dotenv import load_dotenv
import time
from unstructured_parser.base_parser import ParserType

# Load environment variables for database connection
load_dotenv()
MARIADB_HOST = os.getenv("MARIADB_HOST", "mariadb")
MARIADB_DATABASE = os.getenv("MARIADB_DATABASE", "regulaite")
MARIADB_USER = os.getenv("MARIADB_USER", "regulaite_user")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "SecureP@ssw0rd!")

logger = logging.getLogger(__name__)

# Models for chat functionality
class TaskChatMessage(BaseModel):
    """Message in task chat history"""
    message_id: str = Field(..., description="Unique message ID")
    task_id: str = Field(..., description="ID of the task this message belongs to")
    content: str = Field(..., description="Message content")
    role: Literal["user", "system", "assistant"] = Field(..., description="Role of the sender (user, system, assistant)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")

class TaskChatMessageCreate(BaseModel):
    """Request to create a new chat message for a task"""
    content: str = Field(..., description="Message content")
    role: Literal["user", "system", "assistant"] = Field(..., description="Role of the sender (user, system, assistant)")

class TasksUpdateRequest(BaseModel):
    """Request for chat updates for multiple tasks"""
    task_ids: List[str] = Field(..., description="List of task IDs to get updates for")
    since_timestamp: Optional[datetime] = Field(None, description="Only get messages after this timestamp")

class TaskChatUpdates(BaseModel):
    """Chat updates for multiple tasks"""
    task_id: str = Field(..., description="ID of the task")
    messages: List[TaskChatMessage] = Field(default_factory=list, description="List of chat messages")

class TasksChatResponse(BaseModel):
    """Response containing chat updates for multiple tasks"""
    tasks: List[TaskChatUpdates] = Field(default_factory=list, description="Updates for each requested task")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the response")

# WebSocket connection manager for chat
class ChatConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str):
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def broadcast_to_task(self, task_id: str, message: Any):
        if task_id in self.active_connections:
            json_message = jsonable_encoder(message)
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(json_message)
                except Exception as e:
                    logger.error(f"Error sending message to WebSocket: {str(e)}")

# Create connection manager instance
chat_manager = ChatConnectionManager()

# Create a new router with prefix
task_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)

# Include the queuing system's task routes
task_router.include_router(queuing_task_router)

# Additional task endpoints can be added here
@task_router.get("/status")
async def get_tasks_status():
    """Get overall status of the task queuing system."""
    return {"status": "operational", "queued_tasks": 0, "active_tasks": 0}

# Get MariaDB connection
def get_mariadb_connection():
    """Get a connection to MariaDB with retry logic."""
    conn = None
    max_retries = 3
    retry_count = 0
    last_error = None

    while retry_count < max_retries and conn is None:
        try:
            logger.info(f"Attempting to connect to MariaDB at {MARIADB_HOST} (attempt {retry_count + 1}/{max_retries})")

            conn = mariadb.connect(
                host=MARIADB_HOST,
                user=MARIADB_USER,
                password=MARIADB_PASSWORD,
                database=MARIADB_DATABASE
            )

            # Verify connectivity with a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()

            logger.info(f"Connected to MariaDB at {MARIADB_HOST}")
            return conn

        except Exception as e:
            last_error = e
            retry_count += 1
            logger.error(f"Failed to connect to MariaDB (attempt {retry_count}/{max_retries}): {str(e)}")
            time.sleep(5)  # 5 second delay between retries

    logger.error(f"Failed to connect to MariaDB after {max_retries} attempts. Last error: {str(last_error)}")
    raise HTTPException(
        status_code=500,
        detail="Database connection not available"
    )

# Methods for task chat message storage
def store_chat_message(message: TaskChatMessage) -> bool:
    """Store a chat message in the database.

    Args:
        message: The message to store

    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor()

        # Insert the message into the database
        cursor.execute(
            """
            INSERT INTO task_chat_messages
            (message_id, task_id, content, role, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                message.message_id,
                message.task_id,
                message.content,
                message.role,
                message.timestamp
            )
        )

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except Exception as e:
        logger.error(f"Error storing chat message: {str(e)}")
        return False

def get_chat_messages(task_id: str, limit: int = 50) -> List[TaskChatMessage]:
    """Get chat messages for a task from the database.

    Args:
        task_id: ID of the task to get messages for
        limit: Maximum number of messages to return

    Returns:
        List of chat messages
    """
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor(dictionary=True)

        # Get messages for the task
        cursor.execute(
            """
            SELECT message_id, task_id, content, role, timestamp
            FROM task_chat_messages
            WHERE task_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (task_id, limit)
        )

        # Convert the results to TaskChatMessage objects
        messages = []
        for row in cursor.fetchall():
            messages.append(TaskChatMessage(
                message_id=row['message_id'],
                task_id=row['task_id'],
                content=row['content'],
                role=row['role'],
                timestamp=row['timestamp']
            ))

        cursor.close()
        conn.close()

        return messages

    except Exception as e:
        logger.error(f"Error retrieving chat messages: {str(e)}")
        return []

# Update the get_task_chat_history endpoint to use the database
@task_router.get("/chat/{task_id}", response_model=List[TaskChatMessage])
async def get_task_chat_history(task_id: str, limit: int = 50):
    """Get chat history for a specific task.

    Args:
        task_id: ID of the task to get chat history for
        limit: Maximum number of messages to return (default: 50)

    Returns:
        List of chat messages for the task
    """
    try:
        logger.info(f"Retrieving chat history for task {task_id}")

        # Get messages from the database
        messages = get_chat_messages(task_id, limit)

        # If no messages are found, return an empty list
        if not messages:
            logger.info(f"No messages found for task {task_id}")
            return []

        return messages

    except Exception as e:
        logger.error(f"Error retrieving chat history for task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )

# Update the add_task_chat_message endpoint to store messages in the database
@task_router.post("/chat/{task_id}", response_model=TaskChatMessage)
async def add_task_chat_message(task_id: str, message: TaskChatMessageCreate):
    """Add a new chat message to a task's history.

    Args:
        task_id: ID of the task to add the message to
        message: Message content and role

    Returns:
        The created message with ID and timestamp
    """
    try:
        logger.info(f"Adding chat message to task {task_id}: {message.role}")

        # Create a new message
        new_message = TaskChatMessage(
            message_id=f"{task_id}_{uuid.uuid4()}",
            task_id=task_id,
            content=message.content,
            role=message.role,
            timestamp=datetime.now()
        )

        # Store the message in the database
        if not store_chat_message(new_message):
            raise HTTPException(
                status_code=500,
                detail="Failed to store chat message in database"
            )

        # Broadcast the new message to all connected clients for this task
        await chat_manager.broadcast_to_task(task_id, new_message)

        return new_message

    except Exception as e:
        logger.error(f"Error adding chat message to task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding chat message: {str(e)}"
        )

# Add endpoint to get updates for multiple tasks
@task_router.post("/chat-updates", response_model=TasksChatResponse)
async def get_tasks_chat_updates(request: TasksUpdateRequest):
    """Get chat updates for multiple tasks.

    Args:
        request: Request containing task IDs and optional timestamp

    Returns:
        Updates for each requested task
    """
    try:
        logger.info(f"Getting chat updates for {len(request.task_ids)} tasks")

        # In a real implementation, we would retrieve messages from the database
        # For now, we'll return mock data

        response = TasksChatResponse()

        for task_id in request.task_ids:
            # Create a mock update for each task
            task_update = TaskChatUpdates(task_id=task_id)

            # Add some mock messages
            # In a real implementation, we would filter by the since_timestamp
            task_update.messages = [
                TaskChatMessage(
                    message_id=f"{task_id}_system_1",
                    task_id=task_id,
                    content=f"Processing update for task {task_id}",
                    role="system",
                    timestamp=datetime.now()
                )
            ]

            # Add the task update to the response
            response.tasks.append(task_update)

        return response

    except Exception as e:
        logger.error(f"Error getting chat updates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting chat updates: {str(e)}"
        )

# Add WebSocket endpoint for real-time chat updates
@task_router.websocket("/ws/chat/{task_id}")
async def websocket_chat_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time chat updates.

    This allows the UI to receive updates in real-time when new messages are added to the chat.
    """
    await chat_manager.connect(websocket, task_id)
    try:
        # Send the current chat history when the client connects
        messages = await get_task_chat_history(task_id)
        await websocket.send_json(jsonable_encoder(messages))

        # Listen for new messages from the client
        while True:
            # Receive and validate the message
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                message = TaskChatMessageCreate(**message_data)

                # Add the message to the chat history
                new_message = await add_task_chat_message(task_id, message)

                # The broadcast will be handled by the add_task_chat_message function
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                await websocket.send_json({
                    "error": str(e),
                    "status": "error"
                })

    except WebSocketDisconnect:
        chat_manager.disconnect(websocket, task_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        chat_manager.disconnect(websocket, task_id)

# Models for document parsers
class ParserInfo(BaseModel):
    """Information about a document parser"""
    id: str
    name: str
    description: str
    capabilities: List[str]
    best_for: List[str]

class ParserListResponse(BaseModel):
    """Response with list of available parsers"""
    parsers: List[ParserInfo]
    default_parser: str

# Add new endpoint to get information about available parsers
@task_router.get("/documents/parsers", response_model=ParserListResponse)
async def get_available_parsers():
    """Get information about available document parsers"""
    return ParserListResponse(
        parsers=[
            ParserInfo(
                id=ParserType.UNSTRUCTURED.value,
                name="Unstructured (Local)",
                description="Local self-hosted Unstructured API with comprehensive format support",
                capabilities=["Text extraction", "Table extraction", "Header detection", "OCR", "Layout analysis"],
                best_for=["General purpose documents", "Self-hosted environments", "PDFs", "Word documents"]
            ),
            ParserInfo(
                id=ParserType.UNSTRUCTURED_CLOUD.value,
                name="Unstructured (Cloud)",
                description="Cloud-hosted Unstructured API with higher throughput and enhanced capabilities",
                capabilities=["Text extraction", "Table extraction", "Header detection", "OCR", "Layout analysis", "Formula detection"],
                best_for=["High-volume processing", "Complex documents", "Scientific papers", "Math-heavy content"]
            ),
            ParserInfo(
                id=ParserType.DOCTLY.value,
                name="Doctly",
                description="API for document understanding and extraction with enhanced semantic structure",
                capabilities=["Text extraction", "Semantic structure", "Table extraction", "OCR", "Metadata extraction"],
                best_for=["Complex documents", "Forms", "Receipts", "Contracts", "Legal documents"]
            ),
            ParserInfo(
                id=ParserType.LLAMAPARSE.value,
                name="LlamaParse",
                description="Advanced document parsing from LlamaIndex with hierarchical structure",
                capabilities=["Text extraction", "Hierarchical structure", "Header detection", "Table extraction", "Reference detection"],
                best_for=["Research papers", "Long documents", "Technical documentation", "Hierarchical content"]
            )
        ],
        default_parser=ParserType.UNSTRUCTURED.value
    )

# Models for parser settings
class ParserSettings(BaseModel):
    """Settings for a document parser"""
    api_url: str
    api_key: Optional[str] = None
    extract_tables: bool = True
    extract_metadata: bool = True
    extract_images: bool = False
    chunk_size: int = 2048
    chunk_overlap: int = 200

class ParserConfigResponse(BaseModel):
    """Response with parser configuration settings"""
    unstructured_local: ParserSettings
    unstructured_cloud: ParserSettings
    doctly: ParserSettings
    llamaparse: ParserSettings
    default_parser: str

class UpdateParserSettingsRequest(BaseModel):
    """Request to update parser settings"""
    parser_id: str
    settings: ParserSettings

@task_router.get("/documents/parser-settings", response_model=ParserConfigResponse)
async def get_parser_settings():
    """Get current configuration settings for all document parsers"""
    return ParserConfigResponse(
        unstructured_local=ParserSettings(
            api_url=os.getenv("UNSTRUCTURED_API_URL", "http://unstructured:8000/general/v0/general"),
            api_key=os.getenv("UNSTRUCTURED_API_KEY", ""),
            extract_tables=True,
            extract_metadata=True,
            extract_images=False,
            chunk_size=2048,
            chunk_overlap=200
        ),
        unstructured_cloud=ParserSettings(
            api_url=os.getenv("UNSTRUCTURED_CLOUD_API_URL", "https://api.unstructured.io/general/v0/general"),
            api_key=os.getenv("UNSTRUCTURED_CLOUD_API_KEY", ""),
            extract_tables=True,
            extract_metadata=True,
            extract_images=True,
            chunk_size=2048,
            chunk_overlap=200
        ),
        doctly=ParserSettings(
            api_url=os.getenv("DOCTLY_API_URL", "https://api.doctly.dev/v1/parse"),
            api_key=os.getenv("DOCTLY_API_KEY", ""),
            extract_tables=True,
            extract_metadata=True,
            extract_images=False,
            chunk_size=2048,
            chunk_overlap=200
        ),
        llamaparse=ParserSettings(
            api_url=os.getenv("LLAMAPARSE_API_URL", "https://api.llamaindex.ai/v1/parsing"),
            api_key=os.getenv("LLAMAPARSE_API_KEY", ""),
            extract_tables=True,
            extract_metadata=True,
            extract_images=False,
            chunk_size=2048,
            chunk_overlap=200
        ),
        default_parser=os.getenv("DEFAULT_PARSER_TYPE", ParserType.UNSTRUCTURED.value)
    )

@task_router.post("/documents/parser-settings", response_model=dict)
async def update_parser_settings(request: UpdateParserSettingsRequest):
    """Update settings for a specific parser"""
    # In a real implementation, this would save to a database or config file
    # For now, we'll just return success (changes would be lost on restart)

    # Validate parser ID
    if request.parser_id not in [pt.value for pt in ParserType]:
        raise HTTPException(status_code=400, detail=f"Unknown parser type: {request.parser_id}")

    # We would save settings here
    # For demonstration, we'll just return success
    return {
        "status": "success",
        "message": f"Settings for {request.parser_id} parser updated",
        "parser_id": request.parser_id
    }

@task_router.post("/documents/default-parser", response_model=dict)
async def set_default_parser(parser_id: str):
    """Set the default parser to use for document processing"""
    # Validate parser ID
    if parser_id not in [pt.value for pt in ParserType]:
        raise HTTPException(status_code=400, detail=f"Unknown parser type: {parser_id}")

    # In a real implementation, this would update environment variables or a config file
    # For demonstration, we'll just return success
    return {
        "status": "success",
        "message": f"Default parser set to {parser_id}",
        "default_parser": parser_id
    }

# Export the router and functions
__all__ = [
    "task_router",
    "queue_document_processing",
    "TaskChatMessage",
    "TaskChatMessageCreate",
    "TasksUpdateRequest",
    "TaskChatUpdates",
    "TasksChatResponse",
    "ParserInfo",
    "ParserListResponse",
    "ParserSettings",
    "ParserConfigResponse",
    "UpdateParserSettingsRequest"
]

# Add an alias to match the import in __init__.py
router = task_router
