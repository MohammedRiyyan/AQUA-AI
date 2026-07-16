"""
Unit tests for the deterministic hydration goal calculator. Run with:
    pytest backend/tests/test_hydration_calculator.py
"""
from app.models.user import ActivityLevel, User
from app.services.hydration_calculator import calculate_daily_goal


def make_user(**overrides) -> User:
    defaults = dict(email="test@example.com", hashed_password="x", weight_kg=70.0, activity_level=ActivityLevel.MODERATE)
    defaults.update(overrides)
    return User(**defaults)


def test_baseline_goal_uses_activity_multiplier():
    user = make_user(weight_kg=70, activity_level=ActivityLevel.MODERATE)
    breakdown = calculate_daily_goal(user)
    assert breakdown.base_ml == 70 * 35.0
    assert breakdown.total_ml == round(70 * 35.0)


def test_hot_weather_increases_goal():
    user = make_user()
    breakdown = calculate_daily_goal(user, temperature_c=35)
    assert breakdown.weather_adjustment_ml == 700


def test_exercise_adds_proportional_amount():
    user = make_user()
    breakdown = calculate_daily_goal(user, exercise_minutes_today=60, exercise_intensity="vigorous")
    assert breakdown.exercise_adjustment_ml == 900  # 60/20 * 300


def test_pregnancy_and_breastfeeding_stack():
    user = make_user(pregnant=True, breastfeeding=True)
    breakdown = calculate_daily_goal(user)
    assert breakdown.health_adjustment_ml == 1000


def test_caffeine_offset_scales_with_cups():
    user = make_user(caffeine_cups_per_day=3)
    breakdown = calculate_daily_goal(user)
    assert breakdown.health_adjustment_ml == 300
