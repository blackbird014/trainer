# Old Monitoring Cleanup

## Summary

The Grafana container on port 3001 (`prompt_manager_grafana`) is from an **old, deprecated monitoring setup** that was used for prompt-manager module testing.

## Status

✅ **The old docker-compose.yml has been removed** from `_dev/prompt-manager/`  
⚠️ **The container is still running** from a previous session  
✅ **New centralized monitoring** is now in `_dev/monitoring/` (uses port 3000)

## Cleanup Command

Run this to stop and remove the old containers:

```bash
# Stop and remove old containers
docker stop prompt_manager_grafana prompt_manager_prometheus
docker rm prompt_manager_grafana prompt_manager_prometheus

# Or use the cleanup script
cd _dev/prompt-manager
./cleanup-old-monitoring.sh
```

## What Was Found

### Old Setup (Deprecated)
- Location: Was in `_dev/prompt-manager/` (now removed)
- Container names: `prompt_manager_grafana`, `prompt_manager_prometheus`
- Grafana port: 3001 (mapped from container port 3000)
- Purpose: Module-specific monitoring for prompt-manager

### New Setup (Current)
- Location: `_dev/monitoring/`
- Container names: `trainer_monitoring_*`
- Grafana port: 3000
- Purpose: Centralized monitoring for all modules and mini-apps

## Documentation References

The old setup is still mentioned in documentation files (for historical reference):
- `_dev/prompt-manager/DOCKER_SETUP.md` - Marked as DEPRECATED
- `_dev/prompt-manager/QUICK_START.md` - References old setup
- `_dev/prompt-manager/COLIMA_SETUP.md` - Mentions port 3001

These are kept for reference but the actual docker-compose.yml has been removed.

## No Scripts Start It Anymore

✅ `start-services.sh` in prompt-manager - Only starts FastAPI and Express, no Docker  
✅ No docker-compose.yml exists in prompt-manager  
✅ All monitoring is now centralized in `_dev/monitoring/`

The container is just a leftover from previous testing sessions.

## Verify Cleanup

After running cleanup, verify:

```bash
# Should show no prompt_manager containers
docker ps -a | grep prompt_manager

# Should show new monitoring containers
docker ps | grep trainer_monitoring
```

