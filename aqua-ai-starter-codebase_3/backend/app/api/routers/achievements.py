from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.achievement import Achievement, UserAchievement
from app.models.user import User
from app.models.water_log import WaterLog
from app.services.achievement_engine import AchievementContext, newly_unlocked

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get("")
async def list_achievements(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    all_achievements = (await db.scalars(select(Achievement))).all()
    unlocked = {
        ua.achievement_id
        for ua in (await db.scalars(select(UserAchievement).where(UserAchievement.user_id == user.id))).all()
    }
    return [
        {"key": a.key, "name": a.name, "description": a.description, "icon": a.icon, "unlocked": a.id in unlocked}
        for a in all_achievements
    ]


@router.post("/evaluate")
async def evaluate_achievements(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Re-checks unlock criteria (call after logging water). In production this
    would also run on a nightly job to catch streak-based unlocks that
    depend on "yesterday didn't break the streak" rather than a single event.
    """
    lifetime_total = await db.scalar(select(func.coalesce(func.sum(WaterLog.amount_ml), 0)).where(WaterLog.user_id == user.id))
    already = {
        row.achievement.key
        for row in (await db.scalars(select(UserAchievement).where(UserAchievement.user_id == user.id))).all()
    }

    ctx = AchievementContext(
        current_streak_days=0,  # TODO: compute from consecutive days meeting goal
        lifetime_total_ml=lifetime_total,
        today_hit_goal=False,
        days_tracked=0,
    )
    unlocked_keys = newly_unlocked(ctx, already)

    for key in unlocked_keys:
        achievement = await db.scalar(select(Achievement).where(Achievement.key == key))
        if achievement:
            db.add(UserAchievement(user_id=user.id, achievement_id=achievement.id))
    await db.commit()
    return {"newly_unlocked": unlocked_keys}
