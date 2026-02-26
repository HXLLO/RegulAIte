"""
Search-related tools for the RegulAIte Agent Framework.

This module provides tools for searching and retrieving information.
"""
from typing import Dict, List, Optional, Any
import logging
import re

from ..tool_registry import tool

# Set up logging
logger = logging.getLogger(__name__)

@tool(
    id="query_reformulation",
    name="Query Reformulation",
    description="Reformulate a query to improve retrieval results using GRC-specific expansion",
    tags=["search", "retrieval", "query"],
    requires_context=False
)
async def query_reformulation(query: str, strategy: str = "expand") -> Dict[str, Any]:
    """
    Reformulate a query to improve retrieval results.
    
    Args:
        query: The original query
        strategy: The reformulation strategy (expand, specify, simplify, grc_expand)
        
    Returns:
        Dictionary with reformulated queries
    """
    logger.info(f"Reformulating query: {query} using strategy: {strategy}")
    
    reformulations = []
    expansion_info = None
    
    if strategy == "grc_expand":
        # Use GRC-specific query expansion
        try:
            from .query_expansion import get_query_expander
            query_expander = get_query_expander()
            
            expansion_result = await query_expander.expand_query(
                query,
                strategy="comprehensive",
                max_expansions=8,
                include_frameworks=True
            )
            
            if expansion_result.expanded_terms:
                # Create reformulated queries with expanded terms
                reformulations = [
                    query,
                    f"{query} {' '.join(expansion_result.expanded_terms[:3])}",
                    f"{query} {' '.join(expansion_result.expanded_terms[3:6])}",
                    " ".join(expansion_result.expanded_terms[:5])
                ]
                
                expansion_info = {
                    "expanded_terms": expansion_result.expanded_terms,
                    "framework_terms": expansion_result.framework_terms,
                    "confidence_score": expansion_result.confidence_score
                }
            else:
                reformulations = [query]
                
        except Exception as e:
            logger.error(f"GRC expansion failed: {str(e)}")
            reformulations = [query]
            
    elif strategy == "expand":
        # Add synonyms or related terms
        reformulations = [
            query,
            f"information about {query}",
            f"details regarding {query}",
            f"explanation of {query}"
        ]
    elif strategy == "specify":
        # Make the query more specific
        reformulations = [
            query,
            f"specific information about {query}",
            f"detailed explanation of {query}",
            f"{query} detailed information"
        ]
    elif strategy == "simplify":
        # Simplify the query
        # Remove stop words, focus on key terms
        simple_query = re.sub(r'\b(the|a|an|in|on|at|to|for|with|by|about|of)\b', '', query, flags=re.IGNORECASE)
        simple_query = re.sub(r'\s+', ' ', simple_query).strip()
        
        reformulations = [
            query,
            simple_query,
            " ".join([word for word in query.split() if len(word) > 3])
        ]
    else:
        # Default strategy
        reformulations = [query]
    
    result = {
        "original_query": query,
        "strategy": strategy,
        "reformulations": reformulations
    }
    
    if expansion_info:
        result["expansion_info"] = expansion_info
    
    return result

@tool(
    id="filter_search",
    name="Filter Search",
    description="Apply filters to a search query",
    tags=["search", "filter", "retrieval"],
    requires_context=False
)
async def filter_search(query: str, 
                       filters: Optional[Dict[str, Any]] = None, 
                       date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Apply filters to a search query.
    
    Args:
        query: The search query
        filters: Dictionary of filter criteria
        date_range: Date range for filtering
        
    Returns:
        Dictionary with filter information
    """
    logger.info(f"Applying filters to query: {query}")
    
    # Initialize filters if not provided
    if filters is None:
        filters = {}
    
    # Initialize date range if not provided
    if date_range is None:
        date_range = {}
    
    return {
        "query": query,
        "filters": filters,
        "date_range": date_range,
        "filter_query": f"{query} {' '.join([f'{k}:{v}' for k, v in filters.items()])}"
    }

@tool(
    id="extract_search_entities",
    name="Extract Search Entities",
    description="Extract entities from a search query using LLM intelligence",
    tags=["search", "entity", "extraction", "nlp"],
    requires_context=False
)
async def extract_search_entities(query: str) -> Dict[str, List[str]]:
    """
    Extract entities from a search query using LLM intelligence.
    
    Args:
        query: The search query
        
    Returns:
        Dictionary of extracted entities by type
    """
    logger.info(f"Extracting entities from query: {query}")
    
    # Try to get LLM client for intelligent entity extraction
    try:
        from ..integrations.llm_integration import get_llm_integration
        llm_client = get_llm_integration()
        
        if llm_client:
            return await _extract_entities_with_llm(query, llm_client)
        else:
            logger.warning("LLM client not available, falling back to regex extraction")
            return _extract_entities_with_regex(query)
    except Exception as e:
        logger.warning(f"LLM entity extraction failed: {str(e)}, falling back to regex")
        return _extract_entities_with_regex(query)

async def _extract_entities_with_llm(query: str, llm_client) -> Dict[str, List[str]]:
    """
    Extract entities using LLM for intelligent processing.
    
    Args:
        query: The search query
        llm_client: The LLM client to use
        
    Returns:
        Dictionary of extracted entities by type
    """
    import json
    
    prompt = f"""
Extract named entities from the following query and return them as a JSON object. Focus on identifying:

1. **dates**: Any date references (absolute or relative)
2. **organizations**: Company names, institutions, agencies, departments
3. **people**: Person names, titles, roles
4. **locations**: Places, addresses, countries, regions
5. **regulations**: Laws, regulations, directives, standards, codes
6. **financial_terms**: Financial amounts, currencies, financial concepts
7. **document_types**: Types of documents mentioned (contracts, reports, etc.)
8. **keywords**: Important domain-specific terms and concepts

Return the result as JSON in this exact format:
{{
    "dates": ["date1", "date2"],
    "organizations": ["org1", "org2"],
    "people": ["person1", "person2"],
    "locations": ["location1", "location2"],
    "regulations": ["regulation1", "regulation2"],
    "financial_terms": ["term1", "term2"],
    "document_types": ["type1", "type2"],
    "keywords": ["keyword1", "keyword2"]
}}

Query: "{query}"

JSON Response:
"""
    
    try:
        response = await llm_client.generate(prompt, temperature=0.1)
        
        # Try to parse JSON response
        try:
            entities = json.loads(response)
            
            # Ensure all expected keys are present
            expected_keys = ["dates", "organizations", "people", "locations", 
                           "regulations", "financial_terms", "document_types", "keywords"]
            
            for key in expected_keys:
                if key not in entities:
                    entities[key] = []
                    
            logger.info(f"Successfully extracted {sum(len(v) for v in entities.values())} entities with LLM")
            return entities
            
        except json.JSONDecodeError as e:
            logger.warning(f"LLM response is not valid JSON: {str(e)}")
            # Try to extract from text response
            return _parse_entities_from_text(response, query)
            
    except Exception as e:
        logger.error(f"Error in LLM entity extraction: {str(e)}")
        raise

def _parse_entities_from_text(response: str, query: str) -> Dict[str, List[str]]:
    """
    Parse entities from a non-JSON LLM response.
    
    Args:
        response: The text response from LLM
        query: Original query for fallback extraction
        
    Returns:
        Dictionary of extracted entities by type
    """
    import re
    
    entities = {
        "dates": [],
        "organizations": [],
        "people": [],
        "locations": [],
        "regulations": [],
        "financial_terms": [],
        "document_types": [],
        "keywords": []
    }
    
    # Try to extract lists from the response
    for entity_type in entities.keys():
        # Look for patterns like "dates": ["item1", "item2"]
        pattern = rf'{entity_type}["\']?\s*:\s*\[([^\]]+)\]'
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            items_str = match.group(1)
            items = [item.strip(' "\'') for item in items_str.split(',')]
            entities[entity_type] = [item for item in items if item]
    
    # If no entities were found, fall back to regex on original query
    if not any(entities.values()):
        return _extract_entities_with_regex(query)
        
    return entities

def _extract_entities_with_regex(query: str) -> Dict[str, List[str]]:
    """
    Extract entities using regex patterns (fallback method).
    
    Args:
        query: The search query
        
    Returns:
        Dictionary of extracted entities by type
    """
    entities = {
        "dates": [],
        "organizations": [],
        "people": [],
        "locations": [],
        "regulations": [],
        "financial_terms": [],
        "document_types": [],
        "keywords": []
    }
    
    # Extract dates (simple pattern matching)
    date_patterns = [
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b\d{4}-\d{1,2}-\d{1,2}\b",
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b"
    ]
    
    for pattern in date_patterns:
        dates = re.findall(pattern, query, re.IGNORECASE)
        entities["dates"].extend(dates)
    
    # Extract organizations (simple pattern matching)
    org_patterns = [
        r"\b[A-Z][a-z]+ (Inc|Corp|Corporation|Company|Co|Ltd)\b",
        r"\b[A-Z][A-Za-z]+ (Inc|Corp|Corporation|Company|Co|Ltd)\b",
        r"\b[A-Z]{2,}\b"  # All caps words often organizations
    ]
    
    for pattern in org_patterns:
        orgs = re.findall(pattern, query)
        entities["organizations"].extend(orgs)
    
    # Extract financial terms
    financial_patterns = [
        r"[\$€£¥]\s?\d+(?:\.\d+)?",
        r"\d+(?:\.\d+)?\s?(?:dollars|euros|pounds|yen|USD|EUR|GBP|JPY)",
        r"\b(?:profit|loss|revenue|income|expense|budget|cost|price|fee|tax)\b"
    ]
    
    for pattern in financial_patterns:
        terms = re.findall(pattern, query, re.IGNORECASE)
        entities["financial_terms"].extend(terms)
    
    # Extract regulation references
    regulation_patterns = [
        r"article\s+\d+",
        r"section\s+\d+",
        r"§\s*\d+",
        r"\b(?:regulation|directive|law|act|code|standard)\s+\w+",
        r"\b(?:GDPR|SOX|HIPAA|PCI|ISO\s*\d+)\b"
    ]
    
    for pattern in regulation_patterns:
        regs = re.findall(pattern, query, re.IGNORECASE)
        entities["regulations"].extend(regs)
    
    # Extract document types
    doc_patterns = [
        r"\b(?:contract|agreement|report|document|file|pdf|spreadsheet|presentation|form|application)\b"
    ]
    
    for pattern in doc_patterns:
        docs = re.findall(pattern, query, re.IGNORECASE)
        entities["document_types"].extend(docs)
    
    # Extract keywords (simple approach - words longer than 4 chars)
    keywords = [word for word in query.split() if len(word) > 4 and word.isalpha()]
    entities["keywords"] = keywords
    
    return entities 


class SearchTools:
    """
    Search tools collection for the RegulAIte Agent Framework.
    
    This class provides various search capabilities including semantic, keyword,
    and hybrid search methods.
    """
    
    def __init__(self, rag_system=None):
        """
        Initialize the search tools.
        
        Args:
            rag_system: The RAG system to use for semantic search
        """
        self.rag_system = rag_system
        
    async def semantic_search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform semantic search using the RAG system.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filters: Optional filters to apply
            
        Returns:
            Dictionary with search results
        """
        if not self.rag_system:
            logger.warning("RAG system not available for semantic search")
            return {"results": [], "message": "Semantic search not available"}
        
        try:
            results = self.rag_system.retrieve(query, top_k=top_k, filter=filters)
            return {
                "results": results,
                "search_type": "semantic",
                "query": query,
                "total_results": len(results)
            }
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return {"results": [], "error": str(e)}
    
    async def keyword_search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform keyword-based search.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filters: Optional filters to apply
            
        Returns:
            Dictionary with search results
        """
        # For now, this is a placeholder implementation
        # In a real system, this would use BM25 or similar keyword search
        logger.info(f"Performing keyword search for: {query}")
        
        # Reformulate query for better keyword matching
        reformulation_result = await query_reformulation(query, strategy="simplify")
        simplified_query = reformulation_result["reformulations"][1] if len(reformulation_result["reformulations"]) > 1 else query
        
        return {
            "results": [],
            "search_type": "keyword",
            "query": query,
            "processed_query": simplified_query,
            "total_results": 0,
            "message": "Keyword search implementation pending"
        }
    
    async def hybrid_search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None, 
                           semantic_weight: float = 0.7, keyword_weight: float = 0.3) -> Dict[str, Any]:
        """
        Perform hybrid search combining semantic and keyword search.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filters: Optional filters to apply
            semantic_weight: Weight for semantic search results (0-1)
            keyword_weight: Weight for keyword search results (0-1)
            
        Returns:
            Dictionary with combined search results
        """
        logger.info(f"Performing hybrid search for: {query}")
        
        # Perform both searches
        semantic_results = await self.semantic_search(query, top_k, filters)
        keyword_results = await self.keyword_search(query, top_k, filters)
        
        # Combine and weight results
        combined_results = []
        
        # For now, prioritize semantic results since keyword search is not fully implemented
        if semantic_results.get("results"):
            for i, result in enumerate(semantic_results["results"][:top_k]):
                # Add semantic score weighted
                if isinstance(result, dict):
                    result["hybrid_score"] = semantic_weight * result.get("score", 1.0)
                    result["search_type"] = "hybrid"
                combined_results.append(result)
        
        return {
            "results": combined_results,
            "search_type": "hybrid",
            "query": query,
            "semantic_weight": semantic_weight,
            "keyword_weight": keyword_weight,
            "total_results": len(combined_results)
        }


# Tool function implementations
from ..tool_registry import tool

@tool(
    id="semantic_search",
    name="Semantic Search",
    description="Perform semantic search using vector embeddings",
    tags=["search", "semantic", "retrieval"],
    requires_context=False
)
async def semantic_search_tool(query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform semantic search using the RAG system.
    
    Args:
        query: The search query
        top_k: Number of results to return
        filters: Optional filters to apply
        
    Returns:
        Dictionary with search results
    """
    from ..integrations.rag_integration import get_rag_integration
    
    rag_integration = get_rag_integration()
    
    try:
        # Use RAG integration for semantic search
        retrieval_result = await rag_integration.retrieve(query, top_k=top_k, search_filter=filters)
        
        return {
            "results": retrieval_result.get("results", []),
            "sources": retrieval_result.get("sources", []),
            "search_type": "semantic",
            "query": query,
            "total_results": len(retrieval_result.get("results", []))
        }
    except Exception as e:
        logger.error(f"Semantic search tool failed: {str(e)}")
        return {
            "results": [],
            "sources": [],
            "error": str(e),
            "search_type": "semantic",
            "query": query
        }

@tool(
    id="keyword_search",
    name="Keyword Search",
    description="Perform keyword-based search",
    tags=["search", "keyword", "retrieval"],
    requires_context=False
)
async def keyword_search_tool(query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform keyword-based search.
    
    Args:
        query: The search query
        top_k: Number of results to return
        filters: Optional filters to apply
        
    Returns:
        Dictionary with search results
    """
    logger.info(f"Performing keyword search for: {query}")
    
    # Reformulate query for better keyword matching
    reformulation_result = await query_reformulation(query, strategy="simplify")
    simplified_query = reformulation_result["reformulations"][1] if len(reformulation_result["reformulations"]) > 1 else query
    
    return {
        "results": [],
        "search_type": "keyword",
        "query": query,
        "processed_query": simplified_query,
        "total_results": 0,
        "message": "Keyword search implementation pending"
    }

@tool(
    id="hybrid_search",
    name="Hybrid Search",
    description="Perform hybrid search combining semantic and keyword search",
    tags=["search", "hybrid", "retrieval"],
    requires_context=False
)
async def hybrid_search_tool(query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None,
                            semantic_weight: float = 0.7, keyword_weight: float = 0.3) -> Dict[str, Any]:
    """
    Perform hybrid search combining semantic and keyword search.
    
    Args:
        query: The search query
        top_k: Number of results to return
        filters: Optional filters to apply
        semantic_weight: Weight for semantic search results (0-1)
        keyword_weight: Weight for keyword search results (0-1)
        
    Returns:
        Dictionary with combined search results
    """
    logger.info(f"Performing hybrid search for: {query}")
    
    # Perform both searches
    semantic_results = await semantic_search_tool(query, top_k, filters)
    keyword_results = await keyword_search_tool(query, top_k, filters)
    
    # Combine and weight results
    combined_results = []
    
    # For now, prioritize semantic results since keyword search is not fully implemented
    if semantic_results.get("results"):
        for i, result in enumerate(semantic_results["results"][:top_k]):
            # Add semantic score weighted
            if isinstance(result, dict):
                combined_results.append({
                    **result,
                    "hybrid_score": semantic_weight * result.get("score", 1.0),
                    "search_type": "hybrid"
                })
            else:
                combined_results.append({
                    "content": result,
                    "hybrid_score": semantic_weight,
                    "search_type": "hybrid"
                })
    
    return {
        "results": combined_results,
        "sources": semantic_results.get("sources", []),
        "search_type": "hybrid",
        "query": query,
        "semantic_weight": semantic_weight,
        "keyword_weight": keyword_weight,
        "total_results": len(combined_results)
    } 