"""
FastAPI router for document management, upload and configuration.
"""
import logging
import json
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
from datetime import datetime
import asyncio

# Import parser types
from unstructured_parser.base_parser import ParserType

# Import Qdrant models for filtering
from qdrant_client.http import models as qdrant_models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

# Helper function to serialize datetime objects
def datetime_serializer(obj):
    """Custom serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Custom JSON Response class
class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        try:
            # Use custom serializer for datetime objects
            return json.dumps(
                content,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
                default=datetime_serializer,
            ).encode("utf-8")
        except Exception as e:
            logger.error(f"Error rendering JSON: {str(e)}")
            return super().render(content)

# Models for API
class DocumentMetadata(BaseModel):
    """Document metadata for API responses."""
    doc_id: str
    title: str
    name: str
    is_indexed: bool
    file_type: str = ""
    description: str = ""
    language: str = "en"
    size: int = 0
    page_count: int = 0
    chunk_count: int = 0
    created_at: Any
    tags: List[str] = []
    category: str = ""
    author: str = ""
    status: str = "active"


class DocumentDetail(DocumentMetadata):
    """Detailed document information."""
    indexed_at: Optional[Any] = None
    # Additional fields can be added here


class DocumentUploadMetadata(BaseModel):
    """Additional metadata for document processing."""
    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    source: Optional[str] = Field(None, description="Document source")
    publish_date: Optional[str] = Field(None, description="Document publication date")
    category: Optional[str] = Field(None, description="Document category")
    tags: Optional[List[str]] = Field(None, description="Document tags")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom metadata fields")


class DocumentProcessResponse(BaseModel):
    """Response for document processing."""
    doc_id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    chunk_count: int = Field(..., description="Number of chunks processed")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Processing message")


class DocumentIndexStatus(BaseModel):
    """Status of document indexing."""
    doc_id: str = Field(..., description="Document ID")
    status: str = Field(..., description="Indexing status")
    vector_count: Optional[int] = Field(None, description="Number of vectors indexed")
    message: str = Field(..., description="Status message")


class DocumentConfigUpdate(BaseModel):
    """Update to document processing configuration."""
    chunk_size: Optional[int] = Field(None, description="Chunk size for document processing")
    chunk_overlap: Optional[int] = Field(None, description="Chunk overlap for document processing")
    default_language: Optional[str] = Field(None, description="Default language for processing")
    auto_detect_language: Optional[bool] = Field(None, description="Whether to auto-detect language")
    use_nlp: Optional[bool] = Field(None, description="Whether to use NLP for entity extraction")
    use_enrichment: Optional[bool] = Field(None, description="Whether to use data enrichment")
    index_immediately: Optional[bool] = Field(None, description="Whether to index documents immediately after processing")
    embedding_model: Optional[str] = Field(None, description="Model to use for embeddings")
    default_embedding_dim: Optional[int] = Field(None, description="Dimension of default embeddings")
    max_file_size_mb: Optional[int] = Field(None, description="Maximum file size in MB")
    allowed_file_types: Optional[List[str]] = Field(None, description="List of allowed file extensions")


class DocumentConfig(DocumentConfigUpdate):
    """Document processing configuration."""
    pass


class DocumentSearchRequest(BaseModel):
    """Request for document search."""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, description="Maximum number of results")
    offset: int = Field(0, description="Offset for pagination")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range filter")
    hybrid_search: Optional[bool] = Field(True, description="Whether to use hybrid search")
    vector_weight: Optional[float] = Field(0.7, description="Weight for vector search")
    semantic_weight: Optional[float] = Field(0.3, description="Weight for semantic search")
    debug: Optional[bool] = Field(False, description="Include debug info in response")


class DocumentStatsResponse(BaseModel):
    """Response with document statistics."""
    total_documents: int = Field(..., description="Total number of documents")
    total_chunks: int = Field(..., description="Total number of chunks")
    documents_by_type: Dict[str, int] = Field(..., description="Document count by type")
    documents_by_language: Dict[str, int] = Field(..., description="Document count by language")
    recent_uploads: List[Dict[str, Any]] = Field(..., description="Recent document uploads")
    total_storage_mb: float = Field(..., description="Total storage used in MB")


class DocumentListResponse(BaseModel):
    """Response for paginated document list."""
    documents: List[DocumentMetadata] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total number of documents")
    limit: int = Field(..., description="Number of documents per page")
    offset: int = Field(..., description="Current offset")


# Dependency to get document parser
async def get_document_parser():
    """Get the document parser from main application."""
    from main import document_parser
    return document_parser


# Dependency to get RAG system
async def get_rag_system():
    """Get the RAG system from main application."""
    from main import rag_system
    return rag_system


# Dependency to get task router for queue
async def get_task_router():
    """Get the task router from main application."""
    from routers.task_router import queue_document_processing
    return queue_document_processing


@router.post("", response_class=CustomJSONResponse)
async def process_document(
    file: UploadFile = File(...),
    doc_id: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    use_nlp: bool = Form(True),
    use_enrichment: bool = Form(False),
    detect_language: bool = Form(True),
    language: Optional[str] = Form(None),
    parser_type: str = Form(ParserType.UNSTRUCTURED.value),
    document_parser = Depends(get_document_parser)
):
    """Process a document using the specified parser and store it in the system."""
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
                
        # Read the file
        file_content = await file.read()
        
        # Extract file extension and determine file type
        filename = file.filename
        extension = None
        if "." in filename:
            extension = filename.split(".")[-1].lower()
            
        # Map common extensions to standardized file types
        file_type = "unknown"
        if extension:
            extension_to_type = {
                # Documents
                "pdf": "pdf",
                "doc": "doc",
                "docx": "docx",
                "txt": "txt",
                "md": "md",
                "markdown": "md",
                "rtf": "rtf",
                "odt": "odt",
                # Spreadsheets
                "xls": "xls",
                "xlsx": "xlsx",
                "csv": "csv",
                "ods": "ods",
                # Presentations
                "ppt": "ppt",
                "pptx": "pptx",
                "odp": "odp",
                # Web
                "html": "html",
                "htm": "html",
                "xml": "xml",
                "json": "json",
                # Images
                "jpg": "jpg",
                "jpeg": "jpg",
                "png": "png",
                "gif": "gif",
                "bmp": "bmp",
                "svg": "svg",
                # Archives
                "zip": "zip",
                "rar": "rar",
                "tar": "tar",
                "gz": "gz",
                "7z": "7z"
            }
            file_type = extension_to_type.get(extension, extension)
        
        # Fall back to content type if extension extraction failed
        if file_type == "unknown" and file.content_type:
            content_type = file.content_type.lower()
            if "pdf" in content_type:
                file_type = "pdf"
            elif "word" in content_type or "docx" in content_type:
                file_type = "docx"
            elif "excel" in content_type or "xlsx" in content_type:
                file_type = "xlsx"
            elif "powerpoint" in content_type or "pptx" in content_type:
                file_type = "pptx"
            elif "text/plain" in content_type:
                file_type = "txt"
            elif "text/markdown" in content_type:
                file_type = "md"
            elif "html" in content_type:
                file_type = "html"
        
        logger.info(f"Detected file type: {file_type} for {filename}")
        
        # Add file metadata
        doc_metadata["original_filename"] = file.filename
        doc_metadata["name"] = file.filename  # Set name field to the original filename for display
        doc_metadata["content_type"] = file.content_type
        doc_metadata["file_type"] = file_type  # Set the detected file type
        doc_metadata["size"] = len(file_content)  # Store actual byte size of the file content
        doc_metadata["use_nlp"] = use_nlp
        doc_metadata["use_enrichment"] = use_enrichment
        
        # Process the document
        result = document_parser.process_document(
            file_content=file_content,
            file_name=file.filename,
            doc_id=doc_id,
            doc_metadata=doc_metadata,
            detect_language=detect_language
        )
        
        return result
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/", response_model=DocumentListResponse)
@router.get("", response_model=DocumentListResponse)  # Also handle URL without trailing slash
async def document_list(
    skip: int = Query(0, alias="offset"),
    limit: int = Query(100, alias="limit"),
    sort_by: str = Query("created_at", alias="sort_by"),
    sort_order: str = Query("desc", alias="sort_order"),
    filter_tags: Optional[List[str]] = Query(None, alias="tags"),
    filter_status: Optional[List[str]] = Query(None, alias="status"),
    search_query: Optional[str] = Query(None, alias="search"),
    file_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    language: Optional[str] = Query(None)
):
    """
    Get a list of documents with optional filtering and search.
    """
    # Validate sort parameters
    valid_sort_fields = ["created_at", "title", "file_type", "size", "language"]
    valid_sort_orders = ["asc", "desc"]

    if sort_by not in valid_sort_fields:
        # Map 'created' from frontend to 'created_at' in backend
        if sort_by == "created":
            sort_by = "created_at"
        else:
            sort_by = "created_at"

    if sort_order not in valid_sort_orders:
        sort_order = "desc"

    documents = []
    total_count = 0
    unique_doc_ids = set()  # Track unique doc_ids to avoid duplicates
    try:
        # Get RAG system for Qdrant access
        rag_system = await get_rag_system()
        
        if not rag_system:
            logger.warning("RAG system not available for document listing")
            return DocumentListResponse(
                documents=[],
                total_count=0,
                limit=limit,
                offset=skip
            )
        
        # Build filter criteria
        filter_conditions = []
        
        # Add tag filter if provided
        if filter_tags and len(filter_tags) > 0:
            from qdrant_client.models import FieldCondition, MatchAny
            tag_filter = FieldCondition(
                key="tags",
                match=MatchAny(any=filter_tags)
            )
            filter_conditions.append(tag_filter)
            
        # Add status filter if provided
        if filter_status and len(filter_status) > 0:
            from qdrant_client.models import FieldCondition, MatchAny
            status_filter = FieldCondition(
                key="status",
                match=MatchAny(any=filter_status)
            )
            filter_conditions.append(status_filter)
            
        # Add file_type filter if provided
        if file_type:
            from qdrant_client.models import FieldCondition, MatchValue
            file_type_filter = FieldCondition(
                key="file_type",
                match=MatchValue(value=file_type)
            )
            filter_conditions.append(file_type_filter)
            
        # Add category filter if provided
        if category:
            from qdrant_client.models import FieldCondition, MatchValue
            category_filter = FieldCondition(
                key="category",
                match=MatchValue(value=category)
            )
            filter_conditions.append(category_filter)
            
        # Add language filter if provided
        if language:
            from qdrant_client.models import FieldCondition, MatchValue
            language_filter = FieldCondition(
                key="language",
                match=MatchValue(value=language)
            )
            filter_conditions.append(language_filter)
            
        # Create filter object if we have conditions
        query_filter = None
        if filter_conditions:
            from qdrant_client.models import Filter
            query_filter = Filter(
                must=filter_conditions
            )

        # Get documents from Qdrant metadata collection
        try:
            # Get all points from metadata collection to calculate total count
            scroll_params = {
                "collection_name": rag_system.metadata_collection_name,
                "limit": 1000,  # Large limit to get all documents for count
                "with_payload": True,
                "with_vectors": False,
            }
            
            # Only add filter if we have conditions
            if query_filter:
                scroll_params["filter"] = query_filter
                
            scroll_result = rag_system.qdrant_client.scroll(**scroll_params)
            
            metadata_points = scroll_result[0] if scroll_result and len(scroll_result) > 0 else []
            
            # Filter by search query if provided
            if search_query:
                filtered_points = []
                search_query = search_query.lower()
                for point in metadata_points:
                    payload = point.payload
                    if not payload:
                        continue
                    
                    # Search in title, description, and other fields
                    title = payload.get("title", "").lower()
                    description = payload.get("description", "").lower()
                    file_name = payload.get("name", "").lower()
                    original_filename = payload.get("original_filename", "").lower()
                    
                    if (search_query in title or 
                        search_query in description or 
                        search_query in file_name or
                        search_query in original_filename):
                        filtered_points.append(point)
                
                metadata_points = filtered_points
            
            # Sort the points
            def get_sort_key(point):
                payload = point.payload if point.payload else {}
                if sort_by == "created_at":
                    return payload.get("created_at", "")
                elif sort_by == "title":
                    return payload.get("title", "").lower()
                elif sort_by == "file_type":
                    return payload.get("file_type", "").lower()
                elif sort_by == "size":
                    return payload.get("size", 0)
                elif sort_by == "language":
                    return payload.get("language", "").lower()
                return ""
            
            metadata_points.sort(
                key=get_sort_key,
                reverse=(sort_order == "desc")
            )
            
            # Calculate total count of unique documents
            all_unique_doc_ids = set()
            for point in metadata_points:
                payload = point.payload
                if payload:
                    doc_id = payload.get("doc_id", "")
                    if doc_id:
                        all_unique_doc_ids.add(doc_id)
            
            total_count = len(all_unique_doc_ids)
            
            # Apply pagination and track unique documents for current page
            documents = []
            count = 0
            processed = 0
            
            for point in metadata_points:
                payload = point.payload
                if not payload:
                    continue
                    
                doc_id = payload.get("doc_id", "")
                
                # Skip if we already have this document
                if doc_id in unique_doc_ids:
                    continue
                    
                unique_doc_ids.add(doc_id)
                
                # Skip documents before the offset
                if processed < skip:
                    processed += 1
                    continue
                
                # Stop if we've reached the limit
                if count >= limit:
                    break
                    
                count += 1
                
                # Extract document metadata
                doc = DocumentMetadata(
                    doc_id=doc_id,
                    title=payload.get("title", "Untitled"),
                    name=payload.get("name", payload.get("original_filename", "Document " + doc_id[:8])),
                    is_indexed=payload.get("is_indexed", False),
                    file_type=payload.get("file_type", ""),
                    description=payload.get("description", ""),
                    language=payload.get("language", "en"),
                    size=payload.get("size", 0),
                    page_count=payload.get("page_count", 0),
                    chunk_count=payload.get("chunk_count", 0),
                    created_at=payload.get("created_at", datetime.now().isoformat()),
                    tags=payload.get("tags", []),
                    category=payload.get("category", ""),
                    author=payload.get("author", ""),
                    status=payload.get("status", "active")
                )
                documents.append(doc)
                
        except Exception as e:
            logger.error(f"Error fetching documents from Qdrant: {str(e)}")

    except Exception as e:
        logger.error(f"Error fetching document list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return DocumentListResponse(
        documents=documents,
        total_count=total_count,
        limit=limit,
        offset=skip
    )


@router.get("/parsers", response_model=Dict[str, List[Dict[str, str]]])
async def get_parser_types():
    """Get available parser types for document processing."""
    parser_types = []
    
    for parser in ParserType:
        parser_info = {
            "id": parser.value,
            "name": parser.name.replace("_", " ").title(),
            "description": get_parser_description(parser)
        }
        parser_types.append(parser_info)
    
    return {"parsers": parser_types}

def get_parser_description(parser_type: ParserType) -> str:
    """Get the description for a parser type."""
    descriptions = {
        ParserType.UNSTRUCTURED: "Default document parser that extracts text and structure from various document formats",
        ParserType.UNSTRUCTURED_CLOUD: "Cloud-based version of Unstructured with enhanced capabilities",
        ParserType.DOCTLY: "Specialized parser for legal and regulatory documents with enhanced metadata extraction",
        ParserType.LLAMAPARSE: "AI-powered document parser based on LlamaIndex with advanced semantic understanding"
    }
    return descriptions.get(parser_type, "Document parser")

@router.get("/config", response_model=DocumentConfig)
async def get_document_config():
    """Get document processing configuration."""
    try:
        # Get document parser to access its configuration
        doc_parser = await get_document_parser()

        # Get configuration from database
        from main import get_mariadb_connection

        conn = get_mariadb_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT setting_key, setting_value
            FROM regulaite_settings
            WHERE setting_key LIKE 'doc_%'
            """
        )

        settings = {row['setting_key'][4:]: row['setting_value'] for row in cursor.fetchall()}
        conn.close()

        # Convert types as needed
        result = DocumentConfig(
            chunk_size=int(settings.get('chunk_size', 2048)),
            chunk_overlap=int(settings.get('chunk_overlap', 200)),
            default_language=settings.get('default_language', 'fr'),
            auto_detect_language=settings.get('auto_detect_language', 'true').lower() == 'true',
            use_nlp=settings.get('use_nlp', 'true').lower() == 'true',
            use_enrichment=settings.get('use_enrichment', 'true').lower() == 'true',
            index_immediately=settings.get('index_immediately', 'true').lower() == 'true',
            embedding_model=settings.get('embedding_model', 'text-embedding-ada-002'),
            default_embedding_dim=int(settings.get('default_embedding_dim', 1536)),
            max_file_size_mb=int(settings.get('max_file_size_mb', 10)),
            allowed_file_types=settings.get('allowed_file_types', 'pdf,docx,txt,md,html').split(',')
        )

        return result

    except Exception as e:
        logger.error(f"Error retrieving document configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving document configuration: {str(e)}"
        )


@router.post("/config", response_model=DocumentConfig)
async def update_document_config(config: DocumentConfigUpdate):
    """Update document processing configuration."""
    try:
        # Get document parser
        doc_parser = await get_document_parser()

        # Get database connection
        from main import get_mariadb_connection

        conn = get_mariadb_connection()
        cursor = conn.cursor()

        # Update each provided setting
        if config.dict(exclude_none=True):
            for key, value in config.dict(exclude_none=True).items():
                # Convert lists to comma-separated strings
                if isinstance(value, list):
                    value = ','.join(value)

                # Convert booleans to strings
                if isinstance(value, bool):
                    value = str(value).lower()

                # Update or insert the setting
                cursor.execute(
                    """
                    INSERT INTO regulaite_settings (setting_key, setting_value)
                    VALUES (?, ?)
                    ON DUPLICATE KEY UPDATE setting_value = ?
                    """,
                    (f"doc_{key}", str(value), str(value))
                )

        conn.commit()
        conn.close()

        # Return the updated configuration
        return await get_document_config()

    except Exception as e:
        logger.error(f"Error updating document configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating document configuration: {str(e)}"
        )


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, delete_from_index: bool = True):
    """Delete document and its chunks from Neo4j and optionally from vector store."""
    try:
        # Get dependencies
        rag_system = await get_rag_system()
        chunks_deleted = 0
        index_message = ""

        # First try to delete from vector index if requested
        if delete_from_index:
            try:
                # Use RAG system to delete from index
                logger.info(f"Deleting document {doc_id} from vector index")
                rag_deleted = rag_system.delete_document(doc_id)
                
                if rag_deleted:
                    # Get approximate count of chunks that were deleted
                    # The actual chunk count is already deleted, so we can't query it directly
                    # For UI purposes, we'll return a success message
                    chunks_deleted = 1  # At minimum, one document was deleted
                    index_message = ", and deleted from vector index"
                else:
                    logger.warning(f"Document {doc_id} may not exist in vector index or encountered errors during deletion")
                    index_message = ", but document may not exist in vector index"
            except Exception as e:
                # Log error but continue
                logger.error(f"Error deleting document from vector index: {str(e)}")
                index_message = f", but failed to delete from vector index: {str(e)}"
                
        # If we get here, document deletion was successful
        return {
            "doc_id": doc_id,
            "deleted": True,
            "chunks_deleted": chunks_deleted,
            "message": f"Document and metadata deleted from database{index_message}"
        }

    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )


@router.post("/index/{doc_id}", response_model=DocumentIndexStatus)
async def index_document(doc_id: str, force_reindex: bool = False):
    """Index a document in the vector store."""
    try:
                
        # Get RAG system and index document
        rag_system = await get_rag_system()
        index_result = rag_system.index_document(doc_id)
        
        # Check the result format
        if isinstance(index_result, dict):
            # Check if it already contains a "status" key
            if "status" in index_result:
                status = index_result["status"]
                vector_count = index_result.get("vector_count", 0)
                message = index_result.get("message", "")
            # Check if it has positive vector count
            elif "vector_count" in index_result and index_result["vector_count"] > 0:
                status = "success"
                vector_count = index_result["vector_count"]
                message = index_result.get("message", "Document indexed successfully")
            # Check if it's already indexed
            elif index_result.get("message") == "Document already indexed":
                status = "success"
                vector_count = 0
                message = "Document already indexed"
            # Otherwise consider it failed
            else:
                status = "error"
                vector_count = 0
                message = index_result.get("message", "Failed to index document")
        elif index_result:
            # Boolean True result
            status = "success"
            vector_count = None
            message = "Document successfully indexed"
        else:
            # Failed indexing
            status = "error"
            vector_count = 0
            message = "Failed to index document"
        
        return {
            "doc_id": doc_id,
            "status": status,
            "vector_count": vector_count,
            "message": message
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error indexing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error indexing document: {str(e)}"
        )


@router.post("/search", response_model=Dict[str, Any])
async def search_documents(request: DocumentSearchRequest):
    """Search for documents using semantic search."""
    try:
        # Get RAG system
        rag_system = await get_rag_system()

        # Prepare filters
        filters = request.filters or {}
        
        # Add date range to filters if provided
        if request.date_range:
            filters["date_range"] = request.date_range

        # Use RAG system to search
        try:
            results = rag_system.retrieve(
                query=request.query,
                top_k=request.limit,
                filters=filters
            )
        except Exception as retrieval_error:
            logger.error(f"Error during document retrieval: {str(retrieval_error)}")
            # Return empty results instead of failing completely
            results = []

        # Count unique documents
        unique_docs = set()
        for result in results:
            doc_id = result.get("metadata", {}).get("document_id")
            if doc_id:
                unique_docs.add(doc_id)

        return {
            "results": results,
            "query": request.query,
            "count": len(results),
            "unique_documents": len(unique_docs)
        }
    except Exception as e:
        logger.error(f"Error in document search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching documents: {str(e)}"
        )


@router.get("/stats", response_model=DocumentStatsResponse)
async def get_document_stats():
    """Get document statistics."""
    try:
        # Initialize counters
        total_documents = 0
        total_chunks = 0
        total_storage_bytes = 0
        documents_by_type = {}
        documents_by_language = {}
        recent_uploads = []
        
        # Get documents from Qdrant metadata collection
        rag_system = await get_rag_system()
        if rag_system:
            try:
                # Get document metadata
                scroll_result = rag_system.qdrant_client.scroll(
                    collection_name=rag_system.metadata_collection_name,
                    limit=100,  # Limit to 100 documents for stats
                    with_payload=True,
                    with_vectors=False,
                )
                
                metadata_points = scroll_result[0] if scroll_result and len(scroll_result) > 0 else []
                
                # Collect stats from document metadata
                for point in metadata_points:
                    if not point.payload:
                        continue
                    
                    total_documents += 1
                    
                    # Increment chunk count
                    chunk_count = point.payload.get("chunk_count", 0)
                    total_chunks += chunk_count
                    
                    # Track document size
                    size = point.payload.get("size", 0)
                    if size:
                        total_storage_bytes += size
                    else:
                        # Log issue for debugging
                        logger.warning(f"Document {point.payload.get('doc_id', 'unknown')} has no size")
                    
                    # Track document types
                    file_type = point.payload.get("file_type", "unknown")
                    if file_type in documents_by_type:
                        documents_by_type[file_type] += 1
                    else:
                        documents_by_type[file_type] = 1
                    
                    # Track document languages
                    language = point.payload.get("language", "unknown")
                    if language in documents_by_language:
                        documents_by_language[language] += 1
                    else:
                        documents_by_language[language] = 1
                    
                    # Add to recent uploads (limited to 5)
                    if len(recent_uploads) < 5:
                        recent_uploads.append({
                            "doc_id": point.payload.get("doc_id", ""),
                            "title": point.payload.get("title", ""),
                            "file_type": file_type,
                            "created": point.payload.get("created_at", ""),
                            "indexed": point.payload.get("is_indexed", False),
                            "size": size
                        })
                
                # Convert total storage to MB
                total_storage_mb = total_storage_bytes / (1024 * 1024)
            except Exception as e:
                logger.error(f"Error fetching document stats from Qdrant: {str(e)}")
                
        return {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "documents_by_type": documents_by_type,
            "documents_by_language": documents_by_language,
            "recent_uploads": recent_uploads,
            "total_storage_mb": round(total_storage_mb, 2) if 'total_storage_mb' in locals() else 0.0
        }
    except Exception as e:
        logger.error(f"Error generating document statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate document statistics")


@router.post("/repair-metadata", response_model=Dict[str, Any])
async def repair_document_metadata(doc_id: Optional[str] = Query(None, description="Optional document ID to repair")):
    """
    Repair document metadata by creating default metadata for documents with missing metadata.
    If doc_id is provided, repairs only that document, otherwise repairs all documents.
    """
    try:
        # Get RAG system
        rag_system = await get_rag_system()
        
        if not rag_system:
            raise HTTPException(status_code=500, detail="RAG system not available")
        
        # Call the repair function
        result = rag_system.repair_document_metadata(doc_id)
        return result
    except Exception as e:
        logger.error(f"Error repairing document metadata: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error repairing document metadata: {str(e)}"
        )

@router.post("/repair-sizes", response_model=Dict[str, Any])
async def repair_document_sizes():
    """
    Repair document sizes by calculating them from document chunks.
    """
    try:
        # Get RAG system and document metadata
        rag_system = await get_rag_system()
        if not rag_system:
            raise HTTPException(status_code=500, detail="RAG system not available")
        
        # Get all documents
        search_result = rag_system.qdrant_client.scroll(
            collection_name=rag_system.metadata_collection_name,
            limit=100,
            with_payload=True
        )
        
        metadata_points = search_result[0] if search_result and len(search_result) > 0 else []
        
        updated_count = 0
        failed_count = 0
        
        # Process each document
        for point in metadata_points:
            if not point.payload or "doc_id" not in point.payload:
                continue
                
            doc_id = point.payload["doc_id"]
            
            try:
                # Get document chunks
                chunks = rag_system.qdrant_client.search(
                    collection_name=rag_system.collection_name,
                    query_vector=[0.0] * rag_system.embedding_dim,
                    query_filter=qdrant_models.Filter(
                        must=[
                            qdrant_models.FieldCondition(
                                key="doc_id",
                                match=qdrant_models.MatchValue(value=doc_id)
                            )
                        ]
                    ),
                    limit=1000,
                    with_vectors=False
                )
                
                # Calculate size from chunks
                total_size_bytes = 0
                
                for chunk in chunks:
                    if not chunk.payload:
                        continue
                        
                    # Try to get text from payload
                    if "text" in chunk.payload and isinstance(chunk.payload["text"], str):
                        total_size_bytes += len(chunk.payload["text"].encode('utf-8'))
                        
                    # Try to extract from _node_content
                    elif "_node_content" in chunk.payload and isinstance(chunk.payload["_node_content"], str):
                        try:
                            node_content = json.loads(chunk.payload["_node_content"])
                            if "text" in node_content and isinstance(node_content["text"], str):
                                total_size_bytes += len(node_content["text"].encode('utf-8'))
                        except (json.JSONDecodeError, TypeError):
                            pass
                
                # Update metadata with correct size
                if total_size_bytes > 0:
                    # Get point ID for metadata document
                    metadata_point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))
                    
                    # Update existing metadata
                    metadata = point.payload.copy()
                    metadata["size"] = total_size_bytes
                    
                    # Upsert updated metadata
                    rag_system.qdrant_client.upsert(
                        collection_name=rag_system.metadata_collection_name,
                        points=[
                            qdrant_models.PointStruct(
                                id=metadata_point_id,
                                vector=[1.0],  # Dummy vector for metadata
                                payload=metadata
                            )
                        ]
                    )
                    
                    logger.info(f"Updated size for document {doc_id} to {total_size_bytes} bytes ({total_size_bytes/1024:.2f} KB)")
                    updated_count += 1
                else:
                    logger.warning(f"Could not find text content for document {doc_id}")
                    failed_count += 1
            
            except Exception as e:
                logger.error(f"Error updating size for document {doc_id}: {str(e)}")
                failed_count += 1
        
        return {
            "status": "success",
            "updated": updated_count,
            "failed": failed_count,
            "message": f"Updated sizes for {updated_count} documents, {failed_count} failed"
        }
        
    except Exception as e:
        logger.error(f"Error repairing document sizes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error repairing document sizes: {str(e)}"
        )

@router.post("/repair-file-types", response_model=Dict[str, Any])
async def repair_document_file_types():
    """
    Repair document file types by extracting them from filenames.
    """
    try:
        # Get RAG system and document metadata
        rag_system = await get_rag_system()
        if not rag_system:
            raise HTTPException(status_code=500, detail="RAG system not available")
        
        # Get all documents
        search_result = rag_system.qdrant_client.scroll(
            collection_name=rag_system.metadata_collection_name,
            limit=100,
            with_payload=True
        )
        
        metadata_points = search_result[0] if search_result and len(search_result) > 0 else []
        
        updated_count = 0
        failed_count = 0
        
        # Map common extensions to standardized file types
        extension_to_type = {
            # Documents
            "pdf": "pdf",
            "doc": "doc",
            "docx": "docx",
            "txt": "txt",
            "md": "md",
            "markdown": "md",
            "rtf": "rtf",
            "odt": "odt",
            # Spreadsheets
            "xls": "xls",
            "xlsx": "xlsx",
            "csv": "csv",
            "ods": "ods",
            # Presentations
            "ppt": "ppt",
            "pptx": "pptx",
            "odp": "odp",
            # Web
            "html": "html",
            "htm": "html",
            "xml": "xml",
            "json": "json",
            # Images
            "jpg": "jpg",
            "jpeg": "jpg",
            "png": "png",
            "gif": "gif",
            "bmp": "bmp",
            "svg": "svg"
        }
        
        # Process each document
        for point in metadata_points:
            if not point.payload or "doc_id" not in point.payload:
                continue
                
            doc_id = point.payload["doc_id"]
            
            try:
                # Get the filename
                original_filename = point.payload.get("original_filename") or point.payload.get("name")
                current_file_type = point.payload.get("file_type")
                
                # Skip if already has a valid file type
                if current_file_type and current_file_type != "unknown":
                    continue
                    
                # Extract file type from filename
                file_type = "unknown"
                if original_filename and "." in original_filename:
                    extension = original_filename.split(".")[-1].lower()
                    file_type = extension_to_type.get(extension, extension)
                    
                # Update only if we found a valid file type
                if file_type != "unknown":
                    # Get point ID for metadata document
                    metadata_point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))
                    
                    # Update existing metadata
                    metadata = point.payload.copy()
                    metadata["file_type"] = file_type
                    
                    # Upsert updated metadata
                    rag_system.qdrant_client.upsert(
                        collection_name=rag_system.metadata_collection_name,
                        points=[
                            qdrant_models.PointStruct(
                                id=metadata_point_id,
                                vector=[1.0],  # Dummy vector for metadata
                                payload=metadata
                            )
                        ]
                    )
                    
                    logger.info(f"Updated file type for document {doc_id} to {file_type}")
                    updated_count += 1
                else:
                    logger.warning(f"Could not determine file type for document {doc_id}")
                    failed_count += 1
            
            except Exception as e:
                logger.error(f"Error updating file type for document {doc_id}: {str(e)}")
                failed_count += 1
        
        return {
            "status": "success",
            "updated": updated_count,
            "failed": failed_count,
            "message": f"Updated file types for {updated_count} documents, {failed_count} failed"
        }
        
    except Exception as e:
        logger.error(f"Error repairing document file types: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error repairing document file types: {str(e)}"
        )

@router.post("/reprocess/{doc_id}", response_model=Dict[str, Any])
async def reprocess_document(doc_id: str):
    """
    Force reprocessing of a document that has parsing or indexing issues.
    
    Args:
        doc_id: Document ID to reprocess
        
    Returns:
        Dict with operation status
    """
    logger.info(f"Received request to reprocess document: {doc_id}")
    
    # Get RAG system
    rag_system = await get_rag_system()
    
    if not rag_system:
        raise HTTPException(
            status_code=500,
            detail="RAG system is not initialized"
        )
    
    # Force reprocessing of the document
    result = rag_system.force_reprocess_document(doc_id)
    
    if result.get("status") == "error":
        raise HTTPException(
            status_code=500,
            detail=result.get("message", "Unknown error reprocessing document")
        )
    
    logger.info(f"Document {doc_id} marked for reprocessing: {result}")
    
    # Now trigger actual reprocessing using the document parser
    try:
        # Get the document parser
        doc_parser = await get_document_parser()
        
        # Initiate reprocessing
        reprocess_result = await doc_parser.reprocess_document(doc_id)
        
        return {
            "status": "success",
            "message": f"Document {doc_id} reprocessing initiated",
            "doc_id": doc_id,
            "reprocess_result": reprocess_result
        }
    except Exception as e:
        logger.error(f"Error initiating document reprocessing: {str(e)}")
        return {
            "status": "partial_success",
            "message": f"Document {doc_id} marked for reprocessing but reprocessing failed: {str(e)}",
            "doc_id": doc_id,
            "result": result
        }


