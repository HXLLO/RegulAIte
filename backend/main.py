# plugins/regul_aite/backend/main.py
from fastapi import FastAPI, HTTPException, Depends, Body, File, UploadFile, Form, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import logging
import os
import sys
import time
import uuid
import json
import mariadb
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime, timedelta
from openai import OpenAI
from unstructured_parser.base_parser import BaseParser, ParserType
import threading
import random
import string
import shutil
import tempfile
import asyncio
import requests
import uvicorn
import mysql.connector
from enum import Enum

# Add current directory to Python path for Docker
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import centralized configuration
from config.app_config import get_config, validate_config

# Import task router from routers package instead of directly from queuing_sys
from routers.task_router import task_router

# Import document parser
from unstructured_parser.document_parser import DocumentParser

# Import LlamaIndex RAG components
from rag.hype_rag import HyPERagSystem as RAGSystem
from rag.query_engine import RAGQueryEngine

# Import our new custom routers
from routers.chat_router import router as chat_router
from routers.document_router import router as document_router
from routers.config_router import router as config_router
from routers.agents_router import router as agents_router
from routers.welcome_router import router as welcome_router
from routers.auth_router import router as auth_router
from routers.hype_router import router as hype_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Try to import organization router after logger is configured
try:
    from routers.organization_router import router as organization_router
    logger.info("Organization router imported successfully")
except Exception as e:
    logger.error(f"Failed to import organization router: {str(e)}")
    organization_router = None

# Import agent framework (after logger is configured)
from agent_framework.factory import initialize_complete_agent_system
from agent_framework.tools.document_finder import get_document_finder

# Load environment variables
load_dotenv()

# Get configuration
app_config = get_config()

# Validate configuration on startup
config_validation = validate_config()
if not config_validation['valid']:
    logger.error("Configuration validation failed:")
    for error in config_validation['errors']:
        logger.error(f"  - {error}")
    sys.exit(1)

if config_validation['warnings']:
    logger.warning("Configuration warnings:")
    for warning in config_validation['warnings']:
        logger.warning(f"  - {warning}")

# Custom JSON Response class
class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        try:
            # Use custom encoder for handling datetime objects
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

# Helper function to serialize datetime objects
def datetime_serializer(obj):
    """Custom serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Create FastAPI instance
app = FastAPI(
    title="RegulAIte API",
    description="Backend API for RegulAIte application",
    version="1.0.0",
    # Set default response class to use our custom JSON encoder
    default_response_class=CustomJSONResponse,
)

app.include_router(task_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(agents_router)
app.include_router(chat_router)
app.include_router(document_router)
app.include_router(config_router)
app.include_router(welcome_router)
app.include_router(auth_router)
app.include_router(hype_router)

# Include organization router if available
if organization_router:
    app.include_router(organization_router)
    logger.info("Organization router included successfully")
else:
    logger.warning("Organization router not available, skipping include")

# Initialize RAG system and query engine as global variables
rag_system = None
rag_query_engine = None
document_parser = None  # Initialize document parser as None by default

# Initialize agent system as global variable
agent_orchestrator = None

# Model preloading thread
model_thread = None
model_loading_status = {
    "started": False, 
    "completed": False, 
    "results": None, 
    "start_time": None,
    "end_time": None,
    "languages": [],
    "progress": 0,
    "total_languages": 0,
    "current_language": None,
    "error": None,
    "language_status": {},  # Will track per-language loading status
    "language_errors": {}  # Will track per-language errors
}

async def get_global_orchestrator():
    """Get the global agent orchestrator instance, initializing if needed."""
    return await ensure_agent_system_ready()

def get_global_orchestrator_sync():
    """Get the global agent orchestrator instance synchronously (may return None if not ready)."""
    global agent_orchestrator
    if agent_orchestrator is None or agent_orchestrator == "preparing":
        return None
    return agent_orchestrator

def is_agent_system_ready():
    """Check if the agent system is ready."""
    global agent_orchestrator
    if agent_orchestrator is None or agent_orchestrator == "preparing":
        return False
    if not hasattr(agent_orchestrator, 'specialized_agents'):
        return False
    return len(agent_orchestrator.specialized_agents) > 0

@app.on_event("startup")
def startup_event():
    """
    Startup event handler to initialize application
    """
    logger.info("Starting RegulAIte API...")
    
    # Initialize RAG system
    init_rag_system()
    
    # Initialize document parser
    init_document_parser()
    
    # Initialize agent system
    init_agent_system()
    
    # Start model preloading in a separate thread
    # Default to French language model as primary language
    init_language_support(['fr'])


def init_document_parser():
    """Initialize the document parser."""
    global document_parser
    global rag_system # Ensure rag_system is accessible
    
    try:
        
        logger.info("Initializing document parser...")
        
        # Ensure RAG system is initialized first to get embedding_dim
        if not rag_system:
            logger.warning("RAG system not initialized yet. Cannot get embedding_dim for DocumentParser. Using default.")
            embedding_dim = 384 # Default if RAG system is not ready
        else:
            embedding_dim = rag_system.embedding_dim
            
        document_parser = DocumentParser(
            embedding_dim=embedding_dim, # Pass embedding_dim
            chunk_size=app_config.document_parser.chunk_size,
            chunk_overlap=app_config.document_parser.chunk_overlap,
            chunking_strategy="fixed",
            extract_tables=app_config.document_parser.extract_tables,
            extract_metadata=app_config.document_parser.extract_metadata,
            extract_images=app_config.document_parser.extract_images
        )
        logger.info(f"Document parser initialized successfully with embedding_dim: {embedding_dim}")
    except Exception as e:
        logger.error(f"Error initializing document parser: {str(e)}")
        document_parser = None


def init_language_support(languages=['fr']):
    """
    Initialize language support for document processing.
    """
    global model_thread, model_loading_status
    
    if model_thread and model_thread.is_alive():
        logger.info("Model loading already in progress")
        return
    
    model_loading_status.update({
        "started": True,
        "completed": False,
        "start_time": datetime.now().isoformat(),
        "languages": languages,
        "total_languages": len(languages),
        "progress": 0,
        "current_language": None,
        "error": None
    })
    
    def load_models():
        """Load language models in a separate thread."""
        try:
            logger.info(f"Starting model loading for languages: {languages}")
            
            for i, lang in enumerate(languages):
                model_loading_status["current_language"] = lang
                model_loading_status["progress"] = int((i / len(languages)) * 100)
                
                try:
                    logger.info(f"Loading model for language: {lang}")
                    # Simulate model loading - replace with actual model loading logic
                    time.sleep(2)  # Simulate loading time
                    
                    model_loading_status["language_status"][lang] = "loaded"
                    logger.info(f"Model for {lang} loaded successfully")
                    
                except Exception as e:
                    error_msg = f"Failed to load model for {lang}: {str(e)}"
                    logger.error(error_msg)
                    model_loading_status["language_errors"][lang] = error_msg
                    model_loading_status["language_status"][lang] = "failed"
            
            model_loading_status.update({
                "completed": True,
                "progress": 100,
                "end_time": datetime.now().isoformat(),
                "current_language": None
            })
            
            logger.info("Model loading completed")
            
        except Exception as e:
            error_msg = f"Model loading failed: {str(e)}"
            logger.error(error_msg)
            model_loading_status.update({
                "completed": True,
                "error": error_msg,
                "end_time": datetime.now().isoformat()
            })
    
    model_thread = threading.Thread(target=load_models, daemon=True)
    model_thread.start()


def init_rag_system():
    """Initialize the RAG system."""
    global rag_system, rag_query_engine
    
    try:
        logger.info("Initializing RAG system...")
        
        rag_system = RAGSystem(
            qdrant_url=app_config.qdrant.url,
            collection_name=app_config.qdrant.collection_name,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            chunk_size=app_config.document_parser.chunk_size,
            chunk_overlap=app_config.document_parser.chunk_overlap
        )
        
        rag_query_engine = RAGQueryEngine(rag_system)
        
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing RAG system: {str(e)}")
        rag_system = None
        rag_query_engine = None


def init_agent_system():
    """Initialize the agent system with proper dependency injection."""
    global agent_orchestrator
    
    try:
        logger.info("Initializing agent system...")
        
        # Import here to avoid circular imports
        from agent_framework.factory import initialize_complete_agent_system
        from agent_framework.integrations.rag_integration import initialize_rag_integration
        
        # Initialize RAG integration with our systems
        initialize_rag_integration(rag_system=rag_system, rag_query_engine=rag_query_engine)
        
        # For now, mark agent system as preparing and defer actual initialization
        # This avoids event loop conflicts during FastAPI startup
        logger.info("Agent system preparation completed. Actual initialization will happen on first use.")
        agent_orchestrator = "preparing"  # Special marker to indicate preparation
        
    except Exception as e:
        logger.error(f"Error preparing agent system: {str(e)}")
        import traceback
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        agent_orchestrator = None

async def ensure_agent_system_ready():
    """Ensure the agent system is initialized and ready."""
    global agent_orchestrator
    
    # If already initialized and ready, return it
    if agent_orchestrator and agent_orchestrator != "preparing" and hasattr(agent_orchestrator, 'specialized_agents'):
        return agent_orchestrator
    
    # If preparing or not initialized, do it now
    try:
        logger.info("Performing deferred agent system initialization...")
        
        from agent_framework.factory import initialize_complete_agent_system
        
        agent_orchestrator = await initialize_complete_agent_system(rag_system=rag_system)
        
        # Verify that agents are properly registered
        if agent_orchestrator and agent_orchestrator.specialized_agents:
            registered_agents = list(agent_orchestrator.specialized_agents.keys())
            logger.info(f"✅ Agent system ready with {len(registered_agents)} agents: {registered_agents}")
        else:
            logger.error("❌ Agent system initialization failed - no agents registered")
            
        return agent_orchestrator
        
    except Exception as e:
        logger.error(f"Error initializing agent system: {str(e)}")
        import traceback
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        agent_orchestrator = None
        return None


@app.get("/api/status")
def get_status():
    """
    Get API status including model preloading status
    """
    agent_status = "not_prepared"
    agent_count = 0
    
    if is_agent_system_ready():
        agent_status = "ready"
        orchestrator = get_global_orchestrator_sync()
        if orchestrator:
            agent_count = len(orchestrator.specialized_agents)
    elif agent_orchestrator == "preparing":
        agent_status = "preparing"
    elif agent_orchestrator is not None:
        agent_status = "prepared"
        
    status_info = {
        "status": "running",
        "rag_system": "initialized" if rag_system else "not_initialized",
        "document_parser": "initialized" if document_parser else "not_initialized",
        "agent_system": agent_status,
        "agent_count": agent_count
        } 
    return status_info

@app.get("/api/agents/test")
async def test_agent_system():
    """
    Test endpoint pour vérifier que le système d'agents fonctionne.
    """
    try:
        # Importer l'orchestrateur depuis le routeur
        from routers.agents_router import get_orchestrator
        
        orchestrator = await get_orchestrator()
        
        # Test simple de fonctionnement
        from agent_framework.agent import Query
        test_query = Query(query_text="Bonjour, peux-tu me confirmer que le système d'agents fonctionne ?")
        
        response = await orchestrator.process_query(test_query)
        
        return {
            "status": "success",
            "message": "Système d'agents fonctionnel",
            "test_response": response.content[:200] + "..." if len(response.content) > 200 else response.content,
            "agents_registered": list(orchestrator.specialized_agents.keys())
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du test du système d'agents: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur système d'agents: {str(e)}",
            "agents_registered": []
        }

@app.get("/api/agents/debug")
async def debug_agent_system():
    """
    Debug endpoint pour analyser l'état détaillé du système d'agents.
    """
    debug_info = {
        "global_orchestrator": None,
        "router_orchestrator": None,
        "system_status": None
    }
    
    try:
        # Vérifier l'orchestrateur global
        global_orch = await get_global_orchestrator()
        if global_orch:
            debug_info["global_orchestrator"] = {
                "id": global_orch.agent_id,
                "name": global_orch.name,
                "agents_count": len(global_orch.specialized_agents),
                "agents": global_orch.get_registered_agents(),
                "status": "ready" if len(global_orch.specialized_agents) > 0 else "empty"
            }
            # Debug détaillé
            global_orch.debug_agent_status()
        else:
            debug_info["global_orchestrator"] = {"status": "not_initialized"}
            
        # Vérifier l'orchestrateur du routeur
        try:
            from routers.agents_router import get_orchestrator
            router_orch = await get_orchestrator()
            if router_orch:
                debug_info["router_orchestrator"] = {
                    "id": router_orch.agent_id,
                    "name": router_orch.name,
                    "agents_count": len(router_orch.specialized_agents),
                    "agents": router_orch.get_registered_agents(),
                    "status": "ready" if len(router_orch.specialized_agents) > 0 else "empty",
                    "is_same_as_global": router_orch is global_orch
                }
                # Debug détaillé
                router_orch.debug_agent_status()
        except Exception as e:
            debug_info["router_orchestrator"] = {"status": "error", "error": str(e)}
            
        # État du système
        debug_info["system_status"] = {
            "agent_system_ready": is_agent_system_ready(),
            "rag_system": "initialized" if rag_system else "not_initialized",
            "document_parser": "initialized" if document_parser else "not_initialized"
        }
        
        return debug_info
        
    except Exception as e:
        logger.error(f"Erreur lors du debug du système d'agents: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur debug système d'agents: {str(e)}",
            "debug_info": debug_info
        }

@app.get("/")
def root():
    """
    Root endpoint
    """
    return {"message": "Welcome to RegulAIte API"}

# Models
class ChatMessage(BaseModel):
    """Message in a chat conversation."""
    role: Literal["user", "assistant", "system"] = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for chat completion."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    stream: bool = Field(False, description="Whether to stream the response")
    model: str = Field("gpt-4.1", description="Model to use for generation")
    temperature: float = Field(0.2, description="Temperature for generation")
    max_tokens: int = Field(2048, description="Maximum tokens in response")
    include_context: bool = Field(True, description="Whether to include RAG context")
    context_query: Optional[str] = Field(None, description="Query to use for retrieving context")
    

class SearchRequest(BaseModel):
    """Request for search."""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, description="Maximum number of results")
    filter_criteria: Optional[Dict[str, Any]] = Field(None, description="Metadata filter criteria")


class SearchResult(BaseModel):
    """Result from a search query."""
    entity: Optional[str] = None
    related: Optional[str] = None
    relationship: Optional[str] = None
    document: Optional[str] = None
    section: Optional[str] = None
    relevance: Optional[float] = None


class SearchResponse(BaseModel):
    """Response for a search query."""
    results: List[SearchResult]
    query: str
    timestamp: str


class DocumentProcessResponse(BaseModel):
    """Response for document processing."""
    doc_id: str
    filename: str
    chunk_count: int
    status: str
    message: str


class ContextRequest(BaseModel):
    """Request for retrieving context."""
    query: str = Field(..., description="Query to use for retrieving context")
    limit: int = Field(5, description="Maximum number of results to return")
    
def get_mariadb_connection():
    """Get a connection to MariaDB."""
    conn = None
    max_retries = 3
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries and conn is None:
        try:
            logger.info(f"Attempting to connect to MariaDB at {app_config.database.host} (attempt {retry_count + 1}/{max_retries})")
            
            conn = mariadb.connect(
                host=app_config.database.host,
                user=app_config.database.user,
                password=app_config.database.password,
                database=app_config.database.database,
                port=app_config.database.port,
                autocommit=False  # Disable autocommit to manage transactions
            )
            
            # Verify connectivity with a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
            logger.info(f"Connected to MariaDB at {app_config.database.host}")
            
            # Initialize database tables if needed
            initialize_database(conn)
            
            return conn
            
        except mariadb.Error as e:
            last_error = e
            retry_count += 1
            logger.error(f"Failed to connect to MariaDB (attempt {retry_count}/{max_retries}): {str(e)}")
            time.sleep(5)  # 5 second delay between retries
    
    logger.error(f"Failed to connect to MariaDB after {max_retries} attempts. Last error: {str(last_error)}")
    raise HTTPException(
        status_code=500,
        detail="Database connection not available"
    )


def initialize_database(conn):
    """Initialize database tables if they don't exist."""
    try:
        cursor = conn.cursor()
        
        # Create regulaite_settings table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS regulaite_settings (
            setting_key VARCHAR(255) PRIMARY KEY,
            setting_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            description TEXT
        ) ENGINE=InnoDB;
        """)
        
        # Insert default settings if they don't exist
        cursor.execute("""
        INSERT IGNORE INTO regulaite_settings (setting_key, setting_value, description) VALUES
        ('llm_model', 'gpt-4.1', 'Default LLM model'),
        ('llm_temperature', '0.2', 'Default temperature for LLM'),
        ('llm_max_tokens', '2048', 'Default max tokens for LLM'),
        ('llm_top_p', '1', 'Default top_p value for LLM'),
        ('enable_chat_history', 'true', 'Whether to save chat history');
        """)
        
        # Create users table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            company VARCHAR(255),
            username VARCHAR(255) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            settings JSON
        ) ENGINE=InnoDB;
        """)
        
        # Create refresh tokens table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            token_id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            refresh_token VARCHAR(255) NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """)
        
        # Create other necessary tables...
        
        conn.commit()
        cursor.close()
    except mariadb.Error as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()


@app.get("/")
def read_root():
    """Root endpoint."""
    logger.info("Root endpoint called")
    return {
        "status": "ok",
        "message": "RegulAite API is running",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    logger.info("Health check endpoint called")

    mariadb_status = "disconnected"
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        mariadb_status = "connected"
    except:
        pass

    return {
        "status": "healthy",
        "components": {
            "mariadb": mariadb_status,
            "api": "healthy"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/documents/process", response_model=DocumentProcessResponse)
async def process_document(
    file: UploadFile = File(...),
    doc_id: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    use_nlp: bool = Form(True),
    use_enrichment: bool = Form(False),
    detect_language: bool = Form(True),
    language: Optional[str] = Form(None),
    use_queue: bool = Form(False),
    parser_type: str = Form(ParserType.UNSTRUCTURED.value)
):
    """Process a document and store it in the database."""
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

        # Add file metadata
        doc_metadata["original_filename"] = file.filename
        doc_metadata["content_type"] = file.content_type
        doc_metadata["size"] = 0  # Will be updated with actual size
        doc_metadata["use_nlp"] = use_nlp
        doc_metadata["use_enrichment"] = use_enrichment
        doc_metadata["parser_type"] = parser_type  # Store the parser type used

        # Extract file extension and store both filetype and file_type for compatibility
        file_ext = os.path.splitext(file.filename)[1].lower().lstrip('.')
        doc_metadata["filetype"] = file_ext
        doc_metadata["file_type"] = file_ext  # Add both property names for compatibility

        # Add language info if provided
        if language:
            doc_metadata["language"] = language
            doc_metadata["language_detect"] = False
        else:
            doc_metadata["language_detect"] = detect_language

        # Read file content
        file_content = await file.read()
        doc_metadata["size"] = len(file_content)

        # Use queue for processing if requested
        if use_queue:
            # Queue the document processing task
            from routers.task_router import queue_document_processing
            
            # Create a new UploadFile with the read content reset
            file.file.seek(0)
            
            response = await queue_document_processing(
                file=file,
                doc_id=doc_id,
                metadata=json.dumps(doc_metadata),
                use_nlp=use_nlp,
                use_enrichment=use_enrichment,
                detect_language=detect_language,
                language=language,
                parser_type=parser_type
            )
            
            return {
                "doc_id": doc_id,
                "filename": file.filename,
                "chunk_count": 0,
                "status": "queued",
                "message": f"Document queued for processing (Task ID: {response.task_id})"
            }

        # Process document - get the appropriate parser if not using the default
        parser = document_parser
        if parser_type != ParserType.UNSTRUCTURED.value:
            # Get parser using the factory method
            try:
                parser = BaseParser.get_parser(
                    parser_type=ParserType(parser_type),
                    qdrant_url=app_config.qdrant.url
                )
            except Exception as e:
                logger.error(f"Error creating parser of type {parser_type}: {str(e)}")
                # Fall back to default parser
                parser = document_parser
        
        # Check if extract_images is in parser_settings
        extract_images = False
        if "parser_settings" in doc_metadata and isinstance(doc_metadata["parser_settings"], dict):
            if "extract_images" in doc_metadata["parser_settings"]:
                extract_images = bool(doc_metadata["parser_settings"]["extract_images"])
                logger.info(f"Setting extract_images={extract_images} from parser settings")
                
                # If using the default parser, we need to modify its settings
                if parser == document_parser:
                    parser.extract_images = extract_images
        
        # Process the document with the selected parser
        try:
            result = parser.process_document(
                file_content=file_content,
                file_name=file.filename,
                doc_id=doc_id,
                doc_metadata=doc_metadata,
                detect_language=detect_language
            )

            # Extract statistics from the result
            processed_doc_id = result["doc_id"]
            chunk_count = result.get("chunk_count", 0)
            section_count = result.get("section_count", 0)
            entity_count = result.get("entity_count", 0)
            concept_count = result.get("concept_count", 0)
            requirement_count = result.get("requirement_count", 0)
            has_regulatory_content = result.get("has_regulatory_content", False)
            detected_language = result.get("language")
            language_name = result.get("language_name")
            image_count = result.get("image_count", 0)

            # Create language info part of the message
            language_msg = ""
            if detected_language:
                language_msg = f" (Language: {language_name or detected_language})"
                
            # Add image extraction info to message
            image_msg = ""
            if extract_images and image_count > 0:
                image_msg = f" with {image_count} extracted images"

            # Index document in Qdrant through RAG system
            try:
                # Check if indexing is configured
                index_immediately = True  # Default to True
                try:
                    # Get setting from MariaDB
                    conn = get_mariadb_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute(
                        """
                        SELECT setting_value
                        FROM regulaite_settings
                        WHERE setting_key = 'doc_index_immediately'
                        """
                    )
                    db_result = cursor.fetchone()
                    if db_result:
                        index_immediately = db_result['setting_value'].lower() == 'true'
                    conn.close()
                except Exception as config_e:
                    logger.warning(f"Could not get index_immediately setting, using default: {str(config_e)}")
                
                if index_immediately:
                    logger.info(f"Indexing document {processed_doc_id} in Qdrant")
                    index_result = rag_system.process_parsed_document(result)
                    
                    if isinstance(index_result, dict):
                        if index_result.get("status") == "success":
                            vector_count = index_result.get("vector_count", 0)
                            logger.info(f"Document {processed_doc_id} indexed in Qdrant with {vector_count} vectors")
                        elif "vector_count" in index_result and index_result.get("vector_count", 0) > 0:
                            vector_count = index_result.get("vector_count", 0)
                            logger.info(f"Document {processed_doc_id} indexed in Qdrant with {vector_count} vectors")
                        elif index_result.get("message") == "Document already indexed":
                            logger.info(f"Document {processed_doc_id} was already indexed")
                        else:
                            logger.warning(f"Indexing completed but may have issues: {index_result}")
                    else:
                        logger.warning(f"Unexpected indexing result format: {type(index_result)} - {index_result}")
                else:
                    logger.info(f"Immediate indexing disabled, document {processed_doc_id} will not be indexed now")
            except Exception as e:
                logger.error(f"Error indexing document in Qdrant: {str(e)}", exc_info=True)
                # Continue without failing as the document is already processed in Qdrant

            # Make sure to close the custom parser if we created one
            if parser != document_parser:
                try:
                    parser.close()
                except:
                    pass

            return {
                "doc_id": processed_doc_id,
                "filename": file.filename,
                "chunk_count": chunk_count,
                "status": "success",
                "message": f"Document processed successfully with {parser_type} parser{language_msg} with {chunk_count} chunks, {section_count} sections, {entity_count} entities, and {concept_count} concepts{image_msg}" +
                          (f", including {requirement_count} regulatory requirements" if has_regulatory_content else "")
            }

        except Exception as e:
            # Make sure to close the custom parser if we created one
            if parser != document_parser:
                try:
                    parser.close()
                except:
                    pass
                    
            logger.error(f"Error processing document: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing document: {str(e)}"
            )

    except Exception as e:
        logger.error(f"Error handling document upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error handling document upload: {str(e)}"
        )


@app.post("/chat")
async def chat(request: ChatRequest, req: Request):
    """Chat with the RAG-enhanced LLM or AI agent."""
    try:
        # Get messages from request
        messages = request.messages

        # Get the last user message
        user_message = next((m.content for m in reversed(messages) if m.role == "user"), None)

        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No user message found in the chat history"
            )

            # Store the conversation in MariaDB
            try:
                conn = get_mariadb_connection()
                cursor = conn.cursor()

                # Generate a session ID if not present
                session_id = req.headers.get("X-Session-ID", str(uuid.uuid4()))
                user_id = req.headers.get("X-User-ID")
                
                # If no user ID is provided and authentication is required, return error
                if not user_id and os.getenv("REQUIRE_AUTH", "false").lower() == "true":
                    raise HTTPException(
                        status_code=401,
                        detail="Authentication required"
                    )
                    
                # Use a generated user ID if none provided
                if not user_id:
                    user_id = f"guest_{str(uuid.uuid4())[:8]}"

                # Store user message
                cursor.execute(
                    """
                    INSERT INTO chat_history (user_id, session_id, message_text, message_role)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, session_id, user_message, "user")
                )

                # Store assistant response
                cursor.execute(
                    """
                    INSERT INTO chat_history (user_id, session_id, message_text, message_role)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, session_id, assistant_message, "assistant")
                )

                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Error storing chat history: {str(e)}")
                # Continue anyway, as this is not critical

            return {
                "message": assistant_message,
                "model": request.model,
                "agent_type": request.agent_type,
                "agent_used": True,
                "tree_reasoning_used": request.use_tree_reasoning,
                "context_used": request.include_context,
                "timestamp": datetime.now().isoformat()
            }

        # Standard RAG-based processing
        else:
            # Determine if we should use context
            if request.include_context:
                # Use context_query if provided, otherwise use the user message
                query = request.context_query or user_message

                # Retrieve context using RAG system
                retrieved_nodes = rag_system.retrieve(query, top_k=5)

                # Format context
                if retrieved_nodes:
                    context_parts = []
                    for node in retrieved_nodes:
                        source = f"{node['metadata'].get('doc_name', 'Unknown document')}"
                        if 'section' in node['metadata'] and node['metadata']['section'] != 'Unknown':
                            source += f" - {node['metadata']['section']}"

                        context_parts.append(f"Source: {source}\nContent: {node['text']}")

                    context = "\n\n".join(context_parts)
                else:
                    context = "No relevant context found in the knowledge base."
            else:
                context = None

            # Generate response based on chat history and context
            if context:
                # Add system message with context
                system_message = f"""You are an AI assistant that helps with regulatory information.
    Answer based on the information in the provided context.
    If the answer cannot be found in the context, say so politely.

    Context information:
    {context}
    """
                # Prepend system message to the chat history
                messages = [ChatMessage(role="system", content=system_message)] + messages

            # Format messages for OpenAI
            openai_messages = [{"role": m.role, "content": m.content} for m in messages]

            # Call OpenAI with streaming if requested
            if request.stream:
                # For streaming, return a StreamingResponse
                async def generate():
                    client = OpenAI(api_key=app_config.openai.api_key)

                    completion = client.chat.completions.create(
                        model=request.model,
                        messages=openai_messages,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens,
                        stream=True
                    )

                    for chunk in completion:
                        if chunk.choices[0].delta.content:
                            yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

                    yield f"data: [DONE]\n\n"

                return StreamingResponse(generate(), media_type="text/event-stream")
            else:
                # For non-streaming, return a regular response
                client = OpenAI(api_key=app_config.openai.api_key)

                completion = client.chat.completions.create(
                    model=request.model,
                    messages=openai_messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )

                # Extract the assistant's response
                assistant_message = completion.choices[0].message.content

                # Store the conversation in MariaDB
                try:
                    conn = get_mariadb_connection()
                    cursor = conn.cursor()

                    # Generate a session ID if not present
                    session_id = req.headers.get("X-Session-ID", str(uuid.uuid4()))
                    user_id = req.headers.get("X-User-ID")
                    
                    # If no user ID is provided and authentication is required, return error
                    if not user_id and os.getenv("REQUIRE_AUTH", "false").lower() == "true":
                        raise HTTPException(
                            status_code=401,
                            detail="Authentication required"
                        )
                        
                    # Use a generated user ID if none provided
                    if not user_id:
                        user_id = f"guest_{str(uuid.uuid4())[:8]}"

                    # Store user message
                    cursor.execute(
                        """
                        INSERT INTO chat_history (user_id, session_id, message_text, message_role)
                        VALUES (?, ?, ?, ?)
                        """,
                        (user_id, session_id, user_message, "user")
                    )

                    # Store assistant response
                    cursor.execute(
                        """
                        INSERT INTO chat_history (user_id, session_id, message_text, message_role)
                        VALUES (?, ?, ?, ?)
                        """,
                        (user_id, session_id, assistant_message, "assistant")
                    )

                    conn.commit()
                    conn.close()
                except Exception as e:
                    logger.error(f"Error storing chat history: {str(e)}")
                    # Continue anyway, as this is not critical

                return {
                    "message": assistant_message,
                    "model": request.model,
                    "agent_used": False,
                    "tree_reasoning_used": False,
                    "context_used": request.include_context,
                    "timestamp": datetime.now().isoformat()
                }

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating chat response: {str(e)}"
        )


@app.get("/chat/history")
async def get_chat_history(session_id: str, limit: int = 50, skip_old: bool = False, max_age_days: int = None):
    """Get chat history for a session.

    Args:
        session_id: The session ID to get chat history for
        limit: Maximum number of messages to return (default: 50)
        skip_old: Whether to skip old messages entirely
        max_age_days: Maximum age of messages in days to return
    """
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor(dictionary=True)

        # Base query
        query = """
            SELECT message_text, message_role, timestamp
            FROM chat_history
            WHERE session_id = ?
        """
        params = [session_id]

        # Add age filter if requested
        if skip_old or max_age_days:
            if max_age_days:
                query += " AND timestamp >= DATE_SUB(NOW(), INTERVAL ? DAY)"
                params.append(max_age_days)
            elif skip_old:
                query += " AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)"

        # Add ordering and limit
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        history = cursor.fetchall()
        conn.close()

        return {
            "session_id": session_id,
            "messages": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )


@app.delete("/chat/history/{session_id}")
async def delete_chat_history(session_id: str, before_days: int = None):
    """Delete chat history for a session.

    Args:
        session_id: The session ID to delete chat history for
        before_days: If provided, only delete messages older than this many days
    """
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor()

        # Base delete query
        query = "DELETE FROM chat_history WHERE session_id = ?"
        params = [session_id]

        # Add age filter if requested
        if before_days is not None:
            query += " AND timestamp < DATE_SUB(NOW(), INTERVAL ? DAY)"
            params.append(before_days)

        cursor.execute(query, params)
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return {
            "session_id": session_id,
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} messages from chat history"
        }
    except Exception as e:
        logger.error(f"Error deleting chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting chat history: {str(e)}"
        )


@app.delete("/chat/history")
async def delete_all_chat_history(before_days: int = None, user_id: str = None):
    """Delete all chat history or filter by user.

    Args:
        before_days: If provided, only delete messages older than this many days
        user_id: If provided, only delete messages for this user
    """
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor()

        # Base delete query
        query = "DELETE FROM chat_history WHERE 1=1"
        params = []

        # Add filters if requested
        if before_days is not None:
            query += " AND timestamp < DATE_SUB(NOW(), INTERVAL ? DAY)"
            params.append(before_days)

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


@app.get("/settings")
async def get_settings():
    """Get global settings."""
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT setting_key, setting_value
            FROM regulaite_settings
            """
        )

        settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
        conn.close()

        # Format LLM settings if they exist
        llm_settings = {}

        # Extract LLM settings with prefix llm_
        for key, value in list(settings.items()):
            if key.startswith('llm_'):
                # Remove the prefix for cleaner API response
                clean_key = key[4:]  # Remove 'llm_' prefix

                # Handle special types
                if clean_key in ['temperature', 'top_p', 'frequency_penalty', 'presence_penalty']:
                    try:
                        llm_settings[clean_key] = float(value)
                    except ValueError:
                        llm_settings[clean_key] = value
                elif clean_key in ['max_tokens']:
                    try:
                        llm_settings[clean_key] = int(value)
                    except ValueError:
                        llm_settings[clean_key] = value
                else:
                    llm_settings[clean_key] = value

                # Remove these from the main settings dict to avoid duplication
                settings.pop(key)

        # Add the formatted LLM settings to the response if they exist
        if llm_settings:
            settings['llm_config'] = llm_settings

        return settings
    except Exception as e:
        logger.error(f"Error retrieving settings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving settings: {str(e)}"
        )


@app.post("/settings")
async def update_settings(settings: Dict[str, Any]):
    """Update global settings."""
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor()

        # Handle LLM config if it exists in the payload
        if 'llm_config' in settings:
            llm_config = settings.pop('llm_config')

            # Flatten LLM config with llm_ prefix
            for key, value in llm_config.items():
                settings[f'llm_{key}'] = value

        for key, value in settings.items():
            cursor.execute(
                """
                INSERT INTO regulaite_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON DUPLICATE KEY UPDATE setting_value = ?
                """,
                (key, str(value), str(value))
            )

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": f"Updated {len(settings)} settings"
        }
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating settings: {str(e)}"
        )


# Add a specific endpoint just for LLM configuration
@app.get("/settings/llm")
async def get_llm_settings():
    """Get LLM configuration settings."""
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT setting_key, setting_value
            FROM regulaite_settings
            WHERE setting_key LIKE 'llm_%'
            """
        )

        settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
        conn.close()

        # Format settings (remove prefix and convert types)
        llm_config = {}
        for key, value in settings.items():
            clean_key = key[4:]  # Remove 'llm_' prefix

            # Handle special types
            if clean_key in ['temperature', 'top_p', 'frequency_penalty', 'presence_penalty']:
                try:
                    llm_config[clean_key] = float(value)
                except ValueError:
                    llm_config[clean_key] = value
            elif clean_key in ['max_tokens']:
                try:
                    llm_config[clean_key] = int(value)
                except ValueError:
                    llm_config[clean_key] = value
            else:
                llm_config[clean_key] = value

        return llm_config
    except Exception as e:
        logger.error(f"Error retrieving LLM settings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving LLM settings: {str(e)}"
        )


@app.post("/settings/llm")
async def update_llm_settings(llm_config: Dict[str, Any]):
    """Update LLM configuration settings."""
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor()

        # Add llm_ prefix to all keys
        settings = {f'llm_{key}': value for key, value in llm_config.items()}

        for key, value in settings.items():
            cursor.execute(
                """
                INSERT INTO regulaite_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON DUPLICATE KEY UPDATE setting_value = ?
                """,
                (key, str(value), str(value))
            )

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": f"Updated {len(settings)} LLM settings"
        }
    except Exception as e:
        logger.error(f"Error updating LLM settings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating LLM settings: {str(e)}"
        )


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, background_tasks: BackgroundTasks = None):
    """Delete a document from the system."""
    try:
        logger.info(f"Processing request to delete document: {doc_id}")

        # Delete document from Qdrant through RAG system
        if rag_system:
            success = rag_system.delete_document(doc_id)
            if success:
                return {
                    "status": "success",
                    "message": f"Document {doc_id} deleted successfully",
                    "doc_id": doc_id
                }
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Document not found or could not be deleted: {doc_id}"
                )
        else:
            raise HTTPException(
                status_code=500,
                detail="RAG system not available"
            )

    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )


@app.delete("/documents")
async def delete_all_documents(background_tasks: BackgroundTasks = None, confirm: str = ""):
    """Delete ALL documents from the system (nuclear option)."""
    try:
        # Require confirmation parameter to prevent accidental deletion
        if confirm != "DELETE_ALL_DOCUMENTS":
            raise HTTPException(
                status_code=400,
                detail="To delete all documents, you must include confirm=DELETE_ALL_DOCUMENTS parameter"
            )
        
        logger.warning("Processing request to delete ALL documents from the system")

        # Delete all documents from Qdrant through RAG system
        if rag_system:
            result = rag_system.delete_all_documents()
            
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "message": f"Successfully deleted {result.get('total_deleted', 0)} vectors from all collections",
                    "total_deleted": result.get("total_deleted", 0),
                    "collections": result.get("collections", {}),
                    "warning": "All documents have been permanently deleted from the vector store"
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error during bulk deletion: {result.get('error', 'Unknown error')}"
                )
        else:
            raise HTTPException(
                status_code=500,
                detail="RAG system not available"
            )

    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        logger.error(f"Error deleting all documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting all documents: {str(e)}"
        )


@app.get("/documents/count")
async def get_document_count():
    """Get count of documents and vectors in the system."""
    try:
        logger.info("Getting document count")

        if rag_system:
            result = rag_system.get_document_count()
            
            return {
                "status": "success",
                "total_vectors": result.get("total_vectors", 0),
                "unique_documents": result.get("unique_documents", 0),
                "collections": result.get("collections", {}),
                "bm25_nodes": result.get("bm25_nodes", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="RAG system not available"
            )

    except Exception as e:
        logger.error(f"Error getting document count: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting document count: {str(e)}"
        )


@app.get("/documents/list-ids")
async def list_document_ids(limit: int = 100):
    """List all unique document IDs in the system."""
    try:
        logger.info(f"Listing document IDs (limit: {limit})")

        if not rag_system:
            raise HTTPException(
                status_code=500,
                detail="RAG system not available"
            )

        # Get unique document IDs from the vector store
        doc_ids = set()
        offset = None
        total_scanned = 0
        
        while len(doc_ids) < limit and total_scanned < 1000:  # Safety limit
            scroll_data = {
                "limit": 100,
                "with_payload": True,
                "with_vector": False
            }
            
            if offset:
                scroll_data["offset"] = offset
            
            response = requests.post(
                f"{rag_system.qdrant_url}/collections/{rag_system.collection_name}/points/scroll",
                headers={"Content-Type": "application/json"},
                data=json.dumps(scroll_data)
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to scroll Qdrant: {response.text}")
                break
            
            result = response.json()
            points = result.get("result", {}).get("points", [])
            
            if not points:
                break
            
            for point in points:
                doc_id = point.get("payload", {}).get("doc_id")
                if doc_id and len(doc_ids) < limit:
                    doc_ids.add(doc_id)
                total_scanned += 1
            
            offset = result.get("result", {}).get("next_page_offset")
            if not offset:
                break
        
        return {
            "status": "success",
            "document_ids": list(doc_ids),
            "count": len(doc_ids),
            "total_scanned": total_scanned,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error listing document IDs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing document IDs: {str(e)}"
        )


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when shutting down."""
    logger.info("Shutting down API")

    if document_parser:
        try:
            document_parser.close()
            logger.info("Document parser connections closed")
        except:
            pass

    if rag_system:
        try:
            rag_system.close()
            logger.info("RAG system connections closed")
        except:
            pass


@app.get("/settings/user/{user_id}/parser")
async def get_user_parser_settings(user_id: str):
    """Get parser settings for a specific user."""
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor(dictionary=True)

        # First check if user exists
        cursor.execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (user_id,)
        )

        user = cursor.fetchone()
        if not user:
            conn.close()
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )

        # Get user settings
        cursor.execute(
            "SELECT settings FROM users WHERE user_id = ?",
            (user_id,)
        )

        result = cursor.fetchone()
        conn.close()

        if result and result['settings']:
            try:
                settings = json.loads(result['settings'])
                if 'parser_settings' in settings:
                    return settings['parser_settings']
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in user settings for user {user_id}")

        # Return default settings if no user settings found
        return {
            "selected_parser": os.getenv("DEFAULT_PARSER_TYPE", "unstructured"),
            "parser_settings": {
                "extract_tables": True,
                "extract_metadata": True,
                "extract_images": False,
                "chunk_size": 2048,
                "chunk_overlap": 200,
                "chunking_strategy": "fixed"
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving user parser settings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user parser settings: {str(e)}"
        )


@app.post("/settings/user/{user_id}/parser")
async def update_user_parser_settings(user_id: str, parser_settings: Dict[str, Any]):
    """Update parser settings for a specific user."""
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor(dictionary=True)

        # First check if user exists
        cursor.execute(
            "SELECT user_id, settings FROM users WHERE user_id = ?",
            (user_id,)
        )

        user = cursor.fetchone()
        if not user:
            conn.close()
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )

        # Get existing settings or initialize empty dict
        user_settings = {}
        if user['settings']:
            try:
                user_settings = json.loads(user['settings'])
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in user settings for user {user_id}, initializing empty settings")

        # Update parser settings
        user_settings['parser_settings'] = parser_settings

        # Save updated settings
        cursor.execute(
            "UPDATE users SET settings = ? WHERE user_id = ?",
            (json.dumps(user_settings), user_id)
        )

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": "User parser settings updated"
        }
    except Exception as e:
        logger.error(f"Error updating user parser settings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating user parser settings: {str(e)}"
        )
    