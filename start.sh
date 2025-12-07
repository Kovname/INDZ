#!/bin/sh
# Start script for the application
# Handles PORT environment variable properly

PORT="${PORT:-8000}"
echo "Starting application on port $PORT..."
exec python -m uvicorn src.main:app --host 0.0.0.0 --port "$PORT"
