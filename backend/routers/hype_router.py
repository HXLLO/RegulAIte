import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks, Body

# Local imports
from rag.hype_rag import HyPERagSystem
from routers.auth_middleware import get_current_user

# Get environment variables
QDRANT_URL = os.environ.get("QDRANT_URL", "http://regulaite-qdrant:6333")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Instantiate router
router = APIRouter(prefix="/hype", tags=["hype"])

# Setup logging
logger = logging.getLogger(__name__)

# Global HyPE RAG system instance
hype_rag_system = None

# Pydantic models for responses
from pydantic import BaseModel, Field

class HyPERetrievalRequest(BaseModel):
    query: str
    top_k: int = Field(3, ge=1, le=10)
    collection_name: Optional[str] = None

class HyPERetrievalResult(BaseModel):
    text: str
    metadata: Dict[str, Any]
    score: float

class HyPERetrievalResponse(BaseModel):
    results: List[HyPERetrievalResult]
    query: str
    time_taken: float
    count: int

class HyPEIndexingRequest(BaseModel):
    doc_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    collection_name: Optional[str] = None

class HyPEIndexingResponse(BaseModel):
    status: str
    doc_id: str
    chunk_count: int
    indexed_count: int
    processing_time: float
    error: Optional[str] = None

# Helper function to get HyPE RAG system
def get_hype_rag_system(collection_name: Optional[str] = "regulaite_hype") -> HyPERagSystem:
    """Get or initialize HyPE RAG system"""
    global hype_rag_system
    
    if hype_rag_system is None or (collection_name and hype_rag_system.collection_name != collection_name):
        logger.info(f"Initializing HyPE RAG system with collection: {collection_name}")
        try:
            hype_rag_system = HyPERagSystem(
                collection_name=collection_name,
                qdrant_url=QDRANT_URL,
                embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                openai_api_key=OPENAI_API_KEY,
                llm_model="gpt-4.1"
            )
            logger.info("HyPE RAG system initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing HyPE RAG system: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize HyPE RAG system: {str(e)}"
            )
    
    return hype_rag_system

# Routes
@router.post("/retrieve", response_model=HyPERetrievalResponse)
async def retrieve_documents(
    request: HyPERetrievalRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Retrieve documents using HyPE RAG"""
    try:
        # Get RAG system
        rag = get_hype_rag_system(request.collection_name)
        
        # Perform retrieval
        import time
        start_time = time.time()
        results = rag.retrieve(request.query, top_k=request.top_k)
        time_taken = time.time() - start_time
        
        # Format results for response
        formatted_results = [
            HyPERetrievalResult(
                text=doc.get("text", ""),
                metadata=doc.get("metadata", {}),
                score=doc.get("score", 0.0)
            )
            for doc in results
        ]
        
        return HyPERetrievalResponse(
            results=formatted_results,
            query=request.query,
            time_taken=time_taken,
            count=len(results)
        )
    
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve documents: {str(e)}"
        )

@router.post("/index", response_model=HyPEIndexingResponse)
async def index_document(
    request: HyPEIndexingRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Index a document using HyPE RAG"""
    try:
        # Get RAG system
        rag = get_hype_rag_system(request.collection_name)
        
        # Process document in background
        def process_document():
            try:
                result = rag.process_and_index_document(
                    doc_id=request.doc_id,
                    content=request.content,
                    metadata=request.metadata
                )
                logger.info(f"Document {request.doc_id} indexed successfully: {result}")
            except Exception as e:
                logger.error(f"Error indexing document {request.doc_id}: {str(e)}")
        
        # Add task to background tasks
        background_tasks.add_task(process_document)
        
        return HyPEIndexingResponse(
            status="processing",
            doc_id=request.doc_id,
            chunk_count=0,
            indexed_count=0,
            processing_time=0.0
        )
    
    except Exception as e:
        logger.error(f"Error indexing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to index document: {str(e)}"
        )

@router.post("/upload", response_model=HyPEIndexingResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection_name: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: Dict = Depends(get_current_user)
):
    """Upload and index a document using HyPE RAG"""
    try:
        # Read file content
        content = await file.read()
        content_text = content.decode("utf-8", errors="replace")
        
        # Generate doc_id from filename
        doc_id = file.filename.split(".")[0].replace(" ", "_").lower()
        
        # Prepare metadata
        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "doc_name": file.filename
        }
        
        # Get RAG system
        rag = get_hype_rag_system(collection_name)
        
        # Process document in background
        def process_document():
            try:
                result = rag.process_and_index_document(
                    doc_id=doc_id,
                    content=content_text,
                    metadata=metadata
                )
                logger.info(f"Document {doc_id} indexed successfully: {result}")
            except Exception as e:
                logger.error(f"Error indexing document {doc_id}: {str(e)}")
        
        # Add task to background tasks
        background_tasks.add_task(process_document)
        
        return HyPEIndexingResponse(
            status="processing",
            doc_id=doc_id,
            chunk_count=0,
            indexed_count=0,
            processing_time=0.0
        )
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Check HyPE RAG system health"""
    try:
        # Try to initialize RAG system
        rag = get_hype_rag_system()
        
        return {
            "status": "healthy",
            "collection": rag.collection_name,
            "embedding_model": rag.embedding_model_name,
            "embedding_dim": rag.embedding_dim
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"HyPE RAG system is not healthy: {str(e)}"
        )

@router.post("/debug/retrieve")
async def debug_retrieve(request: Dict[str, Any] = Body(...)):
    """Debug endpoint for testing HyPE RAG retrieval with verbose output"""
    try:
        # Get query and parameters
        query = request.get("query", "")
        top_k = request.get("top_k", 5)
        filters = request.get("filters", None)
        debug = request.get("debug", True)
        
        # Validate query
        if not query:
            raise HTTPException(
                status_code=400,
                detail="Query parameter is required"
            )
        
        # Get RAG system
        rag = get_hype_rag_system()
        if not rag:
            raise HTTPException(
                status_code=500,
                detail="HyPE RAG system is not available"
            )
        
        # Get retrieval results
        results = rag.retrieve(query=query, top_k=top_k, filters=filters)
        
        # Format response with extra debug info
        response = {
            "query": query,
            "results": results,
            "result_count": len(results),
            "vector_weight": rag.vector_weight,
            "semantic_weight": rag.semantic_weight,
            "bm25_initialized": rag.bm25_initialized,
            "embedding_model": rag.embedding_model_name,
            "embedding_dim": rag.embedding_dim
        }
        
        # Generate a question for debugging if debug is enabled
        if debug:
            try:
                # Generate sample hypothetical questions for the query
                sample_questions = rag.generate_hypothetical_questions(query)
                response["sample_questions"] = sample_questions
            except Exception as qe:
                logger.error(f"Error generating sample questions: {str(qe)}")
        
        return response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in debug retrieve: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in debug retrieve: {str(e)}"
        )

def get_hype_rag_system():
    """Get the HyPE RAG system from main application"""
    from rag.hype_rag import HyPERagSystem
    from main import rag_system

    # The rag_system in main is actually a HyPERagSystem aliased as RAGSystem
    if not rag_system:
        logger.error("RAG system not initialized in main")
        return None
        
    # Make sure it's a HyPERagSystem
    if not isinstance(rag_system, HyPERagSystem):
        logger.error(f"RAG system in main is not a HyPERagSystem: {type(rag_system)}")
        return None
        
    logger.info("Found HyPE RAG system from main")
    return rag_system 