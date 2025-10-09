# Tutorial Examples

---
**License**: Apache License 2.0
**Copyright**: © 2025 Deep Study AI, LLC
**Project**: AI Nurse Florence
**Repository**: https://github.com/silversurfer562/ai-nurse-florence
---

This directory contains working code examples from the AI Nurse Florence tutorials.

## Files

### `patient_age_service.py`
Complete service implementation from [Tutorial 4: Adding a New Service Method](../docs/tutorials/04-adding-service-method.md)

**What it demonstrates**:
- Service Layer Pattern
- Type hints and documentation
- Clinical age calculation logic
- Error handling and validation
- Age category classification

**Run it**:
```bash
python examples/patient_age_service.py
```

### `test_patient_age.py`
Complete test suite from [Tutorial 5: Writing Tests for Healthcare Code](../docs/tutorials/05-writing-healthcare-tests.md)

**What it demonstrates**:
- Arrange-Act-Assert test pattern
- pytest fixtures for reusable data
- Testing all clinical age categories
- Edge case testing (leap years, boundaries)
- Error handling tests
- Test coverage measurement

**Run it**:
```bash
# Run tests with verbose output
pytest examples/test_patient_age.py -v

# Run tests with coverage report
pytest examples/test_patient_age.py --cov=examples.patient_age_service --cov-report=term-missing

# Run tests with HTML coverage report
pytest examples/test_patient_age.py --cov=examples.patient_age_service --cov-report=html
```

## How to Use These Examples

### As Reference
Copy patterns from these examples when implementing your own features.

### As Learning Tools
Read through the code to understand:
- How services are structured
- How to write comprehensive tests
- How to document code with clinical context

### As Starting Points
Copy and modify these files to create your own features:
```bash
# Copy service template
cp examples/patient_age_service.py src/services/my_new_service.py

# Copy test template
cp examples/test_patient_age.py tests/unit/test_my_new_service.py

# Modify for your use case
```

## Related Tutorials

These examples correspond to specific tutorials in the learning path:

1. [Environment Setup](../docs/tutorials/01-environment-setup.md) (30 min)
2. [Understanding the Codebase](../docs/tutorials/02-understanding-codebase.md) (30 min)
3. [Your First Disease Lookup](../docs/tutorials/03-first-patient-lookup.md) (45 min)
4. [Adding a New Service Method](../docs/tutorials/04-adding-service-method.md) (60 min) ← `patient_age_service.py`
5. [Writing Tests for Healthcare Code](../docs/tutorials/05-writing-healthcare-tests.md) (45 min) ← `test_patient_age.py`
6. [Your First Pull Request](../docs/tutorials/06-first-pull-request.md) (30 min)

**Start the learning path**: [docs/tutorials/README.md](../docs/tutorials/README.md)

## Code Quality

Both example files follow project standards:
- Service Layer Pattern from [PATTERNS.md](../docs/PATTERNS.md)
- Coding standards from [CODING_STANDARDS.md](../docs/CODING_STANDARDS.md)
- Documentation policy from [DOCUMENTATION_POLICY.md](../docs/DOCUMENTATION_POLICY.md)

Use these as templates to ensure your code follows project conventions.
