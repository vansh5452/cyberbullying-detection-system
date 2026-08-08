"""
SQLAlchemy ORM models: User, Prediction, ChatMessage.
"""
import enum
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)

    # Nullable: when STORE_PREDICTION_TEXT=false, only metadata is kept, not raw text.
    input_text = Column(Text, nullable=True)
    text_length = Column(Integer, nullable=False, default=0)

    label = Column(Integer, nullable=False)  # 0 = safe, 1 = cyberbullying
    is_cyberbullying = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    method = Column(String(64), nullable=False)
    matched_words = Column(Text, nullable=True)  # JSON-encoded list
    category = Column(String(64), nullable=False, default="Not Applicable")
    severity = Column(String(32), nullable=False, default="None")

    created_at = Column(DateTime, default=_utcnow, nullable=False)

    user = relationship("User", back_populates="predictions")

    def matched_words_list(self):
        if not self.matched_words:
            return []
        try:
            return json.loads(self.matched_words)
        except (TypeError, ValueError):
            return []

    def set_matched_words(self, words):
        self.matched_words = json.dumps(words or [])


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)

    message = Column(Text, nullable=True)
    label = Column(Integer, nullable=False)  # 0 = safe, 1 = cyberbullying
    blocked = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=_utcnow, nullable=False)

    user = relationship("User", back_populates="chat_messages")
