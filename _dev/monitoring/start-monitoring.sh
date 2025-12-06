#!/bin/bash

# Start centralized monitoring for Trainer modules
# This script starts Prometheus and Grafana for monitoring all modules

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

echo "Starting Prometheus and Grafana..."
docker-compose up -d

echo ""
echo "Waiting for services to start..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services started successfully!"
    echo ""
    echo "Access points:"
    echo "  📊 Grafana:    http://localhost:3000 (admin/admin)"
    echo "  📈 Prometheus: http://localhost:9090"
    echo ""
    echo "Dashboards available:"
    echo "  - Trainer Modules Overview"
    echo "  - Prompt Manager Dashboard"
    echo "  - Prompt Security Dashboard"
    echo "  - LLM Provider Dashboard"
    echo ""
    echo "To stop services:"
    echo "  docker-compose down"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
else
    echo "❌ Error: Services failed to start"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

