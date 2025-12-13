# Test-Agent Tools

This directory contains additional tools and utilities for the test-agent module.

## Dashboard

A web-based dashboard for viewing test analysis, module statistics, and accessing module-specific views.

### Features

- **Test Analysis Viewer**: View comprehensive test analysis reports
- **Module Navigation**: Quick access to all module API services
- **Data Store Browser**: Links to data-store API and MongoDB
- **Format Converter Viewer**: Access to HTML document viewer
- **Monitoring Links**: Direct links to Grafana and Prometheus

### Usage

Start the dashboard server:

```bash
cd _dev/test-agent
python tools/dashboard.py
```

Or with custom host/port:

```bash
python tools/dashboard.py --host 0.0.0.0 --port 8889
```

### Access

Once running, open your browser to:

- **Main Dashboard**: http://localhost:8889/
- **Test Analysis**: http://localhost:8889/test-analysis
- **Data Store**: http://localhost:8889/data-store
- **Format Converter**: http://localhost:8889/format-converter
- **Modules**: http://localhost:8889/modules

### API Endpoints

The dashboard also provides API endpoints:

- `GET /api/test-analysis` - Get test analysis data (JSON)
- `GET /api/test-analysis?module=<name>` - Get specific module analysis
- `GET /api/modules` - Get module information
- `GET /health` - Health check

### Requirements

- FastAPI
- Uvicorn
- Jinja2
- test-agent module

All dependencies are included in test-agent's `pyproject.toml`.

### Integration

The dashboard integrates with:
- Test analysis reports (from `comprehensive_analysis.py`)
- Module API services (if running)
- MongoDB (via data-store)
- Grafana/Prometheus (monitoring)

