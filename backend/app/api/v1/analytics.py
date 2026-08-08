from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", summary="Dashboard statistics (accuracy + real scan counts)")
def dashboard(db: Session = Depends(get_db)):
    return {"success": True, "data": analytics_service.get_dashboard_stats(db)}


@router.get("/model", summary="Model accuracy, confusion matrix, classification report")
def model_analytics():
    return {"success": True, "data": analytics_service.get_model_analytics()}


@router.get("/top-toxic-words", summary="Top positive Logistic Regression coefficients")
def top_toxic_words(top_n: int = Query(10, ge=1, le=50)):
    return {"success": True, "data": analytics_service.get_top_toxic_words(top_n=top_n)}
