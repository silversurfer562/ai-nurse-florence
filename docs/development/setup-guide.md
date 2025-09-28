# Development Setup Guide
## Complete environment setup and development workflow for AI Nurse Florence

## Table of Contents
1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Manual Setup](#manual-setup)
4. [Environment Configuration](#environment-configuration)
5. [Development Workflow](#development-workflow)
6. [Testing Setup](#testing-setup)
7. [Docker Development](#docker-development)
8. [IDE Configuration](#ide-configuration)
9. [Common Issues](#common-issues)

## Quick Start

Get up and running in 2 minutes:

```bash
# Clone repository
git clone https://github.com/silversurfer562/ai-nurse-florence.git
cd ai-nurse-florence

# Run automated setup script
./run_dev.sh

# Access the application
# API Docs: http://localhost:8000/docs
# Health: http://localhost:8000/api/v1/health
```

The `run_dev.sh` script automatically:
- Creates Python virtual environment
- Installs all dependencies
- Sets up `.env` file with defaults
- Starts the development server

## Prerequisites

### Required Software
- **Python**: 3.9+ (3.11+ recommended)
- **Git**: For version control
- **Redis**: Optional but recommended for caching
- **PostgreSQL**: Optional, SQLite used by default

### Recommended Tools
- **Docker**: For containerized development
- **VS Code**: With Python extension
- **Postman/Insomnia**: For API testing
- **pgAdmin**: For PostgreSQL management

### System Requirements
- **OS**: Linux, macOS, Windows (WSL2 recommended)
- **RAM**: Minimum 4GB, 8GB recommended
- **Storage**: 2GB free space

## Manual Setup

If you prefer manual setup or the automated script doesn't work:

### Step 1: Clone and Navigate
```bash
git clone https://github.com/silversurfer562/ai-nurse-florence.git
cd ai-nurse-florence
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# On Windows (Git Bash):
source venv/Scripts/activate
```

### Step 3: Upgrade pip
```bash
pip install --upgrade pip
```

### Step 4: Install Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt

# Additional required packages for live services
pip install requests greenlet
```

### Step 5: Create Environment File
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your preferred editor
nano .env  # or vim, code, notepad, etc.
```

### Step 6: Run Development Server
```bash
# Standard development server
uvicorn app:app --reload

# With specific host and port
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# With live medical APIs enabled
export USE_LIVE=1 && uvicorn app:app --reload
```

## Environment Configuration

### Essential Environment Variables

Create a `.env` file with these configurations:

```bash
# ===== CORE CONFIGURATION =====

# OpenAI API (Required for AI features)
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000

# Live Services Toggle
USE_LIVE=1  # Set to 1 for real medical data, 0 for stubs
USE_MYDISEASE=1
USE_MEDLINEPLUS=1
USE_PUBMED=1

# ===== DATABASE CONFIGURATION =====

# Development (SQLite)
DATABASE_URL=sqlite+aiosqlite:///./app.db

# Alternative: PostgreSQL
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/florence_db

# ===== CACHING CONFIGURATION =====

# Redis (optional, fallback to in-memory if not available)
REDIS_URL=redis://localhost:6379/0
AI_NURSE_DISABLE_REDIS=0  # Set to 1 to force in-memory cache

# ===== EXTERNAL APIs (Optional) =====

# NCBI API Key (enhances PubMed rate limits)
NCBI_API_KEY=your-ncbi-api-key-here

# API URLs (defaults are usually fine)
MYDISEASE_API_URL=https://mydisease.info/v1
MEDLINEPLUS_API_URL=https://connect.medlineplus.gov/service
PUBMED_API_URL=https://eutils.ncbi.nlm.nih.gov/entrez/eutils
CLINICALTRIALS_API_URL=https://clinicaltrials.gov/api/v2

# ===== SECURITY CONFIGURATION =====

# JWT Settings
JWT_SECRET_KEY=your-development-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS (update for your frontend)
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=100

# ===== DEVELOPMENT SETTINGS =====

# Environment
PYTHON_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
LOG_FORMAT=json

# Development URLs
APP_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000/api/v1

# Features
ENABLE_SECURITY_HEADERS=false  # Usually disabled in dev
ENABLE_METRICS=true
ENABLE_ACCESS_LOGS=true
```

### Environment File Best Practices

1. **Never commit `.env` to Git** - It's in `.gitignore`
2. **Use `.env.example` as template** - Keep it updated
3. **Different configs for dev/staging/prod** - Use `.env.development`, `.env.production`
4. **Validate on startup** - Check required variables exist

## Development Workflow

### Standard Development Flow

```bash
# 1. Start your day
cd ai-nurse-florence
git pull origin main
source venv/bin/activate

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Start development server
./run_dev.sh  # or uvicorn app:app --reload

# 4. Make changes and test
# Edit files...
# Test at http://localhost:8000/docs

# 5. Run tests
pytest
pytest --cov=.  # With coverage

# 6. Lint and format
black .
flake8 .
mypy --ignore-missing-imports .

# 7. Commit changes
git add .
git commit -m "feat: add new feature"

# 8. Push and create PR
git push origin feature/your-feature-name
```

### Working with Live Medical APIs

```bash
# Enable live services
export USE_LIVE=1

# Test individual services
python -c "
from services.disease_service import lookup_disease
result = lookup_disease('diabetes')
print(f'Disease lookup: {result}')
"

# Monitor API calls
tail -f logs/external_api.log
```

### Database Management

```bash
# Create initial database
python -c "
from database import engine, Base
import asyncio
async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init())
"

# Run migrations (if using Alembic)
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Testing Setup

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_disease_service.py

# Run specific test function
pytest tests/test_disease_service.py::test_lookup_disease

# Run with coverage
pytest --cov=. --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
pytest -m integration

# Verbose output
pytest -v

# Show print statements
pytest -s
```

### Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_example.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    """Test health endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_async_function():
    """Test async functionality"""
    result = await some_async_function()
    assert result is not None

@pytest.fixture
def mock_openai(monkeypatch):
    """Mock OpenAI API calls"""
    def mock_completion(*args, **kwargs):
        return {"choices": [{"message": {"content": "Mocked response"}}]}
    
    monkeypatch.setattr("openai.ChatCompletion.create", mock_completion)
```

## Docker Development

### Docker Compose Development Setup

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  app:
    build: .
    volumes:
      - .:/app  # Mount code for hot reload
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/florence
      - REDIS_URL=redis://redis:6379
      - USE_LIVE=1
    ports:
      - "8000:8000"
    command: uvicorn app:app --reload --host 0.0.0.0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=florence
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "5050:80"

volumes:
  postgres_data:
```

### Docker Commands

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Start in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f app

# Rebuild after requirements change
docker-compose -f docker-compose.dev.yml build

# Execute commands in container
docker-compose -f docker-compose.dev.yml exec app pytest

# Stop all services
docker-compose -f docker-compose.dev.yml down
```

## IDE Configuration

### VS Code Setup

`.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--max-line-length=120"],
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    "htmlcov": true
  }
}
```

`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app:app", "--reload"],
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"]
    }
  ]
}
```

### PyCharm Setup

1. **Configure Python Interpreter**: 
   - File → Settings → Project → Python Interpreter
   - Select virtual environment

2. **Configure Run Configuration**:
   - Run → Edit Configurations
   - Add new Python configuration
   - Script path: `uvicorn`
   - Parameters: `app:app --reload`

3. **Enable Django Support** (for templates):
   - Settings → Languages & Frameworks → Django
   - Enable Django support

## Common Issues

### Issue: ModuleNotFoundError
```bash
# Solution 1: Ensure virtual environment is activated
source venv/bin/activate

# Solution 2: Reinstall dependencies
pip install -r requirements.txt

# Solution 3: Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Redis Connection Error
```bash
# Solution 1: Start Redis
redis-server

# Solution 2: Use in-memory cache fallback
export AI_NURSE_DISABLE_REDIS=1

# Solution 3: Check Redis is running
redis-cli ping  # Should return PONG
```

### Issue: Database Connection Error
```bash
# Solution 1: Use SQLite for development
export DATABASE_URL=sqlite+aiosqlite:///./app.db

# Solution 2: Start PostgreSQL
sudo service postgresql start

# Solution 3: Create database
createdb florence_db
```

### Issue: OpenAI API Error
```bash
# Solution 1: Check API key is set
echo $OPENAI_API_KEY

# Solution 2: Verify API key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Solution 3: Use development stubs
export USE_LIVE=0
```

### Issue: Port Already in Use
```bash
# Solution 1: Use different port
uvicorn app:app --reload --port 8001

# Solution 2: Find and kill process using port
lsof -i :8000
kill -9 <PID>

# Solution 3: Use Docker with port mapping
docker run -p 8001:8000 ai-nurse-florence
```

## Development Best Practices

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions small
- Use meaningful variable names

### Git Workflow
- Create feature branches
- Write descriptive commit messages
- Keep commits atomic
- Rebase before merging
- Delete merged branches

### Testing
- Write tests for new features
- Maintain >80% coverage
- Test edge cases
- Use fixtures for common setup
- Mock external dependencies

### Security
- Never commit secrets
- Validate all inputs
- Sanitize outputs
- Use parameterized queries
- Keep dependencies updated

---

**Last Updated**: September 2025  
**Development Version**: 2.0.0  
**Python Version**: 3.9+
