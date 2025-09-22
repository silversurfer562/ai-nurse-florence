#!/bin/bash
# AI Nurse Florence - Production Deployment Script
# Secure Docker deployment with health checks and validation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"
PROJECT_NAME="ai-nurse-florence"

echo -e "${BLUE}🏥 AI Nurse Florence - Production Deployment${NC}"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available. Please install Docker Compose.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are available${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.production template...${NC}"
    cp .env.production .env
    echo -e "${YELLOW}📝 Please edit .env file with your actual API keys and configuration${NC}"
    echo -e "${YELLOW}   Required: OPENAI_API_KEY${NC}"
    echo -e "${YELLOW}   Optional: NCBI_API_KEY (recommended for better PubMed rate limits)${NC}"
    read -p "Press Enter after updating .env file..."
fi

# Validate required environment variables
source .env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY is not set in .env file${NC}"
    echo -e "${YELLOW}   Please set your OpenAI API key in .env file${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment configuration validated${NC}"

# Build and start services
echo -e "${BLUE}🔨 Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build

echo -e "${BLUE}🚀 Starting production services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${BLUE}🔍 Checking service health...${NC}"

# Check API health
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${RED}❌ API health check failed${NC}"
    echo -e "${YELLOW}📋 Checking API logs...${NC}"
    docker-compose -f docker-compose.prod.yml logs api
    exit 1
fi

# Check Redis
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${RED}❌ Redis health check failed${NC}"
fi

# Check PostgreSQL
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U florence -d florence_db > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is healthy${NC}"
else
    echo -e "${RED}❌ PostgreSQL health check failed${NC}"
fi

# Test live medical APIs
echo -e "${BLUE}🔬 Testing live medical APIs...${NC}"
API_TEST=$(curl -s http://localhost:8000/api/v1/disease?q=diabetes)
if echo "$API_TEST" | grep -q "diabetes" 2>/dev/null; then
    echo -e "${GREEN}✅ Live medical APIs are working${NC}"
else
    echo -e "${YELLOW}⚠️  Live medical APIs may not be responding (check logs)${NC}"
fi

echo ""
echo -e "${GREEN}🎯 Production Deployment Complete! 🎯${NC}"
echo "=================================================="
echo -e "${BLUE}📊 Service URLs:${NC}"
echo -e "   🏥 API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   ❤️  Health Check:      ${GREEN}http://localhost:8000/api/v1/health${NC}"
echo -e "   📈 Prometheus:         ${GREEN}http://localhost:9090${NC}"
echo -e "   📊 Grafana:            ${GREEN}http://localhost:3000${NC} (admin/admin)"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo -e "   Stop services:    ${YELLOW}docker-compose -f docker-compose.prod.yml down${NC}"
echo -e "   View logs:        ${YELLOW}docker-compose -f docker-compose.prod.yml logs -f${NC}"
echo -e "   Restart API:      ${YELLOW}docker-compose -f docker-compose.prod.yml restart api${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "   1. Configure your domain and SSL certificates"
echo -e "   2. Set up reverse proxy (nginx/cloudflare)"
echo -e "   3. Configure monitoring alerts"
echo -e "   4. Set up automated backups"
echo ""
echo -e "${GREEN}🏥 AI Nurse Florence is ready to serve healthcare professionals! 🏥${NC}"
