# Railway.com Deployment Guide for AI Nurse Florence
# 🚂 Complete environment variable setup for Railway

## 🔑 **IMPORTANT: API Key Security**

**Your real OpenAI API key is stored locally in `.env.secrets.local`**  
**Copy that key from your local file and paste it into Railway environment variables.**  
**Never commit API keys to git repositories.**

## 🔗 Railway Environment Variables

Copy and paste these environment variables into your Railway project:

### 🔐 **CRITICAL SECURITY VARIABLES**

```bash
# JWT Secret (Generated securely)
JWT_SECRET_KEY=13e4a2ed4ff7ab0376acdbcaeddc84863c6d124374e8331d1e3f96f87457204d

# API Bearer Token (Generated securely)
API_BEARER=jYZbnAbvRvs0gXfUI75AWNPFBrc0dA7a2z/xLVMQoRI=

# OpenAI API Key (Get from .env.secrets.local)
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 🌐 **PRODUCTION URLS & DOMAINS**

```bash
# Production URLs (Update with your Railway domain)
APP_URL=https://your-railway-app.railway.app
FRONTEND_URL=https://your-railway-app.railway.app
API_BASE_URL=https://your-railway-app.railway.app/api/v1

# CORS Origins (Railway domain + custom domain)
CORS_ORIGINS=["https://your-railway-app.railway.app","https://ainurseflorence.com","https://www.ainurseflorence.com"]
```

### 🗄️ **DATABASE CONFIGURATION**

```bash
# Railway PostgreSQL (Railway will auto-provide DATABASE_URL)
# DATABASE_URL will be automatically set by Railway's PostgreSQL addon
# But you can also set these for compatibility:

DB_HOST=your-railway-postgres-host
DB_PORT=5432
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=your-railway-postgres-password
```

### 🔄 **REDIS CONFIGURATION**

```bash
# Railway Redis (Railway will auto-provide REDIS_URL)
# REDIS_URL will be automatically set by Railway's Redis addon
# But you can also set these for compatibility:

REDIS_HOST=your-railway-redis-host
REDIS_PORT=6379
REDIS_DB=0
```

### 🔒 **PRODUCTION SETTINGS**

```bash
# Environment
NODE_ENV=production
PYTHON_ENV=production
DEBUG=false

# Security Features
ENABLE_SECURITY_HEADERS=true
ENABLE_CACHING=true
ENABLE_METRICS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=150
```

### 🔧 **FEATURE FLAGS**

```bash
# Enable live medical services
USE_LIVE=true
USE_MYDISEASE=true
USE_MEDLINEPLUS=true
USE_PUBMED=true
```

### 📊 **EXTERNAL API SETTINGS**

```bash
# Medical Data APIs (Public URLs)
MYDISEASE_API_URL=https://mydisease.info/v1
MEDLINEPLUS_API_URL=https://connect.medlineplus.gov/service
PUBMED_API_URL=https://eutils.ncbi.nlm.nih.gov/entrez/eutils

# OpenAI Settings
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
```

### 📝 **LOGGING & MONITORING**

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

### 🎯 **JWT CONFIGURATION**

```bash
# JWT Settings
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
JWT_EXPIRE_MINUTES=30
```

## 🚂 **Railway Setup Steps:**

### 1. **Create New Project on Railway**
- Go to [railway.app](https://railway.app)
- Click "New Project"
- Connect your GitHub repository: `silversurfer562/ai-nurse-florence`

### 2. **Add PostgreSQL Database**
- In your Railway project dashboard
- Click "New Service" → "Database" → "PostgreSQL"
- Railway will automatically set `DATABASE_URL`

### 3. **Add Redis Cache**
- Click "New Service" → "Database" → "Redis"
- Railway will automatically set `REDIS_URL`

### 4. **Configure Environment Variables**
- Go to your app service → "Variables" tab
- Copy and paste all the environment variables above
- **IMPORTANT:** Get the real OpenAI API key from your local `.env.secrets.local` file
- Update the URLs with your Railway domain

### 5. **Deploy Configuration**
- Railway will automatically detect Python and use `requirements.txt`
- Make sure `Dockerfile.production` is used for deployment
- Set start command if needed: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### 6. **Custom Domain Setup**
- In Railway dashboard → "Settings" → "Domains"
- Add your custom domain: `ainurseflorence.com`
- Configure DNS to point to Railway

## 🔧 **Important Railway Notes:**

1. **Auto-Generated URLs**: Railway auto-provides `DATABASE_URL` and `REDIS_URL`
2. **Port Configuration**: Railway sets `PORT` environment variable automatically
3. **Build Process**: Railway will use your `requirements.txt` and `Dockerfile.production`
4. **Health Checks**: Railway monitors your `/api/v1/health` endpoint
5. **Logs**: Access logs through Railway dashboard

## 🎯 **Quick Copy-Paste for Railway Variables:**

```
JWT_SECRET_KEY=13e4a2ed4ff7ab0376acdbcaeddc84863c6d124374e8331d1e3f96f87457204d
API_BEARER=jYZbnAbvRvs0gXfUI75AWNPFBrc0dA7a2z/xLVMQoRI=
OPENAI_API_KEY=sk-your-openai-api-key-here
NODE_ENV=production
PYTHON_ENV=production
DEBUG=false
ENABLE_SECURITY_HEADERS=true
ENABLE_CACHING=true
ENABLE_METRICS=true
USE_LIVE=true
USE_MYDISEASE=true
USE_MEDLINEPLUS=true
USE_PUBMED=true
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=150
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

**Remember to replace `sk-your-openai-api-key-here` with your real API key from `.env.secrets.local`**

After deployment, your app will be available at:
- **Railway URL**: `https://your-app-name.railway.app`
- **Custom Domain**: `https://ainurseflorence.com` (after DNS setup)

🏥 **AI Nurse Florence will be ready to help healthcare professionals!**
