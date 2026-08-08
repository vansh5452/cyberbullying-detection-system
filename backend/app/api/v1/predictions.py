import math
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, get_current_user_optional
from app.db.database import get_db
from app.db.models import Prediction, User
from app.schemas.common import SuccessResponse
from app.schemas.prediction import PredictionData, PredictionRequest
from app.services.prediction_service import build_prediction_response, predict_text
from app.utils.helpers import api_error, paginate_params

router = APIRouter(tags=["Predictions"])


def _validate_text(text: str):
    if len(text) < settings.MIN_TEXT_LENGTH:
        raise api_error(422, "INVALID_INPUT", "Text must not be empty.")
    if len(text) > settings.MAX_TEXT_LENGTH:
        raise api_error(
            422, "INVALID_INPUT",
            f"Text must contain between 1 and {settings.MAX_TEXT_LENGTH} characters."
        )


@router.post(
    "/predict",
    response_model=SuccessResponse[PredictionData],
    summary="Analyze a message for cyberbullying content",
)
def predict(
    payload: PredictionRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    _validate_text(payload.text)

    result = predict_text(payload.text)
    data = build_prediction_response(result)

    # Persist to history (works for both anonymous and authenticated callers;
    # anonymous predictions are stored with user_id=None).
    record = Prediction(
        user_id=user.id if user else None,
        input_text=payload.text if settings.STORE_PREDICTION_TEXT else None,
        text_length=len(payload.text),
        label=result['label'],
        is_cyberbullying=result['label'] == 1,
        confidence=result['confidence'],
        method=result['method'],
        category=result['category'],
        severity=result['severity'],
    )
    record.set_matched_words(result['matched_words'])
    db.add(record)
    db.commit()

    return {"success": True, "data": data}


@router.get(
    "/predictions",
    summary="Get the authenticated user's prediction history (paginated)",
)
def list_predictions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    page, limit, offset = paginate_params(page, limit)

    query = db.query(Prediction).filter(Prediction.user_id == user.id).order_by(Prediction.created_at.desc())
    total = query.count()
    rows = query.offset(offset).limit(limit).all()

    items = [
        {
            "id": r.id,
            "input_text": r.input_text,
            "label": r.label,
            "is_cyberbullying": r.is_cyberbullying,
            "confidence": r.confidence,
            "method": r.method,
            "matched_words": r.matched_words_list(),
            "category": r.category,
            "severity": r.severity,
            "created_at": r.created_at,
        }
        for r in rows
    ]

    return {
        "success": True,
        "data": items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": math.ceil(total / limit) if limit else 0,
        },
    }


@router.get("/predictions/{prediction_id}", summary="Get a single prediction by id")
def get_prediction(prediction_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not record:
        raise api_error(404, "NOT_FOUND", "Prediction not found.")
    if record.user_id != user.id:
        raise api_error(403, "FORBIDDEN", "You do not have access to this prediction.")

    return {
        "success": True,
        "data": {
            "id": record.id,
            "input_text": record.input_text,
            "label": record.label,
            "is_cyberbullying": record.is_cyberbullying,
            "confidence": record.confidence,
            "method": record.method,
            "matched_words": record.matched_words_list(),
            "category": record.category,
            "severity": record.severity,
            "created_at": record.created_at,
        },
    }
