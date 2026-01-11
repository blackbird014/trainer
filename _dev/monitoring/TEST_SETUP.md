# Testing Log Monitoring Setup

## Pre-Test Checklist

### 1. Check for Existing Containers
```bash
docker ps -a | grep -E "grafana|prometheus|loki|promtail"
```

If you see old containers (like `prompt_manager_grafana`), they won't conflict as our containers have different names, but you may want to stop them:
```bash
docker stop prompt_manager_grafana prompt_manager_prometheus
```

### 2. Verify Log Directories Exist
```bash
# Check if log directories exist (create if missing)
mkdir -p _dev/data-store/logs
mkdir -p _dev/data-retriever/logs
mkdir -p _dev/prompt-manager/logs
mkdir -p _dev/llm-provider/logs
mkdir -p _dev/format-converter/logs
```

### 3. Start Monitoring Stack
```bash
cd _dev/monitoring
./start-monitoring.sh
```

Or manually:
```bash
cd _dev/monitoring
python3 generate-promtail-config.py  # Generate Promtail config
docker-compose up -d                  # Start all services
```

## Verification Steps

### 1. Check Services Are Running
```bash
docker ps --filter "name=trainer_monitoring"
```

You should see:
- `trainer_monitoring_prometheus`
- `trainer_monitoring_grafana`
- `trainer_monitoring_loki`
- `trainer_monitoring_promtail`

### 2. Check Loki is Ready
```bash
curl http://localhost:3100/ready
# Should return: "ready"
```

### 3. Check Promtail is Collecting Logs
```bash
docker logs trainer_monitoring_promtail | tail -20
```

Look for:
- No errors about missing files
- Messages about reading log files
- "Successfully sent" messages

### 4. Verify Logs Are in Loki
```bash
# Check available labels (should show job, miniapp, module, etc.)
curl http://localhost:3100/loki/api/v1/labels

# Check if logs are being ingested
curl "http://localhost:3100/loki/api/v1/query_range?query={job=~\".+\"}&limit=10"
```

### 5. Access Grafana
1. Open browser: `http://localhost:3000`
2. Login: `admin` / `admin`
3. Go to: **Dashboards** → Browse
4. You should see:
   - **Log Monitoring Dashboard** - Shows real-time logs
   - **Logs and Metrics Combined** - Correlates logs with metrics

### 6. Test Log Collection
```bash
# Generate some log activity by using the stock-miniapp
cd _dev/stock-miniapp
# Start services or make API calls that generate logs

# Then check Grafana - logs should appear within 10-15 seconds
```

## Expected Behavior

### In Grafana "Log Monitoring Dashboard":
- **Recent Logs panel**: Shows all log entries from all services
- **Error Logs panel**: Filters to show only ERROR/CRITICAL/FATAL logs
- **Service-specific panels**: Separate panels for stock-miniapp, data-store, prompt-manager, llm-provider
- **Log Volume by Service**: Statistics showing log count per service
- **Error Rate Over Time**: Graph showing error frequency

### In Grafana "Logs and Metrics Combined Dashboard":
- Metrics panels on left (from Prometheus)
- Log panels on right (from Loki)
- Time-synchronized views to correlate metrics spikes with log events

## Troubleshooting

### Promtail Not Collecting Logs
```bash
# Check Promtail logs
docker logs trainer_monitoring_promtail

# Check if log files exist and are readable
ls -la _dev/stock-miniapp/logs/
ls -la _dev/data-store/logs/
```

### Loki Not Receiving Logs
```bash
# Check Loki logs
docker logs trainer_monitoring_loki

# Check Promtail is sending to Loki
docker logs trainer_monitoring_promtail | grep -i loki
```

### Grafana Can't Query Loki
1. Go to Grafana: Configuration → Data Sources
2. Check if "Loki" datasource exists and is green
3. Test the connection
4. Check URL: should be `http://loki:3100`

### No Logs Appearing
1. Verify services are generating logs: `tail -f _dev/stock-miniapp/logs/*.log`
2. Check Promtail config: `cat _dev/monitoring/promtail-config.yml`
3. Verify volume mounts: `docker inspect trainer_monitoring_promtail | grep -A 10 Mounts`
4. Restart Promtail: `docker-compose restart promtail`

## Testing Workflow

1. **Start monitoring stack**: `cd _dev/monitoring && ./start-monitoring.sh`
2. **Start stock-miniapp services**: `cd _dev/stock-miniapp && ./start-all-services.sh`
3. **Use the application**: Make API calls, use the UI, etc.
4. **View logs in Grafana**: Open http://localhost:3000, go to Log Monitoring Dashboard
5. **Verify real-time updates**: Logs should appear within 10-15 seconds of being written

## Expected Services Status

After starting both monitoring and application:
- **Port 3000**: Grafana (new monitoring stack)
- **Port 3001**: Old Grafana (can be stopped if not needed)
- **Port 3100**: Loki
- **Port 9090**: Prometheus
- **Port 8008**: Monitoring service API
- **Port 3003**: Stock Mini-App Web UI
- **Port 3002**: Orchestrator
- **Port 8007**: Data Store
- **Port 8003**: Data Retriever
- **Port 8000**: Prompt Manager
- **Port 8001**: LLM Provider
- **Port 8004**: Format Converter

