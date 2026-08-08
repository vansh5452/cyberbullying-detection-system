"""
CyberGuard AI API - FastAPI application entrypoint.

Frontend -> REST API -> FastAPI Backend -> Prediction Service ->
Existing ML Model (TF-IDF + Logistic Regression) -> Database / API Response
"""
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import analytics, auth, health, model, predictions, safety, simulator
from app.core.config import settings
from app.core.logging import logger
from app.db.database import init_db

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Cyberbullying Detection System - REST API backend "
                 "wrapping the existing TF-IDF + Logistic Regression model.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------- lifecycle
@app.on_event("startup")
def on_startup():
    init_db()
    logger.info(f"{settings.APP_NAME} starting up (environment={settings.ENVIRONMENT})")


# ------------------------------------------------------------ error handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Our routes raise HTTPException(detail={"code":..., "message":...});
    # normalize plain-string details too so every error follows one format.
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        payload = {"success": False, "error": detail}
    else:
        payload = {"success": False, "error": {"code": "HTTP_ERROR", "message": str(detail)}}
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak internal stack traces to the client.
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {type(exc).__name__}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
        },
    )


# --------------------------------------------------------------- middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(time.time() - start) * 1000:.1f}"
    return response


# ------------------------------------------------------------------ routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(model.router, prefix=settings.API_V1_PREFIX)
app.include_router(simulator.router, prefix=settings.API_V1_PREFIX)
app.include_router(safety.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"], summary="Root")
def root():
    return {"service": settings.APP_NAME, "docs": "/docs", "health": f"{settings.API_V1_PREFIX}/health"}
