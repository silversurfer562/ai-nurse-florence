# AI Nurse Florence: Developer Guide

This guide provides technical documentation for developers working with the AI Nurse Florence API and codebase.

## Architecture Overview

AI Nurse Florence is a FastAPI-based application that provides healthcare information through various services:

```
┌───────────────┐     ┌─────────────┐     ┌─────────────────┐
│  API Gateway  │────▶│  FastAPI    │────▶│  Core Services  │
└───────────────┘     └─────────────┘     └─────────────────┘
                            │                      │
                            ▼                      ▼
                      ┌─────────────┐     ┌─────────────────┐
                      │  Middleware │     │ External APIs   │
                      └─────────────┘     └─────────────────┘
                            │                      │
                            ▼                      ▼
                      ┌─────────────┐     ┌─────────────────┐
                      │   Caching   │     │ LLM Integration │
                      └─────────────┘     └─────────────────┘
```

### Key Components

- **API Routers**: Endpoint definitions in the `/routers` directory
- **Services**: Core business logic in the `/services` directory
- **Middleware**: Request processing in `/utils/middleware.py`
- **Exception Handling**: Custom exceptions in `/utils/exceptions.py`
- **Caching**: Redis-based caching in `/utils/redis_cache.py`
- **Monitoring**: Prometheus metrics in `/utils/metrics.py`

## Getting Started

### Prerequisites

- Python 3.9+
- Redis (for production deployments)
- Docker and Docker Compose (for containerized deployment)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-nurse-florence
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the development server:
   ```bash
   ./run_dev.sh
   # Or manually: uvicorn app:app --reload
   ```

### Docker Deployment

```bash
docker-compose up -d
```

## API Reference

### Authentication

Most endpoints require API key authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.florence-ai.org/v1/disease?q=diabetes
```

### Endpoint Categories

- **Disease Information**: `/v1/disease`
- **PubMed Search**: `/v1/pubmed`
- **Summarization**: `/summarize/*`
- **Clinical Trials**: `/v1/clinicaltrials`
- **Health Topics**: `/v1/medlineplus`
- **Readability Analysis**: `/v1/readability`

### Complete API Documentation

Access the OpenAPI documentation at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Key Features for Developers

### Prompt Enhancement System

Florence includes a system to enhance user prompts and provide clarification when needed:

```python
from services.prompt_enhancement import enhance_prompt

# Returns (enhanced_prompt, needs_clarification, clarification_question)
result = enhance_prompt("diabetes", service_type="disease")
```

When a clarification is needed, endpoints return a 422 status with details:

```json
{
  "detail": {
    "needs_clarification": true,
    "clarification_question": "What specific aspect of diabetes would you like information about?",
    "original_query": "diabetes"
  }
}
```

See `/docs/prompt_enhancement.md` for more details.

### Caching

Services use Redis-based caching with TTL support:

```python
from utils.redis_cache import cached

@cached(ttl_seconds=3600)
def my_expensive_function(param):
    # Function will be cached for 1 hour
    # ...
```

### Error Handling

Use custom exceptions for consistent error responses:

```python
from utils.exceptions import ExternalServiceException

raise ExternalServiceException(
    message="Failed to fetch data",
    service_name="pubmed",
    details={"query": "diabetes"}
)
```

### Background Tasks

Long-running operations can use background tasks:

```python
from utils.background_tasks import schedule_task

task_info = schedule_task(
    background_tasks,
    my_long_running_function,
    arg1, arg2,
    callback_url="https://example.com/callback"
)
# Returns {"task_id": "uuid", "status": "scheduled"}
```

## Working with External Services

### OpenAI Integration

```python
from services.openai_client import get_client

client = get_client()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a medical assistant."},
        {"role": "user", "content": prompt}
    ]
)
```

### PubMed Integration

```python
from services.pubmed_service import search_pubmed

results = search_pubmed("diabetes treatment", max_results=10)
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_prompt_enhancement.py

# Run with coverage
pytest --cov=.
```

### Writing Tests

- Unit tests go in `/tests`
- Use pytest fixtures from `/tests/conftest.py`
- Mock external services when testing

Example test with mocking:

```python
@patch('services.prompt_enhancement.enhance_prompt')
def test_summarize_endpoint(mock_enhance_prompt, client):
    mock_enhance_prompt.return_value = ("Enhanced prompt", False, None)
    response = client.post("/summarize/chat", json={"prompt": "test"})
    assert response.status_code == 200
```

## Deployment

### CI/CD Pipeline

The project uses GitHub Actions for CI/CD:
- PRs trigger linting, type checking, and tests
- Merges to main trigger deployment to production
- See `.github/workflows/ci-cd.yml` for details

### Monitoring

- Prometheus metrics available at `/metrics`
- Grafana dashboards in `/grafana/dashboards`

## Contributing

1. Create a feature branch (`git checkout -b feature/xyz`)
2. Make changes and add tests
3. Run tests (`pytest`)
4. Commit changes (`git commit -am 'Add feature xyz'`)
5. Push branch (`git push origin feature/xyz`)
6. Create Pull Request

## Code Style and Standards

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and returns
- Write docstrings in Google format
- Run `flake8` and `mypy` before committing

## Common Issues

### Redis Connection Problems

If Redis connections fail, the application will fall back to in-memory caching. Check:
- Redis server is running
- REDIS_URL is correct in .env
- Network allows connection to Redis port

### Rate Limiting

The application includes rate limiting. If you're getting 429 responses:
- Check the `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers
- Implement backoff in your client
- Contact admins for higher limits if needed

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [PubMed API Documentation](https://www.ncbi.nlm.nih.gov/books/NBK25500/)