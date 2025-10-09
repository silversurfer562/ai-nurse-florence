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

---

## 🔧 Troubleshooting

### Common Deployment Issues

#### API Container Won't Start

**Symptom**: Container exits immediately or won't start

**Solutions**:
1. **Check OpenAI API Key**:
   ```bash
   # Verify .env file has valid key
   cat .env | grep OPENAI_API_KEY
   # Key should start with 'sk-proj-' or 'sk-'
   ```

2. **Check Container Logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs api
   # Look for error messages in startup
   ```

3. **Verify Environment Variables**:
   ```bash
   # Ensure USE_LIVE=1 is set
   docker-compose -f docker-compose.prod.yml exec api env | grep USE_LIVE
   ```

4. **Memory Issues**:
   ```bash
   # Increase Docker memory limit to 4GB+
   # Docker Desktop -> Settings -> Resources -> Memory
   ```

#### Database Connection Failures

**Symptom**: API can't connect to PostgreSQL

**Solutions**:
1. **Check PostgreSQL is Running**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps postgres
   # Should show "Up" status
   ```

2. **Test Database Connection**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U florence
   # Should return "accepting connections"
   ```

3. **Reset Database**:
   ```bash
   docker-compose -f docker-compose.prod.yml down
   docker volume rm ai-nurse-florence_postgres-data
   docker-compose -f docker-compose.prod.yml up -d
   ```

#### Redis Connection Issues

**Symptom**: Caching not working or connection errors

**Solutions**:
1. **Verify Redis is Running**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
   # Should return "PONG"
   ```

2. **Clear Redis Cache**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL
   ```

3. **Check Redis Logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs redis
   ```

#### Port Already in Use

**Symptom**: Error binding to port 8000

**Solutions**:
1. **Find Process Using Port**:
   ```bash
   # macOS/Linux
   lsof -i :8000
   # Kill the process
   kill -9 <PID>
   ```

2. **Use Different Port**:
   ```bash
   # Edit docker-compose.prod.yml
   # Change ports: "8001:8000"
   ```

#### External API Timeouts

**Symptom**: Medical data lookups fail or timeout

**Solutions**:
1. **Test External APIs Directly**:
   ```bash
   # Test MyDisease.info
   curl "https://mydisease.info/v1/query?q=diabetes"

   # Test PubMed
   curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=diabetes"

   # Test ClinicalTrials.gov
   curl "https://clinicaltrials.gov/api/v2/studies?query.cond=diabetes"
   ```

2. **Check Network/Firewall**:
   ```bash
   # Ensure outbound HTTPS is allowed
   # Check if behind corporate proxy
   ```

3. **Verify USE_LIVE Setting**:
   ```bash
   # In .env file
   USE_LIVE=1  # Must be set for production
   ```

#### SSL/Certificate Issues

**Symptom**: HTTPS not working or certificate errors

**Solutions**:
1. **Renew Let's Encrypt Certificate**:
   ```bash
   sudo certbot renew
   sudo systemctl reload nginx
   ```

2. **Check Certificate Expiration**:
   ```bash
   sudo certbot certificates
   ```

3. **Test SSL Configuration**:
   ```bash
   curl -I https://api.your-domain.com/api/v1/health
   ```

### Performance Issues

#### Slow Response Times

**Symptoms**: API responses take >5 seconds

**Solutions**:
1. **Check Cache Hit Rate**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec redis redis-cli INFO stats
   # Look for keyspace_hits vs keyspace_misses
   ```

2. **Monitor Resource Usage**:
   ```bash
   docker stats
   # Check CPU and memory usage
   ```

3. **Scale API Instances**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --scale api=3
   ```

#### High Memory Usage

**Symptoms**: Container using >2GB RAM

**Solutions**:
1. **Restart Containers**:
   ```bash
   docker-compose -f docker-compose.prod.yml restart api
   ```

2. **Clear Logs**:
   ```bash
   docker system prune -a --volumes
   ```

3. **Limit Container Memory**:
   ```yaml
   # In docker-compose.prod.yml
   services:
     api:
       deploy:
         resources:
           limits:
             memory: 2G
   ```

### Getting Additional Help

If these solutions don't resolve your issue:

1. **Check Logs**: Always start with `docker-compose logs -f api`
2. **GitHub Issues**: Search existing issues at https://github.com/silversurfer562/ai-nurse-florence/issues
3. **Create Issue**: Include logs, error messages, and environment details
4. **Email Support**: patrickroebuck@pm.me for urgent production issues

---

**Your AI Nurse Florence API is now production-ready! 🏥✨**
