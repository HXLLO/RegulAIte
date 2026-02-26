"""
Core Agent implementation for the RegulAIte Agent Framework with iterative capabilities.
"""
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from pydantic import BaseModel, Field, model_validator
import logging
import uuid
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_json_serializable(obj):
    """
    Recursively converts an object into a JSON-serializable format.
    This utility function handles Pydantic models, complex objects, and nested structures.
    """
    if obj is None:
        return None
    
    try:
        # Test if already serializable
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        pass
    
    # Handle different types
    if hasattr(obj, 'model_dump'):
        # Pydantic models - recursively process the dumped data
        return make_json_serializable(obj.model_dump())
    elif hasattr(obj, 'dict'):
        # Other models with dict method
        return make_json_serializable(obj.dict())
    elif isinstance(obj, dict):
        # Dictionary - recursively process values
        result = {}
        for key, value in obj.items():
            result[str(key)] = make_json_serializable(value)
        return result
    elif isinstance(obj, (list, tuple)):
        # List/tuple - recursively process items
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool)):
        # Primitive types
        return obj
    elif isinstance(obj, datetime):
        # DateTime objects
        return obj.isoformat()
    else:
        # Convert to string as fallback
        return str(obj)

class IntentType(str, Enum):
    """Types of user query intents."""
    QUESTION = "question"
    COMMAND = "command"
    CLARIFICATION = "clarification"
    UNKNOWN = "unknown"

class IterationMode(str, Enum):
    """Types of iteration modes for agents."""
    SINGLE_PASS = "single_pass"
    ITERATIVE = "iterative"
    DEEP_ANALYSIS = "deep_analysis"
    CONTEXT_BUILDING = "context_building"

class QueryContext(BaseModel):
    """Context information about a query with iterative support."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    user_id: Optional[str] = None
    previous_interactions: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Iterative context fields
    iteration_count: int = Field(default=0)
    previous_findings: List[str] = Field(default_factory=list)
    knowledge_base: Dict[str, Any] = Field(default_factory=dict)
    document_analysis_history: List[Dict[str, Any]] = Field(default_factory=list)
    context_gaps: List[str] = Field(default_factory=list)

class Query(BaseModel):
    """Incoming user query with metadata and iterative support."""
    query_text: str = Field(..., description="The raw query text from the user")
    intent: IntentType = Field(default=IntentType.UNKNOWN)
    context: QueryContext = Field(default_factory=QueryContext)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Iterative query fields
    iteration_mode: IterationMode = Field(default=IterationMode.SINGLE_PASS)
    focus_areas: List[str] = Field(default_factory=list)
    required_depth: str = Field(default="standard")  # surface, standard, deep, comprehensive
    
    @model_validator(mode='after')
    def classify_intent(self):
        """Automatically classify the intent if not provided."""
        if self.intent == IntentType.UNKNOWN:
            # Simple classification - can be enhanced later
            query_lower = self.query_text.lower()
            if query_lower.endswith('?'):
                self.intent = IntentType.QUESTION
            elif query_lower.startswith(('find', 'search', 'get', 'retrieve', 'show')):
                self.intent = IntentType.COMMAND
            elif any(x in query_lower for x in ["what do you mean", "can you explain", "please clarify"]):
                self.intent = IntentType.CLARIFICATION
        return self

class ToolResult(BaseModel):
    """Result from executing a tool with iterative context."""
    tool_id: str
    success: bool = True
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Iterative fields
    iteration: int = Field(default=0)
    knowledge_extracted: List[str] = Field(default_factory=list)
    context_gaps_identified: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=1.0)

class AgentResponse(BaseModel):
    """Response from the agent with iterative support."""
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    tools_used: List[str] = Field(default_factory=list)
    context_used: bool = False
    sources: List[Any] = Field(default_factory=list)
    confidence: float = 1.0
    thinking: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Iterative response fields
    iteration_info: Dict[str, Any] = Field(default_factory=dict)
    knowledge_gained: List[str] = Field(default_factory=list)
    context_gaps: List[str] = Field(default_factory=list)
    requires_iteration: bool = Field(default=False)
    suggested_reformulation: Optional[str] = None
    
    @model_validator(mode='after')
    def clean_sources(self):
        """Filter out None values from sources and convert invalid types."""
        if self.sources:
            cleaned_sources = []
            for source in self.sources:
                if source is not None:
                    if isinstance(source, dict):
                        cleaned_sources.append(source)
                    elif isinstance(source, str):
                        cleaned_sources.append(source)
                    else:
                        # Convert other types to string
                        cleaned_sources.append(str(source))
            self.sources = cleaned_sources
        return self
    
class IterativeCapability:
    """Mixin class to add iterative capabilities to agents."""
    
    def __init__(self):
        self.iteration_history = []
        self.knowledge_accumulator = {}
        self.context_tracker = {}
    
    async def assess_context_completeness(self, query: Query, current_results: Any) -> Dict[str, Any]:
        """Évalue si le contexte est suffisant pour une réponse complète."""
        assessment = {
            "is_complete": True,
            "missing_elements": [],
            "confidence_level": 1.0,
            "suggested_actions": []
        }
        
        # Analyser les paramètres de la requête
        if query.parameters.get("iteration_mode"):
            required_depth = query.parameters.get("required_depth", "standard")
            focus_areas = query.parameters.get("focus_areas", [])
            
            # Vérifier si on a suffisamment de profondeur
            if required_depth in ["deep", "comprehensive"]:
                # Logique pour évaluer la profondeur requise
                assessment["is_complete"] = self._check_depth_requirements(current_results, required_depth)
            
            # Vérifier les zones de focus
            if focus_areas:
                missing_focus = self._check_focus_coverage(current_results, focus_areas)
                if missing_focus:
                    assessment["missing_elements"].extend(missing_focus)
                    assessment["is_complete"] = False
        
        return assessment
    
    def _check_depth_requirements(self, results: Any, required_depth: str) -> bool:
        """Vérifie si les résultats atteignent la profondeur requise."""
        # Implémentation simplifiée - peut être surchargée par les agents spécialisés
        if required_depth == "deep":
            return len(str(results)) > 1000  # Heuristique simple
        elif required_depth == "comprehensive":
            return len(str(results)) > 2000
        return True
    
    def _check_focus_coverage(self, results: Any, focus_areas: List[str]) -> List[str]:
        """Vérifie quelles zones de focus ne sont pas couvertes."""
        missing = []
        results_text = str(results).lower()
        
        for area in focus_areas:
            if area.lower() not in results_text:
                missing.append(area)
        
        return missing
    
    async def suggest_query_reformulation(self, original_query: str, gaps: List[str], 
                                        previous_attempts: List[str] = None) -> Optional[str]:
        """Suggère une reformulation de requête pour combler les gaps."""
        if not gaps:
            return None
            
        # Logique de base pour la reformulation
        # Les agents spécialisés peuvent surcharger cette méthode
        gap_focus = ", ".join(gaps)
        reformulated = f"{original_query} - focus spécifique sur: {gap_focus}"
        
        # Éviter les reformulations répétitives
        if previous_attempts and reformulated in previous_attempts:
            return None
            
        return reformulated
    
    def accumulate_knowledge(self, key: str, value: Any, iteration: int = 0):
        """Accumule les connaissances acquises durant les itérations."""
        if key not in self.knowledge_accumulator:
            self.knowledge_accumulator[key] = []
        
        self.knowledge_accumulator[key].append({
            "value": value,
            "iteration": iteration,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_accumulated_knowledge(self, key: str = None) -> Dict[str, Any]:
        """Récupère les connaissances accumulées."""
        if key:
            return self.knowledge_accumulator.get(key, [])
        return self.knowledge_accumulator

class Agent(IterativeCapability):
    """
    Core Agent class for orchestrating query processing with iterative capabilities.
    
    This agent processes user queries, selects appropriate tools,
    and generates responses based on tool outputs. It now supports
    iterative analysis and context building.
    """
    
    def __init__(self, agent_id: str, name: str, tools: Optional[Dict[str, Callable]] = None):
        """
        Initialize the agent with its identity and tools.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
            tools: Dictionary of tools available to this agent
        """
        super().__init__()  # Initialize iterative capabilities
        self.agent_id = agent_id
        self.name = name
        self.tools = tools or {}
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
        # Iterative capabilities
        self.max_iterations = 3
        self.iteration_threshold = 0.8  # Confidence threshold for stopping iterations
        
    async def process_query(self, query: Union[str, Query]) -> AgentResponse:
        """
        Process a user query and generate a response with iterative capabilities.
        
        Args:
            query: Either a raw query string or a Query object
            
        Returns:
            An AgentResponse object with the agent's response
        """
        # Convert string queries to Query objects
        if isinstance(query, str):
            query = Query(query_text=query)
            
        self.logger.info(f"Processing query: {query.query_text}")
        self.logger.info(f"Detected intent: {query.intent}")
        self.logger.info(f"Iteration mode: {query.iteration_mode}")
        
        # Initialize response with iterative support
        response = AgentResponse(
            content="",
            iteration_info={
                "current_iteration": query.context.iteration_count,
                "mode": query.iteration_mode,
                "focus_areas": query.focus_areas
            }
        )
        
        # Check if this is an iterative query
        if query.iteration_mode != IterationMode.SINGLE_PASS:
            response = await self._process_iterative_query(query, response)
        else:
            response = await self._process_single_query(query, response)
        
        return response
    
    async def _process_single_query(self, query: Query, response: AgentResponse) -> AgentResponse:
        """Process a single-pass query."""
        # Basic processing logic - can be overridden by specialized agents
        response.content = f"I received your query: {query.query_text}"
        response.confidence = 0.8
        
        return response
    
    async def _process_iterative_query(self, query: Query, response: AgentResponse) -> AgentResponse:
        """Process a query with iterative capabilities."""
        current_iteration = query.context.iteration_count
        
        # Use previous findings if available
        if query.context.previous_findings:
            self.logger.info(f"Using {len(query.context.previous_findings)} previous findings")
        
        # Focus on specific areas if provided
        if query.focus_areas:
            self.logger.info(f"Focusing on areas: {query.focus_areas}")
        
        # Process with iterative context
        response.content = f"Iterative analysis (iteration {current_iteration + 1}) of: {query.query_text}"
        
        # Assess if we need more context
        context_assessment = await self.assess_context_completeness(query, response.content)
        
        response.requires_iteration = not context_assessment["is_complete"]
        response.context_gaps = context_assessment["missing_elements"]
        response.confidence = context_assessment["confidence_level"]
        
        if response.requires_iteration:
            response.suggested_reformulation = await self.suggest_query_reformulation(
                query.query_text, 
                response.context_gaps,
                query.context.metadata.get("previous_queries", [])
            )
        
        # Store knowledge for future iterations
        self.accumulate_knowledge(
            "query_analysis", 
            {"query": query.query_text, "findings": response.content}, 
            current_iteration
        )
        
        return response
    
    async def execute_tool(self, tool_id: str, **kwargs) -> ToolResult:
        """
        Execute a specific tool with the given parameters and iterative support.
        
        Args:
            tool_id: ID of the tool to execute
            **kwargs: Parameters to pass to the tool
            
        Returns:
            A ToolResult with the output of the tool execution
        """
        if tool_id not in self.tools:
            return ToolResult(
                tool_id=tool_id,
                success=False,
                error=f"Tool not found: {tool_id}"
            )
            
        try:
            tool_func = self.tools[tool_id]
            result = await tool_func(**kwargs)
            
            # Enhanced tool result with iterative context
            tool_result = ToolResult(
                tool_id=tool_id,
                success=True,
                result=result,
                iteration=kwargs.get("iteration", 0)
            )
            
            # Extract knowledge if this is an iterative execution
            if kwargs.get("extract_knowledge", False):
                tool_result.knowledge_extracted = await self._extract_tool_knowledge(result)
            
            return tool_result
            
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_id}: {str(e)}")
            return ToolResult(
                tool_id=tool_id,
                success=False,
                error=str(e)
            )
    
    async def _extract_tool_knowledge(self, tool_result: Any) -> List[str]:
        """Extract key knowledge from tool results."""
        # Basic implementation - can be overridden by specialized agents
        knowledge = []
        
        if isinstance(tool_result, dict):
            for key, value in tool_result.items():
                if key in ["findings", "insights", "conclusions", "recommendations"]:
                    if isinstance(value, list):
                        knowledge.extend(value)
                    else:
                        knowledge.append(str(value))
        
        return knowledge 
    
    def format_document_as_source(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a document object to a properly formatted source dictionary.
        
        Args:
            doc: Document dictionary with various possible fields
            
        Returns:
            Properly formatted source dictionary
        """
        return {
            "doc_id": doc.get('id') or doc.get('doc_id') or doc.get('_id', 'unknown'),
            "title": (doc.get('title') or 
                     doc.get('filename') or 
                     doc.get('original_filename') or 
                     doc.get('name') or 
                     f"Document {doc.get('id', 'unknown')}"),
            "filename": doc.get('filename') or doc.get('original_filename'),
            "original_filename": doc.get('original_filename'),
            "page_number": doc.get('page_number', 1),
            "score": doc.get('score') or doc.get('relevance_score'),
            "relevance_score": doc.get('relevance_score') or doc.get('score'),
            "match_percentage": doc.get('match_percentage'),
            "retrieval_method": doc.get('retrieval_method', 'SEMANTIC'),
            "content": doc.get('content') or doc.get('chunk_text') or doc.get('text'),
            "chunk_text": doc.get('chunk_text') or doc.get('content') or doc.get('text'),
            "chunk_id": doc.get('chunk_id'),
            "chunk_index": doc.get('chunk_index'),
            "node_id": doc.get('node_id'),
            "file_type": doc.get('file_type'),
            "category": doc.get('category'),
            "language": doc.get('language'),
            "author": doc.get('author'),
            "created_at": doc.get('created_at'),
            "size": doc.get('size'),
            "page_count": doc.get('page_count'),
            "matched_via": doc.get('matched_via'),
            "text_content_type": doc.get('text_content_type'),
            "is_question": doc.get('is_question')
        }
    
    def format_documents_as_sources(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert a list of document objects to properly formatted source dictionaries.
        
        Args:
            docs: List of document dictionaries
            
        Returns:
            List of properly formatted source dictionaries
        """
        return [self.format_document_as_source(doc) for doc in docs]