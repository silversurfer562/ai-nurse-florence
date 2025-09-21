# 🚀 AI Nurse Florence - Production Deployment Guide

## Quick Start (5 Minutes)

### 1. Prerequisites
- Docker and Docker Compose installed
- OpenAI API key
- Domain name configured (optional but recommended)

### 2. Environment Setup
```bash
# Copy production environment template
cp .env.production .env

# Edit .env file with your OpenAI API key
nano .env  # or vim .env

# Required: Set your OpenAI API key
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
```

### 3. Deploy with Docker
```bash
# Make deployment script executable
chmod +x deploy-production.sh

# Run production deployment
./deploy-production.sh
```

**That's it!** Your API will be available at:
- 🏥 **API**: http://localhost:8000/docs
- ❤️ **Health Check**: http://localhost:8000/api/v1/health
- 📊 **Monitoring**: http://localhost:3000 (Grafana, admin/admin)

## 📋 What Gets Deployed

### Core Services
- **AI Nurse Florence API** (Port 8000)
  - Live medical data integration (MyDisease.info, PubMed, ClinicalTrials.gov)
  - Treatment plan wizard
  - Clinical documentation tools
  - OpenAI-powered AI features

- **PostgreSQL Database** (Port 5432)
  - Persistent data storage
  - User sessions and wizard state

- **Redis Cache** (Port 6379)
  - Medical API response caching
  - Session management
  - Rate limiting

### Monitoring Stack
- **Prometheus** (Port 9090)
  - Metrics collection
  - API performance monitoring

- **Grafana** (Port 3000)
  - Dashboard visualization
  - Real-time monitoring

## 🔧 Production Configuration

### Required Environment Variables
```bash
# Core (Must set these)
OPENAI_API_KEY=sk-proj-your-key-here
USE_LIVE=1

# Optional but recommended
NCBI_API_KEY=your-ncbi-key-here  # Enhanced PubMed rate limits
CORS_ORIGINS=https://your-domain.com
```

### Optional Configuration
```bash
# Security
JWT_SECRET_KEY=your-secure-secret-key
API_BEARER=secure-bearer-token

# Database
POSTGRES_PASSWORD=secure-db-password

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Monitoring
GRAFANA_ADMIN_PASSWORD=secure-grafana-password
```

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│   API Gateway   │────│  AI Nurse API   │
│   (nginx/CF)    │    │   (optional)    │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                              ┌────────────────────────┼────────────────────────┐
                              │                        │                        │
                    ┌─────────▼─────────┐    ┌─────────▼─────────┐    ┌─────────▼─────────┐
                    │   PostgreSQL DB   │    │   Redis Cache     │    │  External APIs    │
                    │   (Port 5432)     │    │   (Port 6379)     │    │  Medical Data     │
                    └───────────────────┘    └───────────────────┘    └───────────────────┘
                              │                        │                        │
                    ┌─────────▼─────────┐    ┌─────────▼─────────┐    ┌─────────▼─────────┐
                    │   Prometheus      │    │    Grafana        │    │   MyDisease.info  │
                    │   (Port 9090)     │    │   (Port 3000)     │    │   PubMed/NCBI     │
                    └───────────────────┘    └───────────────────┘    │   ClinicalTrials  │
                                                                      └───────────────────┘
```

## 🔍 Health Checks & Monitoring

### API Health Check
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-20T17:30:00Z",
  "dependencies": {
    "redis": "connected",
    "database": "connected",
    "external_apis": "available"
  }
}
```

### Live Medical APIs Test
```bash
# Test disease lookup
curl "http://localhost:8000/api/v1/disease?q=diabetes"

# Test PubMed search
curl "http://localhost:8000/api/v1/pubmed?q=hypertension&max_results=5"

# Test clinical trials
curl "http://localhost:8000/api/v1/trials?condition=cancer&max_results=5"
```

## 🛠️ Management Commands

### Service Management
```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Restart API only
docker-compose -f docker-compose.prod.yml restart api

# View logs
docker-compose -f docker-compose.prod.yml logs -f api

# Scale API (multiple instances)
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

### Database Management
```bash
# Connect to PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres psql -U florence -d florence_db

# Backup database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U florence florence_db > backup.sql

# Restore database
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U florence -d florence_db
```

### Cache Management
```bash
# Connect to Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli

# Clear cache
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL

# View cache statistics
docker-compose -f docker-compose.prod.yml exec redis redis-cli INFO
```

## 🌐 Domain & SSL Setup

### 1. Domain Configuration
Point your domain to your server:
```
A record: api.your-domain.com → your-server-ip
```

### 2. Reverse Proxy (nginx)
```nginx
server {
    server_name api.your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. SSL with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d api.your-domain.com
```

## 📈 Scaling & Performance

### Horizontal Scaling
```bash
# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale api=5

# Add load balancer
# Update nginx configuration to proxy to multiple instances
```

### Performance Optimization
- **Redis Caching**: Medical API responses cached for 1 hour
- **Connection Pooling**: PostgreSQL connections pooled
- **Rate Limiting**: 100 requests/minute per IP
- **Gzip Compression**: Automatic response compression

## 🔒 Security Considerations

### API Security
- Rate limiting enabled (100 req/min)
- CORS configured for specific domains
- JWT authentication for protected endpoints
- Request correlation IDs for tracking

### Medical Data Compliance
- No PHI stored (privacy by design)
- Educational use disclaimers on all responses
- Audit logging enabled
- Secure API key management

### Infrastructure Security
- Docker container isolation
- Non-root user in containers
- Health checks for all services
- Automated SSL certificate renewal

## 🆘 Troubleshooting

### Common Issues

#### API Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs api

# Common fixes:
# 1. Check OPENAI_API_KEY is set
# 2. Ensure ports aren't in use
# 3. Verify Docker has enough memory
```

#### Database Connection Errors
```bash
# Check PostgreSQL health
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U florence

# Reset database
docker-compose -f docker-compose.prod.yml down
docker volume rm ai-nurse-florence_postgres-data
docker-compose -f docker-compose.prod.yml up -d
```

#### Redis Connection Issues
```bash
# Check Redis status
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Clear Redis data
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL
```

#### External API Failures
```bash
# Test individual APIs
curl https://mydisease.info/v1/query?q=diabetes
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=diabetes"
curl "https://clinicaltrials.gov/api/v2/studies?query.cond=diabetes"
```

## 📞 Support & Maintenance

### Regular Maintenance
- **Weekly**: Check service health and disk usage
- **Monthly**: Update Docker images and security patches
- **Quarterly**: Review and rotate API keys

### Monitoring Alerts
Set up alerts for:
- API response time > 5 seconds
- Error rate > 5%
- Database connections > 80%
- Disk usage > 85%

### Backup Strategy
- **Database**: Daily automated backups
- **Configuration**: Version controlled in Git
- **Logs**: Centralized logging with retention policy

---

## 🎯 Production Checklist

- [ ] Docker and Docker Compose installed
- [ ] .env file configured with OpenAI API key
- [ ] USE_LIVE=1 set for production medical APIs
- [ ] Domain name configured (if applicable)
- [ ] SSL certificates installed
- [ ] Monitoring dashboards configured
- [ ] Backup strategy implemented
- [ ] Security review completed

**Your AI Nurse Florence API is now production-ready! 🏥✨**
