#!/bin/bash
# Restart Grafana to pick up dashboard changes

cd "$(dirname "$0")"

echo "Restarting Grafana..."
docker-compose restart grafana

echo ""
echo "Waiting for Grafana to start..."
sleep 5

echo ""
echo "Grafana should be available at: http://localhost:3000"
echo "Check Dashboards → Browse for:"
echo "  - Log Monitoring Dashboard"
echo "  - Logs and Metrics Combined"

