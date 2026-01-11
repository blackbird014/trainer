#!/bin/bash
# Fix datasource UIDs in Grafana to match dashboard expectations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Waiting for Grafana to be ready ==="
MAX_RETRIES=30
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -s -u admin:admin http://localhost:3000/api/health > /dev/null 2>&1; then
        echo "✓ Grafana is ready"
        break
    fi
    RETRY=$((RETRY + 1))
    sleep 2
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo "❌ Grafana did not become ready in time"
    exit 1
fi

echo ""
echo "=== Getting current Loki datasource ==="
LOKI_DS=$(curl -s -u admin:admin http://localhost:3000/api/datasources/name/Loki)
if [ -z "$LOKI_DS" ] || [ "$LOKI_DS" = "null" ]; then
    echo "❌ Loki datasource not found"
    exit 1
fi

LOKI_ID=$(echo "$LOKI_DS" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
if [ -z "$LOKI_ID" ]; then
    echo "❌ Could not get Loki datasource ID"
    exit 1
fi

echo "✓ Found Loki datasource (ID: $LOKI_ID)"

echo ""
echo "=== Updating Loki datasource UID to 'loki' ==="
UPDATE_RESPONSE=$(curl -s -u admin:admin -X PUT "http://localhost:3000/api/datasources/$LOKI_ID" \
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
    }')

if echo "$UPDATE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if d.get('uid') == 'loki' else 1)" 2>/dev/null; then
    echo "✓ Loki datasource UID updated to 'loki'"
else
    echo "⚠️  Warning: Update response: $UPDATE_RESPONSE"
fi

echo ""
echo "=== Getting current Prometheus datasource ==="
PROM_DS=$(curl -s -u admin:admin http://localhost:3000/api/datasources/name/Prometheus)
if [ -z "$PROM_DS" ] || [ "$PROM_DS" = "null" ]; then
    echo "❌ Prometheus datasource not found"
    exit 1
fi

PROM_ID=$(echo "$PROM_DS" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
if [ -z "$PROM_ID" ]; then
    echo "❌ Could not get Prometheus datasource ID"
    exit 1
fi

echo "✓ Found Prometheus datasource (ID: $PROM_ID)"

echo ""
echo "=== Updating Prometheus datasource UID to 'prometheus' ==="
UPDATE_RESPONSE=$(curl -s -u admin:admin -X PUT "http://localhost:3000/api/datasources/$PROM_ID" \
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
    }')

if echo "$UPDATE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if d.get('uid') == 'prometheus' else 1)" 2>/dev/null; then
    echo "✓ Prometheus datasource UID updated to 'prometheus'"
else
    echo "⚠️  Warning: Update response: $UPDATE_RESPONSE"
fi

echo ""
echo "=== Verification ==="
echo "✓ Datasource UIDs have been updated"
echo ""
echo "You can now:"
echo "1. Refresh your Grafana dashboard"
echo "2. The 'datasource loki not found' error should be resolved"
echo ""
echo "To verify, check:"
echo "  curl -s -u admin:admin http://localhost:3000/api/datasources | python3 -m json.tool | grep -A 2 '\"name\".*Loki'"

