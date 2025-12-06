#!/bin/bash
# Test runner script for llm-provider module

set -e

echo "=========================================="
echo "LLM Provider - Test Runner"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Must run from llm-provider directory"
    echo "Usage: cd _dev/llm-provider && ./run_tests.sh"
    exit 1
fi

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not detected"
    echo "Please activate your venv first:"
    echo "  source /path/to/venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Virtual environment: $VIRTUAL_ENV"
fi

echo ""
echo "Step 1: Installing dependencies..."
pip install -e ".[dev]" --quiet

echo ""
echo "Step 2: Running tests..."
echo "=========================================="
pytest tests/ -v

echo ""
echo "=========================================="
echo "Tests completed!"
echo "=========================================="
echo ""
echo "To run examples:"
echo "  python examples/basic_usage.py"
echo "  python examples/all_providers.py"
echo "  python examples/registry_usage.py"

