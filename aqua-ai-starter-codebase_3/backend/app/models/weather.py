import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Index, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WeatherSnapshot(Base):
    """Cached weather reading per city (avoids calling the provider on every request)."""
    __tablename__ = "weather_snapshots"
    __table_args__ = (Index("idx_weather_city_fetched", "city", "fetched_at"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()")
    )
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    country: Mapped[str | None] = mapped_column(String(80))
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct: Mapped[float | None] = mapped_column(Float)
    altitude_m: Mapped[float | None] = mapped_column(Float)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
