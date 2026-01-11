#!/bin/bash
# Check Loki datasource configuration in Grafana

echo "=== Checking Loki Service ==="
docker ps --filter "name=trainer_monitoring_loki" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== Testing Loki Connectivity ==="
echo "From host:"
curl -s http://localhost:3100/ready 2>&1
echo ""
echo "From Grafana container:"
docker exec trainer_monitoring_grafana wget -qO- http://loki:3100/ready 2>&1 || echo "Failed to connect to Loki from Grafana container"
echo ""

echo "=== Checking Grafana Datasources ==="
docker exec trainer_monitoring_grafana ls -la /etc/grafana/provisioning/datasources/ 2>&1
echo ""

echo "=== Checking Loki Datasource Config ==="
docker exec trainer_monitoring_grafana cat /etc/grafana/provisioning/datasources/loki.yml 2>&1
echo ""

echo "=== Checking Grafana Logs for Datasource Errors ==="
docker logs trainer_monitoring_grafana 2>&1 | grep -i -E "(loki|datasource|provision)" | tail -20
echo ""

echo "=== Restart Grafana to Reload Datasources ==="
echo "Run: docker-compose restart grafana"

