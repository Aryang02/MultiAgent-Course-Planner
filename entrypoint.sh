#!/bin/bash
set -euo pipefail

echo "Running database migrations..."
alembic upgrade head

if [ "${API_SERVER:-gunicorn}" = "uvicorn" ]; then
  echo "Starting API server (uvicorn dev mode)..."
  exec uvicorn src.core.api:app --host 0.0.0.0 --port 8000 --reload
fi

echo "Starting API server (gunicorn)..."
exec gunicorn src.core.api:app -c gunicorn.conf.py
