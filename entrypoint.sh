#!/bin/bash
set -euo pipefail

echo "Running database migrations..."
alembic upgrade head

echo "Starting API server..."
exec uvicorn src.core.api:app --host 0.0.0.0 --port 8000 --reload
