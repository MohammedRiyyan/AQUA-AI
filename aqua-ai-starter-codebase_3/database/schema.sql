-- =====================================================================
-- Aqua AI — PostgreSQL schema
-- Mirrors backend/app/models/*.py. Prefer Alembic migrations
-- (backend/alembic/) for real deployments — this file is a readable,
-- versioned reference and a fast way to stand up a fresh dev database:
--   psql -U aqua -d aqua_ai -f database/schema.sql
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------- enums ----------
CREATE TYPE user_role AS ENUM ('admin', 'user', 'researcher');
CREATE TYPE activity_level AS ENUM ('sedentary', 'light', 'moderate', 'active', 'athlete');
CREATE TYPE container_shape AS ENUM ('cylinder', 'cone', 'rounded', 'square');
CREATE TYPE log_source AS ENUM ('manual', 'quick_add', 'voice', 'vision', 'health_sync');
CREATE TYPE recommendation_kind AS ENUM ('daily_advice', 'reminder', 'chat_answer', 'goal_adjustment');
CREATE TYPE document_status AS ENUM ('uploaded', 'chunking', 'embedding', 'indexed', 'failed');

-- ---------- users ----------
CREATE TABLE users (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email                       VARCHAR(255) UNIQUE NOT NULL,
    hashed_password             VARCHAR(255) NOT NULL,
    role                        user_role NOT NULL DEFAULT 'user',

    name                        VARCHAR(120),
    age                         INTEGER,
    gender                      VARCHAR(30),
    weight_kg                   FLOAT,
    height_cm                   FLOAT,
    country                     VARCHAR(80),
    city                        VARCHAR(80),
    occupation                  VARCHAR(120),
    activity_level              activity_level,
    sleep_hours                 FLOAT,
    exercise_frequency_per_week INTEGER,
    daily_walking_minutes       INTEGER,
    medical_conditions          VARCHAR(500),
    pregnant                    BOOLEAN NOT NULL DEFAULT false,
    breastfeeding               BOOLEAN NOT NULL DEFAULT false,
    climate                     VARCHAR(50),
    diet                        VARCHAR(80),
    caffeine_cups_per_day       INTEGER,
    alcohol_units_per_week      INTEGER,
    smoker                      BOOLEAN NOT NULL DEFAULT false,
    primary_goal                VARCHAR(50),

    is_active                   BOOLEAN NOT NULL DEFAULT true,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------- containers ----------
CREATE TABLE containers (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID REFERENCES users(id) ON DELETE CASCADE,  -- NULL = global preset
    name          VARCHAR(80) NOT NULL,
    capacity_ml   FLOAT NOT NULL,
    icon          VARCHAR(50),
    color         VARCHAR(20),
    shape         container_shape,
    height_cm     FLOAT,
    diameter_cm   FLOAT,
    is_estimated  BOOLEAN NOT NULL DEFAULT false,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_containers_user ON containers(user_id);

-- ---------- water_logs ----------
CREATE TABLE water_logs (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    container_id  UUID REFERENCES containers(id),
    amount_ml     FLOAT NOT NULL CHECK (amount_ml > 0 AND amount_ml <= 5000),
    source        log_source NOT NULL DEFAULT 'manual',
    note          VARCHAR(200),
    logged_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_water_logs_user ON water_logs(user_id);
CREATE INDEX idx_water_logs_logged_at ON water_logs(logged_at);
CREATE INDEX idx_water_logs_user_logged_at ON water_logs(user_id, logged_at);

-- ---------- goals ----------
CREATE TABLE goals (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_date              DATE NOT NULL,
    target_ml                FLOAT NOT NULL,
    base_ml                  FLOAT NOT NULL,
    weather_adjustment_ml    FLOAT NOT NULL DEFAULT 0,
    exercise_adjustment_ml   FLOAT NOT NULL DEFAULT 0,
    health_adjustment_ml     FLOAT NOT NULL DEFAULT 0,
    reasoning                VARCHAR(500),
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_goals_user_date ON goals(user_id, target_date);

-- ---------- ai_recommendations ----------
CREATE TABLE ai_recommendations (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id            UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind               recommendation_kind NOT NULL,
    prompt             TEXT,
    output_text        TEXT NOT NULL,
    confidence         FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    reasoning          TEXT,
    retrieved_sources  JSONB NOT NULL DEFAULT '[]',
    model_version      VARCHAR(80),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_ai_recs_user ON ai_recommendations(user_id);

-- ---------- achievements ----------
CREATE TABLE achievements (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key          VARCHAR(60) UNIQUE NOT NULL,
    name         VARCHAR(120) NOT NULL,
    description  VARCHAR(300) NOT NULL,
    icon         VARCHAR(50),
    criteria     VARCHAR(300)
);

CREATE TABLE user_achievements (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id  UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, achievement_id)
);

-- ---------- weather_snapshots ----------
CREATE TABLE weather_snapshots (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    city           VARCHAR(80) NOT NULL,
    country        VARCHAR(80),
    temperature_c  FLOAT NOT NULL,
    humidity_pct   FLOAT,
    altitude_m     FLOAT,
    fetched_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_weather_city_fetched ON weather_snapshots(city, fetched_at DESC);

-- ---------- daily_health_data ----------
CREATE TABLE daily_health_data (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id            UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_date         DATE NOT NULL,
    exercise_minutes   INTEGER,
    exercise_intensity VARCHAR(20),
    steps              INTEGER,
    calories_burned    FLOAT,
    sleep_hours        FLOAT,
    sync_source        VARCHAR(40),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, entry_date, sync_source)
);

-- ---------- knowledge base (RAG) ----------
CREATE TABLE knowledge_documents (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title            VARCHAR(300) NOT NULL,
    source_type      VARCHAR(40) NOT NULL,
    origin           VARCHAR(300),
    file_path        VARCHAR(500) NOT NULL,
    status           document_status NOT NULL DEFAULT 'uploaded',
    dataset_version  VARCHAR(30),
    uploaded_by      UUID REFERENCES users(id),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE document_chunks (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id   UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_index   INTEGER NOT NULL,
    text          TEXT NOT NULL,
    vector_id     VARCHAR(80)
);
CREATE INDEX idx_chunks_document ON document_chunks(document_id);
