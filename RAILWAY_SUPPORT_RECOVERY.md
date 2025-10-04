# Recovering from Railway Support Changes
## After Tech Support Deleted/Modified Service

---

## 🔴 What Happened

Railway tech support likely:
- Deleted the original service to fix SSL issue
- Created a new service
- OR moved service to different project/environment
- OR reset the service configuration

**Result**: Dashboard shows empty, but site still works at `ainurseflorence.com`

---

## 🔍 Step 1: Find Where Your Service Actually Is

### Option A: Check All Projects

1. Go to: https://railway.app
2. Look at **ALL projects** in the sidebar (not just "AI Nurse Florence")
3. Check each project for a running service
4. Look for services with these indicators:
   - Domain: `ainurseflorence.com`
   - Name: Contains "ai-nurse-florence" or "florence"
   - Status: Active/Running

### Option B: Check Railway Activity Log

1. Railway Dashboard → Any project
2. Click **"Activity"** tab (left sidebar)
3. Look for recent events:
   - "Service created"
   - "Service deleted"
   - "Domain added"
   - Recent deployments

### Option C: Railway Support Ticket

1. Check your email for Railway support responses
2. They might have told you:
   - New project name
   - New service URL
   - What they changed

---

## 🎯 Step 2: Reconnect to the Running Service

Once you find where it is:

### If service is in different project:

```bash
# Unlink current
railway unlink

# Link to correct project
railway link
# Select the project where your service actually is
```

### If service has different name:

```bash
railway service
# Select the correct service from the list
```

---

## 🔧 Step 3: Alternative - Create Fresh Setup

If you can't find the service or it's too messy, **start fresh**:

### 3.1 Create New Railway Project from GitHub

1. Railway Dashboard → **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: `silversurfer562/ai-nurse-florence`
4. Select branch: `main`
5. Click **"Deploy"**

Railway will:
- Auto-detect Dockerfile
- Build and deploy
- Give you new domain: `*.up.railway.app`

### 3.2 Add Domain to New Service

1. New service → **"Settings"** → **"Domains"**
2. Click **"Add Domain"**
3. Enter: `ainurseflorence.com`
4. Railway will show DNS records
5. Update your DNS if needed (might already be correct)

### 3.3 Add Services (Redis, Postgres)

1. Same project → **"New"** → **"Database"** → **"Add Redis"**
2. Same project → **"New"** → **"Database"** → **"Add PostgreSQL"**
3. Variables will auto-link

### 3.4 Add Environment Variables

Copy from [SETUP_EMAIL_NOTIFICATIONS.md](SETUP_EMAIL_NOTIFICATIONS.md):
- Email notification variables (7 variables)
- Any other custom variables you had

---

## 📧 Step 4: Contact Railway Support for Clarification

If you're confused, email Railway support:

**Support Email**: support@railway.app

**Sample Message**:
```
Subject: Service Disappeared After SSL Support Ticket

Hi Railway Team,

You recently helped me with an SSL certificate issue for ainurseflorence.com
(ticket #XXXXX). After your changes, my Railway dashboard shows no services
in the "AI Nurse Florence" production environment, but the site is still
responding.

Can you please clarify:
1. What changes were made to my service?
2. Where is the service now running?
3. How do I reconnect my Railway CLI to it?
4. Were any environment variables or databases affected?

Project: AI Nurse Florence
Email: silversurfer562@gmail.com
Domain: ainurseflorence.com

Thank you!
```

---

## 🔍 Step 5: Check What's Actually Running

Let's figure out what version and configuration is live:

```bash
# Check version
curl -k https://ainurseflorence.com/api/v1/health | grep version

# Check routers loaded
curl -k https://ainurseflorence.com/api/v1/health | grep routers_loaded

# Check if webhooks are registered
curl -k https://ainurseflorence.com/api/v1/docs
# Look for /webhooks routes
```

---

## 💡 Prevention for Future

After you get this sorted:

### 1. Document Everything
Create a file `railway-config.txt` with:
- Project ID
- Service ID
- Environment variables list
- Domain configuration
- Database service names

### 2. Export Environment Variables
```bash
railway variables > railway-variables-backup.txt
```

### 3. Take Screenshots
- Railway dashboard showing services
- Domain configuration
- Database connections

### 4. Use Railway CLI to Stay Connected
```bash
# Always verify connection
railway status

# Should show:
# - Project name
# - Service name
# - Environment
```

---

## 🚨 If Site Goes Down

While figuring this out, if the site goes down:

### Quick Redeploy

```bash
cd /Users/patrickroebuck/projects/ai-nurse-florence

# Force deploy to Railway
railway up --detach

# OR push to trigger deploy
git commit --allow-empty -m "redeploy"
git push origin main
```

---

## ✅ Recovery Checklist

- [ ] Find where service is actually running
- [ ] Reconnect Railway CLI to correct project/service
- [ ] Verify environment variables are still there
- [ ] Add Redis if not present
- [ ] Add Postgres if not present
- [ ] Add email notification variables
- [ ] Fix SSL certificate (remove/re-add domain)
- [ ] Set up webhook
- [ ] Document current configuration
- [ ] Export variables as backup

---

## 🎯 Most Likely Scenarios

### Scenario 1: Service in Different Project
- Check "easygoing-cat" project (you have 2 projects)
- Support might have moved it there

### Scenario 2: Service Renamed
- Look for service with name: "web", "service", "main", etc.
- Support might have created with default name

### Scenario 3: Environment Changed
- Check "production" AND "default" environments
- Support might have created in wrong environment

### Scenario 4: Complete Fresh Deploy
- Support deleted everything and told you to redeploy
- Check email for their instructions

---

## 📞 Railway Support Contacts

- **Support Email**: support@railway.app
- **Discord**: https://discord.gg/railway (very responsive!)
- **Twitter**: @Railway (for urgent issues)
- **Docs**: https://docs.railway.app

Discord is usually fastest - Railway team is very active there.

---

**🤖 Generated with Claude Code**
