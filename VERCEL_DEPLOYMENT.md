# Vercel Deployment Guide for AI Nurse Florence

## Overview

This application has been configured to deploy successfully on Vercel serverless functions. The main issues that were causing `FUNCTION_INVOCATION_FAILED` have been resolved.

## Issues Fixed

1. **Pydantic Compatibility**: Updated to use `pydantic-settings` package
2. **Celery Dependencies**: Made Celery/Redis optional for serverless deployment
3. **Middleware Configuration**: Fixed LoggingMiddleware initialization
4. **Missing Dependencies**: Added python-multipart and other required packages
5. **Health Endpoint**: Added `/health` endpoint for monitoring

## Deployment Steps

1. **Connect Repository to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project" and import your GitHub repository

2. **Environment Variables**
   Set these environment variables in Vercel dashboard:
   ```
   API_BEARER=your-secure-api-key
   CORS_ORIGINS=*
   LOG_LEVEL=INFO
   RATE_LIMIT_PER_MINUTE=60
   USE_LIVE=false
   
   # Optional - for OpenAI features
   OPENAI_API_KEY=your-openai-api-key
   ```

3. **Deploy**
   - Vercel will automatically use the `vercel.json` configuration
   - The deployment should complete successfully

## Testing Your Deployment

After deployment, test these endpoints:

- `https://your-app.vercel.app/health` - Should return `{"status":"ok"}`
- `https://your-app.vercel.app/docs` - API documentation
- `https://your-app.vercel.app/api/v1/summarize/chat` - Test with POST request

## Key Configuration Files

- `vercel.json` - Vercel deployment configuration
- `.vercelignore` - Files to exclude from deployment
- `requirements.txt` - Python dependencies (updated with fixes)

## Serverless Adaptations

The application now:
- Runs without Redis/Celery (tasks execute synchronously)
- Handles missing OpenAI API key gracefully
- Uses SQLite database (auto-created on startup)
- Includes proper error handling for serverless environment

## Monitoring

The application includes:
- Health endpoint at `/health`
- Request logging with unique request IDs
- Prometheus metrics at `/metrics`
- Comprehensive error handling

If you encounter issues, check the Vercel function logs for detailed error information.