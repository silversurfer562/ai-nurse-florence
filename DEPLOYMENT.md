# 🏥 AI Nurse Florence - Production Deployment Guide

This guide will help you deploy AI Nurse Florence to production with live medical data connections.

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites
```bash
# Ensure you have Docker and Docker Compose installed
docker --version
docker-compose --version
```

### 2. Configuration
```bash
# Copy the production environment template
cp .env.production.live .env

# Edit the configuration (see below for required changes)
nano .env
```

### 3. Deploy
```bash
# Make deployment script executable and run
chmod +x deploy.sh
./deploy.sh deploy
```

That's it! Your production instance will be available at `http://localhost:8000`

## 🔧 Required Configuration

### Critical Settings to Update in `.env`:

1. **API Keys** (REQUIRED for live data):
   ```bash
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   NCBI_API_KEY=your-ncbi-api-key-here
   ```

2. **Security Tokens** (REQUIRED):
   ```bash
   # Generate with: openssl rand -hex 32
   API_BEARER=your-64-character-secure-token
   JWT_SECRET_KEY=your-64-character-secure-token
   ```

3. **Domain Configuration**:
   ```bash
   APP_BASE_URL=https://your-domain.com
   CORS_ORIGINS=https://your-domain.com
   ```

4. **Enable Live Data**:
   ```bash
   USE_LIVE=1
   USE_LIVE_APIS=true
   ```

## 🌐 Live Data Sources

When properly configured, your deployment will connect to:

- **📚 PubMed/NCBI**: Medical literature and research papers
- **🏥 MyDisease.info**: Comprehensive disease information
- **📖 MedlinePlus**: Patient-friendly health information
- **🔬 ClinicalTrials.gov**: Current clinical trial data
- **🤖 OpenAI GPT-4**: AI-powered analysis and summaries

## 🛠️ Deployment Commands

```bash
# Deploy full stack
./deploy.sh deploy

# Check status
./deploy.sh status

# View logs
./deploy.sh logs

# Test deployment
./deploy.sh test

# Stop services
./deploy.sh stop

# Restart services
./deploy.sh restart
```

## 📊 Available Services

After deployment, you'll have access to:

| Service | URL | Purpose |
|---------|-----|---------|
| **API** | `http://localhost:8000` | Main application |
| **Docs** | `http://localhost:8000/docs` | Interactive API documentation |
| **Health** | `http://localhost:8000/api/v1/health` | Health check endpoint |
| **Grafana** | `http://localhost:3000` | Monitoring dashboard |
| **Prometheus** | `http://localhost:9090` | Metrics collection |

## 🔍 API Endpoints

### Core Endpoints with Live Data:

```bash
# Disease information lookup
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/disease/lookup?q=diabetes"

# Medical literature search
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/pubmed/search?q=heart+disease&limit=10"

# Clinical trials search
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/trials/search?condition=cancer&location=New+York"

# Patient education generation
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"diabetes management","reading_level":"elementary"}' \
  "http://localhost:8000/api/v1/education/generate"
```

## 🏗️ Production Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│  AI Nurse API   │────│   PostgreSQL    │
│   (Optional)    │    │   (FastAPI)     │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Redis Cache    │    │  Celery Worker  │
                       │  (Background)   │    │  (Background)   │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Prometheus    │    │    Grafana      │
                       │   (Metrics)     │    │  (Dashboard)    │
                       └─────────────────┘    └─────────────────┘
```

## 🌍 Cloud Deployment Options

### Railway (Recommended)
```bash
# Deploy to Railway
railway login
railway init
railway up
```

### Heroku
```bash
# Deploy to Heroku
heroku create your-app-name
heroku addons:create heroku-postgresql
heroku addons:create heroku-redis
git push heroku main
```

### AWS/Docker
```bash
# Build and push to registry
docker build -t your-registry/ai-nurse-florence .
docker push your-registry/ai-nurse-florence
```

## 🛡️ Security Checklist

- [ ] Generated secure API bearer tokens
- [ ] Configured HTTPS/SSL certificates
- [ ] Set strong database passwords
- [ ] Enabled rate limiting
- [ ] Configured CORS for your domain
- [ ] Set up monitoring alerts
- [ ] Enabled security headers
- [ ] Database backups configured

## 📈 Monitoring & Maintenance

### Health Monitoring
```bash
# Check system health
curl http://localhost:8000/api/v1/health

# View detailed metrics
curl http://localhost:9090/metrics
```

### Log Management
```bash
# View application logs
docker-compose logs -f api

# View worker logs
docker-compose logs -f worker

# View database logs
docker-compose logs -f postgres
```

### Performance Optimization
- **Redis Caching**: Automatically caches API responses for 30 minutes
- **Rate Limiting**: Prevents API abuse (120 req/min default)
- **Connection Pooling**: Efficient database connections
- **Background Jobs**: Celery handles long-running tasks

## 🔧 Troubleshooting

### Common Issues:

1. **OpenAI API Errors**:
   ```bash
   # Check API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
   ```

2. **Database Connection Issues**:
   ```bash
   # Test database connection
   docker-compose exec postgres pg_isready -U florence
   ```

3. **Redis Connection Issues**:
   ```bash
   # Test Redis connection
   docker-compose exec redis redis-cli ping
   ```

4. **External API Issues**:
   ```bash
   # Test PubMed API
   curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=diabetes&retmode=json"
   ```

### Getting Help:
- Check logs: `./deploy.sh logs`
- Run tests: `./deploy.sh test`
- Check status: `./deploy.sh status`
- View documentation: `http://localhost:8000/docs`

## 📝 API Keys Setup Guide

### 1. OpenAI API Key
1. Go to https://platform.openai.com/
2. Create account or sign in
3. Navigate to API Keys section
4. Create new key and copy it
5. Add to `.env`: `OPENAI_API_KEY=sk-...`

### 2. NCBI API Key (Optional but Recommended)
1. Go to https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
2. Follow the registration process
3. Add to `.env`: `NCBI_API_KEY=your-key`

### 3. FDA API Key (Optional)
1. Go to https://open.fda.gov/api/
2. Register for an API key
3. Add to `.env`: `FDA_API_KEY=your-key`

## 🎯 Next Steps

After successful deployment:

1. **Test all endpoints** using the provided curl examples
2. **Set up monitoring alerts** in Grafana
3. **Configure automated backups** for your database
4. **Set up CI/CD pipeline** for automatic deployments
5. **Configure SSL certificates** for your domain
6. **Monitor API usage and costs**

---

✅ **You now have a production-ready AI Nurse Florence deployment with live medical data!**

For questions or issues, check the troubleshooting section above or review the application logs.