# Prerequisites

Everything `pip install` and `npm install` won't tell you about. Check this
before `docker compose up` or a local (non-Docker) setup.

## If you're using Docker (recommended path)

You only need:
- **Docker** 24+ and **Docker Compose** v2 (`docker compose version` should work — not the old standalone `docker-compose`)
- **~6 GB free disk space** — the backend image installs `torch` + `transformers` (~3 GB of wheels), and the fallback model + embedding model download into a volume on first run
- **Internet access on first run** (see below) — after that, models are cached in the `model_cache` volume and subsequent starts are offline-capable except for the weather endpoint

Everything else (Python, Node, Postgres, Redis, Qdrant) runs inside containers — you don't need them installed locally.

## If you're running locally without Docker

- **Python 3.11** (pinned in `backend/.python-version` — use `pyenv install 3.11` if you don't have it; 3.12+ isn't tested against these pinned dependency versions)
- **Node.js 20** (pinned in `frontend/.nvmrc` — `nvm use` picks it up automatically)
- **PostgreSQL 16** running locally, with `psql` on your PATH to run `database/schema.sql` / `seed.sql`
- **Redis** running locally (only needed once you actually wire up caching/background jobs — nothing currently fails without it, but it's in the stack)
- **A C compiler + `libpq-dev`** (Linux) or Xcode Command Line Tools (macOS) — usually only needed if `asyncpg` doesn't have a prebuilt wheel for your platform/Python version. Ubuntu/Debian: `sudo apt install build-essential libpq-dev`
- Optionally, a **Qdrant** instance (`docker run -p 6333:6333 qdrant/qdrant`) if you set `VECTOR_BACKEND=qdrant` instead of the default `faiss` — FAISS needs nothing extra, it's an embedded index

## Internet access is required on first run, for two things

1. **Model downloads** (Hugging Face Hub) — `sentence-transformers/all-MiniLM-L6-v2` (~90 MB) and the fallback generator `Qwen/Qwen2.5-0.5B-Instruct` (~1 GB) download the first time `app/ai/retrieval/embeddings.py` or `app/ai/generation/generator.py` load. If you're deploying fully offline, pre-download both with `huggingface-cli download <repo>` and point the cache accordingly (or drop your own fine-tuned checkpoint at `GENERATION_MODEL_PATH` — no download needed at that point).
2. **Weather** — `/weather/current` and `/goals/recalculate` call Open-Meteo (`api.open-meteo.com`) live, no API key needed but it does need outbound internet.

## Hardware

- **CPU-only works fine** for the placeholder Qwen 0.5B model — expect a few seconds per generation, not sub-second.
- **GPU is optional**, not required. If you have an NVIDIA GPU + CUDA available, `generator.py` already detects and uses it (`torch.cuda.is_available()`); no code changes needed.
- **RAM**: 8 GB minimum for the backend container comfortably; 16 GB+ if you're also fine-tuning locally later.

## Accounts / API keys

**None required to run this as-is.** Everything (weather, embeddings, generation) runs against free/no-key services or fully locally. The only credential you'll ever need to set is `SECRET_KEY` in `backend/.env` (used for signing JWTs — not an external service).

`OAUTH_GOOGLE_CLIENT_ID` / `OAUTH_GOOGLE_CLIENT_SECRET` in `config.py` are placeholders for a Google login flow that isn't built yet — ignore them unless you're implementing that feature.
