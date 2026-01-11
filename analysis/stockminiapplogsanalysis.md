# Stock Mini-App Logs Analysis

## Context

The current monitoring setup for the stock-miniapp uses **Prometheus** for metrics collection and **Grafana** for visualization. This setup is working for metrics but does not handle logs.

**Current Architecture:**
- **Prometheus**: Collects numeric time-series metrics from services via `/metrics` endpoints (counters, gauges, histograms). Services like prompt-manager, data-store, data-retriever, llm-provider, format-converter, and model-trainer expose metrics such as operations per second, latency, error counts, token usage, costs, and cache performance.
- **Grafana**: Visualizes Prometheus metrics through pre-configured dashboards showing time-series graphs, counters, histograms, and aggregated data (rates, averages, percentiles). Grafana is currently running on port 3001 (mapped from container port 3000 due to port conflict with prompt-manager on port 3000).
- **Monitoring Service**: A standalone service (port 8008) that polls mini-apps to discover services dynamically and aggregates targets for Prometheus HTTP Service Discovery.

**What's Missing:**
- **Loki**: Grafana's log aggregation system that collects, stores, and queries log data. Currently not configured.
- **Promtail**: Log collector that ships logs from services to Loki. Currently not configured.
- **Log Visualization**: While Grafana can display logs when Loki is configured, there is currently no log collection pipeline.

**Key Distinction:**
- **Metrics (Prometheus)**: Numeric time-series data showing aggregated values like "100 operations/sec", "average latency: 50ms", "total errors: 5". These are already working.
- **Logs (Loki)**: Text-based log entries showing individual events like "Error: Connection timeout at 13:45:23", "User logged in", "Processing request ID: abc123". These are not currently collected or visualized.

**Current State:**
- Services write logs to stdout/files (not aggregated)
- Grafana shows metrics (numbers, rates, durations) but cannot show logs
- Prometheus is configured but needs to be running to scrape metrics
- The monitoring service we implemented will automatically discover services via HTTP SD for Prometheus

To visualize both logs and metrics, we need to add Loki and Promtail to the monitoring stack, creating a complete observability solution.

---

## Goal

Implement a complete log monitoring system that enables visualization of application logs in Grafana dashboards alongside existing metrics. This will provide unified observability for the stock-miniapp and its dependent services, allowing developers to correlate log events with metrics, debug issues more effectively, and track application behavior over time.

**What Loki and Promtail Enable:**

- **Loki**: A horizontally-scalable log aggregation system designed to work seamlessly with Grafana. Loki stores log data in a format optimized for querying and visualization, allowing users to search, filter, and analyze logs using LogQL (Loki Query Language). Unlike traditional log systems, Loki indexes only labels (metadata) rather than log content, making it highly efficient and cost-effective. It integrates directly with Grafana as a datasource, enabling log visualization in the same dashboards as metrics.

- **Promtail**: A log shipper agent that collects logs from various sources (files, systemd journal, Docker containers, etc.) and forwards them to Loki. Promtail automatically discovers log sources, extracts labels from log files or container metadata, and tail logs in real-time. It handles log rotation, supports multiple input formats, and can parse structured logs (JSON, key-value pairs) to extract meaningful labels for filtering and querying in Grafana.

Together, Loki and Promtail create a complete log pipeline: Promtail collects logs from services → sends to Loki → Grafana queries and visualizes logs alongside metrics, providing a unified observability experience.

---

## Practical Applications of Loki/Promtail in Our System

**Use Cases:**

1. **Correlate Logs with Metrics**: When a metric shows an error spike, immediately view related log entries to understand the root cause. For example, if `data_store_errors_total` increases, query Loki for error logs from data-store service at that time.

2. **Trace Request Flows**: Follow a `run_id` across multiple services (orchestrator → prompt-manager → llm-provider → format-converter) by searching logs with the same `run_id` label, seeing the complete request journey.

3. **Debug Production Issues**: Search logs by service, log level, or keywords (e.g., "timeout", "connection error") across all services in one place, without SSHing into multiple servers or grepping through log files.

4. **Monitor Error Patterns**: Create Grafana dashboards showing error log frequency over time, grouped by service or error type, alongside error metrics.

5. **Audit and Compliance**: Query logs for specific operations (e.g., all data deletions, security validations) with full context and timestamps.

6. **Performance Analysis**: Correlate slow operations in logs (duration fields) with latency metrics, identifying bottlenecks.

7. **Alerting**: Set up alerts based on log patterns (e.g., alert when "CRITICAL" logs appear, or when error rate in logs exceeds threshold).

---

## Log Storage and Retention

**With Loki/Promtail Pipeline:**

- **Loki Storage**: Loki stores logs in its own storage backend (can be filesystem, S3, GCS, or other object storage). Logs are stored centrally in Loki, not just on individual service disks.

- **Dual Storage Strategy** (Recommended):
  - **Local Files**: Services continue writing logs to local files (for immediate access, backup, and redundancy)
  - **Loki**: Promtail reads from these files and ships to Loki (for centralized querying and visualization)
  - **Result**: Logs exist in both places - you don't lose logs, you gain centralized access

- **Retention Policies**: Loki can be configured with retention periods (e.g., keep logs for 30 days, then archive or delete). This is separate from local file retention.

- **Backup**: Local log files can still be backed up independently. Loki storage can also be backed up (if using object storage, it's automatically durable).

**Key Point**: Loki/Promtail **add** centralized log aggregation without removing existing file-based logging. Services continue logging to files as before, and Promtail collects from those files.

---

## Current Logging System Assessment

**Current State:**

- **Python Standard Logging**: Services use Python's `logging` module (similar to log4j in Java)
- **Basic Configuration**: Most services use `logging.basicConfig()` with simple format strings
- **Output**: Logs go to stdout and/or files in `_dev/stock-miniapp/logs/` (one file per service)
- **No Rotation**: No log rotation configured (files can grow indefinitely)
- **No Structured Format**: Most services use plain text format, not JSON (except prompt-manager which has JSON support)
- **No Database Logging**: Database logging exists in prompt-manager but is not actively used

**Enhancement Needs:**

1. **Log Rotation**: Implement `RotatingFileHandler` or `TimedRotatingFileHandler` to prevent log files from growing too large
2. **Structured Logging**: Use JSON formatting consistently across services for better parsing and querying
3. **Log Levels**: Already supported by Python logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
4. **Multiple Appenders**: Add handlers for:
   - **File Handler**: Write to log files (already exists)
   - **Rotating File Handler**: Auto-rotate when size/time limit reached
   - **Database Handler**: Optional - write critical logs to database (prompt-manager has this but it's not active)
   - **Console Handler**: stdout (already exists)
5. **Contextual Information**: Add structured fields (service name, run_id, request_id) for better correlation

**How Loki/Promtail Integrate:**

- **Loki/Promtail do NOT replace Python logging configuration** - they work with whatever logs are already being written
- **Promtail reads log files** (or stdout) that services are already creating
- **No code changes needed** in services - Promtail is a separate process that tails log files
- **Enhancement benefit**: If you improve logging (JSON format, better structure), Promtail can extract more meaningful labels, making queries in Grafana more powerful

**Recommended Approach:**

1. **Enhance Python logging** (add rotation, JSON format, structured fields) - this improves log quality regardless of Loki
2. **Deploy Promtail** to collect from enhanced log files
3. **Configure Loki** to store and index logs
4. **Result**: Better logs locally + centralized querying in Grafana

**Log Loss Prevention:**

- **Local files remain primary source** - if Loki fails, logs are still in files
- **Promtail can buffer** - if Loki is temporarily unavailable, Promtail can buffer logs
- **Loki replication** - can be configured for high availability
- **Backup strategy**: Continue backing up local log files; optionally backup Loki storage

---

## Deployment Strategy for Loki and Promtail

**Current Setup Verification:**

- **Prometheus**: Running in Docker container (via `docker-compose.yml` in `_dev/monitoring/`)
- **Grafana**: Running in Docker container on port 3001 (mapped from container port 3000)
- **Application Services**: Running locally as Python processes (not in Docker)
  - Services: data-store, data-retriever, prompt-manager, llm-provider, format-converter, orchestrator, monitoring
  - Started via shell scripts (`start-all-services.sh`)
  - Logs written to: `_dev/stock-miniapp/logs/` on host filesystem
  - Each service has its own log file: `data-store.log`, `orchestrator.log`, etc.

**Recommended Deployment:**

**Loki:**
- **Deploy in Docker** (same `docker-compose.yml` as Prometheus/Grafana)
- **Location**: `_dev/monitoring/docker-compose.yml`
- **Reason**: Centralized log storage, consistent with other monitoring tools, easy to manage
- **Port**: 3100 (standard Loki port)
- **Storage**: Docker volume (can be configured for filesystem or object storage)

**Promtail:**
- **Deploy in Docker** (same `docker-compose.yml`)
- **Location**: `_dev/monitoring/docker-compose.yml`
- **Reason**: Consistent deployment, easy management, but needs host filesystem access
- **Configuration**: Mount **all log directories** from all microservices as volumes
- **No port needed**: Promtail doesn't expose HTTP endpoints (it pushes to Loki)

**Log Directories to Mount:**

Since stock-miniapp uses various modules as microservices, we need to mount all possible log locations:

1. **Stock Mini-App Logs** (primary location):
   - `_dev/stock-miniapp/logs/` - Contains logs from services started via startup scripts:
     - `data-store.log`
     - `data-retriever.log`
     - `prompt-manager.log`
     - `llm-provider.log`
     - `format-converter.log`
     - `orchestrator.log`
     - `monitoring.log`
     - `web-server.log`
     - `react-build.log`

2. **Individual Module Logs** (if modules write to their own directories):
   - `_dev/prompt-manager/logs/` - If prompt-manager writes its own logs (has logging system)
   - `_dev/data-store/logs/` - If data-store writes its own logs
   - `_dev/data-retriever/logs/` - If data-retriever writes its own logs
   - `_dev/llm-provider/logs/` - If llm-provider writes its own logs
   - `_dev/format-converter/logs/` - If format-converter writes its own logs
   - `_dev/model-trainer/logs/` - If model-trainer writes its own logs
   - `_dev/test-agent/logs/` - If test-agent writes its own logs

**Volume Mount Strategy:**

**Decision: Use Option B (Explicit Directory Mounting) with Configuration-Driven Approach**

- **Explicitly mount each log directory** for better security and control
- **Configuration-driven**: Use a config file to list all log directories
- **Semi-automated**: When adding a module, update the config file; Promtail and docker-compose read from config
- **Low cost**: Simple config file + script to generate docker-compose volumes
- **Production-ready**: Same approach works for development and production

**Configuration-Driven Architecture:**

1. **Config File**: `_dev/monitoring/log-sources.yml` - Lists all log directories
2. **Promtail Config**: Reads from log-sources.yml to know which files to tail
3. **Docker Compose**: Uses environment variables or script to generate volume mounts from config
4. **Update Process**: When adding a module, update log-sources.yml; restart monitoring stack

**Benefits:**
- **Explicit control**: Know exactly which directories are mounted
- **Security**: No accidental access to unintended directories
- **Maintainable**: Single source of truth (config file)
- **Automated**: Scripts can generate docker-compose volumes from config
- **Scalable**: Easy to add new modules by updating config

**Architecture:**

```
Host Filesystem:
  _dev/
    ├── stock-miniapp/logs/
    │   ├── data-store.log
    │   ├── orchestrator.log
    │   ├── prompt-manager.log
    │   └── ...
    ├── prompt-manager/logs/ (if exists)
    │   └── prompt_manager.log
    ├── data-store/logs/ (if exists)
    └── ... (other module log directories)

Docker Containers (docker-compose.yml):
  ├── Prometheus (port 9090)
  ├── Grafana (port 3001)
  ├── Loki (port 3100) ← NEW
  └── Promtail ← NEW
      └── Volume mounts:
          ├── /host-dev/stock-miniapp/logs → _dev/stock-miniapp/logs/
          ├── /host-dev/prompt-manager/logs → _dev/prompt-manager/logs/ (if exists)
          ├── /host-dev/data-store/logs → _dev/data-store/logs/ (if exists)
          └── ... (other module log directories)
          └── Reads all log files and ships to Loki
```

**Why This Approach:**

1. **Consistency**: All monitoring tools (Prometheus, Grafana, Loki, Promtail) in one docker-compose file
2. **Isolation**: Monitoring stack separate from application services
3. **Easy Management**: Start/stop all monitoring with `docker-compose up/down`
4. **Host Access**: Promtail container can access host log files via volume mount
5. **Scalability**: Easy to add more log sources later (other mini-apps, different directories)

**Alternative Consideration:**

- **Promtail as Local Process**: Could run Promtail locally instead of Docker, but this would:
  - Require installing Promtail binary on host
  - Mix deployment methods (some tools in Docker, some local)
  - Make it harder to manage and version
  - **Recommendation**: Keep Promtail in Docker for consistency

**Configuration Files Needed:**

1. **docker-compose.yml**: Add Loki and Promtail services (with volume mounts from config)
2. **log-sources.yml**: Configuration file listing all log directories and their labels
3. **loki-config.yml**: Loki configuration (storage, retention, etc.)
4. **promtail-config.yml**: Promtail configuration (reads from log-sources.yml, which files to tail, labels to extract)
5. **Grafana datasource**: Add Loki as datasource in Grafana provisioning
6. **generate-volumes.sh** (optional): Script to generate docker-compose volume mounts from log-sources.yml

**Example log-sources.yml Structure:**

```yaml
log_sources:
  - name: stock-miniapp
    path: ../stock-miniapp/logs
    labels:
      miniapp: stock-miniapp
      environment: development
    patterns:
      - "*.log"
  
  - name: prompt-manager
    path: ../prompt-manager/logs
    labels:
      module: prompt-manager
      environment: development
    patterns:
      - "*.log"
      - "prompt_manager*.log"
  
  - name: data-store
    path: ../data-store/logs
    labels:
      module: data-store
      environment: development
    patterns:
      - "*.log"
  
  # Add new modules here when needed
```

**Semi-Automation Approach:**

1. **Config File**: Maintain `log-sources.yml` with all log directories
2. **Promtail Config**: Use Promtail's file discovery to read from mounted directories (configured via log-sources.yml)
3. **Docker Compose**: 
   - Option A: Manually list volumes (simple, explicit)
   - Option B: Use script to generate volume mounts from log-sources.yml (more automated)
4. **Update Process**: 
   - Add new entry to `log-sources.yml`
   - Update docker-compose.yml volumes (or run script to regenerate)
   - Restart monitoring stack

**Script Example (generate-volumes.sh):**

```bash
#!/bin/bash
# Reads log-sources.yml and generates docker-compose volume mount entries
# Output can be pasted into docker-compose.yml or used to generate it dynamically
```

This approach provides explicit control while keeping configuration manageable and semi-automated.

---

## Implementation Steps

The implementation should proceed in the following order, with each step building on the previous:

### Step 1: Create Mini-App Log Sources Configuration

1. **Create `log-sources.yml`** in each mini-app directory (e.g., `_dev/stock-miniapp/log-sources.yml`):
   - Mini-app knows which modules it uses and where their logs are written
   - List all log directories that this mini-app needs to collect
   - Include path (relative to mini-app directory or absolute), labels, and file patterns
   - **Critical**: Include `miniapp` label in each entry to distinguish logs when multiple mini-apps share the same module
   - Example structure (see document above for full example)
   - Start with: `logs/` (relative to mini-app directory) for services started by mini-app
   - Add individual module log directories as needed (e.g., `../data-store/logs/`, `../prompt-manager/logs/`)

2. **Labeling Strategy for Shared Modules**:
   - When multiple mini-apps use the same module (e.g., `data-store`), ensure proper labeling:
     - Each log source must have `miniapp: <miniapp-name>` label
     - Module logs should have both `module: <module-name>` and `miniapp: <miniapp-name>` labels
     - This allows filtering: `{module="data-store", miniapp="stock-miniapp"}` vs `{module="data-store", miniapp="other-miniapp"}`
   - Example:
     ```yaml
     log_sources:
       - name: data-store
         path: ../data-store/logs
         labels:
           miniapp: stock-miniapp  # Critical: identifies which mini-app
           module: data-store
           environment: development
     ```

3. **Path Resolution**:
   - Use relative paths from mini-app directory (e.g., `logs/`, `../data-store/logs/`)
   - Generation scripts will resolve these to absolute paths for docker-compose
   - Or use absolute paths directly in config (simpler but less portable)

### Step 2: Create Configuration Generation Scripts

1. **Create `generate-promtail-config.sh`** in `_dev/monitoring/`:
   - **Aggregates** log sources from all mini-apps
   - Reads `config.yml` to get list of mini-apps (same config used by monitoring service)
   - Reads `log-sources.yml` from each mini-app directory (e.g., `_dev/stock-miniapp/log-sources.yml`)
   - Converts to Promtail's native YAML format (`promtail-config.yml`)
   - Promtail uses `static_configs` or `file_sd_configs` format, not custom YAML
   - Script should:
     - Read `config.yml` to get list of mini-apps (same as monitoring service uses)
     - For each mini-app, read its `log-sources.yml` file
     - Parse each log-sources.yml (use `yq` or Python with `pyyaml`)
     - Merge all log sources into a single Promtail config
     - Generate Promtail `scrape_configs` with `static_configs` entries
     - Resolve relative paths to absolute paths (relative to mini-app directory, then to monitoring directory)
     - Map labels from log-sources.yml to Promtail labels (preserve all labels including `miniapp`)
     - Output valid `promtail-config.yml` in `_dev/monitoring/`

2. **Create `generate-volumes.sh`** in `_dev/monitoring/` (optional but recommended):
   - **Aggregates** volume mounts from all mini-app log sources
   - Reads `config.yml` to get list of mini-apps
   - Reads `log-sources.yml` from each mini-app
   - Generates docker-compose volume mount entries
   - Output format: `- /absolute/path/to/host/logs:/container/path/to/logs:ro` (read-only)
   - Can output to stdout (paste into docker-compose.yml) or directly update docker-compose.yml
   - Resolves relative paths to absolute paths relative to docker-compose.yml location
   - **Important**: Ensures unique mount paths when multiple mini-apps reference the same module (use labels to distinguish)

3. **Make scripts executable**: `chmod +x generate-*.sh`

### Step 3: Create Loki Configuration

1. **Create `loki-config.yml`** in `_dev/monitoring/`:
   - Storage configuration (filesystem for development, can be S3/GCS for production)
   - Retention policies (e.g., 30 days)
   - Schema configuration
   - Limits (ingestion rate, query limits)
   - Standard Loki configuration format

### Step 4: Generate Promtail Configuration

1. **Run generation script**: `cd _dev/monitoring && ./generate-promtail-config.sh`
   - This creates `promtail-config.yml` by aggregating all mini-app `log-sources.yml` files
   - Verify output is valid YAML
   - Check that all log directories from all mini-apps are included
   - Verify labels are correctly mapped (especially `miniapp` labels for shared modules)

2. **Manual verification**: Review `promtail-config.yml` to ensure:
   - All log sources from all mini-app configs are included
   - Paths are correctly resolved (absolute or relative to Promtail container)
   - Labels match the intended structure (miniapp, service, module, environment, etc.)
   - **Critical**: When same module is used by multiple mini-apps, verify each has unique `miniapp` label

### Step 5: Update Docker Compose

1. **Add Loki service** to `_dev/monitoring/docker-compose.yml`:
   - Image: `grafana/loki:latest`
   - Port: `3100:3100`
   - Volume: Mount `loki-config.yml` to `/etc/loki/local-config.yaml`
   - Volume: Create `loki-data` volume for storage
   - Network: `monitoring` network
   - Depends on: None (Loki is independent)

2. **Add Promtail service** to `_dev/monitoring/docker-compose.yml`:
   - Image: `grafana/promtail:latest`
   - No ports needed (Promtail pushes to Loki, doesn't expose HTTP)
   - Volume: Mount `promtail-config.yml` to `/etc/promtail/config.yml`
   - Volumes: Mount all log directories from all mini-app `log-sources.yml` files (use script output or manual)
   - Network: `monitoring` network
   - Depends on: `loki` (should start after Loki is ready)

3. **Volume Mounts**:
   - Option A: Manually add volume mounts from `generate-volumes.sh` output
   - Option B: Use docker-compose environment variable substitution (if supported)
   - Format: `- /absolute/path/to/host/logs:/container/path/to/logs:ro`
   - Use `:ro` (read-only) for security
   - Mount paths should match what's in `promtail-config.yml`

4. **Update Grafana service** (if needed):
   - Ensure Grafana can reach Loki on `monitoring` network
   - No additional volumes needed (Loki datasource configured via provisioning)

### Step 6: Configure Grafana Datasource

1. **Create/Update** `_dev/monitoring/grafana/provisioning/datasources/loki.yml`:
   - Add Loki datasource configuration
   - URL: `http://loki:3100` (internal Docker network name)
   - Type: `loki`
   - Access: `proxy`
   - Set as default or secondary datasource (Prometheus is primary for metrics)

2. **Verify datasource**:
   - After starting services, check Grafana UI → Configuration → Data Sources
   - Loki should appear and be accessible
   - Test connection from Grafana UI

### Step 7: Update Start Scripts (Optional Enhancement)

1. **Update `start-monitoring.sh`** (or create if doesn't exist):
   - Run `generate-promtail-config.sh` before starting docker-compose
   - Verify config files exist before starting
   - Add health check for Loki (wait for Loki to be ready before starting Promtail)

2. **Add validation**:
   - Check that all log directories from all mini-app `log-sources.yml` files exist
   - Warn if directories are missing (but don't fail - they might be created later)
   - Verify that `miniapp` labels are present in all log sources

### Step 8: Test and Verify

1. **Start monitoring stack**:
   ```bash
   cd _dev/monitoring
   ./generate-promtail-config.sh  # Generate config
   docker-compose up -d
   ```

2. **Verify services**:
   - Check Loki: `curl http://localhost:3100/ready`
   - Check Promtail logs: `docker-compose logs promtail`
   - Check Loki is receiving logs: `curl http://localhost:3100/loki/api/v1/labels`

3. **Verify in Grafana**:
   - Open Grafana: `http://localhost:3001`
   - Go to Explore → Select Loki datasource
   - Query logs: `{job="stock-miniapp"}` or `{module="data-store"}`
   - Verify logs are appearing

4. **Test log correlation**:
   - Create a Grafana dashboard with both metrics (Prometheus) and logs (Loki)
   - Verify you can correlate log events with metric spikes
   - Test filtering by service, log level, time range

### Step 9: Create Log Dashboards (Optional)

1. **Create log visualization panels** in Grafana:
   - Logs panel showing recent log entries
   - Logs panel filtered by service
   - Logs panel filtered by log level (ERROR, WARNING, etc.)
   - Time-series of log volume per service

2. **Add to existing dashboards**:
   - Add log panels alongside metric panels
   - Enable correlation between metrics and logs

### Step 10: Documentation and Maintenance

1. **Document the update process**:
   - How to add a new module to mini-app's `log-sources.yml`
   - How to add a new mini-app (create its `log-sources.yml`, regenerate Promtail config)
   - How to regenerate Promtail config (aggregates from all mini-apps)
   - How to update docker-compose volumes
   - How to restart monitoring stack

2. **Add to README**:
   - Update `_dev/monitoring/README.md` with Loki/Promtail information
   - Document log-sources.yml format
   - Document how to query logs in Grafana

**Technical Notes for Implementor:**

- **Promtail Config Format**: Promtail uses YAML with `scrape_configs` containing `static_configs` or `file_sd_configs`. Each config has:
  - `targets`: List of file paths
  - `labels`: Key-value pairs for filtering
  - `job_name`: Identifier for the scrape config
  
- **Path Resolution**: When mounting volumes in Docker, use absolute paths or paths relative to docker-compose.yml location. The generation script should resolve `log-sources.yml` relative paths to appropriate paths for Docker.

- **Label Extraction**: Promtail can extract labels from:
  - File path (using regex)
  - Log content (using regex or JSON parsing)
  - Static labels from config
  
- **Log Rotation**: Promtail handles log rotation automatically - no special configuration needed for rotated files.

- **Performance**: For development, filesystem storage for Loki is sufficient. For production, consider object storage (S3, GCS) for scalability.

**Dependencies:**
- `yq` (YAML processor) or Python with `pyyaml` for parsing log-sources.yml
- Docker and docker-compose
- Access to log directories on host filesystem

**Architecture Consistency:**
- Mini-apps own their `log-sources.yml` configuration (similar to `monitoring_config.yaml`)
- Monitoring service aggregates log sources from all mini-apps (similar to how it aggregates service targets)
- Proper labeling ensures logs from shared modules can be distinguished by mini-app

---

## Production Deployment: Distributed Architecture

This section outlines the architecture for production environments where modules may be distributed across multiple machines or containers.

### Overview

In production, the single-host volume mount approach won't work if:
- Modules run on different machines/containers
- Services are deployed in Kubernetes/ECS clusters
- Logs are written to CloudWatch, syslog, or other centralized systems
- High availability and scalability are required

### Architecture Components

**1. Mini-App Log Sources Endpoint (`/monitoring/log-sources`)**

Similar to the existing `/monitoring/targets` endpoint for metrics, mini-apps should expose a log sources endpoint:

- **Endpoint**: `GET /monitoring/log-sources`
- **Purpose**: Returns log source configuration in a standardized format
- **Format**: JSON array of log source definitions
- **Example Response**:
  ```json
  [
    {
      "name": "data-store",
      "type": "file",  // or "cloudwatch", "syslog", etc.
      "path": "/var/log/data-store/data-store.log",
      "labels": {
        "miniapp": "stock-miniapp",
        "module": "data-store",
        "environment": "production"
      },
      "patterns": ["*.log"]
    },
    {
      "name": "orchestrator",
      "type": "file",
      "path": "/var/log/stock-miniapp/orchestrator.log",
      "labels": {
        "miniapp": "stock-miniapp",
        "service": "orchestrator",
        "environment": "production"
      }
    }
  ]
  ```

**Implementation:**
- Add endpoint to orchestrator service (similar to `/monitoring/targets`)
- Use monitoring library to read from `log-sources.yml` and format response
- Monitoring service polls this endpoint (similar to service discovery polling)
- Aggregates log sources from all mini-apps

**2. Distributed Log Collection Strategies**

When modules are distributed across machines, several approaches are possible:

**Option A: Promtail per Host (Recommended for Kubernetes/ECS)**

- **Architecture**: Run one Promtail instance per host/node
- **How it works**:
  - Each host runs Promtail as a DaemonSet (Kubernetes) or sidecar (ECS)
  - Promtail collects logs from that host's filesystem/containers
  - All Promtail instances send logs to centralized Loki
  - Labels include host/node information for filtering
- **Best Practice**: Standard approach for Kubernetes (Promtail DaemonSet)
- **Pros**: 
  - Scales automatically with cluster size
  - Handles container logs natively
  - No single point of failure
- **Cons**: 
  - Requires Promtail on every host
  - More complex configuration management

**Option B: Centralized Log Forwarding Service**

- **Architecture**: Modules forward logs to a central logging service, Promtail reads from there
- **How it works**:
  - Modules send logs via syslog, HTTP, or logging library to central service
  - Central service aggregates and stores logs (e.g., Fluentd, Logstash, or custom service)
  - Promtail reads from central service's output (files, queue, or API)
  - Single Promtail instance (or small cluster) ships to Loki
- **Best Practice**: Common in traditional server environments
- **Pros**:
  - Centralized control
  - Can buffer/queue logs
  - Single Promtail configuration
- **Cons**:
  - Central service becomes bottleneck
  - Network dependency for log delivery
  - Potential log loss if central service fails

**Option C: CloudWatch Logs / Managed Log Services**

- **Architecture**: Use AWS CloudWatch Logs (or equivalent) as intermediate storage
- **How it works**:
  - Modules write to CloudWatch Logs (via agent or SDK)
  - Promtail CloudWatch plugin reads from CloudWatch Logs
  - Promtail forwards to Loki
- **Best Practice**: Standard for AWS-native deployments
- **Pros**:
  - Managed service (no infrastructure to maintain)
  - Built-in retention and archiving
  - Integrates with AWS services
- **Cons**:
  - Vendor lock-in
  - Additional cost
  - Requires Promtail CloudWatch plugin configuration

**Option D: Shared Storage (NFS/S3)**

- **Architecture**: All modules write logs to shared storage, Promtail reads from there
- **How it works**:
  - Modules write logs to NFS mount or S3 bucket
  - Single Promtail instance (or cluster) reads from shared storage
  - Promtail ships to Loki
- **Best Practice**: Works for small to medium deployments
- **Pros**:
  - Simple architecture
  - Single Promtail configuration
  - Logs persist even if modules fail
- **Cons**:
  - Shared storage becomes bottleneck
  - Network latency for log writes
  - Requires shared storage infrastructure

### Recommended Approach for AWS Production

**Hybrid Strategy:**

1. **For Containerized Services (ECS/EKS)**:
   - Use **Option A**: Promtail DaemonSet/sidecar per node
   - Collect container logs from Docker/containerd
   - Labels include: `miniapp`, `module`, `service`, `node`, `pod`, `namespace`

2. **For Traditional Services (EC2)**:
   - Use **Option C**: CloudWatch Logs
   - Install CloudWatch Logs agent on EC2 instances
   - Promtail reads from CloudWatch Logs via plugin
   - Labels include: `miniapp`, `module`, `service`, `instance_id`, `environment`

3. **Monitoring Service Integration**:
   - Monitoring service polls `/monitoring/log-sources` from all mini-apps
   - Aggregates log source definitions
   - Generates Promtail configuration dynamically (or provides API for Promtail to discover sources)
   - Handles different log source types (file, cloudwatch, syslog)

### Implementation Considerations

**Log Source Types:**
- `file`: Local filesystem (development, single-host)
- `cloudwatch`: AWS CloudWatch Logs (production AWS)
- `syslog`: Syslog forwarding (traditional infrastructure)
- `docker`: Docker container logs (containerized environments)
- `kubernetes`: Kubernetes pod logs (Kubernetes clusters)

**Label Strategy:**
- Always include `miniapp` label (critical for multi-miniapp environments)
- Include `module`, `service`, `environment` labels
- Add infrastructure labels: `host`, `node`, `pod`, `instance_id`, `region`, `availability_zone`
- Use consistent label names across all log sources for effective filtering

**Configuration Management:**
- Mini-apps define log sources in `log-sources.yml` (development) or via `/monitoring/log-sources` endpoint (production)
- Monitoring service aggregates and provides unified view
- Promtail configuration can be:
  - Static (generated from aggregated sources)
  - Dynamic (Promtail queries monitoring service for log source discovery)

**Migration Path:**
1. Start with single-host development setup (current implementation)
2. Add `/monitoring/log-sources` endpoint to mini-apps
3. Update monitoring service to poll log sources (similar to service targets)
4. For production, choose appropriate distributed collection strategy based on deployment model
5. Update Promtail configuration to use distributed log sources

This architecture maintains consistency with the existing monitoring design while supporting production scalability and distribution requirements.

