#!/bin/bash

# Run tests for data-store module

set -e

echo "Running data-store tests..."

# Change to module directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Install module in editable mode if not already installed
pip install -e . > /dev/null 2>&1 || true

# Install test dependencies
pip install pytest pytest-cov pytest-mock > /dev/null 2>&1 || true

# Run tests
echo "Running pytest..."
pytest tests/ -v --cov=data_store --cov-report=term-missing

echo "Tests completed!"

