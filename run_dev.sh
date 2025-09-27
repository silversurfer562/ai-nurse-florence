#!/bin/bash
# AI Nurse Florence - Automated Development Setup
# Following coding instructions for environment setup

set -e

echo "🏥 AI Nurse Florence - Development Setup"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ Please edit .env file with your configuration"
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head 2>/dev/null || echo "⚠️  No migrations to run"

# Start development server
echo "🚀 Starting AI Nurse Florence development server..."
echo "   Medical API: http://localhost:8000/docs"
echo "   Health check: http://localhost:8000/api/v1/health"
echo ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
