# Contributing Guide
## Development contribution guidelines

This guide provides an outline for contributing to AI Nurse Florence.

### Code style and workflow
- Follow the Service Layer Architecture: `services/` for business logic, `routers/` for endpoints, `utils/` for shared utilities.
- Use feature branches: `feature/<short-desc>` and open a PR against `main`.
- Run tests and linters before opening a PR:
	```bash
	pytest
	black .
	flake8 .
	mypy --ignore-missing-imports .
	```

### Testing and mocking
- Use fixtures in `tests/conftest.py` for service mocks.
- Mock external services (PubMed, MyDisease, ClinicalTrials) with type-safe fixtures that match Pydantic schemas.

### Pull Requests
- Write a clear PR description with rationale and testing steps.
- Add reviewers and link related issues.
- Keep PRs small and focused when possible.

### Code reviews
- Maintain backwards compatibility for public APIs.
- Ensure new external calls are cached and have fallbacks when possible.

### Licensing and expectations
- All contributions are under the project's license. See `LICENSE` for details.
