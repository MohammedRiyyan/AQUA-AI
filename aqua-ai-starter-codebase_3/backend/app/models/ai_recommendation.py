import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, Float, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RecommendationKind(enum.StrEnum):
    DAILY_ADVICE = "daily_advice"
    REMINDER = "reminder"
    CHAT_ANSWER = "chat_answer"
    GOAL_ADJUSTMENT = "goal_adjustment"


class AIRecommendation(Base):
    """Every AI output is stored with its confidence, reasoning and sources (explainability)."""
    __tablename__ = "ai_recommendations"
    __table_args__ = (CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_ai_recs_confidence"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[RecommendationKind] = mapped_column(
        Enum(RecommendationKind, name="recommendation_kind", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    prompt: Mapped[str | None] = mapped_column(Text)
    output_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text)
    retrieved_sources: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    model_version: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
