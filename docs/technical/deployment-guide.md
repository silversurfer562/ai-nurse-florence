# Deployment Guide

**Who This Is For**: DevOps engineers, system administrators, and technical leads responsible for deploying and maintaining AI Nurse Florence in production environments. You should have experience with cloud platforms, Docker, and production infrastructure management.

**Prerequisites**:
- Docker and Docker Compose experience
- Understanding of production web application deployment
- Cloud platform account (Railway, AWS, GCP, or Azure)
- Domain name and DNS management access (optional but recommended)
- SSL certificate knowledge (Let's Encrypt or commercial)
- Production PostgreSQL and Redis setup experience

**Time**: 30-45 minutes for initial deployment; 10-15 minutes for subsequent updates.

---

## Table of Contents

- [Deployment Options](#deployment-options)
- [Railway Deployment](#railway-deployment)
- [Docker Deployment](#docker-deployment)
- [Environment Configuration](#environment-configuration)
- [Production Checklist](#production-checklist)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Related Resources](#related-resources)

---

## Deployment Options

AI Nurse Florence can be deployed using several methods:

1. **Railway (Recommended for Quick Start)** - Managed platform with automatic scaling
2. **Docker Compose** - Self-hosted with full control
3. **Kubernetes** - Enterprise-scale deployments
4. **Traditional VPS** - Direct installation on virtual private server

## Railway Deployment

For detailed Railway deployment instructions, see [DEPLOYMENT_QUICK_START.md](../../DEPLOYMENT_QUICK_START.md).

**Quick Steps**:
1. Create Railway account
2. Set environment variables (OPENAI_API_KEY, USE_LIVE=1)
3. Connect GitHub repository
4. Deploy with automatic PostgreSQL and Redis provisioning

## Docker Deployment

For complete Docker-based production deployment, see [DEPLOYMENT_QUICK_START.md](../../DEPLOYMENT_QUICK_START.md).

**Architecture**:
- FastAPI application container
- PostgreSQL 15+ database
- Redis 7+ cache
- Nginx reverse proxy (optional)
- Prometheus + Grafana monitoring (optional)

## Environment Configuration

### Required Variables

```bash
# Core (Required)
OPENAI_API_KEY=sk-proj-your-key-here
USE_LIVE=1

# Database (Auto-configured on Railway)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Cache (Auto-configured on Railway)
REDIS_URL=redis://host:6379
```

### Optional Configuration

```bash
# External APIs (Recommended)
NCBI_API_KEY=your-ncbi-key  # Enhanced PubMed rate limits

# Security
JWT_SECRET_KEY=secure-random-string
API_BEARER=bearer-token

# Performance
RATE_LIMIT_PER_MINUTE=100
CORS_ORIGINS=https://your-domain.com
```

For complete environment variable reference, see [README.md](../../README.md#configuration--environment-variables).

## Production Checklist

- [ ] Environment variables configured
- [ ] OpenAI API key valid and funded
- [ ] USE_LIVE=1 enabled for medical APIs
- [ ] Database migrations applied
- [ ] Redis cache connected
- [ ] Health check endpoint responding
- [ ] SSL certificate installed
- [ ] Domain DNS configured
- [ ] Monitoring dashboards set up
- [ ] Backup strategy implemented
- [ ] Security review completed

## Monitoring and Maintenance

### Health Checks

```bash
# API Health
curl https://your-domain.com/api/v1/health

# Expected response
{"status": "healthy", "dependencies": {...}}
```

### Log Monitoring

Monitor application logs for:
- Error rates >5%
- Response times >5 seconds
- External API failures
- Database connection issues

### Backup Strategy

- **Database**: Daily automated backups with 30-day retention
- **Configuration**: Version controlled in Git
- **Logs**: Centralized logging with retention policy

---

## Related Resources

- [DEPLOYMENT_QUICK_START.md](../../DEPLOYMENT_QUICK_START.md) - Docker deployment with troubleshooting
- [Architecture Overview](./architecture-overview.md) - System design and components
- [API Documentation](./api-documentation.md) - API reference for health checks
- [README.md](../../README.md) - Environment variables and configuration
- [MASTER_DOC.md](../../MASTER_DOC.md) - Complete project documentation
