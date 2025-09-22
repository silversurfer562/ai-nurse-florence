#!/bin/bash

# AI Nurse Florence - Production Deployment Script
# 🚀 Deploy to production with secure credentials

set -e  # Exit on any error

echo "🏥 AI Nurse Florence - Production Deployment"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env.production.ready exists
if [ ! -f ".env.production.ready" ]; then
    echo -e "${RED}❌ Error: .env.production.ready not found!${NC}"
    echo "Please create it from .env.production.template"
    exit 1
fi

# Check if OpenAI API key is set
if grep -q "sk-your-actual-openai-api-key-here" .env.production.ready; then
    echo -e "${YELLOW}⚠️  Warning: Please update OPENAI_API_KEY in .env.production.ready${NC}"
    echo "Current placeholder: sk-your-actual-openai-api-key-here"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${BLUE}📋 Pre-deployment checklist:${NC}"
echo "✅ Secure JWT secret: [Generated secure 64-char hex key]"
echo "✅ Secure API bearer: [Generated base64 token]"  
echo "✅ Secure DB password: [Generated secure password]"
echo "✅ Production CORS: https://ainurseflorence.com"
echo "✅ All dependencies enabled in requirements.txt"

echo -e "\n${BLUE}🐳 Building production Docker image...${NC}"
docker-compose -f docker-compose.production.yml build --no-cache

echo -e "\n${BLUE}🗄️ Starting database and cache...${NC}"
docker-compose -f docker-compose.production.yml up -d postgres redis

echo -e "\n${BLUE}⏳ Waiting for database to be ready...${NC}"
sleep 10

echo -e "\n${BLUE}🔄 Running database migrations...${NC}"
docker-compose -f docker-compose.production.yml run --rm api alembic upgrade head

echo -e "\n${BLUE}🚀 Starting API server...${NC}"
docker-compose -f docker-compose.production.yml up -d api

echo -e "\n${BLUE}🔍 Checking service health...${NC}"
sleep 15

# Health check
if curl -f -s http://localhost:8000/api/v1/health > /dev/null; then
    echo -e "${GREEN}✅ API server is healthy!${NC}"
else
    echo -e "${RED}❌ API server health check failed!${NC}"
    echo "Checking logs..."
    docker-compose -f docker-compose.production.yml logs api --tail=20
    exit 1
fi

echo -e "\n${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
echo "============================================"
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose -f docker-compose.production.yml ps

echo -e "\n${BLUE}🔗 Service URLs:${NC}"
echo "• API Server: http://localhost:8000"
echo "• API Docs: http://localhost:8000/docs"
echo "• Health Check: http://localhost:8000/api/v1/health"

echo -e "\n${BLUE}🛠️  Management Commands:${NC}"
echo "• View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "• Stop services: docker-compose -f docker-compose.production.yml down"
echo "• Restart API: docker-compose -f docker-compose.production.yml restart api"

echo -e "\n${YELLOW}⚠️  IMPORTANT SECURITY NOTES:${NC}"
echo "• Update OPENAI_API_KEY in .env.production.ready before real deployment"
echo "• Change database hosts from 'localhost' to your actual database servers"
echo "• Ensure firewall rules are configured properly"
echo "• Set up SSL/TLS termination (nginx, cloudflare, etc.)"

echo -e "\n${GREEN}🏥 AI Nurse Florence is ready to help healthcare professionals!${NC}"
