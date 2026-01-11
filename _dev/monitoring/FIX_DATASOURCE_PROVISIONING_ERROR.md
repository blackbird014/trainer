# Fix: Grafana Datasource Provisioning Error

## Problem
Grafana fails to start with error:
```
Failed to provision data sources: Datasource provisioning error: data source not found
```

## Root Cause
Grafana tries to validate datasources immediately on startup. If the datasource configuration references something invalid or if Grafana can't validate the datasource (even temporarily), it can fail.

## Solution Applied

1. **Added `version: 1` to datasource configs** - This explicitly sets the datasource version
2. **Simplified Loki config** - Removed any dependencies that might cause validation issues

## Files Updated

- `grafana/provisioning/datasources/prometheus.yml` - Added `version: 1`
- `grafana/provisioning/datasources/loki.yml` - Added `version: 1`, simplified config

## Next Steps

1. **Restart Grafana**:
   ```bash
   cd _dev/monitoring
   docker-compose restart grafana
   ```

2. **If still failing, try force recreate**:
   ```bash
   docker-compose stop grafana
   docker-compose rm -f grafana
   docker-compose up -d grafana
   ```

3. **Wait 20-30 seconds** for Grafana to fully initialize

4. **Check logs**:
   ```bash
   docker logs trainer_monitoring_grafana --tail 50
   ```

5. **Verify**:
   - Access http://localhost:3000
   - Go to Configuration → Data Sources
   - Should see both Prometheus and Loki listed

## Alternative: Make Datasources Optional

If the issue persists, we can make Grafana less strict about datasource provisioning by ensuring services are ready first, or by configuring Grafana to allow datasource provisioning failures.

However, the `version: 1` field should fix the issue in most cases.

