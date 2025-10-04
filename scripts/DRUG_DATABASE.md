# Drug Database Setup and Maintenance

This document explains how to build and maintain the comprehensive drug database for AI Nurse Florence.

## Overview

The drug database is built from **FDA OpenFDA NDC (National Drug Code)** data, which is:
- ✅ 100% Free and Public (U.S. Government data)
- ✅ Comprehensive (all FDA-approved drugs)
- ✅ Authoritative (direct from FDA)
- ✅ Updated regularly by FDA

## Quick Start

### 1. Build the Database (First Time)

```bash
# Full database (recommended - downloads all FDA drugs, ~170,000+ records)
python3 scripts/build_drug_database.py

# Test mode (only 1000 records for testing)
python3 scripts/build_drug_database.py --test

# Limited records (e.g., 10,000 records)
python3 scripts/build_drug_database.py --max-records 10000
```

### 2. Update the Database (Periodic Updates)

Run the same command to refresh with latest FDA data:

```bash
python3 scripts/build_drug_database.py
```

**Recommended update frequency:** Monthly or quarterly

## Database Location

The database is created at:
```
/data/drugs.db
```

This SQLite database contains:
- **drugs table:** All drug records with NDC codes, generic names, brand names, routes, etc.
- **metadata table:** Database info (total drugs, last updated, source)

## Database Schema

```sql
CREATE TABLE drugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_ndc TEXT UNIQUE NOT NULL,
    generic_name TEXT,
    brand_name TEXT,
    brand_name_base TEXT,
    dosage_form TEXT,
    route TEXT,
    product_type TEXT,
    labeler_name TEXT,
    substance_name TEXT,
    active_ingredients TEXT,  -- JSON array
    pharm_class TEXT,
    dea_schedule TEXT,
    marketing_category TEXT,
    application_number TEXT,
    packaging TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## How the Drug Lookup Works

### Lookup Priority (Waterfall Strategy):

1. **SQLite Database** (fastest, local)
   - Searches generic_name, brand_name, brand_name_base, substance_name
   - Returns comprehensive drug info instantly

2. **FDA OpenFDA API** (fallback for missing drugs)
   - Queries live FDA API if drug not in local database
   - Returns detailed label data

3. **Placeholder** (last resort)
   - If drug not found anywhere, returns "Unknown" placeholder
   - Ensures all drugs are displayed (fixes the "missing 3rd drug" bug)

### Enhanced Data Flow:

```
User enters: "aspirin, warfarin, atorvastatin"
    ↓
For each drug:
    1. Check SQLite database → Found atorvastatin ✓
    2. Enrich with FDA label API → Get detailed warnings, interactions
    3. Check hardcoded interaction rules → Check for known major interactions
    ↓
Display all 3 drugs with comprehensive data
```

## Data Sources

### Primary Source: FDA OpenFDA NDC
- **API:** https://api.fda.gov/drug/ndc.json
- **License:** Public Domain
- **Coverage:** ~170,000+ drug products
- **Fields:** NDC, generic name, brand name, dosage form, route, manufacturer

### Secondary Source: FDA OpenFDA Drug Labels
- **API:** https://api.fda.gov/drug/label.json
- **License:** Public Domain
- **Coverage:** Detailed label data for approved drugs
- **Fields:** Indications, contraindications, warnings, boxed warnings, interactions, etc.

## Automation Options

### Option 1: Cron Job (Linux/Mac)
```bash
# Run monthly on the 1st at 2 AM
0 2 1 * * cd /path/to/ai-nurse-florence && python3 scripts/build_drug_database.py >> /var/log/drug_db_update.log 2>&1
```

### Option 2: GitHub Actions (Automated CI/CD)
Create `.github/workflows/update-drug-database.yml`:

```yaml
name: Update Drug Database
on:
  schedule:
    - cron: '0 2 1 * *'  # Monthly on 1st at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  update-database:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install requests
      - name: Build drug database
        run: python3 scripts/build_drug_database.py
      - name: Commit and push if changed
        run: |
          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          git add data/drugs.db
          git diff --quiet && git diff --staged --quiet || (git commit -m "chore: update drug database from FDA" && git push)
```

### Option 3: Railway Scheduled Job
Use Railway's cron jobs feature:
```bash
# In railway.toml or Railway dashboard
[cron]
schedule = "0 2 1 * *"
command = "python3 scripts/build_drug_database.py"
```

## Database Statistics

After building, check stats:
```bash
sqlite3 data/drugs.db "SELECT COUNT(*) as total_drugs FROM drugs;"
sqlite3 data/drugs.db "SELECT value FROM metadata WHERE key='last_updated';"
```

## Troubleshooting

### Database not found error
```
⚠️ Drug database not found at /data/drugs.db
```
**Solution:** Run `python3 scripts/build_drug_database.py` to build it

### Slow queries
**Solution:** The database has indexes on generic_name, brand_name, and substance_name. Queries should be fast (<10ms)

### Out of date data
**Solution:** Re-run the build script to fetch latest FDA data

## Future Enhancements

1. **RxNorm Integration** - Add RxNorm IDs for standardization
2. **Drug Interactions Database** - Store known interactions in database
3. **DrugBank Data** (academic license) - More comprehensive interaction data
4. **Incremental Updates** - Only fetch changed records instead of full rebuild

## References

- [FDA OpenFDA API](https://open.fda.gov/apis/)
- [FDA NDC API Docs](https://open.fda.gov/apis/drug/ndc/)
- [FDA Drug Label API Docs](https://open.fda.gov/apis/drug/label/)
- [RxNorm (NLM)](https://www.nlm.nih.gov/research/umls/rxnorm/)

---

*Last Updated: 2025-10-04*
