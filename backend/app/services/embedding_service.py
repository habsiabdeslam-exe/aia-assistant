"""
Embedding Service

Wrapper around Azure OpenAI embedding generation.
Provides a simple interface for generating embeddings used in RAG retrieval.
"""

import logging
from typing import List
from app.services.openai_service import get_openai_service

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating embeddings using Azure OpenAI.
    Wrapper around OpenAI service for cleaner imports.
    """
    
    def __init__(self):
        self.openai_service = get_openai_service()
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for the given text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (1536 dimensions for text-embedding-ada-002)
        """
        try:
            return self.openai_service.create_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise


# Singleton instance
embedding_service = EmbeddingService()
