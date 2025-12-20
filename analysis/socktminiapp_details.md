# Stock Mini-App – Operational Checks (Data, Logs, Tests)

This document outlines how to inspect the running mini-app (stock-miniapp) focusing on three areas: (1) a lightweight MongoDB data viewer for collections, (2) log/metrics inspection with Grafana/Prometheus, and (3) running tests with test-agent for this app while keeping modules versioned for future reuse.

---

## 1) Simple UI to inspect MongoDB collections in real time

**Goal:** Quickly verify that the app (or any similar mini-app) is inserting documents into MongoDB (e.g., `seed_companies`, `prompt_runs`) without opening a database shell.

### What data-store already offers
- FastAPI service with REST endpoints:
  - `POST /store`, `POST /bulk_store`, `POST /update/{key}`, `DELETE /delete/{key}`, `GET /exists/{key}`
  - `POST /query` (filters, sort, limit, offset) with optional `collection` override
  - `POST /count`, `POST /distinct/{field}`
  - Metrics at `/metrics`, health at `/health`
- Backend abstraction (MongoDB in this deployment) and per-collection overrides via the request body.

### Options for a viewer
- **Option A: Mini-app UI uses data-store API** (recommended)
  - Build a minimal “Collection Explorer” page in the stock mini-app that calls data-store `POST /query` and `POST /count` with a selected collection and optional filters.
  - Pros: No new backend; respects the service boundary; works even if modules live elsewhere.
  - Cons: Needs simple UI work (table + filter form).
- **Option B: Embed explorer inside data-store**
  - Add a tiny UI served by data-store itself to call its own endpoints.
  - Pros: Self-contained; reusable across apps.
  - Cons: Couples UI into the module; less aligned with keeping modules headless/servicelike.

**Recommendation:** Implement the explorer in the mini-app, calling the data-store APIs. This keeps modules clean, headless, and reusable by any app (including future separate repos). Keep it very simple (collection selector, filter JSON, limit, results table).

---

## 2) Logs and metrics analysis (Grafana/Prometheus)

**Goal:** Inspect logs/metrics for the mini-app and its modules (prompt-manager, data-store, data-retriever, llm-provider, format-converter, orchestrator).

### Current monitoring approach
- Each module exposes `/metrics` (Prometheus format) and `/health`.
- Monitoring stack (Grafana/Prometheus) is present but not always running; ports 3000/3001 were used for Grafana in prior setups.
- Logs are local (stdout) per service; orchestrator now logs step-by-step with `run_id`.

### Generic vs app-specific monitoring
- The metrics model is already generic: every module exposes `/metrics`; Prometheus just needs scrape targets.
- To monitor a specific mini-app plus its modules:
  - Provide Prometheus with the list of service endpoints (could be static in `prometheus.yml` or dynamically generated).
  - Grafana dashboards can be templated by job/instance labels, so the same dashboard can visualize any module/mini-app as long as targets are known.
- If dynamic discovery is needed (multiple mini-apps, multiple module deployments):
  - Optionally expose a small “monitoring registry” service from the mini-app (or a shared utility) that lists active module endpoints for Prometheus/Grafana to scrape/label.
  - Otherwise, maintain a simple static target list per environment.

**Recommendation:** Keep monitoring generic. Use the existing `/metrics` endpoints and maintain a small target list per environment. Add a lightweight “targets” file/service only if you need dynamic discovery across many mini-apps.

---

## 3) Running tests with test-agent for stock-miniapp only

**Goal:** Run tests focused on the stock mini-app while treating the other modules as a versioned framework that may live in another repo in the future.

### Current situation
- test-agent can discover and run tests per module and generate coverage.
- The stock mini-app depends on services from the other modules; in a “library + services” model, those modules may be pulled as packages or remote services.

### How to scope tests now
- Use test-agent with module selection (or by path) to run only the stock-miniapp tests.
- For integration flows, you still need service endpoints reachable (real or mocked). Since modules are services, you can run them in mock/lightweight mode or provide recorded responses.
- Keep module tests separate (versioned in their own repos later). The mini-app tests should focus on:
  - UI/API integration against service endpoints (could be mocked).
  - Orchestrator flow tests (can stub llm-provider, etc.).
  - Minimal contract checks to ensure the app can talk to the services’ published APIs.

### Future-proofing when modules live elsewhere
- Treat modules as external services/libraries:
  - If consumed as services: point the mini-app tests to test instances/mocks.
  - If consumed as packages: pin versions and run unit tests for the app only; module tests remain in their own repos/CI.
- Keep a small contract/health check suite in the mini-app to ensure API compatibility with the framework modules.

**Recommendation:** Run test-agent scoped to stock-miniapp tests. For integration flows, spin up (or mock) the required services; avoid running all module tests from the mini-app CI once modules move to separate repos. Maintain light contract checks to ensure API compatibility.

---

## Implementation decisions

### Viewer option A

**Decision:** Use the mini-app UI that calls data-store `/query` and `/count` (Option A) rather than embedding a viewer into data-store. Keep it minimal (collection selector, filters, limit, results table) so the approach stays reusable across future mini-apps.

**Implementation details:**

1. **UI Component Location and Navigation:**
   - Create a new React component: `_dev/stock-miniapp/web/client/src/components/CollectionExplorer.js`
   - Add a link in the main App page (`App.js`) pointing to the DB viewer (e.g., "View Database Collections" button/link)
   - The DB viewer will be accessible at `http://localhost:3003/dbviewer` (or similar route)
   - Add a "Back" button in the DB viewer component to return to the main page
   - Since the app uses client-side routing (or can be extended with React Router), handle navigation between main page and viewer

2. **UI Components:**
   - Collection selector dropdown: populate dynamically from endpoint (see point 3 below)
   - Filter input: JSON textarea for MongoDB query filters (e.g., `{"status": "active"}`)
   - Limit input: number field (default: 50, max: 1000)
   - Sort input: JSON object (e.g., `{"created_at": -1}`)
   - Results table: display documents as rows, with expandable JSON view for nested fields
   - Count display: show total matching documents (from `POST /count`)
   - Refresh button: re-fetch current query
   - Back button: navigate back to main page

3. **Collection Lists Endpoint:**
   - **Add endpoint in data-store API**: `GET /collections`
   - Location: `_dev/data-store/api_service.py` (FastAPI service)
   - Implementation: Query MongoDB to list all collections in the configured database
   - Response format:
     ```json
     {
       "collections": ["seed_companies", "prompt_runs", "stock_data", "data_store"]
     }
     ```
   - **Architecture flow:**
     - React component calls `GET /api/collections` (relative URL)
     - Express server (`server.js`) receives `/api/collections`
     - Express proxy (line 18-156 in `server.js`) strips `/api` prefix and forwards to data-store as `GET /collections`
     - Data-store returns the list of collections
     - Express proxy forwards the response back to React component
   - **No orchestrator needed**: The existing Express proxy at `/api/*` automatically routes all non-`/prompt/*` requests to data-store (see `server.js` lines 87-89)
   - The UI component will call `GET /api/collections` on mount to populate the collection dropdown

4. **Data Store Service URL Configuration:**
   - The stock-miniapp Express server (`_dev/stock-miniapp/web/server.js`) already reads `DATA_STORE_URL` from environment variable
   - Current default: `http://127.0.0.1:8007` (line 8 in `server.js`)
   - Configuration pattern: `const DATA_STORE_URL = process.env.DATA_STORE_URL || 'http://127.0.0.1:8007';`
   - The DB viewer component should use the same proxy pattern: make requests to `/api/query`, `/api/count`, etc., which are already proxied to data-store by the Express server
   - No additional configuration needed in the React component - it uses relative URLs that go through the Express proxy

5. **API Integration:**
   - All API calls from React component use relative URLs starting with `/api/*`
   - **Request flow**: React → Express server (`localhost:3003`) → data-store (`localhost:8007`)
   - **Endpoints to call:**
     - `GET /api/collections` → proxied to data-store `GET /collections` (to be implemented in data-store)
     - `POST /api/count` → proxied to data-store `POST /count` (already exists)
     - `POST /api/query` → proxied to data-store `POST /query` (already exists)
   - **Proxy routing**: Express server automatically routes `/api/*` (except `/api/prompt/*`) to data-store via the existing proxy middleware (no orchestrator needed)
   - Handle errors gracefully (invalid JSON, collection not found, data-store unavailable)
   - Show loading states during API calls

6. **Normal Use Cases (for reference):**
   - The stock-miniapp runs on `localhost:3003` (Express server)
   - Data-store service runs on `localhost:8007` (default, configurable via `DATA_STORE_URL`)
   - Express server proxies `/api/*` requests to data-store automatically
   - React app makes relative API calls (e.g., `/api/query`) which are handled by Express proxy
   - Environment variables can override service URLs if needed (e.g., `DATA_STORE_URL=http://other-host:8007`)

7. **Future mini-apps:**
   - Package this component as a reusable module or copy the pattern
   - Ensure the collections endpoint pattern is replicated in other mini-apps
   - The Express proxy pattern for `/api/*` should be consistent across mini-apps

### Logs and metrics analysis

**Decision:** Implement a centralized monitoring architecture with a standalone monitoring service that polls mini-apps to discover services dynamically. Mini-apps use a shared monitoring library to expose their service configurations. This approach scales well for 1-3 mini-apps per customer and can be extended with messaging queues if needed for larger scale.

**Architecture Overview:**

The monitoring system consists of three components:

1. **Monitoring Service (Standalone)**
   - Runs as an independent FastAPI service
   - Polls mini-apps periodically (e.g., every 30 seconds) to discover services
   - Aggregates service information from all mini-apps
   - Exposes Prometheus HTTP Service Discovery (HTTP SD) endpoint
   - Location: `_dev/monitoring/` (as a Python package with standalone API service)

2. **Monitoring Library (Python Package)**
   - Installable package: `pip install -e _dev/monitoring`
   - Provides shared utilities for mini-apps
   - Defines the "contract" (API signature) between monitoring and mini-apps
   - Location: `_dev/monitoring/src/monitoring/prometheus_sd.py`

3. **Mini-Apps**
   - Import the monitoring library
   - Know their own dependencies (which modules they use)
   - Expose endpoint: `GET /monitoring/targets`
   - Provide configuration: list of services they use with URLs

**Data Flow:**

```
Monitoring Service (standalone)
    │
    │ (polls every 30s)
    │
    ├─→ Stock Mini-App
    │       │
    │       ├─→ Uses monitoring library
    │       ├─→ Provides config: ['data-store:8007', 'llm-provider:8001', ...]
    │       └─→ Exposes: GET /monitoring/targets
    │
    └─→ (aggregates all services)
         │
         └─→ Exposes: GET /monitoring/targets (for Prometheus)
              │
              └─→ Prometheus HTTP SD
                   └─→ Scrapes all discovered services
```

**Implementation details:**

1. **Make monitoring a Python package:**
   - Add `pyproject.toml` to `_dev/monitoring/` with dependencies:
     ```toml
     dependencies = [
         "fastapi>=0.104.0",
         "uvicorn[standard]>=0.24.0",
         "httpx>=0.24.0",      # For async HTTP polling
         "pyyaml>=6.0.0",       # For YAML config files
         "pydantic>=2.0.0",     # For data validation
     ]
     ```
   - Create `src/monitoring/` directory structure (location: `_dev/monitoring/src/monitoring/`)
   - Create `src/monitoring/__init__.py` to export public API
   - Create `src/monitoring/prometheus_sd.py` with utility functions:
     ```python
     from pathlib import Path
     from typing import List, Dict, Any
     
     def load_services_config(config_path: Path) -> Dict[str, str]:
         """
         Load services configuration from YAML file.
         Returns: Dict mapping service name to URL, e.g. {'data-store': 'http://localhost:8007', ...}
         """
         
     def create_prometheus_targets(services_config: Dict[str, str], 
                                    miniapp_name: str = None) -> List[Dict[str, Any]]:
         """
         Convert services config to Prometheus HTTP SD format.
         Returns: List of Prometheus target dicts with 'targets' and 'labels' keys
         """
         
     def format_target_url(url: str) -> str:
         """
         Format URL for Prometheus (strip protocol, extract host:port).
         Returns: Target string like 'localhost:8007'
         """
     ```
   - Install in venv: `pip install -e _dev/monitoring` (automatically installs into active venv)
   - Development workflow:
     ```bash
     # Activate mini-app venv
     cd _dev/stock-miniapp/api
     source venv/bin/activate
     
     # Install monitoring library (installs into this venv)
     pip install -e ../../monitoring
     ```

2. **Create standalone monitoring API service:**
   - File: `_dev/monitoring/api_service.py`
   - FastAPI service that:
     - Maintains list of mini-app URLs to poll (config file or environment)
     - Runs periodic polling job using asyncio (every 30 seconds)
     - Implements hash-based caching to detect changes per mini-app
     - Aggregates targets from all mini-apps
     - Exposes `GET /monitoring/targets` endpoint in Prometheus HTTP SD format
     - Exposes `GET /monitoring/health` for health checks (shows mini-app reachability)
     - Exposes `POST /monitoring/refresh` to force full cache refresh
     - Exposes `POST /monitoring/refresh/{miniapp_url}` to force refresh for specific mini-app
   - **Polling implementation:**
     - Use asyncio periodic task (not FastAPI BackgroundTasks, which runs after response)
     - Startup event creates async polling task:
       ```python
       @app.on_event("startup")
       async def start_polling():
           asyncio.create_task(poll_miniapps_periodically())
       
       async def poll_miniapps_periodically():
           while True:
               await poll_and_update_cache()
               await asyncio.sleep(30)  # 30 second interval
       ```
   - **Caching strategy:**
     - Cache structure: `{miniapp_url: {"hash": "...", "targets": [...], "last_update": timestamp}}`
     - Hash: SHA256 of targets JSON (detects changes at module service level)
     - On startup: Load all mini-apps, cache with hash
     - On poll: Compare hash, update cache only if changed
     - Force refresh endpoints: API endpoints that trigger immediate refresh (future: can call from script/UI)
   - **Error handling:**
     - If mini-app is down: Keep last known good cache entry, log warning, don't fail
     - Health endpoint shows which mini-apps are reachable
     - Future: Heartbeat/health checks can mark services as unhealthy
   - Configuration: `_dev/monitoring/config.yml` or environment variables:
     ```yaml
     miniapps:
       - url: http://localhost:3003
         name: stock-miniapp
     polling_interval: 30
     port: 8008  # Configurable via PORT environment variable
     ```

3. **Mini-app integration (stock-miniapp example):**
   - Install monitoring library in mini-app's venv: `pip install -e ../monitoring`
     - Note: When working in venv, `pip install -e` automatically installs into the active venv
     - No special handling needed - just activate venv and install
   - Create configuration file: `_dev/stock-miniapp/api/monitoring_config.yaml`:
     ```yaml
     services:
       - name: stock-miniapp
         url: http://localhost:3003
       - name: data-store
         url: http://localhost:8007
       - name: data-retriever
         url: http://localhost:8003
       - name: prompt-manager
         url: http://localhost:8000
       - name: llm-provider
         url: http://localhost:8001
       - name: format-converter
         url: http://localhost:8004
     ```
   - In `_dev/stock-miniapp/api/orchestrator_service.py`:
     ```python
     from monitoring.prometheus_sd import create_prometheus_targets, load_services_config
     from pathlib import Path
     
     # Load configuration from YAML file
     config_path = Path(__file__).parent / "monitoring_config.yaml"
     services_config = load_services_config(config_path)
     
     @app.get("/monitoring/targets")
     async def get_monitoring_targets():
         """Returns Prometheus HTTP SD format targets for this mini-app's services"""
         return create_prometheus_targets(services_config, miniapp_name="stock-miniapp")
     ```
   - Note: `load_services_config()` returns `Dict[str, str]` mapping service names to URLs
   - Alternative: Environment variables can override config file values (config file as default, env vars for overrides)

4. **Prometheus configuration:**
   - Update `_dev/monitoring/prometheus/prometheus.yml`:
     ```yaml
     scrape_configs:
       # Use HTTP Service Discovery to get targets from monitoring service
       - job_name: 'all-services'
         http_sd_configs:
           - url: 'http://localhost:8008/monitoring/targets'
             refresh_interval: 30s
     ```
   - Monitoring service runs on port 8008 (or configurable)
   - Prometheus polls monitoring service, which aggregates from all mini-apps

5. **Service discovery (configuration-based):**
   - Monitoring service maintains list of mini-app URLs in config file
   - Format: `_dev/monitoring/config.yml`:
     ```yaml
     miniapps:
       - name: stock-miniapp
         url: http://localhost:3003
       # Future: can add more mini-apps here
     ```
   - For 1-3 mini-apps per customer, manual configuration is sufficient
   - Future enhancement: auto-discovery via service registry or port scanning (optional)

6. **Response format (Prometheus HTTP SD):**
   - Mini-app endpoint returns:
     ```json
     [
       {
         "targets": ["localhost:8007"],
         "labels": {
           "job": "data-store",
           "instance": "data-store-service",
           "miniapp": "stock-miniapp"
         }
       },
       {
         "targets": ["localhost:8001"],
         "labels": {
           "job": "llm-provider",
           "instance": "llm-provider-service",
           "miniapp": "stock-miniapp"
         }
       }
     ]
     ```
   - Monitoring service aggregates multiple mini-app responses into single list

7. **Future mini-apps:**
   - Each mini-app follows the same pattern:
     - Install monitoring library
     - Import `create_prometheus_targets`
     - Provide their service configuration
     - Expose `GET /monitoring/targets` endpoint
   - Add mini-app URL to monitoring service config
   - No changes needed to Prometheus config

8. **Scaling considerations:**
   - For 1-3 mini-apps per customer: polling every 30s is efficient
   - If scaling becomes an issue: can add messaging queue (RabbitMQ/Kafka) between mini-apps and monitoring service
   - Architecture supports this extension without major changes

**Implementation Execution Plan:**

The implementation should proceed in the following order:

1. **Create Python package structure with pyproject.toml**
   - Create `_dev/monitoring/` directory structure
   - Add `pyproject.toml` with dependencies
   - Create `src/monitoring/` directory and `__init__.py`

2. **Implement utility functions in `prometheus_sd.py`**
   - Implement `load_services_config()` to load YAML config files
   - Implement `format_target_url()` to format URLs for Prometheus
   - Implement `create_prometheus_targets()` to convert config to Prometheus HTTP SD format

3. **Create standalone monitoring API service with polling and caching**
   - Implement `api_service.py` with FastAPI application
   - Add asyncio periodic polling task
   - Implement hash-based caching mechanism
   - Add endpoints: `GET /monitoring/targets`, `GET /monitoring/health`, `POST /monitoring/refresh`, `POST /monitoring/refresh/{miniapp_url}`
   - Create `config.yml` for monitoring service configuration

4. **Integrate into stock-miniapp as example**
   - Install monitoring library in stock-miniapp venv
   - Create `monitoring_config.yaml` with service configurations
   - Add `GET /monitoring/targets` endpoint to `orchestrator_service.py`
   - Test integration

5. **Update Prometheus configuration**
   - Update `_dev/monitoring/prometheus/prometheus.yml` to use HTTP SD
   - Configure to poll monitoring service endpoint
   - Verify Prometheus can discover and scrape all services

### Test-agent

**Decision:** Follow the recommendation to run test-agent scoped to stock-miniapp tests, with light contract checks for module APIs. Parameterize test-agent scope (module selector/path) so the same runner can be reused across mini-apps and contexts without pulling in all module tests.

**Implementation details:**

1. **Scope Parameterization Options:**
   - Add CLI argument: `--scope <pattern>` or `--module <name>` or `--path <directory>`
   - Support multiple formats:
     - Path-based: `--scope _dev/stock-miniapp/**` (run tests in this directory tree)
     - Module name: `--scope stock-miniapp` (if test-agent has module registry)
     - Pattern: `--scope "**/stock-miniapp/**/*test*.py"` (glob pattern)
   - Config file option: `test_scope.json` or section in existing config
   - Environment variable: `TEST_AGENT_SCOPE=stock-miniapp`

2. **Implementation in test-agent:**
   - Location: `_dev/test-agent/src/` (main test discovery/runner code)
   - Modify test discovery logic to filter by scope before execution
   - If scope is provided, only discover tests matching the pattern/path
   - If no scope provided, run all tests (backward compatible)

3. **Usage Examples:**
   ```bash
   # Run only stock-miniapp tests
   python -m test_agent --scope _dev/stock-miniapp
   
   # Run tests for specific module
   python -m test_agent --module stock-miniapp
   
   # Run tests matching pattern
   python -m test_agent --scope "**/stock-miniapp/**/*test*.py"
   
   # Use config file
   python -m test_agent --config test_scope.json
   ```

4. **Config File Format (optional):**
   ```json
   {
     "scope": {
       "paths": ["_dev/stock-miniapp/**"],
       "exclude": ["**/node_modules/**", "**/venv/**"],
       "modules": ["stock-miniapp"]
     }
   }
   ```

5. **Integration with CI/CD:**
   - Stock-miniapp CI: `test-agent --scope stock-miniapp`
   - Module CI (future): `test-agent --scope <module-name>` in module's own repo
   - Full suite (local dev): `test-agent` (no scope, runs everything)

6. **Contract Checks:**
   - Add lightweight contract test suite in stock-miniapp
   - File: `_dev/stock-miniapp/tests/test_contracts.py`
   - Tests:
     - Health check endpoints for each module service
     - API schema validation (if OpenAPI/Swagger available)
     - Response format checks for critical endpoints
   - Run contract tests as part of stock-miniapp test suite

7. **Mock/Service Setup:**
   - For integration tests requiring services:
     - Option A: Start lightweight service instances (docker-compose or scripts)
     - Option B: Use mocks/stubs for module services
     - Option C: Use recorded responses (vcrpy or similar)
   - Make service setup configurable via environment or test fixtures

---

## Action summary
- Add a simple “Collection Explorer” page in the mini-app that calls data-store `/query` and `/count` (recommended over embedding UI into data-store).
- Use existing Prometheus/Grafana with a maintained target list; add a tiny “targets” registry only if you need dynamic discovery.
- Run test-agent scoped to stock-miniapp; keep module tests in their own repos, and use mocks/contracts for integration when modules are external.

