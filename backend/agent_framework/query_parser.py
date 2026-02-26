"""
Query Parser for the RegulAIte Agent Framework with Iterative Capabilities.

This module provides functionality for parsing, validating, and classifying 
user queries using Pydantic models for type safety and LLM-based intelligence.
Enhanced with iterative query reformulation and context analysis.
"""
from typing import Dict, List, Optional, Any, Tuple, Union
from pydantic import BaseModel, Field, model_validator
import re
import logging
import json
from enum import Enum

from .agent import Query, IntentType, QueryContext, IterationMode

# Set up logging
logger = logging.getLogger(__name__)

class QueryCategory(str, Enum):
    """Categories of queries for more specific handling."""
    LEGAL = "legal"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    DOCUMENT = "document"
    GENERAL = "general"
    SYSTEM = "system"

class QueryComplexity(str, Enum):
    """Complexity levels for determining iteration needs."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

class ContextGap(BaseModel):
    """Represents a gap in context that requires iteration."""
    gap_type: str
    description: str
    suggested_action: str
    priority: int = Field(ge=1, le=5)  # 1 = high priority, 5 = low priority

class ParsedQuery(Query):
    """
    Extended Query model with additional parsing information and iterative support.
    """
    category: QueryCategory = Field(default=QueryCategory.GENERAL)
    complexity: QueryComplexity = Field(default=QueryComplexity.MODERATE)
    entities: Dict[str, Any] = Field(default_factory=dict)
    keywords: List[str] = Field(default_factory=list)
    parsed_parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    
    # Iterative parsing fields
    context_gaps: List[ContextGap] = Field(default_factory=list)
    requires_iteration: bool = Field(default=False)
    suggested_reformulations: List[str] = Field(default_factory=list)
    iteration_strategy: Optional[str] = None

class QueryParser:
    """
    Parser for extracting structured information from user queries using LLM intelligence
    with enhanced iterative capabilities.
    """
    
    def __init__(self, llm_client=None):
        """Initialize the query parser with optional LLM client."""
        self.llm_client = llm_client
        
        # Initialize LLM client if not provided
        if self.llm_client is None:
            try:
                from .integrations.llm_integration import get_llm_integration
                self.llm_client = get_llm_integration()
                logger.info("Initialized LLM client for query parser")
            except Exception as e:
                logger.warning(f"Could not initialize LLM client: {str(e)}")
                self.llm_client = None
        
        # Enhanced keyword patterns for iterative analysis
        self.keyword_patterns = {
            QueryCategory.LEGAL: [
                r"legal", r"law", r"regulation", r"compliance", r"statute", 
                r"directive", r"ordinance", r"article", r"section"
            ],
            QueryCategory.FINANCIAL: [
                r"financial", r"finance", r"money", r"payment", r"transaction",
                r"bank", r"account", r"deposit", r"withdraw", r"transfer"
            ],
            QueryCategory.COMPLIANCE: [
                r"compliance", r"conform", r"adhere", r"standard", r"requirement",
                r"guideline", r"policy", r"procedure", r"protocol"
            ],
            QueryCategory.DOCUMENT: [
                r"document", r"file", r"pdf", r"spreadsheet", r"contract",
                r"agreement", r"upload", r"download", r"text", r"content"
            ],
            QueryCategory.SYSTEM: [
                r"system", r"login", r"account", r"password", r"settings",
                r"configure", r"setup", r"profile", r"preferences"
            ]
        }
        
        # Patterns indicating need for iteration
        self.iteration_indicators = [
            r"comprehensive", r"detailed", r"thorough", r"in-depth",
            r"complete", r"exhaustive", r"all aspects", r"everything",
            r"deep dive", r"full analysis", r"extensive"
        ]
        
        # Complexity indicators
        self.complexity_patterns = {
            QueryComplexity.SIMPLE: [r"what is", r"define", r"explain"],
            QueryComplexity.MODERATE: [r"how", r"why", r"compare", r"analyze"],
            QueryComplexity.COMPLEX: [r"evaluate", r"assess", r"implement", r"strategy"],
            QueryComplexity.VERY_COMPLEX: [r"comprehensive", r"multi-framework", r"optimize", r"transform"]
        }
        
        # Common named entities we want to extract (fallback patterns)
        self.entity_patterns = {
            "date": r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "url": r"https?://[^\s]+",
            "number": r"\b\d+\b",
            "money": r"[\$€£¥]\s?\d+(?:\.\d+)?|\d+(?:\.\d+)?\s?(?:dollars|euros|pounds|yen)",
            "percentage": r"\d+(?:\.\d+)?%",
            "article_ref": r"article\s+\d+|section\s+\d+|§\s*\d+",
            "framework": r"(ISO\s*27001|RGPD|GDPR|DORA|NIST|SOX|PCI-DSS)",
            "compliance_term": r"(audit|assessment|certification|gap analysis|remediation)"
        }
        
    async def parse(self, query: Union[str, Query]) -> ParsedQuery:
        """
        Parse a query into a structured form using LLM intelligence with iterative support.
        
        Args:
            query: The query text or Query object to parse
            
        Returns:
            A ParsedQuery object with structured information and iteration strategy
        """
        # Convert string to Query if needed
        if isinstance(query, str):
            query = Query(query_text=query)
            
        # Create a ParsedQuery from the Query
        parsed = ParsedQuery(
            query_text=query.query_text,
            intent=query.intent,
            context=query.context,
            parameters=query.parameters,
            iteration_mode=query.iteration_mode,
            focus_areas=query.focus_areas,
            required_depth=query.required_depth
        )
        
        # Use LLM for intelligent parsing if available
        if self.llm_client:
            try:
                await self._parse_with_llm_enhanced(parsed)
            except Exception as e:
                logger.warning(f"LLM parsing failed, falling back to regex: {str(e)}")
                await self._parse_with_regex_enhanced(parsed)
        else:
            # Fallback to enhanced regex-based parsing
            await self._parse_with_regex_enhanced(parsed)
        
        # Analyze iteration requirements
        await self._analyze_iteration_requirements(parsed)
        
        # Log the parsing result
        logger.info(f"Parsed query: {parsed.query_text}")
        logger.info(f"Intent: {parsed.intent}, Category: {parsed.category}, Complexity: {parsed.complexity}")
        logger.info(f"Keywords: {parsed.keywords}")
        logger.info(f"Entities: {parsed.entities}")
        logger.info(f"Requires iteration: {parsed.requires_iteration}")
        
        return parsed
        
    async def _parse_with_llm_enhanced(self, parsed_query: ParsedQuery):
        """
        Enhanced LLM-based parsing with iterative analysis capabilities.
        
        Args:
            parsed_query: The ParsedQuery object to populate
        """
        prompt = f"""
Analyze the following GRC query and extract comprehensive structured information. Return your response as a JSON object:

{{
    "keywords": ["keyword1", "keyword2", "..."],
    "entities": {{
        "dates": ["extracted dates"],
        "organizations": ["company names, org names"],
        "people": ["person names"],
        "locations": ["place names, addresses"],
        "regulations": ["regulation names, law references"],
        "frameworks": ["ISO27001", "RGPD", "DORA", etc.],
        "financial_terms": ["financial concepts, amounts"],
        "document_types": ["document types mentioned"],
        "compliance_terms": ["audit", "assessment", etc.]
    }},
    "category": "legal|financial|compliance|document|general|system",
    "complexity": "simple|moderate|complex|very_complex",
    "intent": "question|command|clarification|information|unknown",
    "iteration_requirements": {{
        "requires_iteration": true/false,
        "iteration_mode": "single_pass|iterative|deep_analysis|context_building",
        "required_depth": "surface|standard|deep|comprehensive",
        "focus_areas": ["area1", "area2"],
        "context_gaps": [
            {{
                "gap_type": "missing_information|insufficient_detail|ambiguous_scope",
                "description": "description of the gap",
                "suggested_action": "what to do to fill the gap",
                "priority": 1-5
            }}
        ]
    }},
    "parameters": {{
        "key": "value for any key-value pairs found"
    }},
    "confidence": 0.0-1.0
}}

Focus on GRC-specific analysis:
1. Identify regulatory frameworks mentioned or implied
2. Detect compliance requirements and standards
3. Assess if the query requires deep analysis or multiple documents
4. Determine if iterative refinement would improve results
5. Identify potential ambiguities that need clarification

Query: "{parsed_query.query_text}"

Respond only with valid JSON:
"""
        
        try:
            response = await self.llm_client.generate(prompt, temperature=0.1)
            
            # Try to parse the JSON response
            try:
                result = json.loads(response)
                
                # Extract basic information
                parsed_query.keywords = result.get("keywords", [])
                parsed_query.entities = result.get("entities", {})
                parsed_query.parsed_parameters = result.get("parameters", {})
                parsed_query.confidence = result.get("confidence", 1.0)
                
                # Set category
                category_str = result.get("category", "general")
                try:
                    parsed_query.category = QueryCategory(category_str)
                except ValueError:
                    parsed_query.category = QueryCategory.GENERAL
                
                # Set complexity
                complexity_str = result.get("complexity", "moderate")
                try:
                    parsed_query.complexity = QueryComplexity(complexity_str)
                except ValueError:
                    parsed_query.complexity = QueryComplexity.MODERATE
                
                # Set intent
                intent_str = result.get("intent", "unknown")
                try:
                    parsed_query.intent = IntentType(intent_str.upper())
                except ValueError:
                    parsed_query.intent = IntentType.UNKNOWN
                
                # Extract iteration requirements
                iteration_req = result.get("iteration_requirements", {})
                parsed_query.requires_iteration = iteration_req.get("requires_iteration", False)
                
                # Set iteration mode
                iteration_mode_str = iteration_req.get("iteration_mode", "single_pass")
                try:
                    parsed_query.iteration_mode = IterationMode(iteration_mode_str)
                except ValueError:
                    parsed_query.iteration_mode = IterationMode.SINGLE_PASS
                
                parsed_query.required_depth = iteration_req.get("required_depth", "standard")
                parsed_query.focus_areas = iteration_req.get("focus_areas", [])
                
                # Parse context gaps
                context_gaps_data = iteration_req.get("context_gaps", [])
                parsed_query.context_gaps = [
                    ContextGap(**gap) for gap in context_gaps_data
                    if isinstance(gap, dict) and all(k in gap for k in ["gap_type", "description", "suggested_action"])
                ]
                
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON, falling back to text extraction")
                await self._extract_from_text_response(parsed_query, response)
                
        except Exception as e:
            logger.error(f"Error in LLM parsing: {str(e)}")
            # Fallback to regex parsing
            await self._parse_with_regex_enhanced(parsed_query)

    async def _parse_with_regex_enhanced(self, parsed_query: ParsedQuery):
        """
        Enhanced regex-based parsing with iterative capabilities.
        
        Args:
            parsed_query: The ParsedQuery object to populate
        """
        text = parsed_query.query_text.lower()
        
        # Extract entities using patterns
        parsed_query.entities = self._extract_entities_enhanced(parsed_query.query_text)
        
        # Extract keywords
        parsed_query.keywords = self._extract_keywords_enhanced(parsed_query.query_text)
        
        # Classify category
        parsed_query.category = self._classify_category(text, parsed_query.keywords)
        
        # Assess complexity
        parsed_query.complexity = self._assess_complexity(text, parsed_query.keywords)
        
        # Extract parameters
        parsed_query.parsed_parameters = self._extract_parameters(parsed_query.query_text)
        
        # Determine if iteration is needed
        parsed_query.requires_iteration = self._needs_iteration(text, parsed_query.complexity)
        
        if parsed_query.requires_iteration:
            parsed_query.iteration_mode = self._determine_iteration_mode(text, parsed_query.complexity)
            parsed_query.context_gaps = self._identify_context_gaps_regex(text, parsed_query)

    def _assess_complexity(self, text: str, keywords: List[str]) -> QueryComplexity:
        """Assess query complexity based on patterns and keywords."""
        complexity_scores = {
            QueryComplexity.SIMPLE: 0,
            QueryComplexity.MODERATE: 0,
            QueryComplexity.COMPLEX: 0,
            QueryComplexity.VERY_COMPLEX: 0
        }
        
        # Check patterns
        for complexity, patterns in self.complexity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    complexity_scores[complexity] += 1
        
        # Additional complexity indicators
        if len(keywords) > 10:
            complexity_scores[QueryComplexity.COMPLEX] += 1
        
        if any(indicator in text for indicator in self.iteration_indicators):
            complexity_scores[QueryComplexity.VERY_COMPLEX] += 2
        
        # Multi-framework queries are more complex
        framework_count = len([k for k in keywords if "iso" in k.lower() or "rgpd" in k.lower() or "dora" in k.lower()])
        if framework_count > 1:
            complexity_scores[QueryComplexity.VERY_COMPLEX] += 1
        
        # Return highest scoring complexity
        return max(complexity_scores.items(), key=lambda x: x[1])[0]

    def _needs_iteration(self, text: str, complexity: QueryComplexity) -> bool:
        """Determine if a query needs iterative processing."""
        # High complexity queries often need iteration
        if complexity in [QueryComplexity.COMPLEX, QueryComplexity.VERY_COMPLEX]:
            return True
        
        # Check for iteration indicators
        for indicator in self.iteration_indicators:
            if indicator in text:
                return True
        
        # Queries asking for multiple aspects
        multi_aspect_indicators = ["and", "also", "additionally", "furthermore", "moreover"]
        if sum(1 for indicator in multi_aspect_indicators if indicator in text) >= 2:
            return True
        
        return False

    def _determine_iteration_mode(self, text: str, complexity: QueryComplexity) -> IterationMode:
        """Determine the appropriate iteration mode."""
        if complexity == QueryComplexity.VERY_COMPLEX:
            if any(word in text for word in ["comprehensive", "complete", "exhaustive"]):
                return IterationMode.DEEP_ANALYSIS
            else:
                return IterationMode.ITERATIVE
        elif complexity == QueryComplexity.COMPLEX:
            return IterationMode.ITERATIVE
        else:
            return IterationMode.CONTEXT_BUILDING

    def _identify_context_gaps_regex(self, text: str, parsed_query: ParsedQuery) -> List[ContextGap]:
        """Identify potential context gaps using regex patterns."""
        gaps = []
        
        # Vague terms that might need clarification
        vague_patterns = [
            (r"\ball\b", "Scope too broad - 'all' is ambiguous"),
            (r"\beverything\b", "Scope too broad - 'everything' needs specification"),
            (r"\bgeneral\b", "Too general - needs specific focus"),
            (r"\bcompletely\b", "Completeness undefined - needs criteria")
        ]
        
        for pattern, description in vague_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                gaps.append(ContextGap(
                    gap_type="ambiguous_scope",
                    description=description,
                    suggested_action="Request specific scope or criteria",
                    priority=2
                ))
        
        # Missing framework specification
        if parsed_query.category == QueryCategory.COMPLIANCE:
            frameworks_mentioned = len([e for e in parsed_query.entities.get("frameworks", [])])
            if frameworks_mentioned == 0:
                gaps.append(ContextGap(
                    gap_type="missing_information",
                    description="No specific compliance framework mentioned",
                    suggested_action="Identify applicable frameworks (ISO27001, RGPD, DORA, etc.)",
                    priority=1
                ))
        
        return gaps

    async def _analyze_iteration_requirements(self, parsed_query: ParsedQuery):
        """Analyze and finalize iteration requirements."""
        # Set required depth based on complexity and iteration mode
        if parsed_query.iteration_mode == IterationMode.DEEP_ANALYSIS:
            parsed_query.required_depth = "comprehensive"
        elif parsed_query.iteration_mode == IterationMode.ITERATIVE:
            parsed_query.required_depth = "deep"
        elif parsed_query.iteration_mode == IterationMode.CONTEXT_BUILDING:
            parsed_query.required_depth = "standard"
        
        # Generate suggested reformulations if gaps exist
        if parsed_query.context_gaps:
            parsed_query.suggested_reformulations = await self._generate_reformulations(parsed_query)

    async def _generate_reformulations(self, parsed_query: ParsedQuery) -> List[str]:
        """Generate suggested query reformulations to address context gaps."""
        reformulations = []
        
        for gap in parsed_query.context_gaps:
            if gap.gap_type == "ambiguous_scope":
                # Make scope more specific
                specific_query = f"{parsed_query.query_text} - specifically focusing on {', '.join(parsed_query.focus_areas) if parsed_query.focus_areas else 'key areas'}"
                reformulations.append(specific_query)
            
            elif gap.gap_type == "missing_information":
                # Add missing context
                if "framework" in gap.description.lower():
                    framework_query = f"{parsed_query.query_text} for ISO27001, RGPD, and DORA frameworks"
                    reformulations.append(framework_query)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_reformulations = []
        for reformulation in reformulations:
            if reformulation not in seen:
                seen.add(reformulation)
                unique_reformulations.append(reformulation)
        
        return unique_reformulations

    def _extract_entities_enhanced(self, text: str) -> Dict[str, Any]:
        """Enhanced entity extraction with GRC-specific entities."""
        entities = {}
        
        # Use base entity patterns
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if entity_type == "date":
                    # Flatten date tuple matches
                    entities[entity_type] = [match[0] if match[0] else match[1] for match in matches if any(match)]
                else:
                    entities[entity_type] = matches
        
        return entities

    def _extract_keywords_enhanced(self, text: str) -> List[str]:
        """Enhanced keyword extraction for GRC context."""
        # Base keyword extraction
        keywords = self._extract_keywords(text)
        
        # Add GRC-specific keywords
        grc_keywords = [
            "compliance", "audit", "assessment", "framework", "standard",
            "policy", "procedure", "control", "risk", "governance",
            "certification", "gap analysis", "remediation", "monitoring"
        ]
        
        text_lower = text.lower()
        for keyword in grc_keywords:
            if keyword in text_lower and keyword not in keywords:
                keywords.append(keyword)
        
        return keywords

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities from the query text using regex patterns.
        
        Args:
            text: The query text
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Apply entity patterns
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                # Some patterns return tuples, flatten to strings
                clean_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        # Take first non-empty group
                        clean_match = next((m for m in match if m), "")
                    else:
                        clean_match = match
                    clean_matches.append(clean_match)
                
                entities[entity_type] = clean_matches
                
        return entities
        
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from the query text using regex patterns.
        
        Args:
            text: The query text
            
        Returns:
            List of extracted keywords
        """
        keywords = []
        
        # Apply all keyword patterns
        for category, patterns in self.keyword_patterns.items():
            for pattern in patterns:
                matches = re.findall(rf"\b{pattern}\b", text, re.IGNORECASE)
                keywords.extend(matches)
                
        # Remove duplicates and convert to lowercase
        keywords = list(set([kw.lower() for kw in keywords]))
        
        return keywords
        
    def _classify_category(self, text: str, keywords: List[str]) -> QueryCategory:
        """
        Classify the query into a category using keyword matching.
        
        Args:
            text: The query text
            keywords: Extracted keywords
            
        Returns:
            The query category
        """
        # Count keywords by category
        category_counts = {category: 0 for category in QueryCategory}
        
        for kw in keywords:
            for category, patterns in self.keyword_patterns.items():
                if any(re.search(rf"\b{pattern}\b", kw, re.IGNORECASE) for pattern in patterns):
                    category_counts[category] += 1
        
        # Find category with highest keyword count
        max_count = 0
        max_category = QueryCategory.GENERAL
        
        for category, count in category_counts.items():
            if count > max_count:
                max_count = count
                max_category = category
                
        return max_category
        
    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """
        Extract parameters from the query text using regex patterns.
        
        Args:
            text: The query text
            
        Returns:
            Dictionary of extracted parameters
        """
        params = {}
        
        # Look for key-value patterns like "key: value" or "key=value"
        kv_patterns = [
            r'(\w+):\s*"([^"]+)"',  # key: "value"
            r"(\w+):\s*'([^']+)'",  # key: 'value'
            r'(\w+):\s*([^\s,;]+)',  # key: value
            r'(\w+)=\s*"([^"]+)"',  # key="value"
            r"(\w+)=\s*'([^']+)'",  # key='value'
            r'(\w+)=\s*([^\s,;]+)'   # key=value
        ]
        
        for pattern in kv_patterns:
            matches = re.findall(pattern, text)
            for key, value in matches:
                # Try to convert value to appropriate type
                if value.lower() == 'true':
                    params[key] = True
                elif value.lower() == 'false':
                    params[key] = False
                elif value.isdigit():
                    params[key] = int(value)
                elif re.match(r'^-?\d+(\.\d+)?$', value):
                    params[key] = float(value)
                else:
                    params[key] = value
                    
        return params 