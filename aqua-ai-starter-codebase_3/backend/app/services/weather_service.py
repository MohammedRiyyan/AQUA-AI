"""
Fetches current weather for a user's city, with a short-lived cache in
Postgres (WeatherSnapshot) so we don't call the provider on every request.
Uses Open-Meteo by default (no API key required); swap WEATHER_PROVIDER_BASE_URL
for any provider that returns temperature/humidity by lat-lon.
"""
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.weather import WeatherSnapshot

settings = get_settings()
CACHE_TTL = timedelta(minutes=30)


async def get_current_weather(db: AsyncSession, city: str, lat: float, lon: float) -> WeatherSnapshot:
    cached = await db.scalar(
        select(WeatherSnapshot)
        .where(WeatherSnapshot.city == city)
        .order_by(WeatherSnapshot.fetched_at.desc())
    )
    if cached and (datetime.now(timezone.utc) - cached.fetched_at) < CACHE_TTL:
        return cached

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            settings.WEATHER_PROVIDER_BASE_URL,
            params={"latitude": lat, "longitude": lon, "current": "temperature_2m,relative_humidity_2m", "timezone": "auto"},
        )
        resp.raise_for_status()
        data = resp.json()["current"]

    snapshot = WeatherSnapshot(
        city=city,
        temperature_c=data["temperature_2m"],
        humidity_pct=data.get("relative_humidity_2m"),
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return snapshot
