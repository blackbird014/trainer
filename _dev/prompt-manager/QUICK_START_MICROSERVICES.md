# Quick Start: Microservices Architecture

Quick guide to run the Express + FastAPI microservices setup.

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm

## Installation

### 1. Install Python Dependencies

```bash
cd _dev/phase1/prompt-manager
pip install -e ".[api]"
```

Or manually:
```bash
pip install fastapi uvicorn[standard] prometheus-client
```

### 2. Install Node Dependencies

```bash
cd express-app
npm install
cd ..
```

## Running Services

### Option 1: Manual (Two Terminals)

**Terminal 1 - FastAPI Service:**
```bash
cd _dev/phase1/prompt-manager
python api_service.py
```

**Terminal 2 - Express App:**
```bash
cd _dev/phase1/prompt-manager/express-app
npm start
```

### Option 2: Using Start Script

```bash
cd _dev/phase1/prompt-manager
chmod +x start-services.sh
./start-services.sh
```

## Verify Services

### Check FastAPI Service
```bash
curl http://localhost:8000/health
```

### Check Express App
```bash
curl http://localhost:3000/health
```

### View API Documentation
- FastAPI Swagger UI: http://localhost:8000/docs
- FastAPI ReDoc: http://localhost:8000/redoc

## Test Endpoints

### Via Express (Port 3000)
```bash
# Fill template
curl -X POST http://localhost:3000/api/prompt/fill \
  -H "Content-Type: application/json" \
  -d '{
    "template_content": "Hello {name}!",
    "params": {"name": "World"}
  }'
```

### Via FastAPI Directly (Port 8000)
```bash
# Fill template
curl -X POST http://localhost:8000/prompt/fill \
  -H "Content-Type: application/json" \
  -d '{
    "template_content": "Hello {name}!",
    "params": {"name": "World"}
  }'
```

## Architecture

```
Express (3000) → FastAPI (8000) → PromptManager
```

- Express handles main application logic
- FastAPI exposes PromptManager as microservice
- Both can run independently

## Troubleshooting

### FastAPI not starting
- Check Python dependencies: `pip list | grep fastapi`
- Check port 8000 is available: `lsof -i :8000`

### Express not starting
- Check Node dependencies: `cd express-app && npm list`
- Check port 3000 is available: `lsof -i :3000`
- Check FastAPI is running first

### Connection errors
- Ensure FastAPI is running before Express
- Check `FASTAPI_URL` environment variable
- Verify CORS settings in `api_service.py`

## Next Steps

- See `ARCHITECTURE.md` for detailed architecture
- See `express-app/README.md` for Express-specific docs
- View Prometheus metrics at http://localhost:8000/metrics

