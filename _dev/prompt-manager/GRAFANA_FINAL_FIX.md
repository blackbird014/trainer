# Final Fix for Grafana "NO DATA"

## What I Fixed

### 1. Datasource UID
Changed from `"uid": "prometheus"` to actual UID: `"PBFA97CFB590B2093"`

Grafana needs the actual datasource UID, not just the name.

### 2. Verified Connection
✅ Grafana CAN query Prometheus (API test passed)
✅ Prometheus HAS data (161,462 tokens)
✅ Datasource is configured correctly

## Now Try This

### Step 1: Wait for Grafana Restart
Wait 10 seconds after restart.

### Step 2: Refresh Dashboard
1. Go to: http://localhost:3000
2. Open "Prompt Manager Dashboard"
3. Click **Refresh** button (top right)

### Step 3: Check Time Range
**CRITICAL:**
- Top right corner
- Set to: **"Last 5 minutes"**
- Click **Apply**

### Step 4: Test Simple Panel
Edit "Total Tokens" panel:
- Query: `sum(prompt_manager_tokens_total)`
- Time range: Last 5 minutes
- Should show: ~161,462

## If Still No Data

### Check Panel Query
1. Edit panel → Query tab
2. Verify query: `sum(prompt_manager_tokens_total)`
3. Verify datasource: Should show "Prometheus"
4. Click "Run query" button
5. Should show data in preview

### Check Time Range Again
- Must be "Last 5 minutes" or "Last 15 minutes"
- NOT "Last 1 hour" or past dates
- Current time should match your Mac time

### Generate Fresh Data
```bash
curl http://localhost:8000/test
```
Wait 30 seconds, then refresh Grafana.

## Quick Test Query

In Grafana Explore tab:
1. Click "Explore" (compass icon)
2. Select "Prometheus" datasource
3. Query: `prompt_manager_operations_total`
4. Time range: Last 5 minutes
5. Should show 3 results

If this works, dashboard panels should work too!

## Summary

✅ Datasource UID fixed
✅ Connection verified
✅ Data exists in Prometheus

**Most likely issue now**: Time range in dashboard (must be "Last 5 minutes")

