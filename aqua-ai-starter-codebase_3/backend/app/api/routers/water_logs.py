from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.goal import Goal
from app.models.user import User
from app.models.water_log import WaterLog
from app.schemas.water_log import DailySummary, WaterLogCreate, WaterLogOut

router = APIRouter(prefix="/water-logs", tags=["water-logs"])


@router.post("", response_model=WaterLogOut, status_code=201)
async def log_water(
    payload: WaterLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = WaterLog(user_id=user.id, **payload.model_dump())
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.get("/today", response_model=list[WaterLogOut])
async def today_logs(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.scalars(
        select(WaterLog)
        .where(WaterLog.user_id == user.id, WaterLog.logged_at >= start_of_day)
        .order_by(WaterLog.logged_at.desc())
    )
    return result.all()


@router.get("/summary", response_model=DailySummary)
async def daily_summary(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    today = date.today()
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    consumed = await db.scalar(
        select(func.coalesce(func.sum(WaterLog.amount_ml), 0)).where(
            WaterLog.user_id == user.id, WaterLog.logged_at >= start_of_day
        )
    )
    goal_row = await db.scalar(
        select(Goal).where(Goal.user_id == user.id, Goal.target_date == today).order_by(Goal.created_at.desc())
    )
    goal_ml = goal_row.target_ml if goal_row else 2600.0  # sensible default until first AI calculation runs

    pct = round((consumed / goal_ml) * 100, 1) if goal_ml else 0.0
    score = "great" if pct >= 90 else "good" if pct >= 60 else "low" if pct >= 30 else "needs_water"

    return DailySummary(
        date=today.isoformat(),
        consumed_ml=consumed,
        goal_ml=goal_ml,
        remaining_ml=max(0.0, goal_ml - consumed),
        hydration_percentage=pct,
        hydration_score=score,
    )


@router.get("/weekly", response_model=list[DailySummary])
async def weekly_summary(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Last 7 days of totals — powers the dashboard's weekly chart."""
    today = date.today()
    summaries = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        consumed = await db.scalar(
            select(func.coalesce(func.sum(WaterLog.amount_ml), 0)).where(
                WaterLog.user_id == user.id, WaterLog.logged_at >= day_start, WaterLog.logged_at < day_end
            )
        )
        goal_row = await db.scalar(select(Goal).where(Goal.user_id == user.id, Goal.target_date == day))
        goal_ml = goal_row.target_ml if goal_row else 2600.0
        pct = round((consumed / goal_ml) * 100, 1) if goal_ml else 0.0
        score = "great" if pct >= 90 else "good" if pct >= 60 else "low" if pct >= 30 else "needs_water"
        summaries.append(
            DailySummary(
                date=day.isoformat(), consumed_ml=consumed, goal_ml=goal_ml,
                remaining_ml=max(0.0, goal_ml - consumed), hydration_percentage=pct, hydration_score=score,
            )
        )
    return summaries
