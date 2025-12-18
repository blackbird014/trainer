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

**Decision:** Follow the recommendation: keep monitoring generic with `/metrics` + maintained scrape targets for Prometheus/Grafana. Standardize a tiny "targets/monitoring registry" endpoint per mini-app (including stock-miniapp and any future mini-apps) when dynamic discovery is needed; fall back to static targets if that suffices.

**Implementation details:**

1. **Monitoring Registry Endpoint:**
   - Add `GET /monitoring/targets` endpoint to stock-miniapp API
   - Location: `_dev/stock-miniapp/api/` (or main API file)
   - Returns JSON array of Prometheus scrape target configurations

2. **Response Format:**
   ```json
   {
     "targets": [
       {
         "job": "stock-miniapp",
         "instance": "stock-miniapp-api",
         "url": "http://localhost:8000/metrics"
       },
       {
         "job": "data-store",
         "instance": "data-store-service",
         "url": "http://localhost:8001/metrics"
       },
       {
         "job": "prompt-manager",
         "instance": "prompt-manager-service",
         "url": "http://localhost:8002/metrics"
       }
     ]
   }
   ```

3. **Configuration:**
   - Maintain a config file or environment-based list of module service URLs
   - File: `_dev/stock-miniapp/api/monitoring_config.py` or similar
   - Read service URLs from environment variables (e.g., `DATA_STORE_URL`, `PROMPT_MANAGER_URL`) or a config file
   - Include the mini-app's own metrics endpoint in the list

4. **Prometheus Integration:**
   - Option A (static): Use existing `prometheus.yml` with hardcoded targets (current approach)
   - Option B (dynamic): Configure Prometheus HTTP SD (Service Discovery) to poll `GET /monitoring/targets` endpoint
   - For HTTP SD, add to `prometheus.yml`:
     ```yaml
     scrape_configs:
       - job_name: 'stock-miniapp-services'
         http_sd_configs:
           - url: 'http://localhost:8000/monitoring/targets'
             refresh_interval: 30s
     ```

5. **Future mini-apps:**
   - Each mini-app should implement the same `GET /monitoring/targets` endpoint
   - Prometheus can scrape multiple mini-app endpoints for multi-app environments
   - Standardize the response format across all mini-apps for consistency

6. **Fallback:**
   - If dynamic discovery isn't needed, skip the endpoint and use static `prometheus.yml` targets
   - The endpoint can be added later without breaking existing static configurations

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

