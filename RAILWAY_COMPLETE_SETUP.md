# Railway Complete Production Setup
## AI Nurse Florence - Full Configuration Guide

---

## 🎯 Overview

Your app needs these Railway services:
1. **Main App** (FastAPI + React) - Already deployed
2. **Redis** (Caching) - Needed
3. **Postgres** (Database) - Recommended for production

---

## 📋 Current Status

✅ Main app is running (v2.1.0)
❌ Recent deployment stuck (v2.3.0 not deployed)
❓ Redis not configured
❓ Postgres not configured

---

## 🚀 Step 1: Add Redis to Railway

### 1.1 Create Redis Service

1. Railway Dashboard → "AI Nurse Florence" project
2. Click **"New"** → **"Database"** → **"Add Redis"**
3. Railway will automatically:
   - Create Redis instance
   - Generate `REDIS_URL` variable
   - Link it to your service

### 1.2 Verify Redis Variable

After adding Redis:
1. Go to your main service → **"Variables"** tab
2. You should see: `REDIS_URL=redis://...`
3. If not, manually link:
   - Variables tab → **"New Variable"** → **"Add a Reference"**
   - Select: `Redis.REDIS_URL`

---

## 🐘 Step 2: Add Postgres to Railway

### 2.1 Create Postgres Service

1. Railway Dashboard → "AI Nurse Florence" project
2. Click **"New"** → **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically:
   - Create Postgres instance
   - Generate `DATABASE_URL` variable
   - Link it to your service

### 2.2 Configure Database Variables

After adding Postgres, add these variables to your main service:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}  (Reference variable)
POSTGRES_USER=${{Postgres.PGUSER}}       (Reference variable)
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}} (Reference variable)
POSTGRES_DB=${{Postgres.PGDATABASE}}     (Reference variable)
```

---

## 📧 Step 3: Add Email Notifications

Add these environment variables to your main service:

```
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_RECIPIENTS=your-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=whteggcxypqmpdvh
SMTP_FROM_EMAIL=your-email@gmail.com
```

---

## 🔧 Step 4: Fix Current Deployment Issue

The deployment is failing because Railway might be building the wrong commit. Let's force a redeploy:

### Option A: Trigger Redeploy via Dashboard

1. Railway Dashboard → Your Service
2. Go to **"Deployments"** tab
3. Find the latest deployment
4. Click **"⋮"** (three dots) → **"Redeploy"**

### Option B: Empty Commit Push

```bash
git commit --allow-empty -m "trigger railway redeploy"
git push origin main
```

### Option C: Railway CLI Force Deploy

```bash
railway up --detach
```

---

## ✅ Step 5: Verify Everything Works

After deployment completes:

### 5.1 Check Health Endpoint
```bash
curl https://ainurseflorence.com/api/v1/health
```

Should show:
- `"version": "2.3.0"` ✅
- `"status": "healthy"` ✅

### 5.2 Check Database Seeding
Look for in Railway logs:
```
✅ Diagnosis library ready (34 diagnoses)
```

### 5.3 Check Redis Connection
Railway logs should show:
```
✅ Redis connected
```

### 5.4 Test Email Notifications
```bash
curl -X POST https://ainurseflorence.com/api/v1/webhooks/test
```

You should receive a test email!

---

## 🌐 Step 6: Fix TLS Certificate

After services are stable:

1. Railway Dashboard → Service → **"Settings"** → **"Domains"**
2. **Remove** `ainurseflorence.com`
3. Wait 30 seconds
4. **Add** `ainurseflorence.com` again
5. Wait for certificate status: "Issuing" → "Active" (1-5 min)

---

## 📊 Step 7: Set Up Railway Webhook

1. Railway Dashboard → Project **"Settings"** → **"Webhooks"**
2. Click **"New Webhook"**
3. URL: `https://ainurseflorence.com/api/v1/webhooks/railway`
4. Events: Select all (Success, Failed, Crashed, Building, Deploying)
5. **Save**

Now you'll get emails for every deployment!

---

## 🔍 Railway Project Architecture

After setup, your Railway project will have:

```
AI Nurse Florence (Project)
├── ai-nurse-florence (Main Service)
│   ├── Environment: production
│   ├── Domain: ainurseflorence.com
│   └── Variables:
│       ├── REDIS_URL → ${{Redis.REDIS_URL}}
│       ├── DATABASE_URL → ${{Postgres.DATABASE_URL}}
│       ├── NOTIFICATION_EMAIL_ENABLED=true
│       └── SMTP_* (email config)
├── Redis (Database Service)
│   └── Provides: REDIS_URL
└── Postgres (Database Service)
    └── Provides: DATABASE_URL, PGUSER, PGPASSWORD, PGDATABASE
```

---

## 💰 Railway Pricing Note

**Free Tier Limits:**
- $5 credit/month
- Sleeps after 30 min inactivity (app restarts when accessed)

**Recommended:**
- Add payment method for uninterrupted service
- Estimated cost: $10-20/month for 3 services (app + Redis + Postgres)

---

## 🐛 Troubleshooting

### Deployment Fails with "Application Failed to Respond"

**Cause**: App crashed during startup

**Fix**:
1. Check Railway logs for error
2. Common issues:
   - Missing environment variables
   - Database connection failed
   - Port binding issue

### Redis Connection Errors

**Symptoms**: Logs show "Redis connection failed"

**Fix**:
1. Verify `REDIS_URL` variable exists
2. Check Redis service is running
3. Redis is optional - app should still work without it

### Postgres Migration Needed

**After adding Postgres**, run migrations:

```bash
# Via Railway CLI
railway run alembic upgrade head

# Or add to startup script
```

### Version Still Shows 2.1.0

**Cause**: Deployment hasn't completed or failed

**Fix**:
1. Check Railway deployment status
2. Look for build errors in logs
3. Force redeploy (see Step 4)

---

## 📚 Environment Variables Complete List

### Required:
```bash
PORT=8000                          # Auto-set by Railway
PYTHONUNBUFFERED=1                 # Auto-set by Railway
```

### Database (after adding Postgres):
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
POSTGRES_USER=${{Postgres.PGUSER}}
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
POSTGRES_DB=${{Postgres.PGDATABASE}}
```

### Cache (after adding Redis):
```bash
REDIS_URL=${{Redis.REDIS_URL}}
REDIS_MAX_CONNECTIONS=20
```

### Email Notifications:
```bash
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_RECIPIENTS=your-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=whteggcxypqmpdvh
SMTP_FROM_EMAIL=your-email@gmail.com
```

### Optional (if using OpenAI features):
```bash
OPENAI_API_KEY=sk-...
```

---

## 🎯 Quick Start Checklist

- [ ] Add Redis service to Railway
- [ ] Add Postgres service to Railway
- [ ] Add email notification variables
- [ ] Force redeploy to get v2.3.0
- [ ] Verify health endpoint shows v2.3.0
- [ ] Fix TLS certificate (remove/re-add domain)
- [ ] Set up Railway webhook
- [ ] Test email notifications
- [ ] Verify diagnosis search works
- [ ] Verify translations show correctly

---

**🤖 Generated with Claude Code**
