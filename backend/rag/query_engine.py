import logging
from typing import List, Dict, Any, Optional
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger("rag_query_engine")

class RAGQueryEngine:
    """
    RAG query engine for retrieving and processing context
    """
    
    def __init__(
        self,
        rag_system,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_tokens: int = 1500,
        use_self_critique: bool = True
    ):
        """
        Initialize the RAG query engine
        
        Args:
            rag_system: The RAG system to use for retrievals
            model_name: OpenAI model to use for LLM
            temperature: Temperature parameter for LLM
            max_tokens: Maximum tokens to generate
            use_self_critique: Whether to use self-critique for improved answers
        """
        self.rag_system = rag_system
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_self_critique = use_self_critique
        
        logger.info(f"Initialized RAG query engine with model {model_name}")
    
    async def query(self, query_text: str, top_k: int = 5, search_filter: Optional[Dict[str, Any]] = None, debug: bool = False, streaming: bool = False, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Query the RAG system and return results with context
        
        Args:
            query_text: The query text
            top_k: Maximum number of results to return
            search_filter: Optional filters for metadata search
            debug: If true, include retrieval scores in the response
            streaming: Whether to stream the response
            custom_prompt: Optional custom prompt for answer generation
            
        Returns:
            Dictionary with query results and context
        """
        try:
            # Get context from RAG system
            context_results = self.rag_system.retrieve(query_text, top_k=top_k, filters=search_filter)
            
            # Format context for response
            contexts = []
            for res in context_results:
                # Include the full result in context
                ctx_item = {
                    "text": res.get("text", ""),
                    "metadata": res.get("metadata", {}),
                    "score": res.get("score", 0),
                    "document_id": res.get("metadata", {}).get("doc_id", "unknown")
                }
                
                contexts.append(ctx_item)
                
            response = {
                "query": query_text,
                "contexts": contexts,  # Named "contexts" instead of "context"
                "timestamp": str(self.rag_system._get_timestamp())
            }
            
            # Include retrieval info for debug
            if debug:
                response["retrieval_info"] = {
                    "vector_weight": self.rag_system.vector_weight,
                    "semantic_weight": self.rag_system.semantic_weight,
                    "search_method": "hybrid" if self.rag_system.semantic_weight > 0 else "vector",
                    "bm25_initialized": self.rag_system.bm25_initialized
                }
                
            # Add context quality assessment based on number of results and scores
            if contexts:
                avg_score = sum(ctx["score"] for ctx in contexts) / len(contexts)
                if avg_score > 0.7:
                    response["context_quality"] = "high"
                elif avg_score > 0.4:
                    response["context_quality"] = "medium"
                else:
                    response["context_quality"] = "low"
            else:
                response["context_quality"] = "none"
                
            return response
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            return {
                "query": query_text,
                "contexts": [],
                "error": str(e),
                "timestamp": str(self.rag_system._get_timestamp())
            }
    
    def generate_answer(self, query_text: str, context_results: List[Dict[str, Any]]) -> str:
        """
        Generate an answer based on the query and context results
        
        Args:
            query_text: The original query
            context_results: List of context results from RAG
            
        Returns:
            Generated answer
        """
        try:
            context_text = ""
            for i, result in enumerate(context_results):
                context_text += f"Context {i+1}:\n{result.get('text', '')}\n\n"
            
            # Create prompt template
            template = f"""
            You are a helpful assistant that answers questions based on the provided context.
            Use only information from the context to answer the question. If you don't know the answer, 
            say that you don't know based on the provided context.
            
            Context:
            {context_text}
            
            Question: {query_text}
            
            Answer:
            """
            
            # Create a ChatOpenAI model
            chat_model = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                openai_api_key=self.rag_system.openai_api_key
            )
            
            # Generate the answer
            response = chat_model.invoke(template)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"An error occurred while generating the answer: {str(e)}" 