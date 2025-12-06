# Fix "NO DATA" in Grafana Dashboard

## Quick Fix Steps

### 1. Generate Data
Visit this URL multiple times (or run the command below):
```
http://localhost:8000/test
```

Or use curl:
```bash
for i in {1..10}; do curl -s http://localhost:8000/test > /dev/null; sleep 1; done
```

### 2. Check Time Range in Grafana
**Most important!**

- **Top right corner** of Grafana dashboard
- Click time picker
- Select: **"Last 5 minutes"** or **"Last 15 minutes"**
- Click **Apply**

If time range is set to past dates, you won't see current data!

### 3. Wait for Prometheus to Scrape
- Prometheus scrapes every **5 seconds** (configured)
- Wait **30 seconds** after generating data
- Refresh dashboard (or set auto-refresh to 5s)

### 4. Verify Prometheus Has Data
Check Prometheus directly:
- Go to: http://localhost:9090
- Try query: `prompt_manager_operations_total`
- Should show results

### 5. Check Data Source
In Grafana:
- Dashboard → **Settings** (gear icon)
- **Variables** tab → Check if Prometheus datasource is set
- Or edit panel → **Query** tab → Verify datasource is "Prometheus"

## Which Panels Should Work

### ✅ Should Work Immediately:
1. **Total Tokens** - `sum(prompt_manager_tokens_total)`
2. **Total Operations** - `prompt_manager_operations_total`

### ⏳ Need Time Range (wait 1-2 minutes):
3. **Operations per Second** - `rate(...[5m])`
4. **Operation Duration** - `histogram_quantile(...)`
5. **Cache Hit Ratio** - `rate(...[5m])`

### ⚠️ May Be Empty:
6. **Total Cost** - `sum(prompt_manager_cost_total)` (if no cost tracked yet)

## Step-by-Step Test

1. **Generate data**: Visit http://localhost:8000/test 5 times
2. **Set time range**: Last 5 minutes (top right)
3. **Wait**: 30 seconds
4. **Refresh**: Dashboard should show data
5. **Check "Total Tokens" panel**: Should show a number

## Troubleshooting

### Still No Data?

**Check Prometheus targets:**
- http://localhost:9090/targets
- `prompt-manager` should be **UP** (green)
- Last scrape should be recent (< 1 minute)

**Check metrics endpoint:**
```bash
curl http://localhost:8000/metrics | grep prompt_manager
```

**Verify queries work in Prometheus:**
- http://localhost:9090/graph
- Try: `prompt_manager_operations_total`
- Should show results

**Check Grafana logs:**
```bash
docker-compose logs grafana | tail -20
```

## Quick Test Query

In Grafana, edit a panel and try this simple query first:
```
prompt_manager_operations_total
```

If this works, then `sum()` and `rate()` queries should work too.

