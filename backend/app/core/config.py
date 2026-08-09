"""
CyberGuard AI API - Application Configuration
Loads all runtime configuration from environment variables (.env file).
Nothing here is hard-coded that should differ between dev and production.
"""
import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    # --- App metadata ---
    APP_NAME: str = os.getenv("APP_NAME", "CyberGuard AI API")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    API_V1_PREFIX: str = "/api/v1"

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cyberguard.db")

    # --- Auth / JWT ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # --- ML model (preserves the existing model.py / cyberbullying_model.pkl contract) ---
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/cyberbullying_model.pkl")
    DATASET_PATH: str = os.getenv("DATASET_PATH", "dataset.csv")

    # --- CORS ---
    ALLOWED_ORIGINS: List[str] = _split_csv(
        os.getenv("ALLOWED_ORIGINS", "http://localhost:8501")
    )

    # --- Privacy ---
    # When False, raw submitted text is NOT persisted to the database -
    # only prediction metadata (label, confidence, category, etc.) is stored.
    STORE_PREDICTION_TEXT: bool = os.getenv("STORE_PREDICTION_TEXT", "true").lower() == "true"

    # --- Request limits ---
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "5000"))
    MIN_TEXT_LENGTH: int = 1

    # --- Rate limiting ---
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
# --- One-time admin setup (see /auth/promote-admin) ---
    ADMIN_SETUP_KEY: str = os.getenv("ADMIN_SETUP_KEY", "")
    # --- Server ---
    PORT: int = int(os.getenv("PORT", "8000"))

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
