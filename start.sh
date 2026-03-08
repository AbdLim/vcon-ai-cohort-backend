#! /usr/bin/env bash
set -e

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the celery worker in background (add the & in the end to keep this running in the background)
echo "Starting celery worker..."
celery -A app.worker.celery_app worker --loglevel=info &

# Start application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
