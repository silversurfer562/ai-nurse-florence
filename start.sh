#!/bin/bash
# Railway startup script to handle PORT environment variable properly

# Default to port 8000 if PORT is not set
PORT=${PORT:-8000}

echo "Starting AI Nurse Florence on port $PORT"

# Determine effective base URL for logging
if [ -n "${APP_BASE_URL:-}" ]; then
	BASE_URL="$APP_BASE_URL"
else
	if [ "${FORCE_HTTPS:-false}" = "true" ]; then
		SCHEME="https"
	else
		SCHEME="http"
	fi
	HOST_FOR_URL=${HOST:-0.0.0.0}
	BASE_URL="$SCHEME://$HOST_FOR_URL:$PORT"
fi
echo "Effective BASE_URL: $BASE_URL"

# Start the FastAPI application
exec uvicorn app:app --host 0.0.0.0 --port $PORT
