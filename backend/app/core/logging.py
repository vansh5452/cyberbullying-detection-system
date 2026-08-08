"""
Structured logging setup.

IMPORTANT (security requirement 20): we never log passwords, JWT tokens,
or raw submitted message text - only metadata (lengths, labels, ids).
"""
import logging
import sys

from app.core.config import settings


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("cyberguard")
    if logger.handlers:
        return logger  # already configured (avoid duplicate handlers on reload)

    logger.setLevel(logging.DEBUG if not settings.is_production else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logging()
