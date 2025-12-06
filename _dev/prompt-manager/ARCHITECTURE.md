# Microservices Architecture

This document describes the microservices architecture for the Prompt Manager system.

## Architecture Overview

```
┌─────────────────┐         HTTP REST         ┌──────────────────┐
│  Node/Express   │ ────────────────────────> │  FastAPI Service │
│  (Port 3000)    │                           │  (Port 8000)     │
│  Main App       │ <──────────────────────── │  PromptManager   │
└─────────────────┘                           └──────────────────┘
```

## Components

### 1. FastAPI Service (`api_service.py`)
- **Port**: 8000
- **Purpose**: Exposes PromptManager functionality as a REST API
- **Technology**: FastAPI + Uvicorn
- **Endpoints**:
  - `GET /` - API information
  - `GET /health` - Health check
  - `GET /metrics` - Prometheus metrics
  - `GET /stats` - Token usage statistics
  - `POST /prompt/load` - Load a prompt template
  - `POST /prompt/load-contexts` - Load context files
  - `POST /prompt/fill` - Fill template with parameters
  - `POST /prompt/compose` - Compose multiple prompts
  - `POST /prompt/test` - Test endpoint

### 2. Express App (`express-app/server.js`)
- **Port**: 3000
- **Purpose**: Main application that calls FastAPI service
- **Technology**: Node.js + Express
- **Endpoints**:
  - `GET /` - API information
  - `GET /health` - Health check (checks FastAPI)
  - `GET /api/stats` - Proxy to FastAPI stats
  - `POST /api/prompt/load` - Proxy to FastAPI load
  - `POST /api/prompt/load-contexts` - Proxy to FastAPI load-contexts
  - `POST /api/prompt/fill` - Proxy to FastAPI fill
  - `POST /api/prompt/compose` - Proxy to FastAPI compose
  - `POST /api/prompt/test` - Proxy to FastAPI test

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd _dev/phase1/prompt-manager
pip install -e ".[api]"
```

Or install manually:
```bash
pip install fastapi uvicorn[standard] prometheus-client
```

### 2. Install Node Dependencies

```bash
cd _dev/phase1/prompt-manager/express-app
npm install
```

### 3. Start FastAPI Service

Terminal 1:
```bash
cd _dev/phase1/prompt-manager
python api_service.py
```

The service will start on `http://localhost:8000`

### 4. Start Express App

Terminal 2:
```bash
cd _dev/phase1/prompt-manager/express-app
npm start
```

The app will start on `http://localhost:3000`

## Testing

### Test FastAPI Directly

```bash
# Health check
curl http://localhost:8000/health

# Stats
curl http://localhost:8000/stats

# Load contexts
curl -X POST http://localhost:8000/prompt/load-contexts \
  -H "Content-Type: application/json" \
  -d '{"context_paths": ["biotech/01-introduction.md"]}'

# Fill template
curl -X POST http://localhost:8000/prompt/fill \
  -H "Content-Type: application/json" \
  -d '{
    "template_content": "Hello {name}!",
    "params": {"name": "World"}
  }'
```

### Test Express App

```bash
# Health check
curl http://localhost:3000/health

# Stats (proxied to FastAPI)
curl http://localhost:3000/api/stats

# Fill template (proxied to FastAPI)
curl -X POST http://localhost:3000/api/prompt/fill \
  -H "Content-Type: application/json" \
  -d '{
    "template_content": "Hello {name}!",
    "params": {"name": "World"}
  }'
```

## API Documentation

### FastAPI Swagger UI

Visit `http://localhost:8000/docs` for interactive API documentation.

### FastAPI ReDoc

Visit `http://localhost:8000/redoc` for alternative API documentation.

## Environment Variables

### Express App

- `FASTAPI_URL`: FastAPI service URL (default: `http://localhost:8000`)

Example:
```bash
FASTAPI_URL=http://localhost:8000 npm start
```

## Production Considerations

### Port Configuration

- **Development**: Express (3000), FastAPI (8000)
- **Production**: Use reverse proxy (Nginx/Caddy) on ports 80/443
  - Proxy routes to Express (internal port 3000)
  - Express calls FastAPI (internal port 8000)

### CORS Configuration

FastAPI CORS is configured for `http://localhost:3000`. Update in production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Production domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Prometheus Metrics

FastAPI service exposes Prometheus metrics at `/metrics` endpoint. Configure Prometheus to scrape:

```yaml
scrape_configs:
  - job_name: 'prompt-manager-api'
    static_configs:
      - targets: ['localhost:8000']
```

## Migration from Flask

The FastAPI service (`api_service.py`) replaces the Flask app (`app_with_metrics.py`). Both provide the same functionality, but FastAPI offers:

- Better async support
- Automatic OpenAPI documentation
- Type validation with Pydantic
- Better performance
- Modern Python async/await patterns

The Flask app can still be used for backward compatibility, but FastAPI is recommended for new deployments.

