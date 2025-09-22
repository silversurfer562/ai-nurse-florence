#!/bin/bash
# Auto-test script to verify GitHub Pages has updated with live data

echo "=== GitHub Pages Update Test - $(date) ==="
echo ""

echo "🔍 Checking if GitHub Pages has the latest API URL..."
if curl -s "https://silversurfer562.github.io/ai-nurse-florence/api-test.html" | grep -q "ai-nurse-florence.vercel.app"; then
    echo "✅ GitHub Pages has the correct API URL"
    
    echo ""
    echo "🧪 Testing live data from GitHub Pages frontend..."
    
    # Test the health endpoint through the frontend
    echo "Testing health endpoint..."
    curl -s "https://ai-nurse-florence.vercel.app/api/v1/health" | jq -r '.version // "No version found"'
    
    echo ""
    echo "Testing disease data (diabetes)..."
    DIABETES_RESULT=$(curl -s "https://ai-nurse-florence.vercel.app/api/v1/disease?q=diabetes" | jq -r '.summary // "No summary found"')
    if [[ "$DIABETES_RESULT" == *"Medical Definition"* ]] || [[ "$DIABETES_RESULT" == *"mydisease"* ]]; then
        echo "✅ LIVE DATA CONFIRMED: $DIABETES_RESULT"
    else
        echo "❌ Still showing demo data: $DIABETES_RESULT"
    fi
    
    echo ""
    echo "Testing disease data (cancer)..."
    CANCER_RESULT=$(curl -s "https://ai-nurse-florence.vercel.app/api/v1/disease?q=cancer" | jq -r '.summary // "No summary found"')
    if [[ "$CANCER_RESULT" == *"Medical Definition"* ]] || [[ "$CANCER_RESULT" == *"mydisease"* ]]; then
        echo "✅ LIVE DATA CONFIRMED: $CANCER_RESULT"
    else
        echo "❌ Still showing demo data: $CANCER_RESULT"
    fi
    
    echo ""
    echo "🌐 GitHub Pages frontend test:"
    echo "Visit: https://silversurfer562.github.io/ai-nurse-florence/api-test.html"
    echo "The page should now show live medical data with MyDisease.info references!"
    
else
    echo "❌ GitHub Pages still has old version - waiting for deployment..."
    echo "Check again in a few more minutes."
fi

echo ""
echo "=== Test completed at $(date) ==="
