"""
SQLAlchemy engine/session setup.
Works with SQLite for local dev (DATABASE_URL=sqlite:///./cyberguard.db)
and is PostgreSQL-compatible for production (DATABASE_URL=postgresql://...).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # required for SQLite when used with multiple threads (FastAPI/Uvicorn workers)
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once on startup (dev-friendly; use Alembic for real migrations)."""
    from app.db import models  # noqa: F401  (ensures models are registered on Base)
    Base.metadata.create_all(bind=engine)

    # Auto-seed default admin user if none exists
    from app.db.models import User, UserRole
    from app.core.security import hash_password
    from app.core.logging import logger

    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.role == UserRole.admin).first()
        if not admin_exists:
            admin_user = User(
                username="admin",
                email="admin@cyberguard.ai",
                password_hash=hash_password("AdminPassword123"),
                role=UserRole.admin,
            )
            db.add(admin_user)
            db.commit()
            logger.info("Database initialized and default admin user seeded successfully (username: admin, password: AdminPassword123).")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding default admin user: {e}")
    finally:
        db.close()
