# Quick Start Guide
## Get AI Nurse Florence running in 5 minutes

## 🚀 Fastest Setup (2 minutes)

### Prerequisites
- Python 3.9+ installed
- Git installed
- OpenAI API key (optional, but recommended)

### Three Simple Steps

```bash
# 1. Clone and enter directory
git clone https://github.com/silversurfer562/ai-nurse-florence.git
cd ai-nurse-florence

# 2. Run automated setup
./run_dev.sh

# 3. Open in browser
# Visit: http://localhost:8000/docs
```

**That's it!** You're now running AI Nurse Florence locally.

## 🔑 Quick Configuration

### Add Your OpenAI Key (Recommended)
Edit the `.env` file created by the setup script:

```bash
# Open .env file
nano .env

# Add your OpenAI API key
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Save and restart server
```

### Enable Live Medical Data
```bash
# In .env file, set:
USE_LIVE=1
```

## 🧪 Test It's Working

### 1. Check Health Endpoint
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-28T10:00:00Z"
}
```

### 2. Try Disease Lookup
```bash
curl "http://localhost:8000/api/v1/disease?q=diabetes"
```

### 3. Explore API Documentation
Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Common Use Cases

### For Healthcare Professionals

#### Look up a disease
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/disease",
    params={"q": "hypertension"}
)
print(response.json())
```

#### Search medical literature
```python
response = requests.get(
    "http://localhost:8000/api/v1/pubmed",
    params={"q": "diabetes treatment", "max_results": 5}
)
print(response.json())
```

#### Start treatment plan wizard
```python
# Start wizard
start_response = requests.post(
    "http://localhost:8000/api/v1/wizards/treatment-plan/start"
)
wizard_id = start_response.json()["data"]["wizard_id"]

# Add assessment
requests.post(
    "http://localhost:8000/api/v1/wizards/treatment-plan/assessment",
    json={"wizard_id": wizard_id, "text": "Patient assessment..."}
)
```

### For Developers

#### Run with custom settings
```bash
# Custom port
uvicorn app:app --reload --port 8001

# With all debug output
LOG_LEVEL=DEBUG uvicorn app:app --reload

# With specific number of workers
uvicorn app:app --workers 4
```

#### Use Docker instead
```bash
# Build and run with Docker
docker build -t ai-nurse-florence .
docker run -p 8000:8000 ai-nurse-florence
```

## 🔧 Quick Troubleshooting

### Server won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt
```

### Module not found errors
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Port already in use
```bash
# Use different port
uvicorn app:app --reload --port 8001
```

### No medical data returned
```bash
# Enable live services in .env
USE_LIVE=1
```

## 📱 What Can You Do Now?

With AI Nurse Florence running, you can:

1. **Disease Information** - Look up any medical condition
2. **Literature Search** - Find relevant medical research
3. **Clinical Trials** - Discover active clinical studies  
4. **Treatment Plans** - Generate evidence-based care plans
5. **SBAR Reports** - Create structured clinical reports
6. **Patient Education** - Generate educational materials
7. **Risk Assessments** - Calculate clinical risk scores

## 🚀 Next Steps

### For Production Deployment
See [Railway Deployment Guide](../deployment/railway.md)

### For Development
See [Development Setup Guide](../development/setup-guide.md)

### For Clinical Features
See [Clinical Workflows](../clinical/clinical-workflows.md)

### For API Integration
See [API Documentation](../technical/api-documentation.md)

## 🆘 Getting Help

- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: [Report bugs](https://github.com/silversurfer562/ai-nurse-florence/issues)
- **Full Documentation**: [Documentation Index](../README.md)

---

**Quick Start Version**: 1.0.0  
**Time to First API Call**: < 5 minutes  
**No PHI Storage** | **Educational Use Only**
