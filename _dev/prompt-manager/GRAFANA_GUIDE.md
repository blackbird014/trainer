# Grafana Guide - What You Can Do

## Access Grafana

**URL**: http://localhost:3000
**Login**: `admin` / `admin`

## What You Can Do

### 1. View Pre-Built Dashboard

The dashboard should auto-load. If not:

1. Go to **Dashboards** → **Browse**
2. Look for **"Prompt Manager Dashboard"**
3. Click to open

**Dashboard includes:**
- Operations per second graph
- Operation duration (P95)
- Total tokens counter
- Total cost (USD)
- Cache hit ratio
- Cache hits vs misses

### 2. Create Custom Panels

**Add new panel:**
1. Click **"+"** → **"Add visualization"**
2. Select **Prometheus** as data source
3. Enter query, e.g.:
   ```
   sum(prompt_manager_tokens_total)
   ```
4. Choose visualization type (Graph, Stat, Table, etc.)

### 3. Useful Queries for Grafana

**Operations per second:**
```
rate(prompt_manager_operations_total[5m])
```

**Total cost:**
```
sum(prompt_manager_cost_total)
```

**Tokens by operation:**
```
sum by (operation) (prompt_manager_tokens_total)
```

**Operation duration (P95):**
```
histogram_quantile(0.95, rate(prompt_manager_operation_duration_seconds_bucket[5m]))
```

**Cache hit ratio:**
```
rate(prompt_manager_cache_hits_total[5m]) / (rate(prompt_manager_cache_hits_total[5m]) + rate(prompt_manager_cache_misses_total[5m]))
```

### 4. Create Alerts

**Set up alerts:**
1. Go to **Alerting** → **Alert rules**
2. Create new rule
3. Example: Alert if operations fail
   ```
   sum(rate(prompt_manager_operations_total{status="error"}[5m])) > 0
   ```

### 5. Explore Data

**Explore tab:**
1. Click **"Explore"** (compass icon)
2. Select **Prometheus** data source
3. Try queries interactively
4. Switch between Graph and Table view

### 6. Customize Dashboard

**Edit dashboard:**
1. Open dashboard
2. Click **"Edit"** (pencil icon)
3. Modify panels, add new ones, change time ranges
4. Save changes

### 7. Export/Import Dashboards

**Export:**
1. Dashboard → **Settings** → **JSON Model**
2. Copy JSON

**Import:**
1. **"+"** → **"Import"**
2. Paste JSON or upload file

### 8. Set Up Variables

**Create dashboard variables:**
1. Dashboard → **Settings** → **Variables**
2. Add variable (e.g., `operation` with values: `load_contexts`, `fill_template`, `compose`)
3. Use in queries: `prompt_manager_operations_total{operation="$operation"}`

## Quick Start Steps

1. **Login**: http://localhost:3000 (admin/admin)
2. **Check dashboard**: Dashboards → Browse → "Prompt Manager Dashboard"
3. **Generate data**: Visit http://localhost:8000/test multiple times
4. **Watch metrics update**: Refresh Grafana dashboard

## Troubleshooting

### Dashboard not showing
- Check Prometheus data source is configured: **Configuration** → **Data sources**
- Verify Prometheus URL: `http://prometheus:9090`

### No data showing
- Generate metrics: http://localhost:8000/test
- Check time range (top right) - set to "Last 5 minutes"
- Verify Prometheus has data: http://localhost:9090

### Can't see panels
- Wait 1-2 minutes after generating data
- Check panel queries are correct
- Try individual metric queries first

## Example Dashboard Panels

### Panel 1: Total Operations
- **Query**: `sum(prompt_manager_operations_total)`
- **Type**: Stat
- **Title**: "Total Operations"

### Panel 2: Operations Rate
- **Query**: `rate(prompt_manager_operations_total[5m])`
- **Type**: Graph
- **Title**: "Operations per Second"

### Panel 3: Token Usage
- **Query**: `sum by (operation) (prompt_manager_tokens_total)`
- **Type**: Pie chart or Bar chart
- **Title**: "Tokens by Operation"

### Panel 4: Cost Tracking
- **Query**: `sum(prompt_manager_cost_total)`
- **Type**: Stat (with currency format)
- **Title**: "Total Cost (USD)"

## Pro Tips

1. **Use time ranges**: Set to "Last 15 minutes" to see recent activity
2. **Refresh rate**: Set auto-refresh to 5s or 10s
3. **Panel links**: Link panels to other dashboards
4. **Annotations**: Add annotations for important events
5. **Snapshots**: Share dashboard snapshots with others

Enjoy visualizing your metrics! 📊

