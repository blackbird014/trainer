#!/bin/bash

# Script to run the llm-provider FastAPI service
# Automatically detects and activates venv if present

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for venv in module directory
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || true
elif [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi

# Check if required packages are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI not found. Installing dependencies..."
    if [ -f "pyproject.toml" ]; then
        pip install -e . 2>/dev/null || {
            echo "❌ Failed to install dependencies"
            exit 1
        }
    else
        echo "❌ pyproject.toml not found"
        exit 1
    fi
fi

# Run the API service
python api_service.py

