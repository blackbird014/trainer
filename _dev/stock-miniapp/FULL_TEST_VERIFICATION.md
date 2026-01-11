# Full Test Verification Guide

## Services Starting

The `start-all-services.sh` script is running and should be starting all services. Here's how to verify everything is working:

## Quick Verification Commands

### 1. Check if Services Are Running

```bash
# Check Docker containers (Prometheus, Grafana, Loki, Promtail)
docker ps --filter "name=trainer_monitoring"

# Check application services
ps aux | grep -E "api_service|orchestrator|node.*server.js" | grep -v grep

# Check MongoDB
docker ps | grep mongodb
```

### 2. Check Service Health Endpoints

```bash
# Web UI
curl http://localhost:3003/health

# Data Store
curl http://localhost:8007/health

# Orchestrator
curl http://localhost:3002/health

# Monitoring Service
curl http://localhost:8008/monitoring/health

# Grafana
curl http://localhost:3000/api/health

# Loki
curl http://localhost:3100/ready

# Prometheus
curl http://localhost:9090/-/ready
```

### 3. Access the Application

**Stock Mini-App Web UI:**
- URL: http://localhost:3003
- Features:
  - View Database Collections (DB Viewer)
  - Test Monitoring (check monitoring setup)
  - Use the application normally

**Grafana (Logs & Metrics):**
- URL: http://localhost:3000
- Login: `admin` / `admin`
- Dashboards:
  - **Log Monitoring Dashboard** - Real-time log viewing
  - **Logs and Metrics Combined** - Unified observability

**Prometheus (Metrics):**
- URL: http://localhost:9090
- Query metrics, see targets, etc.

**Loki (Logs API):**
- URL: http://localhost:3100
- Check: http://localhost:3100/ready (should return "ready")

## Expected Services

All these services should be running:

| Service | Port | URL | Status Check |
|---------|------|-----|--------------|
| MongoDB | 27017 | - | `docker ps | grep mongodb` |
| Data Store | 8007 | http://localhost:8007 | `/health` endpoint |
| Data Retriever | 8003 | http://localhost:8003 | `/health` endpoint |
| Prompt Manager | 8000 | http://localhost:8000 | `/health` endpoint |
| LLM Provider | 8001 | http://localhost:8001 | `/health` endpoint |
| Format Converter | 8004 | http://localhost:8004 | `/health` endpoint |
| Orchestrator | 3002 | http://localhost:3002 | `/health` endpoint |
| Monitoring Service | 8008 | http://localhost:8008 | `/monitoring/health` endpoint |
| Web UI | 3003 | http://localhost:3003 | `/health` endpoint |
| Prometheus | 9090 | http://localhost:9090 | `/-/ready` endpoint |
| Grafana | 3000 | http://localhost:3000 | `/api/health` endpoint |
| Loki | 3100 | http://localhost:3100 | `/ready` endpoint |
| Promtail | - | - | Check Docker logs |

## Testing Workflow

### 1. Verify Services Are Up

```bash
cd _dev/stock-miniapp
./test_services.sh
```

This script tests all service endpoints.

### 2. Use the Application

1. Open http://localhost:3003
2. Click "View Database Collections" to test DB viewer
3. Click "Test Monitoring" to verify monitoring integration
4. Use the application normally to generate log activity

### 3. View Logs in Grafana

1. Open http://localhost:3000
2. Login: `admin` / `admin`
3. Go to **Dashboards** → Browse
4. Open **"Log Monitoring Dashboard"**
5. You should see:
   - Recent logs from all services
   - Error logs filtered
   - Service-specific log panels
   - Log volume statistics

### 4. Test Log Collection

```bash
# Generate some log activity
curl http://localhost:3003/api/health
curl http://localhost:8007/health

# Then check Grafana - logs should appear within 10-15 seconds
```

### 5. View Metrics and Logs Together

1. In Grafana, open **"Logs and Metrics Combined"** dashboard
2. This shows:
   - Metrics graphs on the left (from Prometheus)
   - Log panels on the right (from Loki)
   - Time-synchronized views

## Troubleshooting

### Services Not Starting

Check logs:
```bash
cd _dev/stock-miniapp
tail -f logs/*.log
```

### Monitoring Stack Not Working

```bash
# Check Docker containers
cd _dev/monitoring
docker-compose ps

# Check logs
docker-compose logs promtail
docker-compose logs loki
docker-compose logs grafana
```

### Logs Not Appearing in Grafana

1. Check Promtail is running: `docker ps | grep promtail`
2. Check Promtail logs: `docker logs trainer_monitoring_promtail`
3. Verify log files exist: `ls -la _dev/stock-miniapp/logs/`
4. Check Loki is receiving logs: `curl http://localhost:3100/loki/api/v1/labels`

### Port Conflicts

If you see port conflicts:
- Port 3000: Grafana (new monitoring stack)
- Port 3001: Old Grafana (can be stopped if not needed)
- Port 9090: Prometheus
- Port 3100: Loki

Stop old containers:
```bash
docker stop prompt_manager_grafana prompt_manager_prometheus
```

## Stopping Everything

```bash
cd _dev/stock-miniapp
./stop-all-services.sh
```

This stops:
- All application services
- MongoDB container
- Monitoring stack (Prometheus, Grafana, Loki, Promtail)
- Monitoring service API

## Success Criteria

✅ All services respond to health checks  
✅ Web UI accessible at http://localhost:3003  
✅ Grafana accessible at http://localhost:3000  
✅ Logs appear in Grafana Log Monitoring Dashboard  
✅ Metrics appear in Grafana (from Prometheus)  
✅ Can correlate logs with metrics in Combined dashboard  
✅ DB viewer works in the application  
✅ Monitoring test endpoint works  

