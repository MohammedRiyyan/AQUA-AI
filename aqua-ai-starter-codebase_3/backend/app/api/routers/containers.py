from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.container import Container, estimate_capacity_ml
from app.models.user import User
from app.schemas.water_log import ContainerCreate, ContainerOut

router = APIRouter(prefix="/containers", tags=["containers"])


@router.get("", response_model=list[ContainerOut])
async def list_containers(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Global presets (glasses/bottles) plus this user's custom containers."""
    result = await db.scalars(
        select(Container).where(or_(Container.user_id.is_(None), Container.user_id == user.id))
    )
    return result.all()


@router.post("", response_model=ContainerOut, status_code=201)
async def create_container(
    payload: ContainerCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    capacity = payload.capacity_ml
    is_estimated = False

    if capacity is None:
        if not (payload.shape and payload.height_cm and payload.diameter_cm):
            raise HTTPException(400, detail="Provide capacity_ml, or shape + height_cm + diameter_cm for smart measurement")
        capacity = round(estimate_capacity_ml(payload.shape, payload.height_cm, payload.diameter_cm))
        is_estimated = True

    container = Container(
        user_id=user.id,
        name=payload.name,
        capacity_ml=capacity,
        icon=payload.icon,
        color=payload.color,
        shape=payload.shape,
        height_cm=payload.height_cm,
        diameter_cm=payload.diameter_cm,
        is_estimated=is_estimated,
    )
    db.add(container)
    await db.commit()
    await db.refresh(container)
    return container
