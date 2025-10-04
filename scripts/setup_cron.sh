#!/bin/bash
# Setup cron job for monthly drug database updates
# Runs on the 1st of each month at 2 AM

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Create log directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Cron job command
CRON_CMD="0 2 1 * * cd $PROJECT_DIR && /usr/bin/python3 scripts/build_drug_database.py >> $PROJECT_DIR/logs/drug_db_update.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "build_drug_database.py"; then
    echo "⚠️  Cron job already exists. Updating..."
    # Remove old cron job
    crontab -l 2>/dev/null | grep -v "build_drug_database.py" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "📅 Schedule: Monthly on the 1st at 2:00 AM"
echo "📂 Project: $PROJECT_DIR"
echo "📝 Log file: $PROJECT_DIR/logs/drug_db_update.log"
echo ""
echo "To view current cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove this cron job:"
echo "  crontab -l | grep -v 'build_drug_database.py' | crontab -"
echo ""
echo "To test the update now:"
echo "  python3 $PROJECT_DIR/scripts/build_drug_database.py"
