# Setup Private Epic Demo Repository
## Instructions for creating ai-nurse-florence-epic-demo

**Goal**: Create a private repository for Epic partnership demonstrations while keeping main repo public.

---

## Step 1: Create Private Repository on GitHub

1. **Go to GitHub**: https://github.com/new
2. **Repository name**: `ai-nurse-florence-epic-demo`
3. **Description**: "Private Epic FHIR integration demo for partnership evaluation"
4. **Visibility**: ⚠️ **Private** (important!)
5. **Initialize**: ❌ Do NOT initialize with README (we'll push existing code)
6. **Click**: "Create repository"

---

## Step 2: Add Remote to Local Repository

```bash
# Navigate to your project
cd /Users/patrickroebuck/projects/ai-nurse-florence

# Ensure you're on the epic-integration-demo branch
git checkout epic-integration-demo

# Add the private repo as a new remote
git remote add epic-private https://github.com/silversurfer562/ai-nurse-florence-epic-demo.git

# Verify remotes
git remote -v
# Should show:
# origin        https://github.com/silversurfer562/ai-nurse-florence.git (public)
# epic-private  https://github.com/silversurfer562/ai-nurse-florence-epic-demo.git (private)
```

---

## Step 3: Push Epic Branch to Private Repo

```bash
# Push epic-integration-demo branch to private repo as main
git push epic-private epic-integration-demo:main

# Output should show:
# Enumerating objects: xxx, done.
# Writing objects: 100% (xxx/xxx), ...
# To https://github.com/silversurfer562/ai-nurse-florence-epic-demo.git
#  * [new branch]      epic-integration-demo -> main
```

---

## Step 4: Set Up Branch Protection (Optional)

On GitHub (private repo):
1. Go to **Settings** → **Branches**
2. Add rule for `main` branch:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require conversation resolution before merging

---

## Step 5: Add Epic Collaborators

When ready to share with Epic:

1. Go to private repo: https://github.com/silversurfer562/ai-nurse-florence-epic-demo
2. **Settings** → **Collaborators and teams** → **Add people**
3. Add Epic evaluators' GitHub usernames (they'll provide these)
4. Set permission level: **Read** (they can view, not modify)

**Epic contacts might request access via**:
- vendorservices@epic.com
- Epic App Orchard portal
- Direct partnership manager

---

## Step 6: Customize Private Repo

Add these files specifically for Epic demo (already in branch):

✅ **EPIC_DEMO_README.md** - Main documentation (already exists)
✅ **docs/EPIC_INTEGRATION_PLAN.md** - Full technical plan (already exists)
✅ **tests/mock_fhir_server.py** - Working demo server (already exists)
✅ **src/integrations/epic_fhir_client.py** - Production client (already exists)

**Optional additions for Epic**:
- [ ] `EPIC_PITCH_DECK.pdf` - Slide deck for partnership presentation
- [ ] `DEMO_VIDEO.mp4` - Screen recording of integration in action
- [ ] `EPIC_CREDENTIALS_NEEDED.md` - List of OAuth scopes and access needed
- [ ] `TESTIMONIALS.md` - Quotes from pilot hospitals (if available)

---

## Step 7: Sync Updates Between Repos

**When you make changes to Epic features:**

```bash
# 1. Make changes on epic-integration-demo branch
git checkout epic-integration-demo
# ... make changes ...
git add .
git commit -m "feat: add new Epic feature"

# 2. Push to BOTH public and private repos
git push origin epic-integration-demo         # Public repo (optional)
git push epic-private epic-integration-demo:main  # Private repo (required)
```

**To keep private repo in sync:**
```bash
# Pull latest from public epic branch
git checkout epic-integration-demo
git pull origin epic-integration-demo

# Push to private repo
git push epic-private epic-integration-demo:main
```

---

## Step 8: Merge Epic Features to Main (After Epic Approval)

**Once Epic credentials are obtained and testing is complete:**

```bash
# Switch to development branch
git checkout development

# Merge epic features
git merge epic-integration-demo

# Push to public repo
git push origin development

# Then merge to main
git checkout main
git merge development
git push origin main

# Update private repo with latest main
git push epic-private main:main
```

---

## Repository Structure

### **Public Repo** (ai-nurse-florence)
```
main                    # Production-ready main app
├── development         # Active development
└── epic-integration-demo  # Epic integration work (can be public or merged)
```

**Purpose**: Community, hospitals, general development
**Visibility**: Public
**URL**: https://github.com/silversurfer562/ai-nurse-florence

### **Private Repo** (ai-nurse-florence-epic-demo)
```
main (= epic-integration-demo)  # Epic integration for evaluation
```

**Purpose**: Epic partnership evaluation only
**Visibility**: Private
**URL**: https://github.com/silversurfer562/ai-nurse-florence-epic-demo
**Collaborators**: Epic evaluators only

---

## What Goes Where?

### ✅ **Keep in Both Repos** (Public + Private)
- Mock FHIR server
- EpicFHIRClient code
- FHIR resource parsers
- Integration documentation
- Technical architecture
- EPIC_DEMO_README.md

### ⚠️ **Private Repo Only**
- Epic credentials (when obtained)
- Partnership negotiations details
- Hospital pilot agreements
- Pricing discussions
- Epic-specific customizations (if requested)

### 🚫 **Never Commit** (Use .env files)
- API keys (OpenAI, etc.)
- OAuth secrets (client_secret)
- Database credentials
- Production tokens
- Hospital-specific configs

---

## Commands Cheat Sheet

```bash
# Clone private repo (for Epic evaluators)
git clone https://github.com/silversurfer562/ai-nurse-florence-epic-demo.git

# Pull latest changes
git pull epic-private main

# Push changes to private repo
git push epic-private epic-integration-demo:main

# View remotes
git remote -v

# Remove private remote (if needed)
git remote remove epic-private

# Check which branch you're on
git branch --show-current
```

---

## Sharing with Epic

### **Option 1: GitHub Collaborator Access** (Recommended)
1. Get Epic evaluator's GitHub username
2. Add as collaborator with Read access
3. They clone: `git clone https://github.com/silversurfer562/ai-nurse-florence-epic-demo.git`

### **Option 2: Private Link** (For viewing only)
1. Generate deployment preview on Vercel/Netlify from private repo
2. Share private preview URL with Epic
3. No code access, just running demo

### **Option 3: Scheduled Demo** (Most impressive)
1. Schedule Zoom/Teams call with Epic
2. Share screen showing:
   - Mock server running
   - Live API calls
   - Code walkthrough
   - Architecture diagrams
3. Record session for future reference

---

## Timeline for Going Public Again

**Phase 1: Private (Now - Epic Sandbox Access)**
- Keep private during initial Epic evaluation (2-4 weeks)
- Share with Epic evaluators only
- Negotiate partnership terms

**Phase 2: Selective Public (Sandbox Testing)**
- Merge Epic integration to public `development` branch
- Show Epic you're confident in the code
- Community can see (but not access sandbox)

**Phase 3: Fully Public (Production Launch)**
- Merge to `main` branch
- Full public documentation
- Epic listed as official integration partner
- Private repo archived or deleted

---

## Security Checklist

Before pushing to private repo:

- [ ] Check `.gitignore` includes `.env*` files
- [ ] Verify no API keys in commit history
- [ ] Ensure no patient data (even mock data should be HIPAA-safe)
- [ ] Review all commits for secrets: `git log --all -p | grep -i "secret\|key\|password\|token"`
- [ ] Check environment variable usage: `grep -r "API_KEY\|SECRET" --include="*.py"`
- [ ] Validate `.env.example` shows structure but no real values

**If secrets found in history:**
```bash
# Use BFG Repo-Cleaner to remove secrets
brew install bfg
bfg --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

## Maintenance

### **Weekly Sync** (While Epic Demo Active)
```bash
# Every Monday
git checkout epic-integration-demo
git pull origin epic-integration-demo  # Get latest from public
git push epic-private epic-integration-demo:main  # Update private

# Check for Epic evaluator activity
# GitHub private repo → Insights → Traffic → See who's viewing
```

### **After Epic Approval**
1. Merge epic-integration-demo to main
2. Keep private repo as snapshot for partnership records
3. Update private repo README: "This demo led to Epic partnership approval"
4. Archive private repo (don't delete - keeps partnership history)

---

## Troubleshooting

### **Problem: "Permission denied" when pushing to private repo**
```bash
# Solution: Verify SSH keys or HTTPS credentials
git remote set-url epic-private git@github.com:silversurfer562/ai-nurse-florence-epic-demo.git
# OR use HTTPS with token
git remote set-url epic-private https://USERNAME:TOKEN@github.com/silversurfer562/ai-nurse-florence-epic-demo.git
```

### **Problem: Accidentally pushed secrets**
```bash
# 1. Remove file from latest commit
git rm .env --cached
git commit --amend -m "Remove secrets"
git push epic-private epic-integration-demo:main --force

# 2. Rotate compromised credentials immediately
# 3. Update .gitignore to prevent recurrence
```

### **Problem: Private repo getting out of sync**
```bash
# Force sync from public epic branch
git fetch origin epic-integration-demo
git checkout epic-integration-demo
git reset --hard origin/epic-integration-demo
git push epic-private epic-integration-demo:main --force
```

---

## Success Metrics

Track these to show Epic your integration's value:

- **Mock Server Usage**: Number of API calls, response times
- **Code Quality**: Test coverage %, linter pass rate
- **Documentation**: Pages of technical docs, examples
- **Community Interest**: GitHub stars, forks, issues
- **Hospital Pilots**: Number of hospitals requesting demo
- **Nurse Feedback**: Time savings, satisfaction scores

Add to private repo: `METRICS.md` with these stats updated weekly.

---

## Next Steps After Private Repo Setup

1. ✅ Create private repo on GitHub
2. ✅ Add remote and push epic-integration-demo branch
3. ⏳ Add Epic evaluators as collaborators (when you have their usernames)
4. ⏳ Create pitch deck (`EPIC_PITCH_DECK.pdf`)
5. ⏳ Record demo video (`DEMO_VIDEO.mp4`)
6. ⏳ Write integration tests to show code quality
7. ⏳ Build MRN lookup UI for live demo
8. ⏳ Schedule Epic demo call

---

**Questions? Issues?**
Update this document as you learn more from Epic's evaluation process.

---

*Keep calm and integrate with Epic* 🏥💙
