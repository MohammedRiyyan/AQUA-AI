import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(enum.StrEnum):
    ADMIN = "admin"
    USER = "user"
    RESEARCHER = "researcher"


class ActivityLevel(enum.StrEnum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    ATHLETE = "athlete"


def _values(enum_cls):
    return [member.value for member in enum_cls]


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()")
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=_values),
        nullable=False,
        default=UserRole.USER,
        server_default="user",
    )

    # --- profile (filled in incrementally) ---
    name: Mapped[str | None] = mapped_column(String(120))
    age: Mapped[int | None] = mapped_column(Integer)
    gender: Mapped[str | None] = mapped_column(String(30))
    weight_kg: Mapped[float | None] = mapped_column(Float)
    height_cm: Mapped[float | None] = mapped_column(Float)
    country: Mapped[str | None] = mapped_column(String(80))
    city: Mapped[str | None] = mapped_column(String(80))
    occupation: Mapped[str | None] = mapped_column(String(120))
    activity_level: Mapped[ActivityLevel | None] = mapped_column(
        Enum(ActivityLevel, name="activity_level", values_callable=_values)
    )
    sleep_hours: Mapped[float | None] = mapped_column(Float)
    exercise_frequency_per_week: Mapped[int | None] = mapped_column(Integer)
    daily_walking_minutes: Mapped[int | None] = mapped_column(Integer)
    medical_conditions: Mapped[str | None] = mapped_column(String(500))
    pregnant: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    breastfeeding: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    climate: Mapped[str | None] = mapped_column(String(50))
    diet: Mapped[str | None] = mapped_column(String(80))
    caffeine_cups_per_day: Mapped[int | None] = mapped_column(Integer)
    alcohol_units_per_week: Mapped[int | None] = mapped_column(Integer)
    smoker: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    primary_goal: Mapped[str | None] = mapped_column(String(50))

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
