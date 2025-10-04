# Production Deployment Checklist
## Complete verification checklist before deploying to production

## 📋 Pre-Deployment Checklist

### ✅ Infrastructure Requirements

#### Compute Resources
- [ ] **CPU**: Minimum 2 cores, recommended 4+ cores
- [ ] **RAM**: Minimum 4GB, recommended 8GB+
- [ ] **Storage**: Minimum 20GB SSD
- [ ] **Network**: Stable internet connection with low latency
- [ ] **Uptime SLA**: 99.9% infrastructure availability

#### Platform Selection
- [ ] **Railway.app** (Recommended for ease)
- [ ] **AWS/GCP/Azure** (For enterprise scale)
- [ ] **Docker Swarm/Kubernetes** (For orchestration)
- [ ] **Dedicated VPS** (For full control)

### ✅ Environment Configuration

#### Critical Environment Variables
```bash
# Verify all are set in production environment
- [ ] OPENAI_API_KEY=sk-proj-xxxxx  # Valid and funded
- [ ] JWT_SECRET_KEY=<64-char-secure-key>  # Generated securely
- [ ] API_BEARER=<32-char-secure-token>  # Generated securely
- [ ] DATABASE_URL=postgresql://...  # Production database
- [ ] REDIS_URL=redis://...  # Production Redis
- [ ] USE_LIVE=1  # Enable live medical APIs
- [ ] NODE_ENV=production
- [ ] PYTHON_ENV=production
- [ ] DEBUG=false
```

#### Security Settings
```bash
- [ ] CORS_ORIGINS=["https://your-domain.com"]  # Restricted origins
- [ ] SECURE_SSL_REDIRECT=true
- [ ] SESSION_COOKIE_SECURE=true
- [ ] CSRF_COOKIE_SECURE=true
- [ ] ALLOWED_HOSTS=your-domain.com
- [ ] ENABLE_SECURITY_HEADERS=true
```

#### Rate Limiting
```bash
- [ ] RATE_LIMIT_PER_MINUTE=100
- [ ] RATE_LIMIT_BURST=150
- [ ] RATE_LIMIT_STORAGE=redis
```

### ✅ Database Setup

#### PostgreSQL Configuration
- [ ] **Version**: PostgreSQL 15+
- [ ] **Connection Pool**: Configured (20-50 connections)
- [ ] **Backup Strategy**: Automated daily backups
- [ ] **Replication**: Read replica for scaling (optional)
- [ ] **SSL**: Enforced connections

#### Database Initialization
```sql
-- Run these before deployment
- [ ] CREATE DATABASE florence_db;
- [ ] CREATE USER florence WITH ENCRYPTED PASSWORD 'secure-password';
- [ ] GRANT ALL PRIVILEGES ON DATABASE florence_db TO florence;
- [ ] Run migrations: alembic upgrade head
```

#### Performance Tuning
```sql
- [ ] ALTER SYSTEM SET shared_buffers = '256MB';
- [ ] ALTER SYSTEM SET effective_cache_size = '1GB';
- [ ] ALTER SYSTEM SET max_connections = '200';
- [ ] ALTER SYSTEM SET checkpoint_completion_target = '0.9';
```

### ✅ Redis Configuration

#### Redis Setup
- [ ] **Version**: Redis 7+
- [ ] **Persistence**: AOF enabled
- [ ] **Memory Policy**: allkeys-lru
- [ ] **Max Memory**: Set appropriate limit
- [ ] **Password**: Strong authentication

#### Redis Configuration
```redis
- [ ] maxmemory 256mb
- [ ] maxmemory-policy allkeys-lru
- [ ] save 900 1 300 10 60 10000
- [ ] requirepass your-redis-password
```

### ✅ Security Verification

#### SSL/TLS Configuration
- [ ] **SSL Certificate**: Valid and not expiring soon
- [ ] **TLS Version**: Minimum TLS 1.2
- [ ] **Cipher Suites**: Modern, secure ciphers only
- [ ] **HSTS**: Enabled with appropriate max-age
- [ ] **Certificate Chain**: Complete and valid

#### API Security
- [ ] **Authentication**: JWT tokens configured
- [ ] **API Keys**: Securely generated and stored
- [ ] **Rate Limiting**: Enabled on all endpoints
- [ ] **Input Validation**: All inputs sanitized
- [ ] **SQL Injection**: Parameterized queries verified

#### Secrets Management
- [ ] **No hardcoded secrets** in code
- [ ] **Environment variables** properly set
- [ ] **Secrets rotation** plan in place
- [ ] **Access logs** configured
- [ ] **Audit trail** enabled

### ✅ External Service Verification

#### Medical API Connectivity
```bash
# Test each service
- [ ] MyDisease.info: curl "https://mydisease.info/v1/query?q=diabetes"
- [ ] PubMed/NCBI: curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=test"
- [ ] ClinicalTrials.gov: curl "https://clinicaltrials.gov/api/v2/studies?query.cond=diabetes"
- [ ] MedlinePlus: curl "https://connect.medlineplus.gov/service?mainSearchCriteria.v.c=250.00"
```

#### OpenAI API
- [ ] **API Key Valid**: Test with simple completion
- [ ] **Billing Active**: Verify account has credits
- [ ] **Rate Limits**: Understand your tier limits
- [ ] **Model Access**: Verify GPT-4 access if needed

#### Optional Services
- [ ] **NCBI API Key**: Set for enhanced PubMed rates
- [ ] **Sentry DSN**: Error tracking configured
- [ ] **Analytics**: Google Analytics or similar

### ✅ Application Testing

#### Functional Testing
```bash
- [ ] Health check: GET /api/v1/health returns 200
- [ ] Disease lookup: GET /api/v1/disease?q=diabetes works
- [ ] PubMed search: GET /api/v1/pubmed?q=test returns results
- [ ] Clinical trials: GET /api/v1/trials?condition=cancer works
- [ ] Treatment wizard: POST /api/v1/wizards/treatment-plan/start
- [ ] SBAR generation: Full workflow tested
```

#### Performance Testing
- [ ] **Response Time**: <2s for cached requests
- [ ] **Concurrent Users**: Test with expected load
- [ ] **Memory Usage**: Monitor for leaks
- [ ] **CPU Usage**: Under 80% at normal load
- [ ] **Database Queries**: Optimized, no N+1 queries

#### Error Handling
- [ ] **404 Pages**: Custom error page
- [ ] **500 Errors**: Graceful error handling
- [ ] **External Service Failures**: Fallback behavior works
- [ ] **Rate Limit Responses**: Clear error messages

### ✅ Monitoring Setup

#### Application Monitoring
- [ ] **Health Checks**: Configured and responding
- [ ] **Metrics Endpoint**: /metrics if Prometheus enabled
- [ ] **Log Aggregation**: Centralized logging setup
- [ ] **Error Tracking**: Sentry or similar configured
- [ ] **Performance Monitoring**: APM tool configured

#### Infrastructure Monitoring
- [ ] **Uptime Monitoring**: External monitor configured
- [ ] **SSL Monitoring**: Certificate expiry alerts
- [ ] **Database Monitoring**: Connection pool, slow queries
- [ ] **Redis Monitoring**: Memory usage, hit rate
- [ ] **Disk Space**: Alerts at 80% usage

#### Alerting
- [ ] **Email Alerts**: Critical errors
- [ ] **Slack/Discord**: Team notifications
- [ ] **PagerDuty**: For on-call (if applicable)
- [ ] **Response Time**: SLA monitoring

### ✅ Compliance & Legal

#### Medical Compliance
- [ ] **No PHI Storage**: Verified in code
- [ ] **Medical Disclaimers**: Present on all endpoints
- [ ] **Educational Use**: Clearly stated
- [ ] **Evidence Sources**: Properly attributed
- [ ] **HIPAA Considerations**: Documented

#### Data Protection
- [ ] **Privacy Policy**: Published and accessible
- [ ] **Terms of Service**: Clear and enforceable
- [ ] **Data Retention**: Policy documented
- [ ] **GDPR Compliance**: If serving EU users
- [ ] **Cookie Policy**: If using cookies

#### Audit Requirements
- [ ] **Access Logs**: Retained appropriately
- [ ] **API Usage Logs**: Tracking implemented
- [ ] **Security Events**: Logged and monitored
- [ ] **Compliance Reports**: Generation capability

### ✅ Backup & Recovery

#### Backup Strategy
- [ ] **Database Backups**: Daily automated
- [ ] **Backup Verification**: Test restore process
- [ ] **Offsite Storage**: Backups stored externally
- [ ] **Retention Policy**: 30-day minimum
- [ ] **Point-in-Time Recovery**: Configured if needed

#### Disaster Recovery
- [ ] **RTO Defined**: Recovery time objective set
- [ ] **RPO Defined**: Recovery point objective set
- [ ] **Failover Plan**: Documented procedure
- [ ] **Contact List**: Emergency contacts ready
- [ ] **Runbook**: Step-by-step recovery guide

### ✅ Performance Optimization

#### Caching Configuration
- [ ] **Redis Connected**: Verify connection
- [ ] **Cache Headers**: Proper TTL values
- [ ] **CDN Setup**: Static assets cached
- [ ] **Database Caching**: Query results cached
- [ ] **API Response Caching**: Configured appropriately

#### Database Optimization
- [ ] **Indexes Created**: On frequently queried columns
- [ ] **Query Analysis**: EXPLAIN on slow queries
- [ ] **Connection Pooling**: Properly configured
- [ ] **Vacuum/Analyze**: Scheduled for PostgreSQL

### ✅ Documentation

#### Technical Documentation
- [ ] **API Documentation**: Complete and accurate
- [ ] **Deployment Guide**: Updated for production
- [ ] **Runbook**: Operational procedures documented
- [ ] **Architecture Diagram**: Current and accurate
- [ ] **Configuration Guide**: All settings documented

#### User Documentation
- [ ] **User Guide**: Updated for latest features
- [ ] **FAQ**: Common issues addressed
- [ ] **Support Contact**: Clear support channels
- [ ] **Video Tutorials**: If applicable

### ✅ Team Readiness

#### Knowledge Transfer
- [ ] **Team Training**: Key personnel trained
- [ ] **On-Call Rotation**: If applicable
- [ ] **Escalation Path**: Defined and communicated
- [ ] **Access Control**: Team has necessary access
- [ ] **Documentation Access**: Team knows where docs are

#### Communication Plan
- [ ] **Launch Announcement**: Prepared
- [ ] **Status Page**: Public status page ready
- [ ] **Support Channels**: Configured and staffed
- [ ] **Feedback Mechanism**: User feedback collection

## 🚀 Deployment Steps

### Final Pre-Deployment

```bash
# 1. Final test in staging
./scripts/test_staging.sh

# 2. Backup current production (if exists)
./scripts/backup_production.sh

# 3. Tag release
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0
```

### Deployment Execution

```bash
# Railway deployment
railway up --environment production

# OR Docker deployment
docker-compose -f docker-compose.prod.yml up -d

# OR Kubernetes deployment
kubectl apply -f k8s/production/
```

### Post-Deployment Verification

```bash
# 1. Health check
curl https://your-domain.com/api/v1/health

# 2. Smoke tests
./scripts/smoke_tests.sh

# 3. Monitor logs
tail -f /var/log/ai-nurse-florence/app.log

# 4. Check metrics
curl https://your-domain.com/metrics
```

## ⚠️ Rollback Plan

### Immediate Rollback Triggers
- [ ] Health check failures
- [ ] Error rate >5%
- [ ] Response time >5s
- [ ] Database connection failures
- [ ] Critical security issues

### Rollback Procedure
```bash
# 1. Switch to previous version
railway rollback  # or equivalent

# 2. Verify rollback
curl https://your-domain.com/api/v1/health

# 3. Investigate issues
grep ERROR /var/log/ai-nurse-florence/*.log

# 4. Create incident report
```

## 📊 Success Criteria

### Launch Day Metrics
- [ ] **Uptime**: >99.9% first 24 hours
- [ ] **Error Rate**: <1%
- [ ] **Response Time**: P95 <2s
- [ ] **Successful API Calls**: >95%
- [ ] **No Critical Bugs**: Zero P0 issues

### Week 1 Targets
- [ ] **User Adoption**: Meet target numbers
- [ ] **API Usage**: Within expected range
- [ ] **Support Tickets**: Manageable volume
- [ ] **Performance**: Meets SLA targets
- [ ] **Cost**: Within budget projections

## 📝 Sign-Off

### Approval Required From:
- [ ] **Technical Lead**: Infrastructure and code ready
- [ ] **Security Team**: Security review complete
- [ ] **Medical Advisor**: Clinical content verified
- [ ] **Legal/Compliance**: Compliance requirements met
- [ ] **Project Manager**: All tasks complete

### Final Confirmation
- [ ] All checklist items verified ✅
- [ ] Team ready for launch ✅
- [ ] Rollback plan tested ✅
- [ ] Monitoring active ✅
- [ ] **GO FOR LAUNCH** 🚀

---

**Checklist Version**: 1.0.0  
**Last Updated**: September 2025  
**Next Review**: Before each major deployment

## Emergency Contacts

| Role | Name | Contact | Escalation |
|------|------|---------|------------|
| Technical Lead | [Name] | [Phone/Email] | Primary |
| DevOps Lead | [Name] | [Phone/Email] | Primary |
| Medical Advisor | [Name] | [Phone/Email] | Secondary |
| Security Team | [Name] | [Phone/Email] | As needed |
| Project Manager | [Name] | [Phone/Email] | Updates |
