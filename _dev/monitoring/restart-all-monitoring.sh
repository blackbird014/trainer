#!/bin/bash
# Stop and restart all monitoring services cleanly

cd "$(dirname "$0")"

echo "=========================================="
echo "  Restarting All Monitoring Services"
echo "=========================================="
echo ""

echo "=== Step 1: Stopping all services ==="
docker-compose down
echo ""

echo "=== Step 2: Waiting 5 seconds ==="
sleep 5
echo ""

echo "=== Step 3: Starting all services ==="
docker-compose up -d
echo ""

echo "=== Step 4: Waiting for services to start ==="
echo "Waiting 20 seconds for services to initialize..."
sleep 20
echo ""

echo "=== Step 5: Checking service status ==="
docker-compose ps
echo ""

echo "=== Step 6: Checking Grafana health ==="
if curl -s -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✓ Grafana is responding on port 3000"
    echo "  Access at: http://localhost:3000 (admin/admin)"
else
    echo "✗ Grafana is not responding yet"
    echo "  Checking logs..."
    docker logs trainer_monitoring_grafana --tail 20 2>&1
fi
echo ""

echo "=== Step 7: Checking Prometheus ==="
if curl -s -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✓ Prometheus is responding on port 9090"
else
    echo "✗ Prometheus is not responding"
fi
echo ""

echo "=== Step 8: Checking Loki ==="
if curl -s -f http://localhost:3100/ready > /dev/null 2>&1; then
    echo "✓ Loki is responding on port 3100"
else
    echo "✗ Loki is not responding"
fi
echo ""

echo "=========================================="
echo "  Restart Complete"
echo "=========================================="
echo ""
echo "Services:"
echo "  - Grafana:    http://localhost:3000 (admin/admin)"
echo "  - Prometheus: http://localhost:9090"
echo "  - Loki:       http://localhost:3100"
echo ""
echo "If Grafana is still not working, check logs:"
echo "  docker logs trainer_monitoring_grafana --tail 50"

