# Dashboard JSON Fix Explanation

## What Was Wrong

### Original Structure (API Import Format)
```json
{
  "dashboard": {
    "title": "...",
    "panels": [...]
  }
}
```

**Problem**: This wrapper format is for Grafana **API import**, not **file-based provisioning**.

### Missing Elements
1. **No datasource references** - Panels didn't know which data source to use
2. **Wrong panel types** - Used `"type": "graph"` (old format) instead of `"timeseries"` (new format)
3. **Missing fieldConfig** - Modern Grafana needs `fieldConfig` for proper display
4. **Histogram query** - Missing `rate()` function wrapper

## What I Fixed

### 1. Removed Wrapper
**Before:**
```json
{"dashboard": {...}}
```

**After:**
```json
{...}
```

File-based provisioning expects the dashboard object directly.

### 2. Added Datasource References
**Before:**
```json
"targets": [{
  "expr": "...",
  "refId": "A"
}]
```

**After:**
```json
"targets": [{
  "datasource": {
    "type": "prometheus",
    "uid": "prometheus"
  },
  "expr": "...",
  "refId": "A"
}]
```

Each panel now explicitly references the Prometheus datasource.

### 3. Updated Panel Types
**Before:**
```json
"type": "graph"
```

**After:**
```json
"type": "timeseries"  // For time-series graphs
"type": "stat"        // For stat panels
```

Modern Grafana uses `timeseries` instead of `graph`.

### 4. Added fieldConfig
**Before:**
```json
"yaxes": [{"format": "ops"}]
```

**After:**
```json
"fieldConfig": {
  "defaults": {
    "unit": "ops"
  }
}
```

Modern Grafana uses `fieldConfig` instead of `yaxes`.

### 5. Fixed Histogram Query
**Before:**
```json
"expr": "histogram_quantile(0.95, prompt_manager_operation_duration_seconds)"
```

**After:**
```json
"expr": "histogram_quantile(0.95, rate(prompt_manager_operation_duration_seconds_bucket[5m]))"
```

Histograms need `rate()` and `_bucket` suffix.

## Result

After restarting Grafana, the dashboard should:
1. ✅ Auto-load from `/var/lib/grafana/dashboards/prompt-manager.json`
2. ✅ Show all 6 panels
3. ✅ Have proper datasource connections
4. ✅ Display correctly with modern Grafana format

## Verify

1. **Restart Grafana**: `docker-compose restart grafana`
2. **Wait 10 seconds**
3. **Go to**: Dashboards → Browse
4. **Look for**: "Prompt Manager Dashboard"
5. **Open it**: Should show 6 panels

If panels show "No data":
- Generate metrics: http://localhost:8000/test
- Set time range: Last 5 minutes
- Wait 30 seconds for Prometheus to scrape

