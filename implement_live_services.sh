#!/bin/bash
# Script to implement and test live services for AI Nurse Florence

echo "🏥 AI Nurse Florence - Live Services Implementation"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run ./run_dev.sh first"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if USE_LIVE is enabled
USE_LIVE_STATUS=$(grep "USE_LIVE" .env | cut -d'=' -f2)
if [ "$USE_LIVE_STATUS" = "1" ]; then
    echo "✅ Live services are ENABLED (USE_LIVE=1)"
else
    echo "⚠️  Live services are DISABLED (USE_LIVE=0)"
    echo "   Set USE_LIVE=1 in .env to enable live services"
fi

# Check OpenAI API key
OPENAI_KEY=$(grep "OPENAI_API_KEY" .env | cut -d'=' -f2)
if [ -z "$OPENAI_KEY" ]; then
    echo "⚠️  OpenAI API key is not set"
    echo "   Add your OpenAI API key to .env for AI features"
else
    echo "✅ OpenAI API key is configured"
fi

echo ""
echo "🧪 Testing Live Services..."
echo "============================="

# Test each live service
echo "Testing MyDisease.info service..."
python3 -c "
try:
    import live_mydisease
    print('✅ MyDisease.info connector available')
except Exception as e:
    print(f'❌ MyDisease.info error: {e}')
"

echo "Testing PubMed service..."
python3 -c "
try:
    import live_pubmed
    print('✅ PubMed connector available')
except Exception as e:
    print(f'❌ PubMed error: {e}')
"

echo "Testing ClinicalTrials service..."
python3 -c "
try:
    import live_clinicaltrials
    print('✅ ClinicalTrials connector available')
except Exception as e:
    print(f'❌ ClinicalTrials error: {e}')
"

echo ""
echo "🚀 Starting development server..."
echo "================================="
echo "Server will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"

# Start the FastAPI server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
