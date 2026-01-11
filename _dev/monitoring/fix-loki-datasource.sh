#!/bin/bash
# Fix Loki datasource issue by restarting Grafana

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Checking Loki Service ==="
if ! docker ps --format '{{.Names}}' | grep -q "^trainer_monitoring_loki$"; then
    echo "❌ Loki container is not running!"
    echo "Starting Loki..."
    docker-compose up -d loki
    sleep 5
fi

echo "✓ Loki is running"
echo ""

echo "=== Checking Loki Datasource Config ==="
if [ ! -f "grafana/provisioning/datasources/loki.yml" ]; then
    echo "❌ Loki datasource config file not found!"
    exit 1
fi

echo "✓ Loki datasource config exists"
cat grafana/provisioning/datasources/loki.yml
echo ""

echo "=== Testing Loki Connectivity from Grafana Container ==="
if docker exec trainer_monitoring_grafana wget -qO- http://loki:3100/ready 2>&1 | grep -q "ready"; then
    echo "✓ Grafana can reach Loki"
else
    echo "❌ Grafana cannot reach Loki!"
    echo "Checking network..."
    docker network inspect trainer_monitoring_monitoring 2>&1 | grep -A 5 "Containers" || true
fi
echo ""

echo "=== Restarting Grafana to Reload Datasources ==="
docker-compose restart grafana
echo ""

echo "=== Waiting for Grafana to start ==="
sleep 10

echo "=== Checking Grafana Logs ==="
docker logs trainer_monitoring_grafana 2>&1 | grep -i -E "(loki|datasource|provision)" | tail -10 || echo "No relevant log entries found"
echo ""

echo "=== Verification ==="
echo "1. Open Grafana: http://localhost:3000 (admin/admin)"
echo "2. Go to: Configuration → Data Sources"
echo "3. You should see 'Loki' datasource listed"
echo "4. If not, check the logs above for errors"

