# plugins/regul_aite/backend/unstructured_parser/__init__.py
"""
Document parser module for RegulAite.
This module provides functionality to parse and extract content from various document types.
"""

from .document_parser import DocumentParser
from .base_parser import BaseParser

# Import MetadataParser to make it available from the parser module
from data_enrichment.metadata_parser import MetadataParser

__all__ = ["DocumentParser", "BaseParser"]
