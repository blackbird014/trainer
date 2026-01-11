# Fix: Grafana Not Accessible on Port 3000

## Quick Fix

Run the diagnostic and fix script:

```bash
cd _dev/monitoring
./fix-grafana-port.sh
```

This script will:
1. Check container status
2. Check if port 3000 is in use
3. Check logs for errors
4. Stop and restart Grafana fresh
5. Verify it's working

## Manual Fix Steps

If the script doesn't work, try these steps manually:

### 1. Check Container Status
```bash
docker ps | grep trainer_monitoring_grafana
```

If container is not running, check why:
```bash
docker ps -a | grep trainer_monitoring_grafana
docker logs trainer_monitoring_grafana --tail 50
```

### 2. Check Port 3000
```bash
lsof -i :3000
```

If something else is using port 3000, stop it:
```bash
# If old Grafana is using it
docker stop prompt_manager_grafana 2>/dev/null

# Or kill the process using port 3000
kill -9 $(lsof -t -i:3000)
```

### 3. Restart Grafana
```bash
cd _dev/monitoring
docker-compose stop grafana
docker-compose rm -f grafana
docker-compose up -d grafana
```

### 4. Wait and Check
```bash
# Wait 15-20 seconds for Grafana to start
sleep 15

# Check if it's responding
curl http://localhost:3000/api/health

# Check logs
docker logs trainer_monitoring_grafana --tail 30
```

### 5. Check Logs for Errors
```bash
docker logs trainer_monitoring_grafana 2>&1 | grep -i -E "(error|fail|panic|cannot)" | tail -20
```

## Common Issues

### Issue 1: Container Not Running
**Symptom**: Container doesn't appear in `docker ps`

**Fix**: Start it
```bash
cd _dev/monitoring
docker-compose up -d grafana
```

### Issue 2: Port Conflict
**Symptom**: `lsof -i :3000` shows another process

**Fix**: Stop the conflicting process
```bash
docker stop prompt_manager_grafana 2>/dev/null
# Or kill process: kill -9 $(lsof -t -i:3000)
```

### Issue 3: Container Crashes on Startup
**Symptom**: Container shows "Exited" status

**Fix**: Check logs for startup errors
```bash
docker logs trainer_monitoring_grafana
```

Common causes:
- Configuration file errors
- Volume mount issues
- Dependency services not ready (Loki/Prometheus)

### Issue 4: Grafana Starts But Doesn't Listen on Port 3000
**Symptom**: Container is running but port 3000 not accessible

**Fix**: Check port mapping
```bash
docker ps | grep trainer_monitoring_grafana
# Should show: 0.0.0.0:3000->3000/tcp
```

If port mapping is wrong, check docker-compose.yml:
```yaml
ports:
  - "3000:3000"  # Should be this
```

## Verification

After fixing, verify:

1. **Container is running**:
   ```bash
   docker ps | grep trainer_monitoring_grafana
   ```

2. **Port 3000 is accessible**:
   ```bash
   curl http://localhost:3000/api/health
   # Should return JSON with "database": "ok"
   ```

3. **Grafana UI is accessible**:
   - Open browser: http://localhost:3000
   - Login: admin/admin
   - Should see Grafana dashboard

4. **Loki datasource is configured**:
   - Go to Configuration → Data Sources
   - Should see "Loki" listed

