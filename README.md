# FastAPI Project Template

A production-ready, async-first FastAPI project template with SQLAlchemy (PostgreSQL), Redis, and Docker.

This template isn't just a collection of libraries; it's an **opinionated implementation** of how modern Python microservices should be built to balance simplicity with scalability.

## Architectural Philosophy

Here is the reasoning behind every major architectural decision in this repository.

### 1. Flattened Layout (`app/` at root)
You will notice there is no `src/` folder. The application lives in `app/` at the root.
-   **Why**: For most FastAPI microservices, the "src layout" adds unnecessary nesting. Having `app` at the root is cleaner, simplifies Docker paths, and reduces import complexity (`app.main` vs `src.app.main`).
-   **Trade-off**: Requires careful `pyproject.toml` configuration to ensure tests run correctly (handled via `pythonpath = ["."]`).

### 2. Vertical Slices over Horizontal Layers
Most tutorials teach "Layered Architecture" (controllers, models, services).
-   **The Problem**: To build a simple "Post a Comment" feature, you have to touch files in four different directories. You lose context switching between tabs.
-   **My Solution**: I group code by **Domain Feature** in `app/features/`.
    -   `app/features/auth/` contains the router, the model, the schema, and the service.
-   **Benefit**: All code related to a feature lives in one place. If you delete a feature, you delete one folder.

### 3. Explicit Infrastructure Layer (`app/infrastructure/`)
Business logic (`features/`) should never talk directly to external tools (Redis, Stripe, AWS).
-   **Why**: Vendors change. Libraries break.
-   **Rule**: Wrap external clients in `infrastructure/` and inject them into your services. This makes testing trivial because you can mock the wrapper.

### 4. Async All The Way Down
Python is single-threaded. If you block that thread (e.g., waiting for a database query), your API grinds to a halt.
-   **My Choice**: I refuse to use synchronous drivers in 2026.
    -   **DB**: `asyncpg` + `SQLAlchemy` (Async Session)
    -   **Cache**: `redis.asyncio`
    -   **Http**: `httpx` (Async Client)
This ensures the application can handle thousands of concurrent connections without blocking the event loop.

---

## Features

- **FastAPI**: Modern, fast (high-performance), web framework for building APIs.
- **Async SQLAlchemy**: Database ORM with async support.
- **PostgreSQL**: Robust open-source relational database.
- **Redis**: In-memory data structure store, used for caching and token revocation.
- **Authentication**: JWT-based access and refresh tokens, with revocation.
- **Docker**: Containerized environment for easy development and deployment.
- **UV**: Fast Python package manager.

## Project Structure

```
app/
  main.py           # Application entry point
  core/             # Global configuration and security
  db/               # Database session and base models
  features/         # Feature-based modules (e.g., auth)
  infrastructure/   # External services (Redis, Stripe, Firebase, etc.)
tests/              # Pytest suite
```

## Extending the Template

### Adding New Features
Create a new directory in `app/features/` (e.g., `app/features/posts`). Include `models.py`, `schemas.py`, `service.py`, and `router.py`.

### Infrastructure & Integrations
Place third-party integrations in `app/infrastructure/`.
- **Redis**: Already configured in `app/infrastructure/redis.py`.
- **Stripe/Firebase/Google Maps**: Create a new file (e.g., `app/infrastructure/stripe.py`) to handle client initialization and logic.

## Getting Started

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Docker & Docker Compose

### Local Development

1. **Clone the repository**
2. **Install dependencies**
   ```bash
   uv sync
   ```
3. **Environment Setup**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. **Run the application**
   ```bash
   uv run dev
   ```
   The API will be available at `http://localhost:8000`.
   Docs are at `http://localhost:8000/docs`.

### Running with Docker

```bash
docker-compose up --build
```

### Running Tests

Tests use an in-memory SQLite database and do not require running infrastructure.

```bash
uv run test
```

## Authentication Flow

1. **Signup**: `POST /api/v1/auth/signup`
2. **Login**: `POST /api/v1/auth/login` -> Returns Access & Refresh Tokens
3. **Access Protected Resources**: Use `Authorization: Bearer <access_token>`
4. **Refresh Token**: `POST /api/v1/auth/refresh` -> Returns new Access & Refresh Tokens (rotates refresh token)
5. **Logout**: `POST /api/v1/auth/logout` -> Revokes the Refresh Token in Redis
