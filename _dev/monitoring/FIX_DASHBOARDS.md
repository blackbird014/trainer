# Fix for Missing Dashboards in Grafana

## Problem
The "Log Monitoring Dashboard" and "Logs and Metrics Combined" dashboards were not appearing in Grafana's dashboard list.

## Root Cause
The dashboard JSON files had the dashboard properties nested under a `"dashboard"` key, but Grafana provisioning expects the dashboard properties at the root level of the JSON.

## Solution Applied
1. Extracted the nested dashboard object to root level
2. Updated schema version to 27 (to match working dashboards)
3. Set version to 1

## Files Fixed
- `_dev/monitoring/grafana/dashboards/log-monitoring.json`
- `_dev/monitoring/grafana/dashboards/logs-and-metrics.json`

## Next Steps
Restart Grafana to pick up the corrected dashboards:

```bash
cd _dev/monitoring
docker-compose restart grafana
```

Or reload the provisioning configuration in Grafana UI:
- Go to Configuration → Provisioning → Dashboards
- Click "Reload" if available

After restarting, the dashboards should appear in:
- Dashboards → Browse → "Log Monitoring Dashboard"
- Dashboards → Browse → "Logs and Metrics Combined"

