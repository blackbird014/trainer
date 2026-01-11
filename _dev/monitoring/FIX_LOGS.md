# Fix for Empty Log Dashboards

## Problem
Grafana dashboards were empty because Promtail was configured to read from log directories that don't exist.

## Root Cause
- All services write logs to `_dev/stock-miniapp/logs/` directory
- Each service has its own log file (e.g., `data-store.log`, `data-retriever.log`)
- But `log-sources.yml` was configured to read from separate module directories like `../data-store/logs/` which don't exist

## Solution
Updated `log-sources.yml` to point to the actual log location (`logs/` directory) with specific filename patterns for each service.

## Steps to Apply Fix

1. **Regenerate Promtail configuration:**
   ```bash
   cd _dev/monitoring
   python3 generate-promtail-config.py
   ```

2. **Restart Promtail:**
   ```bash
   docker-compose restart promtail
   ```

3. **Verify logs are being collected:**
   ```bash
   # Check Promtail logs
   docker logs trainer_monitoring_promtail | tail -30
   
   # Check if Loki has labels
   curl http://localhost:3100/loki/api/v1/labels
   
   # Query for logs
   curl "http://localhost:3100/loki/api/v1/query_range?query={job=\"data-store\"}&limit=10"
   ```

4. **Check Grafana:**
   - Go to http://localhost:3000
   - Open "Log Monitoring Dashboard"
   - Logs should appear within a few seconds

## Testing
After fixing, generate some log activity:
```bash
# Use the application to generate logs
curl http://localhost:3003/api/health
curl http://localhost:8007/health
```

Then check Grafana - logs should appear!

