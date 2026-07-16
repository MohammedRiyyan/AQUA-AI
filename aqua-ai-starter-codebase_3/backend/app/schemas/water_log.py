import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.container import ContainerShape
from app.models.water_log import LogSource


class WaterLogCreate(BaseModel):
    amount_ml: float = Field(gt=0, le=5000)
    container_id: uuid.UUID | None = None
    source: LogSource = LogSource.MANUAL
    note: str | None = None


class WaterLogOut(BaseModel):
    id: uuid.UUID
    amount_ml: float
    container_id: uuid.UUID | None
    source: LogSource
    logged_at: datetime

    class Config:
        from_attributes = True


class DailySummary(BaseModel):
    date: str
    consumed_ml: float
    goal_ml: float
    remaining_ml: float
    hydration_percentage: float
    hydration_score: str  # "great" | "good" | "low" | "needs_water"


class ContainerCreate(BaseModel):
    name: str = Field(max_length=80)
    capacity_ml: float | None = Field(default=None, gt=0, le=5000)
    icon: str | None = None
    color: str | None = None

    # smart-glass measurement inputs — provide these instead of capacity_ml
    shape: ContainerShape | None = None
    height_cm: float | None = Field(default=None, gt=0, le=60)
    diameter_cm: float | None = Field(default=None, gt=0, le=30)


class ContainerOut(BaseModel):
    id: uuid.UUID
    name: str
    capacity_ml: float
    icon: str | None
    color: str | None
    is_estimated: bool

    class Config:
        from_attributes = True
