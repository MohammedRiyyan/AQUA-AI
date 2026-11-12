import enum
import math
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ContainerShape(enum.StrEnum):
    CYLINDER = "cylinder"
    CONE = "cone"
    ROUNDED = "rounded"
    SQUARE = "square"


# Fraction of the bounding cylinder that each shape actually holds.
_SHAPE_FILL_FACTOR = {
    ContainerShape.CYLINDER: 1.0,
    ContainerShape.CONE: 0.75,     # tapered drinking glass (between a cone and a cylinder)
    ContainerShape.ROUNDED: 0.9,   # mugs / bottles with curved sides
}


def estimate_capacity_ml(shape: ContainerShape, height_cm: float, diameter_cm: float) -> float:
    """
    Estimate a container's capacity from its height and diameter ("smart measurement").
    1 cm^3 == 1 ml. For SQUARE containers, `diameter_cm` is the side length.
    """
    if shape == ContainerShape.SQUARE:
        return diameter_cm * diameter_cm * height_cm
    cylinder_volume = math.pi * (diameter_cm / 2) ** 2 * height_cm
    return cylinder_volume * _SHAPE_FILL_FACTOR[shape]


class Container(Base):
    __tablename__ = "containers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()")
    )
    # NULL user_id == global preset (visible to every user)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    capacity_ml: Mapped[float] = mapped_column(Float, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50))
    color: Mapped[str | None] = mapped_column(String(20))
    shape: Mapped[ContainerShape | None] = mapped_column(
        Enum(ContainerShape, name="container_shape", values_callable=lambda e: [m.value for m in e])
    )
    height_cm: Mapped[float | None] = mapped_column(Float)
    diameter_cm: Mapped[float | None] = mapped_column(Float)
    is_estimated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
