# Improvements Plan (Monitoring & Logging)

## 1) Loki/Grafana “fix” status
- Current state: Datasources were manually recreated with UIDs `loki` and `prometheus` after provisioning failed. Grafana now works, but the fix is procedural (manual API calls), not a stable, repeatable setup.
- Risks: Restarting Grafana could reintroduce UID drift if provisioning resumes with different IDs; manual steps are brittle.
- What to do next (make it real):
  - Re-enable datasource provisioning with explicit `uid` fields and validate it starts cleanly.
  - Add a single setup script (monitoring bootstrap) that:
    1) Generates Promtail config from `log-sources.yml`
    2) Ensures volume mounts exist
    3) `docker-compose up -d` for loki/promtail/prometheus/grafana
    4) Waits for Loki & Prometheus health
    5) Verifies datasources via Grafana API (and fixes UID if missing)
    6) Imports dashboards (or verifies they are present)
  - Document the one-command flow (e.g., `_dev/monitoring/bootstrap-monitoring.sh`) to guarantee reproducibility.

## 2) Logging enhancements for richer Grafana views
- Goal: Better signal-to-noise, structured logs, and consistent labels for correlation in Loki.
- Modules to cover: data-store, data-retriever, prompt-manager, llm-provider, format-converter, orchestrator, web-server, monitoring helpers.
- Recommended improvements:
  - Logging levels: use `DEBUG` for dev, `INFO` for normal ops, `WARN/ERROR` for issues; avoid noisy DEBUG in prod except behind flags.
  - Handlers: console + rotating file (size/time), keep retention; optional JSON formatter for machine parsing; avoid losing stdout logs.
  - Structure: include `miniapp`, `module`, `service`, `request_id`/`trace_id`, `user/session` (when available), and key domain fields (ticker, job id).
  - Error detail: log stack traces at ERROR with contextual fields, not only messages.
  - Health/ops: log startups, shutdowns, reloads, config versions.
  - Promtail/Loki labels: align with logging fields so LogQL filters match (e.g., labels `miniapp`, `module`, `environment`, `service`).
  - Redaction: ensure sensitive fields (tokens, PII) are masked before logging.
  - Tests/checks: add a lint/check script to validate logging config per module (level, formatter, handler, labels present).

## 3) Implementation outline (next tasks)
- Create `bootstrap-monitoring.sh` that encapsulates generation, stack startup, health checks, datasource UID verification, and dashboard load.
- **Integrate monitoring bootstrap into the mini-app one-command flow**:
  - `start-all-services.sh` remains the single entrypoint for local dev.
  - Inside `start-all-services.sh`, after:
    - ensuring all log directories exist
    - starting the Python/Node/etc. services
    - it calls `_dev/monitoring/bootstrap-monitoring.sh` as the monitoring step.
  - This guarantees that “stop-all → start-all” always brings up both the app and a correctly configured monitoring stack.
- Re-enable and validate datasource provisioning files with fixed UIDs; remove manual API steps from runbooks.
- Standardize Python logging config for all modules:
  - shared formatter (JSON or key-value)
  - rotating file handler + console
  - module-specific logger names and levels
  - ensure logs land in the paths declared in `log-sources.yml`
- Update `log-sources.yml` as needed so Promtail picks up new/rotated files.
- Add quick verification steps: `docker logs grafana|loki|promtail`, `curl loki /ready`, `curl grafana /api/datasources`, and a sample LogQL query to confirm ingestion.

### Sketch: updated `_dev/stock-miniapp/start-all-services.sh`

High-level structure (conceptual, not exact code):

```bash
#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$SCRIPT_DIR/../.."

# 0) Prepare logs
# - create ./logs directory and per-service log files/dirs

# 1) Start core services (data-store, data-retriever, prompt-manager, etc.)
# - each with stdout/stderr redirected into ./logs/*.log as already done

# 2) Start monitoring stack via bootstrap
"$ROOT_DIR/_dev/monitoring/bootstrap-monitoring.sh"

# 3) Final status / URLs
# - print Prometheus, Grafana, and Loki URLs
```

`bootstrap-monitoring.sh` itself will:
- generate Promtail config from all `log-sources.yml`
- ensure directories/volumes for logs exist
- `docker-compose up -d` (loki, promtail, prometheus, grafana)
- wait for `/ready` on Loki and `/api/health` on Grafana
- verify/create datasources with UIDs `loki` and `prometheus`
- (optionally) verify dashboards are present.

