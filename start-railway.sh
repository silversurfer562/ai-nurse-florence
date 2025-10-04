#!/bin/bash
# Railway startup script that properly handles the PORT environment variable

# Force port 8080 for Railway (Railway's default internal port)
export PORT=8080

echo "========================================="
echo "Starting AI Nurse Florence"
echo "PORT: ${PORT}"
echo "Binding to: 0.0.0.0:${PORT}"
echo "========================================="

# Start the application with the resolved port
exec gunicorn -k uvicorn.workers.UvicornWorker --workers 4 --bind "0.0.0.0:8080" --timeout 120 app:app
