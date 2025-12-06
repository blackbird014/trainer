# Docker Setup Guide

> **⚠️ DEPRECATED**: This file documents the old module-specific monitoring setup.  
> **✅ Use centralized monitoring instead**: See [`../../monitoring/README.md`](../../monitoring/README.md)  
> The old `docker-compose.yml`, `prometheus.yml`, and `grafana/` directory have been removed.

## Quick Start

### 1. Install Docker Desktop

Download and install Docker Desktop for Mac:
https://www.docker.com/products/docker-desktop

### 2. Start the Metrics Server

In one terminal, start the Flask app that exposes metrics:

```bash
cd _dev/phase1/prompt-manager
source .venv/bin/activate
python app_with_metrics.py
```

The server will run on `http://localhost:8000`

### 3. Start Docker Containers

In another terminal:

```bash
cd _dev/phase1/prompt-manager
docker-compose up -d
```

This starts:
- **Prometheus** on http://localhost:9090
- **Grafana** on http://localhost:3000

### 4. Access Dashboards

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`
  - Dashboard: "Prompt Manager Dashboard" (auto-loaded)

- **Prometheus**: http://localhost:9090
  - Query: `prompt_manager_operations_total`
  - Query: `rate(prompt_manager_operations_total[5m])`

### 5. Generate Test Metrics

Visit http://localhost:8000/test to generate some test metrics, then refresh Grafana to see them!

## File Structure

```
_dev/phase1/prompt-manager/
├── docker-compose.yml          # Docker services configuration
├── prometheus.yml              # Prometheus scrape configuration
├── app_with_metrics.py         # Flask app with metrics endpoint
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml  # Auto-configure Prometheus datasource
│   │   └── dashboards/
│   │       └── dashboard.yml   # Auto-load dashboards
│   └── dashboards/
│       └── prompt-manager.json # Pre-built dashboard
└── DOCKER_SETUP.md            # This file
```

## Docker Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Restart services
```bash
docker-compose restart
```

### Remove everything (including data)
```bash
docker-compose down -v
```

## Configuration

### Prometheus Configuration

Edit `prometheus.yml` to change scrape interval or add targets:

```yaml
scrape_configs:
  - job_name: 'prompt-manager'
    scrape_interval: 5s  # Change this
    static_configs:
      - targets: ['host.docker.internal:8000']  # Your app endpoint
```

### Grafana Configuration

- **Default login**: admin/admin
- **Change password**: First login will prompt you
- **Dashboard**: Auto-loaded from `grafana/dashboards/`

### Port Configuration

If ports 9090 or 3000 are in use, edit `docker-compose.yml`:

```yaml
ports:
  - "9091:9090"  # Change 9091 to any free port
```

## Troubleshooting

### Prometheus can't scrape metrics

1. **Check if Flask app is running**: http://localhost:8000/metrics
2. **Check Prometheus targets**: http://localhost:9090/targets
3. **For Linux**: Change `host.docker.internal` to `172.17.0.1` in `prometheus.yml`

### Grafana can't connect to Prometheus

1. Check Prometheus is running: http://localhost:9090
2. Check Grafana datasource: http://localhost:3000/datasources
3. Verify URL is `http://prometheus:9090` (internal Docker network)

### Metrics not showing

1. Generate some metrics: http://localhost:8000/test
2. Check Prometheus: http://localhost:9090/graph?g0.expr=prompt_manager_operations_total
3. Wait a few seconds for scrape interval

## Resource Usage

- **Prometheus**: ~50-100MB RAM
- **Grafana**: ~100-200MB RAM
- **Total**: ~150-300MB RAM

Very lightweight for Mac Air!

## Custom Dashboards

Edit `grafana/dashboards/prompt-manager.json` or create new dashboards in Grafana UI.

Common queries:
- `rate(prompt_manager_operations_total[5m])` - Operations per second
- `histogram_quantile(0.95, prompt_manager_operation_duration_seconds)` - P95 latency
- `sum(prompt_manager_cost_total)` - Total cost
- `rate(prompt_manager_cache_hits_total[5m])` - Cache hit rate

## Production Notes

For production:
1. Change Grafana admin password
2. Use environment variables for secrets
3. Add authentication to Flask app
4. Use proper reverse proxy (nginx)
5. Set up log rotation
6. Configure alerting rules in Prometheus

## See Also

- `PROMETHEUS_GRAFANA_SETUP.md` - Detailed setup guide
- `LOGGING_GUIDE.md` - Logging system documentation
- `app_with_metrics.py` - Metrics server implementation

