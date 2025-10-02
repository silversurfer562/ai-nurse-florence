# Railway Environment Variables
## Quick Reference for AI Nurse Florence Deployment

Copy and paste these into Railway's environment variables section.

---

## 🚨 Required for Webhook Health Checks

```bash
# Your Railway deployment URL (automatically set by Railway, but can override)
DEPLOYMENT_URL=https://your-app.railway.app
```

---

## 📧 Email Notifications (Recommended)

### Gmail Setup
```bash
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_RECIPIENTS=your-email@example.com,teammate@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
SMTP_FROM_EMAIL=your-email@gmail.com
```

**Gmail App Password Instructions:**
1. Go to https://myaccount.google.com/apppasswords
2. Create password for "Mail" app
3. Copy 16-character password
4. Use as `SMTP_PASSWORD` (no spaces)

### Other Email Providers

**Outlook/Office 365:**
```bash
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

**Custom SMTP:**
```bash
SMTP_HOST=smtp.yourprovider.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

---

## 💬 Discord Notifications (Optional)

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

**Setup:**
1. Server Settings → Integrations → Webhooks
2. New Webhook → Copy URL
3. Paste into Railway

---

## 💼 Slack Notifications (Optional)

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

**Setup:**
1. Go to https://api.slack.com/apps
2. Create App → Incoming Webhooks
3. Add to Workspace → Copy URL
4. Paste into Railway

---

## ⚙️ How to Add in Railway

### Method 1: Via Web UI
1. Open your Railway project
2. Click on your service
3. Go to "Variables" tab
4. Click "New Variable"
5. Add each variable name and value
6. Click "Add" or "Deploy" to apply

### Method 2: Via Railway CLI
```bash
# Set a single variable
railway variables set NOTIFICATION_EMAIL_ENABLED=true

# Set multiple variables
railway variables set SMTP_USERNAME=your-email@gmail.com
railway variables set SMTP_PASSWORD=your-app-password
railway variables set NOTIFICATION_EMAIL_RECIPIENTS=you@example.com

# View all variables
railway variables
```

### Method 3: Bulk Import
Create a `.env.railway` file:
```bash
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_RECIPIENTS=you@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
DEPLOYMENT_URL=https://your-app.railway.app
```

Then import:
```bash
railway variables set --from-file .env.railway
```

---

## 🧪 Testing Configuration

After adding variables, test the webhook system:

```bash
# Via curl
curl -X POST https://your-app.railway.app/api/v1/webhooks/test

# Via Railway CLI (if deployed)
curl -X POST $(railway status --json | jq -r '.deploymentUrl')/api/v1/webhooks/test
```

You should receive test notifications via all configured channels (email, Discord, Slack).

---

## 🔍 Verifying Variables

Check that variables are set correctly:

```bash
# Via Railway CLI
railway variables

# Via API (after deployment)
curl https://your-app.railway.app/api/v1/health
# Check logs to see which notification services are configured
```

---

## 🎯 Minimal Setup (Email Only)

For the quickest setup with just email notifications:

```bash
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_RECIPIENTS=your-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

---

## 📊 Complete Setup (All Notifications)

For full notification coverage:

```bash
# Health Checks
DEPLOYMENT_URL=https://your-app.railway.app

# Email
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_RECIPIENTS=dev@company.com,ops@company.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=notifications@company.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=AI Nurse Florence <notifications@company.com>

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123/token

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T/B/X
```

---

## 🔐 Security Notes

1. **Never commit** `.env` files with real credentials to git
2. **Use App Passwords** for Gmail (not your main password)
3. **Rotate webhook URLs** if compromised
4. **Limit recipients** to team members only
5. **Use Railway secrets** for sensitive values

---

## 📚 Additional Resources

- Full webhook setup guide: `docs/WEBHOOK_SETUP_GUIDE.md`
- Railway documentation: https://docs.railway.app/reference/variables
- Gmail App Passwords: https://myaccount.google.com/apppasswords
- Discord webhooks: https://discord.com/developers/docs/resources/webhook
- Slack webhooks: https://api.slack.com/messaging/webhooks

---

**🤖 Generated with Claude Code**
