from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.goal import Goal
from app.models.user import User
from app.services.hydration_calculator import calculate_daily_goal
from app.services.weather_service import get_current_weather

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/recalculate")
async def recalculate_today_goal(
    lat: float,
    lon: float,
    exercise_minutes_today: int = 0,
    exercise_intensity: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Recomputes today's goal from the user's profile plus live weather and
    today's exercise. Call this on login, after a workout sync, or whenever
    the weather materially changes — it's cheap (no LLM call), deterministic,
    and fully auditable via the returned breakdown.
    """
    weather = await get_current_weather(db, user.city or "unknown", lat, lon)

    breakdown = calculate_daily_goal(
        user,
        temperature_c=weather.temperature_c,
        humidity_pct=weather.humidity_pct,
        exercise_minutes_today=exercise_minutes_today,
        exercise_intensity=exercise_intensity,
    )

    goal = Goal(
        user_id=user.id,
        target_date=date.today(),
        target_ml=breakdown.total_ml,
        base_ml=breakdown.base_ml,
        weather_adjustment_ml=breakdown.weather_adjustment_ml,
        exercise_adjustment_ml=breakdown.exercise_adjustment_ml,
        health_adjustment_ml=breakdown.health_adjustment_ml,
        reasoning=" | ".join(breakdown.notes),
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal
