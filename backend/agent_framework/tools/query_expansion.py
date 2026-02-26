"""
Query Expansion Module for GRC-focused RAG systems.

This module provides intelligent query expansion capabilities specifically designed
for Governance, Risk, and Compliance (GRC) content retrieval.
"""
from typing import Dict, List, Optional, Set, Any
import logging
import re
from dataclasses import dataclass

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class QueryExpansionResult:
    """Result of query expansion operation."""
    original_query: str
    expanded_terms: List[str]
    synonyms: Dict[str, List[str]]
    framework_terms: List[str]
    expansion_strategy: str
    confidence_score: float

class GRCQueryExpander:
    """
    GRC-specific query expansion system.
    
    Expands queries with domain-specific synonyms, framework terminology,
    and compliance-related terms to improve retrieval accuracy.
    """
    
    def __init__(self):
        """Initialize the GRC Query Expander with domain knowledge."""
        self.grc_synonyms = {
            # Risk Management Terms
            "risk": ["threat", "vulnerability", "hazard", "exposure", "danger"],
            "assessment": ["evaluation", "analysis", "review", "appraisal", "examination"],
            "mitigation": ["reduction", "control", "management", "treatment", "remediation"],
            "impact": ["consequence", "effect", "result", "outcome", "damage"],
            "likelihood": ["probability", "chance", "possibility", "risk level"],
            
            # Compliance Terms
            "compliance": ["conformity", "adherence", "observance", "accordance", "alignment"],
            "requirement": ["obligation", "mandate", "rule", "regulation", "standard"],
            "audit": ["review", "inspection", "examination", "assessment", "evaluation"],
            "evidence": ["proof", "documentation", "record", "attestation", "verification"],
            "non-compliance": ["violation", "breach", "infringement", "non-conformity"],
            
            # Security Terms
            "security": ["protection", "safety", "defense", "safeguard", "cybersecurity"],
            "control": ["safeguard", "countermeasure", "protection", "mechanism", "procedure"],
            "incident": ["event", "occurrence", "breach", "violation", "compromise"],
            "vulnerability": ["weakness", "flaw", "gap", "exposure", "susceptibility"],
            "threat": ["risk", "danger", "hazard", "menace", "attack vector"],
            
            # Governance Terms
            "governance": ["oversight", "management", "administration", "supervision", "stewardship"],
            "policy": ["procedure", "guideline", "standard", "rule", "directive"],
            "framework": ["standard", "methodology", "approach", "model", "structure"],
            "monitoring": ["surveillance", "tracking", "oversight", "observation", "review"],
            
            # Document Types
            "report": ["document", "assessment", "evaluation", "analysis", "summary"],
            "procedure": ["process", "method", "protocol", "workflow", "instruction"],
            "policy": ["guideline", "standard", "rule", "directive", "principle"],
        }
        
        self.framework_mappings = {
            # ISO 27001 Terms
            "iso27001": ["information security", "isms", "security controls", "risk management"],
            "iso_27001": ["information security", "isms", "security controls", "risk management"],
            
            # GDPR/RGPD Terms  
            "gdpr": ["data protection", "privacy", "personal data", "data subject rights"],
            "rgpd": ["data protection", "privacy", "personal data", "data subject rights"],
            
            # DORA Terms
            "dora": ["operational resilience", "digital resilience", "ict risk"],
            
            # SOX Terms
            "sox": ["financial controls", "internal controls", "financial reporting"],
            "sarbanes": ["financial controls", "internal controls", "sox"],
            
            # NIST Terms
            "nist": ["cybersecurity framework", "security controls", "risk management"],
            
            # PCI DSS Terms
            "pci": ["payment security", "card data", "payment processing"],
        }
        
        self.contextual_expansions = {
            "access": ["authentication", "authorization", "identity management", "user access"],
            "data": ["information", "records", "database", "dataset", "content"],
            "network": ["infrastructure", "connectivity", "communication", "system"],
            "breach": ["incident", "compromise", "violation", "security event"],
            "training": ["awareness", "education", "competency", "skills development"],
        }
        
        # Statistics tracking
        self.expansion_stats = {
            "total_expansions": 0,
            "successful_expansions": 0,
            "average_expansion_ratio": 0.0,
            "most_expanded_terms": {}
        }

    async def expand_query(
        self,
        query: str,
        strategy: str = "comprehensive",
        max_expansions: int = 10,
        include_frameworks: bool = True
    ) -> QueryExpansionResult:
        """
        Expand a query with GRC-specific terms and synonyms.
        
        Args:
            query: Original query string
            strategy: Expansion strategy ("conservative", "balanced", "comprehensive")
            max_expansions: Maximum number of expanded terms
            include_frameworks: Whether to include framework-specific expansions
            
        Returns:
            QueryExpansionResult with expanded terms and metadata
        """
        logger.info(f"Expanding query: '{query}' with strategy: {strategy}")
        
        try:
            # Normalize and tokenize query
            normalized_query = self._normalize_query(query)
            tokens = self._tokenize_query(normalized_query)
            
            # Extract framework references
            framework_terms = []
            if include_frameworks:
                framework_terms = self._extract_framework_terms(tokens)
            
            # Generate synonyms based on strategy
            synonyms = {}
            expanded_terms = []
            
            for token in tokens:
                token_lower = token.lower()
                
                # Direct synonym mapping
                if token_lower in self.grc_synonyms:
                    token_synonyms = self._get_synonyms_by_strategy(
                        token_lower, strategy, max_expansions
                    )
                    synonyms[token] = token_synonyms
                    expanded_terms.extend(token_synonyms)
                
                # Contextual expansion
                if token_lower in self.contextual_expansions:
                    contextual_terms = self.contextual_expansions[token_lower]
                    if strategy == "comprehensive":
                        expanded_terms.extend(contextual_terms)
                    elif strategy == "balanced" and len(contextual_terms) > 0:
                        expanded_terms.extend(contextual_terms[:2])
            
            # Add framework-specific terms
            if framework_terms and include_frameworks:
                for framework in framework_terms:
                    if framework.lower() in self.framework_mappings:
                        framework_expansions = self.framework_mappings[framework.lower()]
                        expanded_terms.extend(framework_expansions)
            
            # Remove duplicates and limit results
            expanded_terms = list(set(expanded_terms))[:max_expansions]
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(query, expanded_terms, synonyms)
            
            # Update statistics
            self._update_stats(query, expanded_terms)
            
            result = QueryExpansionResult(
                original_query=query,
                expanded_terms=expanded_terms,
                synonyms=synonyms,
                framework_terms=framework_terms,
                expansion_strategy=strategy,
                confidence_score=confidence_score
            )
            
            logger.info(
                f"Query expansion complete: {len(expanded_terms)} terms added, "
                f"confidence: {confidence_score:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error expanding query '{query}': {str(e)}")
            # Return original query as fallback
            return QueryExpansionResult(
                original_query=query,
                expanded_terms=[],
                synonyms={},
                framework_terms=[],
                expansion_strategy=strategy,
                confidence_score=0.0
            )

    def _normalize_query(self, query: str) -> str:
        """Normalize query text for processing."""
        # Remove extra whitespace and normalize case
        normalized = re.sub(r'\s+', ' ', query.strip())
        return normalized

    def _tokenize_query(self, query: str) -> List[str]:
        """Tokenize query into meaningful terms."""
        # Simple tokenization - can be enhanced with NLP libraries
        tokens = re.findall(r'\b\w+\b', query)
        # Filter out very short tokens
        return [token for token in tokens if len(token) > 2]

    def _extract_framework_terms(self, tokens: List[str]) -> List[str]:
        """Extract framework references from tokens."""
        framework_terms = []
        for token in tokens:
            token_lower = token.lower()
            # Check direct framework matches
            for framework in self.framework_mappings.keys():
                if framework in token_lower or token_lower in framework:
                    framework_terms.append(token)
                    break
        return framework_terms

    def _get_synonyms_by_strategy(
        self, 
        term: str, 
        strategy: str, 
        max_count: int
    ) -> List[str]:
        """Get synonyms based on expansion strategy."""
        synonyms = self.grc_synonyms.get(term, [])
        
        if strategy == "conservative":
            return synonyms[:2]  # Top 2 synonyms
        elif strategy == "balanced":
            return synonyms[:4]  # Top 4 synonyms
        else:  # comprehensive
            return synonyms[:max_count]

    def _calculate_confidence(
        self, 
        original_query: str, 
        expanded_terms: List[str], 
        synonyms: Dict[str, List[str]]
    ) -> float:
        """Calculate confidence score for expansion quality."""
        if not expanded_terms:
            return 0.0
            
        # Base confidence on number of terms expanded and synonym quality
        base_score = min(len(expanded_terms) / 10.0, 1.0)  # Normalize to 0-1
        
        # Boost for framework-specific terms
        framework_boost = 0.0
        for term in expanded_terms:
            if any(fw_term in term.lower() for fw_terms in self.framework_mappings.values() 
                   for fw_term in fw_terms):
                framework_boost += 0.1
        
        # Penalize for over-expansion
        over_expansion_penalty = max(0, (len(expanded_terms) - 8) * 0.05)
        
        confidence = min(base_score + framework_boost - over_expansion_penalty, 1.0)
        return max(confidence, 0.0)

    def _update_stats(self, query: str, expanded_terms: List[str]):
        """Update expansion statistics."""
        self.expansion_stats["total_expansions"] += 1
        
        if expanded_terms:
            self.expansion_stats["successful_expansions"] += 1
            
            # Update expansion ratio
            current_ratio = len(expanded_terms) / len(query.split())
            total_expansions = self.expansion_stats["total_expansions"]
            current_avg = self.expansion_stats["average_expansion_ratio"]
            self.expansion_stats["average_expansion_ratio"] = (
                (current_avg * (total_expansions - 1) + current_ratio) / total_expansions
            )
            
            # Track most expanded terms
            for term in expanded_terms:
                if term in self.expansion_stats["most_expanded_terms"]:
                    self.expansion_stats["most_expanded_terms"][term] += 1
                else:
                    self.expansion_stats["most_expanded_terms"][term] = 1

    def get_expansion_statistics(self) -> Dict[str, Any]:
        """Get query expansion statistics."""
        return self.expansion_stats.copy()

    def add_custom_synonyms(self, term: str, synonyms: List[str]):
        """Add custom synonyms for domain-specific terms."""
        if term.lower() not in self.grc_synonyms:
            self.grc_synonyms[term.lower()] = []
        self.grc_synonyms[term.lower()].extend(synonyms)
        logger.info(f"Added {len(synonyms)} custom synonyms for term: {term}")

    def add_framework_mapping(self, framework: str, terms: List[str]):
        """Add custom framework term mapping."""
        self.framework_mappings[framework.lower()] = terms
        logger.info(f"Added framework mapping for: {framework}")


# Global instance
_query_expander = None

def get_query_expander() -> GRCQueryExpander:
    """Get the global query expander instance."""
    global _query_expander
    if _query_expander is None:
        _query_expander = GRCQueryExpander()
    return _query_expander 