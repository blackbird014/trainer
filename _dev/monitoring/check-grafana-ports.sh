#!/bin/bash
# Check which Grafana instances are running and on what ports

echo "=== All Grafana Containers ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -i grafana
echo ""

echo "=== Checking Port 3000 ==="
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✓ Port 3000 is responding (new centralized Grafana)"
else
    echo "✗ Port 3000 is not responding"
fi
echo ""

echo "=== Checking Port 3001 ==="
if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
    echo "✓ Port 3001 is responding (old Grafana - should be stopped)"
else
    echo "✗ Port 3001 is not responding"
fi
echo ""

echo "=== Recommendation ==="
echo "You should use port 3000 (trainer_monitoring_grafana)"
echo "Port 3001 is the old prompt-manager Grafana - stop it with:"
echo "  docker stop prompt_manager_grafana"
echo "  docker rm prompt_manager_grafana"

