# Grafana Empty Panels - Troubleshooting

## Common Issues & Fixes

### 1. Check Time Range ⏰

**Most common issue!**

- **Top right corner**: Set time range to **"Last 5 minutes"** or **"Last 15 minutes"**
- If set to past dates, you won't see current data
- Click the time picker → Select "Last 5 minutes"

### 2. Generate Data First 📊

**Before creating panels, generate metrics:**

```bash
# Visit this URL multiple times:
http://localhost:8000/test

# Or use curl:
for i in {1..5}; do curl -s http://localhost:8000/test > /dev/null; sleep 1; done
```

### 3. Check Prometheus Has Data 🔍

**Verify Prometheus is scraping:**

1. Go to: http://localhost:9090
2. Click: **Status** → **Targets**
3. Check: `prompt-manager` target should be **UP** (green)
4. **Last scrape** should be recent (< 1 minute ago)

**Test query in Prometheus:**
- Go to: http://localhost:9090/graph
- Try: `prompt_manager_operations_total`
- Should show results

### 4. Verify Data Source 📡

**In Grafana:**

1. Go to: **Configuration** → **Data sources**
2. Click: **Prometheus**
3. **URL** should be: `http://prometheus:9090`
4. Click: **Save & Test**
5. Should show: "Data source is working"

### 5. Use Simple Queries First ✅

**Start with these working queries:**

**Panel 1 - Total Operations:**
```
prompt_manager_operations_total
```
- **Visualization**: Table or Stat
- **Time range**: Last 5 minutes

**Panel 2 - Total Tokens:**
```
sum(prompt_manager_tokens_total)
```
- **Visualization**: Stat
- **Time range**: Last 5 minutes

**Panel 3 - Operations by Type:**
```
sum by (operation) (prompt_manager_operations_total)
```
- **Visualization**: Bar chart or Pie chart
- **Time range**: Last 5 minutes

### 6. Check Query Syntax 🔤

**Common mistakes:**

❌ Wrong:
```
prompt_manager_operations_total{}  # Extra braces
sum(prompt_manager_operations_total[5m])  # sum() doesn't need time range
```

✅ Correct:
```
prompt_manager_operations_total
sum(prompt_manager_operations_total)
rate(prompt_manager_operations_total[5m])  # rate() needs time range
```

### 7. Refresh Panel 🔄

**After generating data:**

1. Click panel **"..."** menu → **Refresh**
2. Or set **Auto-refresh**: 5s or 10s (top right)
3. Wait 30 seconds for Prometheus to scrape

### 8. Check Panel Settings ⚙️

**Panel configuration:**

1. **Edit panel** (click panel → Edit)
2. **Query tab**: Verify query is correct
3. **Transform tab**: Check if any transforms are hiding data
4. **Field tab**: Check if values are being filtered

### 9. Verify Metrics Exist 📈

**Check what metrics are available:**

```bash
# Check metrics endpoint
curl http://localhost:8000/metrics | grep prompt_manager

# Check Prometheus API
curl "http://localhost:9090/api/v1/label/__name__/values" | grep prompt_manager
```

### 10. Step-by-Step Panel Creation 🎯

**Create a working panel:**

1. **Click**: "+" → "Add visualization"
2. **Select**: Prometheus data source
3. **Query A**: `prompt_manager_operations_total`
4. **Time range**: Last 5 minutes (top right)
5. **Visualization**: Choose "Table" first (easiest to debug)
6. **Click**: Apply
7. **Generate data**: Visit http://localhost:8000/test
8. **Wait**: 30 seconds
9. **Refresh**: Panel should show data

## Quick Test

**Run this to generate data and verify:**

```bash
# Generate 10 requests
for i in {1..10}; do 
  curl -s http://localhost:8000/test > /dev/null
  echo "Request $i sent"
  sleep 2
done

# Check Prometheus has data
curl "http://localhost:9090/api/v1/query?query=prompt_manager_operations_total" | python -m json.tool
```

**Then in Grafana:**
- Create panel with: `prompt_manager_operations_total`
- Set time range: Last 5 minutes
- Should see 3 results (load_contexts, fill_template, compose)

## Still Empty?

**Check logs:**

```bash
# Grafana logs
docker-compose logs grafana | tail -20

# Prometheus logs  
docker-compose logs prometheus | tail -20
```

**Common fixes:**
- Restart Grafana: `docker-compose restart grafana`
- Restart Prometheus: `docker-compose restart prometheus`
- Check network: Prometheus can reach `host.docker.internal:8000`

