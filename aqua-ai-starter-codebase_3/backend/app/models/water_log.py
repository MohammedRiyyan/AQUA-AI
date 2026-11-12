import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, Float, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LogSource(enum.StrEnum):
    MANUAL = "manual"
    QUICK_ADD = "quick_add"
    VOICE = "voice"
    VISION = "vision"
    HEALTH_SYNC = "health_sync"


class WaterLog(Base):
    __tablename__ = "water_logs"
    __table_args__ = (
        CheckConstraint("amount_ml > 0 AND amount_ml <= 5000", name="ck_water_logs_amount"),
        Index("idx_water_logs_user_logged_at", "user_id", "logged_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    container_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("containers.id"))
    amount_ml: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[LogSource] = mapped_column(
        Enum(LogSource, name="log_source", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=LogSource.MANUAL,
        server_default="manual",
    )
    note: Mapped[str | None] = mapped_column(String(200))
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
