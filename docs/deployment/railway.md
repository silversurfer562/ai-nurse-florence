# Railway Deployment Guide - Consolidated
## Complete guide for deploying AI Nurse Florence on Railway

## Table of Contents
1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Environment Variables](#environment-variables)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [Database and Redis Setup](#database-and-redis-setup)
6. [Custom Domain Configuration](#custom-domain-configuration)
7. [Production Settings](#production-settings)
8. [Troubleshooting](#troubleshooting)
9. [Health Checks and Monitoring](#health-checks-and-monitoring)
10. [Security Best Practices](#security-best-practices)

## Quick Start

Deploy AI Nurse Florence to Railway in 5 minutes:

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Initialize project
railway init

# 4. Link to GitHub repository
railway link

# 5. Deploy
railway up
```

## Prerequisites

- Railway account ([railway.app](https://railway.app))
- GitHub repository connected
- OpenAI API key
- Domain name (optional but recommended)

## Environment Variables

### 🔐 Critical Security Variables (Required)

Copy these to your Railway Variables tab:

```bash
# JWT Secret (Generate securely)
JWT_SECRET_KEY=your-secure-jwt-secret-key-here

# API Bearer Token (Generate securely)
API_BEARER=your-secure-api-bearer-token-here

# OpenAI API Key (Required for AI features)
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here

# Database Password (if not using Railway PostgreSQL addon)
DB_PASSWORD=your-secure-database-password
```

### 🌐 Production URLs & Domains

```bash
# Production URLs (Update with your Railway domain)
APP_URL=https://your-app-name.railway.app
FRONTEND_URL=https://your-app-name.railway.app
API_BASE_URL=https://your-app-name.railway.app/api/v1

# CORS Origins (Railway domain + custom domain)
CORS_ORIGINS=["https://your-app-name.railway.app","https://ainurseflorence.com"]

# Custom domain (if applicable)
CUSTOM_DOMAIN=ainurseflorence.com
```

### 🗄️ Database Configuration

Railway automatically provides `DATABASE_URL` when you add PostgreSQL:

```bash
# Railway auto-provides DATABASE_URL
# But you can also set these for compatibility:
DB_HOST=${{PGHOST}}
DB_PORT=${{PGPORT}}
DB_NAME=${{PGDATABASE}}
DB_USER=${{PGUSER}}
DB_PASSWORD=${{PGPASSWORD}}
```

### 🔄 Redis Configuration

Railway automatically provides `REDIS_URL` when you add Redis:

```bash
# Railway auto-provides REDIS_URL
# Optional fallback configuration:
REDIS_HOST=${{REDISHOST}}
REDIS_PORT=${{REDISPORT}}
REDIS_PASSWORD=${{REDISPASSWORD}}
```

### 🔒 Production Settings

```bash
# Environment
NODE_ENV=production
PYTHON_ENV=production
DEBUG=false
PORT=$PORT  # Railway provides this

# Security Features
ENABLE_SECURITY_HEADERS=true
ENABLE_CACHING=true
ENABLE_METRICS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=150
```

### 🔧 Feature Flags

```bash
# Enable live medical services
USE_LIVE=true
USE_MYDISEASE=true
USE_MEDLINEPLUS=true
USE_PUBMED=true

# Optional: Enhanced PubMed access
NCBI_API_KEY=your-ncbi-api-key-here
```

### 📊 External API Settings

```bash
# Medical Data APIs (Public URLs)
MYDISEASE_API_URL=https://mydisease.info/v1
MEDLINEPLUS_API_URL=https://connect.medlineplus.gov/service
PUBMED_API_URL=https://eutils.ncbi.nlm.nih.gov/entrez/eutils
CLINICALTRIALS_API_URL=https://clinicaltrials.gov/api/v2

# OpenAI Settings
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
```

### 📝 Logging & Monitoring

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_ACCESS_LOGS=true

# Health checks
HEALTH_CHECK_TIMEOUT=30
HEALTH_CHECK_INTERVAL=60

# Performance
CACHE_TTL_SECONDS=3600
CACHE_MAX_SIZE=1000
```

## Step-by-Step Deployment

### Step 1: Create New Railway Project

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `silversurfer562/ai-nurse-florence`
5. Railway will automatically detect the Python application

### Step 2: Add PostgreSQL Database

1. In your Railway project dashboard
2. Click "New Service" → "Database" → "PostgreSQL"
3. Railway will automatically:
   - Create the database
   - Set `DATABASE_URL` environment variable
   - Handle connection pooling

### Step 3: Add Redis Cache

1. Click "New Service" → "Database" → "Redis"
2. Railway will automatically:
   - Create Redis instance
   - Set `REDIS_URL` environment variable
   - Configure persistence

### Step 4: Configure Environment Variables

1. Go to your app service → "Variables" tab
2. Click "Raw Editor"
3. Paste all environment variables from above
4. **Important**: Replace placeholder values with actual keys
5. Click "Update Variables"

### Step 5: Configure Build Settings

Railway should auto-detect, but verify:

```toml
# railway.toml (if needed)
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Step 6: Deploy

Railway will automatically deploy when you:
- Push to your GitHub repository
- Update environment variables
- Click "Redeploy" in the dashboard

## Database and Redis Setup

### PostgreSQL Configuration

Railway PostgreSQL comes pre-configured, but you can customize:

```sql
-- Run these in Railway's PostgreSQL query interface
ALTER SYSTEM SET max_connections = '200';
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
```

### Redis Configuration

Railway Redis is configured for persistence by default:

```bash
# These are set automatically
maxmemory-policy=allkeys-lru
maxmemory=256mb
save=900 1 300 10 60 10000
```

## Custom Domain Configuration

### Step 1: Add Custom Domain in Railway

1. Go to Settings → Domains
2. Click "Add Custom Domain"
3. Enter your domain: `ainurseflorence.com`
4. Railway provides DNS records

### Step 2: Configure DNS

Add these records to your DNS provider:

```
Type: CNAME
Name: @
Value: your-app-name.up.railway.app

Type: CNAME
Name: www
Value: your-app-name.up.railway.app
```

### Step 3: SSL Certificate

Railway automatically provisions Let's Encrypt SSL certificates.

## Production Settings

### Optimized Dockerfile

```dockerfile
# Dockerfile (if customizing)
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:$PORT/api/v1/health || exit 1

# Run application
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
```

### Performance Tuning

```bash
# Add these for production performance
UVICORN_WORKERS=4  # Multiple worker processes
UVICORN_LOOP=uvloop  # Faster event loop
UVICORN_HTTP=httptools  # Faster HTTP parsing
```

## Troubleshooting

### Common Issues and Solutions

#### Build Fails
```bash
# Check build logs
railway logs --build

# Common fixes:
# 1. Verify Python version in runtime.txt
# 2. Check requirements.txt for conflicts
# 3. Ensure all imports are correct
```

#### Module Not Found Errors
```bash
# Test imports locally
python3 -c "import app; print('✅ App imports OK')"

# Ensure all dependencies in requirements.txt
pip freeze > requirements.txt
```

#### Database Connection Issues
```bash
# Railway auto-provides DATABASE_URL
# Check if it's set:
railway variables

# Test connection:
railway run python -c "from database import engine; print(engine.url)"
```

#### Port Binding Errors
```bash
# Railway provides $PORT automatically
# Ensure your start command uses it:
uvicorn app:app --host 0.0.0.0 --port $PORT
```

#### Environment Variables Not Working
```bash
# Check variables are set
railway variables

# Force redeploy after setting variables
railway redeploy
```

### Debugging Commands

```bash
# View logs
railway logs --follow

# Check deployment status
railway status

# Open Railway dashboard
railway open

# Run commands in production
railway run python manage.py migrate

# Connect to production shell
railway shell
```

## Health Checks and Monitoring

### Health Check Endpoint

Railway monitors `/api/v1/health`:

```json
{
  "status": "healthy",
  "timestamp": "2025-09-28T10:00:00Z",
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "external_apis": {
      "mydisease": "healthy",
      "pubmed": "healthy",
      "clinicaltrials": "healthy"
    }
  }
}
```

### Monitoring Dashboard

Access metrics at:
- Deployment logs: Railway Dashboard → Deployments → View Logs
- Metrics: Railway Dashboard → Metrics
- Usage: Railway Dashboard → Usage

### Setting Up Alerts

Configure alerts in Railway:
1. Go to Settings → Notifications
2. Add webhook URL or email
3. Configure alert conditions:
   - Deployment failures
   - High error rates
   - Resource usage

## Security Best Practices

### 1. Secure Secret Generation

```python
# Generate secure secrets
import secrets

# JWT Secret
jwt_secret = secrets.token_hex(32)
print(f"JWT_SECRET_KEY={jwt_secret}")

# API Bearer Token
api_bearer = secrets.token_urlsafe(32)
print(f"API_BEARER={api_bearer}")

# Database Password
db_password = secrets.token_urlsafe(24)
print(f"DB_PASSWORD={db_password}")
```

### 2. Environment Variable Security

- ✅ Never commit secrets to Git
- ✅ Use Railway's encrypted variable storage
- ✅ Rotate keys regularly
- ✅ Use different keys for staging/production

### 3. Network Security

```bash
# Configure in Railway
ALLOWED_HOSTS=your-app-name.railway.app,ainurseflorence.com
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
```

### 4. Rate Limiting

```python
# Configured automatically with these settings
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_STORAGE=redis
RATE_LIMIT_KEY_PREFIX=rl:
```

## Quick Copy-Paste Variables

For quick setup, copy this entire block to Railway Variables (Raw Editor):

```env
JWT_SECRET_KEY=generate-your-secure-jwt-secret-here
API_BEARER=generate-your-secure-api-bearer-here
OPENAI_API_KEY=sk-proj-your-openai-key-here
NODE_ENV=production
PYTHON_ENV=production
DEBUG=false
USE_LIVE=true
ENABLE_SECURITY_HEADERS=true
ENABLE_CACHING=true
ENABLE_METRICS=true
RATE_LIMIT_PER_MINUTE=100
LOG_LEVEL=INFO
LOG_FORMAT=json
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
CORS_ORIGINS=["https://your-app-name.railway.app"]
```

## Deployment Verification

After deployment, verify everything is working:

1. **Health Check**: 
   ```bash
   curl https://your-app-name.railway.app/api/v1/health
   ```

2. **API Documentation**:
   - Visit: `https://your-app-name.railway.app/docs`

3. **Test Endpoints**:
   ```bash
   # Disease lookup
   curl "https://your-app-name.railway.app/api/v1/disease?q=diabetes"
   
   # PubMed search
   curl "https://your-app-name.railway.app/api/v1/pubmed?q=hypertension"
   ```

## Support and Resources

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Project Issues**: [GitHub Issues](https://github.com/silversurfer562/ai-nurse-florence/issues)
- **Railway Status**: [status.railway.app](https://status.railway.app)

---

**Last Updated**: September 2025  
**Deployment Version**: 2.0.0  
**Platform**: Railway.app
