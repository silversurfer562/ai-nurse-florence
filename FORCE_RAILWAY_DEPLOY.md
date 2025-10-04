# Force Railway Deployment to Publish

## Issue
Deployment was created 11 minutes ago but service hasn't published the new version yet.

---

## Solution 1: Check Build Status (Do This First)

1. **Railway Dashboard → Deployments tab**
2. Click on the latest deployment (created 11 minutes ago)
3. Look at **"Build Logs"** tab
4. Check status:
   - ⏳ **"Building"** - Still in progress, wait a bit longer
   - ❌ **"Failed"** - Look for error in logs (see Solution 3)
   - ✅ **"Success"** - Check "Deploy Logs" to see why it hasn't activated

---

## Solution 2: Manual Redeploy via Dashboard

Force a fresh deployment:

1. **Railway Dashboard → Deployments tab**
2. Find the latest deployment
3. Click the **"⋮"** (three dots menu)
4. Select **"Redeploy"**
5. Confirm and wait 3-5 minutes

This forces Railway to rebuild and deploy from scratch.

---

## Solution 3: Check for Build Errors

Common build failures:

### Error: Frontend Build Failed
**Symptom:** Logs show `npm run build` failed

**Fix:**
```bash
# Test frontend build locally first
cd frontend
npm ci
npm run build
# If this fails, fix the error before redeploying
```

### Error: Python Dependencies Failed
**Symptom:** Logs show `pip install` failed

**Fix:**
```bash
# Test locally
pip install -r requirements.txt
# Check for incompatible versions
```

### Error: Database Migration Failed
**Symptom:** Logs show SQLAlchemy or Alembic errors

**Fix:** Add to Railway variables:
```
SKIP_MIGRATIONS=true
```

---

## Solution 4: Force Deploy via Railway CLI

Use CLI to force a fresh deployment:

```bash
# From project directory
cd /Users/patrickroebuck/projects/ai-nurse-florence

# Force upload and deploy
railway up --detach

# Monitor deployment
railway logs
```

---

## Solution 5: Trigger via Git Push

Sometimes a fresh commit helps:

```bash
# Create empty commit
git commit --allow-empty -m "force railway redeploy"

# Push to trigger deployment
git push origin main

# Wait 3-5 minutes and check
./check_deployment.sh
```

---

## Solution 6: Check Railway Service Settings

Verify deployment settings:

1. **Railway Dashboard → Service → Settings**
2. Check **"Deploy"** section:
   - **Start Command**: Should be `/app/start-railway.sh` or similar
   - **Root Directory**: Should be `/` or empty
   - **Builder**: Should auto-detect Dockerfile

3. Check **"Health Check"** section:
   - Path: `/api/v1/health`
   - Timeout: 300 seconds
   - Interval: 30 seconds

If health check is too strict, deployment might be stuck waiting for health check to pass.

---

## Debug: Check What Railway is Doing

### View Live Logs
```bash
railway logs --follow
```

This shows real-time logs. Look for:
- ✅ `"Starting AI Nurse Florence"` - App starting
- ✅ `"Uvicorn running on"` - Server started
- ❌ `"Error:"` - Something failed
- ⏳ Nothing - Build stuck or queued

### Check Deployment Status via CLI
```bash
railway status
```

Should show:
- Current deployment ID
- Status: Active/Building/Failed
- URL to access service

---

## Most Likely Issue: Build Timeout

If build is taking longer than 10 minutes, Railway might have timed out.

**Frontend build is slow** - Building React frontend with npm takes time.

**Fix:** Optimize Dockerfile for faster builds:
1. Cache npm dependencies
2. Use smaller base image
3. Parallelize builds

But for now, just trigger a fresh redeploy (Solution 2).

---

## Quick Action Plan

**Do this now:**

1. ✅ Go to Railway Dashboard → Deployments
2. ✅ Click latest deployment → Check "Build Logs"
3. ✅ Look for errors or stuck status
4. ✅ If stuck/failed: Click ⋮ → "Redeploy"
5. ✅ Wait 5 minutes
6. ✅ Run: `./check_deployment.sh`

---

## After Successful Deployment

You should see:
- ✅ Version: 2.3.0
- ✅ Translations accessible
- ✅ Diagnosis search working
- ✅ Email notifications enabled

Then we can:
1. Test email notifications
2. Fix TLS certificate
3. Set up Railway webhook

---

**🤖 Generated with Claude Code**
