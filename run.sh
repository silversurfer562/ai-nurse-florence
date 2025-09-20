#!/usr/bin/env bash
set -euo pipefail
PORT=${PORT:-8088}
HOST=${HOST:-0.0.0.0}
exec uvicorn app:app --host "$HOST" --port "$PORT"
