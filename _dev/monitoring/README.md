# Centralized Monitoring Infrastructure

This directory contains the centralized Prometheus and Grafana setup for monitoring all Trainer modules.

## Architecture

```
_dev/monitoring/
├── docker-compose.yml          # Prometheus + Grafana services
├── prometheus/
│   └── prometheus.yml          # Scrapes all modules
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/        # Prometheus datasource config
│   │   └── dashboards/         # Dashboard provisioning config
│   └── dashboards/             # Dashboard JSON files
│       ├── overview.json       # Overview of all modules
│       ├── prompt-manager.json # Prompt Manager metrics
│       ├── prompt-security.json # Prompt Security metrics
│       └── llm-provider.json   # LLM Provider metrics
└── README.md                   # This file
```

## Quick Start

### 1. Start Monitoring Services

```bash
cd _dev/monitoring
docker-compose up -d
```

This starts:
- **Prometheus** on `http://localhost:9090`
- **Grafana** on `http://localhost:3000` (admin/admin)

### 2. Start Your Modules

Each module should expose metrics on its `/metrics` endpoint:

- **Prompt Manager**: `http://localhost:8000/metrics`
- **Prompt Security**: `http://localhost:8001/metrics` (when implemented)
- **LLM Provider**: `http://localhost:8002/metrics` (when implemented)

### 3. Access Dashboards

1. Open Grafana: `http://localhost:3000`
2. Login: `admin` / `admin`
3. Navigate to **Dashboards** → Browse
4. You'll see:
   - **Trainer Modules Overview** - Aggregated view of all modules
   - **Prompt Manager Dashboard** - Detailed Prompt Manager metrics
   - **Prompt Security Dashboard** - Security-specific metrics
   - **LLM Provider Dashboard** - LLM provider metrics

## Configuration

### Prometheus Configuration

Edit `prometheus/prometheus.yml` to add/modify scrape targets:

```yaml
scrape_configs:
  - job_name: 'prompt-manager'
    static_configs:
      - targets: ['host.docker.internal:8000']  # Update host/port
```

**Note**: 
- For Mac/Windows Docker Desktop: use `host.docker.internal`
- For Linux: use `172.17.0.1` or your host IP

### Adding New Modules

To add a new module to monitoring:

1. **Add scrape config** in `prometheus/prometheus.yml`:
   ```yaml
   - job_name: 'new-module'
     scrape_interval: 5s
     static_configs:
       - targets: ['host.docker.internal:8003']
         labels:
           module: 'new-module'
           service: 'new-module-api'
   ```

2. **Create dashboard** in `grafana/dashboards/new-module.json`

3. **Update overview dashboard** to include new module metrics

4. **Reload Prometheus**:
   ```bash
   docker-compose restart prometheus
   ```

## Dashboards

### Overview Dashboard

Aggregates metrics from all modules:
- Total operations across modules
- Cost breakdown by module
- Module health status
- Security overview
- LLM usage summary

### Prompt Manager Dashboard

- Operations per second
- Operation duration (P95)
- Token usage
- Cost tracking
- Cache hit ratio
- Security validations
- Rate limit hits

### Prompt Security Dashboard

- Security validations per second
- Injections detected
- Rate limit hits
- Validation success rate
- Security event timeline

### LLM Provider Dashboard

- Requests per second by provider
- Request duration
- Token usage
- Cost per provider
- Error rate
- Provider distribution

## Metrics Naming Convention

All modules should follow this naming convention:

- `{module}_operations_total` - Total operations
- `{module}_operation_duration_seconds` - Operation duration histogram
- `{module}_tokens_total` - Total tokens used
- `{module}_cost_total` - Total cost
- `{module}_errors_total` - Total errors
- `{module}_cache_hits_total` - Cache hits
- `{module}_cache_misses_total` - Cache misses

Examples:
- `prompt_manager_operations_total`
- `llm_provider_requests_total`
- `prompt_manager_security_validation_total`

## Troubleshooting

### Prometheus Can't Scrape Metrics

1. **Check module is running**:
   ```bash
   curl http://localhost:8000/metrics
   ```

2. **Check Prometheus targets**:
   Visit `http://localhost:9090/targets`

3. **Check network connectivity**:
   - For Linux: Change `host.docker.internal` to `172.17.0.1` in `prometheus.yml`
   - Verify Docker network: `docker network inspect monitoring_monitoring`

### Grafana Can't Connect to Prometheus

1. **Check Prometheus is running**:
   ```bash
   docker-compose ps
   curl http://localhost:9090
   ```

2. **Check Grafana datasource**:
   - Visit `http://localhost:3000/datasources`
   - Verify URL is `http://prometheus:9090` (internal Docker network)

3. **Check logs**:
   ```bash
   docker-compose logs grafana
   ```

### Dashboards Show No Data

1. **Verify metrics exist**:
   ```bash
   curl http://localhost:8000/metrics | grep prompt_manager
   ```

2. **Check Prometheus has data**:
   Visit `http://localhost:9090` and query: `prompt_manager_operations_total`

3. **Wait for scrape interval**:
   Prometheus scrapes every 5-15 seconds (configured in `prometheus.yml`)

4. **Check time range**:
   Ensure Grafana time range includes when metrics were generated

### Port Conflicts

If port 3000 or 9090 are in use, edit `docker-compose.yml`:

```yaml
services:
  grafana:
    ports:
      - "3001:3000"  # Change external port
  prometheus:
    ports:
      - "9091:9090"  # Change external port
```

## Module Integration

### Exposing Metrics from Your Module

Your module should expose Prometheus metrics at `/metrics`:

**FastAPI Example**:
```python
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return generate_latest()
```

**Flask Example**:
```python
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from flask import Flask, Response

app = Flask(__name__)

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
```

### Registering Metrics

Use `prometheus-client` to create metrics:

```python
from prometheus_client import Counter, Histogram, Gauge

# Counter
operations_total = Counter(
    'module_operations_total',
    'Total operations',
    ['operation', 'status']
)

# Histogram
operation_duration = Histogram(
    'module_operation_duration_seconds',
    'Operation duration',
    ['operation']
)

# Gauge
active_connections = Gauge(
    'module_active_connections',
    'Active connections'
)
```

## Production Considerations

1. **Change Grafana admin password**
2. **Use environment variables** for secrets
3. **Add authentication** to module APIs
4. **Configure alerting** in Prometheus
5. **Set up persistent storage** for Prometheus data
6. **Use reverse proxy** (Nginx/Caddy) for Grafana
7. **Enable HTTPS** for all services
8. **Configure retention** in Prometheus (default: 15 days)

## Resource Usage

- **Prometheus**: ~50-100MB RAM
- **Grafana**: ~100-200MB RAM
- **Total**: ~150-300MB RAM

Very lightweight for development!

## Stopping Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes (deletes all data)
docker-compose down -v
```

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Client Python](https://github.com/prometheus/client_python)

