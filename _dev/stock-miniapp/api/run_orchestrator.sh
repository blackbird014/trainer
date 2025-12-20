#!/bin/bash

# Script to run the orchestrator FastAPI service
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

# Check if monitoring package is installed (required for /monitoring/targets endpoint)
if ! python -c "import monitoring.prometheus_sd" 2>/dev/null; then
    echo "⚠️  Monitoring library not found. Installing..."
    MONITORING_DIR="$(cd "$SCRIPT_DIR/../../monitoring" && pwd)"
    if [ -f "$MONITORING_DIR/pyproject.toml" ]; then
        pip install -e "$MONITORING_DIR" 2>/dev/null || {
            echo "⚠️  Warning: Failed to install monitoring library. /monitoring/targets endpoint will not work."
        }
    fi
fi

# Run the orchestrator service
echo "🚀 Starting Stock Mini-App Orchestrator..."
echo "   Port: ${PORT:-3002}"
echo ""

python orchestrator_service.py

