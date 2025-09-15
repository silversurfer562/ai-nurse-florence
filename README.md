# Nurse's NIH Toolkit — FastAPI Wrapper (v3)

**Educational Use Only — Not Medical Advice. No PHI stored.**

Endpoints include disease summaries, PubMed search, clinical trials, MedlinePlus summaries, and product endpoints (SBAR, patient education, readability). OpenAPI includes bearerAuth and example responses for nicer GPT Builder previews.

## Development Setup

### VS Code Setup
This project is optimized for VS Code development. To get started:

1. **Open in VS Code**: Open the workspace file `ai-nurse-florence.code-workspace` or open the folder directly in VS Code
2. **Install Extensions**: VS Code will prompt you to install recommended extensions (Python, Pylance, Black formatter, etc.)
3. **Setup Environment**: Run the setup script:
   ```bash
   ./setup-dev.sh
   ```

### Manual Setup
If you prefer manual setup:

1. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Run Development Server**:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

### Available Commands
- **Run Tests**: `pytest`
- **Format Code**: `black .`
- **Lint Code**: `flake8 .`
- **Sort Imports**: `isort .`
- **Type Check**: `mypy .`

### VS Code Features
- **Debugging**: Pre-configured launch configurations for FastAPI and tests
- **Formatting**: Auto-format on save with Black
- **Linting**: Real-time linting with Flake8
- **Testing**: Integrated test discovery and running
- **IntelliSense**: Full Python autocomplete and type checking
