#!/bin/bash
# Run data-retriever API service with automatic venv activation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv if it exists (automatic, no need to ask)
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check if yfinance is available (optional dependency)
if python -c "import yfinance" 2>/dev/null; then
    YFINANCE_STATUS="✅ yfinance available"
else
    YFINANCE_STATUS="⚠️  yfinance not installed (using mock mode)"
fi

# Check backend mode
BACKEND_MODE="UNKNOWN"
if python -c "import os" 2>/dev/null; then
    if python -c "import os; print('MOCK' if os.getenv('YAHOO_FINANCE_USE_MOCK', 'false') == 'true' else 'REAL')" 2>/dev/null; then
        BACKEND_MODE=$(python -c "import os; print('MOCK' if os.getenv('YAHOO_FINANCE_USE_MOCK', 'false') == 'true' else 'REAL')" 2>/dev/null || echo "UNKNOWN")
    fi
fi

# Run the API service
echo "🚀 Starting data-retriever API..."
echo "   Port: ${PORT:-8003}"
echo "   $YFINANCE_STATUS"
echo "   Backend: $BACKEND_MODE"
echo ""

python api_service.py

