"""
Agent Framework Modules - Modules spécialisés pour l'analyse GRC.

Chaque module fournit une expertise spécialisée pour différents aspects
de l'analyse de gouvernance, risque et conformité.
"""

# Import the organization config module which is working
from .organization_config import (
    OrganizationConfigManager,
    OrganizationType,
    RegulatorySector,
    ComplianceFramework,
    OrganizationProfile,
    get_organization_config_manager
)

# Framework Parser avec support multi-frameworks (from tools directory)
from ..tools.framework_parser import FrameworkParser, get_framework_parser

# Import specialized modules with error handling
try:
    from .risk_assessment_module import RiskAssessmentModule, get_risk_assessment_module
    RISK_ASSESSMENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import RiskAssessmentModule: {e}")
    RISK_ASSESSMENT_AVAILABLE = False

try:
    from .compliance_analysis_module import ComplianceAnalysisModule, get_compliance_analysis_module
    COMPLIANCE_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import ComplianceAnalysisModule: {e}")
    COMPLIANCE_ANALYSIS_AVAILABLE = False

try:
    from .governance_analysis_module import GovernanceAnalysisModule, get_governance_analysis_module
    GOVERNANCE_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import GovernanceAnalysisModule: {e}")
    GOVERNANCE_ANALYSIS_AVAILABLE = False

try:
    from .gap_analysis_module import GapAnalysisModule, get_gap_analysis_module
    GAP_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import GapAnalysisModule: {e}")
    GAP_ANALYSIS_AVAILABLE = False

try:
    from .document_finder_agent import DocumentFinderAgent
    DOCUMENT_FINDER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import DocumentFinderAgent: {e}")
    DOCUMENT_FINDER_AVAILABLE = False

# Build __all__ dynamically based on available modules
__all__ = [
    # Organization Config (working)
    "OrganizationConfigManager",
    "OrganizationType", 
    "RegulatorySector",
    "ComplianceFramework",
    "OrganizationProfile",
    "get_organization_config_manager",
    
    # Framework Parser
    "FrameworkParser",
    "get_framework_parser",
]

# Add available modules to __all__
if RISK_ASSESSMENT_AVAILABLE:
    __all__.extend(["RiskAssessmentModule", "get_risk_assessment_module"])

if COMPLIANCE_ANALYSIS_AVAILABLE:
    __all__.extend(["ComplianceAnalysisModule", "get_compliance_analysis_module"])

if GOVERNANCE_ANALYSIS_AVAILABLE:
    __all__.extend(["GovernanceAnalysisModule", "get_governance_analysis_module"])

if GAP_ANALYSIS_AVAILABLE:
    __all__.extend(["GapAnalysisModule", "get_gap_analysis_module"])

if DOCUMENT_FINDER_AVAILABLE:
    __all__.extend(["DocumentFinderAgent"]) 