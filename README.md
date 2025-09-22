# AI Nurse Florence — Healthcare AI Assistant

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
- **Live Medical Data**: Real-time access to authoritative medical databases and literature

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

## 📚 Documentation

- [Developer Guide](docs/developer_guide.md)
- [User Guide](docs/nurse_user_guide.md)
- [API Reference](docs/api_reference.md)
- [Deployment Guide](docs/deployment.md)

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

**Deep Study AI, LLC** - Advancing healthcare through responsible AI technology