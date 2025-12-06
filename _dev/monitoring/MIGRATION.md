# Migration from Module-Specific Monitoring

This document explains the migration from module-specific monitoring (e.g., `prompt-manager/docker-compose.yml`) to centralized monitoring.

## What Changed

Previously, each module had its own Prometheus/Grafana setup:
- `prompt-manager/docker-compose.yml` - Prometheus + Grafana for prompt-manager only
- `prompt-manager/prometheus.yml` - Scraped only prompt-manager
- `prompt-manager/grafana/` - Dashboards for prompt-manager only

Now, all modules use centralized monitoring:
- `_dev/monitoring/docker-compose.yml` - Prometheus + Grafana for all modules
- `_dev/monitoring/prometheus/prometheus.yml` - Scrapes all modules
- `_dev/monitoring/grafana/dashboards/` - Dashboards for all modules

## Migration Steps

### 1. Stop Old Monitoring (if running)

```bash
cd _dev/prompt-manager
docker-compose down -v
```

### 2. Start Centralized Monitoring

```bash
cd _dev/monitoring
docker-compose up -d
```

### 3. Update Port References

The centralized Grafana runs on port **3000** (not 3001).

Old: `http://localhost:3001` (prompt-manager Grafana)
New: `http://localhost:3000` (centralized Grafana)

### 4. Verify Dashboards

1. Open `http://localhost:3000`
2. Login: `admin` / `admin`
3. Navigate to **Dashboards** → Browse
4. You should see:
   - Trainer Modules Overview
   - Prompt Manager Dashboard
   - Prompt Security Dashboard
   - LLM Provider Dashboard

## What to Keep

The old monitoring files in `prompt-manager/` can be kept for reference, but are no longer needed:

- `prompt-manager/docker-compose.yml` - Can be removed or kept as backup
- `prompt-manager/prometheus.yml` - Can be removed or kept as backup
- `prompt-manager/grafana/` - Can be removed or kept as backup

## Benefits

✅ **Single source of truth** - One Prometheus instance for all modules
✅ **Unified dashboards** - Overview dashboard shows all modules together
✅ **Easier management** - One docker-compose to manage
✅ **Better resource usage** - Single Prometheus/Grafana instance
✅ **Consistent configuration** - Same scrape intervals, retention, etc.

## Backward Compatibility

Modules still expose metrics independently:
- Each module exposes `/metrics` endpoint
- Prometheus scrapes each module separately
- Modules can still be run independently

The only change is where Prometheus/Grafana run from.

