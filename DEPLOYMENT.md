# Vercel Deployment Guide for AI Nurse Florence

This guide will help you deploy the AI Nurse Florence FastAPI application to Vercel.

## Prerequisites

1. Vercel account
2. OpenAI API key (for AI functionality)
3. Any external database or Redis instance (optional)

## Deployment Steps

### 1. Fork or Clone Repository

Make sure you have the repository in your GitHub account.

### 2. Connect to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your repository
4. Select the repository root (not the subfolder)

### 3. Configure Environment Variables

In the Vercel dashboard, go to your project settings and add these environment variables:

```bash
# Required
API_BEARER=your-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
CORS_ORIGINS=https://your-project.vercel.app
JWT_SECRET_KEY=your-secure-random-string-here

# Optional
USE_LIVE=true
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
```

### 4. Deploy

Vercel will automatically deploy your application using the `vercel.json` configuration.

## Project Structure

- `/api/index.py` - Main Vercel serverless function entry point
- `/vercel.json` - Vercel deployment configuration
- `/requirements.txt` - Python dependencies
- `/ai-nurse-florence-working/ai-nurse-florence/` - Main application code

## Configuration Files

### vercel.json
Configures Vercel to run the FastAPI application as a serverless function.

### api/index.py
Entry point that imports the main FastAPI app and wraps it with Mangum for AWS Lambda compatibility.

## Environment Variables

See `.env.production` for a complete list of environment variables that can be configured.

## Troubleshooting

### Import Errors
If you see import errors, check:
1. All dependencies are listed in `requirements.txt`
2. Python path is configured correctly
3. Environment variables are set properly

### Database Issues
For production, consider using:
- PostgreSQL on platforms like Neon, Supabase, or PlanetScale
- Redis on platforms like Upstash or Redis Cloud

### API Key Issues
Make sure all required API keys are set in Vercel environment variables.

## Local Testing

To test the Vercel deployment locally:

```bash
# Install Vercel CLI
npm i -g vercel

# Run locally
vercel dev
```

## Health Check

After deployment, check:
- `https://your-project.vercel.app/` - Main API
- `https://your-project.vercel.app/health` - Health check endpoint
- `https://your-project.vercel.app/docs` - API documentation

## Support

If you encounter issues:
1. Check Vercel build logs
2. Verify environment variables
3. Check Python import paths
4. Ensure all dependencies are compatible with Python 3.12