#!/bin/bash
# Fix dashboard JSON structure for Grafana provisioning

cd "$(dirname "$0")"

echo "Fixing dashboard JSON files..."

for file in grafana/dashboards/log-monitoring.json grafana/dashboards/logs-and-metrics.json; do
    if [ -f "$file" ]; then
        echo "Processing $file..."
        
        # Use Python to fix the JSON structure
        python3 <<PYTHON
import json

with open('$file', 'r') as f:
    data = json.load(f)

# Extract nested dashboard if present
if 'dashboard' in data:
    dashboard = data['dashboard']
else:
    dashboard = data

# Update schema version and version
dashboard['schemaVersion'] = 27
dashboard['version'] = 1
if 'id' in dashboard:
    dashboard['id'] = None

# Write back flattened structure
with open('$file', 'w') as f:
    json.dump(dashboard, f, indent=2)

print(f"  ✓ Fixed: {dashboard.get('title', 'Unknown')}")
PYTHON
    fi
done

echo ""
echo "Done! Restart Grafana to see the dashboards:"
echo "  docker-compose restart grafana"

