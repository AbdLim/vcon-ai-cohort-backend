# Product Architecture: Backend System

## 1. Architecture Overview
The backend system acts as the core orchestration and analysis engine for the AI-Powered Cohort Intelligence Platform. It handles the ingestion of real-time meeting audio, converts it into the vCon standard, streams it through AI analysis pipelines, and serves structured intelligence to the frontend via a RESTful API.

## 2. Language and Framework Decision
**Decision: Python with FastAPI**
After evaluating the options between Python (FastAPI) and Node.js/TypeScript (Express), **Python + FastAPI** is the definitive choice for this project.

**Rationale:**
1. **AI/ML Ecosystem:** The core value of this product relies entirely on transcription, sentiment analysis, topic clustering, and NLP. Python has native support for open-source AI tools (OpenAI SDK, LangChain, PyTorch, Whisper), making AI orchestration seamless.
2. **Library Support:** The official Python `vcon` library (`vcon-dev/vcon`) is highly robust, mature, and actively maintained by the IETF working group for constructing, signing, and analyzing vCon objects.
3. **Async Performance:** FastAPI's asynchronous architecture is perfect for IO-bound tasks like downloading meeting recordings, streaming audio, and calling external LLM APIs concurrently.
4. **Data Science Flow:** Transitioning from data exploration (AI training needs as specified in the MVP) to production is much faster in Python.

## 3. Core Technologies & Libraries

### Core Frameworks
* **Web Framework:** `fastapi` (High performance, async-native REST API)
* **Web Server:** `uvicorn` (ASGI server for FastAPI)

### Conversation Standard (vCon)
* **vCon Library:** `vcon` (The official Python implementation for creating, managing, and parsing vCon objects).

### AI & Analysis
* **Transcription/LLM:** `openai` (For Whisper transcription and GPT-4 based summaries, action item extraction, and sentiment NLP tasks).
* **Prompt Orchestration:** `langchain` or `instructor` (For structuring LLM outputs natively into JSON to append to the vCon analysis tags).

### Background Processing & Ingestion
* **Task Queues:** `celery` + `redis` (Essential for long-running tasks like processing 60-minute meeting recordings, speaker diarization, and running multiple AI inference pipelines without blocking the API).
* **File Upload Handling:** FastAPI `UploadFile` (For handling direct audio/video `.mp4`/`.mp3` multipart uploads from users).

### Data Persistence
* **Database ORM:** `sqlalchemy` + `psycopg2-binary` (PostgreSQL for relational data — users, cohorts, sessions).
* **vCon Storage:** Cloudinary. vCons can become large with attached audio; they should be stored as JSON/binary blobs in object storage (Cloudinary), while metadata is indexed in PostgreSQL or a vector DB (e.g., Pinecone/Milvus) for search.

## 4. System Components & Flow

1. **Ingestion Service (File Upload API):** 
   - Receives `.mp4` or `.mp3` files via frontend multipart upload.
   - Saves raw audio/video to temporary storage or Cloudinary.
   - Triggers the async transcription worker upon successful upload.
2. **vCon Constructor (The Factory):** 
   - Takes raw transcripts and metadata.
   - Initializes a baseline `vCon` object using the `vcon` Python library.
3. **Intelligence Pipeline (Celery Workers):** 
   - Takes the baseline vCon and runs it through AI workers.
   - Worker 1: Diarization & Speaker ID.
   - Worker 2: Semantic Analysis (Summary, Topic Clustering).
   - Worker 3: Cohort Health Scoring.
   - Appends all results as extensions to the vCon object and saves it to Cloudinary.
4. **API Layer (FastAPI):** 
   - Serves the Dashboard frontend.
   - Endpoints for `/cohorts/{id}/health`, `/sessions/{id}/intelligence`, `/participants/{id}/engagement`.
