from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


# Import models here so Alembic's autogenerate can discover them via Base.metadata
from app.models import (  # noqa: E402,F401
    achievement,
    ai_recommendation,
    container,
    document,
    goal,
    health_profile,
    user,
    water_log,
    weather,
)
