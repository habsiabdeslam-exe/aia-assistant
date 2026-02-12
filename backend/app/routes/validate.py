from fastapi import APIRouter, HTTPException
import logging
from app.models.schemas import ValidationInput, ValidationOutput

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/validate", response_model=ValidationOutput)
async def validate_qualification(input_data: ValidationInput):
    """
    Validate qualification data.
    
    Checks if GAB (Gap Analysis Score) = 0, meaning requirements are complete and valid.
    """
    try:
        logger.info("Received validation request")
        qualification = input_data.qualification
        
        # Extract gap score from qualification
        gap = qualification.get("overall_gap", 100)
        
        # Valid if gap is 0 (no gaps in requirements)
        valid = (gap == 0)
        
        logger.info(f"Validation result: valid={valid}, gap={gap}")
        
        return ValidationOutput(
            valid=valid,
            gap=gap
        )
    except Exception as e:
        logger.error(f"Error validating qualification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error validating qualification: {str(e)}")
