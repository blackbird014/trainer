# Starting Services for Stock Mini-App

This document explains how to start all services needed for testing the stock-miniapp.

## Quick Start

### For DB Viewer Testing (Minimal Services)

To test just the DB viewer feature, run:

```bash
cd _dev/stock-miniapp
./start-db-viewer.sh
```

Or force a rebuild of the React app:
```bash
FORCE_REBUILD=true ./start-db-viewer.sh
```

This starts:
- MongoDB (Docker container)
- data-store API (port 8007)
- Stock Mini-App Web UI (port 3003)

Access the app at: **http://localhost:3003**

Press `Ctrl+C` to stop all services.

### For Full Application Testing (All Services)

To test the complete application with all features (including prompt flow), run:

```bash
cd _dev/stock-miniapp
./start-all-services.sh
```

Or force a rebuild of the React app:
```bash
FORCE_REBUILD=true ./start-all-services.sh
```

This starts:
- MongoDB (Docker container)
- data-store API (port 8007)
- data-retriever API (port 8003)
- prompt-manager API (port 8000)
- llm-provider API (port 8001)
- format-converter API (port 8004)
- Orchestrator (port 3002)
- Stock Mini-App Web UI (port 3003)

Access the app at: **http://localhost:3003**

Press `Ctrl+C` to stop all services.

## Stopping Services

To stop all services started by either script:

```bash
cd _dev/stock-miniapp
./stop-all-services.sh
```

Or simply press `Ctrl+C` in the terminal where the start script is running.

## Service Details

### Ports Used

| Port | Service | Required For |
|------|---------|-------------|
| 27017 | MongoDB | All features |
| 8007 | data-store | All features |
| 8003 | data-retriever | Scraping, prompt flow |
| 8000 | prompt-manager | Prompt flow |
| 8001 | llm-provider | Prompt flow |
| 8004 | format-converter | Prompt flow |
| 3002 | orchestrator | Prompt flow |
| 3003 | Web UI | All features |

### Logs

All service logs are written to:
```
_dev/stock-miniapp/logs/
```

Each service has its own log file:
- `data-store.log`
- `data-retriever.log`
- `prompt-manager.log`
- `llm-provider.log`
- `format-converter.log`
- `orchestrator.log`
- `web-server.log`
- `react-build.log` (build output)

## Prerequisites

Before running the scripts, ensure:

1. **Docker is installed and running**
   - Required for MongoDB
   - Check with: `docker ps`

2. **Node.js and npm are installed**
   - Required for React and Express
   - Check with: `node --version` and `npm --version`

3. **Python 3.8+ is installed**
   - Required for all Python services
   - Check with: `python --version`

4. **Dependencies are installed**
   - The scripts will attempt to install missing dependencies automatically
   - If issues occur, install manually:
     ```bash
     # For each Python module
     cd _dev/<module-name>
     pip install -e .
     
     # For React app
     cd _dev/stock-miniapp/web/client
     npm install
     
     # For Express server
     cd _dev/stock-miniapp/web
     npm install
     ```

## Troubleshooting

### MongoDB Not Starting

```bash
# Check if Docker is running
docker ps

# Manually start MongoDB
cd _dev/data-store
./setup_mongodb.sh
```

### Port Already in Use

If a port is already in use, you can:

1. Stop the conflicting service
2. Or modify the port in the service's configuration file

### Services Not Responding

1. Check logs in `_dev/stock-miniapp/logs/`
2. Verify services are running: `ps aux | grep python` or `ps aux | grep node`
3. Test individual services:
   ```bash
   curl http://localhost:8007/health  # data-store
   curl http://localhost:3003/health  # web server
   ```

### React Build Fails

```bash
cd _dev/stock-miniapp/web/client
rm -rf build node_modules
npm install
npm run build
```

### React Build Not Updating

The scripts automatically detect when source files are newer than the build and rebuild automatically. However, if you need to force a rebuild:

```bash
# Force rebuild when starting services
FORCE_REBUILD=true ./start-all-services.sh

# Or manually rebuild
cd _dev/stock-miniapp/web/client
npm run build
```

## Manual Service Start (Alternative)

If you prefer to start services manually:

### 1. Start MongoDB
```bash
cd _dev/data-store
./setup_mongodb.sh
```

### 2. Start data-store
```bash
cd _dev/data-store
./run_api.sh
```

### 3. Start other services (in separate terminals)
```bash
# data-retriever
cd _dev/data-retriever
./run_api.sh

# prompt-manager
cd _dev/prompt-manager
python api_service.py

# llm-provider
cd _dev/llm-provider
./run_api.sh

# format-converter
cd _dev/format-converter
python api_service.py

# orchestrator
cd _dev/stock-miniapp/api
./run_orchestrator.sh
```

### 4. Build and start web server
```bash
# Build React app
cd _dev/stock-miniapp/web/client
npm install
npm run build

# Start Express server
cd _dev/stock-miniapp/web
npm install
npm start
```

## Testing Services

After starting services, test them:

```bash
cd _dev/stock-miniapp
./test_services.sh
```

This script checks all services and reports their status.

