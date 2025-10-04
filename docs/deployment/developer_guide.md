# AI Nurse Florence: Developer Guide

This guide provides technical documentation for developers working with the AI Nurse Florence API and codebase.

## Architecture Overview

AI Nurse Florence is a FastAPI-based application that provides healthcare information through various live medical data services:

```
┌───────────────┐     ┌─────────────┐     ┌─────────────────┐
│  API Gateway  │────▶│  FastAPI    │────▶│  Core Services  │
└───────────────┘     └─────────────┘     └─────────────────┘
                            │                      │
                            ▼                      ▼
                      ┌─────────────┐     ┌─────────────────┐
                      │  Middleware │     │ Live Medical    │
                      └─────────────┘     │ APIs Integration│
                            │             └─────────────────┘
                            ▼                      │
                      ┌─────────────┐              ▼
                      │   Caching   │     ┌─────────────────┐
                      └─────────────┘     │ LLM Integration │
                                          └─────────────────┘
```

### Key Components

- **API Routers**: Endpoint definitions in the `/routers` directory
- **Services**: Core business logic in the `/services` directory with live API integration
- **Live Medical APIs**: Real-time data from `live_mydisease.py`, `live_pubmed.py`, `live_clinicaltrials.py`
- **Middleware**: Request processing, rate limiting, and logging in `/utils/middleware.py`
- **Exception Handling**: Custom exceptions with external service handling in `/utils/exceptions.py`
- **Caching**: Redis-based caching with in-memory fallback in `/utils/cache.py`
- **Monitoring**: Prometheus metrics and health checks in `/utils/metrics.py`

## Live Medical Data Integration

### External APIs

#### MyDisease.info
- **Purpose**: Comprehensive disease information and cross-references
- **File**: `live_mydisease.py`
- **Function**: `lookup(term: str)`
- **Rate Limits**: No authentication required, reasonable use expected
- **Data Fields**: Disease names, definitions, references, cross-database IDs

#### PubMed/NCBI eUtils
- **Purpose**: Medical literature search from 35+ million citations
- **File**: `live_pubmed.py`  
- **Functions**: `search(query, max_results)`, `get_total_count(query)`
- **Rate Limits**: 3/sec (10/sec with API key)
- **API Key**: Set `NCBI_API_KEY` for enhanced rate limits

#### ClinicalTrials.gov
- **Purpose**: Current and completed clinical studies
- **File**: `live_clinicaltrials.py`
- **Function**: `search(condition, status, max_results)`
- **API Version**: v2 (current stable)
- **Rate Limits**: No authentication required

## Getting Started

### Prerequisites

- Python 3.9+
- Redis (for production deployments - optional for development)
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key (required for AI features)
- NCBI API key (optional but recommended for enhanced PubMed rate limits)

### Local Development Setup

#### Option 1: Automated Setup (Recommended)
```bash
./run_dev.sh  # Automated setup: venv, deps, .env creation, uvicorn
```

#### Option 2: Manual Setup
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
   pip install requests greenlet  # Required for live medical APIs
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration:
   # OPENAI_API_KEY=your_openai_key_here
   # USE_LIVE=1  # Enable live medical APIs
   # NCBI_API_KEY=your_ncbi_key_here  # Optional
   ```

5. Run the development server:
   ```bash
   export USE_LIVE=1  # Enable live services
   uvicorn app:app --reload
   # Or use the automated script: ./run_dev.sh
   ```

### Live Services Configuration

#### Enabling Live Medical APIs
Set `USE_LIVE=1` in your environment or `.env` file to enable real-time medical data:

```bash
# Enable all live services
export USE_LIVE=1

# Run with live services
uvicorn app:app --reload
```

#### Service Fallbacks
The application uses conditional imports with graceful degradation:
- **Live services available**: Real medical data from external APIs
- **Live services unavailable**: Development stubs with sample data
- **Network issues**: Cached responses when available

### Testing Live Services

#### Quick Service Verification
```bash
# Test individual live services
python -c "
from live_mydisease import lookup
result = lookup('diabetes')
print(f'MyDisease.info: {result.get(\"name\", \"Failed\")}')
"

python -c "
from live_pubmed import search
result = search('hypertension', max_results=1)
print(f'PubMed: Found {len(result)} articles')
"

python -c "
from live_clinicaltrials import search
result = search('heart failure', max_results=1) 
print(f'ClinicalTrials.gov: Found {len(result)} trials')
"
```

#### FastAPI Integration Testing
```bash
# Test complete API endpoints
python -c "
from fastapi.testclient import TestClient
from app import app
client = TestClient(app)

# Test disease endpoint
response = client.get('/api/v1/disease?q=diabetes')
print(f'Disease API: {response.status_code}')

# Test health check
response = client.get('/api/v1/health')
print(f'Health API: {response.status_code}')
"
```

#### Unit Testing
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/                    # Unit tests only
pytest tests/test_integration.py      # Integration tests
pytest -m integration                 # Integration marked tests
pytest -ra                           # Show all test output
```

### Development Workflows

#### Adding New Medical Information Endpoints
Follow this pattern when adding new medical data endpoints:

1. **Create Live Service** (`live_newservice.py`):
```python
import requests

def lookup_data(term: str):
    # External API call
    response = requests.get(f"https://api.example.com/search", 
                          params={"q": term})
    return response.json()
```

2. **Create Service Layer** (`services/newservice_service.py`):
```python
from utils.cache import cached
from utils.exceptions import ExternalServiceException

@cached(ttl_seconds=3600)
def lookup_service_data(term: str):
    banner = "Educational use only — not medical advice. No PHI stored."
    
    # Conditional import with fallback
    try:
        from live_newservice import lookup_data
        if USE_LIVE:
            return {"data": lookup_data(term), "banner": banner}
    except ImportError:
        pass
    
    # Fallback stub response
    return {"data": f"Sample data for {term}", "banner": banner}
```

3. **Create Router** (`routers/newservice.py`):
```python
from fastapi import APIRouter, Query
from services.newservice_service import lookup_service_data

router = APIRouter(prefix="/newservice", tags=["newservice"])

@router.get("/")
def get_service_data(q: str = Query(..., description="Search term")):
    return lookup_service_data(q)
```

4. **Register Router** (in `app.py`):
```python
from routers.newservice import router as newservice_router
api_router.include_router(newservice_router)
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

## Maintenance & CI

This section helps maintainers run CI-like steps locally, reproduce failures, and perform routine maintenance.

### Run CI steps locally (lightweight)
1. Activate venv (if present) and install dependencies:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt  # optional for linting/tools
```

2. Run the repository healthcheck and tests as CI does:

```bash
# Ensure imports resolve
export PYTHONPATH=$(pwd)
# CI intentionally disables Redis for hermetic test runs
export AI_NURSE_DISABLE_REDIS=1
# Optional: disable pytest-postgresql plugin locally if libpq isn't installed
./.venv/bin/python -m pytest -p no:pytest_postgresql -q
```

3. If CI needs full integration (Redis/Postgres), start local containers:

```bash
docker compose up -d postgres redis
export REDIS_URL=redis://localhost:6379
export DATABASE_URL=postgresql://postgres:password@localhost:5432/florence
export AI_NURSE_DISABLE_REDIS=0
./.venv/bin/python -m pytest -q
```

### CI troubleshooting notes
- If tests hang: confirm `AI_NURSE_DISABLE_REDIS` is set to `1` for CI-style runs.
- If pytest errors about `psycopg` / libpq: either install system `libpq` or run pytest with `-p no:pytest_postgresql` as shown above.
- If GitHub Actions fails with dependency resolution, check pinned versions in `requirements.txt` and `requirements-dev.txt` for conflicts.

### Routine maintenance tasks
- Update dependency pins cautiously; run `pip-compile` or similar dependency pinning in a sandbox before updating `requirements*.txt`.
- Keep `docs/` in sync with major architectural changes; add short migration notes for breaking changes.
- Run `ruff`, `flake8`, and `mypy` locally before opening PRs.

### Helpful commands
```bash
# Lint and type check
./.venv/bin/python -m ruff check . || true
./.venv/bin/python -m mypy src || true

# Run unit tests only
./.venv/bin/python -m pytest tests/unit/ -q

# Run a specific test with verbose output
AI_NURSE_DISABLE_REDIS=1 ./.venv/bin/python -m pytest tests/unit/test_cache_concurrency.py -q -vv -s -x
```