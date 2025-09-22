# AI Nurse Florence - AI Agent Instructions

## Project Overview
Healthcare AI assistant FastAPI application providing evidence-based medical information for nurses and healthcare professionals. **Educational use only - not medical advice. No PHI stored.**

## Architecture Patterns

### Service Layer Architecture
- **Services** (`services/`): Business logic with caching, OpenAI integration, external API calls
- **Routers** (`routers/`): FastAPI endpoints with validation, documentation, error handling  
- **Utils** (`utils/`): Shared utilities (config, logging, caching, middleware)
- **Models** (`models/`): Pydantic schemas and SQLAlchemy models

### Conditional Imports Pattern
Critical pattern throughout codebase - graceful degradation when optional dependencies missing:
```python
try:
    from utils.metrics import record_cache_hit
    _has_metrics = True
except ImportError:
    _has_metrics = False
    def record_cache_hit(cache_key: str) -> None:
        pass
```

### Router Organization
- **Protected routes**: `/api/v1/*` - main functionality
- **Unprotected routes**: `/api/v1/health`, `/api/v1/auth` 
- **Wizards**: Multi-step guided workflows in `routers/wizards/`

## Key Development Workflows

### Environment Setup
```bash
./run_dev.sh  # Automated setup: venv, deps, .env creation, uvicorn
```

### Testing
```bash
pytest  # All tests (see conftest.py for path setup)
pytest tests/unit/  # Unit tests only
pytest tests/test_integration.py  # Integration tests
pytest -m integration  # Run integration marked tests
pytest -ra  # Show all test output (configured in pytest.ini)
```

#### Testing Patterns
- **Fixture-based mocking**: `tests/conftest.py` provides service layer mocks
- **TestClient**: FastAPI's test client for endpoint testing
- **Service mocking**: Each external service has dedicated fixtures (disease, PubMed, trials)
- **Type-safe mocks**: Mock responses match Pydantic type definitions
- **Integration marks**: `pytestmark = pytest.mark.integration` for test categorization

### Database Migration
```bash
alembic upgrade head  # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration
```

### Deployment Workflows
```bash
# Local development
./run_dev.sh  # Automated setup: venv, deps, .env creation, uvicorn

# Docker development
docker-compose up  # Full stack with Redis, PostgreSQL, monitoring

# Production build
docker build -t ai-nurse-florence .
docker run -p 8000:8000 --env-file .env ai-nurse-florence
```

#### Environment Configuration
- **Local**: `.env` file from `.env.example` template
- **Docker**: Environment variables in docker-compose.yml
- **Railway**: Production deployment with PostgreSQL and Redis
- **Production**: PostgreSQL + Redis for caching and session storage

## Critical Code Patterns

### Caching Strategy
- **Redis-backed**: `@cached(ttl_seconds=3600)` decorator pattern
- **Service level**: All external API calls cached (disease, PubMed, trials)
- **Thread-safe**: In-memory fallback with RLock

### Error Handling
- **Custom exceptions**: `utils/exceptions.py` - ServiceException, ExternalServiceException
- **Standardized responses**: `utils/api_responses.py` - create_success_response/create_error_response
- **Request IDs**: RequestIdMiddleware for tracing

### OpenAI Integration
- **Lazy client**: `services/openai_client.py` - returns None if API key missing
- **Model selection**: `services/model_selector.py` - context-aware model choice
- **Prompt enhancement**: `services/prompt_enhancement.py` - clarification logic

### Security & Middleware Stack
1. SecurityHeadersMiddleware (CSP, HSTS headers)
2. RequestIdMiddleware (UUID generation)
3. LoggingMiddleware (structured logging)
4. RateLimiter (60/min default, exempt paths in app.py)
5. CORS (configurable origins)

## Configuration Management
- **Centralized**: `utils/config.py` using Pydantic Settings
- **Environment-based**: `.env` file with sensible defaults
- **Feature flags**: `USE_LIVE` toggles external services vs stubs

## API Design Standards
- **OpenAPI docs**: Comprehensive examples, descriptions for all endpoints
- **Response models**: Pydantic models with educational banners
- **Query enhancement**: Vague queries trigger clarification prompts
- **Educational disclaimers**: All medical content includes safety banners

## Database Patterns
- **Async SQLAlchemy**: AsyncSession pattern throughout
- **SQLite default**: Production uses PostgreSQL via DATABASE_URL
- **Migration-first**: Alembic for all schema changes

## Wizard Pattern Implementation
Multi-step workflows with session state:
- **Session storage**: In-memory dict (Redis in production)
- **UUID-based**: Unique wizard_id per session
- **Step validation**: Pydantic models for each step
- **SBAR reports**: Clinical documentation wizard example

## External Service Integration
- **MyDisease.info**: Disease information lookup
- **PubMed**: Medical literature search
- **ClinicalTrials.gov**: Trial discovery
- **Conditional loading**: Services fail gracefully if APIs unavailable

## Monitoring & Observability
- **Prometheus metrics**: Optional instrumentator integration
- **Structured logging**: JSON format with request correlation
- **Health checks**: `/api/v1/health` with dependency status
- **Cache metrics**: Hit/miss tracking when metrics enabled

## Development Notes
- **Import path setup**: `conftest.py` adds project root to sys.path
- **Modular startup**: Features conditionally enabled based on availability
- **Docker support**: Multi-stage build with health checks
- **Public benefit focus**: All features designed for healthcare accessibility

## Implementation Examples

### Adding New Medical Information Endpoint
Follow this pattern when adding new medical data endpoints:

1. **Create Service** (`services/new_service.py`):
```python
from utils.redis_cache import cached
from utils.exceptions import ExternalServiceException

@cached(ttl_seconds=3600)
def lookup_medical_data(term: str) -> MedicalResult:
    banner = "Draft for clinician review — not medical advice. No PHI stored."
    # Enhance prompt for clarity
    effective_term, needs_clarification, clarification_question = enhance_prompt(term, "medical_data")
    
    if needs_clarification:
        return {"banner": banner, "query": term, "needs_clarification": True, 
                "clarification_question": clarification_question}
    
    # External API call with conditional loading
    if LIVE and external_service:
        try:
            result = external_service.lookup(effective_term)
            return format_result(result, banner)
        except Exception as e:
            raise ExternalServiceException("External service failed", "medical_service")
    
    # Fallback stub response
    return create_stub_response(term, banner)
```

2. **Create Router** (`routers/medical_data.py`):
```python
from fastapi import APIRouter, Query, status
from models.schemas import MedicalDataResponse
from services.medical_service import lookup_medical_data
from utils.api_responses import create_success_response, create_error_response

router = APIRouter(prefix="/medical-data", tags=["medical-data"])

@router.get("/", response_model=MedicalDataResponse)
def get_medical_data(
    q: str = Query(..., description="Medical term to search for",
                   examples={"hypertension": {"summary": "Search for hypertension data"}})
):
    result = lookup_medical_data(q)
    
    if result.get("needs_clarification"):
        return create_error_response(
            message="Query needs clarification",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"clarification_question": result["clarification_question"]}
        )
    
    return create_success_response(result)
```

3. **Add Pydantic Model** (`models/schemas.py`):
```python
class MedicalDataResponse(BaseModel):
    banner: str = Field(default=EDU_BANNER)
    query: str
    data: str
    references: List[Reference] = []
```

4. **Register in App** (`app.py`):
```python
from routers.medical_data import router as medical_data_router
api_router.include_router(medical_data_router)
```

### Authentication & Authorization
- **OAuth2 + JWT**: `utils/auth.py` provides GPT Store-compatible auth flow
- **Protected endpoints**: Use `Depends(get_current_user)` dependency
- **API key auth**: Bearer token validation for service-to-service calls
- **User management**: SQLAlchemy models with CRUD operations

### Rate Limiting & Monitoring
- **Rate limiting**: `utils/rate_limit.py` - IP-based with Redis backend
- **Exempt paths**: Docs, health, metrics excluded (defined in `app.py`)
- **Prometheus metrics**: `utils/metrics.py` - request counts, latency, errors
- **Background tasks**: `utils/background_tasks.py` - async task execution with status tracking

### Middleware Stack Order
Critical order in `app.py`:
1. **SecurityHeadersMiddleware** - CSP, HSTS headers
2. **RequestIdMiddleware** - UUID generation for tracing  
3. **LoggingMiddleware** - Structured request/response logging
4. **RateLimiter** - Request throttling (conditional)
5. **CORS** - Cross-origin handling
