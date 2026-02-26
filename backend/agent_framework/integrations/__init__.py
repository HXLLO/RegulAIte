"""
Integration modules for the RegulAIte Agent Framework.

This package contains integrations with various external systems and services.
"""

# Import core integrations that have minimal dependencies
from .llm_integration import get_llm_integration

# Import other integrations with try/except to handle missing dependencies
__all__ = ["get_llm_integration"]

try:
    from .rag_integration import get_rag_integration
    __all__.append("get_rag_integration")
except ImportError:
    pass

try:
    from .chat_integration import get_chat_integration
    __all__.append("get_chat_integration")
except ImportError:
    pass 