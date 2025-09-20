# AI Nurse Florence — Healthcare AI Assistant

**A Public Benefit Technology Initiative by Deep Study AI, LLC**

> **Mission**: Deep Study AI, LLC is committed to advancing healthcare accessibility and quality through responsible AI technology that empowers healthcare professionals with evidence-based information tools, while prioritizing patient safety, data privacy, and equitable access to medical knowledge.

**Educational Use Only — Not Medical Advice. No PHI stored.**

AI Nurse Florence is a FastAPI-based healthcare information assistant that provides reliable medical information through various endpoints including disease summaries, PubMed search, clinical trials, MedlinePlus summaries, and clinical documentation tools.

## 🏥 Core Features

- **Disease Information**: Comprehensive condition summaries with evidence-based references
- **Literature Search**: PubMed integration for medical research access
- **Clinical Trials**: Search and discovery of relevant clinical studies
- **Patient Education**: Readability-optimized health information materials
- **Clinical Documentation**: SBAR report generation and summarization tools
- **Prompt Enhancement**: Intelligent query clarification and improvement

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Development Server**
   ```bash
   uvicorn app:app --reload
   ```

4. **Access Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🔧 Key Endpoints

- **Health Check**: `GET /api/health`
- **Disease Lookup**: `GET /v1/disease?q=diabetes`
- **PubMed Search**: `GET /v1/pubmed/search?q=COPD`
- **Clinical Trials**: `GET /v1/clinicaltrials/search?condition=cancer`
- **Text Summarization**: `POST /summarize/chat`

## 🏗️ Architecture

- **FastAPI Backend**: High-performance async API framework
- **OpenAI Integration**: GPT models for intelligent content generation
- **Caching Layer**: Redis-backed caching for performance
- **Monitoring**: Prometheus metrics and health checks
- **Authentication**: OAuth2 JWT-based security

## 📚 Documentation

- [Developer Guide](docs/developer_guide.md)
- [User Guide](docs/nurse_user_guide.md)
- [API Reference](docs/api_reference.md)
- [Deployment Guide](docs/deployment.md)

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

## 🛠️ Development

### Quick Testing
For development and testing without external dependencies:
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run unit tests for core services
python test_runner.py

# Run full test suite (requires Redis/database setup)
pytest
```

### Environment Setup
- Copy `.env.example` to `.env` and configure required variables
- For basic development, only `API_BEARER` is required
- For full functionality, configure `OPENAI_API_KEY` and `REDIS_URL`

### Code Quality
```bash
# The project follows standard Python practices
flake8 .
mypy .
```

## 🛡️ Medical Disclaimer

AI Nurse Florence provides educational information for healthcare professionals. All content is for informational purposes only and does not constitute medical advice. Always consult qualified healthcare providers for medical decisions.

---

**Deep Study AI, LLC** - Advancing healthcare through responsible AI technology