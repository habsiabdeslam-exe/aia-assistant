from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class RequirementsInput(BaseModel):
    requirements: str = Field(..., description="String containing functional and non-functional requirements")


class QualificationOutput(BaseModel):
    analysis: str = Field(..., description="Full markdown analysis from analyzer including FR/NFR tables and gaps")
    status: str = Field(..., description="READY or NOT READY status")
    has_gaps: bool = Field(..., description="Whether MUST-HAVE gaps exist")


class ValidationInput(BaseModel):
    qualification: Dict[str, Any] = Field(..., description="Qualification data to validate")


class ValidationOutput(BaseModel):
    valid: bool = Field(..., description="Whether the qualification is valid (GAB = 0)")
    gap: float = Field(..., description="Gap analysis score")


class GenerateTADInput(BaseModel):
    requirements: Dict[str, Any] = Field(..., description="Requirements data for TAD generation")


class GenerateTADOutput(BaseModel):
    tad_markdown: str = Field(..., description="Generated Technical Architecture Document in markdown format")


class RAGChunk(BaseModel):
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
