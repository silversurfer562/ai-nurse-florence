#!/bin/bash

# Development environment setup script for ai-nurse-florence

echo "Setting up development environment for ai-nurse-florence..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install production dependencies
echo "Installing production dependencies..."
pip install -r requirements.txt

# Install development dependencies  
echo "Installing development dependencies..."
pip install -r requirements-dev.txt

echo "Development environment setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the FastAPI development server, run:"
echo "  uvicorn app:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "To run tests, use:"
echo "  pytest"
echo ""
echo "Open the project in VS Code with:"
echo "  code ai-nurse-florence.code-workspace"