"""
Deterministic baseline hydration-goal calculator.

This is intentionally NOT the AI model — it's a transparent, testable formula
layer (grounded in commonly cited hydration guidance: ~35ml/kg body weight
baseline, adjusted for activity, climate/weather, altitude, age, and
condition-specific factors such as pregnancy or breastfeeding). The AI
recommendation engine (app/ai/*) takes this number as a *prior* and layers
retrieval-grounded, personalized natural-language reasoning on top of it —
see app/ai/generation/generator.py. Keeping this layer separate keeps the
number itself auditable even when the language model's phrasing changes.
"""
from dataclasses import dataclass, field

from app.models.user import ActivityLevel, User

ACTIVITY_ML_PER_KG = {
    ActivityLevel.SEDENTARY: 30.0,
    ActivityLevel.LIGHT: 32.0,
    ActivityLevel.MODERATE: 35.0,
    ActivityLevel.ACTIVE: 38.0,
    ActivityLevel.ATHLETE: 42.0,
}


@dataclass
class GoalBreakdown:
    base_ml: float
    weather_adjustment_ml: float = 0.0
    exercise_adjustment_ml: float = 0.0
    health_adjustment_ml: float = 0.0
    notes: list[str] = field(default_factory=list)

    @property
    def total_ml(self) -> float:
        return round(self.base_ml + self.weather_adjustment_ml + self.exercise_adjustment_ml + self.health_adjustment_ml)


def calculate_daily_goal(
    user: User,
    *,
    temperature_c: float | None = None,
    humidity_pct: float | None = None,
    altitude_m: float | None = None,
    exercise_minutes_today: int = 0,
    exercise_intensity: str | None = None,
) -> GoalBreakdown:
    weight = user.weight_kg or 65.0
    activity = user.activity_level or ActivityLevel.MODERATE
    per_kg = ACTIVITY_ML_PER_KG[activity]
    base_ml = weight * per_kg
    notes = [f"Baseline: {per_kg}ml/kg at {weight}kg body weight ({activity.value} activity) = {round(base_ml)}ml"]

    breakdown = GoalBreakdown(base_ml=base_ml, notes=notes)

    # --- Weather ---
    if temperature_c is not None:
        if temperature_c >= 32:
            breakdown.weather_adjustment_ml += 700
            breakdown.notes.append(f"+700ml — high heat ({temperature_c}°C)")
        elif temperature_c >= 27:
            breakdown.weather_adjustment_ml += 400
            breakdown.notes.append(f"+400ml — warm weather ({temperature_c}°C)")
        elif temperature_c <= 5:
            breakdown.weather_adjustment_ml += 150
            breakdown.notes.append(f"+150ml — cold, dry air increases respiratory water loss ({temperature_c}°C)")

    if humidity_pct is not None and humidity_pct < 30 and temperature_c and temperature_c > 20:
        breakdown.weather_adjustment_ml += 150
        breakdown.notes.append(f"+150ml — low humidity ({humidity_pct}%) increases evaporative loss")

    if altitude_m is not None and altitude_m > 1500:
        breakdown.weather_adjustment_ml += 250
        breakdown.notes.append(f"+250ml — altitude ({round(altitude_m)}m) increases fluid loss")

    # --- Exercise ---
    if exercise_minutes_today > 0:
        per_20min = {"light": 100, "moderate": 200, "vigorous": 300}.get(exercise_intensity or "moderate", 200)
        add = round((exercise_minutes_today / 20) * per_20min)
        breakdown.exercise_adjustment_ml += add
        breakdown.notes.append(f"+{add}ml — {exercise_minutes_today} min of {exercise_intensity or 'moderate'} exercise")

    # --- Health / life-stage conditions ---
    if user.pregnant:
        breakdown.health_adjustment_ml += 300
        breakdown.notes.append("+300ml — pregnancy")
    if user.breastfeeding:
        breakdown.health_adjustment_ml += 700
        breakdown.notes.append("+700ml — breastfeeding")
    if user.age is not None and user.age >= 65:
        breakdown.health_adjustment_ml += 150
        breakdown.notes.append("+150ml — reduced thirst sensitivity is common over 65")
    if user.caffeine_cups_per_day:
        add = user.caffeine_cups_per_day * 100
        breakdown.health_adjustment_ml += add
        breakdown.notes.append(f"+{add}ml — offsetting {user.caffeine_cups_per_day} caffeinated drink(s)/day")
    if user.alcohol_units_per_week and user.alcohol_units_per_week > 0:
        breakdown.health_adjustment_ml += 100
        breakdown.notes.append("+100ml — regular alcohol intake increases fluid needs")

    return breakdown
