"""
EmbeddingsModel for text embedding generation in RegulAIte.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Set maximum retry attempts
MAX_RETRIES = 3

class EmbeddingsModel:
    """Model for generating text embeddings for vector search."""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        cache_dir: Optional[str] = None,
        device: str = "cpu",
        normalize_embeddings: bool = True
    ):
        """
        Initialize the embeddings model.
        
        Args:
            model_name: Name of the model to use for embeddings
            cache_dir: Directory to cache models
            device: Device to run inference on (cpu or cuda)
            normalize_embeddings: Whether to normalize embeddings
        """
        self.model_name = model_name
        self.device = device
        self.normalize_embeddings = normalize_embeddings
        self.cache_dir = cache_dir or os.getenv("MODEL_CACHE_DIR", "./model_cache")
        
        # Lazy load the model - it will be loaded on first use
        self._model = None
        self._tokenizer = None
        
        logger.info(f"Initialized EmbeddingsModel with model {model_name} on {device}")

    def _load_model(self):
        """Load the model and tokenizer if not already loaded."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                
                # Check if device has CUDA
                import torch
                if self.device == "cuda" and not torch.cuda.is_available():
                    logger.warning("CUDA not available, falling back to CPU")
                    self.device = "cpu"
                
                self._model = SentenceTransformer(
                    self.model_name,
                    cache_folder=self.cache_dir,
                    device=self.device
                )
                
                logger.info(f"Loaded embedding model {self.model_name}")
            except ImportError:
                logger.error("Cannot load SentenceTransformer. Make sure sentence-transformers is installed.")
                # Create a dummy model that returns random embeddings
                self._model = DummyEmbeddingModel(dim=384)
            except Exception as e:
                logger.error(f"Error loading embedding model: {str(e)}")
                # Create a dummy model that returns random embeddings
                self._model = DummyEmbeddingModel(dim=384)
    
    def get_text_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text.
        
        Args:
            text: Text to embed
            
        Returns:
            Text embedding as a list of floats
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            dim = 384  # Default dimension for BGE models
            return [0.0] * dim
        
        # Load model if not already loaded
        if self._model is None:
            self._load_model()
        
        # Retry mechanism for embedding generation
        for attempt in range(MAX_RETRIES):
            try:
                if isinstance(self._model, DummyEmbeddingModel):
                    embedding = self._model.encode(text)
                else:
                    embedding = self._model.encode(
                        text,
                        normalize_embeddings=self.normalize_embeddings
                    )
                
                # Convert to list of floats
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                
                return embedding
            except Exception as e:
                logger.warning(f"Attempt {attempt+1}/{MAX_RETRIES} failed to generate embedding: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"All attempts to generate embedding failed: {str(e)}")
                    # Return zero vector as fallback
                    dim = 384  # Default dimension for BGE models
                    return [0.0] * dim
        
        # This should never be reached due to the return in the last retry
        return [0.0] * 384


class DummyEmbeddingModel:
    """Dummy embedding model that returns random embeddings."""
    
    def __init__(self, dim: int = 384):
        """
        Initialize the dummy embedding model.
        
        Args:
            dim: Dimension of embeddings to generate
        """
        self.dim = dim
        logger.warning(f"Using dummy embedding model with dimension {dim}")
    
    def encode(self, text: str, **kwargs) -> List[float]:
        """
        Generate a random embedding.
        
        Args:
            text: Text to embed (ignored)
            **kwargs: Additional arguments (ignored)
            
        Returns:
            Random embedding
        """
        # Use fixed seed based on text to ensure consistent embeddings for same text
        import hashlib
        text_hash = int(hashlib.md5(text.encode()).hexdigest(), 16) % 10000
        np.random.seed(text_hash)
        
        # Generate random embedding and normalize
        embedding = np.random.normal(0, 1, self.dim)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.tolist() 