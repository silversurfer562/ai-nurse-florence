# AI Nurse Florence — FastAPI Wrapper (v3)

**Educational Use Only — Not Medical Advice. No PHI stored.**

A comprehensive medical information API wrapper with integrated Notion-GitHub tracking for development workflow management.

## Features

### Core API Endpoints
- Disease summaries and medical condition lookups
- PubMed research paper search
- Clinical trials information
- MedlinePlus patient education content
- SBAR (Situation, Background, Assessment, Recommendation) generation
- Patient education materials with readability analysis

### Notion-GitHub Integration 🆕
- **Real-time webhook integration**: Automatically track GitHub events (pushes, PRs, issues) in Notion
- **Repository digest**: Automated daily summaries of all repository activity
- **Structured tracking**: Organized data in Notion for easy filtering and project management
- **Secure webhook handling**: HMAC signature verification for security

## Quick Start

### 1. Basic Setup
```bash
git clone https://github.com/silversurfer562/ai-nurse-florence.git
cd ai-nurse-florence
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Notion Integration Setup (Optional)
For GitHub-Notion integration, see the detailed setup guide:
📖 **[Notion-GitHub Setup Guide](docs/NOTION_GITHUB_SETUP.md)**

### 4. Validate Configuration
```bash
python scripts/validate_config.py
```

### 5. Run the Application
```bash
uvicorn app:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## Notion Integration Features

- ✅ **Real-time webhooks** for GitHub events
- ✅ **Repository digest** workflow with enhanced formatting
- ✅ **Secure webhook verification** with HMAC signatures
- ✅ **Comprehensive error handling** and retry logic
- ✅ **Health monitoring** endpoints
- ✅ **Configuration validation** tools

### Webhook Health Check
Visit `/webhooks/health` to verify your integration status:
```json
{
  "status": "healthy",
  "configuration": {
    "webhook_secret": true,
    "notion_token": true,
    "notion_database_id": true
  },
  "notion_connection": "connected"
}
```

## API Documentation

OpenAPI documentation includes bearerAuth and example responses optimized for GPT Builder integration. Access at `/docs` when the server is running.

## Development

### Testing
```bash
pytest tests/ -v
```

### Linting
```bash
flake8 . --max-line-length=120
```

## GitHub Actions

The repository includes automated workflows for:
- **CI/CD Pipeline**: Testing, building, and deployment
- **Repository Digest**: Automated summaries to Notion/Email
- **Code Quality**: Linting and type checking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Security

- Webhook endpoints use HMAC signature verification
- Environment variables for sensitive configuration
- No PHI (Protected Health Information) storage
- Educational use disclaimer on all medical content

## License

This project is for educational purposes only and is not intended to provide medical advice.
