import logging
from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from app.config import config

logger = logging.getLogger(__name__)


class AzureSearchService:
    def __init__(self):
        """Initialize Azure Search service using Config (Key Vault in production, env vars in development)."""
        try:
            self.endpoint = config.azure_search_endpoint
            self.api_key = config.azure_search_key
            self.index_name = config.azure_search_index_name
            
            self.search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=AzureKeyCredential(self.api_key)
            )
            
            logger.info(f"AzureSearchService initialized for index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize AzureSearchService: {e}")
            raise
    
    def vector_search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search in Azure AI Search.
        Returns top_k most relevant chunks.
        """
        try:
            results = self.search_client.search(
                search_text=None,
                vector_queries=[{
                    "kind": "vector",
                    "vector": query_vector,
                    "fields": "text_vector",
                    "k": top_k
                }],
                select=["chunk", "title"],
                top=top_k
            )
            
            chunks = []
            for result in results:
                chunks.append({
                    "content": result.get("chunk", ""),
                    "score": result.get("@search.score", 0.0),
                    "metadata": {},
                    "title": result.get("title", "")
                })
            
            return chunks
        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
            return []
    
    def hybrid_search(self, query_text: str, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (keyword + vector) in Azure AI Search.
        Combines semantic search with vector similarity for best results.
        """
        try:
            logger.info(f"Performing hybrid search with query: '{query_text[:100]}...' (top_k={top_k})")
            
            results = self.search_client.search(
                search_text=query_text,
                vector_queries=[{
                    "kind": "vector",
                    "vector": query_vector,
                    "fields": "text_vector",
                    "k": top_k
                }],
                select=["chunk", "title"],
                top=top_k
            )
            
            chunks = []
            for result in results:
                chunks.append({
                    "content": result.get("chunk", ""),
                    "score": result.get("@search.score", 0.0),
                    "metadata": {},
                    "title": result.get("title", "")
                })
            
            logger.info(f"Hybrid search returned {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error performing hybrid search: {e}")
            return []
    
    def keyword_search(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search in Azure AI Search.
        """
        try:
            results = self.search_client.search(
                search_text=query_text,
                select=["chunk", "title"],
                top=top_k
            )
            
            chunks = []
            for result in results:
                chunks.append({
                    "content": result.get("chunk", ""),
                    "score": result.get("@search.score", 0.0),
                    "metadata": {},
                    "title": result.get("title", "")
                })
            
            return chunks
        except Exception as e:
            logger.error(f"Error performing keyword search: {e}")
            return []


# Singleton instance
search_service = AzureSearchService()
