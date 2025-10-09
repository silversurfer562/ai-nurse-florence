# AI Nurse Florence — Healthcare AI Assistant

**Who This Is For**: Healthcare professionals (nurses, nurse practitioners, physician assistants), medical students, and developers building clinical information systems. If you provide patient care or develop healthcare technology, this platform supports your evidence-based practice with live medical data and clinical documentation tools.

**🚀 Production-Ready Platform with Live Medical APIs**

**A Public Benefit Technology Initiative by Deep Study AI, LLC**

> **Mission**: Deep Study AI, LLC is committed to advancing healthcare accessibility and quality through responsible AI technology that empowers healthcare professionals with evidence-based information tools, while prioritizing patient safety, data privacy, and equitable access to medical knowledge.

**Educational Use Only — Not Medical Advice. No PHI stored.**

AI Nurse Florence is a **production-ready** FastAPI-based healthcare information assistant that provides **live medical data** from verified APIs including MyDisease.info, PubMed/NCBI, ClinicalTrials.gov, and MedlinePlus, with professional clinical documentation tools and evidence-based decision support.

## ✅ **Current Status: PRODUCTION-READY**
- **Live API Integrations**: ✅ All medical data sources verified and working
- **GitHub Updated**: ✅ 78 files enhanced with comprehensive improvements  
- **Railway Deployment**: ✅ Production-optimized cloud hosting
- **Live Data Verified**: ✅ Tested returning real medical information from authoritative sources

## 🏥 Core Features

- **Disease Information**: Live integration with MyDisease.info for comprehensive condition summaries with evidence-based references
- **Literature Search**: Real-time PubMed/NCBI integration for medical research access with 35M+ articles
- **Clinical Trials**: Live ClinicalTrials.gov API v2 integration for current clinical studies discovery
- **Patient Education**: Readability-optimized health information materials via MedlinePlus
- **Clinical Documentation**: SBAR report generation and summarization tools
- **Prompt Enhancement**: Intelligent query clarification and improvement with context-aware suggestions
- **Drug Interaction Checker**: ✅ **Deterministic & Reliable** - Uses rule-based algorithms with structured drug interaction database for 100% auditable, safety-critical checking. AI assists with database updates only, NOT clinical decisions. Every interaction flag is traceable and documented.
- **Live Medical Data**: Real-time access to authoritative medical databases and literature

### 🔑 API Requirements

- **Required**: OpenAI API key (for Claude AI patient education and database content management)
- **Optional**: NCBI API key (for PubMed rate limit increases)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
./run_dev.sh  # Automated setup: venv, deps, .env creation, uvicorn
```

### Option 2: Manual Setup
1. **Setup Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (OpenAI required, NCBI optional for PubMed)
   ```

3. **Install Dependencies for Live Services**
   ```bash
   pip install requests greenlet  # Required for live medical APIs
   ```

4. **Run Development Server**
   ```bash
   export USE_LIVE=1  # Enable live services (optional, defaults to stubs)
   uvicorn app:app --reload
   ```

5. **Access Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🔧 API Endpoints & Live Services

### Core Medical APIs
- **Health Check**: `GET /api/v1/health` - System status and dependencies
- **Disease Lookup**: `GET /api/v1/disease?q=diabetes` - Live MyDisease.info integration
- **PubMed Search**: `GET /api/v1/pubmed?q=hypertension&max_results=10` - Real-time literature search
- **Clinical Trials**: `GET /api/v1/trials?condition=cancer&max_results=10` - Live ClinicalTrials.gov v2 API
- **Patient Education**: `GET /api/v1/patient-education?q=heart+disease` - MedlinePlus integration

### AI-Powered Features
- **Text Summarization**: `POST /api/v1/summarize` - Medical text summarization
- **SBAR Reports**: Clinical documentation wizard endpoints
- **Readability Analysis**: `POST /api/v1/readability` - Health literacy optimization

### Live Service Details

#### MyDisease.info Integration
- **Database**: Comprehensive disease information aggregation
- **Rate Limits**: No authentication required, reasonable use expected
- **Data Fields**: Disease names, definitions, references, cross-references
- **Response Time**: ~1-2 seconds average

#### PubMed/NCBI Integration  
- **Database**: 35+ million medical literature citations
- **Rate Limits**: 3 requests/second (10/second with API key)
- **API Key**: Set `NCBI_API_KEY` in .env for enhanced limits
- **Search Fields**: Title, abstract, authors, keywords, MeSH terms

#### ClinicalTrials.gov Integration
- **Database**: Current and completed clinical studies worldwide
- **API Version**: v2 (current stable API)
- **Rate Limits**: No authentication required, reasonable use expected
- **Filters**: Condition, status, location, study type

## 🏗️ Architecture

- **FastAPI Backend**: High-performance async API framework with live medical data integration
- **Live Medical APIs**: Real-time access to MyDisease.info, PubMed/NCBI, ClinicalTrials.gov
- **OpenAI Integration**: GPT models for intelligent content generation and query enhancement
- **Caching Layer**: Redis-backed caching with in-memory fallback for development
- **Conditional Loading**: Graceful degradation when external services unavailable
- **Monitoring**: Prometheus metrics, structured logging, and comprehensive health checks
- **Authentication**: OAuth2 JWT-based security with API key support
- **Rate Limiting**: Configurable per-endpoint rate limiting with Redis backend

## ⚙️ Configuration & Environment Variables

### Required Environment Variables
```bash
# OpenAI (Required for AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Live Services (Optional - enables real medical data)
USE_LIVE=1  # Set to 1 to enable live APIs, 0 for development stubs

# External API Keys (Optional but recommended)
NCBI_API_KEY=your_ncbi_api_key  # Increases PubMed rate limits from 3/sec to 10/sec
```

### Optional Configuration
```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db  # Default: SQLite, Production: PostgreSQL

# Redis (Optional - improves performance)
REDIS_URL=redis://localhost:6379  # Falls back to in-memory cache if unavailable

CI / Testing note
-----------------

If Redis is not available in your test or CI environment, set the environment variable:

```bash
export AI_NURSE_DISABLE_REDIS=1
```

This forces the application to use the in-memory fallback for caching and rate limiting. The project's CI workflow runs a small healthcheck (`scripts/check_redis_health.py`) to ensure future changes do not accidentally make Redis required.

## Testing & development toggles

- AI_NURSE_DISABLE_REDIS
   - Usage: `export AI_NURSE_DISABLE_REDIS=1`
   - Effect: Forces the app to use the in-memory fallback for both the caching layer and the rate limiter. Use this in CI or local test runs when Redis is not available or when you want deterministic, fast tests.

- Async-first caching decorator (how it behaves in tests)
   - The caching decorator used across services is "async-first": it awaits cache lookups for async callables and supports sync callables as well.
   - For sync callables the decorator returns an immediate in-memory cached value (if available) and schedules a non-blocking background update to Redis to keep the remote cache warm. This background update is best-effort and intentionally non-blocking so tests and sync code don't deadlock.
   - Implication for tests: set `AI_NURSE_DISABLE_REDIS=1` to avoid timing-dependent background updates, or use the provided test utilities/monkeypatches to force synchronous cache behavior when you need to assert Redis writes.

- Quick troubleshooting
   - Tests hang on Redis calls? Set `AI_NURSE_DISABLE_REDIS=1` before running pytest.
   - Pytest complains about missing libpq / pytest-postgresql plugin locally? Either install system `libpq`/`psycopg` or run tests locally with the plugin disabled: `pytest -p no:pytest_postgresql`.

The CI job runs the healthcheck script and the test suite with Redis effectively disabled to keep the CI environment hermetic and fast.

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60  # Default: 60 requests per minute per IP

# CORS
CORS_ORIGINS=["http://localhost:3000"]  # Frontend origins
```

### API Rate Limits & Best Practices

#### PubMed/NCBI API
- **Without API Key**: 3 requests/second, 100 requests/hour
- **With API Key**: 10 requests/second, no hourly limit  
- **Best Practice**: Register for free NCBI API key at https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/

#### MyDisease.info API
- **Rate Limits**: No authentication required, reasonable use expected
- **Best Practice**: Cache responses locally, avoid rapid successive calls

#### ClinicalTrials.gov API
- **Rate Limits**: No authentication required, reasonable use expected  
- **Best Practice**: Use specific search terms, limit result counts appropriately

#### OpenAI API
- **Rate Limits**: Varies by plan and model
- **Best Practice**: Implement exponential backoff, monitor usage in OpenAI dashboard

## 📚 Full Documentation

**This README is your starting point.** For complete project documentation, architecture details, development history, and contribution guidelines, see the **[MASTER_DOC.md](./MASTER_DOC.md)** — the central "brain" of the project.

**Quick Navigation by Role:**
- **Nurses & Healthcare Professionals** → Start with [Nurse User Guide](./docs/clinical/nurse_user_guide.md)
- **Developers** → Start with [Developer Guide](./docs/developer_guide.md) or [Quick Start](./docs/getting-started/quick-start.md)
- **DevOps/System Administrators** → Start with [Deployment Guide](./docs/technical/deployment-guide.md)
- **Contributors** → Start with [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Decision Makers** → Start with [Development Philosophy](./docs/DEVELOPMENT_PHILOSOPHY.md)

### Development Philosophy & Standards

- **[Development Philosophy](./docs/DEVELOPMENT_PHILOSOPHY.md)** — Core principles guiding AI Nurse Florence
- **[Coding Standards](./docs/CODING_STANDARDS.md)** — Python, FastAPI, and healthcare-specific code standards
- **[Code Patterns](./docs/PATTERNS.md)** — Reusable patterns for services, routers, and integrations
- **[Architectural Decisions](./docs/adr/)** — ADRs documenting key technical decisions

### Essential Resources

- **[MASTER_DOC.md](./MASTER_DOC.md)** — Project navigation hub and central knowledge base
- **[Developer Guide](./docs/developer_guide.md)** — Technical documentation for developers
- **[Nurse User Guide](./docs/clinical/nurse_user_guide.md)** — Comprehensive guide for healthcare professionals
- **[Architecture Overview](./docs/technical/architecture-overview.md)** — System design and components
- **[API Documentation](./docs/technical/api-documentation.md)** — Detailed API reference (also at `/docs`)
- **[Development Roadmap](./docs/DEVELOPMENT_ROADMAP.md)** — Project phases and future plans

### Quick Links

| Resource | Description |
|----------|-------------|
| [MASTER_DOC.md](./MASTER_DOC.md) | Central project brain and knowledge base |
| [Development Philosophy](./docs/DEVELOPMENT_PHILOSOPHY.md) | Core principles and values |
| [Live API Docs](http://localhost:8000/docs) | Interactive Swagger UI (when running locally) |
| [Deployment Guide](./docs/technical/deployment-guide.md) | Production deployment instructions |
| [Contributing Guide](./CONTRIBUTING.md) | How to contribute to this public benefit initiative |

## 💝 Support This Project

AI Nurse Florence is a public benefit technology initiative that improves healthcare accessibility through open-source AI. Your support helps advance healthcare technology for the global community.

### 🌟 Why Support AI Nurse Florence?
- **Saves Lives**: Faster access to medical information improves patient outcomes
- **Global Impact**: Supports healthcare workers worldwide, especially in underserved areas
- **Open Source**: All code is freely available for research and improvement
- **Evidence-Based**: Promotes best practices in medical care

### 💖 How to Support
- ⭐ **Star this repository** to show your support
- 🐛 **Report bugs** and suggest features
- 💰 **Financial support** via [GitHub Sponsors](https://github.com/sponsors/silversurfer562)
- 🤝 **Contribute code** - see [CONTRIBUTING.md](CONTRIBUTING.md)
- 📢 **Share** with healthcare networks and colleagues

For detailed funding information, see [FUNDING.md](FUNDING.md).

## 🤝 Contributing

We welcome contributions that align with our public benefit mission of improving healthcare accessibility. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License & Notice

This project is developed as a public benefit technology initiative. See [NOTICE](NOTICE) for details on our public benefit commitment and [LICENSE](LICENSE) for usage terms.

## ⚖️ Public Benefit Commitment

As a public benefit corporation technology initiative, this project prioritizes:
- Healthcare accessibility and equity
- Evidence-based medical information
- Patient safety and privacy
- Open, responsible AI development
- Community health outcomes

## 🛡️ Medical Disclaimer

AI Nurse Florence provides educational information for healthcare professionals. All content is for informational purposes only and does not constitute medical advice. Always consult qualified healthcare providers for medical decisions.

---

## Related Resources

- [MASTER_DOC.md](./MASTER_DOC.md) - Central project knowledge base
- [Development Philosophy](./docs/DEVELOPMENT_PHILOSOPHY.md) - Core principles
- [API Documentation](./docs/technical/api-documentation.md) - Complete API reference
- [Architecture Overview](./docs/technical/architecture-overview.md) - System design
- [Clinical Workflows](./docs/clinical/clinical-workflows.md) - Healthcare use cases

---

**Deep Study AI, LLC** - Advancing healthcare through responsible AI technology# Deployed Mon Sep 22 16:47:47 EDT 2025
# Force rebuild
