#!/usr/bin/env python3
"""
Example script showing how to use the refactored document processing pipeline.

This demonstrates the separation of concerns:
1. DocumentParser handles only parsing and chunking
2. HyPERagSystem handles storage with hypothetical question enhancement
"""

import os
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from unstructured_parser.document_parser import DocumentParser
from rag.hype_rag import HyPERagSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_document_with_pipeline(file_path: str, doc_id: str = None) -> dict:
    """
    Example function showing the complete document processing pipeline.
    
    Args:
        file_path: Path to the document file
        doc_id: Optional document ID
        
    Returns:
        Processing result
    """
    
    # Step 1: Initialize the document parser (parsing only)
    logger.info("Initializing DocumentParser...")
    parser = DocumentParser(
        chunk_size=1000,
        chunk_overlap=200,
        chunking_strategy="token",
        extract_tables=True,
        extract_metadata=True
    )
    
    # Step 2: Initialize the HyPE RAG system (storage with enhancement)
    logger.info("Initializing HyPERagSystem...")
    rag_system = HyPERagSystem(
        collection_name="regulaite_docs",
        metadata_collection_name="regulaite_metadata",
        qdrant_url="http://regulaite-qdrant:6333",
        hypothetical_questions_per_chunk=5,
        vector_weight=0.75,
        semantic_weight=0.25
    )
    
    try:
        # Step 3: Read the document file
        logger.info(f"Reading document: {file_path}")
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        file_name = os.path.basename(file_path)
        
        # Step 4: Parse the document (no storage)
        logger.info("Parsing document with DocumentParser...")
        parse_result = parser.process_document(
            file_content=file_content,
            file_name=file_name,
            doc_id=doc_id,
            doc_metadata={
                "source": "example_pipeline",
                "file_path": file_path,
                "category": "example"
            }
        )
        
        logger.info(f"Parsing completed: {parse_result['chunk_count']} chunks generated")
        
        # Step 5: Store with HyPE enhancement
        logger.info("Storing with HyPE RAG enhancement...")
        storage_result = rag_system.process_parsed_document(parse_result)
        
        logger.info(f"Storage completed: {storage_result.get('vector_count', 0)} vectors stored, "
                   f"{storage_result.get('question_count', 0)} questions generated")
        
        # Step 6: Test retrieval
        logger.info("Testing retrieval...")
        test_query = "What is this document about?"
        retrieved_docs = rag_system.retrieve(test_query, top_k=3)
        
        logger.info(f"Retrieved {len(retrieved_docs)} documents for test query")
        
        return {
            "parse_result": parse_result,
            "storage_result": storage_result,
            "test_retrieval": retrieved_docs,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in document processing pipeline: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
    
    finally:
        # Clean up resources
        parser.close()
        rag_system.close()

def process_raw_content_with_pipeline(content: str, doc_id: str = None) -> dict:
    """
    Example function for processing raw text content.
    
    Args:
        content: Raw text content
        doc_id: Optional document ID
        
    Returns:
        Processing result
    """
    
    # Initialize HyPE RAG system only (for raw content processing)
    logger.info("Initializing HyPERagSystem for raw content...")
    rag_system = HyPERagSystem(
        collection_name="regulaite_docs",
        metadata_collection_name="regulaite_metadata",
        qdrant_url="http://regulaite-qdrant:6333",
        hypothetical_questions_per_chunk=3,
        chunk_size=800,
        chunk_overlap=150
    )
    
    try:
        # Process raw content directly with HyPE RAG
        logger.info("Processing raw content with HyPE RAG...")
        result = rag_system.process_and_index_document(
            doc_id=doc_id or "raw_content_doc",
            content=content,
            metadata={
                "source": "raw_content",
                "category": "example",
                "content_type": "text"
            }
        )
        
        logger.info(f"Raw content processing completed: {result.get('vector_count', 0)} vectors stored")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing raw content: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
    
    finally:
        rag_system.close()

if __name__ == "__main__":
    # Example usage
    
    # Test with a document file (if available)
    example_file = "/path/to/your/document.pdf"  # Change this to a real file path
    
    if len(sys.argv) > 1:
        example_file = sys.argv[1]
    
    if os.path.exists(example_file):
        logger.info(f"Processing document file: {example_file}")
        result = process_document_with_pipeline(example_file)
        print(f"Document processing result: {result['status']}")
    else:
        logger.info("No document file found, testing with raw content...")
        
        # Test with raw content
        test_content = """
        This is an example document about artificial intelligence and machine learning.
        
        Machine learning is a subset of artificial intelligence that focuses on algorithms
        that can learn and improve from experience without being explicitly programmed.
        
        There are several types of machine learning:
        1. Supervised learning - learning with labeled examples
        2. Unsupervised learning - finding patterns in unlabeled data
        3. Reinforcement learning - learning through interaction and feedback
        
        Natural language processing is another important area of AI that deals with
        understanding and generating human language.
        """
        
        result = process_raw_content_with_pipeline(test_content, "example_ml_doc")
        print(f"Raw content processing result: {result['status']}") 