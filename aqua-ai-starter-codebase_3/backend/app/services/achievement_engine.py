"""
Evaluates achievement-unlock criteria after each water log or daily rollup.
Achievement catalog rows live in the DB (see Achievement model / seed data
in database/seed.sql) — this module maps each `key` to the check that
decides whether a user has earned it.
"""
from dataclasses import dataclass


@dataclass
class AchievementContext:
    current_streak_days: int
    lifetime_total_ml: float
    today_hit_goal: bool
    days_tracked: int


CRITERIA_CHECKS = {
    "seven_day_streak": lambda ctx: ctx.current_streak_days >= 7,
    "hydration_master": lambda ctx: ctx.current_streak_days >= 30,
    "ocean_level": lambda ctx: ctx.lifetime_total_ml >= 50_000,
    "aqua_legend": lambda ctx: ctx.current_streak_days >= 100,
    "100l_club": lambda ctx: ctx.lifetime_total_ml >= 100_000,
    "500l_club": lambda ctx: ctx.lifetime_total_ml >= 500_000,
}


def newly_unlocked(ctx: AchievementContext, already_unlocked_keys: set[str]) -> list[str]:
    """Returns achievement keys the user just qualified for, excluding ones they already have."""
    return [key for key, check in CRITERIA_CHECKS.items() if key not in already_unlocked_keys and check(ctx)]
