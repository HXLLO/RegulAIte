import os
import uuid
import logging
import time
import datetime
import types
import requests
import json
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import qdrant_client
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, OptimizersConfigDiff
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from llama_index.core import Document, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.text_splitter import TokenTextSplitter
from llama_index.core.schema import TextNode
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore

# Set up logging
logger = logging.getLogger("hype_rag")

class HyPERagSystem:
    """
    Hypothetical Document Embedding (HyPE) RAG System
    
    This system enhances retrieval by generating hypothetical questions for documents
    and using them as proxies for retrieval.
    """
    
    def __init__(
        self,
        collection_name: str = "regulaite_documents",
        metadata_collection_name: str = "regulaite_metadata",
        qdrant_url: str = "http://regulaite-qdrant:6333",
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        openai_api_key: Optional[str] = None,
        llm_model: str = "gpt-4o-mini",
        chunk_size: int = 2048,
        chunk_overlap: int = 200,
        hypothetical_questions_per_chunk: int = 5,
        vector_weight: float = 0.75,
        semantic_weight: float = 0.25,
        max_workers: int = 4,
        qdrant_batch_size: int = 50,
        qdrant_timeout: float = 120.0
    ):
        """
        Initialize the HyPE RAG System
        """
        self.collection_name = collection_name
        self.metadata_collection_name = metadata_collection_name
        self.qdrant_url = qdrant_url
        self.embedding_model_name = embedding_model
        self.llm_model = llm_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.hypothetical_questions_per_chunk = hypothetical_questions_per_chunk
        self.vector_weight = vector_weight
        self.semantic_weight = semantic_weight
        self.max_workers = max_workers
        self.qdrant_batch_size = qdrant_batch_size
        self.qdrant_timeout = qdrant_timeout
        
        # Set OpenAI API key from environment if not provided
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key must be provided or set in environment")
        
        # Initialize embedding model
        logger.info(f"Initializing embedding model: {embedding_model}")
        self.embedding_model = HuggingFaceEmbedding(model_name=embedding_model)
        
        # Get embedding dimension by creating a test embedding
        test_embedding = self.embedding_model.get_text_embedding("test")
        self.embedding_dim = len(test_embedding)
        logger.info(f"Embedding dimension: {self.embedding_dim}")
        
        # Initialize Qdrant client
        logger.info(f"Connecting to Qdrant at {qdrant_url}")
        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            timeout=self.qdrant_timeout,
            grpc_port=6334,
            prefer_grpc=True
        )
        
        # Create vector store
        self._ensure_collection_exists()
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=collection_name,
        )
        
        # Set up LLM for question generation
        self.llm = ChatOpenAI(temperature=0, model=llm_model, api_key=self.openai_api_key)
        
        # Configure llama_index settings
        Settings.llm = OpenAI(model=llm_model, api_key=self.openai_api_key)
        Settings.embed_model = self.embedding_model
        Settings.chunk_size = self.chunk_size
        Settings.chunk_overlap = self.chunk_overlap
        
        # Initialize hybrid search retriever
        self._init_retrievers()
        
        # Set up prompt for generating hypothetical questions
        self.question_gen_prompt = PromptTemplate.from_template(
            "Analyse le texte ci-dessous et génère {num_questions} questions précises qui permettraient de "
            "reconstituer fidèlement son contenu si elles recevaient des réponses. Les questions doivent être "
            "informatives, ciblées sur les faits clés, les entités nommées et les relations importantes du texte. "
            "Formule chaque question de manière concise, sur une seule ligne, sans numérotation ni préambule.\n\n"
            "Exemple :\n"
            "Texte :\n"
            "Gestion des exceptions\n"
            "Neo Financia reconnaît que des exceptions temporaires à la PSSI peuvent être nécessaires dans certaines circonstances. "
            "Ces exceptions sont encadrées par un processus formel:\n"
            "1. Soumission d'une demande d'exception documentée incluant :\n"
            "- Description de l'exception\n"
            "- Justification business\n"
            "- Évaluation des risques\n"
            "- Mesures compensatoires proposées\n"
            "- Durée prévue\n"
            "2. Analyse et avis du RSS\n\n"
            "Questions :\n"
            "Quelle organisation reconnaît la nécessité d'exceptions temporaires à la PSSI ?\n"
            "Dans quel contexte des exceptions à la PSSI peuvent-elles être accordées chez Neo Financia ?\n"
            "Quel document doit être soumis pour demander une exception à la PSSI ?\n"
            "Quels éléments doivent figurer dans la demande d'exception à la PSSI ?\n"
            "Quel rôle joue le RSS dans le processus de gestion des exceptions ?\n"
            "Quelle est la durée typique prévue pour une exception à la PSSI chez Neo Financia ?\n"
            "Pourquoi une justification business est-elle requise dans une demande d'exception à la PSSI ?\n"
            "Quelles mesures sont attendues pour compenser les risques liés à une exception ?\n\n"
            "Texte :\n{chunk_text}\n\n"
            "Questions :\n"
        )
        self.question_chain = self.question_gen_prompt | self.llm | StrOutputParser()
        
        logger.info("HyPE RAG System initialized successfully")
    
    def _batch_upsert_with_retry(self, collection_name: str, points: List[PointStruct], batch_size: int = 100, max_retries: int = 3) -> int:
        """
        Upsert points in batches with retry logic to handle timeouts.
        
        Args:
            collection_name: Name of the collection to upsert to
            points: List of points to upsert
            batch_size: Number of points to upsert in each batch
            max_retries: Maximum number of retries per batch
            
        Returns:
            Number of successfully upserted points
        """
        total_upserted = 0
        total_points = len(points)
        
        logger.info(f"Starting batch upsert of {total_points} points in batches of {batch_size}")
        
        for i in range(0, total_points, batch_size):
            batch_points = points[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_points + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches}: {len(batch_points)} points")
            
            for attempt in range(max_retries):
                try:
                    start_time = time.time()
                    self.qdrant_client.upsert(
                        collection_name=collection_name,
                        points=batch_points
                    )
                    
                    upsert_time = time.time() - start_time
                    total_upserted += len(batch_points)
                    logger.info(f"Batch {batch_num}/{total_batches} completed successfully in {upsert_time:.2f}s ({len(batch_points)} points)")
                    break  # Success, move to next batch
                    
                except Exception as e:
                    attempt_num = attempt + 1
                    if attempt_num < max_retries:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Batch {batch_num}/{total_batches} failed on attempt {attempt_num}/{max_retries}: {str(e)}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Batch {batch_num}/{total_batches} failed after {max_retries} attempts: {str(e)}")
                        # Continue with next batch instead of failing completely
                        continue
        
        logger.info(f"Batch upsert completed: {total_upserted}/{total_points} points successfully upserted")
        return total_upserted
    
    def _ensure_collection_exists(self):
        """Ensure that the collection exists in Qdrant, or create it with the correct dimension"""
        try:
            collections_to_check = [
                self.collection_name,
                self.metadata_collection_name
            ]
            
            for collection_name in collections_to_check:
                # Check if collection exists
                if self.qdrant_client.collection_exists(collection_name):
                    logger.info(f"Collection {collection_name} already exists")
                    
                    # Get collection info to check the vector dimension
                    try:
                        collection_info = self.qdrant_client.get_collection(collection_name)
                        current_vector_config = collection_info.config.params.vectors
                        
                        # Check if the vector dimension doesn't match our embedding dimension
                        if current_vector_config.size != self.embedding_dim:
                            logger.warning(f"Vector dimension mismatch in {collection_name}: Collection has {current_vector_config.size} but current embedding is {self.embedding_dim}")
                            logger.warning(f"Recreating collection {collection_name} with correct dimension")
                            
                            # Delete the existing collection
                            self.qdrant_client.delete_collection(collection_name)
                            
                            # Create a new collection with the correct dimension and optimized indexing
                            self.qdrant_client.create_collection(
                                collection_name=collection_name,
                                vectors_config=VectorParams(
                                    size=self.embedding_dim,
                                    distance=Distance.COSINE
                                ),
                                optimizers_config=OptimizersConfigDiff(
                                    indexing_threshold=1000,  # Index vectors after 1000 points instead of 20000
                                    max_indexing_threads=4,
                                    flush_interval_sec=5
                                )
                            )
                            logger.info(f"Collection {collection_name} recreated with dimension {self.embedding_dim} and optimized indexing")
                    except Exception as e:
                        logger.error(f"Error checking vector dimensions for {collection_name}: {str(e)}")
                        # If we can't check dimensions, recreate the collection to be safe
                        logger.warning(f"Recreating collection {collection_name} with correct dimension")
                        
                        # Delete the existing collection
                        self.qdrant_client.delete_collection(collection_name)
                        
                        # Create a new collection with the correct dimension and optimized indexing
                        self.qdrant_client.create_collection(
                            collection_name=collection_name,
                            vectors_config=VectorParams(
                                size=self.embedding_dim,
                                distance=Distance.COSINE
                            ),
                            optimizers_config=OptimizersConfigDiff(
                                indexing_threshold=1000,  # Index vectors after 1000 points instead of 20000
                                max_indexing_threads=4,
                                flush_interval_sec=5
                            )
                        )
                        logger.info(f"Collection {collection_name} recreated with dimension {self.embedding_dim} and optimized indexing")
                else:
                    logger.info(f"Creating collection {collection_name}")
                    
                    # Create collection with proper schema and optimized indexing
                    self.qdrant_client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=self.embedding_dim,
                            distance=Distance.COSINE
                        ),
                        optimizers_config=OptimizersConfigDiff(
                            indexing_threshold=1000,  # Index vectors after 1000 points instead of 20000
                            max_indexing_threads=4,
                            flush_interval_sec=5
                        )
                    )
                    
                    logger.info(f"Collection {collection_name} created successfully with optimized indexing")
                
            return True
        except Exception as e:
            logger.error(f"Error ensuring collections exist: {str(e)}")
            return False
    
    def _init_retrievers(self):
        """Initialize the retrievers for hybrid search"""
        try:
            # Initialize vector retriever with vector store
            self.vector_retriever = self.vector_store
            
            # Initialize BM25 retriever with a proper default document
            from llama_index.retrievers.bm25 import BM25Retriever
            from llama_index.core.schema import NodeWithScore, Node
            
            # We won't initialize BM25 immediately - defer until we have actual documents
            # This avoids the "max() arg is an empty sequence" error
            logger.info("Setting up deferred BM25 initialization")
            self.bm25_retriever = None
            self.bm25_initialized = False
            
            # Store nodes for BM25 indexing
            self.bm25_nodes = []
            
            # Define a method to lazily initialize BM25 when needed
            def init_bm25_with_nodes(self):
                if not self.bm25_initialized and self.bm25_nodes:
                    try:
                        # Filter out nodes with empty or very short text content
                        valid_nodes = []
                        for node in self.bm25_nodes:
                            if hasattr(node, 'text') and node.text and len(node.text.strip()) >= 10:
                                valid_nodes.append(node)
                            else:
                                logger.debug(f"Filtering out node with insufficient text: {getattr(node, 'id_', 'unknown')}")
                        
                        if len(valid_nodes) < 5:
                            logger.warning(f"Not enough valid nodes for BM25 initialization ({len(valid_nodes)} valid nodes, need at least 5)")
                            return False
                        
                        logger.info(f"Initializing BM25 retriever with {len(valid_nodes)} valid nodes (filtered from {len(self.bm25_nodes)} total)")
                        self.bm25_retriever = BM25Retriever.from_defaults(
                            nodes=valid_nodes,
                            similarity_top_k=50
                        )
                        self.bm25_initialized = True
                        logger.info("BM25 retriever initialized successfully")
                        return True
                    except Exception as e:
                        logger.warning(f"Error initializing BM25 retriever with nodes: {str(e)}")
                        # Log more details for debugging
                        if self.bm25_nodes:
                            sample_texts = []
                            for i, node in enumerate(self.bm25_nodes[:5]):
                                text_preview = getattr(node, 'text', 'NO_TEXT')[:100] if hasattr(node, 'text') else 'NO_TEXT_ATTR'
                                sample_texts.append(f"Node {i}: {text_preview}")
                            logger.debug(f"Sample node texts: {sample_texts}")
                        return False
                return self.bm25_initialized
            
            # Attach the method to the instance
            self.init_bm25_with_nodes = types.MethodType(init_bm25_with_nodes, self)
            
            logger.info(f"Initialized retriever with vector_weight={self.vector_weight}, semantic_weight={self.semantic_weight}")
            return True
        except Exception as e:
            logger.error(f"Error initializing retrievers: {str(e)}")
            return False
    
    def generate_hypothetical_questions(self, chunk_text: str) -> List[str]:
        """
        Generate hypothetical questions for a document chunk using LLM
        """
        try:
            # Log the start of question generation
            question_start_time = time.time()
            chunk_preview = chunk_text[:50] + "..." if len(chunk_text) > 50 else chunk_text
            logger.info(f"Generating {self.hypothetical_questions_per_chunk} questions for chunk: {chunk_preview}")
            
            # Generate questions
            response = self.question_chain.invoke({
                "chunk_text": chunk_text,
                "num_questions": self.hypothetical_questions_per_chunk
            })
            
            # Parse questions from response
            questions = response.strip().replace("\n\n", "\n").split("\n")
            
            # Filter out any empty questions
            questions = [q.strip() for q in questions if q.strip()]
            
            # Log the generated questions
            question_time = time.time() - question_start_time
            logger.info(f"Generated {len(questions)} questions in {question_time:.2f}s")
            for i, question in enumerate(questions):
                logger.debug(f"Question {i+1}: {question}")
            
            return questions
        except Exception as e:
            logger.error(f"Error generating hypothetical questions: {str(e)}")
            # Log the stack trace for debugging
            import traceback
            logger.error(f"Question generation traceback: {traceback.format_exc()}")
            # Return a basic question in case of error
            return [f"De quoi parle ce texte: {chunk_text[:50]}..."]
    
    def process_and_index_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process and index a document with hypothetical questions
        
        IMPORTANT: This method now directly inserts into Qdrant instead of using QdrantVectorStore
        to have full control over the payload structure.
        """
        start_time = time.time()
        logger.info(f"Processing document {doc_id} with HyPE RAG")
        total_chars = len(content)
        logger.info(f"Document {doc_id} size: {total_chars} characters")
        
        total_vectors_indexed_for_doc = 0
        total_questions_indexed_for_doc = 0
        successfully_processed_chunks = 0

        try:
            base_metadata = metadata or {}
            base_metadata["doc_id"] = doc_id
            base_metadata["processed_timestamp"] = datetime.datetime.now().isoformat()
            
            splitter = TokenTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            chunks = splitter.split_text(content)
            total_chunks_in_document = len(chunks)
            logger.info(f"Document {doc_id} split into {total_chunks_in_document} chunks (chunk_size={self.chunk_size}, overlap={self.chunk_overlap})")
            
            if not chunks:
                logger.warning(f"Document {doc_id} resulted in 0 chunks. No processing will occur.")
                processing_time = time.time() - start_time
                return {
                    "status": "success_no_chunks",
                    "doc_id": doc_id,
                    "message": "Document was empty or too small to create chunks.",
                    "total_chunks_in_doc": 0,
                    "processed_chunk_count": 0,
                    "vector_count": 0,
                    "question_count": 0,
                    "processing_time": processing_time
                }

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for i, chunk_text in enumerate(chunks):
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata["chunk_id"] = f"{doc_id}_chunk_{i}"
                    chunk_metadata["chunk_index"] = i
                    chunk_metadata["total_chunks"] = total_chunks_in_document
                    
                    logger.debug(f"Submitting chunk {i+1}/{total_chunks_in_document} for processing")
                    futures.append(
                        executor.submit(
                            self._process_and_index_chunk,
                            chunk_text,
                            chunk_metadata
                        )
                    )
                
                logger.info(f"Waiting for {len(futures)} chunk processing tasks to complete for document {doc_id}")
                for i, future in enumerate(as_completed(futures)):
                    try:
                        vectors_added, questions_added = future.result()
                        if vectors_added > 0:
                            successfully_processed_chunks += 1
                        total_vectors_indexed_for_doc += vectors_added
                        total_questions_indexed_for_doc += questions_added
                        logger.debug(f"Completed chunk task {i+1}/{len(futures)}: {vectors_added} vectors, {questions_added} questions")
                    except Exception as e:
                        logger.error(f"A chunk processing task for doc {doc_id} failed at future level: {str(e)}")
            
            processing_time = time.time() - start_time
            logger.info(f"Document {doc_id} processed in {processing_time:.2f} seconds.")
            logger.info(f"Summary for {doc_id}: {successfully_processed_chunks}/{total_chunks_in_document} chunks processed successfully.")
            logger.info(f"Total vectors indexed for {doc_id}: {total_vectors_indexed_for_doc}")
            logger.info(f"Total questions indexed for {doc_id}: {total_questions_indexed_for_doc}")
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "total_chunks_in_doc": total_chunks_in_document,
                "processed_chunk_count": successfully_processed_chunks,
                "vector_count": total_vectors_indexed_for_doc,
                "question_count": total_questions_indexed_for_doc,
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Major error during processing of document {doc_id} after {processing_time:.2f}s: {str(e)}")
            import traceback
            logger.error(f"Document processing traceback for {doc_id}: {traceback.format_exc()}")
            return {
                "status": "error",
                "doc_id": doc_id,
                "error": str(e),
                "total_chunks_in_doc": total_chunks_in_document,
                "processed_chunk_count": successfully_processed_chunks,
                "vector_count": total_vectors_indexed_for_doc,
                "question_count": total_questions_indexed_for_doc,
                "processing_time": processing_time
            }
    
    def _process_and_index_chunk(self, chunk_text: str, metadata: Dict[str, Any]) -> Tuple[int, int]:
        """
        Process and index a single document chunk with hypothetical questions.
        
        This method now directly inserts points into Qdrant to ensure proper payload structure.
        """
        num_vectors_added_for_chunk = 0
        questions_indexed_for_chunk = 0
        node_id = "unknown_node"

        try:
            chunk_start_time = time.time()
            doc_id = metadata.get("doc_id", "unknown")
            chunk_index = metadata.get("chunk_index", 0)
            node_id = f"{doc_id}_chunk_{chunk_index}"
            logger.info(f"Processing chunk {node_id}")

            points_to_add = []

            # 1. Create point for the chunk itself
            chunk_embedding = self.embedding_model.get_text_embedding(chunk_text)
            chunk_point_id = str(uuid.uuid4())
            
            # Prepare payload for chunk
            chunk_payload = {
                "node_id": node_id,
                "doc_id": doc_id,
                "chunk_id": chunk_point_id,
                "chunk_index": chunk_index,
                "text": chunk_text,
                "text_content_type": "chunk",
                "is_question": False,  # Explicitly mark as not a question
                "metadata": metadata.copy()
            }
            
            chunk_point = PointStruct(
                id=chunk_point_id,
                vector=chunk_embedding,
                payload=chunk_payload
            )
            points_to_add.append(chunk_point)
            logger.debug(f"Prepared chunk point {chunk_point_id}")

            # Also add to BM25 nodes
            if self.bm25_nodes is not None:
                try:
                    from llama_index.core.schema import Node
                    # Only add to BM25 if chunk has meaningful text content
                    if chunk_text and len(chunk_text.strip()) >= 10:
                        bm25_chunk_node = Node(
                            text=chunk_text,
                            metadata=metadata.copy(),
                            id_=node_id
                        )
                        self.bm25_nodes.append(bm25_chunk_node)
                    else:
                        logger.debug(f"Skipping BM25 node for chunk {node_id} - insufficient text content")
                except Exception as bm25_error:
                    logger.warning(f"Error preparing BM25 node for chunk {node_id}: {str(bm25_error)}")

            # 2. Generate hypothetical questions and create points for them
            questions = self.generate_hypothetical_questions(chunk_text)
            logger.info(f"Generated {len(questions)} questions for chunk {node_id}")

            for i, question_text in enumerate(questions):
                question_embedding = self.embedding_model.get_text_embedding(question_text)
                question_point_id = str(uuid.uuid4())
                question_node_id = f"{node_id}-q{i}"

                # Prepare payload for question
                question_payload = {
                    "node_id": question_node_id,
                    "doc_id": doc_id,
                    "chunk_id": chunk_point_id,  # Reference to parent chunk
                    "parent_chunk_id": chunk_point_id,
                    "parent_node_id": node_id,
                    "chunk_index": chunk_index,
                    "text": question_text,  # The actual question text
                    "original_chunk_text": chunk_text,  # Keep reference to original chunk
                    "text_content_type": "question",
                    "is_question": True,  # Explicitly mark as a question
                    "question_index": i,
                    "metadata": metadata.copy()
                }

                question_point = PointStruct(
                    id=question_point_id,
                    vector=question_embedding,
                    payload=question_payload
                )
                points_to_add.append(question_point)
                logger.debug(f"Prepared question point {question_point_id}: {question_text[:50]}...")

                # Also add to BM25 nodes
                if self.bm25_nodes is not None:
                    try:
                        # For BM25, we use the chunk text but with question metadata
                        from llama_index.core.schema import Node
                        bm25_question_metadata = metadata.copy()
                        bm25_question_metadata["is_question"] = True
                        bm25_question_metadata["question"] = question_text
                        bm25_question_metadata["question_index"] = i
                        bm25_question_metadata["parent_id"] = node_id
                        
                        # Only add to BM25 if chunk has meaningful text content
                        if chunk_text and len(chunk_text.strip()) >= 10:
                            bm25_question_node = Node(
                                text=chunk_text,  # BM25 searches on chunk text
                                metadata=bm25_question_metadata,
                                id_=question_node_id
                            )
                            self.bm25_nodes.append(bm25_question_node)
                        else:
                            logger.debug(f"Skipping BM25 node for question {question_node_id} - insufficient chunk text content")
                    except Exception as bm25_q_error:
                        logger.warning(f"Error preparing BM25 node for question {question_node_id}: {str(bm25_q_error)}")
                
                questions_indexed_for_chunk += 1
            
            # Insert all points directly into Qdrant
            if points_to_add:
                num_vectors_added_for_chunk = self._batch_upsert_with_retry(
                    collection_name=self.collection_name,
                    points=points_to_add,
                    batch_size=self.qdrant_batch_size,
                    max_retries=3
                )
                logger.info(f"Added {num_vectors_added_for_chunk} points (1 chunk, {questions_indexed_for_chunk} questions) to Qdrant for chunk {node_id}")
            else:
                logger.info(f"No points to add to Qdrant for chunk {node_id}")

            # Initialize BM25 if we have enough nodes
            if self.bm25_nodes is not None and not self.bm25_initialized and len(self.bm25_nodes) >= 5:
                logger.info(f"Sufficient nodes ({len(self.bm25_nodes)}) collected, attempting to initialize BM25.")
                self.init_bm25_with_nodes()

            chunk_processing_time = time.time() - chunk_start_time
            logger.info(f"Finished processing chunk {node_id}: added {questions_indexed_for_chunk} questions, {num_vectors_added_for_chunk} total vectors in {chunk_processing_time:.2f}s")
            return num_vectors_added_for_chunk, questions_indexed_for_chunk
            
        except Exception as e:
            error_node_id_ref = node_id if node_id != "unknown_node" else f"{metadata.get('doc_id', 'unknown_doc')}_chunk_{metadata.get('chunk_index', 'unknown_idx')}"
            logger.error(f"Error processing chunk {error_node_id_ref}: {str(e)}")
            import traceback
            logger.error(f"Chunk processing traceback for {error_node_id_ref}: {traceback.format_exc()}")
            return 0, 0
    
    def process_existing_chunks(self, doc_id: str) -> Dict[str, Any]:
        """
        Process existing document chunks to generate hypothetical questions.
        This method is designed to work with chunks already stored by unstructured_parser.
        
        Args:
            doc_id: Document ID whose chunks should be processed
            
        Returns:
            Result of processing operation
        """
        start_time = time.time()
        total_questions_generated = 0
        total_chunks_processed = 0
        
        try:
            logger.info(f"Processing existing chunks for document {doc_id} with HyPE")
            
            # Use HTTP API directly to scroll through chunks
            chunks = []
            offset = None
            
            # Scroll through all chunks for this document
            while True:
                scroll_data = {
                    "filter": {
                        "must": [
                            {"key": "doc_id", "match": {"value": doc_id}}
                        ]
                    },
                    "limit": 100,
                    "with_payload": True,
                    "with_vector": False
                }
                
                if offset:
                    scroll_data["offset"] = offset
                
                # Direct API call to Qdrant
                response = requests.post(
                    f"{self.qdrant_url}/collections/{self.collection_name}/points/scroll",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(scroll_data)
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to scroll: {response.text}")
                    break
                
                result = response.json()
                points = result.get("result", {}).get("points", [])
                
                if not points:
                    break
                
                chunks.extend(points)
                
                offset = result.get("result", {}).get("next_page_offset")
                
                if not offset:
                    break
            
            if not chunks:
                logger.warning(f"No chunks found for document {doc_id}")
                return {
                    "status": "error",
                    "doc_id": doc_id,
                    "error": "No chunks found",
                    "chunks_processed": 0,
                    "questions_generated": 0
                }
            
            logger.info(f"Found {len(chunks)} existing chunks for document {doc_id}")
            
            # Process each chunk to generate questions
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                
                for chunk_data in chunks:
                    # Skip if this is already a question
                    if chunk_data.get("payload", {}).get("is_question", False):
                        logger.debug(f"Skipping chunk {chunk_data['id']} - already a question")
                        continue
                    
                    chunk_text = chunk_data.get("payload", {}).get("text", "")
                    chunk_metadata = chunk_data.get("payload", {}).get("metadata", {})
                    chunk_id = chunk_data["id"]
                    
                    # Ensure doc_id is in metadata
                    chunk_metadata["doc_id"] = doc_id
                    chunk_metadata["original_chunk_id"] = chunk_id
                    
                    futures.append(
                        executor.submit(
                            self._generate_and_store_questions,
                            chunk_text,
                            chunk_id,
                            chunk_metadata
                        )
                    )
                
                # Wait for all processing to complete
                for future in as_completed(futures):
                    try:
                        questions_count = future.result()
                        if questions_count > 0:
                            total_chunks_processed += 1
                            total_questions_generated += questions_count
                    except Exception as e:
                        logger.error(f"Error processing chunk: {str(e)}")
            
            processing_time = time.time() - start_time
            logger.info(f"Processed {total_chunks_processed} chunks for document {doc_id} in {processing_time:.2f}s")
            logger.info(f"Generated {total_questions_generated} questions total")
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "chunks_processed": total_chunks_processed,
                "questions_generated": total_questions_generated,
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing existing chunks for {doc_id}: {str(e)}")
            import traceback
            logger.error(f"Processing traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "doc_id": doc_id,
                "error": str(e),
                "chunks_processed": total_chunks_processed,
                "questions_generated": total_questions_generated,
                "processing_time": processing_time
            }

    def _generate_and_store_questions(self, chunk_text: str, chunk_id: str, metadata: Dict[str, Any]) -> int:
        """
        Generate hypothetical questions for a chunk and store them in Qdrant.
        
        Args:
            chunk_text: Text content of the chunk
            chunk_id: ID of the original chunk
            metadata: Metadata for the chunk
            
        Returns:
            Number of questions generated and stored
        """
        try:
            logger.info(f"Generating questions for chunk {chunk_id}")
            
            # Generate hypothetical questions
            questions = self.generate_hypothetical_questions(chunk_text)
            logger.info(f"Generated {len(questions)} questions for chunk {chunk_id}")
            
            if not questions:
                return 0
            
            # Create points for each question
            question_points = []
            
            for i, question_text in enumerate(questions):
                question_embedding = self.embedding_model.get_text_embedding(question_text)
                question_point_id = str(uuid.uuid4())
                
                # Prepare payload for question
                question_payload = {
                    "node_id": f"{chunk_id}-q{i}",
                    "doc_id": metadata.get("doc_id"),
                    "parent_chunk_id": chunk_id,
                    "chunk_id": chunk_id,  # Reference to parent chunk
                    "text": question_text,  # The actual question text
                    "original_chunk_text": chunk_text,  # Keep reference to original chunk
                    "text_content_type": "question",
                    "is_question": True,  # CRITICAL: Mark as a question
                    "question_index": i,
                    "metadata": metadata.copy()
                }
                
                question_point = PointStruct(
                    id=question_point_id,
                    vector=question_embedding,
                    payload=question_payload
                )
                question_points.append(question_point)
                logger.debug(f"Prepared question point {question_point_id}: {question_text[:50]}...")
            
            # Store all question points in Qdrant
            if question_points:
                num_stored = self._batch_upsert_with_retry(
                    collection_name=self.collection_name,
                    points=question_points,
                    batch_size=self.qdrant_batch_size,
                    max_retries=3
                )
                logger.info(f"Stored {num_stored} questions for chunk {chunk_id}")
                return num_stored
                
            return 0
            
        except Exception as e:
            logger.error(f"Error generating questions for chunk {chunk_id}: {str(e)}")
            import traceback
            logger.error(f"Question generation traceback: {traceback.format_exc()}")
            return 0

    def index_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Index a document by processing its existing chunks to generate questions
        
        Args:
            doc_id: Document ID to index
            
        Returns:
            Result of indexing operation
        """
        try:
            logger.info(f"Indexing document {doc_id}")
            
            # Process existing chunks to generate questions
            result = self.process_existing_chunks(doc_id)
            
            # Return compatible result format
            return {
                "status": result["status"],
                "doc_id": doc_id,
                "vector_count": result.get("questions_generated", 0),
                "message": f"Generated {result.get('questions_generated', 0)} questions from {result.get('chunks_processed', 0)} chunks"
            }
            
        except Exception as e:
            logger.error(f"Error indexing document {doc_id}: {str(e)}")
            return {
                "status": "error",
                "doc_id": doc_id,
                "error": str(e),
                "vector_count": 0
            }
    
    def retrieve(self, query: str, top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks using hybrid search.
        
        This implements proper HyPE RAG: search both questions and chunks for better retrieval,
        but always return the original chunk content.
        """
        try:
            logger.info(f"Retrieving documents for query: {query}")
            
            # Step 1: Vector search through Qdrant client directly
            query_embedding = self.embedding_model.get_text_embedding(query)
            
            # Prepare search parameters - search both questions AND chunks
            search_params = {
                "collection_name": self.collection_name,
                "query_vector": query_embedding,
                "limit": top_k * 2,  # Get more results to account for deduplication
                "with_payload": True
            }
            
            # Convert API filters to Qdrant format if provided
            base_filter_conditions = []
            if filters:
                qdrant_filter = self._convert_filters_to_qdrant(filters)
                if qdrant_filter and qdrant_filter.get("must"):
                    base_filter_conditions.extend(qdrant_filter["must"])
            
            # Apply the combined filter (DO NOT filter out questions - we want both!)
            if base_filter_conditions:
                search_params["query_filter"] = {"must": base_filter_conditions}
            
            # Check if BM25 should be initialized before retrieval        
            if not self.bm25_initialized and len(self.bm25_nodes) >= 5:
                logger.info("Attempting to initialize BM25 before retrieval")
                self.init_bm25_with_nodes()
                    
            # Execute search
            logger.info("Performing vector search (including both questions and chunks for better retrieval)")
            results = self.qdrant_client.search(**search_params)
            
            # Process results: convert questions to their original chunks and deduplicate
            documents = []
            seen_chunks = set()  # Track chunks we've already added
            
            for result in results:
                payload = result.payload
                is_question = payload.get("is_question", False)
                
                if is_question:
                    # This is a question - extract the original chunk information
                    original_chunk_text = payload.get("original_chunk_text", "")
                    doc_id = payload.get("doc_id", "")
                    chunk_index = payload.get("chunk_index", 0)
                    parent_chunk_id = payload.get("parent_chunk_id", "")
                    
                    # Create a unique identifier for this chunk to avoid duplicates
                    chunk_identifier = f"{doc_id}_chunk_{chunk_index}"
                    
                    if chunk_identifier not in seen_chunks and original_chunk_text:
                        # Create a document entry using the original chunk content
                        doc = {
                            "node_id": payload.get("parent_node_id", chunk_identifier),
                            "doc_id": doc_id,
                            "chunk_id": parent_chunk_id or payload.get("chunk_id", ""),
                            "chunk_index": chunk_index,
                            "text": original_chunk_text,  # Use original chunk text, not question
                            "text_content_type": "chunk",  # Mark as chunk content
                            "is_question": False,  # Mark as chunk, not question
                            "metadata": payload.get("metadata", {}),
                            "score": result.score,
                            "matched_via": "question"  # Indicate this was found via question match
                        }
                        documents.append(doc)
                        seen_chunks.add(chunk_identifier)
                        logger.debug(f"Added chunk via question match: {chunk_identifier} (score: {result.score:.4f})")
                else:
                    # This is a regular chunk
                    doc_id = payload.get("doc_id", "")
                    chunk_index = payload.get("chunk_index", 0)
                    chunk_identifier = f"{doc_id}_chunk_{chunk_index}"
                    
                    if chunk_identifier not in seen_chunks:
                        # Add the chunk as-is
                        doc = payload.copy()
                        doc["score"] = result.score
                        doc["matched_via"] = "chunk"  # Indicate this was found via direct chunk match
                        documents.append(doc)
                        seen_chunks.add(chunk_identifier)
                        logger.debug(f"Added chunk via direct match: {chunk_identifier} (score: {result.score:.4f})")
                
                # Stop if we have enough unique chunks
                if len(documents) >= top_k:
                    break
            
            # Sort by score (descending) and limit to requested top_k
            documents = sorted(documents, key=lambda x: x.get("score", 0), reverse=True)[:top_k]
            
            # Enrich documents with metadata from the metadata collection
            documents = self._enrich_documents_with_metadata(documents)
            
            logger.info(f"Retrieved {len(documents)} unique document chunks from vector search (questions helped improve retrieval)")
            
            # Log some stats about how chunks were found
            chunk_matches = sum(1 for doc in documents if doc.get("matched_via") == "chunk")
            question_matches = sum(1 for doc in documents if doc.get("matched_via") == "question")
            logger.info(f"Retrieval breakdown: {chunk_matches} direct chunk matches, {question_matches} via question matches")
            
            # Log BM25 status for debugging
            if self.bm25_initialized:
                logger.debug("BM25 is available for hybrid search")
            else:
                logger.debug(f"BM25 not available (initialized: {self.bm25_initialized}, nodes: {len(self.bm25_nodes) if self.bm25_nodes else 0})")
            
            return documents
                
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            import traceback
            logger.error(f"Retrieval traceback: {traceback.format_exc()}")
            raise
    
    def _enrich_documents_with_metadata(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich retrieved documents with metadata from the metadata collection.
        
        Args:
            documents: List of document chunks retrieved from the main collection
            
        Returns:
            List of documents enriched with metadata (filename, title, etc.)
        """
        if not documents:
            return documents
            
        try:
            # Get unique document IDs from the retrieved documents
            doc_ids = list(set(doc.get("doc_id") for doc in documents if doc.get("doc_id")))
            
            if not doc_ids:
                logger.warning("No document IDs found in retrieved documents")
                return documents
            
            logger.debug(f"Enriching documents with metadata for doc_ids: {doc_ids}")
            
            # Fetch metadata for all document IDs in one query
            metadata_map = {}
            
            for doc_id in doc_ids:
                try:
                    # Search for document metadata using proper Qdrant filter
                    metadata_results = self.qdrant_client.scroll(
                        collection_name=self.metadata_collection_name,
                        scroll_filter=qdrant_client.models.Filter(
                            must=[
                                qdrant_client.models.FieldCondition(
                                    key="doc_id",
                                    match=qdrant_client.models.MatchValue(value=doc_id)
                                )
                            ]
                        ),
                        limit=1,
                        with_payload=True,
                        with_vectors=False
                    )
                    
                    if metadata_results and len(metadata_results[0]) > 0:
                        metadata_payload = metadata_results[0][0].payload
                        metadata_map[doc_id] = metadata_payload
                        logger.debug(f"Found metadata for doc_id {doc_id}: title={metadata_payload.get('title', 'N/A')}")
                    else:
                        logger.debug(f"No metadata found for doc_id {doc_id}")
                        
                except Exception as e:
                    logger.warning(f"Error fetching metadata for doc_id {doc_id}: {str(e)}")
                    continue
            
            # Enrich each document with its metadata
            enriched_documents = []
            for doc in documents:
                doc_id = doc.get("doc_id")
                if doc_id in metadata_map:
                    doc_metadata = metadata_map[doc_id]
                    
                    # Add essential metadata fields for frontend display
                    doc["title"] = doc_metadata.get("title", f"Document {doc_id[:8]}")
                    doc["filename"] = doc_metadata.get("name", doc_metadata.get("original_filename", f"Document {doc_id[:8]}"))
                    doc["original_filename"] = doc_metadata.get("original_filename", "")
                    doc["file_type"] = doc_metadata.get("file_type", "")
                    doc["category"] = doc_metadata.get("category", "Uncategorized")
                    doc["language"] = doc_metadata.get("language", "en")
                    doc["author"] = doc_metadata.get("author", "")
                    doc["created_at"] = doc_metadata.get("created_at", "")
                    doc["size"] = doc_metadata.get("size", 0)
                    doc["page_count"] = doc_metadata.get("page_count", 0)
                    
                    logger.debug(f"Enriched document {doc_id} with filename: {doc['filename']}")
                else:
                    logger.debug(f"No metadata found for doc_id {doc_id}, using defaults")
                    # Provide default values to avoid "unknown" display
                    doc["title"] = f"Document {doc_id[:8]}" if doc_id else "Unknown Document"
                    doc["filename"] = f"Document {doc_id[:8]}" if doc_id else "Unknown Document"
                    doc["original_filename"] = ""
                    doc["file_type"] = ""
                    doc["category"] = "Uncategorized"
                    doc["language"] = "en"
                    doc["author"] = ""
                    doc["created_at"] = ""
                    doc["size"] = 0
                    doc["page_count"] = 0
                
                enriched_documents.append(doc)
            
            logger.info(f"Successfully enriched {len(enriched_documents)} documents with metadata")
            return enriched_documents
            
        except Exception as e:
            logger.error(f"Error enriching documents with metadata: {str(e)}")
            import traceback
            logger.error(f"Metadata enrichment traceback: {traceback.format_exc()}")
            # Return original documents if enrichment fails
            return documents

    def _convert_filters_to_qdrant(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert API filters to Qdrant filter format
        
        Now properly handles the flat payload structure where is_question is a top-level field.
        """
        if not filters:
            return None
            
        # Basic filter conversion
        qdrant_filter = {"must": []}
        
        for key, value in filters.items():
            if key == "date_range":
                # Handle date range filter
                date_range = value
                if "start" in date_range:
                    qdrant_filter["must"].append({
                        "range": {
                            "metadata.date": {
                                "gte": date_range["start"]
                            }
                        }
                    })
                if "end" in date_range:
                    qdrant_filter["must"].append({
                        "range": {
                            "metadata.date": {
                                "lte": date_range["end"]
                            }
                        }
                    })
            elif isinstance(value, list):
                # Handle list values (OR condition)
                should_conditions = []
                for val in value:
                    should_conditions.append({
                        "key": key,
                        "match": {"value": val}
                    })
                if should_conditions:
                    qdrant_filter["must"].append({"should": should_conditions})
            else:
                # Handle simple key-value match
                # All fields are now at the top level in our new structure
                qdrant_filter["must"].append({
                    "key": key,
                    "match": {"value": value}
                })
                
        # Log the created filter for debugging
        logger.debug(f"Created Qdrant filter: {qdrant_filter}")
        
        return qdrant_filter if qdrant_filter["must"] else None
    
    def close(self):
        """Clean up resources"""
        # Any cleanup needed
        pass

    def _get_timestamp(self):
        """Get the current timestamp as datetime object"""
        return datetime.datetime.now()
        
    def ensure_language_initialized(self, language_code: str):
        """
        Ensure the language model for a specific language is initialized
        """
        try:
            # In this implementation, no special language initialization is needed
            # All languages are supported by the embedding model
            logger.info(f"Language {language_code} support checked")
            return True
        except Exception as e:
            logger.error(f"Error initializing language {language_code}: {str(e)}")
            return False

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and its vectors from the system with improved robustness
        """
        try:
            logger.info(f"Deleting document {doc_id}")
            
            # Track deletion counts for reporting
            total_deleted = 0
            
            # First, let's see what we're about to delete
            for collection in [self.collection_name, self.metadata_collection_name]:
                try:
                    # Count existing points before deletion using proper Qdrant filter format
                    count_filter = qdrant_client.models.Filter(
                        must=[
                            qdrant_client.models.FieldCondition(
                                key="doc_id",
                                match=qdrant_client.models.MatchValue(value=doc_id)
                            )
                        ]
                    )
                    
                    count_result = self.qdrant_client.count(
                        collection_name=collection,
                        count_filter=count_filter
                    )
                    
                    existing_count = count_result.count if hasattr(count_result, 'count') else 0
                    logger.info(f"Found {existing_count} vectors for document {doc_id} in collection {collection}")
                    
                    if existing_count > 0:
                        # Delete document chunks from this collection using proper filter format
                        filter_doc_chunks = qdrant_client.models.Filter(
                            must=[
                                qdrant_client.models.FieldCondition(
                                    key="doc_id",
                                    match=qdrant_client.models.MatchValue(value=doc_id)
                                )
                            ]
                        )
                        
                        # Perform the deletion
                        result = self.qdrant_client.delete(
                            collection_name=collection,
                            points_selector=qdrant_client.models.FilterSelector(
                                filter=filter_doc_chunks
                            )
                        )
                        
                        # Check if the deletion was successful
                        if hasattr(result, 'operation_id'):
                            logger.info(f"Successfully initiated deletion from {collection} with operation_id: {result.operation_id}")
                            total_deleted += existing_count
                        else:
                            logger.warning(f"Deletion result from {collection} didn't return operation_id: {result}")
                            
                    else:
                        logger.info(f"No vectors found for document {doc_id} in collection {collection}")
                        
                except Exception as e:
                    logger.error(f"Error deleting from collection {collection}: {str(e)}")
                    # Continue with next collection
                    continue
            
            # Additional cleanup: check for any orphaned vectors that might have doc_id in metadata
            try:
                logger.info(f"Checking for orphaned vectors with doc_id in metadata for {doc_id}")
                
                # Alternative filter for doc_id in metadata (fallback for older data) using proper format
                alt_filter = qdrant_client.models.Filter(
                    must=[
                        qdrant_client.models.FieldCondition(
                            key="metadata.doc_id",
                            match=qdrant_client.models.MatchValue(value=doc_id)
                        )
                    ]
                )
                
                for collection in [self.collection_name, self.metadata_collection_name]:
                    try:
                        count_result = self.qdrant_client.count(
                            collection_name=collection,
                            count_filter=alt_filter
                        )
                        
                        alt_count = count_result.count if hasattr(count_result, 'count') else 0
                        
                        if alt_count > 0:
                            logger.info(f"Found {alt_count} additional vectors with doc_id in metadata for {doc_id} in {collection}")
                            
                            result = self.qdrant_client.delete(
                                collection_name=collection,
                                points_selector=qdrant_client.models.FilterSelector(
                                    filter=alt_filter
                                )
                            )
                            
                            if hasattr(result, 'operation_id'):
                                logger.info(f"Successfully deleted orphaned vectors from {collection}")
                                total_deleted += alt_count
                                
                    except Exception as e:
                        logger.warning(f"Error checking/deleting orphaned vectors from {collection}: {str(e)}")
                        
            except Exception as e:
                logger.warning(f"Error during orphaned vector cleanup: {str(e)}")
            
            # Clean up BM25 nodes if they exist
            if hasattr(self, 'bm25_nodes') and self.bm25_nodes:
                try:
                    initial_count = len(self.bm25_nodes)
                    # Remove nodes related to this document
                    self.bm25_nodes = [
                        node for node in self.bm25_nodes 
                        if not (hasattr(node, 'metadata') and node.metadata.get('doc_id') == doc_id)
                    ]
                    removed_count = initial_count - len(self.bm25_nodes)
                    if removed_count > 0:
                        logger.info(f"Removed {removed_count} BM25 nodes for document {doc_id}")
                        # Re-initialize BM25 if we still have nodes
                        if len(self.bm25_nodes) >= 10:
                            self.bm25_initialized = False
                            self.init_bm25_with_nodes()
                except Exception as e:
                    logger.warning(f"Error cleaning up BM25 nodes: {str(e)}")
            
            if total_deleted > 0:
                logger.info(f"Successfully deleted document {doc_id} - removed {total_deleted} total vectors")
                return True
            else:
                logger.warning(f"Document {doc_id} not found or no vectors were deleted")
                return False
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            import traceback
            logger.error(f"Delete document traceback: {traceback.format_exc()}")
            return False

    def delete_all_documents(self) -> Dict[str, Any]:
        """
        Delete all documents from both collections (nuclear option)
        
        Returns:
            Dict with deletion results
        """
        try:
            logger.warning("Deleting ALL documents from vector store - this cannot be undone!")
            
            total_deleted = 0
            results = {}
            
            for collection in [self.collection_name, self.metadata_collection_name]:
                try:
                    # Count existing points
                    count_result = self.qdrant_client.count(collection_name=collection)
                    existing_count = count_result.count if hasattr(count_result, 'count') else 0
                    
                    logger.info(f"Found {existing_count} total vectors in collection {collection}")
                    
                    if existing_count > 0:
                        # Delete all points in the collection
                        # We'll recreate the collection to ensure it's completely clean
                        
                        # First, get collection info
                        collection_info = self.qdrant_client.get_collection(collection)
                        vector_config = collection_info.config.params.vectors
                        
                        # Delete the collection
                        self.qdrant_client.delete_collection(collection)
                        logger.info(f"Deleted collection {collection}")
                        
                        # Recreate the collection with the same configuration
                        self.qdrant_client.create_collection(
                            collection_name=collection,
                            vectors_config=qdrant_client.models.VectorParams(
                                size=vector_config.size,
                                distance=vector_config.distance
                            )
                        )
                        logger.info(f"Recreated collection {collection}")
                        
                        results[collection] = {
                            "deleted_count": existing_count,
                            "status": "success"
                        }
                        total_deleted += existing_count
                    else:
                        results[collection] = {
                            "deleted_count": 0,
                            "status": "empty"
                        }
                        
                except Exception as e:
                    logger.error(f"Error deleting all documents from collection {collection}: {str(e)}")
                    results[collection] = {
                        "deleted_count": 0,
                        "status": f"error: {str(e)}"
                    }
            
            # Clean up BM25 nodes
            if hasattr(self, 'bm25_nodes'):
                self.bm25_nodes = []
                self.bm25_initialized = False
                logger.info("Cleared BM25 nodes")
            
            logger.info(f"Bulk deletion completed - removed {total_deleted} total vectors")
            
            return {
                "status": "success",
                "total_deleted": total_deleted,
                "collections": results,
                "message": f"Successfully deleted {total_deleted} vectors from all collections"
            }
            
        except Exception as e:
            logger.error(f"Error during bulk deletion: {str(e)}")
            import traceback
            logger.error(f"Bulk deletion traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "error": str(e),
                "total_deleted": 0
            }

    def get_document_count(self) -> Dict[str, Any]:
        """
        Get count of documents and vectors in the system
        
        Returns:
            Dict with counts per collection
        """
        try:
            counts = {}
            total_vectors = 0
            
            for collection in [self.collection_name, self.metadata_collection_name]:
                try:
                    count_result = self.qdrant_client.count(collection_name=collection)
                    count = count_result.count if hasattr(count_result, 'count') else 0
                    counts[collection] = count
                    total_vectors += count
                    logger.info(f"Collection {collection}: {count} vectors")
                except Exception as e:
                    logger.error(f"Error counting vectors in {collection}: {str(e)}")
                    counts[collection] = f"error: {str(e)}"
            
            # Count unique documents by doc_id
            unique_docs = 0
            try:
                # Scroll through main collection to count unique doc_ids
                offset = None
                doc_ids = set()
                
                while True:
                    scroll_data = {
                        "limit": 100,
                        "with_payload": True,
                        "with_vector": False
                    }
                    
                    if offset:
                        scroll_data["offset"] = offset
                    
                    response = requests.post(
                        f"{self.qdrant_url}/collections/{self.collection_name}/points/scroll",
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(scroll_data)
                    )
                    
                    if response.status_code != 200:
                        break
                    
                    result = response.json()
                    points = result.get("result", {}).get("points", [])
                    
                    if not points:
                        break
                    
                    for point in points:
                        doc_id = point.get("payload", {}).get("doc_id")
                        if doc_id:
                            doc_ids.add(doc_id)
                    
                    offset = result.get("result", {}).get("next_page_offset")
                    if not offset:
                        break
                
                unique_docs = len(doc_ids)
                
            except Exception as e:
                logger.error(f"Error counting unique documents: {str(e)}")
                unique_docs = "error"
            
            return {
                "total_vectors": total_vectors,
                "unique_documents": unique_docs,
                "collections": counts,
                "bm25_nodes": len(self.bm25_nodes) if hasattr(self, 'bm25_nodes') and self.bm25_nodes else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return {
                "error": str(e),
                "total_vectors": 0,
                "unique_documents": 0
            }

    def process_parsed_document(self, parsed_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document that has already been parsed by the DocumentParser.
        This method takes the parsed chunks and stores them with HyPE enhancement.
        
        Args:
            parsed_result: Result from DocumentParser.process_document() containing:
                - doc_id: Document ID
                - chunks: List of parsed and enriched chunks
                - metadata: Document metadata
                - content: Raw content text
                - file_name: Original filename
                
        Returns:
            Result of processing operation
        """
        start_time = time.time()
        
        try:
            doc_id = parsed_result.get("doc_id")
            chunks = parsed_result.get("chunks", [])
            metadata = parsed_result.get("metadata", {})
            content = parsed_result.get("content", "")
            file_name = parsed_result.get("file_name", "unknown")
            
            if not doc_id:
                raise ValueError("No doc_id provided in parsed_result")
                
            logger.info(f"Processing parsed document {doc_id} with {len(chunks)} chunks using HyPE RAG")
            
            # If we have pre-parsed chunks, store them and generate questions
            if chunks:
                return self._process_parsed_chunks(doc_id, chunks, metadata)
            elif content:
                # Fallback: if no chunks but we have content, process as raw content
                logger.info(f"No chunks provided, processing raw content for {doc_id}")
                return self.process_and_index_document(doc_id, content, metadata)
            else:
                raise ValueError("No chunks or content provided in parsed_result")
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing parsed document: {str(e)}")
            import traceback
            logger.error(f"Processing traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": processing_time
            }
    
    def _process_parsed_chunks(self, doc_id: str, chunks: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process pre-parsed chunks and store them with HyPE enhancement.
        
        Args:
            doc_id: Document ID
            chunks: List of parsed chunks with embeddings
            metadata: Document metadata
            
        Returns:
            Result of processing operation
        """
        start_time = time.time()
        total_vectors_indexed = 0
        total_questions_generated = 0
        successfully_processed_chunks = 0
        
        try:
            logger.info(f"Processing {len(chunks)} pre-parsed chunks for document {doc_id}")
            
            base_metadata = metadata.copy() if metadata else {}
            base_metadata["doc_id"] = doc_id
            base_metadata["processed_timestamp"] = datetime.datetime.now().isoformat()
            
            points_to_add = []
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                
                for i, chunk in enumerate(chunks):
                    chunk_text = chunk.get("text", "")
                    if not chunk_text:
                        logger.warning(f"Skipping empty chunk {i} for document {doc_id}")
                        continue
                    
                    # Prepare chunk metadata
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata.update(chunk.get("metadata", {}))
                    chunk_metadata["chunk_index"] = i
                    chunk_metadata["total_chunks"] = len(chunks)
                    
                    # Use existing chunk_id or generate new one
                    chunk_id = chunk.get("chunk_id")
                    if not chunk_id:
                        chunk_id = str(uuid.uuid4())
                    elif not isinstance(chunk_id, str):
                        chunk_id = str(chunk_id)
                    
                    futures.append(
                        executor.submit(
                            self._process_parsed_chunk,
                            chunk_text,
                            chunk_id,
                            chunk_metadata,
                            chunk.get("embedding", [])
                        )
                    )
                
                # Wait for all processing to complete
                for i, future in enumerate(as_completed(futures)):
                    try:
                        chunk_points, questions_count = future.result()
                        if chunk_points:
                            points_to_add.extend(chunk_points)
                            successfully_processed_chunks += 1
                            total_questions_generated += questions_count
                            logger.debug(f"Processed chunk {i+1}/{len(futures)}: {len(chunk_points)} points, {questions_count} questions")
                    except Exception as e:
                        logger.error(f"Error processing chunk {i}: {str(e)}")
            
            # Batch insert all points
            if points_to_add:
                total_vectors_indexed = self._batch_upsert_with_retry(
                    collection_name=self.collection_name,
                    points=points_to_add,
                    batch_size=self.qdrant_batch_size,
                    max_retries=3
                )
                logger.info(f"Stored {total_vectors_indexed} vectors for document {doc_id}")
            
            # Store document metadata in the metadata collection for frontend display
            self._store_document_metadata(doc_id, base_metadata, len(chunks), total_questions_generated)
            
            # Initialize BM25 if we have enough nodes
            if self.bm25_nodes is not None and not self.bm25_initialized and len(self.bm25_nodes) >= 5:
                logger.info(f"Sufficient nodes ({len(self.bm25_nodes)}) collected, attempting to initialize BM25.")
                self.init_bm25_with_nodes()
            
            processing_time = time.time() - start_time
            logger.info(f"Processed parsed document {doc_id} in {processing_time:.2f} seconds")
            logger.info(f"Summary: {successfully_processed_chunks}/{len(chunks)} chunks processed successfully")
            logger.info(f"Total vectors indexed: {total_vectors_indexed}")
            logger.info(f"Total questions generated: {total_questions_generated}")
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "total_chunks": len(chunks),
                "processed_chunk_count": successfully_processed_chunks,
                "vector_count": total_vectors_indexed,
                "question_count": total_questions_generated,
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing parsed chunks for {doc_id}: {str(e)}")
            import traceback
            logger.error(f"Parsed chunks processing traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "doc_id": doc_id,
                "error": str(e),
                "total_chunks": len(chunks),
                "processed_chunk_count": successfully_processed_chunks,
                "vector_count": total_vectors_indexed,
                "question_count": total_questions_generated,
                "processing_time": processing_time
            }
    
    def _process_parsed_chunk(self, chunk_text: str, chunk_id: str, metadata: Dict[str, Any], embedding: List[float] = None) -> Tuple[List[PointStruct], int]:
        """
        Process a single pre-parsed chunk and generate hypothetical questions.
        
        Args:
            chunk_text: Text content of the chunk
            chunk_id: ID of the chunk
            metadata: Metadata for the chunk
            embedding: Pre-computed embedding (optional)
            
        Returns:
            Tuple of (list of points to add, number of questions generated)
        """
        points_to_add = []
        questions_generated = 0
        
        try:
            chunk_start_time = time.time()
            doc_id = metadata.get("doc_id", "unknown")
            chunk_index = metadata.get("chunk_index", 0)
            node_id = f"{doc_id}_chunk_{chunk_index}"
            
            logger.debug(f"Processing parsed chunk {node_id}")
            
            # 1. Create point for the chunk itself using provided or generated embedding
            if embedding and len(embedding) > 0:
                chunk_embedding = embedding
            else:
                chunk_embedding = self.embedding_model.get_text_embedding(chunk_text)
            
            # Prepare payload for chunk
            chunk_payload = {
                "node_id": node_id,
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "chunk_index": chunk_index,
                "text": chunk_text,
                "text_content_type": "chunk",
                "is_question": False,  # Explicitly mark as not a question
                "metadata": metadata.copy()
            }
            
            chunk_point = PointStruct(
                id=chunk_id,
                vector=chunk_embedding,
                payload=chunk_payload
            )
            points_to_add.append(chunk_point)
            
            # Also add to BM25 nodes
            if self.bm25_nodes is not None:
                try:
                    from llama_index.core.schema import Node
                    # Only add to BM25 if chunk has meaningful text content
                    if chunk_text and len(chunk_text.strip()) >= 10:
                        bm25_chunk_node = Node(
                            text=chunk_text,
                            metadata=metadata.copy(),
                            id_=node_id
                        )
                        self.bm25_nodes.append(bm25_chunk_node)
                    else:
                        logger.debug(f"Skipping BM25 node for chunk {node_id} - insufficient text content")
                except Exception as bm25_error:
                    logger.warning(f"Error preparing BM25 node for chunk {node_id}: {str(bm25_error)}")
            
            # 2. Generate hypothetical questions
            questions = self.generate_hypothetical_questions(chunk_text)
            logger.debug(f"Generated {len(questions)} questions for chunk {node_id}")
            
            for i, question_text in enumerate(questions):
                question_embedding = self.embedding_model.get_text_embedding(question_text)
                question_point_id = str(uuid.uuid4())
                question_node_id = f"{node_id}-q{i}"
                
                # Prepare payload for question
                question_payload = {
                    "node_id": question_node_id,
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,  # Reference to parent chunk
                    "parent_chunk_id": chunk_id,
                    "parent_node_id": node_id,
                    "chunk_index": chunk_index,
                    "text": question_text,  # The actual question text
                    "original_chunk_text": chunk_text,  # Keep reference to original chunk
                    "text_content_type": "question",
                    "is_question": True,  # Explicitly mark as a question
                    "question_index": i,
                    "metadata": metadata.copy()
                }
                
                question_point = PointStruct(
                    id=question_point_id,
                    vector=question_embedding,
                    payload=question_payload
                )
                points_to_add.append(question_point)
                
                # Also add to BM25 nodes
                if self.bm25_nodes is not None:
                    try:
                        from llama_index.core.schema import Node
                        bm25_question_metadata = metadata.copy()
                        bm25_question_metadata["is_question"] = True
                        bm25_question_metadata["question"] = question_text
                        bm25_question_metadata["question_index"] = i
                        bm25_question_metadata["parent_id"] = node_id
                        
                        # Only add to BM25 if chunk has meaningful text content
                        if chunk_text and len(chunk_text.strip()) >= 10:
                            bm25_question_node = Node(
                                text=chunk_text,  # BM25 searches on chunk text
                                metadata=bm25_question_metadata,
                                id_=question_node_id
                            )
                            self.bm25_nodes.append(bm25_question_node)
                        else:
                            logger.debug(f"Skipping BM25 node for question {question_node_id} - insufficient chunk text content")
                    except Exception as bm25_q_error:
                        logger.warning(f"Error preparing BM25 node for question {question_node_id}: {str(bm25_q_error)}")
                
                questions_generated += 1
            
            chunk_processing_time = time.time() - chunk_start_time
            logger.debug(f"Processed parsed chunk {node_id}: {questions_generated} questions, {len(points_to_add)} total points in {chunk_processing_time:.2f}s")
            
            return points_to_add, questions_generated
            
        except Exception as e:
            logger.error(f"Error processing parsed chunk {chunk_id}: {str(e)}")
            import traceback
            logger.error(f"Parsed chunk processing traceback: {traceback.format_exc()}")
            return [], 0

    def _store_document_metadata(self, doc_id: str, metadata: Dict[str, Any], total_chunks: int, total_questions: int):
        """
        Store document metadata in the metadata collection for frontend display
        """
        try:
            logger.info(f"Storing document metadata for {doc_id}")
            
            # Prepare comprehensive metadata for storage that frontend expects
            metadata_to_store = {
                "doc_id": doc_id,
                "title": metadata.get("title", metadata.get("original_filename", f"Document {doc_id[:8]}")),
                "name": metadata.get("original_filename", f"Document {doc_id[:8]}"),
                "original_filename": metadata.get("original_filename", ""),
                "is_indexed": True,  # Document is being indexed right now
                "file_type": metadata.get("file_type", metadata.get("filetype", "")),
                "description": metadata.get("description", ""),
                "language": metadata.get("language", "en"),
                "size": metadata.get("size", 0),
                "page_count": metadata.get("page_count", 0),
                "chunk_count": total_chunks,
                "created_at": metadata.get("created_at") or datetime.datetime.now().isoformat(),
                "uploaded_at": metadata.get("uploaded_at") or datetime.datetime.now().isoformat(),
                "processed_timestamp": metadata.get("processed_timestamp"),
                "tags": metadata.get("tags", []),
                "category": metadata.get("category", "Uncategorized"),
                "author": metadata.get("author", ""),
                "status": "active",
                "total_questions": total_questions,
                "parser_type": metadata.get("parser_type", "unstructured"),
                "use_nlp": metadata.get("use_nlp", False),
                "use_enrichment": metadata.get("use_enrichment", False)
            }
            
            # Store metadata in the metadata collection
            self.qdrant_client.upsert(
                collection_name=self.metadata_collection_name,
                points=[
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=self.embedding_model.get_text_embedding(json.dumps(metadata_to_store, default=str)),
                        payload=metadata_to_store
                    )
                ]
            )
            
            logger.info(f"Stored comprehensive document metadata for {doc_id} in metadata collection")
            
        except Exception as e:
            logger.error(f"Error storing document metadata for {doc_id}: {str(e)}")
            import traceback
            logger.error(f"Metadata storage traceback: {traceback.format_exc()}")