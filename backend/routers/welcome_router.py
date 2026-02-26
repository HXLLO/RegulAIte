"""
FastAPI router for welcome page and dashboard data.
"""
import logging
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
import os
from datetime import datetime, timedelta
from routers.auth_middleware import get_current_user
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/welcome",
    tags=["welcome"],
    responses={404: {"description": "Not found"}},
)

# Models for API
class WelcomeContent(BaseModel):
    """Content for the welcome page."""
    title: str = Field(..., description="Welcome title")
    subtitle: Optional[str] = Field(None, description="Welcome subtitle")
    intro_text: str = Field(..., description="Introduction text")
    features: List[Dict[str, str]] = Field(..., description="Features to highlight")
    getting_started: List[Dict[str, str]] = Field(..., description="Getting started steps")
    recent_updates: Optional[List[Dict[str, Any]]] = Field(None, description="Recent updates")
    cta_text: Optional[str] = Field(None, description="Call to action text")
    cta_link: Optional[str] = Field(None, description="Call to action link")


class DashboardStats(BaseModel):
    """Statistics for the dashboard."""
    document_count: int = Field(..., description="Total number of documents")
    agent_count: int = Field(..., description="Number of available agents")
    recent_document_count: int = Field(..., description="Number of recently added documents")
    recent_chat_count: int = Field(..., description="Number of recent chat sessions")
    storage_usage_mb: float = Field(..., description="Storage usage in MB")
    task_stats: Dict[str, int] = Field(..., description="Task statistics")


class DashboardActivity(BaseModel):
    """Recent activity for the dashboard."""
    recent_documents: List[Dict[str, Any]] = Field(..., description="Recently added documents")
    recent_chats: List[Dict[str, Any]] = Field(..., description="Recent chat sessions")
    recent_tasks: List[Dict[str, Any]] = Field(..., description="Recent tasks")


class DashboardResponse(BaseModel):
    """Dashboard data response."""
    stats: DashboardStats = Field(..., description="Dashboard statistics")
    activity: DashboardActivity = Field(..., description="Recent activity")
    system_status: Dict[str, Any] = Field(..., description="System status")


class UserDashboardResponse(BaseModel):
    """User dashboard data response."""
    user_id: int
    stats: Dict[str, int] = Field(..., description="User statistics")
    document_types: List[Dict[str, int]] = Field(..., description="Document types")
    recent_uploads: List[Dict[str, Any]] = Field(..., description="Recent uploads")
    recent_chats: List[Dict[str, Any]] = Field(..., description="Recent chats")
    activity: List[Dict[str, Any]] = Field(..., description="Activity")
    timestamp: str


# Helper function to get database connection
async def get_db_connection():
    """Get MariaDB connection from main application."""
    from main import get_mariadb_connection
    return get_mariadb_connection()


# Helper function to get RAG system
async def get_rag_system():
    """Get the RAG system from main application."""
    from main import rag_system
    return rag_system


@router.get("", response_model=WelcomeContent)
async def get_welcome_content():
    """Get welcome page content."""
    try:
        # Get welcome content from database
        conn = await get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT setting_key, setting_value
            FROM regulaite_settings
            WHERE setting_key LIKE 'welcome_%'
            """
        )

        settings = {row['setting_key'][8:]: row['setting_value'] for row in cursor.fetchall()}
        conn.close()

        # Check if we have welcome content stored
        if not settings or 'title' not in settings:
            # Provide default welcome content
            welcome_content = WelcomeContent(
                title="Welcome to RegulAite",
                subtitle="AI-powered Regulatory Compliance Solution",
                intro_text="RegulAite helps you navigate complex regulatory landscapes with AI-driven insights, document analysis, and intelligent agents.",
                features=[
                    {
                        "title": "AI Chat",
                        "description": "Chat with AI that understands your regulatory documents and compliance needs.",
                        "icon": "chat"
                    },
                    {
                        "title": "Document Analysis",
                        "description": "Extract knowledge and insights from your regulatory documents.",
                        "icon": "document"
                    },
                    {
                        "title": "Intelligent Agents",
                        "description": "Specialized AI agents for compliance mapping, gap analysis, and more.",
                        "icon": "agent"
                    },
                    {
                        "title": "Knowledge Graph",
                        "description": "Visualize relationships between regulatory concepts and requirements.",
                        "icon": "graph"
                    }
                ],
                getting_started=[
                    {
                        "step": "1",
                        "title": "Upload Documents",
                        "description": "Start by uploading your regulatory documents to build your knowledge base."
                    },
                    {
                        "step": "2",
                        "title": "Explore Insights",
                        "description": "Use AI chat to ask questions about your regulatory documents."
                    },
                    {
                        "step": "3",
                        "title": "Use Specialized Agents",
                        "description": "Leverage purpose-built agents for specific compliance tasks."
                    }
                ],
                cta_text="Get Started",
                cta_link="/documents"
            )

            # Return default content
            return welcome_content

        # Parse stored welcome content
        try:
            # Parse JSON fields
            features = json.loads(settings.get('features', '[]'))
            getting_started = json.loads(settings.get('getting_started', '[]'))
            recent_updates = json.loads(settings.get('recent_updates', '[]'))

            # Create welcome content from stored settings
            welcome_content = WelcomeContent(
                title=settings.get('title', 'Welcome to RegulAite'),
                subtitle=settings.get('subtitle'),
                intro_text=settings.get('intro_text', 'AI-powered regulatory compliance solution'),
                features=features,
                getting_started=getting_started,
                recent_updates=recent_updates,
                cta_text=settings.get('cta_text'),
                cta_link=settings.get('cta_link')
            )

            return welcome_content

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing welcome content: {str(e)}")
            # Fall back to default content
            welcome_content = WelcomeContent(
                title=settings.get('title', 'Welcome to RegulAite'),
                subtitle=settings.get('subtitle'),
                intro_text=settings.get('intro_text', 'AI-powered regulatory compliance solution'),
                features=[
                    {"title": "AI Chat", "description": "Chat with your documents", "icon": "chat"}
                ],
                getting_started=[
                    {"step": "1", "title": "Upload Documents", "description": "Start by uploading documents"}
                ]
            )

            return welcome_content

    except Exception as e:
        logger.error(f"Error retrieving welcome content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving welcome content: {str(e)}"
        )


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_data():
    """Get dashboard data and statistics."""
    try:
        # Get RAG system for document stats
        rag_system = await get_rag_system()

        # Get MariaDB connection for chat and task stats
        db_conn = await get_db_connection()
        db_cursor = db_conn.cursor(dictionary=True)

        # Get document stats from Qdrant collection metadata
        doc_count = 0
        doc_types = {}
        recent_uploads = []
        
        if rag_system:
            try:
                # Get collection statistics from metadata collection
                scroll_params = {
                    "collection_name": rag_system.metadata_collection_name,
                    "limit": 10  # Limit for recent uploads
                }
                metadata_points = rag_system.qdrant_client.scroll(**scroll_params)[0]
                
                # Count total documents
                doc_count = len(metadata_points)
                
                # Count document types
                for point in metadata_points:
                    payload = point.payload
                    file_type = payload.get("file_type", "unknown")
                    if file_type in doc_types:
                        doc_types[file_type] += 1
                    else:
                        doc_types[file_type] = 1
                
                # Get recent uploads
                recent_uploads = []
                for point in metadata_points:
                    payload = point.payload
                    recent_uploads.append({
                        "doc_id": payload.get("doc_id"),
                        "title": payload.get("title", "Untitled Document"),
                        "file_type": payload.get("file_type", "unknown"),
                        "created": payload.get("created_at", datetime.now().isoformat()),
                        "indexed": payload.get("is_indexed", False),
                        "size": payload.get("size", 0)
                    })
            except Exception as e:
                logger.error(f"Error getting document stats from Qdrant: {str(e)}")

        # Get chat stats from MariaDB
        db_cursor.execute(
            """
            SELECT COUNT(DISTINCT session_id) as session_count, 
                   COUNT(*) as message_count
            FROM chat_history
            """
        )
        chat_stats = db_cursor.fetchone()
        
        # Get task stats from MariaDB
        db_cursor.execute(
            """
            SELECT 
                COUNT(*) as total_tasks,
                SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as completed_tasks,
                SUM(CASE WHEN status = 'FAILURE' THEN 1 ELSE 0 END) as failed_tasks,
                SUM(CASE WHEN status = 'PENDING' OR status = 'STARTED' THEN 1 ELSE 0 END) as active_tasks
            FROM celery_taskresult
            """
        )
        task_stats = db_cursor.fetchone()
        
        db_conn.close()
        
        # Return formatted dashboard data
        return {
            "stats": {
                "document_count": doc_count,
                "chat_session_count": chat_stats.get("session_count", 0) if chat_stats else 0,
                "message_count": chat_stats.get("message_count", 0) if chat_stats else 0,
                "task_count": task_stats.get("total_tasks", 0) if task_stats else 0
            },
            "document_types": [
                {"type": doc_type, "count": count} 
                for doc_type, count in doc_types.items()
            ],
            "recent_uploads": recent_uploads,
            "recent_tasks": [],  # Would need additional query to get this data
            "status": {
                "components": {
                    "database": "connected",
                    "rag_system": "connected" if rag_system else "unavailable",
                    "embedding_service": "operational",
                    "task_queue": "operational"
                },
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting dashboard data: {str(e)}"
        )


@router.get("/user/dashboard", response_model=UserDashboardResponse)
async def get_user_dashboard_data(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get personalized dashboard data for authenticated user."""
    try:
        # Get RAG system for document stats
        rag_system = await get_rag_system()
        
        # Get MariaDB connection for additional stats
        db_conn = await get_db_connection()
        db_cursor = db_conn.cursor(dictionary=True)
        
        # Extract user information
        user_id = current_user["user_id"]
        
        # Get user-specific document stats from Qdrant
        user_doc_count = 0
        user_doc_types = {}
        user_recent_uploads = []
        
        if rag_system:
            try:
                # Get documents that belong to this user
                scroll_params = {
                    "collection_name": rag_system.metadata_collection_name,
                    "limit": 10,  # Limit for recent uploads
                    "filter": Filter(
                        must=[
                            FieldCondition(
                                key="user_id",
                                match=MatchValue(value=user_id)
                            )
                        ]
                    )
                }
                metadata_points = rag_system.qdrant_client.scroll(**scroll_params)[0]
                
                # Count total documents for this user
                user_doc_count = len(metadata_points)
                
                # Count document types for this user
                for point in metadata_points:
                    payload = point.payload
                    file_type = payload.get("file_type", "unknown")
                    if file_type in user_doc_types:
                        user_doc_types[file_type] += 1
                    else:
                        user_doc_types[file_type] = 1
                
                # Get recent uploads for this user
                user_recent_uploads = []
                for point in metadata_points:
                    payload = point.payload
                    user_recent_uploads.append({
                        "doc_id": payload.get("doc_id"),
                        "title": payload.get("title", "Untitled Document"),
                        "file_type": payload.get("file_type", "unknown"),
                        "created": payload.get("created_at", datetime.now().isoformat()),
                        "indexed": payload.get("is_indexed", False),
                        "size": payload.get("size", 0)
                    })
            except Exception as e:
                logger.error(f"Error getting user document stats from Qdrant: {str(e)}")
        
        # Get user chat stats from MariaDB
        db_cursor.execute(
            """
            SELECT COUNT(DISTINCT session_id) as session_count, 
                   COUNT(*) as message_count
            FROM chat_history
            WHERE user_id = %s
            """,
            (user_id,)
        )
        chat_stats = db_cursor.fetchone()
        
        # Get user's recent chat sessions
        db_cursor.execute(
            """
            SELECT 
                session_id, 
                MAX(timestamp) as last_interaction,
                COUNT(*) as message_count
            FROM chat_history
            WHERE user_id = %s
            GROUP BY session_id
            ORDER BY MAX(timestamp) DESC
            LIMIT 5
            """,
            (user_id,)
        )
        recent_chats = db_cursor.fetchall()
        
        # Get user's activity summary
        db_cursor.execute(
            """
            SELECT 
                DATE(timestamp) as date, 
                COUNT(*) as activity_count
            FROM chat_history
            WHERE user_id = %s
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) DESC
            LIMIT 7
            """,
            (user_id,)
        )
        activity_data = db_cursor.fetchall()
        
        db_conn.close()
        
        # Return the personalized dashboard data
        return {
            "user_id": user_id,
            "stats": {
                "document_count": user_doc_count,
                "chat_session_count": chat_stats.get("session_count", 0) if chat_stats else 0,
                "message_count": chat_stats.get("message_count", 0) if chat_stats else 0
            },
            "document_types": [
                {"type": doc_type, "count": count} 
                for doc_type, count in user_doc_types.items()
            ],
            "recent_uploads": user_recent_uploads,
            "recent_chats": recent_chats,
            "activity": [
                {
                    "date": item.get("date").isoformat() if hasattr(item.get("date"), "isoformat") else str(item.get("date")),
                    "count": item.get("activity_count", 0)
                }
                for item in activity_data
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving user dashboard data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user dashboard data: {str(e)}"
        )
