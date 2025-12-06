# Prometheus & Grafana Setup Guide

> **⚠️ DEPRECATED**: This file documents the old module-specific monitoring setup.  
> **✅ Use centralized monitoring instead**: See [`../../monitoring/README.md`](../../monitoring/README.md)  
> The old `docker-compose.yml`, `prometheus.yml`, and `grafana/` directory have been removed.

## Quick Answer

**For testing metrics endpoint**: Only `prometheus-client` is needed (already included)

**For visualization**: You need Prometheus + Grafana, but there are lightweight options!

## Option 1: Test Metrics Endpoint Only (Lightest)

You can test the metrics endpoint **without** Prometheus or Grafana:

```python
from prompt_manager import PromptManager
from prometheus_client import generate_latest

manager = PromptManager(enable_metrics=True)

# Do some operations
manager.load_contexts([...])

# View raw metrics
metrics = generate_latest()
print(metrics.decode())
```

**Output** (readable text format):
```
# HELP prompt_manager_operations_total Total number of operations
# TYPE prompt_manager_operations_total counter
prompt_manager_operations_total{operation="load_contexts",status="success"} 1.0
```

**This is enough to verify metrics are working!**

## Option 2: Docker (Recommended for Mac)

**Lightweight Docker setup** - runs in containers, easy to start/stop:

### Prerequisites
```bash
# Install Docker Desktop for Mac (if not installed)
# Download from: https://www.docker.com/products/docker-desktop
```

### Quick Start with Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prompt-manager'
    static_configs:
      - targets: ['host.docker.internal:8000']  # Your Python app
```

**Start everything:**
```bash
docker-compose up -d
```

**Access:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

**Stop:**
```bash
docker-compose down
```

**Resource usage**: ~200-300MB RAM total (very lightweight!)

## Option 3: Local Installation (Heavier)

### Prometheus
- **Size**: ~100MB download
- **RAM**: ~50-100MB when running
- **Install**: `brew install prometheus` (on Mac)

### Grafana
- **Size**: ~200MB download
- **RAM**: ~100-200MB when running
- **Install**: `brew install grafana` (on Mac)

**Total**: ~300MB disk, ~150-300MB RAM

**Verdict**: Fine for Mac Air, but Docker is easier to manage.

## Option 4: View Metrics in Browser (No Installation)

You can create a simple Flask app to view metrics:

```python
from flask import Flask
from prompt_manager import PromptManager
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
manager = PromptManager(enable_metrics=True)

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/')
def index():
    metrics_text = generate_latest().decode()
    return f'<pre>{metrics_text}</pre>'

if __name__ == '__main__':
    app.run(port=8000)
```

Visit http://localhost:8000 to see metrics in browser!

## Resource Comparison

| Option | Disk Space | RAM Usage | Setup Time |
|--------|------------|-----------|------------|
| **prometheus-client only** | 0MB | 0MB | 0 min |
| **Docker** | ~500MB | ~200-300MB | 5 min |
| **Local install** | ~300MB | ~150-300MB | 15 min |
| **Browser view** | 0MB | ~50MB | 2 min |

## Recommendation for Mac Air

**Best option**: **Docker** (Option 2)
- Easy to start/stop
- Doesn't clutter your system
- Lightweight containers
- Easy to remove completely

**Quick test**: **prometheus-client only** (Option 1)
- Just verify metrics are being generated
- No installation needed

**For development**: **Browser view** (Option 4)
- Simple Flask app
- See metrics immediately
- No external dependencies

## Testing Without Full Setup

You can verify everything works with just `prometheus-client`:

```python
# test_metrics.py
from prompt_manager import PromptManager
from prometheus_client import generate_latest

manager = PromptManager(enable_metrics=True)

# Do operations
manager.load_contexts(["biotech/01-introduction.md"])

# Check metrics
metrics = generate_latest().decode()
print("Metrics generated:")
print(metrics)

# Verify metrics format
assert "prompt_manager_operations_total" in metrics
assert "prompt_manager_operation_duration_seconds" in metrics
print("✓ Metrics working correctly!")
```

**This proves metrics work without Prometheus/Grafana!**

## Grafana Dashboard Examples

Once you have Grafana running, you can create dashboards for:

1. **Operations per second**
   ```
   rate(prompt_manager_operations_total[5m])
   ```

2. **Operation latency (P95)**
   ```
   histogram_quantile(0.95, prompt_manager_operation_duration_seconds)
   ```

3. **Total cost**
   ```
   sum(prompt_manager_cost_total)
   ```

4. **Cache hit ratio**
   ```
   rate(prompt_manager_cache_hits_total[5m]) / 
   (rate(prompt_manager_cache_hits_total[5m]) + rate(prompt_manager_cache_misses_total[5m]))
   ```

## Summary

✅ **To test metrics**: Only `prometheus-client` needed (already included)  
✅ **For visualization**: Docker is lightest option (~200-300MB RAM)  
✅ **Mac Air friendly**: All options work fine  
✅ **Quick test**: Use browser view or raw metrics output  

**Start with Option 1** (just test metrics), then move to Docker if you want visualization!

