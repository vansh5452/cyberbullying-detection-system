from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel


class ModelStatusData(BaseModel):
    model_loaded: bool
    model_type: str
    fallback_available: bool
    accuracy: Optional[float] = None


class ModelAnalyticsData(BaseModel):
    accuracy: Optional[float] = None
    confusion_matrix: Optional[List[List[int]]] = None
    classification_report: Optional[Dict] = None
    model_type: str
    trained: bool


class TopToxicWord(BaseModel):
    word: str
    weight: float


class DashboardStats(BaseModel):
    model_accuracy: Optional[float] = None
    messages_scanned: int
    safe_messages: int
    cyberbullying_detected: int


class RetrainResult(BaseModel):
    success: bool
    accuracy: Optional[float] = None
    training_rows: Optional[int] = None
    testing_rows: Optional[int] = None
    message: str
