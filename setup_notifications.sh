#!/bin/bash
# Setup Email Notifications for Railway Deployments
# AI Nurse Florence - Webhook Configuration

echo "=========================================="
echo "Email Notification Setup for Railway"
echo "=========================================="
echo ""

# Check if Railway CLI is available
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install with: npm i -g @railway/cli"
    exit 1
fi

echo "📧 This script will configure email notifications for deployments."
echo ""
echo "You'll need:"
echo "  1. Your Gmail address"
echo "  2. A Gmail App Password (16 characters)"
echo ""
echo "To get a Gmail App Password:"
echo "  → Go to: https://myaccount.google.com/apppasswords"
echo "  → Create password for 'Mail'"
echo "  → Copy the 16-character password"
echo ""

read -p "Press Enter to continue or Ctrl+C to exit..."

# Prompt for email configuration
echo ""
echo "Enter your Gmail address:"
read -p "Email: " GMAIL_ADDRESS

echo ""
echo "Enter your Gmail App Password (16 chars, format: xxxx-xxxx-xxxx-xxxx):"
read -s GMAIL_APP_PASSWORD
echo ""

echo ""
echo "Enter recipient email(s) - separate multiple with commas:"
read -p "Recipients: " RECIPIENTS

echo ""
echo "Setting Railway environment variables..."
echo ""

# Set the variables
railway variables set NOTIFICATION_EMAIL_ENABLED=true
railway variables set NOTIFICATION_EMAIL_RECIPIENTS="$RECIPIENTS"
railway variables set SMTP_HOST=smtp.gmail.com
railway variables set SMTP_PORT=587
railway variables set SMTP_USERNAME="$GMAIL_ADDRESS"
railway variables set SMTP_PASSWORD="$GMAIL_APP_PASSWORD"
railway variables set SMTP_FROM_EMAIL="$GMAIL_ADDRESS"

echo ""
echo "✅ Environment variables configured!"
echo ""
echo "Next steps:"
echo "1. Railway will redeploy with new variables"
echo "2. After deployment, set up webhook in Railway dashboard:"
echo ""
echo "   → Go to: Project Settings → Webhooks → New Webhook"
echo "   → URL: https://ainurseflorence.com/api/v1/webhooks/railway"
echo "   → Events: Success, Failed, Crashed, Building, Deploying"
echo "   → Save Webhook"
echo ""
echo "3. Test it:"
echo "   curl -X POST https://ainurseflorence.com/api/v1/webhooks/test"
echo ""
echo "You should receive a test email!"
echo ""
