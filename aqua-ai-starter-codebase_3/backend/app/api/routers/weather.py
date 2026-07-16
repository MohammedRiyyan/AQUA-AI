from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.weather_service import get_current_weather

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current")
async def current_weather(
    lat: float,
    lon: float,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    snapshot = await get_current_weather(db, user.city or "unknown", lat, lon)
    return {
        "city": snapshot.city,
        "temperature_c": snapshot.temperature_c,
        "humidity_pct": snapshot.humidity_pct,
        "fetched_at": snapshot.fetched_at,
    }
