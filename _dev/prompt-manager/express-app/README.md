# Express App for Prompt Manager

Express application that calls the PromptManager FastAPI microservice.

## Quick Start

1. Install dependencies:
```bash
npm install
```

2. Start the server:
```bash
npm start
```

For development with auto-reload:
```bash
npm run dev
```

## Configuration

Set the FastAPI service URL via environment variable:
```bash
FASTAPI_URL=http://localhost:8000 npm start
```

Default: `http://localhost:8000`

## Endpoints

All endpoints proxy to the FastAPI service:

- `GET /` - API information
- `GET /health` - Health check (checks FastAPI service)
- `GET /api/stats` - Get token usage statistics
- `POST /api/prompt/load` - Load a prompt template
- `POST /api/prompt/load-contexts` - Load context files
- `POST /api/prompt/fill` - Fill template with parameters
- `POST /api/prompt/compose` - Compose multiple prompts
- `POST /api/prompt/test` - Test endpoint

## Example Usage

### Load Contexts

```bash
curl -X POST http://localhost:3000/api/prompt/load-contexts \
  -H "Content-Type: application/json" \
  -d '{
    "context_paths": ["biotech/01-introduction.md"]
  }'
```

### Fill Template

```bash
curl -X POST http://localhost:3000/api/prompt/fill \
  -H "Content-Type: application/json" \
  -d '{
    "template_content": "Hello {name}!",
    "params": {"name": "World"}
  }'
```

### Compose Prompts

```bash
curl -X POST http://localhost:3000/api/prompt/compose \
  -H "Content-Type: application/json" \
  -d '{
    "templates": ["Prompt 1", "Prompt 2"],
    "strategy": "sequential"
  }'
```

## Prerequisites

Make sure the FastAPI service is running on port 8000 before starting this app.

See `../ARCHITECTURE.md` for full architecture details.

