# AI Nurse Florence - Production Deployment Guide

This guide provides comprehensive instructions for deploying AI Nurse Florence in a production environment using Docker.

## 🏥 Overview

AI Nurse Florence is a healthcare AI assistant providing evidence-based medical information for nurses and healthcare professionals. This production deployment uses Docker containers with PostgreSQL, Redis, and optional Nginx reverse proxy.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended

### Software Requirements
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- OpenSSL (for generating certificates)

### Account Requirements
- OpenAI API account and API key
- Domain name (for production SSL)
- SSL certificates (Let's Encrypt recommended)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/silversurfer562/ai-nurse-florence.git
cd ai-nurse-florence
```

### 2. Configure Environment
```bash
# Copy production environment template
cp .env.example .env.production

# Edit production configuration
nano .env.production
```

### 3. Generate Secure Secrets
```bash
# Generate API Bearer token
openssl rand -base64 32

# Generate JWT secret
openssl rand -base64 64

# Generate database password
openssl rand -base64 24
```

### 4. Deploy
```bash
# Make deployment script executable
chmod +x deploy-production.sh

# Run production deployment
./deploy-production.sh
```

## 🔧 Configuration

### Critical Environment Variables

Update these in `.env.production`:

```bash
# Security tokens (REQUIRED)
API_BEARER=your-secure-bearer-token-here
JWT_SECRET_KEY=your-secure-jwt-secret-here
DB_PASSWORD=your-secure-database-password

# OpenAI API (REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Domain configuration
APP_URL=https://your-domain.com
CORS_ORIGINS=["https://your-domain.com","https://www.your-domain.com"]

# Database
DATABASE_URL=postgresql+asyncpg://florence:your-db-password@postgres:5432/florence_db

# Redis
REDIS_URL=redis://redis:6379/0
```

### SSL Configuration

For production HTTPS:

1. **Obtain SSL certificates** (Let's Encrypt recommended):
```bash
# Using certbot
sudo certbot certonly --standalone -d your-domain.com
```

2. **Copy certificates**:
```bash
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

3. **Update nginx configuration**:
```bash
nano nginx/nginx.conf
# Update server_name to your domain
```

## 🐳 Docker Services

### Production Architecture

```
┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   API Server    │
│  (Port 80/443)  │───▶│   (Port 8000)   │
│  Load Balancer  │    │   FastAPI App   │
└─────────────────┘    └─────────────────┘
                                │
                         ┌──────┴──────┐
                         │             │
                    ┌─────────┐   ┌─────────┐
                    │PostgreSQL│   │  Redis  │
                    │Database │   │ Cache   │
                    └─────────┘   └─────────┘
```

### Service Details

#### API Server
- **Image**: Custom built from `Dockerfile.production`
- **Port**: 8000
- **Health Check**: `/health`
- **Resources**: 1GB RAM limit, 0.5 CPU limit

#### PostgreSQL Database
- **Image**: `postgres:15-alpine`
- **Port**: 5432 (internal)
- **Data**: Persistent volume `florence_postgres_data`
- **Resources**: 512MB RAM limit

#### Redis Cache
- **Image**: `redis:7-alpine`
- **Port**: 6379 (internal)
- **Data**: Persistent volume `florence_redis_data`
- **Resources**: 256MB RAM limit

#### Nginx (Optional)
- **Image**: `nginx:alpine`
- **Ports**: 80, 443
- **Features**: SSL termination, rate limiting, static file serving

## 🔐 Security

### Security Features Enabled

- **HTTPS**: SSL/TLS encryption with modern cipher suites
- **Security Headers**: CSP, HSTS, X-Frame-Options, etc.
- **Rate Limiting**: API and static resource protection
- **Non-root Containers**: All services run as non-root users
- **Network Isolation**: Services communicate via internal network
- **Input Validation**: All API inputs validated with Pydantic
- **Authentication**: JWT tokens and API bearer authentication

### Security Checklist

- [ ] SSL certificates configured and valid
- [ ] Strong passwords for all services
- [ ] Firewall configured (ports 80, 443 only)
- [ ] Regular security updates scheduled
- [ ] Log monitoring configured
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting set up

## 📊 Monitoring & Logging

### Log Locations
```bash
# Application logs
./logs/app.log

# Nginx logs
./logs/nginx/access.log
./logs/nginx/error.log

# Container logs
docker-compose -f docker-compose.production.yml logs -f
```

### Health Monitoring
```bash
# API health check
curl https://your-domain.com/health

# Service status
docker-compose -f docker-compose.production.yml ps

# Resource usage
docker stats
```

### Metrics (Optional)
Enable Prometheus metrics by setting:
```bash
ENABLE_METRICS=true
```

## 🔄 Maintenance

### Regular Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and redeploy
./deploy-production.sh

# Database migrations (if needed)
docker-compose -f docker-compose.production.yml exec api alembic upgrade head
```

### Backup Strategy
```bash
# Database backup
docker-compose -f docker-compose.production.yml exec postgres pg_dump -U florence florence_db > backup.sql

# Volume backup
docker run --rm -v florence_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

### Scaling
```bash
# Scale API servers
docker-compose -f docker-compose.production.yml up -d --scale api=3

# Scale workers
docker-compose -f docker-compose.production.yml up -d --scale worker=2
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs api

# Check environment
docker-compose -f docker-compose.production.yml exec api env

# Restart services
docker-compose -f docker-compose.production.yml restart
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose -f docker-compose.production.yml exec postgres pg_isready -U florence

# Reset database
docker-compose -f docker-compose.production.yml down
docker volume rm florence_postgres_data
docker-compose -f docker-compose.production.yml up -d
```

#### SSL Certificate Issues
```bash
# Test certificate
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Renew Let's Encrypt
sudo certbot renew
```

### Performance Tuning

#### Database Optimization
```sql
-- Add to init-db.sql for large datasets
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = '200';
ALTER SYSTEM SET shared_buffers = '256MB';
```

#### Redis Optimization
```bash
# Add to redis configuration
maxmemory 256mb
maxmemory-policy allkeys-lru
```

## 📱 API Endpoints

### Core Medical Endpoints
- `GET /api/v1/health` - Health check
- `GET /api/v1/disease?q=condition` - Disease information
- `GET /api/v1/pubmed/search?q=query` - Medical literature
- `GET /api/v1/trials/search?condition=query` - Clinical trials
- `POST /api/v1/patient-education` - Patient education materials
- `POST /api/v1/readability/check` - Text readability analysis
- `POST /api/v1/summarize/chat` - AI text summarization

### Documentation
- `/docs` - Interactive API documentation
- `/redoc` - Alternative documentation format

## 🏥 Medical Data Sources

### Integrated APIs
- **MyDisease.info**: Disease and drug information
- **PubMed/NCBI**: Medical literature database
- **ClinicalTrials.gov**: Clinical trial registry
- **OpenAI GPT-4**: AI-powered text analysis and generation

### Data Usage
- All medical data is for **educational purposes only**
- Not intended as medical advice
- Users advised to verify with healthcare providers
- No PHI (Personal Health Information) stored

## 📞 Support

### Getting Help
- **Documentation**: Check this guide and API docs
- **GitHub Issues**: Report bugs and feature requests
- **Health Checks**: Monitor `/health` endpoint
- **Logs**: Check application and container logs

### Reporting Issues
Include:
- Environment details (OS, Docker version)
- Error messages and logs
- Steps to reproduce
- Configuration (sanitized)

---

## 🎯 Success Criteria

Your production deployment is successful when:

- [ ] All health checks pass
- [ ] API endpoints respond correctly
- [ ] SSL certificate is valid
- [ ] Medical data queries return results
- [ ] Documentation is accessible
- [ ] Logs show no critical errors
- [ ] Performance meets requirements

**AI Nurse Florence is now ready to serve healthcare professionals with evidence-based medical information!** 🏥✨
