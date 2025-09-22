#!/bin/bash
# AI Nurse Florence - Production Validation Script
# Validates the production setup without deploying

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔍 AI Nurse Florence - Production Validation${NC}"
echo "=============================================="

# Check files exist
echo -e "${BLUE}📁 Checking production files...${NC}"

files=(
    "Dockerfile.production"
    "docker-compose.production.yml"
    ".env.production"
    "deploy-production.sh"
    "init-db.sql"
    "nginx/nginx.conf"
)

for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file (missing)${NC}"
    fi
done

# Check environment template
echo -e "\n${BLUE}🔧 Environment Configuration Check${NC}"

if [[ -f ".env.production" ]]; then
    echo -e "${GREEN}✅ .env.production exists${NC}"
    
    # Check for placeholder values that need updating
    placeholders=(
        "CHANGE_ME"
        "your-domain.com"
        "your-openai-api-key"
        "your-email@domain.com"
    )
    
    needs_update=false
    for placeholder in "${placeholders[@]}"; do
        if grep -q "$placeholder" .env.production 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Found placeholder: $placeholder${NC}"
            needs_update=true
        fi
    done
    
    if [[ "$needs_update" == true ]]; then
        echo -e "${YELLOW}📝 Update .env.production with your production values${NC}"
    else
        echo -e "${GREEN}✅ Environment file appears configured${NC}"
    fi
else
    echo -e "${RED}❌ .env.production missing${NC}"
fi

# Check Docker files syntax
echo -e "\n${BLUE}🐳 Docker Configuration Check${NC}"

if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker available${NC}"
    
    # Validate Dockerfile
    if docker build --dry-run -f Dockerfile.production . &>/dev/null; then
        echo -e "${GREEN}✅ Dockerfile.production syntax valid${NC}"
    else
        echo -e "${YELLOW}⚠️  Dockerfile.production may have issues${NC}"
    fi
    
    # Validate docker-compose
    if docker-compose -f docker-compose.production.yml config &>/dev/null; then
        echo -e "${GREEN}✅ docker-compose.production.yml syntax valid${NC}"
    else
        echo -e "${YELLOW}⚠️  docker-compose.production.yml may have issues${NC}"
    fi
    
else
    echo -e "${YELLOW}⚠️  Docker not available for validation${NC}"
fi

# Check application files
echo -e "\n${BLUE}🏥 Application Files Check${NC}"

app_files=(
    "app.py"
    "requirements.txt"
    "start.sh"
    "routers/disease.py"
    "routers/pubmed.py"
    "routers/trials.py"
    "services/openai_client.py"
)

for file in "${app_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file (missing)${NC}"
    fi
done

# Security check
echo -e "\n${BLUE}🔒 Security Check${NC}"

if [[ -f ".env" ]]; then
    echo -e "${YELLOW}⚠️  .env file exists - ensure it's not committed to git${NC}"
fi

if [[ -f ".env.production" ]]; then
    if grep -q "sk-" .env.production 2>/dev/null; then
        echo -e "${YELLOW}⚠️  OpenAI API key found in .env.production - ensure secure handling${NC}"
    fi
fi

# Check for common secrets in git
if git ls-files | xargs grep -l "sk-.*" 2>/dev/null | head -1; then
    echo -e "${RED}❌ Potential secrets found in git-tracked files${NC}"
else
    echo -e "${GREEN}✅ No obvious secrets in git-tracked files${NC}"
fi

echo -e "\n${BLUE}📋 Production Deployment Checklist${NC}"
echo "=================================="
echo "Before deploying to production:"
echo ""
echo "🔧 Configuration:"
echo "  [ ] Update .env.production with real values"
echo "  [ ] Generate secure API_BEARER token"
echo "  [ ] Generate secure JWT_SECRET_KEY"
echo "  [ ] Generate secure DB_PASSWORD"
echo "  [ ] Add your OpenAI API key"
echo "  [ ] Update CORS_ORIGINS for your domain"
echo ""
echo "🌐 Infrastructure:"
echo "  [ ] Domain name configured"
echo "  [ ] SSL certificates obtained"
echo "  [ ] DNS records pointing to server"
echo "  [ ] Firewall configured (ports 80, 443)"
echo ""
echo "🔒 Security:"
echo "  [ ] Server hardened and updated"
echo "  [ ] SSH key authentication configured"
echo "  [ ] Regular backups configured"
echo "  [ ] Monitoring and alerting set up"
echo ""
echo "📊 Testing:"
echo "  [ ] Test deployment in staging environment"
echo "  [ ] Load testing completed"
echo "  [ ] Health checks verified"
echo "  [ ] Medical API integrations tested"
echo ""
echo -e "${GREEN}🚀 Ready to deploy with: ./deploy-production.sh${NC}"
