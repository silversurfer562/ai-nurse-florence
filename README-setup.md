Quick re-setup guide for ai-nurse-florence

1) Create a Python virtual environment and install dependencies

   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # optional for tests

2) Environment

   - Create a `.env` file if you need API keys (OpenAI, PubMed, etc.). The app reads env vars directly.

3) Run tests (basic)

   source .venv/bin/activate
   pytest -q

4) Run the server locally

   source .venv/bin/activate
   uvicorn app:app --reload

Notes

- This project targets Python 3.12+ based on pyc files in the repo.
- If you use Homebrew Python or pyenv, adjust the `python3` command accordingly.

Developer notes
----------------

- APP_BASE_URL and FORCE_HTTPS

   - The application exposes a `APP_BASE_URL` environment variable (set in your `.env`) which, when present, will be used as the canonical public base URL for the app (used in OpenAPI `servers` and the health endpoints).
   - If `APP_BASE_URL` is not set, the application constructs a base URL from `HOST` and `PORT`. Set `FORCE_HTTPS=true` to force an `https://` scheme when constructing the base URL in environments where TLS is terminated upstream.

- Router registration convention

   - Register routers once on the central `api_router` (defined in `app.py` with prefix `/api/v1`). This prevents duplicate OpenAPI operation IDs.
   - If an alias path is required for backward compatibility (for example `/api/v1/wizards`), include the router as an alias but mark non-primary aliases with `include_in_schema=False` or ensure operation IDs stay unique.

