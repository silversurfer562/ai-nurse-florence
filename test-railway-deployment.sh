#!/bin/bash

# 🧪 AI Nurse Florence - Railway Deployment Test Suite
# Usage: ./test-railway-deployment.sh <railway-app-url>

if [ -z "$1" ]; then
    echo "❌ Usage: $0 <railway-app-url>"
    echo "   Example: $0 https://your-app.railway.app"
    exit 1
fi

RAILWAY_URL="$1"
echo "🚂 TESTING RAILWAY DEPLOYMENT: $RAILWAY_URL"
echo "================================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local url="$1"
    local description="$2"
    local expected_status="$3"
    
    echo -e "\n${BLUE}Testing: $description${NC}"
    echo "URL: $url"
    
    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ SUCCESS: HTTP $status_code${NC}"
        if [ ${#body} -gt 200 ]; then
            echo "Response: $(echo "$body" | head -c 200)..."
        else
            echo "Response: $body"
        fi
    else
        echo -e "${RED}❌ FAILED: HTTP $status_code (expected $expected_status)${NC}"
        echo "Response: $body"
    fi
}

echo -e "\n${YELLOW}🏥 TESTING CORE ENDPOINTS${NC}"
echo "----------------------------------------"

# Test 1: Health Check
test_endpoint "$RAILWAY_URL/api/v1/health" "Health Check" "200"

# Test 2: API Documentation
test_endpoint "$RAILWAY_URL/docs" "API Documentation" "200"

# Test 3: OpenAPI Schema
test_endpoint "$RAILWAY_URL/openapi.json" "OpenAPI Schema" "200"

echo -e "\n${YELLOW}🔬 TESTING MEDICAL ENDPOINTS${NC}"
echo "----------------------------------------"

# Test 4: Disease Information
test_endpoint "$RAILWAY_URL/api/v1/disease/?q=diabetes" "Disease Information (Diabetes)" "200"

# Test 5: PubMed Search
test_endpoint "$RAILWAY_URL/api/v1/pubmed/?q=hypertension" "PubMed Literature Search" "200"

# Test 6: Clinical Trials
test_endpoint "$RAILWAY_URL/api/v1/trials/?q=cancer" "Clinical Trials Search" "200"

# Test 7: Patient Education
test_endpoint "$RAILWAY_URL/api/v1/patient-education/?q=heart+attack" "Patient Education" "200"

# Test 8: Readability Analysis
test_endpoint "$RAILWAY_URL/api/v1/readability/?text=This+is+a+test+sentence+for+medical+readability+analysis" "Readability Analysis" "200"

echo -e "\n${YELLOW}🤖 TESTING AI FEATURES${NC}"
echo "----------------------------------------"

# Test 9: Text Summarization
test_endpoint "$RAILWAY_URL/api/v1/summarize/?text=Medical+text+to+summarize&summary_type=clinical" "AI Text Summarization" "200"

echo -e "\n${YELLOW}📊 DEPLOYMENT SUMMARY${NC}"
echo "========================================"

echo -e "\n${GREEN}🎉 TESTING COMPLETE!${NC}"
echo ""
echo "Your AI Nurse Florence is deployed at: $RAILWAY_URL"
echo ""
echo "Key URLs:"
echo "🏥 Health Check: $RAILWAY_URL/api/v1/health"
echo "📚 API Docs: $RAILWAY_URL/docs"
echo "🔍 Disease Lookup: $RAILWAY_URL/api/v1/disease?q=diabetes"
echo "📖 Literature Search: $RAILWAY_URL/api/v1/pubmed?q=hypertension"
echo "🧪 Clinical Trials: $RAILWAY_URL/api/v1/trials?q=cancer"
echo ""
echo -e "${BLUE}💡 Next Steps:${NC}"
echo "1. Visit the API docs at $RAILWAY_URL/docs"
echo "2. Test interactive endpoints in the docs"
echo "3. Configure your custom domain (ainurseflorence.com)"
echo "4. Share with healthcare professionals!"
echo ""
echo -e "${GREEN}🏥 Your Healthcare AI Assistant is LIVE! 🚀${NC}"
