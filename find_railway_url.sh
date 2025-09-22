#!/bin/bash

# 🚂 Railway Deployment Helper
# Helps you find and test your Railway deployment

echo "🚂 AI NURSE FLORENCE - RAILWAY DEPLOYMENT FINDER"
echo "================================================"
echo ""

echo "🎯 STEP 1: Find Your Railway URL"
echo "--------------------------------"
echo "Go to: https://railway.app/dashboard"
echo "Look for your AI Nurse Florence project"
echo "The URL will look like: https://web-production-XXXX.up.railway.app"
echo ""

echo "🔗 STEP 2: Test Your Railway Deployment"
echo "---------------------------------------"
echo "Once you have the URL, run:"
echo "  ./test_railway_deployment.sh https://your-railway-url.up.railway.app"
echo ""

echo "🌐 STEP 3: Update Domain (When Ready)"
echo "-------------------------------------"
echo "To point ainurseflorence.com to Railway:"
echo "1. Get your Railway deployment URL"
echo "2. In your domain provider's DNS settings:"
echo "   - Add a CNAME record: www -> your-railway-url.up.railway.app"
echo "   - Add an A record: @ -> Railway's IP (check Railway docs)"
echo "3. Wait for DNS propagation (can take up to 48 hours)"
echo ""

echo "📋 STEP 4: Environment Variables Check"
echo "--------------------------------------"
echo "Make sure these are set in Railway dashboard → Variables:"
echo "✅ JWT_SECRET_KEY"
echo "✅ API_BEARER" 
echo "✅ OPENAI_API_KEY"
echo "✅ DB_PASSWORD"
echo "✅ USE_LIVE=true"
echo "✅ NODE_ENV=production"
echo ""

echo "🎉 Once your Railway URL is working, ainurseflorence.com will"
echo "   automatically point to it after DNS propagation!"
echo ""

if [ "$1" = "--help" ]; then
    echo "💡 QUICK COMMANDS:"
    echo "=================="
    echo ""
    echo "Link to Railway project:"
    echo "  railway login"
    echo "  railway link"
    echo "  railway status"
    echo ""
    echo "Deploy to Railway:"
    echo "  git push origin main  # Railway auto-deploys from GitHub"
    echo ""
    echo "Check Railway logs:"
    echo "  railway logs"
    echo ""
fi
