#!/bin/bash
# Diagnose why Grafana isn't accessible on port 3000

cd "$(dirname "$0")"

echo "=== Checking Container Status ==="
docker ps --filter "name=trainer_monitoring_grafana" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== Checking All Grafana Containers ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -i grafana
echo ""

echo "=== Checking if Port 3000 is in Use ==="
if lsof -i :3000 2>/dev/null | head -5; then
    echo "Port 3000 is in use by:"
    lsof -i :3000 2>/dev/null | grep -v COMMAND
else
    echo "Port 3000 appears to be free"
fi
echo ""

echo "=== Checking Container Logs (last 30 lines) ==="
docker logs trainer_monitoring_grafana 2>&1 | tail -30
echo ""

echo "=== Testing Grafana Health Endpoint ==="
if curl -s -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✓ Grafana is responding on port 3000"
    curl -s http://localhost:3000/api/health | head -3
else
    echo "✗ Grafana is NOT responding on port 3000"
    echo "Trying to connect..."
    curl -v http://localhost:3000/api/health 2>&1 | head -10
fi
echo ""

echo "=== Checking docker-compose Status ==="
docker-compose ps
echo ""

echo "=== Checking if Container Exists but Stopped ==="
docker ps -a --filter "name=trainer_monitoring_grafana" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

