from fastapi import APIRouter, HTTPException
import logging
from app.models.schemas import GenerateTADInput, GenerateTADOutput
from app.services.tad_orchestrator import tad_orchestrator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate-tad", response_model=GenerateTADOutput)
async def generate_tad(input_data: GenerateTADInput):
    """
    Generate Technical Architecture Document using multi-stage orchestrated pipeline.
    
    Pipeline Stages:
    1. Context Normalization - Validate and structure input requirements
    2. Structured RAG Retrieval - Query knowledge base for governance standards
    3. Writer Agent - Generate each section with professional writing
    4. Reviewer Agent - Validate section quality and compliance
    5. Correction Loops - Regenerate sections if validation fails
    
    Returns:
        Complete TAD with validation report and metadata
    """
    try:
        logger.info("Received TAD generation request - using orchestrated pipeline")
        requirements = input_data.requirements
        
        # Use TAD Orchestrator for multi-stage generation
        result = await tad_orchestrator.generate_tad(requirements)
        
        logger.info("TAD generation completed successfully via orchestrator")
        logger.info(f"Metadata: {result.get('metadata', {})}")
        
        return GenerateTADOutput(tad_markdown=result["tad_markdown"])
        
    except ValueError as e:
        logger.error(f"Validation error in generate_tad: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating TAD: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating TAD: {str(e)}")
