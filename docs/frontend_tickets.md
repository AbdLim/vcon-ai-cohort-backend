# Frontend Engineering Tickets

This document outlines the Phase 1 (MVP) implementation tickets for the frontend developer. The frontend will be a single-page or SSR application (e.g., Next.js or React/Vite) that consumes the Cohort Intelligence API.

## Epic 1: Project Setup & Foundation

### [FE-01] Initialize Project & Design System
* **Description:** Set up the base repository, routing, and design system.
* **Tasks:**
  * Initialize project (Next.js/React).
  * Set up Tailwind CSS or preferred styling framework.
  * Create base UI components (Buttons, Cards, Modals, Tables, Charts).
  * Configure API fetching library (e.g., Axios + React Query or SWR) with a base URL pointing to the FastAPI backend.

### [FE-02] Build Navigation & Layout Shell
* **Description:** Implement the main application shell.
* **Tasks:**
  * Implement Sidebar/Top navbar.
  * Define routing structure: `/dashboard`, `/cohorts/[id]`, `/sessions/[id]`, `/participants/[id]`.

## Epic 2: Core Dashboard Views

### [FE-03] Implement Global Dashboard Overview
* **Description:** Build the landing page showing active cohorts and global metrics.
* **API Integration:**
  * Endpoint: `GET /api/dashboard/overview`
  * Expected Response: `{ active_cohorts: [], upcoming_sessions: [], engagement_trend: [...] }`
* **Tasks:**
  * Render summary KPI cards.
  * Render list/table of active cohorts.
  * **Hackathon MVP:** Build an "Upload Recording" button and modal to send `multipart/form-data` files to `POST /api/sessions/upload`.
  * **Hackathon MVP:** Build "Import from URL" support in the same modal, sending a JSON payload `{title, cohort_id, url}` to `POST /api/sessions/url`.

### [FE-04] Implement Cohort Detail View
* **Description:** Display specific cohort health and a list of its sessions.
* **API Integration:**
  * Endpoint: `GET /api/cohorts/{cohort_id}`
  * Expected Response: `{ cohort_info: {...}, sessions: [...], health_score: 85 }`
* **Tasks:**
  * Create timeline view of past and upcoming sessions.
  * Render a high-level engagement gauge/chart.

## Epic 3: Session & Participant Intelligence

### [FE-05] Implement Session Intelligence View
* **Description:** The most complex view. Shows the AI analysis of a specific meeting.
* **API Integration:**
  * Endpoint: `GET /api/sessions/{session_id}`
  * Expected Response: `{ metadata: {...}, summary: "...", transcript: [...], action_items: [...] }`
* **Tasks:**
  * Render session metadata (duration, attendees).
  * Display the AI-generated executive summary.
  * Build a scrollable transcript component with speaker attribution.
  * Render extracted action items/questions in a checklist format.

### [FE-06] Implement Participant View (Learner Profile)
* **Description:** Show engagement metrics for a specific individual across the cohort.
* **API Integration:**
  * Endpoint: `GET /api/participants/{participant_id}`
  * Expected Response: `{ user_info: {...}, engagement_score: 92, speaking_time_ratio: 0.15, risk_level: "low" }`
* **Tasks:**
  * Display participant profile and risk level indicator.
  * Render charts showing speaking patterns vs listening time.
  * List recommended actions (e.g., "Follow up, participant has been silent for 2 sessions").
