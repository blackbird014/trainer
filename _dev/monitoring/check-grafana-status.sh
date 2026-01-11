#!/bin/bash
# Check Grafana status and logs

cd "$(dirname "$0")"

echo "=== Grafana Container Status ==="
docker ps -a --filter "name=trainer_monitoring_grafana" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== All Monitoring Containers ==="
docker-compose ps
echo ""

echo "=== Grafana Logs (last 50 lines) ==="
docker logs trainer_monitoring_grafana --tail 50 2>&1
echo ""

echo "=== Errors in Grafana Logs ==="
docker logs trainer_monitoring_grafana 2>&1 | grep -i -E "(error|fail|panic|fatal|cannot)" | tail -20
echo ""

echo "=== Testing Grafana Health ==="
if curl -s -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✓ Grafana is responding"
    curl -s http://localhost:3000/api/health | head -3
else
    echo "✗ Grafana is NOT responding"
fi
echo ""

echo "=== Checking Datasource Config Files ==="
echo "Loki config:"
cat grafana/provisioning/datasources/loki.yml
echo ""
echo "Prometheus config:"
cat grafana/provisioning/datasources/prometheus.yml
echo ""
