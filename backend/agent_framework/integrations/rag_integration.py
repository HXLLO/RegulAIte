"""
RAG Integration for the RegulAIte Agent Framework.

This module provides integration with the existing RAG system.
"""
from typing import Dict, List, Optional, Any, Union, Set
import logging
import json
import sys
import os
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

class RAGIntegration:
    """
    Integration with the existing RAG system.
    
    This class provides a bridge between the Agent Framework and the
    existing RAG system.
    """
    
    def __init__(self, query_engine=None, rag_system=None, use_query_expansion=False):
        """
        Initialize the RAG integration.
        
        Args:
            query_engine: An existing QueryEngine instance to use
            rag_system: An existing RAG system instance to use
            use_query_expansion: Whether to enable query expansion for better retrieval
        """
        self.query_engine = query_engine
        self.rag_system = rag_system
        self.use_query_expansion = use_query_expansion
        
        # Initialize query expansion if enabled
        self.query_expander = None
        if self.use_query_expansion:
            try:
                from ..tools.query_expansion import get_query_expander
                self.query_expander = get_query_expander()
                logger.info("Query expansion initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize query expansion: {str(e)}")
                self.use_query_expansion = False
        
        if self.query_engine is None and self.rag_system is None:
            logger.warning("RAG integration initialized without query engine or RAG system")
                
    async def retrieve(self, query: str, top_k: int = 5, search_filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve relevant documents from the RAG system.
        
        Args:
            query: The query to retrieve documents for
            top_k: Maximum number of documents to retrieve
            search_filter: Optional filter for the search
            
        Returns:
            Dictionary with retrieval results and sources
        """
        # Check if we have a query engine or RAG system available
        if self.query_engine is None and self.rag_system is None:
            logger.error("Cannot retrieve documents: Neither RAG query engine nor RAG system is initialized")
            return {"results": [], "sources": []}
            
        try:
            logger.info(f"Retrieving documents for query: {query}")
            
            # Apply query expansion if enabled
            queries_to_search = [query]
            expansion_info = None
            
            if self.use_query_expansion and self.query_expander:
                try:
                    expansion_result = await self.query_expander.expand_query(
                        query, 
                        strategy="balanced",
                        max_expansions=5
                    )
                    
                    if expansion_result.expanded_terms:
                        # Create expanded query variations
                        expanded_query = f"{query} {' '.join(expansion_result.expanded_terms[:3])}"
                        queries_to_search.append(expanded_query)
                        
                        expansion_info = {
                            "original_query": query,
                            "expanded_terms": expansion_result.expanded_terms,
                            "confidence_score": expansion_result.confidence_score,
                            "framework_terms": expansion_result.framework_terms
                        }
                        
                        logger.info(
                            f"Query expanded with {len(expansion_result.expanded_terms)} terms, "
                            f"confidence: {expansion_result.confidence_score:.2f}"
                        )
                    else:
                        logger.info("No expansion terms found for query")
                        
                except Exception as e:
                    logger.warning(f"Query expansion failed, using original query: {str(e)}")
            
            # Perform retrieval with all query variations
            all_results = []
            seen_doc_ids = set()
            
            for search_query in queries_to_search:
                logger.debug(f"Searching with query: {search_query}")
                
                # First try using the query engine if available
                if self.query_engine is not None:
                    # Call the query engine with the appropriate parameters
                    if hasattr(self.query_engine, 'retrieve'):
                        # If the query engine has a retrieve method, use it
                        retrieval_result = await self.query_engine.retrieve(
                            search_query, 
                            top_k=top_k, 
                            search_filter=search_filter
                        )
                        
                        # Process and deduplicate results
                        processed_result = self._process_retrieval_result(retrieval_result)
                        self._merge_results(all_results, processed_result, seen_doc_ids)
                        
                    elif hasattr(self.query_engine, 'query'):
                        # If the query engine only has a query method, use it
                        # and extract the context used for the response
                        query_result = await self.query_engine.query(
                            search_query,
                            top_k=top_k,
                            search_filter=search_filter
                        )
                        
                        # Process and deduplicate results
                        processed_result = self._process_query_result(query_result)
                        self._merge_results(all_results, processed_result, seen_doc_ids)
                        
                    else:
                        logger.warning("RAG query engine does not have retrieve or query methods, trying RAG system")
                
                # If query engine is not available or doesn't work, try using RAG system directly
                if self.rag_system is not None and not all_results:
                    if hasattr(self.rag_system, 'retrieve'):
                        # Use RAG system retrieve method
                        retrieval_result = self.rag_system.retrieve(search_query, top_k=top_k)
                        processed_result = self._process_retrieval_result(retrieval_result)
                        self._merge_results(all_results, processed_result, seen_doc_ids)
                        
                    elif hasattr(self.rag_system, 'search'):
                        # Use RAG system search method
                        search_result = self.rag_system.search(search_query, limit=top_k)
                        processed_result = self._process_retrieval_result(search_result)
                        self._merge_results(all_results, processed_result, seen_doc_ids)
            
            # Prepare final result
            if not all_results:
                if self.rag_system is None and self.query_engine is None:
                    logger.error("No RAG system available for retrieval")
                else:
                    logger.error("RAG system does not have retrieve or search methods")
                return {"results": [], "sources": []}
            
            # Sort results by relevance score and limit to top_k
            all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            final_results = all_results[:top_k]
            
            # Add expansion information to the result
            result = {
                "results": [r.get('text', str(r)) for r in final_results],
                "sources": final_results
            }
            
            if expansion_info:
                result["query_expansion"] = expansion_info
                
            return result
                
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return {"results": [], "sources": []}
    
    def _merge_results(self, all_results: List[Dict], new_results: Dict, seen_doc_ids: Set[str]):
        """Merge new retrieval results with existing results, avoiding duplicates."""
        if not new_results or not new_results.get("sources"):
            return
            
        for source in new_results["sources"]:
            # Create a unique identifier for deduplication
            doc_id = source.get('doc_id', source.get('document_id', ''))
            text_preview = str(source.get('text', ''))[:100]
            unique_id = f"{doc_id}_{hash(text_preview)}"
            
            if unique_id not in seen_doc_ids:
                all_results.append(source)
                seen_doc_ids.add(unique_id)
            
    async def query(self, query: str, **kwargs) -> str:
        """
        Query the RAG system for a response.
        
        Args:
            query: The query to process
            **kwargs: Additional parameters for the query
            
        Returns:
            The response from the RAG system
        """
        # Check if we have a query engine or RAG system available
        if self.query_engine is None and self.rag_system is None:
            logger.error("Cannot query: Neither RAG query engine nor RAG system is initialized")
            return "I'm sorry, but I cannot access the knowledge base at the moment."
            
        try:
            logger.info(f"Querying RAG system: {query}")
            
            # First try using the query engine if available
            if self.query_engine is not None:
                if hasattr(self.query_engine, 'query'):
                    response = await self.query_engine.query(query, **kwargs)
                    
                    # If the response is a dictionary, extract the response text
                    if isinstance(response, dict) and "response" in response:
                        return response["response"]
                    elif isinstance(response, dict) and "answer" in response:
                        return response["answer"]
                    elif isinstance(response, str):
                        return response
                    else:
                        return str(response)
                else:
                    logger.warning("RAG query engine does not have a query method, trying RAG system")
            
            # If query engine is not available or doesn't work, try using RAG system directly
            if self.rag_system is not None:
                if hasattr(self.rag_system, 'query'):
                    # Use RAG system query method
                    response = self.rag_system.query(query, **kwargs)
                    if isinstance(response, dict) and "response" in response:
                        return response["response"]
                    elif isinstance(response, dict) and "answer" in response:
                        return response["answer"]
                    elif isinstance(response, str):
                        return response
                    else:
                        return str(response)
                elif hasattr(self.rag_system, 'retrieve'):
                    # Use retrieve + generate approach
                    retrieval_result = self.rag_system.retrieve(query, top_k=5)
                    
                    # Format context from retrieval
                    if retrieval_result and len(retrieval_result) > 0:
                        context_parts = []
                        for node in retrieval_result:
                            if isinstance(node, dict):
                                text = node.get('text', str(node))
                                metadata = node.get('metadata', {})
                                source = metadata.get('doc_name', 'Unknown document')
                                context_parts.append(f"Source: {source}\nContent: {text}")
                            else:
                                context_parts.append(str(node))
                        
                        context = "\n\n".join(context_parts)
                        return f"Based on the available information:\n\n{context}\n\nPlease note that this is a direct retrieval from the knowledge base. For a more comprehensive answer, please use the chat interface."
                    else:
                        return "I couldn't find relevant information in the knowledge base for your query."
                else:
                    logger.error("RAG system does not have query or retrieve methods")
                    return "I'm sorry, but I cannot process your query with the available RAG system methods."
            else:
                logger.error("No RAG system available for querying")
                return "I'm sorry, but I cannot access the knowledge base at the moment."
                
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            return f"I encountered an error while processing your query: {str(e)}"
            
    def _process_retrieval_result(self, result: Any) -> Dict[str, Any]:
        """
        Process the retrieval result into a standard format.
        
        Args:
            result: The retrieval result from the RAG system
            
        Returns:
            Dictionary with processed results and sources
        """
        # Handle different result formats
        if result is None:
            return {"results": [], "sources": []}
            
        if isinstance(result, dict):
            # If the result is already a dictionary, check for required keys
            results = result.get("results", [])
            sources = result.get("sources", [])
            
            # If sources is not in the result, try to extract from the results
            if not sources and results:
                sources = []
                for i, text in enumerate(results):
                    source = {"id": f"source_{i}", "title": f"Source {i+1}"}
                    
                    # Try to extract metadata if available
                    if isinstance(text, dict) and "metadata" in text:
                        source.update(text["metadata"])
                        
                    sources.append(source)
            
            return {
                "results": results,
                "sources": sources
            }
        elif isinstance(result, list):
            # If the result is a list, assume it's a list of documents from HyPE RAG
            results = []
            sources = []
            
            logger.debug(f"Processing {len(result)} documents from RAG retrieval")
            
            # Create sources based on the enriched documents
            for i, doc in enumerate(result):
                if isinstance(doc, dict):
                    # Extract text content for results
                    text_content = doc.get("text", str(doc))
                    results.append(text_content)
                    
                    # Log the document keys to see what we have
                    logger.debug(f"Document {i} keys: {list(doc.keys())}")
                    logger.debug(f"Document {i} filename fields: filename={doc.get('filename')}, original_filename={doc.get('original_filename')}, title={doc.get('title')}")
                    
                    # Create source with enriched metadata
                    source = {
                        "id": f"source_{i}",
                        "title": doc.get("filename") or doc.get("original_filename") or doc.get("title") or f"Document {i+1}",
                        "content": text_content,
                        "chunk_text": text_content,
                    }
                    
                    # Copy all fields from the enriched document to the source
                    # This includes: doc_id, chunk_id, chunk_index, node_id, score, matched_via, 
                    # filename, original_filename, file_type, category, language, author, created_at, size, etc.
                    for key, value in doc.items():
                        if key not in ["text"]:  # Don't override the content/chunk_text we already set
                            source[key] = value
                    
                    # Ensure we have essential fields for the frontend
                    if "filename" not in source and "original_filename" in source:
                        source["filename"] = source["original_filename"]
                    
                    # Convert score to match_percentage if available
                    if "score" in source and source["score"] is not None:
                        source["relevance_score"] = source["score"]
                        source["match_percentage"] = round(source["score"] * 100, 1)
                    
                    logger.debug(f"Created source {i} with title: {source['title']}")
                    sources.append(source)
                else:
                    # Handle non-dict items
                    text_content = str(doc)
                    results.append(text_content)
                    sources.append({
                        "id": f"source_{i}", 
                        "title": f"Source {i+1}",
                        "content": text_content,
                        "chunk_text": text_content
                    })
            
            return {
                "results": results,
                "sources": sources
            }
        else:
            # If the result is some other type, convert to string
            return {
                "results": [str(result)],
                "sources": [{"id": "source_0", "title": "Source 1"}]
            }
            
    def _process_query_result(self, result: Any) -> Dict[str, Any]:
        """
        Process the query result to extract context.
        
        Args:
            result: The query result from the RAG system
            
        Returns:
            Dictionary with extracted context and sources
        """
        if result is None:
            return {"results": [], "sources": []}
            
        if isinstance(result, dict):
            # Try to extract context from the result
            context = result.get("context", [])
            if not context:
                # Check other possible keys for context
                context = result.get("contexts", [])
            if not context:
                context = result.get("documents", [])
            
            # Try to extract sources
            sources = result.get("sources", [])
            if not sources:
                # Check other possible keys for sources
                sources = result.get("citations", [])
                
            # If sources is still empty, create from context
            if not sources and context:
                sources = []
                for i, ctx_item in enumerate(context):
                    source = {"id": f"source_{i}", "title": f"Source {i+1}"}
                    
                    # Handle different context item formats
                    if isinstance(ctx_item, dict):
                        # Extract metadata if available
                        if "metadata" in ctx_item:
                            metadata = ctx_item["metadata"]
                            source.update(metadata)
                            
                            # Extract filename from metadata
                            if "filename" in metadata:
                                source["filename"] = metadata["filename"]
                            elif "original_filename" in metadata:
                                source["filename"] = metadata["original_filename"]
                            
                            # Update title with actual filename if available
                            if "filename" in source:
                                source["title"] = source["filename"]
                        
                        # Extract chunk text content
                        if "text" in ctx_item:
                            source["content"] = ctx_item["text"]
                            source["chunk_text"] = ctx_item["text"]  # Also store as chunk_text for clarity
                        
                        # Extract relevance score
                        if "score" in ctx_item:
                            source["relevance_score"] = ctx_item["score"]
                            source["match_percentage"] = round(ctx_item["score"] * 100, 1)  # Convert to percentage
                        
                        # Extract document ID
                        if "document_id" in ctx_item:
                            source["document_id"] = ctx_item["document_id"]
                        
                        # Extract additional RAG-specific metadata
                        if "doc_id" in ctx_item:
                            source["doc_id"] = ctx_item["doc_id"]
                        if "chunk_id" in ctx_item:
                            source["chunk_id"] = ctx_item["chunk_id"]
                        if "chunk_index" in ctx_item:
                            source["chunk_index"] = ctx_item["chunk_index"]
                        if "node_id" in ctx_item:
                            source["node_id"] = ctx_item["node_id"]
                        if "matched_via" in ctx_item:
                            source["matched_via"] = ctx_item["matched_via"]
                        if "text_content_type" in ctx_item:
                            source["text_content_type"] = ctx_item["text_content_type"]
                        if "is_question" in ctx_item:
                            source["is_question"] = ctx_item["is_question"]
                        
                        # Extract file metadata if available in metadata
                        if "metadata" in ctx_item and isinstance(ctx_item["metadata"], dict):
                            metadata = ctx_item["metadata"]
                            # Add file-specific metadata
                            for key in ["file_type", "filetype", "size", "category", "language", 
                                       "created_at", "uploaded_at", "author", "page_count"]:
                                if key in metadata:
                                    source[key] = metadata[key]
                    elif isinstance(ctx_item, str):
                        # If context item is just a string, use it as content
                        source["content"] = ctx_item
                        source["chunk_text"] = ctx_item
                        
                    sources.append(source)
            
            # Extract text content for results
            results = []
            for ctx_item in context:
                if isinstance(ctx_item, dict) and "text" in ctx_item:
                    results.append(ctx_item["text"])
                elif isinstance(ctx_item, str):
                    results.append(ctx_item)
                else:
                    results.append(str(ctx_item))
            
            return {
                "results": results,
                "sources": sources
            }
        else:
            # If the result is not a dictionary, we can't extract context
            return {"results": [], "sources": []}

# Singleton instance
_rag_integration = None

def initialize_rag_integration(rag_system=None, rag_query_engine=None, use_query_expansion=False):
    """
    Initialize the global RAG integration with explicit systems.
    
    Args:
        rag_system: The RAG system instance from main
        rag_query_engine: The RAG query engine instance from main
        use_query_expansion: Whether to enable query expansion
    """
    global _rag_integration
    
    logger.info(f"Initializing global RAG integration with explicit systems (query_expansion={use_query_expansion})")
    
    # Create integration with the provided systems
    _rag_integration = RAGIntegration(
        query_engine=rag_query_engine, 
        rag_system=rag_system,
        use_query_expansion=use_query_expansion
    )
    
    # If we have a rag_system but no query_engine, add the rag_system
    if rag_system is not None and rag_query_engine is None:
        _rag_integration.rag_system = rag_system
        logger.info("RAG system set in integration")
    
    return _rag_integration

def get_rag_integration(rag_system=None, rag_query_engine=None, use_query_expansion=False):
    """
    Get the RAG integration instance.
    
    Args:
        rag_system: Optional RAG system to use if creating new instance
        rag_query_engine: Optional RAG query engine to use if creating new instance
        use_query_expansion: Whether to enable query expansion
    
    Returns:
        The RAG integration instance
    """
    global _rag_integration
    
    if _rag_integration is None:
        if rag_system is not None or rag_query_engine is not None:
            # Initialize with provided systems
            _rag_integration = initialize_rag_integration(rag_system, rag_query_engine, use_query_expansion)
        else:
            # Initialize with auto-discovery
            _rag_integration = RAGIntegration(use_query_expansion=use_query_expansion)
        
    return _rag_integration 