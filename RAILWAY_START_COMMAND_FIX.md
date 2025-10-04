# Fix Railway Start Command Configuration

## Issue
Railway deployment stuck because start command was changed to `npm` instead of using Dockerfile.

---

## Understanding the Architecture

AI Nurse Florence is:
- **Backend**: Python FastAPI (runs on port 8000)
- **Frontend**: React (built during Docker build, served by FastAPI)
- **Deployment**: Docker container with custom start script

**npm is ONLY used during build** to compile the React frontend. It's **NOT** used to start the application.

---

## Correct Railway Configuration

### Service Settings → Deploy Section

1. **Start Command**:
   - ✅ **Leave EMPTY** (recommended - let Dockerfile handle it)
   - ✅ OR set to: `/app/start-railway.sh`
   - ❌ NOT: `npm start` or `npm run dev`

2. **Builder**:
   - ✅ Should auto-detect: **Dockerfile**
   - ❌ NOT: Nixpacks or Buildpack

3. **Root Directory**:
   - ✅ Leave empty or set to: `/`

4. **Dockerfile Path**:
   - ✅ Should be: `Dockerfile` (default)

---

## How the Start Process Works

### During Build (Docker):
```bash
1. Install Python dependencies (pip install)
2. Install Node.js and npm
3. Copy project files
4. Build React frontend (npm ci && npm run build)
5. Make start-railway.sh executable
```

### During Runtime (Container Start):
```bash
1. Docker CMD runs: /app/start-railway.sh
2. Script reads PORT env variable (from Railway)
3. Starts Gunicorn with Uvicorn workers
4. Binds to 0.0.0.0:$PORT
5. FastAPI serves both API and built React frontend
```

---

## Step-by-Step Fix

### 1. Go to Railway Service Settings

Railway Dashboard → Your Service → **Settings** tab

### 2. Check Deploy Configuration

Scroll to **"Deploy"** section and verify:

**Start Command:**
```
[EMPTY - or /app/start-railway.sh]
```

**NOT:**
```
npm start  ❌
npm run dev  ❌
node index.js  ❌
```

### 3. Save Changes

If you made changes, click **"Save"** or **"Update"**

### 4. Trigger Fresh Deployment

Go to **Deployments** tab:
1. Click latest deployment
2. Click **⋮** (three dots)
3. Select **"Redeploy"**
4. Wait 3-5 minutes

### 5. Verify Deployment

After deployment completes, check:

```bash
# Should show v2.3.0
curl -k https://ainurseflorence.com/api/v1/health | grep version

# Should return JSON
curl -k https://ainurseflorence.com/locales/en/translation.json | head -20
```

---

## What Each Component Does

### Dockerfile
- Defines the build process
- Installs all dependencies
- Builds the frontend
- Sets the default start command

### start-railway.sh
- Reads Railway's PORT variable
- Starts Gunicorn with 4 workers
- Uses Uvicorn worker class (for async FastAPI)
- Binds to 0.0.0.0:$PORT

### app.py (FastAPI)
- Main Python application
- Mounts static files (frontend)
- Serves API endpoints
- Serves React app at root

### frontend/ (React)
- Built during Docker build
- Compiled to frontend/dist/
- Served by FastAPI as static files
- NOT run separately

---

## Common Mistakes

### ❌ Mistake 1: Using npm start
```
Start Command: npm start
```
**Why it fails**: This is a Python app, not a Node.js app. npm is only for building the frontend during Docker build.

### ❌ Mistake 2: Wrong port
```
Start Command: python app.py
```
**Why it fails**: Doesn't read Railway's PORT variable. Use start-railway.sh instead.

### ❌ Mistake 3: Not using Dockerfile
```
Builder: Nixpacks
```
**Why it fails**: Nixpacks won't build the frontend correctly. Must use Dockerfile.

---

## Expected Railway Logs (Successful Deployment)

When deployment succeeds, logs should show:

```
Building Docker image...
✓ Step 1/12: FROM python:3.11-slim
✓ Step 2/12: WORKDIR /app
...
✓ Step 11/12: Building frontend (npm ci && npm run build)
✓ Step 12/12: CMD ["/app/start-railway.sh"]
Image built successfully

Deploying...
Starting AI Nurse Florence on port 8080
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:8080
[INFO] Using worker: uvicorn.workers.UvicornWorker
✅ Deployment successful
```

---

## Troubleshooting

### Deployment still fails after fix?

**Check Build Logs for:**
- Frontend build errors (npm ci or npm run build failed)
- Python dependency errors (pip install failed)
- Permission errors (chmod failed)

**Check Deploy Logs for:**
- Port binding errors
- Import errors in Python code
- Database connection errors

---

## Quick Verification Checklist

After fixing start command:

- [ ] Railway Settings → Deploy → Start Command is empty or `/app/start-railway.sh`
- [ ] Railway Settings → Deploy → Builder shows "Dockerfile"
- [ ] Triggered fresh redeploy
- [ ] Build logs show frontend build succeeded
- [ ] Deploy logs show "Starting AI Nurse Florence on port XXXX"
- [ ] Health endpoint returns v2.3.0: `curl -k https://ainurseflorence.com/api/v1/health`
- [ ] Translations accessible: `curl -k https://ainurseflorence.com/locales/en/translation.json`

---

**🤖 Generated with Claude Code**
