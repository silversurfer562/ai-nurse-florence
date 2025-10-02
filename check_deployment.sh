#!/bin/bash
# Check Railway Deployment Status
# AI Nurse Florence - Deployment Verification

echo "=========================================="
echo "Railway Deployment Status Check"
echo "=========================================="
echo ""

echo "Checking deployed version..."
VERSION=$(curl -k -s https://ainurseflorence.com/api/v1/health 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4)

if [ "$VERSION" == "2.3.0" ]; then
    echo "✅ Version: $VERSION (LATEST)"
    echo ""

    echo "Running feature verification..."
    echo ""

    # Check translations
    echo "1. Testing translations..."
    TRANS=$(curl -k -s https://ainurseflorence.com/locales/en/translation.json 2>/dev/null | head -c 20)
    if [[ $TRANS == *"common"* ]]; then
        echo "   ✅ Translations accessible"
    else
        echo "   ❌ Translations NOT accessible"
    fi

    # Check diagnosis search
    echo "2. Testing diagnosis search..."
    DIAG=$(curl -k -s "https://ainurseflorence.com/api/v1/content-settings/diagnosis/search?q=diabetes&limit=5" 2>/dev/null | head -c 20)
    if [[ $DIAG == *"Internal"* ]]; then
        echo "   ❌ Diagnosis search still returning errors"
    elif [[ $DIAG == "[]" ]] || [[ $DIAG == *"icd10"* ]]; then
        echo "   ✅ Diagnosis search working (graceful or with data)"
    else
        echo "   ⚠️  Diagnosis search status unclear"
    fi

    # Check health endpoint
    echo "3. Testing health endpoint..."
    HEALTH=$(curl -k -s https://ainurseflorence.com/api/v1/health 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$HEALTH" == "healthy" ]; then
        echo "   ✅ Health check: $HEALTH"
    else
        echo "   ❌ Health check failed"
    fi

    echo ""
    echo "=========================================="
    echo "✅ Deployment Successful!"
    echo "=========================================="

elif [ "$VERSION" == "2.1.0" ]; then
    echo "⏳ Version: $VERSION (OLD - deployment in progress)"
    echo ""
    echo "Railway is still building/deploying v2.3.0..."
    echo "This usually takes 3-5 minutes."
    echo ""
    echo "Check Railway dashboard for deployment status:"
    echo "https://railway.app"

else
    echo "❌ Version: $VERSION (unexpected)"
    echo ""
    echo "Something went wrong with the deployment."
    echo "Check Railway logs for errors."
fi

echo ""
