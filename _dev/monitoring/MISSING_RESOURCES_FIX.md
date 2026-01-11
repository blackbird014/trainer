# Fix: Missing Resources Errors in Grafana

## Problem
Grafana logs show many "missing resources" errors, likely related to dashboards trying to reference the Loki datasource before it's provisioned, or the datasource provisioning failing.

## Root Cause
The Loki datasource configuration had `derivedFields` that reference the Prometheus datasource. If Prometheus isn't ready when Grafana starts, or if there's a dependency issue, this can cause the Loki datasource provisioning to fail, which then causes dashboards to show "missing resources" errors.

## Solution Applied
Simplified the Loki datasource configuration by removing the `derivedFields` dependency. This ensures the Loki datasource can be provisioned independently of Prometheus.

## Next Steps

1. **Restart Grafana** to pick up the simplified configuration:
   ```bash
   cd _dev/monitoring
   docker-compose restart grafana
   ```

2. **Wait for Grafana to fully start** (check logs):
   ```bash
   docker logs trainer_monitoring_grafana -f
   ```
   Look for "HTTP Server Listen" - that means Grafana is ready.

3. **Verify Loki datasource is provisioned**:
   - Open Grafana: http://localhost:3000
   - Go to: Configuration → Data Sources
   - You should see "Loki" with a green checkmark

4. **Check dashboards**:
   - Go to: Dashboards → Browse
   - Open any log dashboard (e.g., "Log Monitoring Dashboard")
   - The "missing resources" errors should be gone

## If Issues Persist

If you still see "missing resources" errors after restarting:

1. **Check if Loki is running and reachable**:
   ```bash
   docker ps | grep loki
   docker exec trainer_monitoring_grafana wget -qO- http://loki:3100/ready
   ```

2. **Check Grafana logs for specific errors**:
   ```bash
   docker logs trainer_monitoring_grafana 2>&1 | grep -i -E "(loki|datasource|missing|resource|error)" | tail -50
   ```

3. **Verify all services are running**:
   ```bash
   docker-compose ps
   ```

4. **Force recreate Grafana** (if needed):
   ```bash
   docker-compose stop grafana
   docker rm trainer_monitoring_grafana
   docker-compose up -d grafana
   ```

