# Quick Testing Guide

This file provides quick commands and references for maintainers to run tests and reproduce CI-like runs locally.

Use the project venv to run tests in a way that matches CI behavior (CI disables Redis for hermetic tests):

```bash
export PYTHONPATH=$(pwd)
export AI_NURSE_DISABLE_REDIS=1
./.venv/bin/python -m pytest -p no:pytest_postgresql -q
```

Run unit tests only:

```bash
./.venv/bin/python -m pytest tests/unit/ -q
```

Run a single test file (verbose):

```bash
AI_NURSE_DISABLE_REDIS=1 ./.venv/bin/python -m pytest tests/unit/test_cache_concurrency.py -q -vv -s -x
```

Run integration tests (requires live services):

```bash
export AI_NURSE_DISABLE_REDIS=0
./.venv/bin/python -m pytest -m integration -q
```

Troubleshooting
- If pytest errors about `psycopg` / libpq, run with `-p no:pytest_postgresql` as shown above.
- If tests hang due to background cache writes, set `AI_NURSE_DISABLE_REDIS=1`.
- If `pdbpp` causes import-time errors, remove it from the venv for CI runs.

See `docs/development/testing-strategy.md` for the full testing strategy and guidelines.
