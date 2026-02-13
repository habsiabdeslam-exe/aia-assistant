"""
Structured RAG Retrieval Service (Stage 2)

Executes targeted queries against Azure AI Search for specific governance domains.
Organizes retrieved knowledge by domain for downstream consumption.
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.search_service import search_service
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class StructuredRAGRetriever:
    """
    Executes structured RAG queries for specific governance domains.
    Returns organized knowledge base context for TAD generation.
    """
    
    def __init__(self):
        self.search_service = search_service
        self.embedding_service = embedding_service
        
        # Define structured queries for each domain
        self.rag_queries = {
            "naming_conventions": {
                "resource_groups": "resource group naming convention private paas RG pattern GCCC",
                "vnets": "virtual network vnet naming convention pattern azure",
                "subnets": "subnet naming convention pattern network",
                "security_groups": "entra id security group naming convention pattern azure ad",
                "key_vaults": "key vault naming convention pattern secrets",
                "storage": "storage account naming convention pattern blob"
            },
            "governance": {
                "tagging": "azure tagging policy standard mandatory tags governance",
                "rbac": "role based access control rbac model azure permissions",
                "security_baseline": "security baseline standards controls compliance azure"
            },
            "architecture": {
                "network_segmentation": "network segmentation hub spoke topology vnet peering",
                "iam_model": "identity access management model entra id azure ad authentication",
                "reference_patterns": "reference architecture pattern best practices azure"
            }
        }
    
    async def retrieve_all(self, normalized_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all RAG queries and organize results by domain.
        
        Args:
            normalized_context: Normalized project context
            
        Returns:
            Organized RAG data by domain
        """
        try:
            logger.info("Starting structured RAG retrieval")
            
            rag_data = {
                "naming_conventions": {},
                "governance": {},
                "architecture": {},
                "metadata": {
                    "total_queries": 0,
                    "successful_queries": 0,
                    "failed_queries": 0
                }
            }
            
            # Retrieve naming conventions
            logger.info("Retrieving naming conventions")
            rag_data["naming_conventions"] = await self._retrieve_naming_conventions()
            
            # Retrieve governance standards
            logger.info("Retrieving governance standards")
            rag_data["governance"] = await self._retrieve_governance()
            
            # Retrieve architecture patterns
            logger.info("Retrieving architecture patterns")
            rag_data["architecture"] = await self._retrieve_architecture(normalized_context)
            
            # Calculate metadata
            total = 0
            successful = 0
            for domain in ["naming_conventions", "governance", "architecture"]:
                for subdomain, data in rag_data[domain].items():
                    total += 1
                    if data.get("found"):
                        successful += 1
            
            rag_data["metadata"]["total_queries"] = total
            rag_data["metadata"]["successful_queries"] = successful
            rag_data["metadata"]["failed_queries"] = total - successful
            
            logger.info(f"RAG retrieval completed. {successful}/{total} queries successful")
            
            return rag_data
            
        except Exception as e:
            logger.error(f"Error in structured RAG retrieval: {e}")
            raise
    
    async def _retrieve_naming_conventions(self) -> Dict[str, Any]:
        """Retrieve all naming convention standards"""
        
        naming_data = {}
        
        for resource_type, query in self.rag_queries["naming_conventions"].items():
            try:
                logger.debug(f"Querying naming convention for {resource_type}")
                
                # Generate embedding
                query_vector = self.embedding_service.generate_embedding(query)
                
                # Execute hybrid search
                results = self.search_service.hybrid_search(
                    query_text=query,
                    query_vector=query_vector,
                    top_k=5
                )
                
                if results:
                    naming_data[resource_type] = {
                        "found": True,
                        "query": query,
                        "chunks": results,
                        "top_score": results[0].get("score", 0) if results else 0,
                        "source_files": list(set([r.get("title", "Unknown") for r in results]))
                    }
                    logger.info(f"Found {len(results)} chunks for {resource_type} naming convention")
                else:
                    naming_data[resource_type] = {
                        "found": False,
                        "query": query,
                        "chunks": [],
                        "error": f"{resource_type} naming convention not found in AI Search index"
                    }
                    logger.warning(f"No results for {resource_type} naming convention")
                    
            except Exception as e:
                logger.error(f"Error retrieving {resource_type} naming convention: {e}")
                naming_data[resource_type] = {
                    "found": False,
                    "query": query,
                    "chunks": [],
                    "error": str(e)
                }
        
        return naming_data
    
    async def _retrieve_governance(self) -> Dict[str, Any]:
        """Retrieve governance standards (tagging, RBAC, security baseline)"""
        
        governance_data = {}
        
        for standard_type, query in self.rag_queries["governance"].items():
            try:
                logger.debug(f"Querying governance standard: {standard_type}")
                
                # Generate embedding
                query_vector = self.embedding_service.generate_embedding(query)
                
                # Execute hybrid search
                results = self.search_service.hybrid_search(
                    query_text=query,
                    query_vector=query_vector,
                    top_k=5
                )
                
                if results:
                    governance_data[standard_type] = {
                        "found": True,
                        "query": query,
                        "chunks": results,
                        "top_score": results[0].get("score", 0) if results else 0,
                        "source_files": list(set([r.get("title", "Unknown") for r in results]))
                    }
                    logger.info(f"Found {len(results)} chunks for {standard_type} governance standard")
                else:
                    governance_data[standard_type] = {
                        "found": False,
                        "query": query,
                        "chunks": [],
                        "error": f"{standard_type} governance standard not found in AI Search index"
                    }
                    logger.warning(f"No results for {standard_type} governance standard")
                    
            except Exception as e:
                logger.error(f"Error retrieving {standard_type} governance standard: {e}")
                governance_data[standard_type] = {
                    "found": False,
                    "query": query,
                    "chunks": [],
                    "error": str(e)
                }
        
        return governance_data
    
    async def _retrieve_architecture(self, normalized_context: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve architecture patterns and reference architectures"""
        
        architecture_data = {}
        
        for pattern_type, query_template in self.rag_queries["architecture"].items():
            try:
                # Customize query based on project context
                query = query_template
                if pattern_type == "reference_patterns":
                    project_type = self._infer_project_type(normalized_context)
                    query = query_template.replace("{project_type}", project_type)
                
                logger.debug(f"Querying architecture pattern: {pattern_type}")
                
                # Generate embedding
                query_vector = self.embedding_service.generate_embedding(query)
                
                # Execute hybrid search
                results = self.search_service.hybrid_search(
                    query_text=query,
                    query_vector=query_vector,
                    top_k=5
                )
                
                if results:
                    architecture_data[pattern_type] = {
                        "found": True,
                        "query": query,
                        "chunks": results,
                        "top_score": results[0].get("score", 0) if results else 0,
                        "source_files": list(set([r.get("title", "Unknown") for r in results]))
                    }
                    logger.info(f"Found {len(results)} chunks for {pattern_type} architecture pattern")
                else:
                    architecture_data[pattern_type] = {
                        "found": False,
                        "query": query,
                        "chunks": [],
                        "error": f"{pattern_type} architecture pattern not found in AI Search index"
                    }
                    logger.warning(f"No results for {pattern_type} architecture pattern")
                    
            except Exception as e:
                logger.error(f"Error retrieving {pattern_type} architecture pattern: {e}")
                architecture_data[pattern_type] = {
                    "found": False,
                    "query": query,
                    "chunks": [],
                    "error": str(e)
                }
        
        return architecture_data
    
    def _infer_project_type(self, normalized_context: Dict[str, Any]) -> str:
        """
        Infer project type from context for targeted architecture pattern search.
        
        Returns:
            Project type keyword (e.g., "iot", "data analytics", "web application")
        """
        
        project_name = normalized_context.get("project", {}).get("full_name", "").lower()
        description = normalized_context.get("project", {}).get("description", "").lower()
        
        combined_text = f"{project_name} {description}"
        
        # Pattern matching for common project types
        if any(keyword in combined_text for keyword in ["iot", "internet of things", "sensor", "device"]):
            return "iot platform"
        elif any(keyword in combined_text for keyword in ["data", "analytics", "bi", "warehouse", "lake"]):
            return "data analytics"
        elif any(keyword in combined_text for keyword in ["web", "portal", "website", "frontend"]):
            return "web application"
        elif any(keyword in combined_text for keyword in ["api", "microservice", "service"]):
            return "microservices"
        elif any(keyword in combined_text for keyword in ["mobile", "app"]):
            return "mobile application"
        elif any(keyword in combined_text for keyword in ["ai", "ml", "machine learning", "artificial intelligence"]):
            return "ai ml platform"
        else:
            return "cloud application"
    
    def get_rag_summary(self, rag_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary of RAG retrieval results.
        
        Returns:
            Summary with found/missing standards
        """
        
        summary = {
            "found": [],
            "missing": [],
            "coverage_score": 0.0
        }
        
        total = 0
        found = 0
        
        for domain in ["naming_conventions", "governance", "architecture"]:
            for subdomain, data in rag_data.get(domain, {}).items():
                total += 1
                if data.get("found"):
                    found += 1
                    summary["found"].append(f"{domain}.{subdomain}")
                else:
                    summary["missing"].append(f"{domain}.{subdomain}")
        
        summary["coverage_score"] = found / total if total > 0 else 0.0
        
        return summary


# Singleton instance
structured_rag_retriever = StructuredRAGRetriever()
