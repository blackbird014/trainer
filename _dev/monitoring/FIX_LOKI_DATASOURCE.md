# Fix: Loki Datasource Not Found in Grafana

## Problem
Grafana dashboards show "datasource loki was not found" even though Loki is running and the datasource configuration exists.

## Root Cause
Grafana needs to be restarted to pick up datasource provisioning changes, or the datasource provisioning file was added after Grafana started.

## Solution

### Option 1: Restart Grafana (Recommended)
```bash
cd _dev/monitoring
docker-compose restart grafana
```

Wait 10-15 seconds for Grafana to fully start, then:
1. Open Grafana: http://localhost:3000
2. Login: admin/admin
3. Go to: **Configuration → Data Sources**
4. You should see **Loki** listed

### Option 2: Verify Configuration Files

Check that the datasource file exists and is correct:
```bash
cat _dev/monitoring/grafana/provisioning/datasources/loki.yml
```

It should contain:
```yaml
apiVersion: 1

datasources:
  - name: Loki
    uid: loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: false
    editable: true
```

### Option 3: Check Container Connectivity

Verify Grafana can reach Loki:
```bash
# From Grafana container
docker exec trainer_monitoring_grafana wget -qO- http://loki:3100/ready

# Should return: "ready"
```

### Option 4: Check Grafana Logs

Look for datasource provisioning errors:
```bash
docker logs trainer_monitoring_grafana 2>&1 | grep -i -E "(loki|datasource|provision)" | tail -20
```

## Verification

After restarting Grafana:
1. **Data Sources page** should show "Loki" with a green checkmark
2. **Dashboards** should load without "datasource not found" errors
3. **Log panels** should show data (if Promtail is collecting logs)

## If Still Not Working

1. Check docker-compose.yml volume mount is correct:
   ```yaml
   volumes:
     - ./grafana/provisioning:/etc/grafana/provisioning
   ```

2. Verify files are actually in the container:
   ```bash
   docker exec trainer_monitoring_grafana ls -la /etc/grafana/provisioning/datasources/
   ```

3. Check Grafana version supports Loki datasource (should be fine with latest Grafana)

4. Try manually adding the datasource via Grafana UI to see if there's an error:
   - Configuration → Data Sources → Add data source → Loki
   - URL: `http://loki:3100`
   - Click "Save & Test"

