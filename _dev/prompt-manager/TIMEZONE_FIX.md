# Timezone Fix - Docker vs Mac Time Mismatch

## The Problem

Your Mac: 13:37 (1:37 PM)  
Docker containers: 12:37 (12:37 PM)  
**Difference: 1 hour**

This causes Grafana to show "NO DATA" because:
- Grafana time range is based on container time (12:37)
- Prometheus timestamps are UTC
- Time ranges don't match!

## What I Fixed

Added timezone to both containers in `docker-compose.yml`:

```yaml
environment:
  - TZ=Europe/Rome  # Adjust to your timezone
```

**Restarted both containers** to apply the fix.

## Verify Fix

1. **Wait 30 seconds** for containers to restart
2. **Check Grafana**: http://localhost:3000
3. **Set time range**: Last 5 minutes
4. **Refresh**: Should now show data!

## If Still Issues

### Check Your Timezone
```bash
# On Mac
date
timedatectl  # If available

# In Docker
docker-compose exec grafana date
docker-compose exec prometheus date
```

### Adjust Timezone in docker-compose.yml

If you're in a different timezone, change `TZ=Europe/Rome` to:
- `TZ=America/New_York`
- `TZ=Europe/London`
- `TZ=Asia/Tokyo`
- etc.

Find your timezone: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### Alternative: Use UTC Everywhere

If you want everything in UTC:
```yaml
environment:
  - TZ=UTC
```

Then set Grafana timezone to UTC in dashboard settings.

## Why This Matters

- **Prometheus** stores timestamps in UTC
- **Grafana** displays based on configured timezone
- **Time ranges** must match between Grafana and Prometheus
- **1 hour difference** = data appears "in the future" or "in the past"

## After Fix

1. Restart containers (already done)
2. Set Grafana time range: **Last 5 minutes**
3. Generate data: http://localhost:8000/test
4. Wait 30 seconds
5. Refresh Grafana - should work!

The timezone mismatch was causing Grafana to look for data at the wrong time!

