# Fix Stale Data in Prometheus/Grafana

## The Problem

Prometheus shows old data (46739) even though new data exists (148295+). This happens when:
1. Prometheus hasn't scraped recently
2. Time range in Grafana is wrong
3. Data source connection issue

## Quick Fixes

### 1. Force Prometheus to Scrape Now

**Reload Prometheus config:**
```bash
curl -X POST http://localhost:9090/-/reload
```

**Or restart Prometheus:**
```bash
docker-compose restart prometheus
```

### 2. Check Time Range in Grafana

**Critical!**

- **Top right** of Grafana dashboard
- Click time picker
- Select: **"Last 5 minutes"** or **"Last 15 minutes"**
- **NOT** "Last 1 hour" or past dates
- Click **Apply**

### 3. Generate Fresh Data

```bash
# Generate 5 requests
for i in {1..5}; do 
  curl -s http://localhost:8000/test > /dev/null
  echo "Request $i"
  sleep 2
done

# Wait 30 seconds for Prometheus to scrape
sleep 30
```

### 4. Verify Prometheus Has New Data

**Check in Prometheus UI:**
- Go to: http://localhost:9090
- Query: `sum(prompt_manager_tokens_total)`
- Should show current value (~148295+)

**Check scrape status:**
- Go to: http://localhost:9090/targets
- `prompt-manager` should be **UP**
- **Last scrape** should be recent (< 1 minute)

### 5. Refresh Grafana Dashboard

**After fixing time range:**
1. Click **Refresh** button (top right)
2. Or set **Auto-refresh**: 5s or 10s
3. Wait 30 seconds

## Step-by-Step Fix

1. **Generate data**: `curl http://localhost:8000/test` (5 times)
2. **Wait**: 30 seconds
3. **Check Prometheus**: http://localhost:9090 (query: `sum(prompt_manager_tokens_total)`)
4. **Set Grafana time**: Last 5 minutes
5. **Refresh Grafana**: Should show data

## Verify It's Working

**In Grafana, edit "Total Tokens" panel:**
- Query: `sum(prompt_manager_tokens_total)`
- Time range: Last 5 minutes
- Should show: ~148295 or higher

**If still showing old data:**
- Check time range again (most common issue!)
- Verify Prometheus has new data
- Restart Grafana: `docker-compose restart grafana`

## Common Issues

### Prometheus Not Scraping
- Check: http://localhost:9090/targets
- Should show "UP" and recent last scrape
- If not, check `prometheus.yml` config

### Grafana Time Range Wrong
- **Most common issue!**
- Must be "Last 5 minutes" or recent
- Past dates = no data

### Data Source Not Connected
- Grafana → Configuration → Data sources
- Prometheus URL: `http://prometheus:9090`
- Click "Save & Test"

