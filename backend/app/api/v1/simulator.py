from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user_optional
from app.db.database import get_db
from app.db.models import ChatMessage, User
from app.services import safety_service
from app.services.prediction_service import predict_text
from app.utils.helpers import api_error

router = APIRouter(prefix="/simulator", tags=["Simulator"])


class SimulatorMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)


@router.post("/message", summary="Send a chat message through the moderation pipeline")
def simulate_message(
    payload: SimulatorMessageRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_optional),
):
    if not payload.message.strip():
        raise api_error(422, "INVALID_INPUT", "Message must not be empty.")

    result = predict_text(payload.message)
    is_bullying = result['label'] == 1

    record = ChatMessage(
        user_id=user.id if user else None,
        message=payload.message if settings.STORE_PREDICTION_TEXT else None,
        label=result['label'],
        blocked=is_bullying,
    )
    db.add(record)
    db.commit()

    if is_bullying:
        return {
            "allowed": False,
            "blocked": True,
            "prediction": "Cyberbullying",
            "confidence": result['confidence'],
            "category": result['category'],
            "severity": result['severity'],
        }
    return {
        "allowed": True,
        "blocked": False,
        "prediction": "Safe",
    }


@router.get("/posts", summary="Simulated social media feed used by the Chat Simulator page")
def simulator_posts():
    return {"success": True, "data": safety_service.SIMULATED_POSTS}
