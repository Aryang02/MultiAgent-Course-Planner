#!/bin/bash
set -euo pipefail

echo "Starting API server..."
exec uvicorn src.core.api:app --host 0.0.0.0 --port 8000 --reload
