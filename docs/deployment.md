# AI Nurse Florence: Deployment Guide

This guide covers deployment strategies and best practices for the AI Nurse Florence healthcare API.

## 🚀 Deployment Options

### 1. Docker Container (Recommended for Production)

#### Prerequisites
- Docker and Docker Compose
- PostgreSQL database
- Redis instance
- Load balancer (optional)

#### Production Setup
1. **Build Image**
   ```bash
   docker build -t ai-nurse-florence:latest .
   ```

2. **Production Docker Compose**
   ```yaml
   version: '3.8'
   services:
     app:
       image: ai-nurse-florence:latest
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/florence
         - REDIS_URL=redis://redis:6379
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - USE_LIVE=1
         - NCBI_API_KEY=${NCBI_API_KEY}
       depends_on:
         - db
         - redis
       restart: unless-stopped
         
     db:
       image: postgres:15
       environment:
         - POSTGRES_DB=florence
         - POSTGRES_PASSWORD=password
       volumes:
         - postgres_data:/var/lib/postgresql/data
       restart: unless-stopped
         
     redis:
       image: redis:7-alpine
       restart: unless-stopped
       
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - ./ssl:/etc/nginx/ssl
       depends_on:
         - app
       restart: unless-stopped

   volumes:
     postgres_data:
   ```

3. **Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

#### Features
- ✅ Full control over infrastructure
- ✅ Persistent storage
- ✅ Custom scaling
- ✅ Health checks and monitoring
- ❌ Requires server management

### 2. Kubernetes (Enterprise Production)

#### Prerequisites
- Kubernetes cluster
- Helm (optional)
- External database and Redis
- Ingress controller

#### Deployment Manifests
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-nurse-florence
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-nurse-florence
  template:
    metadata:
      labels:
        app: ai-nurse-florence
    spec:
      containers:
      - name: app
        image: ai-nurse-florence:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: florence-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: florence-secrets
              key: openai-api-key
        - name: USE_LIVE
          value: "1"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: ai-nurse-florence-service
spec:
  selector:
    app: ai-nurse-florence
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

#### Features
- ✅ Auto-scaling
- ✅ Rolling updates
- ✅ Health checks
- ✅ Service mesh integration
- ❌ Complex setup and management

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# Core Application
OPENAI_API_KEY=sk-...                    # Required for AI features
USE_LIVE=1                               # Enable live medical APIs

# Database (Production)
DATABASE_URL=postgresql://user:pass@host:5432/db  # PostgreSQL recommended

# Cache (Production)
REDIS_URL=redis://host:6379              # Redis for caching and sessions

# External APIs (Optional but recommended)
NCBI_API_KEY=your_ncbi_key               # Enhanced PubMed rate limits

# Security
JWT_SECRET_KEY=your-secure-secret-key    # For authentication
CORS_ORIGINS=["https://your-frontend.com"]  # Frontend domains

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60                 # Requests per minute per IP

# Monitoring (Optional)
PROMETHEUS_METRICS=true                  # Enable metrics collection
SENTRY_DSN=https://...                   # Error tracking
```

### Development vs Production

#### Development (.env)
```bash
USE_LIVE=1
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite+aiosqlite:///./app.db
REDIS_URL=redis://localhost:6379  # Optional
CORS_ORIGINS=["http://localhost:3000"]
```

#### Production (.env.prod)
```bash
USE_LIVE=1
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@prod-db:5432/florence
REDIS_URL=redis://prod-redis:6379
JWT_SECRET_KEY=complex-production-secret
CORS_ORIGINS=["https://florence-app.com"]
RATE_LIMIT_PER_MINUTE=100
PROMETHEUS_METRICS=true
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints
```bash
# Basic health check
GET /api/v1/health
# Response: {"status": "healthy", "dependencies": {...}}

# Detailed system info
GET /api/v1/health/detailed
# Response: {"status": "healthy", "services": {"redis": "ok", "database": "ok"}}
```

### Prometheus Metrics
Available at `/metrics` when enabled:
- `http_requests_total` - Request count by endpoint
- `http_request_duration_seconds` - Response time histogram
- `external_api_calls_total` - External service calls
- `cache_hits_total` / `cache_misses_total` - Cache performance

### Logging
Structured JSON logging with correlation IDs:
```json
{
  "timestamp": "2025-09-20T16:57:04.327Z",
  "level": "INFO",
  "name": "utils.middleware",
  "message": "Request completed: GET /api/v1/disease - 200",
  "request_id": "15a59298-9f95-40f0-802f-2b3f6169e2a2",
  "duration_ms": 1812
}
```

## 🚦 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] SSL certificates installed (production)
- [ ] Domain names configured
- [ ] Rate limiting configured
- [ ] Monitoring setup (Prometheus, Sentry)

### Live Services Verification
- [ ] `USE_LIVE=1` environment variable set
- [ ] MyDisease.info connectivity test
- [ ] PubMed/NCBI API connectivity test  
- [ ] ClinicalTrials.gov API connectivity test
- [ ] OpenAI API key validated
- [ ] NCBI API key configured (optional but recommended)

### Performance Testing
- [ ] Load testing with realistic traffic
- [ ] Database connection pooling configured
- [ ] Redis caching working
- [ ] Response time targets met (<2s for medical queries)

### Security
- [ ] HTTPS/TLS configured
- [ ] CORS origins restricted
- [ ] Rate limiting active
- [ ] Authentication working
- [ ] Security headers configured
- [ ] API keys secured (not in logs/responses)

### Monitoring
- [ ] Health checks responding
- [ ] Metrics collection working
- [ ] Error tracking configured
- [ ] Log aggregation setup
- [ ] Alerts configured for critical services

### Post-Deployment
- [ ] End-to-end API testing
- [ ] Medical data accuracy verification
- [ ] Performance monitoring
- [ ] Error rate monitoring
- [ ] User feedback collection

## 🔐 Security Considerations

### API Security
- Use HTTPS/TLS in production
- Implement rate limiting per endpoint
- Validate all inputs
- Sanitize medical queries
- Log security events

### Medical Data Compliance
- Ensure no PHI (Personal Health Information) is stored
- Implement audit logging
- Regular security assessments
- Data retention policies
- Privacy policy compliance

### External API Security
- Secure API key storage
- Monitor API usage and costs
- Implement circuit breakers for external services
- Cache responses to reduce external calls
- Fallback strategies for service outages

## 📈 Scaling Strategies

### Horizontal Scaling
- Load balancer configuration
- Multiple FastAPI instances
- Database read replicas
- Redis clustering

### Vertical Scaling
- Increase CPU/memory resources
- Optimize database queries
- Implement connection pooling
- Cache frequently accessed data

### Auto-Scaling
- Kubernetes HPA (Horizontal Pod Autoscaler)
- CloudRun auto-scaling
- Docker Swarm scaling
- Load-based scaling metrics

## 🆘 Troubleshooting

### Common Issues

#### External API Failures
```bash
# Check service connectivity
curl https://mydisease.info/v1/query?q=diabetes
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=diabetes"
curl "https://clinicaltrials.gov/api/v2/studies?query.cond=diabetes"
```

#### Database Connection Issues
```bash
# Test database connection
python -c "
from database import get_db
import asyncio
async def test():
    async for db in get_db():
        print('Database connected successfully')
        break
asyncio.run(test())
"
```

#### Redis Connection Issues
```bash
# Test Redis connection
python -c "
from utils.cache import get_redis_client
client = get_redis_client()
if client:
    print('Redis connected successfully')
else:
    print('Using in-memory cache fallback')
"
```

### Log Analysis
```bash
# Filter by service
docker logs ai-nurse-florence | grep "services.disease_service"

# Filter by request ID
docker logs ai-nurse-florence | grep "15a59298-9f95-40f0-802f-2b3f6169e2a2"

# Monitor error rates
docker logs ai-nurse-florence | grep -E "(ERROR|WARNING|CRITICAL)"
```

## 📞 Support

For deployment support and technical issues:
- Review logs with request correlation IDs
- Check health endpoints for service status
- Monitor external API rate limits and quotas
- Validate environment configuration
- Test individual service components

Healthcare-specific considerations:
- Ensure compliance with local healthcare regulations
- Implement appropriate medical disclaimers
- Regular accuracy reviews of medical content
- User feedback collection and analysis
