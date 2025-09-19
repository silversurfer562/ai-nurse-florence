# Notion-GitHub Integration Setup Guide

This guide will help you set up the Notion-GitHub integration for the AI Nurse Florence project, enabling real-time tracking of GitHub repository changes in your Notion workspace.

## Overview

The integration provides:
- **Real-time webhooks**: GitHub events (pushes, PRs, issues) automatically create Notion pages
- **Repository digest**: Daily summaries of all repository activity
- **Structured tracking**: Organized data in Notion for easy filtering and analysis
- **Error handling**: Robust retry logic and comprehensive logging

## Prerequisites

1. **GitHub Repository**: Admin access to configure webhooks
2. **Notion Workspace**: Account with permission to create integrations
3. **Deployment Platform**: Vercel, Railway, or similar with environment variable support

## Step 1: Create Notion Integration

### 1.1 Create a Notion Integration
1. Go to [Notion Developers](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Fill in the details:
   - **Name**: `AI Nurse Florence GitHub Integration`
   - **Logo**: Optional
   - **Associated workspace**: Select your workspace
4. Click "Submit"
5. Copy the **Internal Integration Token** (starts with `secret_`)

### 1.2 Create Notion Database

1. Create a new page in your Notion workspace
2. Add a database with the following properties:

| Property Name | Type | Description |
|---------------|------|-------------|
| **Title** | Title | Event title (auto-generated) |
| **Type** | Select | Event type (Push, Pull Request, Issue, etc.) |
| **Repository** | Rich Text | Repository name |
| **Author** | Rich Text | Person who triggered the event |
| **Action** | Select | Action taken (opened, closed, merged, etc.) |
| **Branch** | Rich Text | Git branch (for pushes) |
| **State** | Select | Current state (open, closed, merged, etc.) |
| **Commit Count** | Number | Number of commits (for pushes) |
| **Review State** | Select | Review status (for PR reviews) |
| **Date** | Date | When the event occurred |
| **URL** | URL | Link to GitHub item |

3. Copy the database ID from the URL:
   ```
   https://notion.so/your-workspace/DATABASE_ID?v=...
   ```

### 1.3 Share Database with Integration
1. Click "Share" on your database page
2. Click "Invite"
3. Search for your integration name
4. Select it and click "Invite"

## Step 2: Configure Environment Variables

Add these environment variables to your deployment platform:

```bash
# Notion Configuration
NOTION_TOKEN=secret_your_notion_integration_token
NOTION_DATABASE_ID=your_database_id_here
ENABLE_NOTION_SYNC=true

# GitHub Webhook Configuration  
GITHUB_WEBHOOK_SECRET=your_secure_webhook_secret

# Optional: Retry Configuration
RETRY_ATTEMPTS=3
RETRY_DELAY=1
```

### For Vercel:
1. Go to your project dashboard
2. Navigate to Settings → Environment Variables
3. Add each variable for Production environment
4. Redeploy your application

### For Railway:
1. Go to your project dashboard
2. Navigate to Variables tab
3. Add each variable
4. Railway will auto-redeploy

## Step 3: Configure GitHub Webhook

### 3.1 Set Up Webhook
1. Go to your GitHub repository
2. Navigate to Settings → Webhooks
3. Click "Add webhook"
4. Configure:
   - **Payload URL**: `https://your-domain.com/webhooks/github`
   - **Content type**: `application/json`
   - **Secret**: Use the same value as `GITHUB_WEBHOOK_SECRET`
   - **SSL verification**: Enable
   - **Events**: Select individual events:
     - ✅ Pushes
     - ✅ Pull requests
     - ✅ Issues
     - ✅ Issue comments
     - ✅ Pull request reviews
     - ✅ Pull request review comments

5. Click "Add webhook"

### 3.2 Test Webhook
1. GitHub will send a ping event to test the webhook
2. Check your application logs for successful receipt
3. Verify the webhook health endpoint: `https://your-domain.com/webhooks/health`

## Step 4: Enable Repository Digest (Optional)

The repository already includes a GitHub Action for daily/push-based repository summaries.

### 4.1 Enable Notion Integration in GitHub Actions
1. Go to your repository Settings → Secrets and variables → Actions
2. Add repository variables:
   - `ENABLE_NOTION`: Set to `1`
3. Add repository secrets:
   - `NOTION_TOKEN`: Your Notion integration token
   - `NOTION_DATABASE_ID`: Your database ID

### 4.2 Test the Workflow
1. Go to Actions tab in your repository
2. Find "Repo Digest" workflow
3. Click "Run workflow" to test manually
4. Check if a new page appears in your Notion database

## Step 5: Verification and Testing

### 5.1 Test Webhook Health
Visit: `https://your-domain.com/webhooks/health`

Expected response:
```json
{
  "status": "healthy",
  "configuration": {
    "webhook_secret": true,
    "notion_token": true,
    "notion_database_id": true
  },
  "notion_connection": "connected",
  "webhook_url": "/webhooks/github"
}
```

### 5.2 Test Integration
1. Create a test issue in your repository
2. Create a test pull request
3. Push a commit to a branch
4. Check your Notion database for new entries

### 5.3 Monitor Logs
Check your application logs for:
- `"Received GitHub webhook"` - Confirms webhook receipt
- `"Created Notion page"` - Confirms successful processing
- Any error messages for troubleshooting

## Troubleshooting

### Common Issues

#### 1. Webhook Returns 503 Error
**Cause**: Missing configuration
**Solution**: Verify all environment variables are set correctly

#### 2. "Invalid signature" Error
**Cause**: Webhook secret mismatch
**Solution**: Ensure `GITHUB_WEBHOOK_SECRET` matches GitHub webhook configuration

#### 3. Notion API Errors
**Cause**: Permission issues or invalid database structure
**Solution**: 
- Verify integration has access to database
- Check database property types match expected schema

#### 4. Pages Not Created
**Cause**: Background task failures
**Solution**: Check application logs for detailed error messages

### Debug Commands

```bash
# Test Notion connection
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Notion-Version: 2022-06-28" \
     https://api.notion.com/v1/databases/YOUR_DATABASE_ID

# Test webhook endpoint
curl -X POST https://your-domain.com/webhooks/health
```

## Advanced Configuration

### Custom Event Filtering
Modify `routers/webhooks.py` to filter specific events:

```python
# Only process certain actions
if event_type == "pull_request" and data.get("action") not in ["opened", "closed", "merged"]:
    return  # Skip this event
```

### Custom Page Properties
Modify `services/notion_service.py` to add custom properties:

```python
properties["Custom Field"] = {
    "rich_text": self._create_rich_text("custom value")
}
```

### Webhook Security
The integration includes HMAC signature verification for security. The webhook secret should be:
- At least 20 characters long
- Include numbers, letters, and special characters
- Kept secure and rotated periodically

## Support

For issues or questions:
1. Check application logs first
2. Verify configuration using health endpoint
3. Test individual components (Notion API, webhook receipt)
4. Create an issue in the repository with detailed error logs

## Example Notion Database Template

You can duplicate this database template: [Coming Soon]

Or create manually with the properties listed in Step 1.2.