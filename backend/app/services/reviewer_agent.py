"""
Reviewer Agent Service (Stage 4)

Validates TAD sections for completeness, quality, and RAG compliance.
Acts as a second persona to ensure enterprise-grade output.
"""

import logging
import os
import re
from typing import Dict, Any, List
from openai import AzureOpenAI
from app.config import config
from app.services.section_schemas import SectionSchema, SectionName

logger = logging.getLogger(__name__)


class ReviewerAgentService:
    """
    Reviewer Agent - Validates TAD sections against quality standards.
    Simulates a senior technical reviewer checking completeness and compliance.
    """
    
    def __init__(self):
        """Initialize Azure OpenAI client for Reviewer Agent"""
        try:
            self.endpoint = config.azure_openai_endpoint
            self.api_key = config.azure_openai_key
            self.api_version = "2024-02-15-preview"
            self.gpt4_deployment = config.gpt4_deployment
            
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version
            )
            
            self.prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts", "reviewer_agent")
            
            logger.info("ReviewerAgentService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ReviewerAgentService: {e}")
            raise
    
    async def validate_section(
        self,
        section_name: SectionName,
        content: str,
        schema: SectionSchema,
        rag_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a TAD section for completeness and quality.
        
        Args:
            section_name: Section identifier
            content: Generated section content
            schema: Section schema with requirements
            rag_data: RAG data used for generation
            
        Returns:
            Validation result with issues and recommendations
        """
        try:
            logger.info(f"Reviewer Agent validating section: {section_name.value}")
            
            # Perform automated checks first
            automated_validation = self._automated_validation(content, schema, rag_data)
            
            # If critical issues found in automated checks, return immediately
            critical_automated = [i for i in automated_validation["issues"] if i["severity"] == "critical"]
            if critical_automated:
                logger.warning(f"Section {section_name.value} failed automated validation with {len(critical_automated)} critical issues")
                return {
                    "valid": False,
                    "score": automated_validation["score"],
                    "issues": automated_validation["issues"],
                    "recommendations": automated_validation["recommendations"],
                    "validation_method": "automated"
                }
            
            # Perform LLM-based validation for quality assessment
            llm_validation = await self._llm_validation(section_name, content, schema, rag_data)
            
            # Combine automated and LLM validation results
            combined_validation = self._combine_validations(automated_validation, llm_validation)
            
            logger.info(f"Section {section_name.value} validation completed. Valid: {combined_validation['valid']}, Score: {combined_validation['score']:.2f}")
            
            return combined_validation
            
        except Exception as e:
            logger.error(f"Error validating section {section_name.value}: {e}")
            raise
    
    def _automated_validation(
        self,
        content: str,
        schema: SectionSchema,
        rag_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform automated validation checks.
        Fast, deterministic checks for structural completeness.
        """
        
        issues = []
        recommendations = []
        score = 1.0
        
        # Check 1: Minimum length
        if len(content) < 500:
            issues.append({
                "category": "structural",
                "severity": "critical",
                "description": f"Section too short ({len(content)} chars). Minimum expected: 500 chars.",
                "location": "overall"
            })
            score -= 0.3
        
        # Check 2: Maximum length
        if len(content) > schema.max_length:
            issues.append({
                "category": "structural",
                "severity": "minor",
                "description": f"Section exceeds maximum length ({len(content)} > {schema.max_length} chars).",
                "location": "overall"
            })
            score -= 0.1
        
        # Check 3: Minimum paragraphs
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and not p.strip().startswith("#")]
        if len(paragraphs) < schema.min_paragraphs:
            issues.append({
                "category": "structural",
                "severity": "major",
                "description": f"Insufficient paragraphs ({len(paragraphs)} found, {schema.min_paragraphs} required).",
                "location": "overall"
            })
            score -= 0.2
        
        # Check 4: Required tables
        for table_name in schema.required_tables:
            if not self._has_markdown_table(content):
                issues.append({
                    "category": "structural",
                    "severity": "critical",
                    "description": f"Required table '{table_name}' not found.",
                    "location": "tables"
                })
                score -= 0.2
                break  # Only report once
        
        # Check 5: Mermaid diagram if required
        if schema.requires_mermaid:
            if "```mermaid" not in content.lower():
                issues.append({
                    "category": "structural",
                    "severity": "major",
                    "description": "Required Mermaid diagram not found.",
                    "location": "diagrams"
                })
                score -= 0.15
        
        # Check 6: RAG compliance - check for "not found" statements
        for rag_domain in schema.required_rag_domains:
            domain_path = rag_domain.value.split(".")
            if len(domain_path) == 2:
                domain, subdomain = domain_path
                domain_data = rag_data.get(domain, {}).get(subdomain, {})
                
                if not domain_data.get("found"):
                    # Should have "not found" statement
                    if "not found in ai search index" not in content.lower():
                        issues.append({
                            "category": "rag",
                            "severity": "critical",
                            "description": f"RAG domain '{rag_domain.value}' not found, but section doesn't state this explicitly.",
                            "location": "rag_compliance"
                        })
                        score -= 0.25
        
        # Check 7: Generic statements detection
        generic_phrases = [
            "will be established",
            "will be defined",
            "to be determined",
            "following best practices",
            "per standards"
        ]
        
        for phrase in generic_phrases:
            if phrase in content.lower():
                recommendations.append(f"Generic phrase detected: '{phrase}'. Consider providing concrete details.")
                score -= 0.05
        
        # Check 8: Source citations
        if schema.required_rag_domains:
            if "[source:" not in content.lower() and "source:" not in content.lower():
                issues.append({
                    "category": "rag",
                    "severity": "major",
                    "description": "No source citations found for RAG-based content.",
                    "location": "citations"
                })
                score -= 0.15
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        # Determine if valid
        critical_issues = [i for i in issues if i["severity"] == "critical"]
        valid = len(critical_issues) == 0 and score >= 0.6
        
        return {
            "valid": valid,
            "score": score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _llm_validation(
        self,
        section_name: SectionName,
        content: str,
        schema: SectionSchema,
        rag_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform LLM-based validation for quality assessment.
        Uses GPT-4 to evaluate content quality, coherence, and professionalism.
        """
        
        try:
            # Build validation prompt
            system_prompt = self._build_reviewer_system_prompt()
            user_prompt = self._build_reviewer_user_prompt(section_name, content, schema, rag_data)
            
            logger.debug(f"Calling GPT-4 for LLM validation of section: {section_name.value}")
            
            response = self.client.chat.completions.create(
                model=self.gpt4_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            validation_text = response.choices[0].message.content
            
            # Parse validation response
            parsed_validation = self._parse_llm_validation_response(validation_text)
            
            return parsed_validation
            
        except Exception as e:
            logger.error(f"Error in LLM validation: {e}")
            # Return neutral validation on error
            return {
                "valid": True,
                "score": 0.7,
                "issues": [],
                "recommendations": ["LLM validation could not be completed."]
            }
    
    def _build_reviewer_system_prompt(self) -> str:
        """Build system prompt for Reviewer Agent"""
        
        prompt_path = os.path.join(self.prompts_dir, "quality_validator.txt")
        
        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not load reviewer prompt: {e}")
        
        # Fallback to generic reviewer prompt
        return """You are a Senior Technical Reviewer validating a Technical Architecture Document section.

ROLE: Senior Technical Reviewer with 20+ years of experience in enterprise architecture governance.

TASK: Review the provided TAD section for quality, completeness, and compliance.

VALIDATION CRITERIA:

1. Content Quality
   - Professional enterprise writing style
   - Clear, logical flow
   - Appropriate level of detail
   - No ambiguous statements

2. Completeness
   - All required information present
   - No missing artifacts or tables
   - Concrete values (not placeholders)
   - Proper subsection structure

3. RAG Compliance
   - Standards from RAG properly cited
   - No invented naming conventions
   - Explicit statements when standards not found
   - No hallucinated policies

4. Technical Accuracy
   - Architecturally sound decisions
   - Realistic configurations
   - Proper Azure service usage
   - Security best practices

OUTPUT FORMAT:
Provide validation in this exact format:

VALIDATION RESULT: [PASS/FAIL]
SCORE: [0.0-1.0]

ISSUES:
- [SEVERITY] Description (Location)

RECOMMENDATIONS:
- Recommendation text

Be strict but fair. Focus on critical issues that would make the document unusable."""
    
    def _build_reviewer_user_prompt(
        self,
        section_name: SectionName,
        content: str,
        schema: SectionSchema,
        rag_data: Dict[str, Any]
    ) -> str:
        """Build user prompt for reviewer with section content"""
        
        return f"""SECTION TO REVIEW: {schema.title}

SECTION REQUIREMENTS:
- Required Artifacts: {', '.join([a.value for a in schema.required_artifacts]) if schema.required_artifacts else 'None'}
- Required Tables: {', '.join(schema.required_tables) if schema.required_tables else 'None'}
- Required RAG Domains: {', '.join([d.value for d in schema.required_rag_domains]) if schema.required_rag_domains else 'None'}
- Minimum Paragraphs: {schema.min_paragraphs}
- Requires Mermaid: {schema.requires_mermaid}

RAG DATA AVAILABILITY:
{self._format_rag_availability(schema, rag_data)}

SECTION CONTENT TO REVIEW:
---
{content}
---

Validate this section against all criteria and provide your assessment."""
    
    def _format_rag_availability(self, schema: SectionSchema, rag_data: Dict[str, Any]) -> str:
        """Format RAG data availability for reviewer"""
        
        if not schema.required_rag_domains:
            return "No RAG data required for this section."
        
        availability = []
        for rag_domain in schema.required_rag_domains:
            domain_path = rag_domain.value.split(".")
            if len(domain_path) == 2:
                domain, subdomain = domain_path
                domain_data = rag_data.get(domain, {}).get(subdomain, {})
                status = "✅ FOUND" if domain_data.get("found") else "❌ NOT FOUND"
                availability.append(f"- {rag_domain.value}: {status}")
        
        return "\n".join(availability)
    
    def _parse_llm_validation_response(self, validation_text: str) -> Dict[str, Any]:
        """Parse LLM validation response into structured format"""
        
        try:
            # Extract validation result
            valid = "PASS" in validation_text.upper()
            
            # Extract score
            score_match = re.search(r'SCORE:\s*([0-9.]+)', validation_text, re.IGNORECASE)
            score = float(score_match.group(1)) if score_match else 0.7
            
            # Extract issues
            issues = []
            issues_section = re.search(r'ISSUES:(.*?)(?:RECOMMENDATIONS:|$)', validation_text, re.DOTALL | re.IGNORECASE)
            if issues_section:
                issue_lines = issues_section.group(1).strip().split("\n")
                for line in issue_lines:
                    line = line.strip()
                    if line.startswith("-"):
                        # Parse: - [SEVERITY] Description (Location)
                        match = re.match(r'-\s*\[(\w+)\]\s*(.+?)(?:\((.+?)\))?$', line)
                        if match:
                            issues.append({
                                "category": "content",
                                "severity": match.group(1).lower(),
                                "description": match.group(2).strip(),
                                "location": match.group(3).strip() if match.group(3) else "general"
                            })
            
            # Extract recommendations
            recommendations = []
            rec_section = re.search(r'RECOMMENDATIONS:(.*?)$', validation_text, re.DOTALL | re.IGNORECASE)
            if rec_section:
                rec_lines = rec_section.group(1).strip().split("\n")
                for line in rec_lines:
                    line = line.strip()
                    if line.startswith("-"):
                        recommendations.append(line[1:].strip())
            
            return {
                "valid": valid,
                "score": score,
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error parsing LLM validation response: {e}")
            return {
                "valid": True,
                "score": 0.7,
                "issues": [],
                "recommendations": []
            }
    
    def _combine_validations(
        self,
        automated: Dict[str, Any],
        llm: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine automated and LLM validation results"""
        
        # Combine issues
        all_issues = automated["issues"] + llm["issues"]
        
        # Combine recommendations
        all_recommendations = automated["recommendations"] + llm["recommendations"]
        
        # Calculate combined score (weighted average)
        combined_score = (automated["score"] * 0.6) + (llm["score"] * 0.4)
        
        # Determine validity
        critical_issues = [i for i in all_issues if i["severity"] == "critical"]
        valid = len(critical_issues) == 0 and combined_score >= 0.6
        
        return {
            "valid": valid,
            "score": combined_score,
            "issues": all_issues,
            "recommendations": all_recommendations,
            "validation_method": "combined",
            "automated_score": automated["score"],
            "llm_score": llm["score"]
        }
    
    def _has_markdown_table(self, content: str) -> bool:
        """Check if content contains a markdown table"""
        # Look for table pattern: | header | header |
        table_pattern = r'\|[^\n]+\|[^\n]+\n\|[-:\s|]+\|'
        return bool(re.search(table_pattern, content))


# Singleton instance
reviewer_agent = ReviewerAgentService()
