from fastapi import APIRouter

from app.services.model_service import model_service

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Liveness / readiness check")
def health_check():
    """Basic liveness check. Intentionally does NOT depend on the database,
    so the service can report 'healthy' even if the DB is briefly unavailable."""
    return {
        "status": "healthy",
        "service": "CyberGuard AI API",
        "model_loaded": model_service.is_loaded,
    }
