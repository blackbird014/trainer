#!/bin/bash
cd "$(dirname "$0")"
docker-compose restart grafana
echo "Grafana restarted. Waiting 15 seconds for it to start..."
sleep 15
echo ""
echo "Checking if Grafana can reach Loki..."
docker exec trainer_monitoring_grafana wget -qO- http://loki:3100/ready 2>&1 || echo "Loki not reachable"
echo ""
echo "Done. Check Grafana at http://localhost:3000"
echo "Go to: Configuration → Data Sources → You should see 'Loki'"

