#!/bin/bash
# Railway startup script to handle PORT environment variable properly

# Default to port 8000 if PORT is not set
PORT=${PORT:-8000}

echo "Starting AI Nurse Florence on port $PORT"

# Start the FastAPI application
exec uvicorn app:app --host 0.0.0.0 --port $PORT
