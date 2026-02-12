import os
import logging
from typing import List, Dict, Any
from openai import AzureOpenAI
from app.config import config

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    def __init__(self):
        """Initialize Azure OpenAI service using Config (Key Vault in production, env vars in development)."""
        try:
            self.endpoint = config.azure_openai_endpoint
            self.api_key = config.azure_openai_key
            self.api_version = "2024-02-15-preview"
            self.gpt4_deployment = config.gpt4_deployment
            self.embedding_deployment = config.embedding_deployment
            
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version
            )
            
            self.prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
            logger.info(f"AzureOpenAIService initialized successfully (GPT-4: {self.gpt4_deployment}, Embedding: {self.embedding_deployment})")
        except Exception as e:
            logger.error(f"Failed to initialize AzureOpenAIService: {e}")
            raise
    
    def _load_prompt_template(self, filename: str) -> str:
        """Load prompt template from file."""
        try:
            prompt_path = os.path.join(self.prompts_dir, filename)
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt template not found: {filename}")
            raise
        except Exception as e:
            logger.error(f"Error loading prompt template {filename}: {e}")
            raise
    
    def qualify_requirements(self, requirements: str) -> Dict[str, Any]:
        """
        Analyze and qualify requirements using GPT-4.
        Returns markdown analysis with READY/NOT READY status.
        """
        try:
            logger.info("Starting requirements qualification")
            
            system_prompt = self._load_prompt_template("requirements_analyzer.txt")
            user_prompt = f"Analyze these requirements:\n\n{requirements}"
            
            logger.debug(f"Calling GPT-4 with {len(requirements)} characters of requirements")
            
            response = self.client.chat.completions.create(
                model=self.gpt4_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse status from analysis
            status = "NOT READY"
            has_gaps = True
            if "Status: READY" in analysis_text:
                status = "READY"
                has_gaps = False
            elif "MUST-HAVE gaps: 0" in analysis_text:
                status = "READY"
                has_gaps = False
            
            logger.info(f"Requirements qualification completed. Status: {status}")
            
            return {
                "analysis": analysis_text,
                "status": status,
                "has_gaps": has_gaps
            }
            
        except Exception as e:
            logger.error(f"Error in qualify_requirements: {e}")
            raise
    
    def generate_tad(self, requirements: Dict[str, Any], rag_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate Technical Architecture Document using GPT-4 with RAG context following Sodexo template.
        """
        try:
            logger.info("Starting TAD generation with Sodexo template")
            
            # Build RAG context from chunks
            rag_context = self._build_rag_context(rag_chunks)
            
            # Load Sodexo TAD generation prompt template
            system_prompt = self._load_prompt_template("tad_generator_sodexo.txt")
            
            # Format requirements
            import json
            requirements_text = json.dumps(requirements, indent=2)
            
            user_prompt = f"""Requirements Analysis (from Analyzer):
{requirements_text}

Sodexo Knowledge Base (RAG Context):
{rag_context}

Generate a comprehensive Technical Architecture Document following the Sodexo template structure.
Use ONLY policies from the Sodexo knowledge base provided above.
Cite sources in format: [Source: Document Title, Section X, Version Y]
If a policy is not found in the knowledge base, state "Policy not found in KB" and use industry best practices."""

            logger.debug(f"Calling GPT-4 for TAD generation with {len(rag_chunks)} RAG chunks")
            
            response = self.client.chat.completions.create(
                model=self.gpt4_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=4000
            )
            
            tad_content = response.choices[0].message.content
            logger.info(f"TAD generation completed. Generated {len(tad_content)} characters")
            
            return tad_content
            
        except Exception as e:
            logger.error(f"Error in generate_tad: {e}")
            raise
    
    def _build_rag_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build formatted context from RAG chunks."""
        if not chunks:
            return "No reference materials available."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            content = chunk.get("content", "")
            score = chunk.get("score", 0)
            title = chunk.get("title", f"Reference {i}")
            
            context_parts.append(f"### Reference {i}: {title} (Relevance: {score:.2f})\n{content}")
        
        return "\n\n".join(context_parts)
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding vector for the given text using Azure OpenAI.
        """
        try:
            logger.debug(f"Creating embedding for text of length {len(text)}")
            
            response = self.client.embeddings.create(
                model=self.embedding_deployment,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Embedding created successfully. Dimension: {len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise


# Singleton instance - lazy loaded
_openai_service_instance = None

def get_openai_service() -> AzureOpenAIService:
    """Get or create the OpenAI service singleton instance."""
    global _openai_service_instance
    if _openai_service_instance is None:
        _openai_service_instance = AzureOpenAIService()
    return _openai_service_instance

# For backward compatibility
openai_service = None  # Will be initialized on first use
