# 🚂 Railway Build/Publish Troubleshooting Guide

## 🎯 **Quick Fix Steps**

### Step 1: Connect to Railway Project
```bash
# Login to Railway (opens browser)
railway login

# Link your local project to Railway
railway link
# Select your AI Nurse Florence project from the list
```

### Step 2: Check Current Deployment Status
```bash
# View deployment logs
railway logs

# Check current deployment status
railway status
```

### Step 3: Verify Environment Variables
Go to: **Railway Dashboard → Your Project → Variables**

Ensure these are set:
- ✅ `OPENAI_API_KEY` = your OpenAI API key
- ✅ `JWT_SECRET_KEY` = your secure JWT key  
- ✅ `API_BEARER` = your secure API token
- ✅ `DB_PASSWORD` = your database password
- ✅ `USE_LIVE` = `true`
- ✅ `NODE_ENV` = `production`

### Step 4: Trigger New Deployment
```bash
# Push to trigger Railway auto-deployment
git push origin main

# OR manually redeploy in Railway dashboard
railway up
```

## 🚨 **Common Build Issues & Solutions**

### Issue 1: "Module not found" errors
**Solution**: Check Python path and imports
```bash
# Test local imports
python3 -c "import app; print('✅ App imports OK')"

# Check requirements.txt has all dependencies
pip install -r requirements.txt
```

### Issue 2: Wrong start command
**Fixed**: Updated `railway.toml` to use `app:app` instead of `main:app`

### Issue 3: Environment variables missing
**Solution**: Set in Railway Dashboard → Variables tab

### Issue 4: Database connection issues
**Solution**: Railway auto-provides PostgreSQL connection string
- Check if `DATABASE_URL` is auto-set by Railway
- Verify PostgreSQL addon is attached

### Issue 5: Port binding errors
**Solution**: Use Railway's `$PORT` environment variable
- Our config: `--port $PORT` ✅
- Railway auto-sets this

## 🔍 **Debugging Commands**

```bash
# Check Railway project info
railway status

# View real-time logs
railway logs --follow

# Check environment variables
railway vars

# Manual deployment (if auto-deploy fails)
railway up

# Open Railway dashboard
railway open
```

## 📋 **What Railway Needs to Work**

✅ **Files Present:**
- `app.py` (main FastAPI application)
- `requirements.txt` (Python dependencies)
- `railway.toml` (Railway configuration)
- Environment variables set in Railway Dashboard

✅ **Repository Connected:**
- GitHub repository linked to Railway project
- Auto-deployment enabled
- Main branch tracked

## 🎯 **Expected Build Process**

1. **Railway detects push** to main branch
2. **Nixpacks builds** Python environment
3. **Installs dependencies** from requirements.txt
4. **Runs health check** on `/health` endpoint
5. **Starts application** with uvicorn command
6. **Application available** at Railway URL

## ❓ **Still Having Issues?**

Please share:
1. **Specific error messages** from Railway logs
2. **Build output** from Railway dashboard
3. **Environment variables status** (are they all set?)
4. **Railway project URL** for testing

Run this for full diagnostic:
```bash
./diagnose_railway.sh
```
