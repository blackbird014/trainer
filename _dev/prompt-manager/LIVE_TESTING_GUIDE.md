# Live Testing Guide: Express + FastAPI + Grafana/Prometheus

Guide for testing the live microservices setup with metrics collection.

> **⚠️ NOTE**: This guide references centralized monitoring.  
> **✅ Use**: [`../../monitoring/README.md`](../../monitoring/README.md) for monitoring setup

## Prerequisites

1. ✅ All tests passing (72/72 tests)
2. Docker and Docker Compose installed
3. Node.js and npm installed
4. Python virtual environment set up

## Step 1: Start Prometheus and Grafana

```bash
cd ../../monitoring
docker-compose up -d
```

This starts:
- Prometheus on `http://localhost:9090`
- Grafana on `http://localhost:3000` (admin/admin)

**Note**: Grafana runs on port 3000. If Express app also uses 3000, you may need to adjust ports.

## Step 2: Start FastAPI Service

**Terminal 1:**
```bash
cd _dev/phase1/prompt-manager
source .venv/bin/activate
python api_service.py
```

Expected output:
```
Starting server on http://0.0.0.0:8000
```

Verify:
```bash
curl http://localhost:8000/health
```

## Step 3: Start Express App

**Terminal 2:**
```bash
cd _dev/phase1/prompt-manager/express-app
npm start
```

Expected output:
```
Server running on http://localhost:3000
```

Verify:
```bash
curl http://localhost:3000/health
```

## Step 4: Generate Test Traffic

### Via Express (Port 3000)

```bash
# Fill template
curl -X POST http://localhost:3000/api/prompt/fill \
  -H "Content-Type: application/json" \
  -d '{
    "template_content": "Hello {name}!",
    "params": {"name": "World"}
  }'

# Compose prompts
curl -X POST http://localhost:3000/api/prompt/compose \
  -H "Content-Type: application/json" \
  -d '{
    "templates": ["Prompt 1", "Prompt 2"],
    "strategy": "sequential"
  }'

# Test endpoint (generates metrics)
curl -X POST http://localhost:3000/api/prompt/test

# Get stats
curl http://localhost:3000/api/stats
```

### Via FastAPI Directly (Port 8000)

```bash
# Fill template
curl -X POST http://localhost:8000/prompt/fill \
  -H "Content-Type: application/json" \
  -d '{
    "template_content": "Hello {name}!",
    "params": {"name": "World"}
  }'

# Test endpoint
curl -X POST http://localhost:8000/prompt/test

# Get stats
curl http://localhost:8000/stats
```

## Step 5: Verify Prometheus Metrics

Visit: `http://localhost:9090`

### Check Metrics Endpoint
```bash
curl http://localhost:8000/metrics | grep prompt_manager
```

Expected metrics:
- `prompt_manager_operations_total`
- `prompt_manager_operation_duration_seconds`
- `prompt_manager_tokens_total`
- `prompt_manager_cost_total`
- `prompt_manager_cache_hits_total`
- `prompt_manager_cache_misses_total`

### Query in Prometheus UI

1. Go to `http://localhost:9090`
2. Click "Graph" tab
3. Try queries:
   - `prompt_manager_operations_total`
   - `rate(prompt_manager_operations_total[5m])`
   - `prompt_manager_tokens_total`
   - `prompt_manager_operation_duration_seconds`

## Step 6: Verify Grafana Dashboard

### Port Conflict Resolution

If Grafana is on port 3000 (conflicts with Express):

**Option 1**: Change Grafana port in `docker-compose.yml`:
```yaml
services:
  grafana:
    ports:
      - "3001:3000"  # Change to 3001
```

**Option 2**: Use Grafana on different port temporarily

### Access Grafana

1. Visit: `http://localhost:3000` (or configured port)
2. Login: `admin` / `admin`
3. Navigate to Dashboards → Prompt Manager
4. Verify metrics are displayed:
   - Operations count
   - Token usage
   - Operation duration
   - Cache hit/miss ratio
   - Cost tracking

### Create Test Dashboard (if needed)

1. Go to Dashboards → New Dashboard
2. Add panels for:
   - Operations per second
   - Token usage over time
   - Average operation duration
   - Cache hit rate

## Step 7: Verify End-to-End Flow

### Test Complete Workflow

```bash
# 1. Health check via Express
curl http://localhost:3000/health

# 2. Generate some operations
for i in {1..10}; do
  curl -X POST http://localhost:3000/api/prompt/fill \
    -H "Content-Type: application/json" \
    -d "{\"template_content\": \"Test {num}\", \"params\": {\"num\": \"$i\"}}"
done

# 3. Check stats
curl http://localhost:3000/api/stats

# 4. Verify metrics in Prometheus
curl http://localhost:8000/metrics | grep prompt_manager_operations_total
```

## Troubleshooting

### FastAPI Not Starting
- Check port 8000 is available: `lsof -i :8000`
- Verify dependencies: `pip list | grep fastapi`
- Check logs for errors

### Express Not Starting
- Check port 3000 is available: `lsof -i :3000`
- Verify FastAPI is running first
- Check `FASTAPI_URL` environment variable

### Prometheus Not Scraping
- Check `prometheus.yml` configuration
- Verify FastAPI `/metrics` endpoint: `curl http://localhost:8000/metrics`
- Check Prometheus targets: `http://localhost:9090/targets`

### Grafana No Data
- Verify Prometheus is running
- Check Grafana datasource configuration
- Ensure Prometheus is selected as data source
- Check time range in Grafana (may be too narrow)

### Port Conflicts
- Grafana (3000) vs Express (3000): Change Grafana port
- Check all ports: `lsof -i :3000 -i :8000 -i :9090`

## Expected Results

After running test traffic:

1. ✅ Express health check shows both services healthy
2. ✅ Prometheus shows metrics increasing
3. ✅ Grafana dashboard displays data
4. ✅ Stats endpoint shows token usage
5. ✅ All operations complete successfully

## Next Steps After Testing

1. Review metrics in Grafana
2. Check Prometheus queries
3. Verify token tracking accuracy
4. Test error scenarios
5. Load testing (optional)

