# Deployment Workflow
## Production vs Development Environments

---

## 🎯 Environment Strategy

### **Production Environment**
- **Purpose**: Stable, production-ready releases
- **Version**: 2.3.0 (current stable)
- **Deployment**: Docker-based via Railway
- **Branch**: `main`
- **Changes**: Only deploy after thorough testing
- **Policy**: Leave alone once stable - minimal changes

### **Development Environment**
- **Purpose**: Active development and testing
- **Version**: 2.4.0-dev (next version)
- **Deployment**: Docker-based via Railway
- **Branch**: `develop` (recommended) or `main`
- **Changes**: Frequent deployments for testing
- **Policy**: Experimental features, breaking changes allowed

---

## 🚀 Deployment Methods

### Method 1: Git Push (Recommended for Production)

**Automatic deployment when code is pushed to GitHub:**

```bash
# Make changes
git add .
git commit -m "feat: your feature description"
git push origin main

# Railway automatically:
# 1. Detects push to main branch
# 2. Uses Dockerfile to build
# 3. Runs npm ci && npm run build in frontend/
# 4. Deploys to production environment
```

**Pros:**
- ✅ Consistent builds from git history
- ✅ Automatic deployment on push
- ✅ Railway uses Dockerfile as specified in railway.toml
- ✅ Build logs preserved in Railway

**Cons:**
- ⏱️ Slower (pulls from GitHub, builds from scratch)

---

### Method 2: Railway CLI Upload (Faster for Testing)

**Upload current directory directly to Railway:**

```bash
# From project root
railway up --detach

# Specify environment explicitly
railway up --detach --environment production
railway up --detach --environment development
```

**Pros:**
- ⚡ Faster deployment (uploads local files)
- 🔧 Good for quick iterations
- 🧪 Test changes before committing

**Cons:**
- ⚠️ Deploys uncommitted changes
- ⚠️ May include local files not in git
- ⚠️ Less reproducible

---

## 📋 Production Deployment Checklist

Before deploying to production:

### 1. **Testing** (Per claude.md)
```bash
# Run comprehensive test suite
source venv/bin/activate
pytest tests/ -v --tb=short

# ALL tests must pass
# Fix any failures before deploying
```

### 2. **Linting** (Per claude.md)
```bash
# Lint edited frontend files
cd frontend && npm run lint

# Or for frontend-react
cd frontend-react && npm run lint

# Fix all linting errors
```

### 3. **Version Update**
```bash
# Update version in src/utils/config.py
APP_VERSION: str = Field(default="2.3.0", ...)

# Update fallback in app.py
APP_VERSION = "2.3.0"
```

### 4. **Documentation**
- Update CHANGELOG (if exists)
- Document new features in code
- Update help content
- Update planning documents

### 5. **Commit & Push**
```bash
git add .
git commit -m "release: v2.3.0 - description of changes"
git tag v2.3.0
git push origin main
git push origin v2.3.0
```

### 6. **Monitor Deployment**
```bash
# Watch Railway deployment
railway logs

# Or via web UI:
# https://railway.com/project/your-project-id
```

### 7. **Post-Deployment Verification**
```bash
# Test health endpoint
curl https://your-app.railway.app/api/v1/health

# Verify version
curl https://your-app.railway.app/api/v1/health | jq '.version'

# Check webhook notifications (if configured)
# You should receive deployment SUCCESS notification
```

---

## 🛠️ Development Environment Workflow

### Setup Development Environment

1. **In Railway Dashboard:**
   - Click "New Environment"
   - Name it "development"
   - Clone from "production"
   - This copies all variables and settings

2. **Link CLI to Development:**
   ```bash
   railway link
   # Select: development environment

   # Or specify explicitly:
   railway environment development
   ```

3. **Verify Configuration:**
   ```bash
   railway status
   # Should show: Environment: development
   ```

### Typical Development Workflow

```bash
# 1. Make changes locally
vim app.py

# 2. Test locally
source venv/bin/activate
python app.py
# Test at http://localhost:8000

# 3. Deploy to development environment
railway up --detach --environment development

# 4. Monitor logs
railway logs --environment development

# 5. Test on development URL
curl https://ai-nurse-florence-dev.railway.app/api/v1/health

# 6. Once satisfied, commit and deploy to production
git add .
git commit -m "feat: new feature"
git push origin main  # Auto-deploys to production
```

---

## 🔄 Version Management Strategy

### Current State: v2.3.0 (Production)
- Stable release
- Webhook integration
- Voice dictation
- Disease search
- Gene lookup
- Document generation

### Next Development: v2.4.0-dev (Development)
```bash
# Update version in development branch/environment
APP_VERSION = "2.4.0-dev"

# Work on new features:
# - New API endpoints
# - UI improvements
# - Performance optimizations
# - Bug fixes

# When ready for production:
# 1. Update version to 2.4.0 (remove -dev)
# 2. Run full test suite
# 3. Merge to main
# 4. Tag release
# 5. Deploy to production
```

---

## 🚦 Railway Environment Configuration

### Production Environment Variables
```bash
# Core
APP_ENV=production
APP_VERSION=2.3.0
DEPLOYMENT_URL=https://ainurseflorence.com

# Webhooks (if configured)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/prod/...
NOTIFICATION_EMAIL_RECIPIENTS=ops@company.com

# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Development Environment Variables
```bash
# Core
APP_ENV=development
APP_VERSION=2.4.0-dev
DEPLOYMENT_URL=https://ai-nurse-florence-dev.railway.app

# Webhooks (separate channels)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/dev/...
NOTIFICATION_EMAIL_RECIPIENTS=dev@company.com

# Development Database (separate from production)
DATABASE_URL=postgresql://dev-db...
REDIS_URL=redis://dev-cache...
```

---

## 📊 Deployment Monitoring

### Via Railway CLI
```bash
# View active deployments
railway status

# Watch logs in real-time
railway logs

# Check deployment history
railway deployments
```

### Via Web UI
1. Go to Railway dashboard
2. Click on service
3. View "Deployments" tab
4. Check:
   - Build logs
   - Deploy logs
   - HTTP logs
   - Metrics

### Via Webhooks (if configured)
- Automatic notifications on:
  - Deployment started
  - Build success/failure
  - Deployment success/failure
- Includes automated health checks
- Sent to Email/Discord/Slack

---

## 🐛 Troubleshooting Deployments

### Deployment Failing?

1. **Check Build Logs**
   ```bash
   railway logs --deployment <deployment-id>
   ```

2. **Verify Dockerfile**
   ```bash
   # Test locally
   docker build -t test-build .
   docker run -p 8000:8000 test-build
   ```

3. **Check Frontend Build**
   ```bash
   cd frontend
   npm ci && npm run build
   # Should complete without errors
   ```

4. **Verify Environment Variables**
   ```bash
   railway variables
   # Check all required vars are set
   ```

### Deployment Skipped?

Railway skips deployment if:
- No file changes detected
- Watch paths configured but no matching files changed
- Deployment already in progress

**Solution:**
```bash
# Force deployment
railway up --detach
```

### Health Check Failing?

1. **Check health endpoint manually**
   ```bash
   curl https://your-app.railway.app/api/v1/health
   ```

2. **Review Railway logs**
   ```bash
   railway logs | grep health
   ```

3. **Increase timeout in railway.toml**
   ```toml
   healthcheckTimeout = 300  # 5 minutes
   ```

---

## 📝 Best Practices

### DO:
- ✅ Test thoroughly before production deployment
- ✅ Use development environment for experiments
- ✅ Tag production releases with version numbers
- ✅ Monitor deployment notifications
- ✅ Keep production stable (v2.3.0)
- ✅ Use semantic versioning (MAJOR.MINOR.PATCH)
- ✅ Document all changes

### DON'T:
- ❌ Deploy untested code to production
- ❌ Skip the test suite
- ❌ Make breaking changes directly in production
- ❌ Deploy with failing health checks
- ❌ Ignore deployment notifications
- ❌ Mix development and production databases

---

## 🎓 Quick Reference Commands

```bash
# Check current environment
railway status

# Switch to production
railway environment production

# Switch to development
railway environment development

# Deploy to current environment
railway up --detach

# Deploy to specific environment
railway up --detach --environment production
railway up --detach --environment development

# View logs
railway logs

# View environment variables
railway variables

# Set environment variable
railway variables set KEY=value

# Check recent deployments
railway deployments
```

---

**Version:** 2.3.0
**Last Updated:** 2025-10-02
**🤖 Generated with Claude Code**
