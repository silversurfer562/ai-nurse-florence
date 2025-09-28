# Testing Strategy

This document summarizes how to run and write tests for AI Nurse Florence and includes troubleshooting tips for maintainers.

## Core ideas
- Prefer fast, deterministic unit tests for business logic and services.
- Use pytest fixtures (see `tests/conftest.py`) to provide mocked services and test clients.
- Mark long-running or environment-dependent tests with `@pytest.mark.integration`.

## Running tests
- Run the full test suite (CI style):

```bash
# Use project venv python for deterministic environment
export PYTHONPATH=$(pwd)
export AI_NURSE_DISABLE_REDIS=1   # Recommended for CI/local runs where Redis is not available
./.venv/bin/python -m pytest -q
```

- Run unit tests only:

```bash
./.venv/bin/python -m pytest tests/unit/ -q
```

- Run integration tests (requires live services or proper test fixtures):

```bash
export AI_NURSE_DISABLE_REDIS=0
./.venv/bin/python -m pytest -m integration -q
```

### Common pytest options
- `-k <expr>` - run tests matching expression
- `-x` - stop after first failure
- `-ra` - display extra test summary info

## Testing patterns and guidelines
- Use the fixtures in `tests/conftest.py` for database, Redis, and external services.
- Mock external HTTP calls with `pytest-httpx` or monkeypatch `httpx.AsyncClient` / `requests` where appropriate.
- For async code use `pytest-asyncio` and `async def` tests.

## CI reproducibility and local simulation
- The CI workflow runs tests with Redis disabled to avoid flaky external dependencies. Use `AI_NURSE_DISABLE_REDIS=1` to match CI behavior.
- If you need to validate Redis-backed behaviour locally, run a Redis container:

```bash
docker run -p 6379:6379 -d --name local-redis redis:7
export REDIS_URL=redis://localhost:6379
export AI_NURSE_DISABLE_REDIS=0
./.venv/bin/python -m pytest tests/unit/ -q
```

## Troubleshooting
- Tests fail on import of `psycopg`/`pytest-postgresql` (libpq missing): disable the plugin locally when you don't have libpq installed:

```bash
# Temporarily disable plugin
./.venv/bin/python -m pytest -p no:pytest_postgresql -q
```

- Tests hang or time out due to background cache writes: set `AI_NURSE_DISABLE_REDIS=1` to force in-memory cache during tests.

- If you see `pdbpp` import-time errors (pdb hooks during pytest startup), avoid installing `pdbpp` in CI venvs; it's a developer convenience not required for CI.

## Writing tests
- Unit tests: focus on service functions and small utilities. Mock external service clients.
- Integration tests: exercise FastAPI endpoints using `TestClient` and real or containerized dependencies.
- Add an integration marker for slow tests and run them separately in CI or locally with appropriate environment variables.

## Example: simple async test

```python
import pytest

@pytest.mark.asyncio
async def test_async_cache_behavior(async_client):
    resp = await async_client.get('/api/v1/health')
    assert resp.status_code == 200
```
