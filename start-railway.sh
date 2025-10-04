#!/bin/bash
# Railway startup script that properly handles the PORT environment variable

# Force port 8080 for Railway (Railway's default internal port)
export PORT=8080

echo "========================================="
echo "Starting AI Nurse Florence"
echo "PORT: ${PORT}"
echo "Binding to: 0.0.0.0:${PORT}"
echo "========================================="

# Check if drug database exists, build if missing
DB_PATH="/app/ai_nurse_florence.db"
if [ ! -f "$DB_PATH" ]; then
    echo "========================================="
    echo "Drug database not found at $DB_PATH"
    echo "Building database from FDA data..."
    echo "This is a one-time setup (unless volume is cleared)"
    echo "========================================="
    python3 scripts/build_drug_database.py --max-records 25000 || echo "Warning: Drug database build failed, will use FDA API fallback"
else
    echo "========================================="
    echo "Drug database found at $DB_PATH"
    echo "Skipping rebuild (use cron job to update monthly)"
    echo "========================================="
fi

# Start the application with the resolved port
exec gunicorn -k uvicorn.workers.UvicornWorker --workers 4 --bind "0.0.0.0:8080" --timeout 120 app:app
