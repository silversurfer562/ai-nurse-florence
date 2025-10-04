# Fix Railway TLS Certificate Issue

## 🔴 Problem
Your domain `ainurseflorence.com` has a TLS certificate stuck in "Issuing" state, causing:
```
SSL: no alternative certificate subject name matches target host name 'ainurseflorence.com'
```

## ✅ Solution (from Railway Support)

### Step 1: Remove and Re-add Custom Domain

1. Go to Railway dashboard: https://railway.app/project/YOUR_PROJECT
2. Click on your service
3. Go to **"Settings"** tab
4. Scroll to **"Domains"** section
5. Find `ainurseflorence.com`
6. Click **"Remove Domain"** (⚠️ Yes, remove it completely)
7. Wait 30 seconds
8. Click **"Add Domain"**
9. Enter: `ainurseflorence.com`
10. Click **"Add"**

### Step 2: Verify DNS is Correct

Railway will show you DNS records needed. Verify your DNS has:

**Option A: CNAME (Recommended)**
```
ainurseflorence.com  →  CNAME  →  YOUR-APP.up.railway.app
```

**Option B: A Record + AAAA Record**
```
ainurseflorence.com  →  A      →  [Railway IPv4 address]
ainurseflorence.com  →  AAAA   →  [Railway IPv6 address]
```

### Step 3: Wait for Certificate Provisioning

- Railway uses Let's Encrypt for TLS certificates
- Certificate issuance takes **1-5 minutes** typically
- Status will change from "Issuing" → "Active"
- You'll see a green checkmark ✅ when ready

### Step 4: Verify It's Working

```bash
# Test TLS certificate
curl -I https://ainurseflorence.com

# Should return: HTTP/2 200 (no SSL errors)
```

---

## 🔧 If That Doesn't Work

### Alternative 1: Contact Railway Support

The support team can manually trigger certificate reissue:
- Support: https://railway.app/help
- Or via Discord: https://discord.gg/railway

### Alternative 2: Use Railway Subdomain Temporarily

While fixing the custom domain, use the Railway-provided domain:
```
https://ai-nurse-florence-production.up.railway.app
```

This domain has a working certificate and will work immediately.

### Alternative 3: Check DNS Propagation

Verify your DNS is propagated globally:
```bash
# Check DNS from multiple locations
nslookup ainurseflorence.com
dig ainurseflorence.com

# Online tool: https://www.whatsmydns.net/#CNAME/ainurseflorence.com
```

---

## 📊 Common Causes of Certificate Issues

1. **DNS not propagated** - Wait 24-48 hours after DNS change
2. **Wrong DNS records** - Must point to Railway's provided target
3. **Cloudflare proxy enabled** - If using Cloudflare, ensure proxy is OFF for Railway
4. **Previous certificate cached** - Remove and re-add domain to force new cert
5. **Railway API issue** - Rare, but contact support

---

## 🎯 Quick Check: What's Your DNS Provider?

Railway works best with these DNS setups:

**✅ Works Great:**
- Cloudflare (with proxy OFF)
- Namecheap
- GoDaddy
- Google Domains
- AWS Route 53

**⚠️ Requires Special Setup:**
- Cloudflare (proxy ON) - Use Full SSL mode
- Vercel DNS - May conflict

---

## 🔄 Current Status Check

Check your current Railway deployment status:

1. Railway Dashboard → Your Service → Settings → Domains
2. Look for certificate status:
   - ✅ **Active** = Working
   - 🔄 **Issuing** = In progress (should take < 5 min)
   - ❌ **Failed** = Needs re-add

---

## 📧 After Fixing Certificate

Once TLS is working, you can:
1. Set up webhook notifications (SETUP_EMAIL_NOTIFICATIONS.md)
2. Test the site: https://ainurseflorence.com
3. Verify all API endpoints work

---

## 🆘 Emergency Workaround

If you need the app working NOW while fixing the certificate:

### Use Railway's Default Domain:
```bash
# Find your Railway domain
railway status

# It will be something like:
# https://ai-nurse-florence-production-XXXXX.up.railway.app
```

This domain has a valid certificate and works immediately. You can:
- Update webhook URL to use this domain
- Share this URL with users temporarily
- Switch back to custom domain once certificate is fixed

---

**Note**: According to Railway support threads, removing and re-adding the domain forces a fresh certificate issuance, which resolves 90% of stuck certificate issues.

**🤖 Generated with Claude Code**
