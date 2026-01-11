#!/bin/bash

# Start centralized monitoring for Trainer modules
# This script starts Prometheus, Grafana, Loki, and Promtail for monitoring all modules

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Trainer Centralized Monitoring"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Generate Promtail configuration from mini-app log sources
echo "Step 1: Generating Promtail configuration..."
if [ -f "generate-promtail-config.py" ]; then
    python3 generate-promtail-config.py
    if [ $? -eq 0 ]; then
        echo "✅ Promtail configuration generated"
    else
        echo "⚠️  Warning: Failed to generate Promtail config, but continuing..."
    fi
else
    echo "⚠️  Warning: generate-promtail-config.py not found, skipping config generation"
fi
echo ""

# Validate log directories (warn if missing, but don't fail)
echo "Step 2: Validating log directories..."
if [ -f "promtail-config.yml" ]; then
    # Extract paths from promtail-config.yml (basic check)
    MISSING_DIRS=0
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "
import yaml
import sys
from pathlib import Path

try:
    with open('promtail-config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    for scrape_config in config.get('scrape_configs', []):
        for static_config in scrape_config.get('static_configs', []):
            path = static_config.get('labels', {}).get('__path__', '')
            if path and '*.*' not in path and not Path(path).exists():
                # Check parent directory
                parent = Path(path).parent
                if not parent.exists():
                    print(f'⚠️  Warning: Log directory does not exist: {path}')
                    sys.exit(1)
except Exception as e:
    pass
" 2>/dev/null || MISSING_DIRS=1
    
    if [ $MISSING_DIRS -eq 0 ]; then
        echo "✅ Log directories validated"
    else
        echo "⚠️  Warning: Some log directories may not exist (they may be created later)"
    fi
fi
echo ""

# Start services
echo "Step 3: Starting monitoring services (Prometheus, Grafana, Loki, Promtail)..."
docker-compose up -d

echo ""
echo "Waiting for services to start..."
sleep 8

# Wait for Loki to be ready
echo "Step 4: Waiting for Loki to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:3100/ready > /dev/null 2>&1; then
        echo "✅ Loki is ready"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠️  Warning: Loki may not be ready yet (will retry in background)"
fi
echo ""

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services started successfully!"
    echo ""
    echo "Access points:"
    echo "  📊 Grafana:    http://localhost:3000 (admin/admin)"
    echo "  📈 Prometheus: http://localhost:9090"
    echo "  📝 Loki:       http://localhost:3100"
    echo ""
    echo "Dashboards available:"
    echo "  - Trainer Modules Overview"
    echo "  - Prompt Manager Dashboard"
    echo "  - Log Monitoring Dashboard (new)"
    echo ""
    echo "To stop services:"
    echo "  docker-compose down"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To check Promtail logs:"
    echo "  docker-compose logs promtail"
else
    echo "❌ Error: Services failed to start"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

