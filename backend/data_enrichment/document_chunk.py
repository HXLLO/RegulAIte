"""
DocumentChunk class for representing document chunks in RegulAIte.
"""

import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """
    Represents a chunk of a document with metadata and embedding.
    
    This class is used for storing and retrieving document chunks
    from vector databases like Qdrant.
    """
    
    chunk_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    doc_id: str
    text: str
    content: str = ""  # For compatibility with some systems that use content instead of text
    embedding: List[float] = []
    metadata: Dict[str, Any] = {}
    page_num: Optional[int] = None
    element_type: str = "text"
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure content and text are synchronized
        if not self.content and self.text:
            self.content = self.text
        elif not self.text and self.content:
            self.text = self.content
            
        # Ensure doc_id is in metadata
        if "doc_id" not in self.metadata:
            self.metadata["doc_id"] = self.doc_id
            
        # Ensure chunk_id is in metadata (as string)
        if "chunk_id" not in self.metadata:
            self.metadata["chunk_id"] = str(self.chunk_id)
            
        # Store original string ID if needed
        if "chunk_string_id" not in self.metadata:
            self.metadata["chunk_string_id"] = f"{self.doc_id}_chunk_{str(self.chunk_id)[-8:]}"
            
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the chunk to a dictionary for storage.
        
        Returns:
            Dictionary representation of the chunk
        """
        return {
            "chunk_id": str(self.chunk_id),
            "doc_id": self.doc_id,
            "text": self.text,
            "content": self.content,
            "metadata": self.metadata,
            "page_num": self.page_num,
            "element_type": self.element_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a chunk from a dictionary.
        
        Args:
            data: Dictionary representation of a chunk
            
        Returns:
            DocumentChunk instance
        """
        # Handle potential fields with different names
        if "content" in data and not data.get("text"):
            data["text"] = data["content"]
        if "text" in data and not data.get("content"):
            data["content"] = data["text"]
            
        # Ensure metadata is a dictionary
        if "metadata" not in data:
            data["metadata"] = {}

        # Convert chunk_id to UUID if it's a string
        if "chunk_id" in data and isinstance(data["chunk_id"], str):
            try:
                data["chunk_id"] = uuid.UUID(data["chunk_id"])
            except ValueError:
                # If string is not a valid UUID, generate a new one
                data["chunk_id"] = uuid.uuid4()
            
        return cls(**data) 