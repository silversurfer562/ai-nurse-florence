# Configuration Guide for AI Nurse Florence

## Overview

This document provides a comprehensive guide to configuring the AI Nurse Florence application. All configuration settings have been reviewed and properly defined with sensible defaults to ensure the application can start in various environments.

## Quick Start

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Set your OpenAI API key (required for AI features):**
   ```bash
   # Edit .env file
   OPENAI_API_KEY=your-openai-api-key-here
   ```

3. **Start the application:**
   ```bash
   uvicorn app:app --reload
   ```

## Configuration Settings

### Required Settings (with defaults)

These settings are required but have sensible defaults that allow the application to start without additional configuration:

| Setting | Default | Description |
|---------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./ai_nurse_florence.db` | Database connection URL |
| `JWT_SECRET_KEY` | `your-secret-key-change-in-production` | Secret key for JWT signing ⚠️ |
| `JWT_ALGORITHM` | `HS256` | Algorithm for JWT token signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token expiration time |
| `CORS_ORIGINS` | `["http://localhost:3000", "http://localhost:8000"]` | Allowed CORS origins |
| `RATE_LIMIT_PER_MINUTE` | `60` | Rate limit per client per minute |
| `USE_LIVE` | `false` | Use live external APIs vs mocked data |
| `LOG_LEVEL` | `INFO` | Logging level |

⚠️ **Security Warning**: Change `JWT_SECRET_KEY` in production!

### Optional Settings

These settings are optional and the application will function without them:

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENAI_API_KEY` | `None` | OpenAI API key for AI functionality |
| `API_BEARER` | `None` | Legacy API bearer token |
| `OAUTH_CLIENT_ID` | `None` | OAuth2 client ID for OpenAI GPT integration |
| `OAUTH_CLIENT_SECRET` | `None` | OAuth2 client secret for OpenAI GPT integration |
| `REDIS_URL` | `None` | Redis URL for caching and background tasks |
| `NIH_API_BASE` | `None` | Custom NIH API endpoint |

## Environment-Specific Configuration

### Development (Default)

The application works out-of-the-box for development with SQLite and mocked external APIs:

```bash
# Minimal .env for development
OPENAI_API_KEY=your-openai-key-here
```

### Production

For production deployments, configure these additional settings:

```bash
# Production .env example
OPENAI_API_KEY=your-production-openai-key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ai_nurse_florence
JWT_SECRET_KEY=your-very-secure-secret-key-here
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
RATE_LIMIT_PER_MINUTE=120
REDIS_URL=redis://redis-server:6379/0
USE_LIVE=true
LOG_LEVEL=WARNING
```

### Docker

For Docker deployments:

```bash
# Docker .env example  
OPENAI_API_KEY=your-openai-key
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/ai_nurse_florence
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=https://your-frontend-domain.com
```

## Configuration Features

### Smart CORS Parsing

The `CORS_ORIGINS` setting accepts both formats:

```bash
# List format (default)
CORS_ORIGINS=["http://localhost:3000", "https://example.com"]

# Comma-separated string (environment variable friendly)
CORS_ORIGINS=http://localhost:3000,https://example.com,https://app.example.com
```

### Validation

Configuration includes validation for:
- Rate limits must be positive numbers
- Proper error messages for invalid values
- Type conversion and validation

### Database Support

#### SQLite (Default - Development)
```bash
DATABASE_URL=sqlite+aiosqlite:///./ai_nurse_florence.db
```

#### PostgreSQL (Recommended - Production)
```bash
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/ai_nurse_florence
```

## Feature Flags

### USE_LIVE Setting

Controls whether the application uses live external APIs or mocked data:

- `USE_LIVE=false` (default): Uses mocked data for external APIs (good for development/testing)
- `USE_LIVE=true`: Uses live external APIs (required for production)

## Security Considerations

### JWT Configuration

1. **Always change `JWT_SECRET_KEY` in production**
2. Use a strong, randomly generated secret key
3. Consider shorter token expiration times for sensitive environments

### API Authentication

The application supports both:
- **OAuth2 JWT tokens** (recommended for GPT integration)
- **Legacy bearer tokens** (for backward compatibility)

### CORS Configuration

Configure `CORS_ORIGINS` to only include trusted domains in production.

## Troubleshooting

### Common Issues

1. **"Field required" error for OPENAI_API_KEY**
   - This is expected if not set - the app will start but AI features won't work
   - Set the key in your `.env` file to enable AI functionality

2. **Database connection errors**
   - Verify your `DATABASE_URL` is correct
   - For PostgreSQL, ensure the database exists and is accessible
   - SQLite is created automatically

3. **CORS errors in browser**
   - Add your frontend URL to `CORS_ORIGINS`
   - Use comma-separated format for multiple origins

4. **Rate limiting too strict/loose**
   - Adjust `RATE_LIMIT_PER_MINUTE` based on your needs
   - Must be a positive integer

### Configuration Validation

You can validate your configuration by running:

```python
from utils.config import settings
print("Configuration loaded successfully!")
print(f"Database: {settings.DATABASE_URL}")
print(f"OpenAI: {'Configured' if settings.OPENAI_API_KEY else 'Not configured'}")
```

## Migration from Previous Versions

If you're upgrading from a previous version:

1. Copy your existing `.env` file
2. Review the new `.env.example` for any new settings
3. The application will use sensible defaults for any missing settings
4. No configuration changes are required for basic functionality

## Support

For configuration issues:
1. Check this documentation
2. Review the `.env.example` file for examples
3. Verify your environment variables are properly set
4. Check the application logs for specific error messages