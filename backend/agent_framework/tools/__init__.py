"""
Tool modules for the RegulAIte Agent Framework.

This package contains various tools that can be used by agents.
"""

# Import all tools to make them discoverable
from .document_finder import (
    DocumentFinder, 
    document_finder_tool, 
    get_document_finder
)
from .search_tools import (
    SearchTools,
    semantic_search_tool,
    keyword_search_tool,
    hybrid_search_tool
)
from .entity_extractor import (
    EntityExtractor,
    EntityType,
    ControlType, 
    RiskLevel,
    Control,
    Risk,
    Finding,
    Requirement,
    Asset,
    entity_extractor_tool,
    get_entity_extractor
)
from .cross_reference import (
    CrossReferenceTool,
    RelationType,
    Relationship,
    CrossReferenceResult,
    cross_reference_tool,
    get_cross_reference_tool
)
from .temporal_analyzer import (
    TemporalAnalyzer,
    TrendDirection,
    MetricType,
    TimeSeriesPoint,
    TrendAnalysis,
    TemporalReport,
    temporal_analyzer_tool,
    get_temporal_analyzer
)

# Import Framework Parser
from .framework_parser import (
    FrameworkParser,
    FrameworkType,
    RequirementType,
    ImplementationLevel,
    FrameworkRequirement,
    FrameworkMapping,
    ComplianceGap,
    framework_parser_tool,
    get_framework_parser
)

__all__ = [
    # Document Finder
    "DocumentFinder",
    "DocumentType",
    "document_finder_tool",
    "get_document_finder",
    
    # Search Tools
    "SearchTools",
    "semantic_search_tool",
    "keyword_search_tool",
    "hybrid_search_tool",
    
    # Entity Extractor
    "EntityExtractor",
    "ControlType",
    "RiskLevel",
    "EntityType",
    "Control",
    "Risk", 
    "Finding",
    "Requirement",
    "Asset",
    "entity_extractor_tool",
    "get_entity_extractor",
    
    # Cross Reference Tool
    "CrossReferenceTool",
    "RelationType",
    "Relationship",
    "CrossReferenceResult",
    "cross_reference_tool",
    "get_cross_reference_tool",
    
    # Temporal Analyzer
    "TemporalAnalyzer",
    "TrendDirection",
    "MetricType", 
    "TimeSeriesPoint",
    "TrendAnalysis",
    "TemporalReport",
    "temporal_analyzer_tool",
    "get_temporal_analyzer",
    
    # Framework Parser
    "FrameworkParser",
    "FrameworkType",
    "RequirementType",
    "ImplementationLevel",
    "FrameworkRequirement",
    "FrameworkMapping",
    "ComplianceGap",
    "framework_parser_tool",
    "get_framework_parser"
] 