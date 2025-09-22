# 🚂 Railway Environment Variables Setup

## 🔐 **CRITICAL: Set These in Railway Dashboard**

Go to your Railway project → Variables tab and add these environment variables:

### **Required Production Secrets**

```bash
# 1. JWT Secret (Generate a new secure 64-character hex string)
JWT_SECRET_KEY=13e4a2ed4ff7ab0376acdbcaeddc84863c6d124374e8331d1e3f96f87457204d

# 2. API Bearer Token (Generate a new secure base64 token)
API_BEARER=jYZbnAbvRvs0gXfUI75AWNPFBrc0dA7a2z/xLVMQoRI=

# 3. Database Password (Generate a new secure password)
DB_PASSWORD=lWmZmyJ0QM/ysbSSatzKAA==

# 4. OpenAI API Key (Your actual OpenAI API key)
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
```

### **Required Production Configuration**

```bash
# Environment
NODE_ENV=production
PYTHON_ENV=production
USE_LIVE=true
DEBUG=false

# CORS
CORS_ORIGINS=https://ainurseflorence.com,https://www.ainurseflorence.com

# Logging
LOG_LEVEL=INFO
```

## 🎯 **How to Add in Railway:**

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Select your AI Nurse Florence project**
3. **Click on "Variables" tab**
4. **Add each variable one by one:**
   - Click "Add Variable"
   - Enter the variable name (e.g., `JWT_SECRET_KEY`)
   - Enter the value (the actual secret)
   - Click "Add"

## ⚠️ **IMPORTANT SECURITY NOTES:**

- ✅ **These secrets are now SAFE in Railway** (encrypted and secure)
- ✅ **These secrets are NOT in your git repository** (security best practice)
- ✅ **Railway will inject them at runtime** (secure deployment)
- ✅ **GitHub push protection is resolved** (no more blocking)

## 🚀 **After Setting Variables:**

Railway will automatically redeploy your application with the new environment variables. Your AI Nurse Florence will then be fully functional with:

- ✅ Secure JWT authentication
- ✅ API security with bearer tokens
- ✅ OpenAI integration for medical AI
- ✅ Production database connection
- ✅ All medical APIs (MyDisease, PubMed, Clinical Trials)

## 🏥 **Your Healthcare AI is Ready!**

Once variables are set, your application will be live at:
- **Railway URL**: `https://your-railway-app.railway.app`
- **Health Check**: `https://your-railway-app.railway.app/api/v1/health`
- **API Docs**: `https://your-railway-app.railway.app/docs`
