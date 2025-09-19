# GitHub Copilot Instructions for AI Nurse Florence

## Project Overview

AI Nurse Florence is a FastAPI-based healthcare API designed to assist healthcare professionals with clinical information, research, and patient education. The system provides endpoints for disease summaries, PubMed search, clinical trials, MedlinePlus summaries, and specialized healthcare workflows like SBAR and patient education tools.

**Important**: This is for educational use only, provides no medical advice, and stores no PHI (Protected Health Information).

## Architecture

### Core Components
- **FastAPI Application** (`app.py`): Main ASGI application with rate limiting and configuration validation
- **API Routers** (`routers/`): Modular endpoint definitions for different functionalities
- **Services** (`services/`): Core business logic and external API integrations  
- **Utils** (`utils/`): Shared utilities for API responses, rate limiting, configuration
- **Models & Schemas** (`models/`, `schemas.py`): Data models and Pydantic schemas
- **Tests** (`tests/`): Comprehensive test suite with pytest

### Key Features
- **Wizard-based workflows**: Multi-step processes for disease search and SBAR reports
- **External API integrations**: PubMed, MedlinePlus, Clinical Trials, MyDisease.info
- **Prompt enhancement**: LLM-based query refinement system
- **Rate limiting**: Built-in request throttling for API protection
- **Standardized responses**: Consistent success/error response formats
- **Background tasks**: Support for long-running operations

## Development Guidelines

### Code Style and Standards
- Follow **PEP 8** style guidelines with 120 character line length
- Use **type hints** for all function parameters and return values
- Write **docstrings** in Google format for all public functions/classes
- Use **Pydantic models** for request/response validation
- Implement **proper error handling** with custom exceptions

### File Organization
```
├── app.py                 # FastAPI application entry point
├── routers/              # API endpoint definitions
│   ├── wizards/         # Multi-step workflow endpoints
│   └── ...              # Other API modules
├── services/            # Business logic and external integrations
├── utils/               # Shared utilities and helpers
├── models/              # Database models (if applicable)
├── schemas.py           # Pydantic request/response schemas
├── tests/               # Test suite
└── docs/                # Documentation
```

### Testing Requirements
- Write **unit tests** for all new functions and endpoints
- Use **pytest fixtures** from `tests/conftest.py`
- **Mock external services** when testing API integrations
- Run tests with: `pytest` (some tests may fail due to missing configuration)
- Test dependencies: `pip install redis hypothesis` if not already installed
- Note: Some integration tests require environment variables (OPENAI_API_KEY, etc.)

### Example Test Pattern
```python
@patch('services.external_service.api_call')
def test_endpoint_success(mock_api_call, client):
    mock_api_call.return_value = {"data": "test"}
    response = client.post("/endpoint", json={"param": "value"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

### API Response Standards
Always use standardized response formats:

**Success Response:**
```python
from utils.api_responses import create_success_response
return create_success_response(data=result, status_code=200)
```

**Error Response:**
```python
from utils.api_responses import create_error_response
return create_error_response(
    message="Error description",
    status_code=400,
    code="error_code",
    details={"additional": "info"}
)
```

### Configuration Management
- Use `utils.config.get_settings()` for environment variables
- Required environment variables: `OPENAI_API_KEY`, `API_BEARER`
- Store sensitive data in `.env` file (never commit to git)
- Reference `.env.example` for configuration template

### External API Integration Patterns
```python
# Use httpx for HTTP requests
import httpx

async def fetch_external_data(query: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://api.example.com/search?q={query}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ExternalServiceException(
                message=f"Failed to fetch data: {str(e)}",
                service_name="example_api"
            )
```

### Wizard Implementation Pattern
For multi-step workflows:
1. Store session data in memory (or Redis for production)
2. Generate unique wizard IDs
3. Validate session state at each step
4. Clean up sessions after completion
5. Provide clear error messages for invalid states

## Development Workflow

### Setup
```bash
# Clone and setup environment
git clone <repository-url>
cd ai-nurse-florence
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools
```

### Quick Development
```bash
# Run development server
uvicorn app:app --reload

# Run tests (note: some may fail without environment setup)
pytest

# Lint code (note: existing codebase has style issues)
flake8 . --max-line-length=120 --exclude=.venv
mypy --ignore-missing-imports services routers utils

# Install additional test dependencies if needed
pip install redis hypothesis
```

### Pre-commit Checklist
1. Check linting: `flake8 . --max-line-length=120 --exclude=.venv` (note: existing code has style issues)
2. Run type checking: `mypy --ignore-missing-imports services routers utils`
3. Run available tests: `pytest` (some may fail without proper configuration)
4. Update documentation if needed
5. Ensure no secrets in code
6. Test your specific changes manually

### Known Development Issues
- Current codebase has style violations (many E302, W293, F401 warnings)
- Some tests require environment variables and may fail in CI
- Integration tests marked with `@pytest.mark.integration` 
- Missing dependencies in requirements-dev.txt (redis, hypothesis need manual install)

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches
- `hotfix/*`: Critical production fixes

## Common Patterns and Solutions

### Authentication
API uses bearer token authentication:
```python
from fastapi import Depends, HTTPException
from utils.auth import verify_token

async def protected_endpoint(token: str = Depends(verify_token)):
    # Endpoint logic here
```

### Rate Limiting
```python
from utils.rate_limit import RateLimiter
rate_limiter = RateLimiter(requests_per_minute=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    return await rate_limiter.check_rate_limit(request, call_next)
```

### Background Tasks
```python
from fastapi import BackgroundTasks
from utils.background_tasks import schedule_task

@router.post("/long-running-task")
async def start_task(background_tasks: BackgroundTasks):
    task_info = schedule_task(
        background_tasks,
        my_long_function,
        arg1, arg2,
        callback_url="https://example.com/callback"
    )
    return create_success_response(task_info)
```

### Error Handling
Use custom exceptions for consistent error responses:
```python
from utils.exceptions import ExternalServiceException, ValidationException

# In service layer
if not valid_input:
    raise ValidationException("Invalid input format")

# In external API calls  
if response.status_code != 200:
    raise ExternalServiceException(
        message="Service unavailable",
        service_name="pubmed",
        details={"status_code": response.status_code}
    )
```

### LLM Integration
When working with OpenAI API:
```python
from openai import OpenAI
from utils.config import get_settings

def get_client():
    settings = get_settings()
    return OpenAI(api_key=settings.OPENAI_API_KEY)

# Use structured outputs when possible
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    response_format={"type": "json_object"}  # For JSON responses
)
```

## Deployment and Operations

### CI/CD Pipeline
- **GitHub Actions** workflow in `.github/workflows/ci-cd.yml`
- Runs on Python 3.9, 3.10, 3.11
- Steps: lint, type check, test, build, deploy
- Automatic deployment to production on main branch merges

### Docker Deployment
```bash
# Build image
docker build -t ai-nurse-florence .

# Run with docker-compose
docker-compose up -d
```

### Monitoring
- Prometheus metrics available at `/metrics`
- Use logging middleware for request tracking
- Monitor external API rate limits and response times

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure virtual environment is activated
2. **Missing environment variables**: Check `.env` file configuration
3. **API rate limits**: Implement proper error handling and retry logic
4. **Test failures**: Many tests require environment setup (OPENAI_API_KEY, etc.)
5. **Style violations**: Current codebase has many flake8 issues to clean up gradually
6. **Missing dependencies**: Some test deps (redis, hypothesis) need manual installation
7. **Module not found**: Check if services are properly imported and structured

### Debug Mode
```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
uvicorn app:app --reload
```

### Performance Issues
- Monitor slow endpoints with FastAPI's built-in request timing
- Use Redis for caching frequently requested data
- Implement proper connection pooling for external APIs

## Security Considerations

- Never commit API keys or secrets to version control
- Validate all input data with Pydantic schemas
- Implement proper authentication for production
- Use HTTPS in production environments
- Regularly update dependencies for security patches
- Follow OWASP guidelines for API security

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes following the guidelines above
4. Add tests for new functionality
5. Ensure all checks pass (`flake8`, `mypy`, `pytest`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Project Developer Guide](docs/developer_guide.md)
- [User Guide](docs/nurse_user_guide.md)