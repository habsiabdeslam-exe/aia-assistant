"""
Context Normalization Service (Stage 1)

Transforms raw user requirements into structured internal schema.
Validates completeness and extracts key project attributes.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextNormalizationService:
    """
    Normalizes and validates user input requirements.
    Transforms unstructured input into structured context for downstream processing.
    """
    
    def __init__(self):
        self.required_fields = [
            "project_name",
            "description",
            "cloud_region"
        ]
        
        self.optional_fields = [
            "business_line",
            "region",
            "environments",
            "functional_requirements",
            "non_functional_requirements",
            "constraints",
            "assumptions",
            "risks",
            "stakeholders"
        ]
    
    def normalize(self, raw_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw requirements into structured context.
        
        Args:
            raw_requirements: Raw user input
            
        Returns:
            Normalized context with validation results
        """
        try:
            logger.info("Starting context normalization")
            
            # Extract and normalize project information
            project = self._normalize_project_info(raw_requirements)
            
            # Extract and normalize infrastructure settings
            infrastructure = self._normalize_infrastructure(raw_requirements)
            
            # Extract and normalize requirements
            requirements = self._normalize_requirements(raw_requirements)
            
            # Extract stakeholders
            stakeholders = self._normalize_stakeholders(raw_requirements)
            
            # Validate completeness
            completeness = self._validate_completeness(raw_requirements, project, infrastructure)
            
            normalized_context = {
                "project": project,
                "infrastructure": infrastructure,
                "requirements": requirements,
                "stakeholders": stakeholders,
                "completeness": completeness,
                "metadata": {
                    "normalized_at": datetime.utcnow().isoformat(),
                    "source": "user_input"
                }
            }
            
            logger.info(f"Context normalization completed. Completeness score: {completeness['score']:.2f}")
            
            return normalized_context
            
        except Exception as e:
            logger.error(f"Error normalizing context: {e}")
            raise
    
    def _normalize_project_info(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize project information"""
        
        project_name_raw = raw.get("project_name", "PROJECT")
        
        # Extract acronym from project name (e.g., "IoT Platform" -> "IOT")
        project_acronym = self._extract_acronym(project_name_raw)
        
        return {
            "name": project_acronym,
            "full_name": project_name_raw,
            "description": raw.get("description", ""),
            "business_line": raw.get("business_line", "GLB").upper(),
            "region": raw.get("region", "GLB").upper(),
            "owner": raw.get("owner", ""),
            "cost_center": raw.get("cost_center", "")
        }
    
    def _normalize_infrastructure(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize infrastructure settings"""
        
        # Normalize cloud region
        cloud_region = raw.get("cloud_region", "North Europe")
        
        # Determine environments
        environments = raw.get("environments", ["DEV", "PRD", "TST"])
        if isinstance(environments, str):
            environments = [e.strip().upper() for e in environments.split(",")]
        else:
            environments = [e.upper() for e in environments]
        
        return {
            "cloud_provider": "Azure",
            "primary_region": cloud_region,
            "secondary_region": raw.get("secondary_region"),
            "environments": environments,
            "high_availability": raw.get("high_availability", True),
            "disaster_recovery": raw.get("disaster_recovery", False),
            "multi_region": raw.get("multi_region", False)
        }
    
    def _normalize_requirements(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize functional and non-functional requirements"""
        
        functional = raw.get("functional_requirements", [])
        non_functional = raw.get("non_functional_requirements", [])
        constraints = raw.get("constraints", [])
        assumptions = raw.get("assumptions", [])
        risks = raw.get("risks", [])
        
        # Convert strings to lists if needed
        if isinstance(functional, str):
            functional = [r.strip() for r in functional.split("\n") if r.strip()]
        if isinstance(non_functional, str):
            non_functional = [r.strip() for r in non_functional.split("\n") if r.strip()]
        if isinstance(constraints, str):
            constraints = [c.strip() for c in constraints.split("\n") if c.strip()]
        if isinstance(assumptions, str):
            assumptions = [a.strip() for a in assumptions.split("\n") if a.strip()]
        if isinstance(risks, str):
            risks = [r.strip() for r in risks.split("\n") if r.strip()]
        
        return {
            "functional": functional,
            "non_functional": non_functional,
            "constraints": constraints,
            "assumptions": assumptions,
            "risks": risks
        }
    
    def _normalize_stakeholders(self, raw: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract and normalize stakeholder information"""
        
        stakeholders = raw.get("stakeholders", [])
        
        if isinstance(stakeholders, str):
            # Parse string format: "Name (Role), Name (Role)"
            stakeholder_list = []
            for s in stakeholders.split(","):
                s = s.strip()
                match = re.match(r"(.+?)\s*\((.+?)\)", s)
                if match:
                    stakeholder_list.append({
                        "name": match.group(1).strip(),
                        "role": match.group(2).strip()
                    })
                else:
                    stakeholder_list.append({
                        "name": s,
                        "role": "Stakeholder"
                    })
            return stakeholder_list
        
        return stakeholders
    
    def _validate_completeness(
        self, 
        raw: Dict[str, Any], 
        project: Dict[str, Any], 
        infrastructure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate completeness of normalized context.
        
        Returns:
            Completeness assessment with score and missing fields
        """
        
        missing_fields = []
        
        # Check required fields
        for field in self.required_fields:
            if not raw.get(field):
                missing_fields.append(field)
        
        # Check project info completeness
        if not project.get("full_name"):
            missing_fields.append("project.full_name")
        if not project.get("description"):
            missing_fields.append("project.description")
        
        # Check infrastructure completeness
        if not infrastructure.get("primary_region"):
            missing_fields.append("infrastructure.primary_region")
        
        # Calculate completeness score
        total_fields = len(self.required_fields) + len(self.optional_fields)
        provided_fields = sum(1 for f in self.required_fields + self.optional_fields if raw.get(f))
        score = provided_fields / total_fields
        
        is_complete = len(missing_fields) == 0 and score >= 0.6
        
        return {
            "is_complete": is_complete,
            "score": score,
            "missing_fields": missing_fields,
            "provided_fields": provided_fields,
            "total_fields": total_fields,
            "status": "READY" if is_complete else "INCOMPLETE"
        }
    
    def _extract_acronym(self, project_name: str) -> str:
        """
        Extract acronym from project name.
        
        Examples:
            "IoT Platform" -> "IOT"
            "Data Analytics Platform" -> "DAP"
            "Customer Portal" -> "CP"
        """
        
        # Remove common words
        common_words = ["platform", "system", "service", "application", "portal"]
        words = project_name.split()
        filtered_words = [w for w in words if w.lower() not in common_words]
        
        if not filtered_words:
            filtered_words = words
        
        # If single word, take first 3-4 letters
        if len(filtered_words) == 1:
            word = filtered_words[0].upper()
            return word[:4] if len(word) > 3 else word
        
        # If multiple words, take first letter of each
        acronym = "".join([w[0].upper() for w in filtered_words])
        
        # Limit to 10 characters
        return acronym[:10]


# Singleton instance
context_normalizer = ContextNormalizationService()
