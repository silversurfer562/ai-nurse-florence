#!/bin/bash
# Deploy AI Nurse Florence Epic Demo to Railway
# Run this script to deploy the epic-integration-demo branch to Railway

set -e  # Exit on error

echo "🚀 AI Nurse Florence - Epic Demo Deployment to Railway"
echo "======================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found${NC}"
    echo "Install it with: npm install -g @railway/cli"
    echo "Or: curl -fsSL https://railway.app/install.sh | sh"
    exit 1
fi

# Check if logged in
echo -e "${BLUE}🔐 Checking Railway login status...${NC}"
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Railway${NC}"
    echo "Running: railway login"
    railway login
fi

# Verify we're on the correct branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "epic-integration-demo" ]; then
    echo -e "${YELLOW}⚠️  You're on branch: $CURRENT_BRANCH${NC}"
    echo -e "${YELLOW}   Switching to epic-integration-demo...${NC}"
    git checkout epic-integration-demo
fi

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  You have uncommitted changes${NC}"
    echo "Commit them first or stash them:"
    echo "  git add ."
    echo "  git commit -m 'Update Epic demo'"
    echo "  git push origin epic-integration-demo"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ask if user wants to create new project or use existing
echo ""
echo -e "${BLUE}Railway Project Setup${NC}"
echo "1) Create NEW Railway project (recommended for first deployment)"
echo "2) Use EXISTING Railway project"
read -p "Choose option (1 or 2): " PROJECT_OPTION

if [ "$PROJECT_OPTION" == "1" ]; then
    echo ""
    echo -e "${GREEN}📦 Creating new Railway project...${NC}"
    echo ""
    echo "⚠️  This will open your browser for GitHub authentication"
    echo "    Please select:"
    echo "    - Repository: silversurfer562/ai-nurse-florence"
    echo "    - Branch: epic-integration-demo"
    echo ""
    read -p "Press ENTER to continue..."

    railway init

elif [ "$PROJECT_OPTION" == "2" ]; then
    echo ""
    echo -e "${GREEN}🔗 Linking to existing Railway project...${NC}"
    railway link
else
    echo -e "${RED}Invalid option${NC}"
    exit 1
fi

# Set environment variables
echo ""
echo -e "${BLUE}⚙️  Setting environment variables...${NC}"

railway variables set EPIC_MOCK_MODE=true
railway variables set MOCK_FHIR_SERVER_ENABLED=true
railway variables set APP_ENV=production
railway variables set APP_VERSION=2.4.2
railway variables set USE_LIVE_SERVICES=true

echo -e "${GREEN}✅ Environment variables set${NC}"

# Optional: Add OpenAI API key
echo ""
read -p "Do you want to add OpenAI API key for AI features? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your OpenAI API key: " OPENAI_KEY
    railway variables set OPENAI_API_KEY="$OPENAI_KEY"
    railway variables set OPENAI_MODEL=gpt-4o-mini
    echo -e "${GREEN}✅ OpenAI API key added${NC}"
fi

# Deploy
echo ""
echo -e "${GREEN}🚀 Deploying to Railway...${NC}"
echo "This will take 2-3 minutes..."
railway up

# Get deployment URL
echo ""
echo -e "${GREEN}✅ Deployment initiated!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Check deployment status: railway status"
echo "2. View logs: railway logs --tail 100"
echo "3. Get domain: railway domain"
echo ""
echo -e "${YELLOW}⏳ Wait 2-3 minutes for build to complete${NC}"
echo ""
echo "Once deployed, your Epic demo will be at:"
echo "  https://your-app.up.railway.app/static/epic-demo.html"
echo ""
echo "Test endpoints:"
echo "  Health: https://your-app.up.railway.app/api/v1/ehr/health"
echo "  Epic Status: https://your-app.up.railway.app/api/v1/ehr/epic/status"
echo ""
echo -e "${GREEN}🎉 Deployment script complete!${NC}"
