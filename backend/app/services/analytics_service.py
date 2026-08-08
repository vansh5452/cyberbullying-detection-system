"""
analytics_service.py

Dashboard + model analytics, backed by the database (real stored prediction
rows) and the loaded model's own stored metrics. Nothing here is fabricated:
if the model hasn't been trained, or there are no predictions yet, the
relevant fields come back as None/0 rather than invented numbers.
"""
from typing import Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Prediction
from app.services.model_service import model_service


def get_model_status() -> Dict:
    return {
        "model_loaded": model_service.is_loaded,
        "model_type": "TF-IDF + Logistic Regression",
        "fallback_available": True,
        "accuracy": model_service.accuracy,
    }


def get_model_analytics() -> Dict:
    return {
        "accuracy": model_service.accuracy,
        "confusion_matrix": model_service.confusion_matrix,
        "classification_report": model_service.classification_report,
        "model_type": "TF-IDF + Logistic Regression",
        "trained": model_service.is_loaded,
    }


def get_top_toxic_words(top_n: int = 10):
    words = model_service.top_toxic_words(top_n=top_n)
    return [{"word": w, "weight": weight} for w, weight in words]


def get_dashboard_stats(db: Session) -> Dict:
    """Real counts pulled from the predictions table - not session-state
    counters, so stats now persist across restarts and across users."""
    total = db.query(func.count(Prediction.id)).scalar() or 0
    bullying = (
        db.query(func.count(Prediction.id))
        .filter(Prediction.is_cyberbullying.is_(True))
        .scalar()
        or 0
    )
    safe = total - bullying

    return {
        "model_accuracy": model_service.accuracy,
        "messages_scanned": total,
        "safe_messages": safe,
        "cyberbullying_detected": bullying,
    }
