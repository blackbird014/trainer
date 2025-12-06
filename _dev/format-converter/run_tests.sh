#!/bin/bash

# Test runner script for format-converter module

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Format Converter Test Suite"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo "⚠️  pytest not found. Installing dependencies..."
    
    # Try to install in a virtual environment
    if [ ! -d ".test_venv" ]; then
        echo "Creating test virtual environment..."
        python3 -m venv .test_venv
    fi
    
    echo "Activating virtual environment..."
    source .test_venv/bin/activate
    
    echo "Installing test dependencies..."
    pip install -e ".[dev]" > /dev/null 2>&1 || pip install pytest pytest-cov pytest-mock
fi

echo "Running tests..."
echo ""

# Run tests
python3 -m pytest tests/ -v --tb=short

echo ""
echo "=========================================="
echo "Tests completed!"
echo "=========================================="

