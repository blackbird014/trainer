# Apply Dashboard Fix

## Problem
The "Log Monitoring Dashboard" and "Logs and Metrics Combined" dashboards are not appearing in Grafana because the JSON structure has the dashboard properties nested under a `"dashboard"` key, but Grafana provisioning expects them at the root level.

## Solution

Run the fix script:

```bash
cd _dev/monitoring
chmod +x fix-dashboards.sh
./fix-dashboards.sh
```

Or manually using Python:

```bash
cd _dev/monitoring
python3 << 'EOF'
import json

for filename in ["grafana/dashboards/log-monitoring.json", "grafana/dashboards/logs-and-metrics.json"]:
    with open(filename, 'r') as f:
        data = json.load(f)
    
    # Extract nested dashboard if present
    if 'dashboard' in data:
        dashboard = data['dashboard']
    else:
        dashboard = data
    
    # Update schema version
    dashboard['schemaVersion'] = 27
    dashboard['version'] = 1
    if 'id' in dashboard:
        dashboard['id'] = None
    
    # Write back flattened structure
    with open(filename, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"Fixed: {filename}")

EOF
```

## Restart Grafana

After fixing the JSON files, restart Grafana:

```bash
cd _dev/monitoring
docker-compose restart grafana
```

## Verify

1. Open Grafana: http://localhost:3000
2. Go to Dashboards → Browse
3. You should now see:
   - "Log Monitoring Dashboard"
   - "Logs and Metrics Combined"

