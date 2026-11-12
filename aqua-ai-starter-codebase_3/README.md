# Aqua AI — *Every Drop Counts*

An AI-powered water intake tracker built around a **custom-trained hydration
model** — not a wrapper around OpenAI, Claude, Gemini, Llama-API, DeepSeek,
Grok, or any other hosted LLM. Every recommendation the app shows comes from
a locally-run retrieval-augmented generation (RAG) pipeline over a knowledge
base you control (WHO/CDC guidelines, research papers, your own datasets).

This repo is a **starter codebase**, not a finished product: it gives you a
working, coherent architecture across every layer (UI, API, database, AI
pipeline, deployment) that you can build out feature-by-feature. See
[What's stubbed vs. real](#whats-stubbed-vs-real) before you dive in.

---

## What's in here

```
aqua-ai/
├── frontend/                Next.js 14 + TypeScript + Tailwind app
├── backend/                 FastAPI + SQLAlchemy + custom RAG pipeline
├── database/                 Raw SQL schema + seed data (mirrors the SQLAlchemy models)
├── docker-compose.yml        Postgres + Redis + Qdrant + backend + frontend, one command
└── .github/workflows/ci.yml  Lint, test, build on every push
```

### Try the UI quickly

The Next.js UI can run on its own (no backend, database or Docker needed) to preview the screens:

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

Features that call the API (login, logging water, AI coach) need the backend — see below.

### Run the full stack

> Check [`PREREQUISITES.md`](./PREREQUISITES.md) first — Docker vs. local dev need different things installed, and there's a one-time internet requirement for model downloads.

```bash
cp backend/.env.example backend/.env
docker compose up --build
```
- Frontend → http://localhost:3000
- Backend docs (Swagger) → http://localhost:8000/docs
- Qdrant dashboard → http://localhost:6333/dashboard

First run: the Postgres container auto-applies `database/schema.sql` and
`database/seed.sql`. Register a user via `POST /api/v1/auth/register`, then
promote yourself to `admin` in the DB to access the training console at
`/admin`.

---

## Architecture

**Frontend** — Next.js App Router, TypeScript, Tailwind, a small typed API
client (`src/lib/api.ts`). The visual language is documented inline in
`tailwind.config.ts` and `globals.css`: an Apple/VisionOS-inspired glass
surface system (`--glass-bg`, `--glass-border`, backdrop blur) over an
ambient animated-gradient background, with the **Aqua Orb** — a real SVG
liquid simulation with wave physics and rising bubbles — as the signature
element instead of a generic progress ring.

**Backend** — FastAPI, async SQLAlchemy 2.0, JWT auth with role-based access
(`admin` / `user` / `researcher`, matching the brief's security
requirements). Routers map 1:1 to the feature list: `auth`, `users`,
`water_logs`, `containers`, `goals`, `ai`, `achievements`, `weather`,
`admin_training`.

**AI / RAG pipeline** (`backend/app/ai/`) — this is the part that makes the
"custom AI model" requirement real rather than aspirational:

```
Upload (admin console) → loaders.py → chunker.py → embeddings.py → vector_store.py
                                                                          │
User question → domain_classifier.py (guardrail) → retriever.py ────────┘
                                                          │
                                              generator.py (local LLM)
                                                          │
                                              explainability.py → AIAnswer
                                              {text, confidence, sources, reasoning}
```

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` by default, run
  locally via `sentence-transformers`. Swap for your own fine-tuned
  bi-encoder in `core/config.py`.
- **Vector store**: FAISS (embedded, zero infra) or Qdrant (service, in
  `docker-compose.yml`) — same interface, chosen via `VECTOR_BACKEND`.
- **Generation**: `app/ai/generation/generator.py` loads a local
  `transformers` causal LM. It resolves `GENERATION_MODEL_PATH` (your
  fine-tuned checkpoint) first, and falls back to a small open-weight
  instruct model (`Qwen/Qwen2.5-0.5B-Instruct`) so the pipeline is runnable
  **today**, before your fine-tune exists. Swap the checkpoint path once
  training is done — nothing else in the codebase changes.
- **Domain guardrail**: a two-layer check (keyword screen + embedding
  similarity against the corpus centroid) rejects anything outside
  hydration/water science *before* generation runs, with a fixed honest
  refusal rather than a best-effort off-topic answer.
- **Explainability**: every answer — daily advice, reminders, chat — is
  stored with its confidence score, retrieved sources, and a plain-language
  reasoning string (`ai_recommendations` table), so it's auditable after the
  fact, not just displayed once and forgotten.

**Hydration goal calculator** (`backend/app/services/hydration_calculator.py`)
is deliberately a separate, deterministic, unit-tested formula layer — not
part of the LLM. It computes the actual target-ml number from weight,
activity level, weather, exercise, and health factors (pregnancy,
breastfeeding, age, caffeine, alcohol). The AI model explains and
contextualizes that number in natural language; it doesn't invent it. This
split keeps the number auditable even as the model's phrasing evolves.

**Database** — see `database/schema.sql` for the full DDL (mirrors
`backend/app/models/`). Prefer Alembic migrations for real deployments;
`schema.sql` is the fast path for local dev and a readable reference.

---

## What's stubbed vs. real

| Feature | Status |
|---|---|
| Water logging, quick-add, custom containers, smart glass measurement | **Real** — full API + DB + UI |
| Hydration goal calculator (weather/exercise/health adjustments) | **Real** — deterministic, unit-tested |
| RAG pipeline (ingestion → embedding → retrieval → generation → explainability) | **Real**, running on a placeholder open-weight model until you fine-tune your own |
| Domain guardrail | **Real**, heuristic — replace with a trained classifier once you have labeled off-topic examples |
| Auth (JWT, roles) | **Real** |
| Admin training console (upload → auto chunk/embed/index) | **Real** |
| Achievements | **Real** unlock logic for total-volume badges; streak tracking is stubbed (`current_streak_days` needs a daily rollup job) |
| Weekly analytics | **Real**; monthly/yearly are one router each, following the same pattern |
| Weather-based adjustment | **Real**, via Open-Meteo (no API key needed) |
| Computer vision (camera → fill level) | **Not started** — the brief marks this "optional future module"; the `vision` log source is modeled but unimplemented |
| Apple Health / Google Fit / Samsung Health / smartwatch sync | **Not started** — `DailyHealthData.sync_source` models the field; needs each platform's SDK integration |
| Family accounts, doctor dashboard, voice logging, QR sharing, offline mode, cloud backup, widgets | **Not started** — out of scope for a first pass; each is a self-contained feature that layers onto the existing user/auth model |

---

## Training your own model

1. Collect hydration-domain text (research papers, WHO/CDC PDFs, Q&A pairs)
   and upload via the admin console (`/admin` → calls
   `POST /api/v1/admin/documents`). This populates the vector index
   automatically — that part works today with the placeholder generator.
2. For the generator itself: fine-tune an open-weight base model (e.g. a
   small Llama/Qwen/Mistral variant) on hydration-domain instruction data.
   Standard approaches: LoRA/QLoRA fine-tuning with `transformers` +
   `peft`, or full fine-tuning if you have the compute. This repo doesn't
   include a training script (that depends heavily on your dataset format
   and compute budget), but `generator.py` is written so that dropping your
   checkpoint's path into `GENERATION_MODEL_PATH` is the *only* change
   needed to go live.
3. For the embedding model: if retrieval quality on your corpus is weak
   with the default MiniLM model, fine-tune a bi-encoder on
   question↔passage pairs mined from your documents
   (`sentence-transformers` has a straightforward training API for this).

---

## Local development without Docker

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point DATABASE_URL at a local Postgres
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Run backend tests: `cd backend && pytest -v` (currently covers the
hydration goal calculator — extend as you add routers).

---

## Tech stack

Frontend: React · Next.js · TypeScript · Tailwind CSS · Framer Motion
Backend: FastAPI · Python · PostgreSQL · Redis
AI: PyTorch · Transformers · Sentence-Transformers · FAISS / Qdrant · your fine-tuned checkpoint
No external AI APIs, anywhere.
