from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.deps import require_admin
from app.db.models import User
from app.services import analytics_service
from app.services.model_service import model_service
from app.utils.helpers import api_error

router = APIRouter(prefix="/model", tags=["Model"])


@router.get("/status", summary="Whether the trained model or the lexicon fallback is active")
def model_status():
    return {"success": True, "data": analytics_service.get_model_status()}


@router.post("/retrain", summary="Retrain the model from dataset.csv (admin only)")
def retrain(_: User = Depends(require_admin)):
    try:
        result = model_service.retrain(settings.DATASET_PATH)
    except FileNotFoundError as e:
        raise api_error(404, "DATASET_NOT_FOUND", str(e))
    except ValueError as e:
        raise api_error(422, "INVALID_DATASET", str(e))
    except Exception:
        raise api_error(500, "TRAINING_FAILED", "Model retraining failed. Check server logs for details.")

    return {"success": True, "data": result}
