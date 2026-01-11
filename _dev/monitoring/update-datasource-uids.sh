#!/bin/bash
# Update datasource UIDs in Grafana

set -e

echo "=== Getting datasource IDs ==="
DS_LIST=$(curl -s -u admin:admin http://localhost:3000/api/datasources)
LOKI_ID=$(echo "$DS_LIST" | python3 -c "import sys, json; ds=json.load(sys.stdin); loki=[d for d in ds if d['type']=='loki'][0]; print(loki['id'])")
PROM_ID=$(echo "$DS_LIST" | python3 -c "import sys, json; ds=json.load(sys.stdin); prom=[d for d in ds if d['type']=='prometheus'][0]; print(prom['id'])")

echo "Loki datasource ID: $LOKI_ID"
echo "Prometheus datasource ID: $PROM_ID"
echo ""

echo "=== Updating Loki datasource UID ==="
curl -s -u admin:admin -X PUT "http://localhost:3000/api/datasources/$LOKI_ID" \
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
    }' | python3 -m json.tool | head -5

echo ""
echo "=== Updating Prometheus datasource UID ==="
curl -s -u admin:admin -X PUT "http://localhost:3000/api/datasources/$PROM_ID" \
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
    }' | python3 -m json.tool | head -5

echo ""
echo "✓ Datasource UIDs updated!"
echo ""
echo "Now restore the provisioning files:"
echo "  cd _dev/monitoring"
echo "  mv grafana/provisioning/datasources.bak grafana/provisioning/datasources"
echo "  docker-compose restart grafana"

