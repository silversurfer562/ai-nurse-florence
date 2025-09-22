#!/bin/bash

# 🚂 Railway Deployment Tester
# Usage: ./test_railway_deployment.sh https://your-app.up.railway.app

if [ -z "$1" ]; then
    echo "❌ Please provide your Railway app URL as an argument"
    echo "Usage: ./test_railway_deployment.sh https://your-app.up.railway.app"
    exit 1
fi

RAILWAY_URL="$1"

echo "🔬 TESTING RAILWAY DEPLOYMENT: $RAILWAY_URL"
echo "=============================================="
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Endpoint..."
HEALTH_URL="$RAILWAY_URL/api/v1/health"
echo "URL: $HEALTH_URL"
if command -v curl &> /dev/null; then
    curl -s "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || echo "Health check response (raw):"
    echo ""
else
    echo "ℹ️  Visit: $HEALTH_URL"
    echo "   Expected response: {\"status\": \"ok\"}"
fi
echo ""

# Test 2: API Documentation
echo "2️⃣  API Documentation..."
DOCS_URL="$RAILWAY_URL/docs"
echo "URL: $DOCS_URL"
echo "ℹ️  Open this URL in your browser to see interactive API docs"
echo ""

# Test 3: Disease Lookup
echo "3️⃣  Testing Disease Lookup..."
DISEASE_URL="$RAILWAY_URL/api/v1/disease?q=diabetes"
echo "URL: $DISEASE_URL"
echo "ℹ️  This should return disease information about diabetes"
echo ""

# Test 4: PubMed Search
echo "4️⃣  Testing PubMed Search..."
PUBMED_URL="$RAILWAY_URL/api/v1/pubmed?q=hypertension"
echo "URL: $PUBMED_URL"
echo "ℹ️  This should return medical literature about hypertension"
echo ""

# Test 5: Clinical Trials
echo "5️⃣  Testing Clinical Trials..."
TRIALS_URL="$RAILWAY_URL/api/v1/trials?q=cancer"
echo "URL: $TRIALS_URL"
echo "ℹ️  This should return clinical trials related to cancer"
echo ""

echo "🎉 TEST URLS GENERATED!"
echo "======================="
echo ""
echo "🔍 Quick Browser Tests:"
echo "• Health: $HEALTH_URL"
echo "• Docs:   $DOCS_URL"
echo ""
echo "📝 Copy any URL above and paste in your browser to test!"
echo ""
echo "✅ If health check returns {\"status\": \"ok\"}, your deployment is working!"
