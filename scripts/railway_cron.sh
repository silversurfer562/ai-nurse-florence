#!/bin/bash
# Railway Cron Job - Monthly Drug Database Update
# This script is designed to run on Railway as a scheduled job

set -e  # Exit on error

echo "🔄 Starting monthly drug database update..."
echo "📅 Date: $(date)"
echo "🌍 Environment: ${RAILWAY_ENVIRONMENT:-local}"

# Navigate to project directory
cd /app 2>/dev/null || cd "$(dirname "$0")/.."

# Run database update
python3 scripts/build_drug_database.py --max-records 25000

# Check if database was created
if [ -f "data/drugs.db" ]; then
    DB_SIZE=$(ls -lh data/drugs.db | awk '{print $5}')
    DRUG_COUNT=$(sqlite3 data/drugs.db "SELECT COUNT(*) FROM drugs;" 2>/dev/null || echo "unknown")
    echo "✅ Database updated successfully!"
    echo "   Size: $DB_SIZE"
    echo "   Drugs: $DRUG_COUNT"

    # Optional: Commit and push to GitHub (if you want auto-commits)
    # Uncomment if you want database updates to be committed automatically
    # git config user.name "Railway Cron Bot"
    # git config user.email "cron@railway.app"
    # git add data/drugs.db
    # git commit -m "chore: automated drug database update - $(date +%Y-%m-%d)" || true
    # git push || true
else
    echo "❌ Database update failed!"
    exit 1
fi

echo "🎉 Monthly update complete!"
