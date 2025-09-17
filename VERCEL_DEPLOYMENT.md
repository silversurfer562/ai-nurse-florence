# Vercel Deployment Guide

This document provides guidance for deploying the AI Nurse Florence application to Vercel.

## Fixed Issues

The following issues that were causing `FUNCTION_INVOCATION_FAILED` errors have been resolved:

1. **Pydantic BaseSettings Import Error**: Updated to use `pydantic-settings` package
2. **Missing Dependencies**: Added `pydantic-settings` and `python-multipart` to requirements.txt
3. **Undefined Variables**: Added missing `EXEMPT_PATHS` variable
4. **Middleware Configuration**: Fixed LoggingMiddleware registration
5. **Environment Variables**: Made `API_BEARER` optional to prevent startup failures
6. **Celery Configuration**: Made Redis dependency optional for serverless deployment

## Deployment Configuration

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "env": {
    "PYTHONPATH": ".",
    "LOG_LEVEL": "INFO"
  }
}
```

### Environment Variables (Vercel Dashboard)

Set these in your Vercel project's environment variables:

- `API_BEARER` (optional): Your API bearer token
- `OPENAI_API_KEY` (optional): OpenAI API key for AI features
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `LOG_LEVEL`: Set to "INFO" or "DEBUG"
- `REDIS_URL` (optional): Redis URL for caching (if available)

## Testing Deployment

After deployment, test these endpoints:

1. **Health Check**: `https://your-app.vercel.app/health`
   - Should return: `{"status": "ok", "service": "ai-nurse-florence"}`

2. **Root Endpoint**: `https://your-app.vercel.app/`
   - Should return: `{"message": "AI Nurse Florence API", "status": "running", "docs": "/docs"}`

3. **API Documentation**: `https://your-app.vercel.app/docs`
   - Should display the FastAPI documentation interface

## Troubleshooting

### If you still get FUNCTION_INVOCATION_FAILED:

1. **Check the Vercel function logs** in your Vercel dashboard
2. **Verify environment variables** are set correctly
3. **Check import errors** by testing locally first:
   ```bash
   python -c "from api.index import handler; print('OK')"
   ```

### Common Issues:

1. **Import Errors**: Make sure all dependencies are in requirements.txt
2. **Environment Variables**: Ensure required env vars are set in Vercel dashboard
3. **File Structure**: Verify the api/index.py file exists and imports correctly
4. **Database Issues**: The app defaults to SQLite which works in serverless environments

## Local Testing

To test locally before deployment:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app:app --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/
```

## Notes

- The application is configured to work without Redis or external databases
- Celery tasks will run synchronously when Redis is not available
- All endpoints except auth require authentication when `API_BEARER` is set
- Health and documentation endpoints are always accessible