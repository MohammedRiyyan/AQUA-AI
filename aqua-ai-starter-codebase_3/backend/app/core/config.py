"""
Central application configuration.
All values are overridable via environment variables / .env — see .env.example.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    APP_NAME: str = "Aqua AI"
    ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security ---
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    OAUTH_GOOGLE_CLIENT_ID: str | None = None
    OAUTH_GOOGLE_CLIENT_SECRET: str | None = None

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://aqua:aqua@localhost:5432/aqua_ai"
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Vector store ---
    VECTOR_BACKEND: str = "faiss"  # "faiss" (local/offline) or "qdrant" (service)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "aqua_hydration_knowledge"
    FAISS_INDEX_PATH: str = "app/ai/retrieval/store/faiss.index"
    FAISS_METADATA_PATH: str = "app/ai/retrieval/store/metadata.jsonl"

    # --- Custom AI model (NO hosted LLM APIs) ---
    # EMBEDDING_MODEL: open-weight sentence-transformers model, run locally.
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    # GENERATION_MODEL_PATH: path to your fine-tuned checkpoint. Until fine-tuning
    # is complete, this points at a small open-weight instruct model as a
    # local placeholder so the RAG pipeline is fully functional end-to-end.
    GENERATION_MODEL_PATH: str = "models/aqua-hydration-llm"  # local dir or HF repo id
    GENERATION_MODEL_FALLBACK: str = "Qwen/Qwen2.5-0.5B-Instruct"
    MAX_NEW_TOKENS: int = 220
    RETRIEVAL_TOP_K: int = 4
    DOMAIN_SIMILARITY_THRESHOLD: float = 0.30  # guardrail cutoff, see guardrails/domain_classifier.py

    # --- Weather ---
    WEATHER_PROVIDER_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"

    # --- CORS ---
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
