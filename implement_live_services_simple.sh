#!/bin/bash

# AI Nurse Florence - Live Services Implementation (No Redis)
# Testing live services without Celery background tasks

set -e

echo "🏥 AI Nurse Florence - Live Services Implementation (Simplified)"
echo "=============================================================="

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if USE_LIVE is enabled
if grep -q "USE_LIVE=1" .env; then
    echo "✅ Live services are ENABLED (USE_LIVE=1)"
else
    echo "❌ Live services are DISABLED. Set USE_LIVE=1 in .env"
    exit 1
fi

# Check OpenAI API key
if grep -q "OPENAI_API_KEY=\$" .env || grep -q "OPENAI_API_KEY=$" .env; then
    echo "⚠️  OpenAI API key is not set"
    echo "   Add your OpenAI API key to .env for AI features"
else
    echo "✅ OpenAI API key is configured"
fi

echo ""
echo "🧪 Testing Live Services..."
echo "============================="

# Test individual live services
echo "Testing MyDisease.info service..."
python -c "
import sys
sys.path.append('.')
try:
    from live_mydisease import get_disease_info
    result = get_disease_info('diabetes')
    if result and 'summary' in result:
        print('✅ MyDisease.info service working')
    else:
        print('⚠️  MyDisease.info returned empty result')
except Exception as e:
    print(f'❌ MyDisease.info error: {e}')
"

echo "Testing PubMed service..."
python -c "
import sys
sys.path.append('.')
try:
    from live_pubmed import search_pubmed
    result = search_pubmed('diabetes treatment', retmax=1)
    if result and result.get('papers'):
        print('✅ PubMed service working')
    else:
        print('⚠️  PubMed returned empty result')
except Exception as e:
    print(f'❌ PubMed error: {e}')
"

echo "Testing ClinicalTrials service..."
python -c "
import sys
sys.path.append('.')
try:
    from live_clinicaltrials import search_trials
    result = search_trials('diabetes', max_studies=1)
    if result and result.get('studies'):
        print('✅ ClinicalTrials service working')
    else:
        print('⚠️  ClinicalTrials returned empty result')
except Exception as e:
    print(f'❌ ClinicalTrials error: {e}')
"

echo ""
echo "📋 Configuration Summary:"
echo "========================"
echo "• Live services: ENABLED"
echo "• External APIs: MyDisease.info, PubMed, ClinicalTrials.gov"
echo "• Background tasks: DISABLED (no Redis/Celery)"
echo "• Database: SQLite (configured)"
echo "• Caching: In-memory fallback"

echo ""
echo "⚠️  Note: Some features requiring Celery background tasks will be disabled:"
echo "   • Long-running summarization tasks"
echo "   • Background document processing"
echo "   • Task queue status tracking"

echo ""
echo "🚀 Starting development server (no Celery)..."
echo "=============================================="
echo "Server will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"

# Start server without Celery imports by temporarily renaming the problematic import
mv services/tasks.py services/tasks.py.backup 2>/dev/null || true
echo "# Celery tasks disabled for Redis-free development" > services/tasks.py

# Also need to handle the import in routers/summarize.py
if grep -q "from services.tasks import summarize_text_task" routers/summarize.py; then
    sed -i.backup 's/from services.tasks import summarize_text_task/# from services.tasks import summarize_text_task  # Disabled for Redis-free dev/' routers/summarize.py
fi

# Start the server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
