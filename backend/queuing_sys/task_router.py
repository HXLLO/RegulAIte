# plugins/regul_aite/backend/queuing_sys/task_router.py
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging
import os
import uuid
import json
import base64
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime
from celery.result import AsyncResult

# Import Celery tasks
from .celery_worker import (
    app as celery_app,
    process_document,
    execute_agent_task,
    bulk_index_documents,
    retrieve_context
)

# Import parser types enum
from unstructured_parser.base_parser import ParserType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/tasks", tags=["tasks"])

# Models for API
class TaskResponse(BaseModel):
    """Response with task ID"""
    task_id: str
    status: str
    message: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class AgentTaskRequest(BaseModel):
    """Request for agent task execution"""
    agent_type: str
    task: str
    config: Optional[Dict[str, Any]] = None
    include_context: bool = True
    context_query: Optional[str] = None

class BulkIndexRequest(BaseModel):
    """Request for bulk document indexing"""
    doc_ids: List[str]

class ContextRequest(BaseModel):
    """Request for context retrieval"""
    query: str
    top_k: int = 5

class ParserSettingsRequest(BaseModel):
    """Optional parser-specific settings to use for this document"""
    extract_tables: Optional[bool] = None
    extract_metadata: Optional[bool] = None
    extract_images: Optional[bool] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    chunking_strategy: Optional[Literal["fixed", "recursive", "semantic", "hierarchical", "token"]] = None

# Routes
@router.post("/documents/process", response_model=TaskResponse)
async def queue_document_processing(
    file: UploadFile = File(...),
    doc_id: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    use_nlp: bool = Form(True),
    use_enrichment: bool = Form(False),
    detect_language: bool = Form(True),
    language: Optional[str] = Form(None),
    parser_type: Optional[str] = Form(ParserType.UNSTRUCTURED.value),
    parser_settings: Optional[str] = Form(None)
):
    """Queue document for processing"""
    try:
        # Generate document ID if not provided
        if not doc_id:
            doc_id = f"doc_{uuid.uuid4()}"

        # Parse metadata if provided
        doc_metadata = {}
        if metadata:
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse metadata JSON: {metadata}")

        # Parse parser settings if provided
        custom_parser_settings = {}
        if parser_settings:
            try:
                settings_obj = json.loads(parser_settings)
                # Convert to a dictionary with proper validation
                if isinstance(settings_obj, dict):
                    # Only include valid settings
                    valid_keys = [
                        "extract_tables", "extract_metadata", "extract_images",
                        "chunk_size", "chunk_overlap", "chunking_strategy"
                    ]
                    custom_parser_settings = {k: v for k, v in settings_obj.items() if k in valid_keys}

                    # Add to processing metadata
                    doc_metadata["parser_settings"] = custom_parser_settings
                else:
                    logger.warning(f"Parser settings not in expected format: {parser_settings}")
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse parser settings JSON: {parser_settings}")

        # Add file metadata
        doc_metadata["original_filename"] = file.filename
        doc_metadata["content_type"] = file.content_type
        doc_metadata["size"] = 0  # Will be updated with actual size
        doc_metadata["use_nlp"] = use_nlp
        doc_metadata["use_enrichment"] = use_enrichment
        doc_metadata["queued_at"] = datetime.now().isoformat()
        doc_metadata["parser_type"] = parser_type  # Store the parser type used

        # Add language info if provided
        if language:
            doc_metadata["language"] = language
            doc_metadata["language_detect"] = False
        else:
            doc_metadata["language_detect"] = detect_language

        # Read file content
        file_content = await file.read()
        doc_metadata["size"] = len(file_content)

        # Convert file content to base64 for task serialization
        file_content_b64 = base64.b64encode(file_content).decode('utf-8')

        # Validate parser type
        if parser_type not in [pt.value for pt in ParserType]:
            logger.warning(f"Invalid parser type: {parser_type}, using default: {ParserType.UNSTRUCTURED.value}")
            parser_type = ParserType.UNSTRUCTURED.value

        # Create Celery task for document processing
        task = process_document.delay(
            file_content_b64=file_content_b64,
            file_name=file.filename,
            doc_id=doc_id,
            doc_metadata=doc_metadata,
            enrich=use_enrichment,
            detect_language=detect_language,
            parser_type=parser_type,
            parser_settings=custom_parser_settings
        )

        # Return task ID and status
        return TaskResponse(
            task_id=task.id,
            status="pending",
            message=f"Document {doc_id} queued for processing with {parser_type} parser"
        )

    except Exception as e:
        logger.error(f"Error queuing document for processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error queuing document: {str(e)}"
        )

@router.post("/agents/execute", response_model=TaskResponse)
async def queue_agent_task(request: AgentTaskRequest):
    """Queue an agent task for execution"""
    try:
        # Create Celery task for agent execution
        task = execute_agent_task.delay(
            agent_type=request.agent_type,
            task=request.task,
            config=request.config if request.config else None,
            include_context=request.include_context,
            context_query=request.context_query
        )

        # Return task ID and status
        return TaskResponse(
            task_id=task.id,
            status="pending",
            message=f"{request.agent_type.capitalize()} agent task queued for execution"
        )

    except Exception as e:
        logger.error(f"Error queuing agent task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error queuing agent task: {str(e)}"
        )

@router.post("/documents/bulk-index", response_model=TaskResponse)
async def queue_bulk_indexing(request: BulkIndexRequest):
    """Queue multiple documents for indexing"""
    try:
        # Validate input
        if not request.doc_ids:
            raise HTTPException(
                status_code=400,
                detail="No document IDs provided"
            )

        # Create Celery task for bulk indexing
        task = bulk_index_documents.delay(doc_ids=request.doc_ids)

        # Return task ID and status
        return TaskResponse(
            task_id=task.id,
            status="pending",
            message=f"Bulk indexing of {len(request.doc_ids)} documents queued"
        )

    except Exception as e:
        logger.error(f"Error queuing bulk indexing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error queuing bulk indexing: {str(e)}"
        )

@router.post("/context/retrieve", response_model=TaskResponse)
async def queue_context_retrieval(request: ContextRequest):
    """Queue context retrieval from RAG system"""
    try:
        # Create Celery task for context retrieval
        task = retrieve_context.delay(
            query=request.query,
            top_k=request.top_k
        )

        # Return task ID and status
        return TaskResponse(
            task_id=task.id,
            status="pending",
            message=f"Context retrieval for query queued"
        )

    except Exception as e:
        logger.error(f"Error queuing context retrieval: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error queuing context retrieval: {str(e)}"
        )

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a queued task"""
    try:
        # Get task by ID
        task_result = AsyncResult(task_id, app=celery_app)

        # Determine task status
        if task_result.successful():
            result = task_result.result
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "completed_at": datetime.now().isoformat()
            }
        elif task_result.failed():
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(task_result.result),
                "completed_at": datetime.now().isoformat()
            }
        elif task_result.status == 'PENDING':
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "Task is pending execution"
            }
        else:
            return {
                "task_id": task_id,
                "status": task_result.status,
                "message": "Task is being processed"
            }

    except Exception as e:
        logger.error(f"Error retrieving task status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving task status: {str(e)}"
        )

@router.delete("/cancel/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a queued task if possible"""
    try:
        # Get task by ID
        task_result = AsyncResult(task_id, app=celery_app)

        # Try to revoke the task
        if task_result.status in ['PENDING', 'STARTED']:
            celery_app.control.revoke(task_id, terminate=True)
            return {
                "task_id": task_id,
                "status": "revoked",
                "message": "Task has been canceled"
            }
        else:
            return {
                "task_id": task_id,
                "status": task_result.status,
                "message": f"Cannot cancel task in {task_result.status} state"
            }

    except Exception as e:
        logger.error(f"Error canceling task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error canceling task: {str(e)}"
        )

@router.get("/active")
async def get_active_tasks():
    """Get list of currently active tasks"""
    try:
        # Get active tasks from Celery
        i = celery_app.control.inspect()
        active_tasks = i.active()

        # Format the response
        formatted_tasks = []
        if active_tasks:
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    formatted_tasks.append({
                        "task_id": task["id"],
                        "name": task["name"],
                        "worker": worker,
                        "args": task["args"],
                        "kwargs": task["kwargs"],
                        "started_at": task["time_start"]
                    })

        return {
            "count": len(formatted_tasks),
            "tasks": formatted_tasks
        }

    except Exception as e:
        logger.error(f"Error retrieving active tasks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving active tasks: {str(e)}"
        )
