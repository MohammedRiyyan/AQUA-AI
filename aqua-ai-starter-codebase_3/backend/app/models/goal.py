import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Goal(Base):
    """A user's daily hydration target, with the breakdown that produced it."""
    __tablename__ = "goals"
    __table_args__ = (Index("idx_goals_user_date", "user_id", "target_date"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_ml: Mapped[float] = mapped_column(Float, nullable=False)
    base_ml: Mapped[float] = mapped_column(Float, nullable=False)
    weather_adjustment_ml: Mapped[float] = mapped_column(Float, nullable=False, default=0, server_default="0")
    exercise_adjustment_ml: Mapped[float] = mapped_column(Float, nullable=False, default=0, server_default="0")
    health_adjustment_ml: Mapped[float] = mapped_column(Float, nullable=False, default=0, server_default="0")
    reasoning: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
