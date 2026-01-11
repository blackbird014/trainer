#!/bin/bash
# Fix Grafana port 3000 issue

cd "$(dirname "$0")"

echo "=== Step 1: Checking Container Status ==="
docker ps --filter "name=trainer_monitoring_grafana" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== Step 2: Checking All Grafana Containers ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -i grafana
echo ""

echo "=== Step 3: Checking if Port 3000 is in Use ==="
if command -v lsof > /dev/null 2>&1; then
    if lsof -i :3000 2>/dev/null | grep -v COMMAND; then
        echo "WARNING: Port 3000 is already in use!"
        lsof -i :3000 2>/dev/null | grep -v COMMAND
    else
        echo "✓ Port 3000 is free"
    fi
else
    echo "lsof not available, skipping port check"
fi
echo ""

echo "=== Step 4: Checking Container Logs ==="
if docker ps -a --format '{{.Names}}' | grep -q "^trainer_monitoring_grafana$"; then
    echo "Last 20 lines of Grafana logs:"
    docker logs trainer_monitoring_grafana --tail 20 2>&1
else
    echo "Container doesn't exist"
fi
echo ""

echo "=== Step 5: Checking docker-compose Status ==="
docker-compose ps
echo ""

echo "=== Step 6: Testing Grafana Health Endpoint ==="
if curl -s -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✓ Grafana is responding on port 3000"
    curl -s http://localhost:3000/api/health | head -3
else
    echo "✗ Grafana is NOT responding on port 3000"
fi
echo ""

echo "=== Attempting Fix ==="
echo "Stopping and removing container..."
docker-compose stop grafana 2>/dev/null
docker rm trainer_monitoring_grafana 2>/dev/null || true

echo "Starting Grafana fresh..."
docker-compose up -d grafana

echo ""
echo "Waiting 15 seconds for Grafana to start..."
sleep 15

echo ""
echo "=== Final Status Check ==="
if curl -s -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✓ SUCCESS: Grafana is now responding on port 3000"
    echo "Access it at: http://localhost:3000 (admin/admin)"
else
    echo "✗ Grafana is still not responding"
    echo ""
    echo "Checking logs for errors:"
    docker logs trainer_monitoring_grafana --tail 30 2>&1 | grep -i -E "(error|fail|panic)" || docker logs trainer_monitoring_grafana --tail 30 2>&1
fi
echo ""

