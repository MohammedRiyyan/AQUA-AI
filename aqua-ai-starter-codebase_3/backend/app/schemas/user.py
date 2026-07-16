import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import ActivityLevel, UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileUpdate(BaseModel):
    """All fields optional — the profile is filled in incrementally."""
    name: str | None = None
    age: int | None = None
    gender: str | None = None
    weight_kg: float | None = None
    height_cm: float | None = None
    country: str | None = None
    city: str | None = None
    occupation: str | None = None
    activity_level: ActivityLevel | None = None
    sleep_hours: float | None = None
    exercise_frequency_per_week: int | None = None
    daily_walking_minutes: int | None = None
    medical_conditions: str | None = None
    pregnant: bool | None = None
    breastfeeding: bool | None = None
    climate: str | None = None
    diet: str | None = None
    caffeine_cups_per_day: int | None = None
    alcohol_units_per_week: int | None = None
    smoker: bool | None = None
    primary_goal: str | None = None


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str | None
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True
