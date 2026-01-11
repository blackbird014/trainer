# Grafana Slow Restart - Troubleshooting

## Is It Normal?

**Grafana usually starts in 10-30 seconds**, but can take longer if:
- It's the first startup (initializing database)
- There are many dashboards to load
- There are datasource connectivity issues
- The container is resource-constrained

## Quick Check

Run this to see Grafana's current status:
```bash
cd _dev/monitoring
docker logs trainer_monitoring_grafana --tail 50
```

Look for:
- **"HTTP Server Listen"** - Grafana is ready
- **"Failed to provision"** - Datasource configuration errors
- **"Connection refused"** - Can't reach Loki/Prometheus
- **Stuck on "waiting for..."** - Dependency issues

## Common Causes

### 1. Datasource Provisioning Errors
If Grafana can't connect to Loki/Prometheus during startup, it may hang or retry.

**Fix:** Check if Loki and Prometheus are running:
```bash
docker ps --filter "name=trainer_monitoring" --format "table {{.Names}}\t{{.Status}}"
```

### 2. First-Time Database Initialization
First startup can take 1-2 minutes while Grafana creates its SQLite database.

**Fix:** Wait it out - subsequent starts will be faster.

### 3. Large Number of Dashboards
Loading many dashboards can slow startup.

**Fix:** Check dashboard directory size:
```bash
ls -lh _dev/monitoring/grafana/dashboards/
```

### 4. Resource Constraints
If the system is low on memory/CPU, Grafana may be slow.

**Fix:** Check resource usage:
```bash
docker stats trainer_monitoring_grafana --no-stream
```

### 5. Configuration File Errors
Syntax errors in provisioning files can cause hangs.

**Fix:** Validate YAML syntax:
```bash
# Check datasource configs
cat _dev/monitoring/grafana/provisioning/datasources/loki.yml
cat _dev/monitoring/grafana/provisioning/datasources/prometheus.yml

# Check dashboard provisioning
cat _dev/monitoring/grafana/provisioning/dashboards/dashboard.yml
```

## If Grafana is Stuck

1. **Stop and start fresh:**
   ```bash
   cd _dev/monitoring
   docker-compose stop grafana
   docker-compose up -d grafana
   ```

2. **Check logs in real-time:**
   ```bash
   docker logs trainer_monitoring_grafana -f
   ```
   Press Ctrl+C to stop watching

3. **Force restart:**
   ```bash
   docker-compose restart grafana
   docker logs trainer_monitoring_grafana -f
   ```

4. **If completely stuck, remove and recreate:**
   ```bash
   docker-compose stop grafana
   docker rm trainer_monitoring_grafana
   docker-compose up -d grafana
   ```
   Note: This won't delete your dashboards (they're in volumes/provisioning)

## Expected Startup Time

- **First startup:** 1-2 minutes (database initialization)
- **Normal restart:** 10-30 seconds
- **With errors:** May hang indefinitely or take several minutes

## Verification

Grafana is ready when:
1. Logs show: `"HTTP Server Listen"` or `"t=... lvl=info msg="HTTP Server Listen"`
2. Health endpoint responds: `curl http://localhost:3000/api/health` returns JSON
3. Web UI is accessible: http://localhost:3000

