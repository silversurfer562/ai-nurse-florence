# Cron Job Setup for Drug Database Updates

This guide explains how to set up automated monthly updates for the drug database.

## 🏠 Local Development (Mac/Linux)

### Quick Setup

Run the automated setup script:

```bash
./scripts/setup_cron.sh
```

This installs a cron job that runs on the **1st of each month at 2:00 AM**.

### Manual Setup

Add to your crontab manually:

```bash
crontab -e
```

Add this line:
```cron
0 2 1 * * cd /Users/patrickroebuck/projects/ai-nurse-florence && /usr/bin/python3 scripts/build_drug_database.py >> /Users/patrickroebuck/projects/ai-nurse-florence/logs/drug_db_update.log 2>&1
```

### Verify Installation

```bash
crontab -l
```

### View Logs

```bash
tail -f logs/drug_db_update.log
```

### Remove Cron Job

```bash
crontab -l | grep -v 'build_drug_database.py' | crontab -
```

---

## ☁️ Railway Production

Railway doesn't have built-in cron jobs, but you have several options:

### Option 1: GitHub Actions (Recommended) ✅

Create `.github/workflows/update-drug-database.yml`:

```yaml
name: Update Drug Database
on:
  schedule:
    - cron: '0 2 1 * *'  # Monthly on 1st at 2 AM UTC
  workflow_dispatch:  # Manual trigger button

jobs:
  update-database:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Build drug database
        run: python3 scripts/build_drug_database.py --max-records 25000

      - name: Commit and push if changed
        run: |
          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          git add data/drugs.db
          git diff --quiet && git diff --staged --quiet || (git commit -m "chore: update drug database from FDA [$(date +%Y-%m-%d)]" && git push)
```

**Benefits:**
- ✅ Free on GitHub
- ✅ Reliable scheduling
- ✅ Auto-commits updated database
- ✅ Triggers Railway deployment automatically

### Option 2: External Cron Service

Use a service like **cron-job.org** or **EasyCron**:

1. Create account at https://cron-job.org
2. Set schedule: `0 2 1 * *` (monthly)
3. Create Railway API endpoint:

```python
# Add to src/routers/admin.py
from fastapi import APIRouter, BackgroundTasks
import subprocess

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/update-drug-database")
async def trigger_database_update(background_tasks: BackgroundTasks):
    """Trigger drug database update (called by external cron)"""
    background_tasks.add_task(run_database_update)
    return {"status": "Database update triggered"}

def run_database_update():
    subprocess.run(["python3", "scripts/build_drug_database.py", "--max-records", "25000"])
```

4. Point cron-job.org to: `https://your-app.railway.app/admin/update-drug-database`

### Option 3: Railway Deployment Auto-Update

**Already Configured!** ✅

The Dockerfile automatically rebuilds the database on each deployment:

```dockerfile
RUN python3 scripts/build_drug_database.py --max-records 25000
```

So every time you deploy to Railway, you get fresh FDA data!

### Option 4: Manual Updates

Simply run locally and commit:

```bash
python3 scripts/build_drug_database.py
git add data/drugs.db
git commit -m "chore: update drug database"
git push
```

Railway will auto-deploy with the updated database.

---

## 📊 Monitoring Updates

### Check Last Update

```bash
sqlite3 data/drugs.db "SELECT value FROM metadata WHERE key='last_updated';"
```

### Check Drug Count

```bash
sqlite3 data/drugs.db "SELECT COUNT(*) FROM drugs;"
```

### Check Database Size

```bash
ls -lh data/drugs.db
```

---

## 🔧 Troubleshooting

### Cron job not running

**Check cron is active:**
```bash
sudo systemctl status cron  # Linux
# or
sudo launchctl list | grep cron  # macOS
```

**Check logs:**
```bash
tail -f logs/drug_db_update.log
```

**Test manually:**
```bash
python3 scripts/build_drug_database.py
```

### Database not updating on Railway

1. Check GitHub Actions workflow status
2. Verify Railway deployment succeeded
3. Check Railway build logs for database build step
4. Ensure `data/drugs.db` is in git (should be force-added)

### FDA API rate limiting

If you hit rate limits, the script will gracefully stop. Current limits:
- 1000 requests/minute
- 120,000 requests/day

Our monthly updates use ~30 requests, well within limits.

---

## 📅 Recommended Schedule

| Environment | Update Frequency | Method |
|-------------|-----------------|--------|
| **Local Dev** | Manual (as needed) | `python3 scripts/build_drug_database.py` |
| **Production** | Monthly (1st @ 2 AM) | GitHub Actions + Railway auto-deploy |
| **Emergency** | On-demand | Manual run + push |

---

## ✅ Current Setup Status

- ✅ **Local cron:** Installed (monthly on 1st @ 2:00 AM)
- ✅ **Railway auto-build:** Configured in Dockerfile
- ⏳ **GitHub Actions:** Not yet configured (optional)
- ✅ **Database:** 25,718 drugs loaded

---

*Last Updated: 2025-10-04*
