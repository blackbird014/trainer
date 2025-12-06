# Import Dashboard to Grafana

## Option 1: Manual Import (Easiest)

1. **Open Grafana**: http://localhost:3000
2. **Login**: admin / admin
3. **Go to**: Dashboards → **Import**
4. **Copy JSON**: Open `grafana/dashboards/prompt-manager.json`
5. **Paste JSON** into the import box
6. **Click**: "Load"
7. **Select**: Prometheus data source
8. **Click**: "Import"

## Option 2: Restart Grafana (Auto-load)

I just restarted Grafana. Wait 10 seconds, then:

1. **Refresh Grafana**: http://localhost:3000
2. **Go to**: Dashboards → Browse
3. **Look for**: "Prompt Manager Dashboard"

If it's still not there, use **Option 1** (manual import).

## Option 3: Fix Provisioning (If needed)

If provisioning isn't working, check:

1. **Dashboard file location**: Should be in `grafana/dashboards/prompt-manager.json`
2. **Provisioning config**: Should be in `grafana/provisioning/dashboards/dashboard.yml`
3. **Restart**: `docker-compose restart grafana`

## Quick Import Command

You can also use Grafana API:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d @grafana/dashboards/prompt-manager.json \
  http://localhost:3000/api/dashboards/db
```

## Verify Dashboard

After import:
1. Go to **Dashboards** → **Browse**
2. You should see **"Prompt Manager Dashboard"**
3. Click to open
4. You should see 6 panels with metrics

## Troubleshooting

**Dashboard not showing?**
- Check Prometheus data source is configured
- Verify time range (top right) - set to "Last 5 minutes"
- Generate some data: http://localhost:8000/test

**Panels showing "No data"?**
- Wait 1-2 minutes after generating data
- Check Prometheus has metrics: http://localhost:9090
- Verify queries in panels are correct

