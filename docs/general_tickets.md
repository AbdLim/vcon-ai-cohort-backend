# Project Management: AI Cohort Intelligence Platform

This document serves as the high-level Epic and Ticket tracker for the Project Manager. It links the backend (BE) and frontend (FE) efforts and highlights dependencies.

## Phase 1 (MVP) Overall Goal
Deliver a working end-to-end system where a Zoom/Meet audio recording can be ingested into the backend, processed into a vCon object using AI (summaries, transcription), and displayed on a web dashboard for the cohort coach.

---

## Epic 1: Foundation & Setup
**Goal:** Both teams establish their base repositories, boilerplate, and database/routing structures.
*   [ ] **[PM-01]** BE: Initialize FastAPI, PostgreSQL, and Celery setup (`BE-01`, `BE-02`).
*   [ ] **[PM-02]** FE: Initialize Next.js/React app, routing, and design system shell (`FE-01`, `FE-02`).
*   **Dependency:** None. Both can happen in parallel.

## Epic 2: Data Ingestion & Storage Pipeline (Backend Heavy)
**Goal:** The backend is capable of receiving meeting data and saving it in the vCon standard format.
*   [ ] **[PM-03]** BE: Implement `POST /api/sessions/upload` multipart endpoint (`BE-03`).
*   [ ] **[PM-04]** BE: Implement the vCon serialization module using the python `vcon` library (`BE-04`).
*   **Dependency:** BE only. FE can begin mocking API responses for Epic 3 based on the JSON contract.

## Epic 3: AI Intelligence Pipeline (Backend Heavy)
**Goal:** The backend processes the raw meeting data into transcripts and actionable insights using Whisper and GPT-4.
*   [ ] **[PM-05]** BE: Implement Celery worker for audio transcription and diarization (`BE-05`).
*   [ ] **[PM-06]** BE: Implement Celery worker for LLM analysis (summary, action items, engagement scoring) (`BE-06`).
*   **Dependency:** BE only. Requires Epic 2 to be completed to test the full pipeline.

## Epic 4: Dashboard API & UI Integration (Collaborative)
**Goal:** Connect the backend intelligence to the frontend UI so users can view cohort and session data.
*   [ ] **[PM-07]** BE: Build `GET` endpoints for `/dashboard/overview` and `/cohorts/{id}` (`BE-07`).
*   [ ] **[PM-08]** FE: Implement Global Dashboard and Cohort views consuming the BE endpoints (`FE-03`, `FE-04`).
*   [ ] **[PM-09]** BE: Build `GET` endpoints for `/sessions/{id}` and `/participants/{id}` (`BE-08`).
*   [ ] **[PM-10]** FE: Implement Session details (transcripts, summaries) and Participant views (`FE-05`, `FE-06`).
*   **Dependency:** FE requires BE endpoints to be live (or strictly mocked) to complete integration. Postman/Swagger docs from FastAPI should be shared with FE.

---

## Technical Risk & Blocker Tracking
1.  **Audio/Video File Sizes:** Uploading 60-minute files (500MB+) from the frontend requires robust handling. For the MVP, increase FastAPI's upload limits, or consider a direct-to-S3 presigned URL approach if timeout becomes an issue. (Owner: Backend/Frontend)
2.  **Speaker Diarization Accuracy:** Since we only receive a single mixed audio file instead of isolated tracks, diarization via Whisper and PyAnnote might group speakers imperfectly. Prompting GPT-4 to correct transcripts using context is key. (Owner: Backend/AI)
3.  **API Latency:** Dashboard load times might be slow if the FE fetches massive vCon JSON objects. The BE must aggregate data into PostgreSQL and only send necessary data to the FE. (Owner: Frontend/Backend)
4.  **Hackathon Demo Preparation:** Prepare a pre-processed "Golden Demo" vCon object in the database to guarantee a perfect dashboard showing during the pitch, while demonstrating a live 1-minute upload in the background to prove the tech works. (Owner: PM)
