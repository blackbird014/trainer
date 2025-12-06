# Colima Setup for Docker

## Quick Start with Colima

### 1. Start Colima

```bash
colima start
```

This will:
- Start the Lima VM
- Set up Docker daemon
- Configure Docker socket

**First time**: May take 2-3 minutes to download and set up VM.

### 2. Verify Docker is Working

```bash
docker ps
# Should show empty list (no error)

docker --version
# Should show Docker version
```

### 3. Set Docker Context (if needed)

```bash
# Check current context
docker context ls

# Use colima context
docker context use colima
```

### 4. Start Metrics Server (Terminal 1)

```bash
cd _dev/phase1/prompt-manager
source .venv/bin/activate
python app_with_metrics.py
```

### 5. Start Docker Containers (Terminal 2)

```bash
cd _dev/phase1/prompt-manager
docker-compose up -d
```

### 6. Access Dashboards

- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Test: http://localhost:8000/test

## Colima Commands

```bash
# Start Colima
colima start

# Stop Colima
colima stop

# Check status
colima status

# View logs
colima logs

# Restart
colima restart
```

## Troubleshooting

### Socket Error

If you get socket errors:

```bash
# Make sure Colima is running
colima status

# If not running, start it
colima start

# Verify Docker works
docker ps
```

### Context Issues

```bash
# List contexts
docker context ls

# Use colima context
docker context use colima

# Or set environment variable
export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"
```

### Port Conflicts

If ports 9090 or 3000 are in use, edit `docker-compose.yml`:

```yaml
ports:
  - "9091:9090"  # Change external port
  - "3001:3000"
```

## Stop Everything

```bash
# Stop containers
docker-compose down

# Stop Colima (optional - keeps VM running)
colima stop

# Or stop Colima completely
colima stop --force
```

## Resource Usage

Colima is lighter than Docker Desktop:
- **VM RAM**: ~2GB default (configurable)
- **Disk**: ~5-10GB
- **CPU**: Minimal when idle

## Configuration

Edit Colima settings:

```bash
# Start with custom resources
colima start --cpu 4 --memory 4

# Or edit config
colima edit
```

## See Also

- Colima docs: https://github.com/abiosoft/colima
- `QUICK_START.md` - General quick start guide
- `DOCKER_SETUP.md` - Docker setup details

