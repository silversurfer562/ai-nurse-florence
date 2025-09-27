#!/usr/bin/env bash
set -euo pipefail
PORT=${PORT:-8088}
HOST=${HOST:-0.0.0.0}
# Compute effective base URL for logs
if [ -n "${APP_BASE_URL:-}" ]; then
	BASE_URL="$APP_BASE_URL"
else
	if [ "${FORCE_HTTPS:-false}" = "true" ]; then
		SCHEME="https"
	else
		SCHEME="http"
	fi
	BASE_URL="$SCHEME://$HOST:$PORT"
fi

echo "Starting AI Nurse Florence on $BASE_URL"
exec uvicorn app:app --host "$HOST" --port "$PORT"
