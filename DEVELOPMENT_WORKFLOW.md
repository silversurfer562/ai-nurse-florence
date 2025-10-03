# Development Workflow - AI Nurse Florence

## Branch Strategy

### Overview
- **`main` branch** → Production environment (https://ainurseflorence.com)
- **`development` branch** → Development environment (https://ai-nurse-florence-development.up.railway.app)

### Current Versions
- **Production (main):** 2.3.1
- **Development (development):** 2.4.0-dev

---

## Daily Development Workflow

### 1. Starting Work

Always work on the **development** branch:

```bash
# Switch to development branch
git checkout development

# Pull latest changes
git pull origin development

# Verify you're on the right branch
git branch --show-current  # Should show: development
```

### 2. Making Changes

```bash
# Make your code changes...
# Edit files, add features, fix bugs, etc.

# Run tests locally
pytest tests/ -v --tb=short

# Stage your changes
git add .

# Commit with conventional commit format
git commit -m "feat: description of your feature"
# or
git commit -m "fix: description of bug fix"
# or
git commit -m "chore: description of maintenance task"
```

### 3. Deploy to Development

```bash
# Push to development branch
git push origin development
```

**Railway will automatically:**
- Detect the push to the development branch
- Build the Docker image
- Deploy to development environment
- Run health checks

### 4. Test in Development

Once deployed (2-3 minutes):

```bash
# Check health and version
curl https://ai-nurse-florence-development.up.railway.app/api/v1/health | jq '.version'
# Should show: "2.4.0-dev"

# Test your changes
curl "https://ai-nurse-florence-development.up.railway.app/api/v1/disease/lookup?q=diabetes"
```

Access the web interface:
- https://ai-nurse-florence-development.up.railway.app

### 5. Deploy to Production (Business Hours Only)

**⚠️ IMPORTANT:** Only deploy to production between 8 AM - 6 PM or after 6 PM if needed.

When your changes are tested and ready:

```bash
# Switch to main branch
git checkout main

# Pull latest main
git pull origin main

# Merge development into main
git merge development

# Verify tests still pass
pytest tests/ -v

# Push to production (triggers Railway deployment)
git push origin main
```

**Wait 3-5 minutes for deployment, then verify:**

```bash
# Check production health
curl https://ainurseflorence.com/api/v1/health | jq '.version'
# Should show: current production version

# Test production endpoints
curl "https://ainurseflorence.com/api/v1/disease/lookup?q=diabetes"
```

**Post-deployment verification:**
1. Open https://ainurseflorence.com in browser
2. Test key features that were changed
3. Check browser console for errors
4. Monitor Railway logs for issues

### 6. Return to Development

```bash
# Always switch back to development after production deploy
git checkout development

# Pull to sync any merge commits
git pull origin development
```

---

## Common Scenarios

### Scenario 1: Quick Bug Fix in Development

```bash
git checkout development
# Fix the bug in your editor
git add .
git commit -m "fix: correct disease lookup error handling"
git push origin development
# Wait for Railway deployment
# Test in development environment
```

### Scenario 2: Emergency Production Hotfix

**Only during business hours or critical emergencies!**

```bash
# Option A: Fix in development first (recommended)
git checkout development
# Make fix
git commit -m "fix: critical issue with authentication"
git push origin development
# Test thoroughly in dev, then merge to main

# Option B: Direct to main (EMERGENCY ONLY)
git checkout main
# Make fix
git commit -m "fix: critical security issue"
git push origin main
# Immediately test in production
# Then backport to development:
git checkout development
git merge main
git push origin development
```

### Scenario 3: Working on a Long-Term Feature

```bash
# Create a feature branch from development
git checkout development
git checkout -b feature/new-clinical-tool

# Work on feature over multiple days
# Commit regularly
git add .
git commit -m "feat: add new clinical assessment tool"
git push origin feature/new-clinical-tool

# When ready, merge to development
git checkout development
git merge feature/new-clinical-tool
git push origin development

# Test in development environment
# When stable, merge development to main for production
```

---

## Railway Environments

### Development Environment
- **URL:** https://ai-nurse-florence-development.up.railway.app
- **Branch:** `development`
- **Version:** 2.4.0-dev
- **Purpose:** Testing new features, bug fixes, experiments
- **Deployment:** Automatic on push to development branch
- **Database:** Separate PostgreSQL instance
- **Redis:** Separate Redis instance
- **Variables:** 21 environment variables (same as production but isolated)

### Production Environment
- **URL:** https://ainurseflorence.com
- **Branch:** `main`
- **Version:** 2.3.1 (or current stable version)
- **Purpose:** Live application for end users
- **Deployment:** Automatic on push to main branch (only during business hours)
- **Database:** Production PostgreSQL instance
- **Redis:** Production Redis instance
- **Stability:** Should always be stable and tested

---

## Testing Checklist

### Before Pushing to Development
- [ ] Code compiles/runs locally
- [ ] Pytest tests pass locally: `pytest tests/ -v`
- [ ] No obvious console errors

### Before Merging to Production
- [ ] All changes tested in development environment
- [ ] Pytest tests pass: `pytest tests/ -v --tb=short`
- [ ] Frontend linting clean (if frontend changed)
- [ ] Manual testing completed in development
- [ ] No breaking changes
- [ ] Documentation updated (if needed)
- [ ] Current time is between 8 AM - 6 PM (preferred)

---

## Emergency Procedures

### If Development is Broken
- Development is for testing - it's okay if it breaks temporarily
- Fix and redeploy from development branch
- No impact on production

### If Production is Broken
1. Check Railway logs immediately
2. Identify the issue
3. If possible, fix in development and test first
4. If critical, hotfix directly to main
5. Document the incident
6. Consider rolling back:
   ```bash
   git checkout main
   git reset --hard <last-good-commit-hash>
   git push origin main --force
   ```

### Rolling Back a Bad Deployment
```bash
# Find the last good commit
git log --oneline -10

# Reset to that commit (example)
git checkout main
git reset --hard 9a3cc3b
git push origin main --force

# Railway will redeploy the previous version
```

---

## Monitoring & Verification

### Check Current Versions
```bash
# Development
curl -s https://ai-nurse-florence-development.up.railway.app/api/v1/health | jq '.version'

# Production
curl -s https://ainurseflorence.com/api/v1/health | jq '.version'
```

### View Railway Logs
```bash
# Development logs
railway logs --environment development --service ai-nurse-florence

# Production logs (if service is linked)
railway logs --environment production --service ai-nurse-florence
```

### Check Railway Deployment Status
```bash
# List recent deployments
railway deployments --environment development
railway deployments --environment production
```

---

## Best Practices

### ✅ DO:
- Always work on the development branch
- Test thoroughly in development before production
- Use conventional commit messages
- Deploy to production during business hours (8 AM - 6 PM)
- Keep main branch stable at all times
- Run tests before deploying
- Monitor deployments after pushing
- Document breaking changes

### ❌ DON'T:
- Don't push directly to main without testing in development first
- Don't deploy to production outside business hours (unless emergency)
- Don't merge untested code to main
- Don't skip running tests
- Don't commit sensitive data (.env files, secrets, database files)
- Don't force push to main unless emergency rollback

---

## Troubleshooting

### "Railway deployment failed"
1. Check build logs in Railway dashboard
2. Look for errors in requirements.txt or Dockerfile
3. Verify all environment variables are set
4. Check if port is correctly configured (8080)

### "Tests failing in CI"
1. Run tests locally: `pytest tests/ -v`
2. Fix failing tests
3. Commit fixes to development
4. Verify in development environment

### "Development and production are out of sync"
```bash
# Update development from main
git checkout development
git merge main
git push origin development
```

---

## Quick Reference Commands

```bash
# Switch to development
git checkout development

# Pull latest
git pull origin development

# Make changes, then...
git add .
git commit -m "feat: your change"
git push origin development

# Check deployment
curl https://ai-nurse-florence-development.up.railway.app/api/v1/health | jq '.version'

# When ready for production
git checkout main
git merge development
git push origin main

# Return to development
git checkout development
```

---

**Last Updated:** 2025-10-03
**Current Production Version:** 2.3.1
**Current Development Version:** 2.4.0-dev
