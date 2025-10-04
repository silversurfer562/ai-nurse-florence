# Add Email Notification Variables to Railway

## Current Status
✅ You have 14 environment variables already configured
📧 Need to add 7 more for email notifications

---

## Variables to Add

Go to Railway Dashboard → Your Service → **Variables** tab → Click **"New Variable"** for each:

### 1. Enable Email Notifications
```
NOTIFICATION_EMAIL_ENABLED=true
```

### 2. Recipients (Your Email)
```
NOTIFICATION_EMAIL_RECIPIENTS=your-email@gmail.com
```
*Replace `your-email@gmail.com` with your actual Gmail address*
*For multiple recipients, use commas: `email1@gmail.com,email2@gmail.com`*

### 3. SMTP Host
```
SMTP_HOST=smtp.gmail.com
```

### 4. SMTP Port
```
SMTP_PORT=587
```

### 5. SMTP Username (Same as Your Gmail)
```
SMTP_USERNAME=your-email@gmail.com
```
*Replace with your actual Gmail address*

### 6. SMTP Password (Gmail App Password)
```
SMTP_PASSWORD=whteggcxypqmpdvh
```
*This is your Gmail App Password (no spaces)*

### 7. From Email (Same as Your Gmail)
```
SMTP_FROM_EMAIL=your-email@gmail.com
```
*Replace with your actual Gmail address*

---

## Quick Copy-Paste (Replace YOUR-EMAIL)

For faster entry, here's the format Railway accepts:

```
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_RECIPIENTS=YOUR-EMAIL@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=YOUR-EMAIL@gmail.com
SMTP_PASSWORD=whteggcxypqmpdvh
SMTP_FROM_EMAIL=YOUR-EMAIL@gmail.com
```

**Don't forget to replace `YOUR-EMAIL` with your actual Gmail address!**

---

## After Adding Variables

Railway will automatically redeploy your service when you add environment variables.

### Wait for Redeploy (2-3 minutes)
Watch the Deployments tab to see when it completes.

### Test Email Notifications
Once deployed, test it:
```bash
curl -X POST https://ainurseflorence.com/api/v1/webhooks/test
```

You should receive a test email within seconds!

---

## What You'll Receive

### ✅ Successful Deployment
- Email subject: "✅ Deployment Successful - AI Nurse Florence"
- Contains: Health check results, response times, deployment ID
- Color-coded status indicators

### ❌ Failed Deployment
- Email subject: "❌ Deployment Failed - AI Nurse Florence"
- Contains: Error details, deployment ID, timestamp

### 🔨 Build Started
- Email subject: "🔨 Build Started - AI Nurse Florence"
- Contains: Deployment ID, timestamp

---

## Troubleshooting

### Not Receiving Emails?

1. **Check spam folder** - First deployment emails sometimes go to spam
2. **Verify password** - Must be `whteggcxypqmpdvh` (no spaces)
3. **Check Railway logs** - Look for "Email notifications enabled"
4. **Gmail App Password** - Verify it's still valid at https://myaccount.google.com/apppasswords

### Need New Gmail App Password?

1. Go to: https://myaccount.google.com/apppasswords
2. Select: "Mail" app
3. Generate new password
4. Copy the 16-character password (remove spaces)
5. Update `SMTP_PASSWORD` in Railway

---

**Total Variables After Setup:** 21 (14 existing + 7 new)

**🤖 Generated with Claude Code**
