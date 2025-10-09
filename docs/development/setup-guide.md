# Development Setup Guide

**Who This Is For**: Developers setting up a local development environment for AI Nurse Florence. You should be comfortable with command-line tools, Python virtual environments, and Git workflows. This guide covers both automated and manual setup processes.

**Prerequisites**:
- **Python**: 3.9+ installed (3.11+ recommended for best performance)
- **Git**: Version control system installed
- **Text Editor/IDE**: VS Code, PyCharm, or similar
- **Terminal Access**: Command-line/bash experience
- **OpenAI API Key**: For AI features (optional but recommended)
- **Redis** (Optional): For caching - improves performance but not required
- **PostgreSQL** (Optional): For production-like setup - SQLite used by default
- **Docker** (Optional): For containerized development

**Time**: 5 minutes with automated script; 15-20 minutes for manual setup.

---

## Table of Contents

- [Quick Start (Automated)](#quick-start-automated)
- [Manual Setup](#manual-setup)
- [Environment Configuration](#environment-configuration)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Related Resources](#related-resources)

---

## Quick Start (Automated)

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

## Manual Setup

For detailed manual setup steps or customization, see the archived setup guide or follow these steps:

1. Create virtual environment
2. Install dependencies from requirements.txt
3. Copy .env.example to .env
4. Configure environment variables
5. Initialize database (optional)
6. Run development server

(Additional manual setup details would continue here...)

---

## Environment Configuration

### Required Variables

```bash
# OpenAI API (Required for AI features)
OPENAI_API_KEY=sk-proj-your-key-here

# Live Services (Optional for development)
USE_LIVE=1  # Set to 0 for stub data during development
```

### Optional Variables

```bash
# Development Database
DATABASE_URL=sqlite+aiosqlite:///./dev.db  # Default

# Redis (Optional)
REDIS_URL=redis://localhost:6379

# Development Settings
LOG_LEVEL=DEBUG
RATE_LIMIT_PER_MINUTE=1000  # Higher limit for dev
```

---

## Related Resources

**For Development:**
- [Developer Guide](../developer_guide.md) - Technical architecture and patterns
- [Quick Start](../getting-started/quick-start.md) - Fast getting started
- [CODING_STANDARDS.md](../../docs/CODING_STANDARDS.md) - Code style guidelines
- [PATTERNS.md](../../docs/PATTERNS.md) - Reusable code patterns

**For Testing:**
- [API Documentation](../technical/api-documentation.md) - Test endpoints
- [Architecture Overview](../technical/architecture-overview.md) - System design

**For Deployment:**
- [Deployment Guide](../technical/deployment-guide.md) - Production deployment
- [DEPLOYMENT_QUICK_START.md](../../DEPLOYMENT_QUICK_START.md) - Quick deploy guide
