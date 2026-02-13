"""
TAD Orchestrator (Main Pipeline Coordinator)

Orchestrates the complete multi-stage TAD generation pipeline:
Stage 1: Context Normalization
Stage 2: Structured RAG Retrieval
Stage 3: Writer Agent (section generation)
Stage 4: Reviewer Agent (validation)

Implements correction loops: Writer → Reviewer → Regenerate if needed
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from app.services.context_normalizer import context_normalizer
from app.services.structured_rag_retriever import structured_rag_retriever
from app.services.naming_service import naming_service
from app.services.writer_agent import writer_agent
from app.services.reviewer_agent import reviewer_agent
from app.services.section_schemas import (
    SectionName,
    SectionSchema,
    get_section_schema,
    get_section_order,
    TAD_SECTION_SCHEMAS
)

logger = logging.getLogger(__name__)


class TADOrchestrator:
    """
    Orchestrates the multi-stage TAD generation pipeline.
    Coordinates: Context Normalization → RAG Retrieval → Writer Agent → Reviewer Agent
    """
    
    def __init__(self):
        self.context_normalizer = context_normalizer
        self.rag_retriever = structured_rag_retriever
        self.naming_service = naming_service
        self.writer_agent = writer_agent
        self.reviewer_agent = reviewer_agent
        
        self.max_retries = 2  # Maximum regeneration attempts per section
    
    async def generate_tad(self, raw_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration method - generates complete TAD through multi-stage pipeline.
        
        Args:
            raw_requirements: Raw user input requirements
            
        Returns:
            Complete TAD with validation report and metadata
        """
        try:
            logger.info("=" * 80)
            logger.info("TAD ORCHESTRATOR - Starting multi-stage pipeline")
            logger.info("=" * 80)
            
            start_time = datetime.utcnow()
            
            # STAGE 1: Context Normalization
            logger.info("\n[STAGE 1] Context Normalization")
            normalized_context = self.context_normalizer.normalize(raw_requirements)
            
            if not normalized_context["completeness"]["is_complete"]:
                logger.warning("Requirements incomplete - returning early")
                return self._handle_incomplete_requirements(normalized_context)
            
            logger.info(f"✅ Context normalized. Completeness score: {normalized_context['completeness']['score']:.2f}")
            
            # STAGE 2: Structured RAG Retrieval
            logger.info("\n[STAGE 2] Structured RAG Retrieval")
            rag_data = await self.rag_retriever.retrieve_all(normalized_context)
            
            rag_summary = self.rag_retriever.get_rag_summary(rag_data)
            logger.info(f"✅ RAG retrieval completed. Coverage: {rag_summary['coverage_score']:.2%}")
            logger.info(f"   Found: {len(rag_summary['found'])} domains")
            logger.info(f"   Missing: {len(rag_summary['missing'])} domains")
            
            # Generate naming artifacts
            logger.info("\n[STAGE 2.5] Generating naming artifacts")
            naming_data = self._generate_naming_artifacts(normalized_context)
            logger.info(f"✅ Naming artifacts generated for {len(naming_data)} environments")
            
            # STAGE 3 & 4: Generate sections with validation
            logger.info("\n[STAGE 3 & 4] Section Generation with Validation")
            sections = {}
            validation_report = {}
            
            # Generate priority sections first (hosting, IAM, network)
            priority_sections = [
                SectionName.HOSTING,
                SectionName.IDENTITY_ACCESS_MANAGEMENT,
                SectionName.NETWORK_CONFIGURATION
            ]
            
            for section_name in priority_sections:
                if section_name in TAD_SECTION_SCHEMAS:
                    logger.info(f"\n--- Generating: {section_name.value} ---")
                    section_result = await self._generate_section_with_validation(
                        section_name=section_name,
                        context=normalized_context,
                        rag_data=rag_data,
                        naming_data=naming_data
                    )
                    
                    sections[section_name.value] = section_result["content"]
                    validation_report[section_name.value] = section_result["validation"]
                    
                    logger.info(f"✅ {section_name.value} completed. Valid: {section_result['validation']['valid']}, "
                               f"Score: {section_result['validation']['score']:.2f}, "
                               f"Attempts: {section_result['attempts']}")
            
            # Generate remaining sections
            remaining_sections = [s for s in get_section_order() if s not in priority_sections]
            
            for section_name in remaining_sections:
                if section_name in TAD_SECTION_SCHEMAS:
                    logger.info(f"\n--- Generating: {section_name.value} ---")
                    section_result = await self._generate_section_with_validation(
                        section_name=section_name,
                        context=normalized_context,
                        rag_data=rag_data,
                        naming_data=naming_data
                    )
                    
                    sections[section_name.value] = section_result["content"]
                    validation_report[section_name.value] = section_result["validation"]
                    
                    logger.info(f"✅ {section_name.value} completed. Valid: {section_result['validation']['valid']}, "
                               f"Score: {section_result['validation']['score']:.2f}")
            
            # Assemble final TAD
            logger.info("\n[FINAL] Assembling TAD document")
            tad_markdown = self._assemble_tad(
                sections=sections,
                validation_report=validation_report,
                normalized_context=normalized_context,
                rag_summary=rag_summary
            )
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"\n✅ TAD generation completed in {duration:.1f} seconds")
            logger.info(f"   Total sections: {len(sections)}")
            logger.info(f"   Valid sections: {sum(1 for v in validation_report.values() if v['valid'])}")
            logger.info(f"   Average score: {sum(v['score'] for v in validation_report.values()) / len(validation_report):.2f}")
            
            return {
                "tad_markdown": tad_markdown,
                "validation_report": validation_report,
                "rag_coverage": rag_summary,
                "metadata": {
                    "generation_time": duration,
                    "total_sections": len(sections),
                    "valid_sections": sum(1 for v in validation_report.values() if v["valid"]),
                    "average_score": sum(v["score"] for v in validation_report.values()) / len(validation_report),
                    "generated_at": end_time.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in TAD orchestration: {e}", exc_info=True)
            raise
    
    async def _generate_section_with_validation(
        self,
        section_name: SectionName,
        context: Dict[str, Any],
        rag_data: Dict[str, Any],
        naming_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a single section with Writer → Reviewer → Correction loop.
        
        Args:
            section_name: Section to generate
            context: Normalized project context
            rag_data: Retrieved RAG knowledge
            naming_data: Pre-generated naming artifacts
            
        Returns:
            Section content with validation results
        """
        
        schema = get_section_schema(section_name)
        feedback = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"  Attempt {attempt + 1}/{self.max_retries + 1}")
                
                # Writer Agent: Generate section
                logger.debug(f"  → Writer Agent generating...")
                section_content = await self.writer_agent.generate_section(
                    section_name=section_name,
                    schema=schema,
                    context=context,
                    rag_data=rag_data,
                    naming_data=naming_data,
                    feedback=feedback
                )
                
                logger.debug(f"  → Section generated ({len(section_content)} chars)")
                
                # Reviewer Agent: Validate section
                logger.debug(f"  → Reviewer Agent validating...")
                validation_result = await self.reviewer_agent.validate_section(
                    section_name=section_name,
                    content=section_content,
                    schema=schema,
                    rag_data=rag_data
                )
                
                logger.debug(f"  → Validation: Valid={validation_result['valid']}, Score={validation_result['score']:.2f}")
                
                # Check if valid
                if validation_result["valid"]:
                    logger.info(f"  ✅ Section validated successfully on attempt {attempt + 1}")
                    return {
                        "content": section_content,
                        "validation": validation_result,
                        "attempts": attempt + 1
                    }
                
                # Check for critical issues
                critical_issues = [
                    i for i in validation_result["issues"]
                    if i["severity"] == "critical"
                ]
                
                # If no critical issues and we've tried at least once, accept it
                if not critical_issues and attempt > 0:
                    logger.info(f"  ⚠️  Section accepted with minor issues on attempt {attempt + 1}")
                    return {
                        "content": section_content,
                        "validation": validation_result,
                        "attempts": attempt + 1
                    }
                
                # Prepare feedback for next attempt
                logger.warning(f"  ❌ Section validation failed. Critical issues: {len(critical_issues)}")
                for issue in critical_issues[:3]:  # Log first 3 critical issues
                    logger.warning(f"     - [{issue['severity'].upper()}] {issue['description']}")
                
                feedback = {
                    "issues": critical_issues,
                    "recommendations": validation_result["recommendations"]
                }
                
            except Exception as e:
                logger.error(f"  Error in attempt {attempt + 1}: {e}")
                if attempt == self.max_retries:
                    raise
        
        # Failed after max retries
        logger.error(f"  ❌ Section generation failed after {self.max_retries + 1} attempts")
        return {
            "content": self._generate_error_section(section_name, validation_result),
            "validation": validation_result,
            "attempts": self.max_retries + 1
        }
    
    def _generate_naming_artifacts(self, normalized_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate naming artifacts for all environments"""
        
        naming_data = {}
        
        project_name = normalized_context.get("project", {}).get("name", "PROJECT")
        cloud_region = normalized_context.get("infrastructure", {}).get("primary_region", "North Europe")
        business_line = normalized_context.get("project", {}).get("business_line", "GLB")
        region = normalized_context.get("project", {}).get("region", "GLB")
        
        environments = normalized_context.get("infrastructure", {}).get("environments", ["DEV", "PRD", "TST"])
        
        for env in environments:
            rg_result = self.naming_service.generate_resource_group_name({
                "project_name": project_name,
                "cloud_region": cloud_region,
                "environment": env,
                "business_line": business_line,
                "region": region
            })
            naming_data[f"rg_{env.lower()}"] = rg_result
        
        return naming_data
    
    def _assemble_tad(
        self,
        sections: Dict[str, str],
        validation_report: Dict[str, Any],
        normalized_context: Dict[str, Any],
        rag_summary: Dict[str, Any]
    ) -> str:
        """Assemble final TAD document from generated sections"""
        
        project_name = normalized_context.get("project", {}).get("full_name", "Project")
        
        tad_parts = []
        
        # Document header
        tad_parts.append(f"# Technical Architecture Document")
        tad_parts.append(f"## {project_name}")
        tad_parts.append(f"\n**Document Version:** 1.0")
        tad_parts.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        tad_parts.append(f"**Status:** Draft for Review")
        tad_parts.append("\n---\n")
        
        # Add sections in order
        for section_name in get_section_order():
            section_key = section_name.value
            if section_key in sections:
                tad_parts.append(sections[section_key])
                tad_parts.append("\n---\n")
        
        # Add validation report
        tad_parts.append(self._generate_validation_report_section(validation_report, rag_summary))
        
        return "\n".join(tad_parts)
    
    def _generate_validation_report_section(
        self,
        validation_report: Dict[str, Any],
        rag_summary: Dict[str, Any]
    ) -> str:
        """Generate validation report section"""
        
        report_parts = []
        
        report_parts.append("## Document Validation Report")
        report_parts.append("\nThis section provides transparency on the TAD generation process and validation results.\n")
        
        # RAG Coverage
        report_parts.append("### RAG Knowledge Base Coverage")
        report_parts.append(f"\n**Coverage Score:** {rag_summary['coverage_score']:.1%}\n")
        
        if rag_summary['found']:
            report_parts.append("**Standards Retrieved from Knowledge Base:**")
            for domain in rag_summary['found']:
                report_parts.append(f"- ✅ {domain}")
        
        if rag_summary['missing']:
            report_parts.append("\n**Standards Not Found in Knowledge Base:**")
            for domain in rag_summary['missing']:
                report_parts.append(f"- ❌ {domain}")
            report_parts.append("\n**Action Required:** Upload missing standard documents to Azure Blob Storage (knowledge-base container) and re-run indexer.")
        
        # Section Quality
        report_parts.append("\n### Section Quality Scores")
        report_parts.append("\n| Section | Valid | Score | Issues |")
        report_parts.append("|---------|-------|-------|--------|")
        
        for section_name, validation in validation_report.items():
            valid_icon = "✅" if validation["valid"] else "❌"
            score = validation["score"]
            issue_count = len(validation.get("issues", []))
            
            report_parts.append(f"| {section_name.replace('_', ' ').title()} | {valid_icon} | {score:.2f} | {issue_count} |")
        
        # Critical Issues Summary
        all_critical_issues = []
        for section_name, validation in validation_report.items():
            critical = [i for i in validation.get("issues", []) if i["severity"] == "critical"]
            for issue in critical:
                all_critical_issues.append(f"{section_name}: {issue['description']}")
        
        if all_critical_issues:
            report_parts.append("\n### Critical Issues Detected")
            for issue in all_critical_issues:
                report_parts.append(f"- ⚠️ {issue}")
        
        # Recommendations
        report_parts.append("\n### Recommendations")
        report_parts.append("1. Review sections with scores below 0.8 for potential improvements")
        report_parts.append("2. Upload missing standard documents to improve RAG coverage")
        report_parts.append("3. Validate all generated names against organizational standards")
        report_parts.append("4. Have architecture review board approve before implementation")
        
        return "\n".join(report_parts)
    
    def _generate_error_section(self, section_name: SectionName, validation_result: Dict[str, Any]) -> str:
        """Generate error section when generation fails"""
        
        schema = get_section_schema(section_name)
        
        error_parts = []
        error_parts.append(f"### {schema.title}")
        error_parts.append(f"\n**⚠️ Section Generation Failed**\n")
        error_parts.append(f"This section could not be generated successfully after {self.max_retries + 1} attempts.\n")
        error_parts.append("**Issues Detected:**\n")
        
        for issue in validation_result.get("issues", [])[:5]:
            error_parts.append(f"- [{issue['severity'].upper()}] {issue['description']}")
        
        error_parts.append("\n**Action Required:**")
        error_parts.append("1. Review the requirements and ensure all necessary information is provided")
        error_parts.append("2. Verify that required standards are available in the knowledge base")
        error_parts.append("3. Regenerate this section after addressing the issues")
        
        return "\n".join(error_parts)
    
    def _handle_incomplete_requirements(self, normalized_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incomplete requirements"""
        
        completeness = normalized_context["completeness"]
        
        error_message = f"""# Requirements Incomplete

The provided requirements are incomplete and cannot be used to generate a TAD.

**Completeness Score:** {completeness['score']:.1%}

**Missing Required Fields:**
{chr(10).join(['- ' + field for field in completeness['missing_fields']])}

**Action Required:**
Please provide the missing information and regenerate the TAD.
"""
        
        return {
            "tad_markdown": error_message,
            "validation_report": {},
            "rag_coverage": {},
            "metadata": {
                "status": "incomplete_requirements",
                "completeness_score": completeness["score"]
            }
        }


# Singleton instance
tad_orchestrator = TADOrchestrator()
