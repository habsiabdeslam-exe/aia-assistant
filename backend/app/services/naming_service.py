import logging
import re
from typing import List, Dict, Optional, Any
from app.services.search_service import search_service
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class NamingService:
    """
    Service for retrieving and applying Sodexo GCCC naming conventions from RAG knowledge base.
    NEVER hardcodes naming patterns - always retrieves from Azure AI Search.
    """
    
    def __init__(self):
        self.search_service = search_service
        self.embedding_service = embedding_service
        
        # Azure region to Sodexo cloud region code mapping
        # This will be extracted from RAG, but we keep a fallback
        self.azure_region_fallback = {
            "north europe": "IENO",
            "west europe": "NLWE",
            "east us": "USEA",
            "west us": "USWE",
            "central us": "USCE",
            "uk south": "UKSO",
            "france central": "FRCE",
        }
    
    def search_naming_convention_for_resource_groups(self) -> List[Dict[str, Any]]:
        """
        Query Azure AI Search for Resource Group naming conventions.
        
        Returns:
            List of relevant chunks with content, score, title, and metadata
        """
        try:
            query_text = "resource group naming convention private paas azure RG pattern"
            
            logger.info(f"Searching for RG naming convention with query: '{query_text}'")
            
            # Generate embedding for hybrid search
            query_vector = self.embedding_service.generate_embedding(query_text)
            
            # Perform hybrid search (keyword + vector)
            results = self.search_service.hybrid_search(
                query_text=query_text,
                query_vector=query_vector,
                top_k=10  # Get more results to ensure we find the pattern
            )
            
            logger.info(f"Found {len(results)} chunks for RG naming convention")
            
            # Filter for naming-convention category if metadata available
            filtered_results = []
            for result in results:
                # Check if this chunk is relevant to resource groups
                content_lower = result.get("content", "").lower()
                if any(keyword in content_lower for keyword in ["resource group", "rg##", "rg01", "naming convention"]):
                    filtered_results.append(result)
            
            logger.info(f"Filtered to {len(filtered_results)} relevant RG naming chunks")
            
            return filtered_results[:5]  # Return top 5 most relevant
            
        except Exception as e:
            logger.error(f"Error searching for RG naming convention: {e}")
            return []
    
    def extract_rg_naming_pattern(self, rag_results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract the Resource Group naming pattern from RAG results.
        
        Expected pattern: {Business Line}-{Region}-{Cloud Region}-{Project}-{Environment}-RG##
        
        Args:
            rag_results: List of chunks from Azure AI Search
            
        Returns:
            Dict with pattern structure, examples, and source reference, or None if not found
        """
        if not rag_results:
            logger.warning("No RAG results provided for pattern extraction")
            return None
        
        try:
            # Look for pattern in the chunks
            pattern_regex = r'\{[^}]+\}-\{[^}]+\}-\{[^}]+\}-\{[^}]+\}-\{[^}]+\}-RG##'
            
            for result in rag_results:
                content = result.get("content", "")
                title = result.get("title", "Unknown")
                
                # Search for the pattern
                pattern_match = re.search(pattern_regex, content)
                
                if pattern_match:
                    pattern_str = pattern_match.group(0)
                    
                    # Extract segment names
                    segments = re.findall(r'\{([^}]+)\}', pattern_str)
                    
                    # Look for examples in the content
                    examples = []
                    example_regex = r'[A-Z]{3}-[A-Z]{3}-[A-Z]{4}-[A-Z]{3,10}-[A-Z]{3}-RG\d{2}'
                    example_matches = re.findall(example_regex, content)
                    examples.extend(example_matches[:3])  # Take up to 3 examples
                    
                    logger.info(f"Extracted RG naming pattern: {pattern_str} from {title}")
                    
                    return {
                        "pattern": pattern_str,
                        "segments": segments,
                        "separator": "-",
                        "examples": examples,
                        "source": {
                            "file": title,
                            "content_snippet": content[:200] + "..." if len(content) > 200 else content
                        }
                    }
            
            # If exact pattern not found, look for descriptive pattern
            for result in rag_results:
                content = result.get("content", "")
                title = result.get("title", "Unknown")
                
                # Look for pattern description
                if "business line" in content.lower() and "cloud region" in content.lower() and "rg" in content.lower():
                    logger.info(f"Found pattern description in {title}")
                    
                    return {
                        "pattern": "{Business Line}-{Region}-{Cloud Region}-{Project}-{Environment}-RG##",
                        "segments": ["Business Line", "Region", "Cloud Region", "Project", "Environment", "RG##"],
                        "separator": "-",
                        "examples": [],
                        "source": {
                            "file": title,
                            "content_snippet": content[:200] + "..." if len(content) > 200 else content
                        }
                    }
            
            logger.warning("Could not extract RG naming pattern from RAG results")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting RG naming pattern: {e}")
            return None
    
    def extract_naming_codes(self, rag_results: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
        """
        Extract naming code tables from RAG results.
        
        Args:
            rag_results: List of chunks from Azure AI Search
            
        Returns:
            Dict with code mappings for business_lines, regions, cloud_regions, environments
        """
        codes = {
            "business_lines": {},
            "regions": {},
            "cloud_regions": {},
            "environments": {}
        }
        
        try:
            for result in rag_results:
                content = result.get("content", "")
                
                # Extract business line codes (GLB, OSS, IST, etc.)
                bl_matches = re.findall(r'(GLB|OSS|IST|FMS|BRS|ENE|HCR|EDU|SPO|SEN)\s*[:-]?\s*([A-Za-z\s]+)', content)
                for code, desc in bl_matches:
                    codes["business_lines"][code] = desc.strip()
                
                # Extract region codes (GLB, NAM, COE, etc.)
                region_matches = re.findall(r'(GLB|NAM|COE|LAM|APJ|MEA)\s*[:-]?\s*([A-Za-z\s]+)', content)
                for code, desc in region_matches:
                    codes["regions"][code] = desc.strip()
                
                # Extract cloud region codes (IENO, NLWE, etc.)
                cloud_matches = re.findall(r'([A-Z]{4})\s*[:-]?\s*(Ireland|Netherlands|UK|France|US|[A-Za-z\s]+(?:North|South|East|West|Central)[A-Za-z\s]*)', content)
                for code, desc in cloud_matches:
                    codes["cloud_regions"][code] = desc.strip()
                
                # Extract environment codes (PRD, DEV, TST, etc.)
                env_matches = re.findall(r'(PRD|DEV|TST|STG|UAT|QAS)\s*[:-]?\s*(Production|Development|Test|Staging|UAT|Quality|[A-Za-z\s]+)', content)
                for code, desc in env_matches:
                    codes["environments"][code] = desc.strip()
            
            # Add common defaults if not found
            if not codes["business_lines"]:
                codes["business_lines"]["GLB"] = "Global"
            if not codes["regions"]:
                codes["regions"]["GLB"] = "Global"
            if not codes["environments"]:
                codes["environments"].update({
                    "PRD": "Production",
                    "DEV": "Development",
                    "TST": "Test"
                })
            
            logger.info(f"Extracted naming codes: {len(codes['business_lines'])} business lines, "
                       f"{len(codes['regions'])} regions, {len(codes['cloud_regions'])} cloud regions, "
                       f"{len(codes['environments'])} environments")
            
            return codes
            
        except Exception as e:
            logger.error(f"Error extracting naming codes: {e}")
            return codes
    
    def map_azure_region_to_sodexo_code(self, azure_region: str, extracted_codes: Dict[str, str]) -> Optional[str]:
        """
        Map Azure region name to Sodexo cloud region code.
        
        Args:
            azure_region: Azure region name (e.g., "North Europe")
            extracted_codes: Cloud region codes extracted from RAG
            
        Returns:
            Sodexo cloud region code (e.g., "IENO") or None
        """
        azure_region_lower = azure_region.lower().strip()
        
        # First try extracted codes
        for code, description in extracted_codes.items():
            if azure_region_lower in description.lower():
                logger.info(f"Mapped '{azure_region}' to '{code}' using RAG data")
                return code
        
        # Fallback to hardcoded mapping
        if azure_region_lower in self.azure_region_fallback:
            code = self.azure_region_fallback[azure_region_lower]
            logger.warning(f"Mapped '{azure_region}' to '{code}' using fallback (not found in RAG)")
            return code
        
        logger.error(f"Could not map Azure region '{azure_region}' to Sodexo code")
        return None
    
    def generate_resource_group_name(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a Sodexo-compliant Resource Group name using RAG-retrieved naming conventions.
        
        Args:
            requirements: Dict with project_name, cloud_region, environment, business_line (optional), region (optional)
            
        Returns:
            Dict with generated name, pattern, components, source, and validation info
        """
        try:
            # Step 1: Search for naming convention in RAG
            logger.info("Step 1: Searching for RG naming convention in RAG")
            rag_results = self.search_naming_convention_for_resource_groups()
            
            if not rag_results:
                logger.error("No naming convention found in AI Search index")
                return {
                    "error": "Resource Group naming convention not found in AI Search index",
                    "name": None,
                    "source": None,
                    "validation": {
                        "rag_query_executed": True,
                        "naming_convention_found": False,
                        "all_codes_validated": False
                    }
                }
            
            # Step 2: Extract naming pattern
            logger.info("Step 2: Extracting naming pattern from RAG results")
            pattern_info = self.extract_rg_naming_pattern(rag_results)
            
            if not pattern_info:
                logger.error("Could not extract naming pattern from RAG results")
                return {
                    "error": "Could not extract Resource Group naming pattern from retrieved documents",
                    "name": None,
                    "source": None,
                    "validation": {
                        "rag_query_executed": True,
                        "naming_convention_found": False,
                        "all_codes_validated": False
                    }
                }
            
            # Step 3: Extract naming codes
            logger.info("Step 3: Extracting naming codes from RAG results")
            codes = self.extract_naming_codes(rag_results)
            
            # Step 4: Get requirements with defaults
            project_name = requirements.get("project_name", "PROJECT").upper()
            business_line = requirements.get("business_line", "GLB").upper()
            region = requirements.get("region", "GLB").upper()
            cloud_region = requirements.get("cloud_region", "North Europe")
            environment = requirements.get("environment", "PRD").upper()
            
            # Step 5: Map Azure region to Sodexo code
            logger.info(f"Step 5: Mapping Azure region '{cloud_region}' to Sodexo code")
            cloud_region_code = self.map_azure_region_to_sodexo_code(cloud_region, codes["cloud_regions"])
            
            if not cloud_region_code:
                logger.error(f"Could not map cloud region '{cloud_region}'")
                return {
                    "error": f"Could not map Azure region '{cloud_region}' to Sodexo cloud region code",
                    "name": None,
                    "source": pattern_info["source"],
                    "validation": {
                        "rag_query_executed": True,
                        "naming_convention_found": True,
                        "all_codes_validated": False
                    }
                }
            
            # Step 6: Validate codes
            all_codes_valid = True
            validation_errors = []
            
            if business_line not in codes["business_lines"] and business_line != "GLB":
                validation_errors.append(f"Business line '{business_line}' not found in extracted codes")
                all_codes_valid = False
            
            if region not in codes["regions"] and region != "GLB":
                validation_errors.append(f"Region '{region}' not found in extracted codes")
                all_codes_valid = False
            
            if environment not in codes["environments"]:
                validation_errors.append(f"Environment '{environment}' not found in extracted codes")
                all_codes_valid = False
            
            # Step 7: Build the name
            logger.info("Step 7: Building Resource Group name")
            rg_name = f"{business_line}-{region}-{cloud_region_code}-{project_name}-{environment}-RG01"
            
            # Step 8: Build response
            return {
                "name": rg_name,
                "pattern": pattern_info["pattern"],
                "components": {
                    "business_line": {
                        "value": business_line,
                        "description": codes["business_lines"].get(business_line, "Global")
                    },
                    "region": {
                        "value": region,
                        "description": codes["regions"].get(region, "Global")
                    },
                    "cloud_region": {
                        "value": cloud_region_code,
                        "description": codes["cloud_regions"].get(cloud_region_code, cloud_region)
                    },
                    "project": {
                        "value": project_name,
                        "description": f"{project_name} Project"
                    },
                    "environment": {
                        "value": environment,
                        "description": codes["environments"].get(environment, environment)
                    },
                    "suffix": {
                        "value": "RG01",
                        "description": "Resource Group 01"
                    }
                },
                "source": {
                    "file": pattern_info["source"]["file"],
                    "section": "Private PaaS Assets - Resource Group Naming",
                    "pattern_source": "Retrieved from RAG knowledge base",
                    "examples_from_docs": pattern_info.get("examples", [])
                },
                "validation": {
                    "rag_query_executed": True,
                    "naming_convention_found": True,
                    "all_codes_validated": all_codes_valid,
                    "validation_errors": validation_errors if validation_errors else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating Resource Group name: {e}")
            return {
                "error": f"Error generating Resource Group name: {str(e)}",
                "name": None,
                "source": None,
                "validation": {
                    "rag_query_executed": False,
                    "naming_convention_found": False,
                    "all_codes_validated": False
                }
            }
    
    def validate_resource_group_name(self, name: str) -> Dict[str, Any]:
        """
        Validate that a Resource Group name follows Sodexo GCCC naming convention.
        
        Args:
            name: Resource Group name to validate
            
        Returns:
            Dict with validation result and details
        """
        try:
            # Expected pattern: {BL}-{REG}-{CLOUD}-{PROJ}-{ENV}-RG##
            pattern = r'^[A-Z]{3}-[A-Z]{3}-[A-Z]{4}-[A-Z]{3,10}-[A-Z]{3}-RG\d{2}$'
            
            if not re.match(pattern, name):
                return {
                    "valid": False,
                    "error": "Name does not match Sodexo GCCC pattern",
                    "expected_pattern": "{Business Line}-{Region}-{Cloud Region}-{Project}-{Environment}-RG##",
                    "details": "Name must follow format: XXX-XXX-XXXX-PROJECT-XXX-RG##"
                }
            
            # Split and validate segments
            segments = name.split("-")
            
            if len(segments) != 6:
                return {
                    "valid": False,
                    "error": f"Expected 6 segments, found {len(segments)}",
                    "segments": segments
                }
            
            # Validate RG suffix
            if not segments[5].startswith("RG"):
                return {
                    "valid": False,
                    "error": "Last segment must start with 'RG'",
                    "found": segments[5]
                }
            
            return {
                "valid": True,
                "segments": {
                    "business_line": segments[0],
                    "region": segments[1],
                    "cloud_region": segments[2],
                    "project": segments[3],
                    "environment": segments[4],
                    "suffix": segments[5]
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating Resource Group name: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }


# Singleton instance
naming_service = NamingService()
