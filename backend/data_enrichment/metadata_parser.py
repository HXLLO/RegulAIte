"""
Metadata parser for documents in RegulAIte.
"""

import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MetadataParser:
    """Simple metadata parser for document processing."""
    
    def __init__(self):
        """Initialize metadata parser."""
        logger.info("Initializing metadata parser")
    
    def parse_metadata(self, doc_id: str, document: Any, mime_type: str = None) -> Dict[str, Any]:
        """
        Parse metadata from a document.
        
        Args:
            doc_id: Document ID
            document: Document to parse metadata from
            mime_type: MIME type of document
            
        Returns:
            Dictionary of metadata
        """
        # Basic metadata
        metadata = {
            "doc_id": doc_id,
            "timestamp": time.time(),
            "mime_type": mime_type or "text/plain",
        }
        
        # If the document has metadata, add it
        if hasattr(document, "metadata"):
            metadata.update(document.metadata)
            
        return metadata 