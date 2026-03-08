# AI Cohort vCon Backend

A production-ready FastAPI microservice for managing cohorts, uploading session recordings, generating standard vCons (conversations), and performing AI-driven semantic analysis (summaries, action items, topics, key moments, etc.) using OpenAI's Whisper and GPT-4o.

## Overview

This project provides the backend infrastructure for analyzing conversational intelligence across different organizational cohorts. It leverages the global standard `vcon` format for deeply structured meeting data.

### Core Features

- **Organizations & Cohorts**: Multi-tenant architecture allowing sessions to be grouped into specific learning or development cohorts.
- **Session Processing**: Upload audio/video URLs directly. Background workers handle downloading, extracting audio, transcribing via Whisper, and generating a standard `.vcon.json` representation.
- **Semantic Analysis**: Automatically extracts actionable insights (Action Items, Key Topics, Summary, Talk/Listen Ratios, Questions Asked, Key Moments) using `instructor` and GPT-4o.
- **Background Workers**: Uses Celery and Redis to handle heavy processing (transcription, cloud fetching, semantic AI analysis) asynchronously.
- **Robust API**: Built on FastAPI with SQLAlchemy (sync over async for specific worker bounds) and connected to a PostgreSQL database.

## Architecture

We use a feature-slice architecture (vertical slices over horizontal layers) to keep domain logic tightly encapsulated.

```
app/
  core/             # Config, security, base settings
  db/               # Database setup and SQLAlchemy session handling
  features/         # Domain functionality
    ├── auth/       # JWT authentication and user roles
    ├── cohorts/    # Cohort management
    ├── dashboard/  # Aggregated analytics overview
    ├── users/      # User management
    ├── sessions/   # Session uploads and metadata
    └── participants/ # Meeting participants
  infrastructure/   # External client wrappers (Cloudinary, vCon Builder, AI)
  services/         # Helper services
  worker/           # Celery tasks (transcription, AI analysis)
```

## Getting Started

### Prerequisites

- [uv](https://github.com/astral-sh/uv)
- Docker & Docker Compose
- OpenAI API Key
- Cloudinary Credentials (for storing vCon JSONs and temporary media)

### Local Development

1. **Clone the repository**
2. **Setup environment**
   ```bash
   cp .env.example .env
   # Ensure you fill out the OPENAI_API_KEY and CLOUDINARY_* variables in .env
   ```
3. **Run local infrastructure (Postgres & Redis)**
   ```bash
   docker compose up -d postgres redis
   ```
4. **Apply Database Migrations**
   ```bash
   uv run alembic upgrade head
   ```
5. **Run the API (Terminal 1)**
   ```bash
   uv run dev
   ```
6. **Run the Celery Worker (Terminal 2)**
   ```bash
   uv run celery -A app.worker.celery_app worker -l info
   ```

### Running with Docker

You can spin up the entire stack (API, Postgres, Redis, and Celery Worker implicitly if added to compose) via Docker.

```bash
docker compose up --build
```

*(Note: Ensure `./migrations` is mounted in your compose file or run migrations within the container prior to full operation).*

## Background Processing Pipeline

When a session is uploaded via `POST /api/v1/sessions/upload-url`:
1. `process_session_task`: Saves the initial media to Cloudinary and builds the base `vcon`.
2. `generate_transcript_task`: Downloads media, converts via `ffmpeg`, transcribes using `whisper-1`, and appends the transcript to the vCon.
3. `generate_semantic_analysis_task`: Feeds the transcript to `gpt-4o` using `instructor`, extracts structured insights (including `key_moments`), appends them to the vCon, and updates the fast-access cached fields in the Postgres `sessions` table.
