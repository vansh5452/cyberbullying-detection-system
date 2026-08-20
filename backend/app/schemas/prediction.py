from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictionRequest(BaseModel):
    text: str = Field(..., description="Message to analyze for cyberbullying content")

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text must not be empty")
        return v


class PredictionData(BaseModel):
    label: int
    is_cyberbullying: bool
    prediction: str
    confidence: float
    confidence_percent: float
    matched_words: List[str]
    method: str
    category: str
    severity: str
    disclaimer: str = (
        "This confidence score is a statistical estimate from a machine learning "
        "model, not a guarantee. It should support human judgment, not replace it."
    )


class PredictionRecord(BaseModel):
    id: str
    input_text: Optional[str] = None
    label: int
    is_cyberbullying: bool
    confidence: float
    method: str
    matched_words: List[str]
    category: str
    severity: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
