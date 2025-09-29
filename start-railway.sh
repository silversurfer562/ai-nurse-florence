#!/bin/bash
# Railway startup script that properly handles the PORT environment variable

# Use Railway's PORT if available, otherwise default to 8000
PORT=${PORT:-8000}

echo "Starting AI Nurse Florence on port $PORT"

# Start the application with the resolved port
exec gunicorn -k uvicorn.workers.UvicornWorker --workers 4 --bind "0.0.0.0:$PORT" app:app
