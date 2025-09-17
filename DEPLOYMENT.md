# AI Nurse Florence - Deployment Guide

## Vercel Deployment

This FastAPI application is configured for deployment to Vercel. Follow these steps:

### Prerequisites

1. Vercel account
2. Environment variables configured in Vercel dashboard

### Required Environment Variables

Set these in your Vercel dashboard under Project Settings > Environment Variables:

```
API_BEARER=your-strong-api-key-here
OPENAI_API_KEY=sk-your-openai-api-key
CORS_ORIGINS=https://chat.openai.com,https://chatgpt.com
DATABASE_URL=postgresql://user:password@host:port/dbname
REDIS_URL=redis://user:password@host:port
JWT_SECRET_KEY=your-super-secret-jwt-key-at-least-32-characters-long
OAUTH_CLIENT_ID=your-chatgpt-oauth-client-id
OAUTH_CLIENT_SECRET=your-chatgpt-oauth-client-secret
LOG_LEVEL=INFO
USE_LIVE=1
RATE_LIMIT_PER_MINUTE=60
```

### Deployment Steps

1. Connect your GitHub repository to Vercel
2. Configure environment variables
3. Deploy using `vercel --prod` or through the Vercel dashboard

### ChatGPT Store Integration

The API is designed for ChatGPT store integration with:

- OAuth2 authentication flow at `/api/v1/auth/token`
- Bearer token authentication for all protected endpoints
- Comprehensive OpenAPI documentation at `/docs`
- Health check endpoint at `/api/v1/health`
- CORS configured for ChatGPT domains

### Local Development

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run
uvicorn app:app --reload
```

Access the API at http://localhost:8000 and docs at http://localhost:8000/docs

### Database Setup

For production, use PostgreSQL. For development, SQLite is used by default.

### Security Notes

- All API endpoints except `/health` and `/auth/token` require authentication
- Rate limiting is enabled (60 requests/minute by default)
- CORS is configured for ChatGPT domains in production
- Environment variables should be kept secure and not committed to repository