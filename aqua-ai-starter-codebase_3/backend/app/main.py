from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import achievements, admin_training, ai, auth, containers, goals, users, water_logs, weather
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Every Drop Counts — AI-powered water intake tracker with a custom-trained hydration model.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth, users, water_logs, containers, ai, goals, achievements, weather, admin_training):
    app.include_router(router.router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["meta"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
