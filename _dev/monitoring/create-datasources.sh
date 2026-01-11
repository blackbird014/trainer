#!/bin/bash
# Create datasources in Grafana with correct UIDs

set -e

echo "=== Creating Loki datasource ==="
curl -s -u admin:admin -X POST http://localhost:3000/api/datasources \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Loki",
        "type": "loki",
        "access": "proxy",
        "url": "http://loki:3100",
        "isDefault": false,
        "editable": true,
        "uid": "loki",
        "jsonData": {
            "maxLines": 1000
        }
    }' | python3 -m json.tool

echo ""
echo "=== Creating Prometheus datasource ==="
curl -s -u admin:admin -X POST http://localhost:3000/api/datasources \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Prometheus",
        "type": "prometheus",
        "access": "proxy",
        "url": "http://prometheus:9090",
        "isDefault": true,
        "editable": true,
        "uid": "prometheus",
        "jsonData": {
            "timeInterval": "5s"
        }
    }' | python3 -m json.tool

echo ""
echo "✓ Datasources created with UIDs: loki and prometheus"

