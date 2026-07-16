# Aqua AI — Project Documentation

*Every Drop Counts*

---

## 1. What this project is

Aqua AI is an AI-powered water intake tracker built around one non-negotiable
constraint: **the AI has to be a custom-trained model you own, not a wrapper
around a hosted LLM.** No OpenAI, no Claude, no Gemini, no Llama-API, no
DeepSeek, no Grok — anywhere in the request path.

That constraint shapes almost every architectural decision in this repo. A
typical "AI water tracker" would be a CRUD app with a system prompt bolted
onto a hosted chat API. This one instead has to include the actual
machinery a real custom model needs: a retrieval pipeline over a knowledge
base you control, a local generation model you can swap for your own
fine-tuned checkpoint, a domain guardrail so it doesn't turn into a general
chatbot, and an explainability layer so every recommendation is traceable
back to a source and a confidence score — not just a plausible-sounding
sentence.

This document explains what was built, why it's structured the way it is,
and exactly how data moves through the system. For setup commands, see
`README.md`; for system-level prerequisites, see `PREREQUISITES.md`. This
document is the "how it works and why," not the "how to run it."

---

## 2. Design philosophy

### 2.1 Visual language

The brief asked for an "Apple + Nothing OS + VisionOS inspired Fluid Glass
UI." Rather than generic frosted-glass panels, the design commits to a
**water** identity specifically:

- **Palette**: a near-black deep-ocean base (`#030B14`) in dark mode,
  paired with an electric aqua accent (`#17D3FF`) and secondary teal
  (`#0BA5A0`) — not a generic blue, a *water* blue.
- **Typography**: Space Grotesk for display text (geometric, slightly
  technical — fits a data-driven health app), Inter for body/UI text,
  JetBrains Mono for every numeric readout (ml counts, percentages,
  streaks) so data feels instrumented rather than decorative.
- **The Aqua Orb**: the single most important visual decision in this
  project. Instead of a generic circular progress ring (the default,
  expected choice for "show hydration progress"), the home screen's hero
  element is a physically-simulated liquid inside a glass sphere — two
  overlapping sine-wave surfaces animate independently to suggest real
  liquid motion, small bubbles rise continuously, and a radial specular
  highlight sits on top to sell the glass material. This is implemented
  identically (same math, same layered SVG structure) in both the
  standalone HTML prototype and the production `WaterOrb.tsx` React
  component, so what you see in the prototype is exactly what ships.

### 2.2 Why a deterministic calculator sits *underneath* the AI, not inside it

`hydration_calculator.py` computes the actual target-ml number using a
transparent formula (baseline ml/kg by activity level, then additive
adjustments for weather, exercise, and health factors). This is
deliberately **not** something the language model computes or guesses at.

The reasoning: if the AI model directly generated "your goal is 2,847ml,"
that number would silently drift every time you changed the model's
phrasing, fine-tuned on new data, or swapped the checkpoint. By keeping the
number-crunching in ordinary, unit-tested Python and having the AI layer
*explain and contextualize* that number in natural language, the goal stays
auditable and stable regardless of what happens to the language model. This
is the same reason production recommendation systems generally keep
business-critical arithmetic out of the LLM's hands — the model narrates,
it doesn't compute.

### 2.3 Why the domain guardrail is a separate, first-class module

The brief was explicit: *"The AI should answer ONLY water and hydration
related questions. No general chatbot functionality."* This is implemented
as `app/ai/guardrails/domain_classifier.py`, which runs **before** the
generator is ever invoked — an off-topic question never reaches the
language model at all, it gets a fixed, honest refusal. Two independent
signals (keyword screen + embedding-similarity against the corpus
centroid) both have to pass, so neither a bad keyword match nor a bad
embedding similarity alone can let something through. This is a heuristic,
not a trained classifier — the docstring in that file explains exactly how
to replace it with one once you have labeled off-topic examples.

---

## 3. System architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js)                      │
│   Dashboard · Analytics · Achievements · Profile · Admin Console │
└───────────────────────────────┬─────────────────────────────────┘
                                 │ REST (JWT bearer)
┌───────────────────────────────▼─────────────────────────────────┐
│                        BACKEND (FastAPI)                         │
│  ┌───────────┐ ┌────────────┐ ┌───────────┐ ┌─────────────────┐ │
│  │   auth    │ │ water_logs │ │ containers│ │  goals/weather  │ │
│  └───────────┘ └────────────┘ └───────────┘ └─────────────────┘ │
│  ┌────────────────────────────┐ ┌────────────────────────────┐  │
│  │      ai (chat/advice)      │ │   admin_training (upload)  │  │
│  └──────────────┬─────────────┘ └──────────────┬─────────────┘  │
└─────────────────┼───────────────────────────────┼───────────────┘
                   │                               │
      ┌────────────▼────────────┐     ┌────────────▼─────────────┐
      │   AI / RAG PIPELINE     │     │   INGESTION PIPELINE     │
      │ guardrail → retriever   │     │ loaders → chunker →      │
      │ → generator →           │◄────┤ embeddings → vector_store │
      │ explainability          │     │                          │
      └────────────┬────────────┘     └────────────┬─────────────┘
                   │                                │
      ┌────────────▼────────────────────────────────▼─────────────┐
      │      VECTOR STORE (FAISS embedded / Qdrant service)        │
      └──────────────────────────────────────────────────────────┘
                   │
      ┌────────────▼────────────┐        ┌──────────────────────┐
      │   PostgreSQL             │        │  Redis (cache, unwired│
      │  users · water_logs ·    │        │  yet — see roadmap)  │
      │  containers · goals ·    │        └──────────────────────┘
      │  ai_recommendations ·    │
      │  achievements ·          │
      │  knowledge_documents     │
      └──────────────────────────┘
```

Five moving parts, each independently swappable:
1. **Frontend** — presentation only, talks to the backend over REST.
2. **Backend API** — routing, auth, business logic, orchestrates everything below.
3. **Deterministic services** — hydration calculator, achievement engine, weather service. Plain Python, no AI, fully unit-testable.
4. **AI/RAG pipeline** — the custom model itself: ingestion, retrieval, generation, guardrail, explainability.
5. **Storage** — PostgreSQL for structured data, FAISS/Qdrant for vectors.

---

## 4. Feature-by-feature breakdown

### 4.1 Water logging (fully implemented)

Four logging methods, all converging on the same `WaterLog` model and
`POST /api/v1/water-logs` endpoint:
- **Preset glasses** (150–500ml) and **preset bottles** (500ml–2L) — seeded
  as global `Container` rows (`user_id IS NULL`) in `database/seed.sql`,
  surfaced as tappable chips in `QuickAddRow.tsx`.
- **Custom quantity** — direct ml entry, no container needed.
- **Custom containers** — user-created, named, colored, capacity-defined
  rows in the same `Container` table (`user_id` set to the owner).

### 4.2 Smart glass measurement (fully implemented)

`estimate_capacity_ml()` in `app/models/container.py` (mirrored in
`ContainerBuilderModal.tsx` for instant client-side preview) computes
volume from height, diameter, and one of four shape approximations:

| Shape | Formula | Rationale |
|---|---|---|
| Cylinder | `π·r²·h` | Standard glass/tumbler |
| Cone | `(1/3)·π·r²·h` | Tapered cups |
| Rounded | `π·r²·h·0.92` | Slight inward taper allowance vs. a perfect cylinder |
| Square | `d²·h` | Square/rectangular mugs, treating diameter as side length |

The 0.92 factor for "rounded" is a heuristic, not a measured constant —
documented as such in the code so it's clear it's an approximation, not
derived from real container data.

### 4.3 Computer vision (explicitly not built)

The brief marks this "optional future module." The `LogSource.VISION` enum
value exists in `water_log.py` so the data model already has a slot for it,
but no camera/CV code exists. This was a deliberate scoping decision, not
an oversight — see Section 8.

### 4.4 Daily dashboard (fully implemented)

`GET /water-logs/summary` returns consumed/goal/remaining/percentage/score
in one call; `GET /water-logs/weekly` returns the same shape for the last 7
days, powering `WeeklyChart.tsx`. Monthly/yearly are one router function
each away — not built, but the pattern to extend is documented inline in
`analytics/page.tsx`.

### 4.5 Smart AI recommendation engine (fully implemented, placeholder model)

This is the centerpiece — see Section 5 for the full walkthrough.

### 4.6 Profile (fully implemented)

Every field from the brief (age, gender, weight, height, country, city,
occupation, activity level, sleep hours, exercise frequency, walking,
medical conditions, pregnancy, breastfeeding, climate, diet, caffeine,
alcohol, smoking, goals) exists as a column on the `User` model and a field
in `ProfileUpdate` schema and the `/profile` page form. These feed directly
into `hydration_calculator.py` and into the AI's `user_context` dict passed
to the generator.

### 4.7 AI-calculated daily goal (fully implemented)

`POST /goals/recalculate` — takes live weather + today's exercise, runs
`calculate_daily_goal()`, stores a `Goal` row with a full breakdown
(`base_ml`, `weather_adjustment_ml`, `exercise_adjustment_ml`,
`health_adjustment_ml`, and a human-readable `reasoning` string built from
the same notes the function accumulates internally).

### 4.8 Notifications (not built)

Modeled as `RecommendationKind.REMINDER` in `ai_recommendation.py`, but no
scheduler/push mechanism exists. Wiring this in means: a Celery beat
schedule (dependency already listed as a roadmap item in
`requirements.txt`) that periodically calls the same `answer_question()`
function used by chat/daily-advice, with a reminder-specific prompt.

### 4.9 Health analytics (partially implemented)

Daily/weekly are real (Section 4.4). Streak/longest-streak/best-day/
worst-day: `AchievementContext.current_streak_days` exists as a field but
is hardcoded to `0` in `achievements.py` — computing it needs a "consecutive
days where consumed_ml ≥ goal_ml" query, intentionally left as a TODO
rather than a rushed implementation.

### 4.10 Achievements (partially implemented)

Total-volume badges (Ocean Level, 100L Club, 500L Club) are fully working —
`achievement_engine.py` checks lifetime totals against thresholds on every
`POST /achievements/evaluate` call. Streak-based badges (7 Day Streak,
Hydration Master, Aqua Legend) are wired into the same engine but will
never unlock until the streak-counting TODO above is resolved.

### 4.11 Custom AI knowledge base / RAG (fully implemented, see Section 5)

### 4.12 Security (partially implemented)

JWT auth with bcrypt password hashing: real (`core/security.py`). Role
management (`admin` / `user` / `researcher`) with `require_role()` guarding
the admin training endpoints: real. OAuth (Google): scaffolded config
fields only, no actual OAuth router — flagged as not built rather than left
ambiguous. Encrypted database: not configured (that's a Postgres-level
`pgcrypto`/disk-encryption decision made at deployment time, not something
an application-layer schema controls).

### 4.13 Extra features (not built)

Smart Watch Sync, Google Fit/Apple Health/Samsung Health Sync, Offline
Mode, Cloud Backup, Widgets, Voice Logging, QR sharing, Family Accounts,
Doctor Dashboard — all explicitly out of scope for this pass. Where a data
model slot already exists (e.g. `DailyHealthData.sync_source` for the
health-platform syncs), it's noted in Section 8.

---

## 5. The AI / RAG pipeline, in detail

This is the part of the codebase that makes "custom AI model" a real
architectural commitment rather than a marketing label.

### 5.1 Ingestion — building the knowledge base

Trigger: `POST /admin/documents` (admin/researcher role required) with a
file + metadata (title, source type, origin citation like "WHO Hydration
Guidelines 2023", optional dataset version tag).

```
upload → save to disk → KnowledgeDocument row (status=uploaded)
       → background task: ingest_document()
           → loaders.load_document()   # pdf/csv/json/markdown/txt → plain text
           → chunker.chunk_text()      # 800-char sliding window, 120-char overlap
           → embeddings.embed_texts()  # sentence-transformers, batched
           → vector_store.upsert()     # FAISS or Qdrant
           → DocumentChunk rows saved  # text + vector_id, for traceability
       → status=indexed
```

Runs as a FastAPI `BackgroundTask` so the upload request returns
immediately (202 Accepted); `GET /admin/documents` polls status for the
training-monitor view in the admin console.

### 5.2 Retrieval — finding relevant passages

`retriever.py` embeds the incoming question with the same model used at
ingestion time, then does a top-k cosine-similarity search
(`RETRIEVAL_TOP_K`, default 4) against whichever vector backend is active.
Both backends (`FaissVectorStore`, `QdrantVectorStore`) implement the exact
same three-method interface (`upsert` / `search` / `delete_by_document`),
so the retriever, ingestion pipeline, and everything downstream is entirely
unaware of which one is running.

### 5.3 Domain guardrail — deciding whether to answer at all

Covered in depth in Section 2.3. Runs *before* retrieval — an off-topic
question doesn't just get a bad answer suppressed after the fact, it never
triggers retrieval or generation in the first place, which also means it
never costs a model inference.

### 5.4 Generation — the custom model itself

`generator.py` resolves the model in this order:
1. `GENERATION_MODEL_PATH` — if this local directory exists, it's assumed
   to be your fine-tuned checkpoint and loaded directly.
2. `GENERATION_MODEL_FALLBACK` (`Qwen/Qwen2.5-0.5B-Instruct`) — a small
   open-weight instruct model used purely so the pipeline is runnable
   *today*, before any fine-tuning has happened. This is the one part of
   the stack that isn't literally "your model" yet — it's a stand-in with
   the exact same interface your fine-tuned checkpoint will have.

The prompt itself (`prompt_templates.py`) is a RAG-style template: system
instruction (hydration-only, cite context, admit uncertainty) + user
profile summary + numbered retrieved passages + the question. Nothing about
this template is hardcoded to the fallback model — it's a plain
instruction-following prompt any decent instruct model (including your
fine-tune) can use.

### 5.5 Explainability — making the answer auditable

`explainability.py` wraps the above into a single `AIAnswer` object:
- `text` — the actual answer.
- `confidence` — a heuristic blend of retrieval-relevance scores and
  domain-classifier confidence (explicitly documented as *not* a calibrated
  probability — a placeholder for a trained confidence head).
- `reasoning` — a plain-language sentence like *"Retrieved 3 passages...
  avg. relevance 0.87... grounded in the user's profile."*
- `sources` — every retrieved passage's document title + relevance score.

Every call to `/ai/chat` or `/ai/daily-advice` persists this full object
into `ai_recommendations` (including the JSON-serialized source list), so a
user's hydration advice history is a genuine audit trail, not a
disappearing chat log.

### 5.6 What training your own model actually involves

Documented in the README's "Training your own model" section, but in
short: the *retrieval half* of this pipeline works today, unconditionally,
regardless of what you do with the generator — upload real WHO/CDC PDFs and
research papers via the admin console right now and they'll be properly
chunked, embedded, and searchable. The *generation half* needs you to
fine-tune an open-weight base model on hydration-domain instruction data
(LoRA/QLoRA being the practical default) and point `GENERATION_MODEL_PATH`
at the result — no other code changes required.

---

## 6. Database schema walkthrough

All tables live in `database/schema.sql`, mirroring
`backend/app/models/*.py` exactly (SQLAlchemy is the source of truth; the
raw SQL is a fast-path/reference, not a second independent schema).

| Table | Purpose | Notable design choice |
|---|---|---|
| `users` | Auth + the entire personalization profile (30+ fields from the brief) | One wide table rather than a separate `profiles` table — simpler joins, acceptable since profile fields are 1:1 with the user and rarely queried independently |
| `containers` | Presets (`user_id IS NULL`) and custom containers, unified | Smart-glass fields (`shape`, `height_cm`, `diameter_cm`, `is_estimated`) live on the same table rather than a separate one, since a container is either measured or not — no need for a join |
| `water_logs` | Every intake event | `CHECK (amount_ml > 0 AND amount_ml <= 5000)` — a sanity ceiling on any single log entry, prevents obviously bad data (e.g. accidental unit errors) at the DB layer, not just in Pydantic |
| `goals` | Daily targets with full adjustment breakdown | Stores `base_ml`/`weather_adjustment_ml`/`exercise_adjustment_ml`/`health_adjustment_ml` as separate columns, not just the total — so the "why is my goal 2,847ml today" question is always answerable from stored data, not recomputed |
| `ai_recommendations` | Every AI output, ever | `retrieved_sources` as `JSONB` rather than a normalized join table — sources are a snapshot at generation time (relevance scores from that specific retrieval), not a live relationship to `knowledge_documents` that would drift if a source is later deleted |
| `achievements` / `user_achievements` | Catalog + unlock join table | Standard catalog/join pattern; `UNIQUE(user_id, achievement_id)` prevents duplicate unlocks |
| `weather_snapshots` | Cached weather reads | Cached rather than fetched live on every request — `weather_service.py` enforces a 30-minute TTL before hitting Open-Meteo again |
| `daily_health_data` | Exercise/sleep/steps, manual or synced | `sync_source` column anticipates Apple Health/Google Fit/Samsung Health integration without needing a schema change when that's built |
| `knowledge_documents` / `document_chunks` | The RAG corpus | Chunks store the raw `text` redundantly (not just a pointer into the vector store) so the DB alone — without touching FAISS/Qdrant — is enough to inspect or re-index the corpus |

---

## 7. Two end-to-end data flows

### 7.1 "I just drank a glass of water"

```
User taps "250ml" chip (QuickAddRow.tsx)
  → POST /api/v1/water-logs {amount_ml: 250}
  → water_logs.py: WaterLog row inserted, user_id from JWT
  → (client-side) local state optimistically updates the Aqua Orb fill %
  → next dashboard load: GET /water-logs/summary recomputes
    consumed/remaining/percentage from the DB, replacing the optimistic guess
```

No AI involved in this path at all — logging is pure CRUD, deliberately
fast and simple.

### 7.2 "Should I drink more water right now?"

```
Dashboard loads → GET /ai/daily-advice
  → ai.py builds a fixed prompt + user_context dict from the JWT'd user's profile
  → explainability.answer_question()
      → domain_classifier.is_in_domain()  — always true for this fixed prompt
      → retriever.retrieve()              — top-4 passages from the vector store
      → generator.generate_answer()       — local model, RAG-prompted
      → AIAnswer assembled with confidence + sources + reasoning
  → AIRecommendation row persisted (kind=daily_advice)
  → AIAnswer returned to AIAdvicePanel.tsx, rendered with confidence pill + source chips
```

The free-form chat path (`POST /ai/chat`) is identical except the prompt is
the user's actual typed question, and the guardrail check can actually
reject it (see the refusal message in `explainability.py`).

---

## 8. Explicit scope boundaries (what's real vs. modeled vs. absent)

This section exists so nothing in this codebase is ambiguous about its
status — every feature from the original brief falls into exactly one of
three buckets:

**Real** — implemented end-to-end, API + DB + UI, and exercised by at least
one test or manual API call during development: water logging, all four
logging methods, smart glass measurement, daily/weekly dashboards, the full
RAG pipeline, the domain guardrail, the hydration calculator, JWT auth with
roles, the admin training console, weather-based goal adjustment,
total-volume achievements.

**Modeled but not implemented** — a database column, enum value, or config
field exists specifically so adding the feature later doesn't require a
schema migration, but no business logic or UI exists yet: computer vision
(`LogSource.VISION`), health-platform sync (`DailyHealthData.sync_source`),
Google OAuth (`OAUTH_GOOGLE_CLIENT_ID/SECRET`), reminders
(`RecommendationKind.REMINDER`), streak-based achievements
(`current_streak_days` hardcoded to 0).

**Absent** — no schema slot, no code, not started: family accounts, doctor
dashboard, voice logging, QR sharing, offline mode, cloud backup, widgets.

This three-tier distinction matters more than a flat "done/not done" list
because it tells you, for any given feature, whether you're starting from
zero or building on top of an already-considered data shape.

---

## 9. Repository reference

```
aqua-ai/
├── README.md                    Setup commands, quick start, tech stack
├── PREREQUISITES.md             System-level requirements (this doc covers architecture, not setup)
├── docker-compose.yml           postgres + redis + qdrant + backend + frontend
├── .github/workflows/ci.yml     Lint → test → docker build, on every push
│
├── prototype/
│   └── aqua_ai_prototype.html   Standalone, dependency-free UI mock — open directly in a browser
│
├── database/
│   ├── schema.sql                Full DDL, mirrors backend/app/models/
│   └── seed.sql                  Container presets + achievement catalog
│
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── tests/
│   │   └── test_hydration_calculator.py
│   └── app/
│       ├── main.py                        FastAPI app, router wiring
│       ├── core/
│       │   ├── config.py                  All settings, env-overridable
│       │   └── security.py                JWT + bcrypt
│       ├── db/
│       │   ├── base.py                    SQLAlchemy declarative base
│       │   └── session.py                 Async engine + session dependency
│       ├── models/                        One file per table (Section 6)
│       ├── schemas/                       Pydantic request/response shapes
│       ├── api/
│       │   ├── deps.py                    get_current_user, require_role
│       │   └── routers/                   One file per feature area (Section 3)
│       ├── services/
│       │   ├── hydration_calculator.py    Deterministic goal formula (Section 2.2)
│       │   ├── achievement_engine.py      Unlock-criteria checks
│       │   └── weather_service.py         Open-Meteo + Postgres cache
│       └── ai/                            The RAG pipeline (Section 5)
│           ├── explainability.py
│           ├── guardrails/domain_classifier.py
│           ├── retrieval/{embeddings,vector_store,retriever}.py
│           ├── generation/{generator,prompt_templates}.py
│           └── ingestion/{loaders,chunker,pipeline}.py
│
└── frontend/
    ├── package.json, tsconfig.json, tailwind.config.ts, next.config.js
    ├── .env.local.example
    ├── Dockerfile
    └── src/
        ├── app/
        │   ├── layout.tsx, globals.css        Fonts, theme tokens
        │   ├── page.tsx                        Home dashboard
        │   ├── analytics/page.tsx
        │   ├── achievements/page.tsx
        │   ├── profile/page.tsx
        │   └── admin/page.tsx                  Training console UI
        ├── components/
        │   ├── gauge/WaterOrb.tsx               The signature liquid gauge
        │   ├── logging/{QuickAddRow,ContainerBuilderModal}.tsx
        │   ├── ai/AIAdvicePanel.tsx
        │   ├── analytics/WeeklyChart.tsx
        │   └── layout/{BlobField,Dock}.tsx
        ├── lib/api.ts                           Typed fetch client
        └── types/index.ts                       Shared TS interfaces
```

---

## 10. API reference (summary)

All routes are prefixed `/api/v1`. Full interactive docs (with request/
response schemas) are auto-generated by FastAPI at `/docs` once the backend
is running.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | — | Create account |
| POST | `/auth/login` | — | Get JWT |
| GET / PATCH | `/users/me` | user | Read/update profile |
| POST | `/water-logs` | user | Log water |
| GET | `/water-logs/today` \| `/summary` \| `/weekly` | user | Dashboard data |
| GET / POST | `/containers` | user | List presets + custom, create new |
| POST | `/goals/recalculate` | user | Recompute today's goal from weather + exercise |
| POST | `/ai/chat` | user | Ask the hydration coach anything |
| GET | `/ai/daily-advice` | user | Proactive personalized advice |
| GET | `/achievements` | user | List with unlock status |
| POST | `/achievements/evaluate` | user | Re-check unlock criteria |
| GET | `/weather/current` | user | Current conditions for the user's location |
| POST / GET / DELETE | `/admin/documents` | admin/researcher | Upload, list, remove knowledge-base sources |

---

## 11. Closing note on scope

This documentation, the README, and the codebase all agree on the same
honest framing: this is a **complete, coherent starting architecture**, not
a finished consumer product. Every "Real" item in Section 8 works the way
a production feature should — typed, tested where it matters most (the
hydration math), and traceable (the AI layer especially). Every "Modeled"
and "Absent" item was a deliberate scoping call given the size of the
original brief, not a corner cut silently. Building outward from here means
picking the next feature from Section 8's Modeled list — the schema
already expects it.
