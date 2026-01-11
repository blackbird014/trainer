#!/bin/bash

# Stop All Services for Stock Mini-App
# This script stops all services started by start-all-services.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.service_pids"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "Stopping all services..."

if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}No PID file found. Services may not be running.${NC}"
    exit 0
fi

stopped=0
while read pid; do
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null && {
            echo "  Stopped process $pid"
            stopped=$((stopped + 1))
        } || true
    fi
done < "$PID_FILE"

rm -f "$PID_FILE"

# Also stop MongoDB if running
if docker ps --format '{{.Names}}' | grep -q "^mongodb$"; then
    echo "  Stopping MongoDB container..."
    docker stop mongodb > /dev/null 2>&1
    stopped=$((stopped + 1))
fi

# Stop monitoring stack (Prometheus, Grafana, Loki, Promtail)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MONITORING_DIR="$PROJECT_ROOT/_dev/monitoring"

if [ -f "$MONITORING_DIR/docker-compose.yml" ]; then
    cd "$MONITORING_DIR"
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        echo "  Stopping monitoring stack (Prometheus, Grafana, Loki, Promtail)..."
        docker-compose down > /dev/null 2>&1
        stopped=$((stopped + 1))
    fi
fi

if [ $stopped -eq 0 ]; then
    echo -e "${YELLOW}No running services found.${NC}"
else
    echo -e "${GREEN}Stopped $stopped service(s).${NC}"
fi

