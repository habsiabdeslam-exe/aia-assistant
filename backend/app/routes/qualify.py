from fastapi import APIRouter, HTTPException
import logging
from app.models.schemas import RequirementsInput, QualificationOutput
from app.services.openai_service import get_openai_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/qualify", response_model=QualificationOutput)
async def qualify_requirements(input_data: RequirementsInput):
    """
    Qualify requirements using Azure OpenAI GPT-4.
    
    Analyzes the provided requirements and returns:
    - Detailed qualification analysis (completeness, clarity, feasibility, consistency)
    - Gap analysis score (GAB)
    """
    try:
        logger.info("Received requirements qualification request")
        
        if not input_data.requirements or not input_data.requirements.strip():
            logger.warning("Empty requirements received")
            raise HTTPException(status_code=400, detail="Requirements cannot be empty")
        
        logger.info(f"Qualifying requirements (length: {len(input_data.requirements)} chars)")
        service = get_openai_service()
        result = service.qualify_requirements(input_data.requirements)
        
        logger.info(f"Qualification completed with GAB score: {result['gap']}")
        return QualificationOutput(
            qualification=result["qualification"],
            gap=result["gap"]
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in qualify_requirements: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error qualifying requirements: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error qualifying requirements: {str(e)}")
