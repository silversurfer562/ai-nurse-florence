#!/bin/bash
# Railway startup script that properly handles the PORT environment variable

# Force port 8080 for Railway (Railway's default internal port)
export PORT=8080

echo "========================================="
echo "Starting AI Nurse Florence"
echo "PORT: ${PORT}"
echo "Binding to: 0.0.0.0:${PORT}"
echo "========================================="

# Create necessary data directories
mkdir -p /app/data/generated_documents
echo "Created /app/data/generated_documents for PDF storage"

# Check if drug database exists, build if missing or outdated
DB_PATH="/app/data/drugs.db"
DB_AGE_DAYS=30  # Rebuild if database is older than 30 days (FDA updates monthly)

if [ ! -f "$DB_PATH" ]; then
    echo "========================================="
    echo "Drug database not found at $DB_PATH"
    echo "Building database from FDA data..."
    echo "This is first-time setup or volume was cleared"
    echo "========================================="
    python3 scripts/build_drug_database.py --max-records 25000 || echo "Warning: Drug database build failed, will use FDA API fallback"
elif [ $(find "$DB_PATH" -mtime +$DB_AGE_DAYS 2>/dev/null | wc -l) -gt 0 ]; then
    echo "========================================="
    echo "Drug database is older than $DB_AGE_DAYS days"
    echo "Rebuilding to get latest FDA updates..."
    echo "========================================="
    python3 scripts/build_drug_database.py --max-records 25000 || echo "Warning: Drug database build failed, will use FDA API fallback"
else
    DB_AGE=$((($(date +%s) - $(stat -f %m "$DB_PATH" 2>/dev/null || stat -c %Y "$DB_PATH")) / 86400))
    echo "========================================="
    echo "Drug database found at $DB_PATH (${DB_AGE} days old)"
    echo "Skipping rebuild (database is fresh)"
    echo "Next rebuild in $((DB_AGE_DAYS - DB_AGE)) days or when FDA updates"
    echo "========================================="
fi

# Start mock FHIR server in background if EPIC_MOCK_MODE is enabled
if [ "$EPIC_MOCK_MODE" = "true" ] || [ "$MOCK_FHIR_SERVER_ENABLED" = "true" ]; then
    echo "========================================="
    echo "Starting Mock Epic FHIR Server on port 8888"
    echo "========================================="
    python3 tests/mock_fhir_server.py &
    MOCK_PID=$!
    echo "Mock FHIR server started with PID: $MOCK_PID"
    sleep 2  # Give mock server time to start
fi

# Start the application with the resolved port
exec gunicorn -k uvicorn.workers.UvicornWorker --workers 4 --bind "0.0.0.0:8080" --timeout 120 app:app
