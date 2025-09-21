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
