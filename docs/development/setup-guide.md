# Development Setup Guide
## Complete environment setup and development workflow for AI Nurse Florence

### Quick Start

Get up and running quickly:

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

### Prerequisites

- **Python**: 3.9+ (3.11+ recommended)
- **Redis**: Optional but recommended for caching
- **PostgreSQL**: Optional, SQLite used by default

### Manual setup

Follow the manual steps in the archive or use `./run_dev.sh` for automation.

## ... (content continues from archived setup-guide)
