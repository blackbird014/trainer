# Quick Start - See It In Action!

## Step 1: Start Docker Desktop

**Make sure Docker Desktop is running!**

- Open Docker Desktop application
- Wait for it to fully start (whale icon in menu bar)
- Verify: `docker ps` should work without errors

## Step 2: Start Metrics Server

Open Terminal 1:

```bash
cd _dev/phase1/prompt-manager
source .venv/bin/activate
python app_with_metrics.py
```

You should see:
```
Starting server on http://0.0.0.0:8000
```

**Keep this terminal open!**

## Step 3: Start Docker Containers

Open Terminal 2:

```bash
cd _dev/phase1/prompt-manager
docker-compose up -d
```

You should see:
```
Creating network "prompt-manager_monitoring" ... done
Creating prompt_manager_prometheus ... done
Creating prompt_manager_grafana    ... done
```

## Step 4: Verify Everything is Running

```bash
# Check Docker containers
docker-compose ps

# Should show:
# prompt_manager_prometheus   running
# prompt_manager_grafana      running

# Check metrics endpoint
curl http://localhost:8000/metrics | grep prompt_manager

# Generate test metrics
curl http://localhost:8000/test
```

## Step 5: Access Dashboards

### Grafana (Visualization)
1. Open browser: http://localhost:3000
2. Login: `admin` / `admin`
3. Go to Dashboards → Prompt Manager Dashboard
4. You should see 6 panels with metrics!

### Prometheus (Raw Metrics)
1. Open browser: http://localhost:9090
2. Go to Graph tab
3. Try query: `prompt_manager_operations_total`
4. Click "Execute"

## Step 6: Generate More Metrics

Visit http://localhost:8000/test multiple times, then refresh Grafana to see metrics update!

## Troubleshooting

### Docker not running
```bash
# Start Docker Desktop, then:
docker ps  # Should work
```

### Ports already in use
Edit `docker-compose.yml` and change ports:
```yaml
ports:
  - "9091:9090"  # Change 9090 to 9091
  - "3001:3000"  # Change 3000 to 3001
```

### Can't connect to metrics
- Make sure Flask app is running (Terminal 1)
- Check: http://localhost:8000/health
- For Linux: Change `host.docker.internal` to `172.17.0.1` in `prometheus.yml`

### No metrics showing
1. Visit http://localhost:8000/test to generate metrics
2. Wait 5-10 seconds for Prometheus to scrape
3. Refresh Grafana dashboard

## Stop Everything

```bash
# Stop Docker
docker-compose down

# Stop Flask app
# Press Ctrl+C in Terminal 1
```

## What You'll See

**Grafana Dashboard:**
- Operations per second graph
- Operation duration (P95)
- Total tokens counter
- Total cost (USD)
- Cache hit ratio
- Cache hits vs misses

**Prometheus:**
- Raw metric values
- Query interface
- Target status

Enjoy! 🎉

