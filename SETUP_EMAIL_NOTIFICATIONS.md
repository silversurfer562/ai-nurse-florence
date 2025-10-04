# Email Notification Setup - AI Nurse Florence

## ✅ Quick Setup Instructions

Your Gmail App Password: `whte ggcx ypqm pdvh`

---

## Step 1: Add Environment Variables to Railway

Go to your Railway dashboard and add these variables:

### Railway Dashboard Method (Recommended):
1. Open: https://railway.app/project/YOUR_PROJECT
2. Click on your service (ai-nurse-florence)
3. Go to **"Variables"** tab
4. Click **"New Variable"** for each:

```
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_RECIPIENTS=your-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=whteggcxypqmpdvh
SMTP_FROM_EMAIL=your-email@gmail.com
```

**Important**:
- Replace `your-email@gmail.com` with your actual Gmail address (the one you created the app password for)
- For `NOTIFICATION_EMAIL_RECIPIENTS`, you can add multiple emails separated by commas
- Remove spaces from the password: `whteggcxypqmpdvh` (no spaces)

---

## Step 2: Set Up Railway Webhook

After adding the variables, Railway will redeploy. Then:

1. Go to **Project Settings** → **Webhooks**
2. Click **"New Webhook"**
3. Enter webhook URL:
   ```
   https://ainurseflorence.com/api/v1/webhooks/railway
   ```
4. Select these events:
   - ✅ **SUCCESS** - Deployment succeeded
   - ✅ **FAILED** - Deployment failed
   - ✅ **CRASHED** - Application crashed
   - ✅ **BUILDING** - Build started
   - ✅ **DEPLOYING** - Deployment started
5. Click **"Save"**

---

## Step 3: Test the Webhook

After deployment completes, test it:

```bash
curl -X POST https://ainurseflorence.com/api/v1/webhooks/test
```

You should receive a test email within seconds!

---

## 📧 What You'll Receive

### Successful Deployment Email:
- ✅ Deployment status
- 📊 Health check results
- ⏱️ Response times for all endpoints
- 🔗 Link to your app

### Failed Deployment Email:
- ❌ Failure notification
- 📝 Deployment details
- 🔍 Troubleshooting link

### Building Notification:
- 🔨 Build started
- 📦 Deployment ID

---

## 🎯 Email Recipients

To notify multiple people, use comma-separated emails:

```
NOTIFICATION_EMAIL_RECIPIENTS=you@gmail.com,teammate@company.com,ops@company.com
```

---

## ✅ Verification

After setup, check Railway logs for:
```
✅ Email notifications enabled (recipients: your-email@gmail.com)
```

---

## 🔧 Troubleshooting

**Not receiving emails?**
1. Check spam folder
2. Verify SMTP_PASSWORD has no spaces: `whteggcxypqmpdvh`
3. Check Railway logs for errors
4. Test with: `curl -X POST https://ainurseflorence.com/api/v1/webhooks/test`

**Gmail App Password not working?**
1. Verify 2-Step Verification is enabled on your Google account
2. Regenerate app password at: https://myaccount.google.com/apppasswords
3. Use the new password (16 characters, remove spaces)

---

## 📱 Optional: Discord/Slack Notifications

If you also want Discord or Slack notifications, add:

**Discord:**
```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

**Slack:**
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

**🤖 Generated with Claude Code**
