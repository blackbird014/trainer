#!/bin/bash

# Bootstrap the monitoring stack (Loki, Promtail, Prometheus, Grafana)
# - Generates Promtail config from log-sources.yml
# - Ensures log directories/mounts exist
# - Starts docker-compose stack
# - Waits for Loki/Grafana readiness
# - Ensures datasources have stable UIDs (loki, prometheus)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-admin}"

INFO="[INFO]"
WARN="[WARN]"
ERR="[ERR ]"

echo "=========================================="
echo "Bootstrap Monitoring Stack"
echo "=========================================="

# --- helpers ---
curl_json() {
  # $1 = method, $2 = url, $3 = data (optional)
  local method="$1"; shift
  local url="$1"; shift
  local data="${1:-}"
  if [ -n "$data" ]; then
    curl -s -u "$GRAFANA_USER:$GRAFANA_PASSWORD" -H "Content-Type: application/json" -X "$method" "$url" -d "$data"
  else
    curl -s -u "$GRAFANA_USER:$GRAFANA_PASSWORD" -H "Content-Type: application/json" -X "$method" "$url"
  fi
}

ensure_docker() {
  if ! docker info >/dev/null 2>&1; then
    echo "$ERR Docker is not running. Please start Docker."
    exit 1
  fi
}

generate_promtail_config() {
  echo "$INFO Generating Promtail configuration..."
  if [ -f "$SCRIPT_DIR/generate-promtail-config.py" ]; then
    if python3 "$SCRIPT_DIR/generate-promtail-config.py"; then
      echo "$INFO Promtail configuration generated."
    else
      echo "$WARN Failed to generate Promtail config; continuing."
    fi
  else
    echo "$WARN generate-promtail-config.py not found; skipping."
  fi
}

ensure_log_directories() {
  # Parse promtail-config.yml and ensure parent directories exist
  if [ ! -f "$SCRIPT_DIR/promtail-config.yml" ]; then
    echo "$WARN promtail-config.yml not found; skipping directory check."
    return
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    echo "$WARN python3 not available; skipping directory check."
    return
  fi
  echo "$INFO Ensuring log directories exist..."
  python3 - <<'PYCODE'
import yaml
from pathlib import Path

try:
    with open("promtail-config.yml", "r") as f:
        cfg = yaml.safe_load(f) or {}
    paths = []
    for sc in cfg.get("scrape_configs", []):
        for st in sc.get("static_configs", []):
            p = st.get("labels", {}).get("__path__")
            if p:
                paths.append(p)
    seen = set()
    for p in paths:
        # take parent dir (strip glob if present)
        if "*" in p:
            parent = Path(p).parent
        else:
            parent = Path(p).parent
        if parent in seen:
            continue
        seen.add(parent)
        parent.mkdir(parents=True, exist_ok=True)
        print(f"  ensured: {parent}")
except Exception as e:
    print(f"  warning: failed to inspect directories ({e})")
PYCODE
}

start_stack() {
  echo "$INFO Starting monitoring stack (docker-compose up -d)..."
  cd "$SCRIPT_DIR"
  docker-compose up -d
}

wait_for_loki() {
  echo "$INFO Waiting for Loki (/ready)..."
  for i in {1..30}; do
    if curl -s http://localhost:3100/ready >/dev/null 2>&1; then
      echo "$INFO Loki is ready."
      return
    fi
    sleep 1
  done
  echo "$WARN Loki may not be ready yet."
}

wait_for_grafana() {
  echo "$INFO Waiting for Grafana (/api/health)..."
  for i in {1..40}; do
    if curl -s http://localhost:3000/api/health >/dev/null 2>&1; then
      echo "$INFO Grafana is reachable."
      return
    fi
    sleep 1
  done
  echo "$WARN Grafana may not be ready yet."
}

ensure_datasource() {
  # args: name uid type url isDefault jsonData_json
  local name="$1"; local uid="$2"; local dtype="$3"; local url="$4"; local isDefault="$5"; local jsonData="$6"
  local existing
  existing=$(curl -s -u "$GRAFANA_USER:$GRAFANA_PASSWORD" "http://localhost:3000/api/datasources/name/$name")
  if echo "$existing" | grep -q '"id"'; then
    local id
    id=$(echo "$existing" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || echo "")
    if [ -n "$id" ]; then
      echo "$INFO Updating datasource $name (id=$id, uid=$uid)..."
      curl_json PUT "http://localhost:3000/api/datasources/$id" "$(cat <<EOF
{"name":"$name","type":"$dtype","access":"proxy","url":"$url","isDefault":$isDefault,"editable":true,"uid":"$uid","jsonData":$jsonData}
EOF
)"
      echo ""
      return
    fi
  fi
  echo "$INFO Creating datasource $name (uid=$uid)..."
  curl_json POST "http://localhost:3000/api/datasources" "$(cat <<EOF
{"name":"$name","type":"$dtype","access":"proxy","url":"$url","isDefault":$isDefault,"editable":true,"uid":"$uid","jsonData":$jsonData}
EOF
)"
  echo ""
}

ensure_datasources() {
  echo "$INFO Ensuring Grafana datasources (uids: loki, prometheus)..."
  ensure_datasource "Loki" "loki" "loki" "http://loki:3100" false '{"maxLines":1000}'
  ensure_datasource "Prometheus" "prometheus" "prometheus" "http://prometheus:9090" true '{"timeInterval":"5s"}'
}

# --- main flow ---
ensure_docker
generate_promtail_config
ensure_log_directories
start_stack
wait_for_loki
wait_for_grafana
ensure_datasources

echo ""
echo "$INFO Monitoring stack ready."
echo "  Grafana:    http://localhost:3000 (admin/admin)"
echo "  Prometheus: http://localhost:9090"
echo "  Loki:       http://localhost:3100"
echo "  Promtail:   collecting logs per promtail-config.yml"

