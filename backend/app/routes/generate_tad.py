from fastapi import APIRouter, HTTPException
import logging
from app.models.schemas import GenerateTADInput, GenerateTADOutput
from app.services.openai_service import get_openai_service
from app.services.search_service import search_service
from app.services.naming_service import naming_service
import json

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate-tad", response_model=GenerateTADOutput)
async def generate_tad(input_data: GenerateTADInput):
    """
    Generate Technical Architecture Document using Azure OpenAI GPT-4 with RAG.
    
    Process:
    1. Create embedding of requirements
    2. Search Azure AI Search for relevant knowledge base chunks using hybrid search
    3. Build prompt with requirements + RAG chunks + TAD template
    4. Call GPT-4 to generate TAD in markdown
    5. Return the generated TAD
    """
    try:
        logger.info("Received TAD generation request")
        requirements = input_data.requirements
        
        # Convert requirements to string for embedding and search
        requirements_text = json.dumps(requirements, indent=2)
        
        # Step 1: Create embedding of requirements
        logger.info("Creating embedding for requirements")
        service = get_openai_service()
        query_vector = service.create_embedding(requirements_text)
        
        # Step 2: Search Azure AI Search for relevant chunks using hybrid search (text + vector)
        # Using top_k=10 to get comprehensive context from knowledge base
        logger.info("Performing hybrid search in Azure AI Search")
        rag_results = search_service.hybrid_search(
            query_text=requirements_text,
            query_vector=query_vector,
            top_k=10
        )
        
        if not rag_results:
            logger.warning("No RAG results found, proceeding with empty context")
        
        # Step 2.5: Generate Sodexo-compliant Resource Group names using naming service
        logger.info("Generating Resource Group names using naming service")
        naming_data = {}
        
        # Extract project info from requirements
        project_name = requirements.get("project_name", "PROJECT")
        cloud_region = requirements.get("cloud_region", "North Europe")
        
        # Generate RG names for each environment
        for env in ["DEV", "PRD", "TST"]:
            rg_result = naming_service.generate_resource_group_name({
                "project_name": project_name,
                "cloud_region": cloud_region,
                "environment": env,
                "business_line": requirements.get("business_line", "GLB"),
                "region": requirements.get("region", "GLB")
            })
            naming_data[f"rg_{env.lower()}"] = rg_result
        
        # Add naming data to requirements for TAD generation
        requirements["_naming_data"] = naming_data
        
        # Step 3 & 4: Build prompt and generate TAD using GPT-4
        logger.info(f"Generating TAD with {len(rag_results)} RAG chunks and naming data")
        tad_markdown = service.generate_tad(requirements, rag_results)
        
        # Step 5: Return the generated TAD
        logger.info("TAD generation completed successfully")
        return GenerateTADOutput(tad_markdown=tad_markdown)
        
    except ValueError as e:
        logger.error(f"Validation error in generate_tad: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating TAD: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating TAD: {str(e)}")
