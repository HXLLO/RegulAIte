# plugins/regul_aite/backend/queuing_sys/celery_worker.py
import os
import sys
import logging
import json
from celery import Celery
from typing import Dict, Any, Optional, Union, List, BinaryIO
import time
import uuid
from dotenv import load_dotenv


# Add the parent directory to Python's module path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Redis URL from environment or default
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Initialize Celery app
app = Celery(
    'regul_aite_tasks',
    broker=redis_url,
    backend=redis_url
)

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=7200,  # 2 hours task timeout (increased from 1 hour)
    task_soft_time_limit=6600,  # 1 hour 50 minutes soft timeout
    worker_prefetch_multiplier=1,  # Fetch one task at a time
    task_acks_late=True,  # Acknowledge task after it's done
    task_reject_on_worker_lost=True,  # Reject task when worker disconnects
    broker_connection_retry_on_startup=True,
    worker_max_memory_per_child=1000000,  # Restart worker after processing ~1GB to prevent memory leaks
    worker_max_tasks_per_child=10  # Restart worker after 10 tasks to prevent memory leaks
)

# Import tasks - we define these here to avoid circular imports
from unstructured_parser.base_parser import BaseParser, ParserType
from rag.hype_rag import HyPERagSystem as RAGSystem

# Configuration from environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

# Unstructured API configurations
UNSTRUCTURED_API_URL = os.getenv("UNSTRUCTURED_API_URL", "http://unstructured:8000/general/v0/general")
UNSTRUCTURED_CLOUD_API_URL = os.getenv("UNSTRUCTURED_CLOUD_API_URL", "https://api.unstructured.io/general/v0/general")
UNSTRUCTURED_CLOUD_API_KEY = os.getenv("UNSTRUCTURED_CLOUD_API_KEY", "")

# Other API configurations
DOCTLY_API_URL = os.getenv("DOCTLY_API_URL", "https://api.doctly.dev/v1/parse")
LLAMAPARSE_API_URL = os.getenv("LLAMAPARSE_API_URL", "https://api.llamaindex.ai/v1/parsing")

# Initialize shared components with retry logic
def get_document_parser(parser_type: str = ParserType.UNSTRUCTURED):
    """
    Get or initialize document parser with retry logic

    Args:
        parser_type: Type of parser to use (unstructured, unstructured_cloud, doctly, llamaparse)

    Returns:
        A document parser instance
    """
    max_retries = 5
    retry_count = 0

    parser_type_enum = None
    try:
        # Convert string to enum
        parser_type_enum = ParserType(parser_type)
    except ValueError:
        logger.warning(f"Invalid parser type: {parser_type}, using default: {ParserType.UNSTRUCTURED}")
        parser_type_enum = ParserType.UNSTRUCTURED

    # Set up specific API configurations if needed
    parser_kwargs = {
        "neo4j_uri": NEO4J_URI,
        "neo4j_user": NEO4J_USER,
        "neo4j_password": NEO4J_PASSWORD,
        "use_enrichment": True
    }

    # Add parser-specific configurations
    if parser_type_enum == ParserType.UNSTRUCTURED:
        parser_kwargs["unstructured_api_url"] = UNSTRUCTURED_API_URL
        parser_kwargs["is_cloud"] = False
    elif parser_type_enum == ParserType.UNSTRUCTURED_CLOUD:
        parser_kwargs["unstructured_api_url"] = UNSTRUCTURED_CLOUD_API_URL
        parser_kwargs["unstructured_api_key"] = UNSTRUCTURED_CLOUD_API_KEY
        parser_kwargs["is_cloud"] = True
    elif parser_type_enum == ParserType.DOCTLY:
        parser_kwargs["doctly_api_url"] = DOCTLY_API_URL
    elif parser_type_enum == ParserType.LLAMAPARSE:
        parser_kwargs["llamaparse_api_url"] = LLAMAPARSE_API_URL

    while retry_count < max_retries:
        try:
            # Use factory method to create the appropriate parser
            parser = BaseParser.get_parser(
                parser_type=parser_type_enum,
                **parser_kwargs
            )
            logger.info(f"{parser_type} parser initialized successfully")
            return parser
        except Exception as e:
            retry_count += 1
            logger.error(f"Failed to initialize {parser_type} parser (attempt {retry_count}/{max_retries}): {str(e)}")
            time.sleep(5)  # Wait 5 seconds before retry

    raise Exception(f"Failed to initialize {parser_type} parser after multiple attempts")

def get_rag_system():
    """Get or initialize RAG system with retry logic"""
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            rag = RAGSystem(
                collection_name="regulaite_docs",
                qdrant_url=QDRANT_URL,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                openai_api_key=OPENAI_API_KEY,
                llm_model="gpt-4o-mini",
                chunk_size=1024,
                chunk_overlap=200,
                vector_weight=0.7,
                semantic_weight=0.3
            )
            logger.info("RAG system initialized successfully")
            return rag
        except Exception as e:
            retry_count += 1
            logger.error(f"Failed to initialize RAG system (attempt {retry_count}/{max_retries}): {str(e)}")
            time.sleep(5)  # Wait 5 seconds before retry

    raise Exception("Failed to initialize RAG system after multiple attempts")

# Task definitions
@app.task(bind=True, name="process_document", max_retries=3)
def process_document(self, file_content_b64: str, file_name: str, doc_id: Optional[str] = None,
                    doc_metadata: Optional[Dict[str, Any]] = None, enrich: bool = True,
                    detect_language: bool = True, parser_type: str = ParserType.UNSTRUCTURED.value,
                    parser_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Process a document using the specified parser API and store in Neo4j

    Args:
        file_content_b64: Base64 encoded file content
        file_name: Name of the file
        doc_id: Optional document ID (generated if not provided)
        doc_metadata: Optional document metadata
        enrich: Whether to apply enrichment
        detect_language: Whether to detect document language
        parser_type: Type of parser to use (unstructured, unstructured_cloud, doctly, llamaparse)
        parser_settings: Optional override settings for the parser

    Returns:
        Dictionary with document ID and processing details
    """
    import base64

    try:
        # Decode base64 content
        file_content = base64.b64decode(file_content_b64)

        # Generate document ID if not provided
        if not doc_id:
            doc_id = f"doc_{uuid.uuid4()}"

        # Initialize document metadata if not provided
        if not doc_metadata:
            doc_metadata = {}

        # Add file metadata
        doc_metadata["original_filename"] = file_name
        doc_metadata["size"] = len(file_content)
        doc_metadata["processed_by"] = "celery_worker"
        doc_metadata["parser_type"] = parser_type

        # Set up specific API configurations if needed
        parser_kwargs = {
            "neo4j_uri": NEO4J_URI,
            "neo4j_user": NEO4J_USER,
            "neo4j_password": NEO4J_PASSWORD,
            "use_enrichment": True
        }

        # Add parser-specific configurations
        if parser_type == ParserType.UNSTRUCTURED.value:
            parser_kwargs["unstructured_api_url"] = UNSTRUCTURED_API_URL
            parser_kwargs["is_cloud"] = False
        elif parser_type == ParserType.UNSTRUCTURED_CLOUD.value:
            parser_kwargs["unstructured_api_url"] = UNSTRUCTURED_CLOUD_API_URL
            parser_kwargs["unstructured_api_key"] = UNSTRUCTURED_CLOUD_API_KEY
            parser_kwargs["is_cloud"] = True
        elif parser_type == ParserType.DOCTLY.value:
            parser_kwargs["doctly_api_url"] = DOCTLY_API_URL
            parser_kwargs["doctly_api_key"] = os.getenv("DOCTLY_API_KEY", "")
        elif parser_type == ParserType.LLAMAPARSE.value:
            parser_kwargs["llamaparse_api_url"] = LLAMAPARSE_API_URL
            parser_kwargs["llamaparse_api_key"] = os.getenv("LLAMAPARSE_API_KEY", "")

        # Apply custom parser settings if provided
        if parser_settings:
            logger.info(f"Applying custom parser settings: {parser_settings}")
            parser_kwargs.update(parser_settings)
            # Store the actual settings used in metadata
            doc_metadata["parser_settings_applied"] = parser_settings

        # Initialize document parser with specified type
        try:
            parser_type_enum = ParserType(parser_type)
        except ValueError:
            logger.warning(f"Invalid parser type: {parser_type}, using default: {ParserType.UNSTRUCTURED}")
            parser_type_enum = ParserType.UNSTRUCTURED

        parser = BaseParser.get_parser(
            parser_type=parser_type_enum,
            **parser_kwargs
        )

        # Process the document
        result = parser.process_document(
            file_content=file_content,
            file_name=file_name,
            doc_id=doc_id,
            doc_metadata=doc_metadata,
            enrich=enrich,
            detect_language=detect_language
        )

        # Check if document was successfully processed
        if result and "doc_id" in result:
            processed_doc_id = result["doc_id"]

            # Index document in RAG system
            try:
                # Add a delay before indexing to ensure Neo4j transaction has completed
                time.sleep(2)
                
                # Verify document exists in Neo4j before indexing
                driver = GraphDatabase.driver(
                    NEO4J_URI,
                    auth=(NEO4J_USER, NEO4J_PASSWORD)
                )
                
                document_exists = False
                with driver.session() as session:
                    verify_result = session.run(
                        "MATCH (d:Document {doc_id: $doc_id}) RETURN count(d) as count",
                        doc_id=processed_doc_id
                    )
                    record = verify_result.single()
                    document_exists = record and record["count"] > 0
                
                driver.close()
                
                if not document_exists:
                    logger.warning(f"Document {processed_doc_id} not found in Neo4j, delaying indexing")
                    result["indexed"] = False
                    result["index_error"] = "Document not yet available in Neo4j"
                    # Schedule indexing for later via bulk_index_documents
                    bulk_index_documents.apply_async(
                        args=[[processed_doc_id]], 
                        countdown=15  # Delay 15 seconds before trying again
                    )
                    return result
                
                # Now proceed with indexing since document exists
                rag_system = get_rag_system()
                index_result = rag_system.index_document(processed_doc_id)
                
                if isinstance(index_result, dict) and index_result.get("status") == "success":
                    result["indexed"] = True
                    result["vector_count"] = index_result.get("vector_count", 0)
                    logger.info(f"Document {processed_doc_id} indexed in RAG system with {index_result.get('vector_count', 0)} vectors")
                elif index_result is True:
                    result["indexed"] = True
                    logger.info(f"Document {processed_doc_id} indexed in RAG system")
                else:
                    result["indexed"] = False
                    result["index_error"] = "Unknown indexing result"
                    logger.warning(f"Document {processed_doc_id} indexing returned unexpected result: {index_result}")
            except Exception as e:
                logger.error(f"Error indexing document in RAG system: {str(e)}", exc_info=True)
                result["indexed"] = False
                result["index_error"] = str(e)
                # Continue without failing

        # Clean up
        parser.close()

        return result
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        self.retry(exc=e, countdown=30, max_retries=3)  # Retry after 30 seconds, up to 3 times

@app.task(bind=True, name="execute_agent_task", max_retries=2)
def execute_agent_task(self, agent_type: str, task: str, config: Optional[Dict[str, Any]] = None,
                      include_context: bool = True, context_query: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a task using an AI agent

    Args:
        agent_type: Type of agent to use
        task: Task description
        config: Optional agent configuration
        include_context: Whether to include RAG context
        context_query: Query to use for retrieving context

    Returns:
        Dictionary with agent execution results
    """
    try:
        # Generate agent ID
        agent_id = f"{agent_type}_{uuid.uuid4()}"
        
        # Initialize RAG system
        rag_system = get_rag_system()
        
        # Since pyndantic_agents is removed, we need an alternative approach
        # Using direct LLM calls via RAG system
        query = f"Task: {task}\nAgent type: {agent_type}"
        
        if include_context and context_query:
            context = rag_system.retrieve(context_query or task, top_k=5)
            context_str = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(context)])
            query = f"{context_str}\n\n{query}"
            
        # Use RAG system's query method directly
        result = rag_system.query(query)
        
        # Clean up
        rag_system.close()

        return {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "task": task,
            "result": str(result),
            "status": "completed"
        }
    except Exception as e:
        logger.error(f"Error executing agent task: {str(e)}")
        self.retry(exc=e, countdown=20, max_retries=2)

@app.task(bind=True, name="bulk_index_documents", max_retries=3)
def bulk_index_documents(self, doc_ids: List[str]) -> Dict[str, Any]:
    """
    Index multiple documents in the RAG system

    Args:
        doc_ids: List of document IDs to index

    Returns:
        Dictionary with indexing results
    """
    try:
        # Initialize RAG system
        rag_system = get_rag_system()

        # Track results
        results = {
            "successful": [],
            "failed": []
        }

        # Process each document
        for doc_id in doc_ids:
            try:
                index_result = rag_system.index_document(doc_id)
                
                if isinstance(index_result, dict):
                    if index_result.get("status") == "success":
                        results["successful"].append({
                            "doc_id": doc_id,
                            "vector_count": index_result.get("vector_count", 0),
                            "message": "Successfully indexed"
                        })
                    elif "vector_count" in index_result and index_result.get("vector_count", 0) > 0:
                        results["successful"].append({
                            "doc_id": doc_id,
                            "vector_count": index_result.get("vector_count", 0),
                            "message": index_result.get("message", "Indexed successfully")
                        })
                    elif index_result.get("message") == "Document already indexed":
                        results["successful"].append({
                            "doc_id": doc_id,
                            "vector_count": 0,
                            "message": "Document was already indexed"
                        })
                    else:
                        logger.warning(f"Indexing completed but with issues for {doc_id}: {index_result}")
                        results["failed"].append({
                            "doc_id": doc_id,
                            "error": f"Indexing issue: {index_result.get('message', 'Unknown issue')}"
                        })
                elif index_result:
                    results["successful"].append({
                        "doc_id": doc_id,
                        "message": "Indexing reported success"
                    })
                else:
                    results["failed"].append({
                        "doc_id": doc_id,
                        "error": "Indexing returned False"
                    })
            except Exception as e:
                logger.error(f"Error indexing document {doc_id}: {str(e)}")
                results["failed"].append({
                    "doc_id": doc_id,
                    "error": str(e)
                })

        # Clean up
        rag_system.close()

        return {
            "status": "completed",
            "total": len(doc_ids),
            "successful": len(results["successful"]),
            "failed": len(results["failed"]),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in bulk document indexing: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=3)

@app.task(bind=True, name="retrieve_context", max_retries=2)
def retrieve_context(self, query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Retrieve context from RAG system

    Args:
        query: Search query
        top_k: Number of results to return

    Returns:
        Dictionary with retrieved context
    """
    try:
        # Initialize RAG system
        rag_system = get_rag_system()

        # Retrieve context
        results = rag_system.retrieve(query, top_k=top_k)

        # Clean up
        rag_system.close()

        return {
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        self.retry(exc=e, countdown=15, max_retries=2)

@app.task(name="check_unindexed_documents")
def check_unindexed_documents():
    """Check for unindexed documents and schedule them for indexing"""
    try:
        # Connect to Neo4j
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

        # Find unindexed documents - use is_indexed property instead of indexed
        with driver.session() as session:
            result = session.run(
                """
                MATCH (d:Document)
                WHERE COALESCE(d.is_indexed, false) = false
                RETURN d.doc_id as doc_id, 
                       COALESCE(d.title, d.name, 'Untitled') as title, 
                       COALESCE(d.language, 'en') as language
                LIMIT 100
                """
            )

            unindexed_docs = [(record["doc_id"], record.get("language", "en")) for record in result]
            
            # Group documents by language
            language_groups = {}
            for doc_id, language in unindexed_docs:
                lang = language if language else "en"
                if lang not in language_groups:
                    language_groups[lang] = []
                language_groups[lang].append(doc_id)
            
        # Close Neo4j connection
        driver.close()

        # Initialize RAG system to initialize languages
        rag_system = get_rag_system()
        
        # Make sure all needed languages are initialized
        for lang in language_groups.keys():
            try:
                rag_system.ensure_language_initialized(lang)
                logger.info(f"Initialized language {lang} for indexing")
            except Exception as e:
                logger.error(f"Failed to initialize language {lang}: {str(e)}")
        
        # Clean up RAG system
        rag_system.close()
        
        indexed_count = 0
        for lang, docs in language_groups.items():
            if docs:
                logger.info(f"Found {len(docs)} unindexed documents for language {lang}. Scheduling for indexing.")
                # Schedule bulk indexing task
                bulk_index_documents.delay(doc_ids=docs)
                indexed_count += len(docs)

        if indexed_count > 0:
            return {
                "status": "success",
                "unindexed_documents": indexed_count,
                "language_groups": {k: len(v) for k, v in language_groups.items()},
                "doc_ids": [doc_id for doc_id, _ in unindexed_docs]
            }
        else:
            logger.info("No unindexed documents found.")
            return {
                "status": "success",
                "unindexed_documents": 0,
                "doc_ids": []
            }
    except Exception as e:
        logger.error(f"Error checking for unindexed documents: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# Optional: Celery beat tasks for scheduled operations
app.conf.beat_schedule = {
    'check-unindexed-documents': {
        'task': 'check_unindexed_documents',
        'schedule': 600.0,  # Every 10 minutes (changed from 3600.0)
    },
}
