# Railway Webhook Integration Guide
## Automated Deployment Notifications & Health Checks

This guide explains how to set up Railway webhooks to automatically notify you of deployment status and run health checks after successful deployments.

---

## 🎯 Features

### 1. **Deployment Notifications**
- ✅ **Email**: HTML and plain text deployment notifications
- ✅ **Discord**: Rich embed notifications with color-coded status
- ✅ **Slack**: Block Kit formatted messages
- 📊 Deployment status tracking (Success, Failed, Building, etc.)

### 2. **Automated Health Checks**
- 🏥 Automatic endpoint testing after successful deployments
- ⚡ Response time monitoring
- 📈 Health status reports (Healthy, Degraded, Unhealthy)
- 🔍 Tests critical endpoints:
  - `/api/v1/health` - Core health check
  - `/api/v1/disease/lookup` - Disease lookup API
  - `/api/v1/genes/search` - Gene search API
  - `/docs` - API documentation
  - `/api/v1/literature/search` - Literature search

### 3. **Webhook Event Tracking**
- 📝 Event history and logging
- 🔎 Detailed event inspection
- 📊 Deployment metrics

---

## 🚀 Quick Start

### Step 1: Configure Environment Variables

Add these to your Railway environment variables or `.env` file:

```bash
# Deployment URL (for health checks)
DEPLOYMENT_URL=https://your-app.railway.app

# Email Notifications (Recommended)
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_RECIPIENTS=your-email@example.com,teammate@example.com

# SMTP Settings (for Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use Gmail App Password, not regular password
SMTP_FROM_EMAIL=your-email@gmail.com

# Discord Notifications (Optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL

# Slack Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Step 2: Set Up Gmail App Password (for Email Notifications)

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (if not already enabled)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Create new app password for "Mail"
5. Use the generated password for `SMTP_PASSWORD`

### Step 3: Configure Railway Webhook

1. Go to your Railway project settings
2. Navigate to **Webhooks** section
3. Click **"New Webhook"**
4. Enter webhook endpoint:
   ```
   https://your-app.railway.app/api/v1/webhooks/railway
   ```
5. Select events to monitor:
   - ✅ Success
   - ✅ Failed
   - ✅ Crashed
   - ✅ Building
   - ✅ Deploying
6. Click **"Save Webhook"**

### Step 4: Test the Webhook

Test the webhook endpoint:
```bash
curl -X POST https://your-app.railway.app/api/v1/webhooks/test
```

You should receive a test notification via email (and Discord/Slack if configured).

---

## 📧 Email Notification Setup

### Gmail Configuration

1. **Enable 2-Step Verification**:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Turn on 2-Step Verification

2. **Create App Password**:
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select app: "Mail"
   - Select device: "Other" (enter "AI Nurse Florence")
   - Click "Generate"
   - Copy the 16-character password

3. **Set Environment Variables**:
   ```bash
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # 16-character app password
   SMTP_FROM_EMAIL=your-email@gmail.com
   NOTIFICATION_EMAIL_ENABLED=true
   NOTIFICATION_EMAIL_RECIPIENTS=your-email@gmail.com
   ```

### Other Email Providers

#### Outlook/Office 365
```bash
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

#### Custom SMTP Server
```bash
SMTP_HOST=smtp.yourprovider.com
SMTP_PORT=587  # or 465 for SSL
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

---

## 💬 Discord Notification Setup

1. **Create Discord Webhook**:
   - Go to Discord Server Settings → Integrations → Webhooks
   - Click "New Webhook"
   - Choose channel for notifications
   - Copy webhook URL

2. **Add to Environment**:
   ```bash
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/your-webhook-token
   ```

3. **Test**:
   - Deploy your app or use the test endpoint
   - Check Discord channel for notification

---

## 💼 Slack Notification Setup

1. **Create Slack App**:
   - Go to [Slack API](https://api.slack.com/apps)
   - Click "Create New App" → "From scratch"
   - Name it "AI Nurse Florence" and select workspace

2. **Enable Incoming Webhooks**:
   - Go to "Incoming Webhooks"
   - Toggle "Activate Incoming Webhooks" to On
   - Click "Add New Webhook to Workspace"
   - Select channel and authorize

3. **Add to Environment**:
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```

---

## 🔧 API Endpoints

### Railway Webhook Handler
```http
POST /api/v1/webhooks/railway
Content-Type: application/json

{
  "type": "DEPLOY",
  "status": "SUCCESS",
  "timestamp": "2025-10-02T12:00:00Z",
  "project": {"id": "...", "name": "ai-nurse-florence"},
  "deployment": {"id": "...", "url": "https://..."}
}
```

### Get Webhook Events
```http
GET /api/v1/webhooks/events?limit=50
```

Response:
```json
{
  "total": 10,
  "events": [
    {
      "id": "deployment-123",
      "type": "DEPLOY",
      "status": "SUCCESS",
      "timestamp": "2025-10-02T12:00:00",
      "source": "railway"
    }
  ]
}
```

### Get Event Details
```http
GET /api/v1/webhooks/events/{event_id}
```

### Test Webhook
```http
POST /api/v1/webhooks/test
```

---

## 🏥 Health Check System

### Automatic Health Checks

After a successful deployment, the system automatically tests:

1. **Core Health** (`/api/v1/health`)
   - Timeout: 10s
   - Expected: 200 OK

2. **Disease Lookup** (`/api/v1/disease/lookup?q=diabetes`)
   - Timeout: 15s
   - Tests MedlinePlus integration

3. **Gene Search** (`/api/v1/genes/search?q=BRCA1`)
   - Timeout: 15s
   - Tests myGene.info integration

4. **API Documentation** (`/docs`)
   - Timeout: 10s
   - Verifies Swagger UI accessibility

5. **Literature Search** (`/api/v1/literature/search?q=nursing`)
   - Timeout: 20s
   - Tests PubMed integration

### Health Check Report

Example report structure:
```json
{
  "deployment_id": "abc123",
  "timestamp": "2025-10-02T12:05:00",
  "overall_status": "healthy",
  "checks_passed": 5,
  "checks_failed": 0,
  "checks_total": 5,
  "summary": "All 5 health checks passed",
  "results": [
    {
      "endpoint": "/api/v1/health",
      "status": "passed",
      "status_code": 200,
      "response_time_ms": 45.2,
      "timestamp": "2025-10-02T12:05:00"
    }
  ]
}
```

---

## 📊 Notification Examples

### Email Notification

**Subject**: ✅ AI Nurse Florence Deployment SUCCESS

**Body** (HTML formatted):
- Green header for success, red for failures
- Deployment details (ID, environment, timestamp)
- Clickable deployment URL
- Commit message
- Error details (if failed)

### Discord Notification

Rich embed with:
- Color-coded status (green for success, red for failure)
- Deployment information fields
- Railway branding
- Timestamp

### Slack Notification

Block Kit formatted message with:
- Header with status emoji
- Deployment details in grid format
- Link to deployment
- Error details (if applicable)

---

## 🔍 Troubleshooting

### Email Not Sending

1. **Check Gmail App Password**:
   - Make sure you're using an App Password, not your regular password
   - App Password is 16 characters without spaces

2. **Verify Environment Variables**:
   ```bash
   railway variables
   # Should show:
   # SMTP_USERNAME=your-email@gmail.com
   # SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   # NOTIFICATION_EMAIL_ENABLED=true
   ```

3. **Check Logs**:
   ```bash
   railway logs
   # Look for:
   # "📧 Sending email notifications..."
   # "✅ Email notification sent..."
   ```

4. **Less Secure Apps** (if using old Gmail setup):
   - Gmail may block "less secure apps"
   - Use App Passwords instead

### Discord/Slack Not Receiving

1. **Verify Webhook URL**:
   - Test manually with curl:
   ```bash
   curl -X POST $DISCORD_WEBHOOK_URL \
     -H "Content-Type: application/json" \
     -d '{"content": "Test message"}'
   ```

2. **Check Permissions**:
   - Ensure webhook has permission to post in channel

### Health Checks Failing

1. **Check Deployment URL**:
   ```bash
   # Make sure DEPLOYMENT_URL is set correctly
   echo $DEPLOYMENT_URL
   # Should be: https://your-app.railway.app
   ```

2. **Manual Health Check**:
   ```bash
   curl https://your-app.railway.app/api/v1/health
   ```

3. **Review Logs**:
   ```bash
   railway logs
   # Look for health check results
   ```

---

## 📝 Best Practices

1. **Multiple Recipients**: Add multiple email addresses for team notifications
   ```bash
   NOTIFICATION_EMAIL_RECIPIENTS=dev@company.com,ops@company.com,manager@company.com
   ```

2. **Separate Channels**: Use different Discord/Slack channels for:
   - Production deployments
   - Staging deployments
   - Development deployments

3. **Monitor Health Checks**: Review health check reports to catch degraded performance early

4. **Webhook Security**: Railway webhooks include signature headers for verification (optional)

5. **Event Retention**: Webhook events are stored in memory - consider logging to external service for long-term tracking

---

## 🎓 Next Steps

1. ✅ Configure email notifications (recommended)
2. ✅ Set up Railway webhook
3. ✅ Test with a deployment
4. 📊 Monitor webhook events via `/api/v1/webhooks/events`
5. 🔧 Customize health check endpoints as needed
6. 📈 Add Discord/Slack for real-time team notifications

---

## 🆘 Support

For issues or questions:
1. Check logs: `railway logs`
2. Test webhook endpoint: `POST /api/v1/webhooks/test`
3. Review environment variables: `railway variables`
4. Consult Railway webhook documentation: https://docs.railway.app/reference/webhooks

---

**🤖 Generated with Claude Code**
**AI Nurse Florence - Healthcare AI Assistant**
