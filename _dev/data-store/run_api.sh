#!/bin/bash
# Run data-store API service with automatic venv activation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv if it exists (automatic, no need to ask)
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check backend mode
BACKEND_MODE="UNKNOWN"
if python -c "from data_store.config import StoreConfig" 2>/dev/null; then
    BACKEND_MODE=$(python -c "from data_store.config import StoreConfig; c = StoreConfig(); print(c.backend.upper())" 2>/dev/null || echo "UNKNOWN")
fi

# Run the API service
echo "🚀 Starting data-store API..."
echo "   Port: ${PORT:-8007}"
echo "   Backend: $BACKEND_MODE"
echo ""

python api_service.py

