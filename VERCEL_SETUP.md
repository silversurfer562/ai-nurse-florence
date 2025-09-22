# Vercel Environment Variables Setup Guide

## 🎯 **Quick Setup for Vercel Dashboard**

### **Step 1: Access Vercel Dashboard**
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your `ai-nurse-florence` project
3. Navigate to **Settings** → **Environment Variables**

### **Step 2: Add Production Environment Variables**
Add these variables with your actual values (set Environment to "Production"):

#### **🔐 Required Secrets**
```bash
# OpenAI Integration (Required for AI features)
OPENAI_API_KEY=sk-your-actual-openai-api-key

# Internal API Security
API_BEARER=your-secure-production-bearer-token-32-chars-min

# JWT Authentication (if using auth features)
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-64-chars-recommended
```

#### **🌐 Domain Configuration**
```bash
# CORS Origins (Replace with your actual domains)
CORS_ORIGINS=https://your-frontend-domain.com,https://api.your-domain.com
```

#### **📊 Optional: Enhanced Medical APIs**
```bash
# NCBI API Key (Optional - increases PubMed rate limits from 3/sec to 10/sec)
NCBI_API_KEY=your-ncbi-api-key-from-ncbi-account
```

#### **💾 Optional: Database & Caching**
```bash
# PostgreSQL Database (if using database features)
DATABASE_URL=postgresql://user:password@host:5432/database

# Redis Cache (if using advanced caching)
REDIS_URL=redis://user:password@host:6379/0
```

#### **📈 Optional: Monitoring**
```bash
# Grafana Admin Password (if using monitoring)
GRAFANA_ADMIN_PASSWORD=your-secure-grafana-password
```

---

## 🔧 **Environment Variable Categories**

### **✅ Set in Vercel Dashboard (Sensitive)**
These contain secrets and should NEVER be in code:
- `OPENAI_API_KEY` - OpenAI API key
- `API_BEARER` - Internal API authentication
- `JWT_SECRET_KEY` - JWT signing secret
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string
- `NCBI_API_KEY` - NCBI/PubMed enhanced access
- `CORS_ORIGINS` - Production domain origins
- `GRAFANA_ADMIN_PASSWORD` - Monitoring password

### **📋 Auto-Set by Vercel (No Action Needed)**
- `VERCEL=1` - Indicates Vercel environment
- `VERCEL_URL` - Your app's Vercel URL
- `VERCEL_REGION` - Deployment region

### **⚙️ Handled by Code Defaults (Non-Sensitive)**
These have sensible defaults in the application:
- `USE_LIVE=true` - Enable live APIs in production
- `LOG_LEVEL=INFO` - Logging level
- `RATE_LIMIT_PER_MINUTE=100` - API rate limiting
- `CACHE_TTL_SECONDS=3600` - Cache time-to-live
- `FUNCTION_TIMEOUT=30` - Serverless function timeout
- `FUNCTION_MEMORY=512` - Serverless function memory

---

## 🚀 **Quick Start Checklist**

### **Minimal Setup (Basic Features)**
- [ ] Add `OPENAI_API_KEY` in Vercel Dashboard
- [ ] Add `API_BEARER` in Vercel Dashboard  
- [ ] Update `CORS_ORIGINS` in Vercel Dashboard with your domain
- [ ] Deploy and test at your Vercel URL

### **Enhanced Setup (All Features)**
- [ ] All items from Minimal Setup
- [ ] Add `NCBI_API_KEY` for better PubMed access
- [ ] Add `DATABASE_URL` if using database features
- [ ] Add `REDIS_URL` if using advanced caching
- [ ] Add `JWT_SECRET_KEY` if using authentication

---

## 🔒 **Security Best Practices**

1. **Strong Secrets**: Use 32+ character random strings for tokens
2. **API Key Security**: Never commit API keys to version control
3. **Domain Restriction**: Set CORS_ORIGINS to your exact domains only
4. **Regular Rotation**: Change secrets periodically
5. **Environment Separation**: Use different keys for development/production

---

## 🧪 **Testing Your Setup**

After setting variables in Vercel Dashboard:

1. **Redeploy** your application (Vercel → Deployments → Redeploy)
2. **Test Health Endpoint**: `https://your-app.vercel.app/api/v1/health`
3. **Test Disease Lookup**: `https://your-app.vercel.app/api/v1/disease?q=diabetes`
4. **Check Frontend**: Verify clinical optimizer loads properly

---

## 🆘 **Troubleshooting**

### **Common Issues:**
- **CORS Errors**: Check `CORS_ORIGINS` matches your frontend domain exactly
- **API Failures**: Verify `OPENAI_API_KEY` is set correctly
- **Auth Issues**: Ensure `API_BEARER` is set and used consistently

### **Debugging:**
- Check Vercel Function logs: Vercel Dashboard → Functions → View logs
- Test individual endpoints with curl or browser
- Verify environment variables are showing in Vercel Dashboard

---

## 📝 **Environment File Summary**

| File | Purpose | Contains |
|------|---------|----------|
| `.env.example` | Template for all possible variables | Non-sensitive examples |
| `.env` | Local development | Your local settings |
| `.env.vercel` | Vercel documentation | Instructions for dashboard |
| `.env.production` | Self-hosted production | Non-sensitive production defaults |
| `.env.redis` | Redis-specific settings | Cache configuration |

**Remember**: Sensitive variables go in Vercel Dashboard, not in files!
