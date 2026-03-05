# Backend Engineering Tickets

This document outlines the Phase 1 (MVP) implementation tickets for the backend developer. The backend will be built in **Python using FastAPI**, leveraging the **official `vcon` library**, Celery for asynchronous AI processing, and PostgreSQL for state management.

## Epic 1: Infrastructure & API Foundation

### [BE-01] Initialize FastAPI Project & Database
* **Description:** Set up the base repository, routing, and database connection.
* **Libraries:** `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, `alembic`.
* **Tasks:**
  * Initialize FastAPI app with CORS middleware.
  * Set up PostgreSQL connection and Alembic for migrations.
  * Define core SQLAlchemy models: `Organization`, `Cohort`, `Session`, `Participant`.

### [BE-02] Set up Celery & Redis for Background Tasks
* **Description:** Configure the async task queue for long-running AI inference and audio processing.
* **Libraries:** `celery`, `redis`.
* **Tasks:**
  * Spin up local Redis instance via Docker.
  * Configure Celery worker connected to the FastAPI app.
  * Create a dummy task to verify the worker is processing.

## Epic 2: Data Ingestion & vCon Creation

### [BE-03] Implement File Upload Endpoint
* **Description:** Create the endpoint to receive manual meeting audio/video uploads from the frontend.
* **Endpoint Spec:** 
  * `POST /api/sessions/upload`
  * Request Body: `multipart/form-data` with `file`, `cohort_id`, and `title`.
  * Response: `202 Accepted`, `{ "task_id": "...", "status": "processing" }`
* **Tasks:**
  * Handle large file uploads via FastAPI `UploadFile`.
  * Save file to disk/S3 and dispatch a Celery task to begin audio processing.

### [BE-04] Implement vCon Object Constructor
* **Description:** Build the module that converts raw meeting data into a standard vCon object.
* **Libraries:** `vcon` (official Python package).
* **Tasks:**
  * Create a Python service class that initializes a `Vcon` object.
  * Append session metadata (parties, datetime) to the vCon.
  * Save the base vCon JSON to AWS S3 / Cloud Storage.

## Epic 3: AI Intelligence Pipeline (Celery Workers)

### [BE-05] Audio Transcription & Diarization Task
* **Description:** Worker task to transcribe audio and identify speakers.
* **Libraries:** `openai` (Whisper API) or local PyTorch equivalent.
* **Tasks:**
  * Download audio from the provider URL.
  * Send to Whisper API for transcription with speaker diarization.
  * **vCon Action:** Append the transcript as a `dialog` object in the vCon.

### [BE-06] Semantic Analysis Task (LLM)
* **Description:** Worker task to generate summaries, action items, and engagement metrics via LLM.
* **Libraries:** `openai` (GPT-4o), `instructor` or `langchain` for structured JSON output.
* **Tasks:**
  * Pass the generated transcript to the LLM with a specific prompt.
  * Extract: Summary, Questions Asked, Action Items, Talk/Listen ratios.
  * **vCon Action:** Append these insights into the `analysis` array of the vCon.
  * Update the PostgreSQL database with the aggregated metrics for fast frontend querying.

## Epic 4: Data Serving API (Frontend Consumption)

### [BE-07] Dashboard & Cohort Endpoints
* **Description:** Serve data for the high-level frontend views.
* **Endpoints:**
  * `GET /api/dashboard/overview` -> Returns global active cohorts and latest processed sessions.
  * `GET /api/cohorts/{cohort_id}` -> Returns cohort metadata and list of associated sessions.

### [BE-08] Session & Participant Details Endpoints
* **Description:** Serve detailed AI insights for a specific session or learner.
* **Endpoints:**
  * `GET /api/sessions/{session_id}` -> Returns the stitched summary, transcript, and action items (read from DB/vCon object).
  * `GET /api/participants/{participant_id}` -> Returns aggregated profile metrics and health scores.
