"""
Writer Agent Service (Stage 3)

Generates TAD sections with structured architectural reasoning.
Uses section-specific prompts and RAG context to produce professional content.
"""

import logging
import os
from typing import Dict, Any, Optional
from openai import AzureOpenAI
from app.config import config
from app.services.section_schemas import SectionSchema, SectionName

logger = logging.getLogger(__name__)


class WriterAgentService:
    """
    Writer Agent - Generates TAD sections with professional enterprise writing.
    Each section is generated independently with structured reasoning.
    """
    
    def __init__(self):
        """Initialize Azure OpenAI client for Writer Agent"""
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
            
            self.prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts", "writer_agent")
            
            logger.info("WriterAgentService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WriterAgentService: {e}")
            raise
    
    async def generate_section(
        self,
        section_name: SectionName,
        schema: SectionSchema,
        context: Dict[str, Any],
        rag_data: Dict[str, Any],
        naming_data: Dict[str, Any],
        feedback: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a single TAD section using structured reasoning.
        
        Args:
            section_name: Section identifier
            schema: Section schema with requirements
            context: Normalized project context
            rag_data: Retrieved RAG knowledge
            naming_data: Pre-generated naming artifacts
            feedback: Feedback from previous attempt (if regenerating)
            
        Returns:
            Generated section content in Markdown
        """
        try:
            logger.info(f"Writer Agent generating section: {section_name.value}")
            
            # Build system prompt
            system_prompt = self._build_system_prompt(section_name, schema)
            
            # Build user prompt with context
            user_prompt = self._build_user_prompt(
                section_name=section_name,
                schema=schema,
                context=context,
                rag_data=rag_data,
                naming_data=naming_data,
                feedback=feedback
            )
            
            logger.debug(f"Calling GPT-4 for section: {section_name.value}")
            
            # Generate section
            response = self.client.chat.completions.create(
                model=self.gpt4_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=4000
            )
            
            section_content = response.choices[0].message.content
            
            logger.info(f"Section {section_name.value} generated successfully ({len(section_content)} characters)")
            
            return section_content
            
        except Exception as e:
            logger.error(f"Error generating section {section_name.value}: {e}")
            raise
    
    def _build_system_prompt(self, section_name: SectionName, schema: SectionSchema) -> str:
        """Build system prompt for Writer Agent"""
        
        # Try to load section-specific prompt
        prompt_file = f"{section_name.value}.txt"
        prompt_path = os.path.join(self.prompts_dir, prompt_file)
        
        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not load prompt file {prompt_file}: {e}")
        
        # Fallback to generic writer prompt
        return self._build_generic_writer_prompt(section_name, schema)
    
    def _build_generic_writer_prompt(self, section_name: SectionName, schema: SectionSchema) -> str:
        """Build generic writer prompt when section-specific prompt not available"""
        
        return f"""You are a Senior Cloud Architect writing the "{schema.title}" section of a Technical Architecture Document.

ROLE: Senior Cloud Architect with 15+ years of experience in enterprise architecture design.

TASK: Generate the {schema.title} section with professional enterprise writing quality.

SECTION DESCRIPTION:
{schema.description}

REQUIRED ARTIFACTS:
{self._format_required_artifacts(schema)}

REQUIRED TABLES:
{self._format_required_tables(schema)}

REQUIRED RAG DOMAINS:
{self._format_required_rag_domains(schema)}

STRUCTURAL REQUIREMENTS:
- Minimum paragraphs: {schema.min_paragraphs}
- Maximum length: {schema.max_length} characters
- Requires Mermaid diagram: {schema.requires_mermaid}
- Subsections: {', '.join(schema.subsections) if schema.subsections else 'None'}

WRITING STYLE:
- Professional enterprise documentation style
- Clear, structured paragraphs (2-4 sentences each)
- Supporting bullet points for details
- Tables for structured data
- Concrete values and names (no placeholders)
- Source citations for all governance elements

CRITICAL CONSTRAINTS:
1. Use ONLY standards retrieved from RAG context
2. If standard not found in RAG, state: "[Standard Name] not found in AI Search index"
3. Generate ALL required artifacts (names, tables, diagrams)
4. No generic statements without concrete values
5. No invented naming conventions or patterns
6. No hallucinated standards or policies

OUTPUT FORMAT:
- Markdown with proper heading hierarchy
- Tables in GitHub Flavored Markdown format
- Mermaid diagrams where required
- Source citations: [Source: Document Name, Section]

QUALITY EXPECTATIONS:
This section must read as if written by a senior architect and reviewed by a governance team.
It must be complete, professional, and immediately usable in production."""
    
    def _build_user_prompt(
        self,
        section_name: SectionName,
        schema: SectionSchema,
        context: Dict[str, Any],
        rag_data: Dict[str, Any],
        naming_data: Dict[str, Any],
        feedback: Optional[Dict[str, Any]]
    ) -> str:
        """Build user prompt with project context and RAG data"""
        
        # Format project context
        project_context = self._format_project_context(context)
        
        # Format RAG context for this section
        rag_context = self._format_rag_context_for_section(section_name, schema, rag_data)
        
        # Format naming data
        naming_context = self._format_naming_context(naming_data)
        
        # Format feedback if regenerating
        feedback_context = ""
        if feedback:
            feedback_context = f"""
FEEDBACK FROM PREVIOUS ATTEMPT:
The previous version of this section had the following issues that MUST be corrected:

{self._format_feedback(feedback)}

Please regenerate the section addressing all feedback points.
"""
        
        return f"""PROJECT CONTEXT:
{project_context}

RAG RETRIEVED STANDARDS:
{rag_context}

PRE-GENERATED NAMING ARTIFACTS:
{naming_context}
{feedback_context}

Generate the {schema.title} section following all requirements and constraints.
Ensure all required artifacts, tables, and subsections are present.
Use concrete values from the context and RAG data provided above."""
    
    def _format_project_context(self, context: Dict[str, Any]) -> str:
        """Format project context for prompt"""
        
        project = context.get("project", {})
        infrastructure = context.get("infrastructure", {})
        
        return f"""
Project Name: {project.get('full_name', 'N/A')}
Project Acronym: {project.get('name', 'N/A')}
Description: {project.get('description', 'N/A')}
Business Line: {project.get('business_line', 'GLB')}
Region: {project.get('region', 'GLB')}

Infrastructure:
- Cloud Provider: {infrastructure.get('cloud_provider', 'Azure')}
- Primary Region: {infrastructure.get('primary_region', 'N/A')}
- Environments: {', '.join(infrastructure.get('environments', []))}
- High Availability: {infrastructure.get('high_availability', False)}
- Disaster Recovery: {infrastructure.get('disaster_recovery', False)}
"""
    
    def _format_rag_context_for_section(
        self,
        section_name: SectionName,
        schema: SectionSchema,
        rag_data: Dict[str, Any]
    ) -> str:
        """Format RAG context relevant to this section"""
        
        if not schema.required_rag_domains:
            return "No specific RAG standards required for this section."
        
        rag_context_parts = []
        
        for rag_domain in schema.required_rag_domains:
            domain_path = rag_domain.value.split(".")
            
            if len(domain_path) == 2:
                domain, subdomain = domain_path
                domain_data = rag_data.get(domain, {}).get(subdomain, {})
                
                if domain_data.get("found"):
                    chunks = domain_data.get("chunks", [])
                    source_files = domain_data.get("source_files", [])
                    
                    rag_context_parts.append(f"\n### {domain}.{subdomain}")
                    rag_context_parts.append(f"Status: ✅ FOUND")
                    rag_context_parts.append(f"Source Files: {', '.join(source_files)}")
                    rag_context_parts.append(f"\nRetrieved Content:")
                    
                    for i, chunk in enumerate(chunks[:3], 1):  # Top 3 chunks
                        content = chunk.get("content", "")
                        rag_context_parts.append(f"\nChunk {i}:\n{content[:500]}...")
                else:
                    error = domain_data.get("error", "Not found")
                    rag_context_parts.append(f"\n### {domain}.{subdomain}")
                    rag_context_parts.append(f"Status: ❌ NOT FOUND")
                    rag_context_parts.append(f"Error: {error}")
        
        return "\n".join(rag_context_parts) if rag_context_parts else "No RAG data retrieved."
    
    def _format_naming_context(self, naming_data: Dict[str, Any]) -> str:
        """Format pre-generated naming artifacts"""
        
        if not naming_data:
            return "No pre-generated naming artifacts available."
        
        naming_parts = []
        
        for key, data in naming_data.items():
            if "error" in data:
                naming_parts.append(f"\n{key.upper()}: ❌ {data['error']}")
            else:
                naming_parts.append(f"\n{key.upper()}:")
                naming_parts.append(f"  Name: {data.get('name', 'N/A')}")
                naming_parts.append(f"  Pattern: {data.get('pattern', 'N/A')}")
                if data.get('source'):
                    naming_parts.append(f"  Source: {data['source'].get('file', 'N/A')}")
        
        return "\n".join(naming_parts) if naming_parts else "No naming data available."
    
    def _format_feedback(self, feedback: Dict[str, Any]) -> str:
        """Format feedback from reviewer"""
        
        issues = feedback.get("issues", [])
        recommendations = feedback.get("recommendations", [])
        
        feedback_parts = []
        
        if issues:
            feedback_parts.append("Issues to fix:")
            for issue in issues:
                severity = issue.get("severity", "unknown")
                description = issue.get("description", "")
                feedback_parts.append(f"  - [{severity.upper()}] {description}")
        
        if recommendations:
            feedback_parts.append("\nRecommendations:")
            for rec in recommendations:
                feedback_parts.append(f"  - {rec}")
        
        return "\n".join(feedback_parts)
    
    def _format_required_artifacts(self, schema: SectionSchema) -> str:
        """Format required artifacts list"""
        if not schema.required_artifacts:
            return "None"
        return "\n".join([f"  - {artifact.value}" for artifact in schema.required_artifacts])
    
    def _format_required_tables(self, schema: SectionSchema) -> str:
        """Format required tables list"""
        if not schema.required_tables:
            return "None"
        return "\n".join([f"  - {table}" for table in schema.required_tables])
    
    def _format_required_rag_domains(self, schema: SectionSchema) -> str:
        """Format required RAG domains list"""
        if not schema.required_rag_domains:
            return "None"
        return "\n".join([f"  - {domain.value}" for domain in schema.required_rag_domains])


# Singleton instance
writer_agent = WriterAgentService()
