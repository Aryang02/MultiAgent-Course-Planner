#!/bin/bash

echo "Entrypoint script executed"

exec uvicorn src.core.api:app --host "0.0.0.0" --port 8000 --reload