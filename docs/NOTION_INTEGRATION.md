# Notion Integration for AI Nurse Florence

**Purpose:** Track TODOs, progress, and project tasks in Notion for better visibility and planning.

**Philosophy:** Keep it simple - manual sync is fine, don't over-engineer.

---

## Notion Database Schema

### Database: "AI Nurse Florence - Tasks"

**Properties:**

| Property | Type | Description | Values/Options |
|----------|------|-------------|----------------|
| **Task** | Title | Task name/description | - |
| **Status** | Select | Current status | `Not Started`, `In Progress`, `Blocked`, `Completed` |
| **Priority** | Select | Task priority | `Critical`, `High`, `Medium`, `Low` |
| **Category** | Select | Type of work | `Bug Fix`, `Feature`, `Documentation`, `Testing`, `Infrastructure`, `Refactoring` |
| **Effort** | Select | Estimated time | `< 1hr`, `1-3 hrs`, `3-6 hrs`, `1-2 days`, `> 2 days` |
| **Session** | Date | When worked on | - |
| **Completed** | Date | When finished | - |
| **Notes** | Text | Additional context | - |
| **Related Files** | Text | File paths affected | - |
| **Commits** | Text | Git commit hashes | - |

---

## How to Use (Manual Workflow)

### 1. Morning Report → Notion

**After generating morning report:**

1. Open Notion database
2. Review morning report markdown file
3. Manually add/update tasks in Notion:
   - New tasks discovered → Create rows
   - Completed tasks → Mark status as "Completed"
   - In-progress tasks → Update status

**Time:** ~5-10 minutes per session

### 2. Daily Planning

**Before coding session:**

1. Review Notion board
2. Sort by Priority + Status
3. Pick top 3-5 tasks for session
4. Update Status to "In Progress"

### 3. Post-Session Update

**After coding session:**

1. Update completed tasks → Status: "Completed"
2. Add commit hashes to "Commits" field
3. Note any blockers → Status: "Blocked"

---

## Optional: Semi-Automated Sync

**If you want light automation later (NOT now):**

```python
# scripts/sync_to_notion.py - Future enhancement
# Uses Notion API to sync from markdown

import os
from notion_client import Client

# Requires NOTION_API_KEY and NOTION_DATABASE_ID env vars
# Parse morning report markdown
# Create/update Notion database rows
# Keep it simple - one-way sync only
```

**Time to implement:** 2-3 hours (do this later if needed)

---

## Benefits of This Approach

✅ **Simple:** Manual process, no complex automation
✅ **Flexible:** Easy to adjust structure as needs change
✅ **Visual:** Kanban board view in Notion
✅ **Searchable:** Find tasks by category, file, commit
✅ **Historical:** Track completed work over time
✅ **Low Maintenance:** No automation to break

---

## Views to Create in Notion

### View 1: "Active Sprint" (Default)
- **Filter:** Status is "In Progress" OR "Not Started"
- **Sort:** Priority (descending), then Effort
- **Group:** Category

### View 2: "Completed This Week"
- **Filter:** Completed is within "This week"
- **Sort:** Completed (descending)
- **Display:** Table view

### View 3: "Blocked/Needs Attention"
- **Filter:** Status is "Blocked"
- **Sort:** Priority (descending)
- **Display:** List view

### View 4: "By Category"
- **Group:** Category
- **Sort:** Priority within groups
- **Display:** Board view (Kanban)

---

## Example Task Entries

### Bug Fix Example
```
Task: Patient Education Wizard - 422 Validation Error
Status: Completed
Priority: Critical
Category: Bug Fix
Effort: 3-6 hrs
Session: 2025-10-06
Completed: 2025-10-06
Notes: Multi-layer issue - form fields, browser validation, TypeScript errors
Related Files: frontend/src/pages/PatientEducation.tsx, src/routers/patient_education_documents.py
Commits: 2403ad5, f00b330, 3347978
```

### Documentation Example
```
Task: Document enhanced_literature_service.py
Status: Not Started
Priority: Medium
Category: Documentation
Effort: 1-3 hrs
Session: -
Notes: Part of Phase 1A - Priority 1 medical services
Related Files: src/services/enhanced_literature_service.py
```

### Infrastructure Example
```
Task: Drug Database Persistence Strategy
Status: Completed
Priority: High
Category: Infrastructure
Effort: 1-3 hrs
Session: 2025-10-06
Completed: 2025-10-06
Notes: 30-day rebuild cycle, Railway persistent volume
Related Files: start-railway.sh, railway.toml
Commits: 982b37f
```

---

## Migration Path from Morning Reports

**Current:** TODOs scattered across morning reports (markdown)
**Future:** TODOs centralized in Notion database

**Process:**
1. Parse each morning report for TODO sections
2. Extract task lists (checkboxes)
3. Manually create Notion rows for uncompleted items
4. Mark completed items with completion dates

**One-time effort:** ~30-60 minutes to migrate Oct 4-6 reports

---

## Quick Start Instructions

### Step 1: Create Notion Database

1. Open Notion
2. Create new database: "AI Nurse Florence - Tasks"
3. Add all properties from schema above
4. Create the 4 views listed

**Time:** 15 minutes

### Step 2: Migrate Current TODOs

1. Open `docs/MORNING_REPORT_2025-10-04.md`
2. Copy Phase 1A, 1B, 2, 3 TODO lists
3. Create Notion rows for each uncompleted task
4. Repeat for Oct 5-6 reports

**Time:** 30 minutes

### Step 3: Daily Workflow

1. **Morning:** Review Notion, pick tasks
2. **During work:** Update status as you go
3. **End of session:** Mark completed, add commits
4. **Weekly:** Review "Completed This Week" view

**Time per day:** 5-10 minutes

---

## Notes

- **No automation needed initially** - manual is fine and fast
- **Don't over-engineer** - simple structure that works
- **Iterate as needed** - adjust views/properties based on usage
- **Optional later:** Build Python script for auto-sync if manual becomes tedious

---

**Created:** 2025-10-06
**Status:** Proposed (not implemented yet)
**Next Step:** Create Notion database and migrate TODOs from morning reports
