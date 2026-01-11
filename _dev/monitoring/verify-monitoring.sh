#!/bin/bash

# Comprehensive Monitoring Stack Verification Script
# Verifies health, datasources, dashboards, and log ingestion

# We don't use set -e because we want to see all results, 
# but we will track if any step failed to exit with non-zero at the end.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-admin}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FAILED=0

echo "=================================================================================="
echo "                  MONITORING STACK VERIFICATION"
echo "=================================================================================="
echo ""

# --- Helpers ---
check_step() {
  local name="$1"
  local cmd="$2"
  echo -n "Checking $name... "
  # Retry up to 3 times for network-related checks
  local max_retries=3
  local count=0
  local success=0
  
  while [ $count -lt $max_retries ]; do
    if eval "$cmd" > /dev/null 2>&1; then
      success=1
      break
    fi
    count=$((count + 1))
    [ $count -lt $max_retries ] && sleep 1
  done

  if [ $success -eq 1 ]; then
    echo -e "${GREEN}✓ OK${NC}"
    return 0
  else
    echo -e "${RED}✗ FAILED${NC}"
    FAILED=1
    return 1
  fi
}

# 1. Docker Containers
echo -e "${BLUE}1. Container Status${NC}"
check_step "Grafana container" "docker ps --format '{{.Names}}' | grep -q trainer_monitoring_grafana"
check_step "Loki container" "docker ps --format '{{.Names}}' | grep -q trainer_monitoring_loki"
check_step "Prometheus container" "docker ps --format '{{.Names}}' | grep -q trainer_monitoring_prometheus"
check_step "Promtail container" "docker ps --format '{{.Names}}' | grep -q trainer_monitoring_promtail"
echo ""

# 2. Service Health
echo -e "${BLUE}2. Service Health Endpoints${NC}"
check_step "Grafana API" "curl -s -f http://127.0.0.1:3000/api/health"
check_step "Loki readiness" "curl -s -f http://127.0.0.1:3100/ready"
check_step "Prometheus health" "curl -s -f http://127.0.0.1:9090/-/healthy"
echo ""

# 3. Datasources (UID Verification)
echo -e "${BLUE}3. Datasource UIDs${NC}"
check_step "Loki datasource (uid: loki)" "curl -s -u $GRAFANA_USER:$GRAFANA_PASSWORD http://127.0.0.1:3000/api/datasources | grep -q '\"uid\":\"loki\"'"
check_step "Prometheus datasource (uid: prometheus)" "curl -s -u $GRAFANA_USER:$GRAFANA_PASSWORD http://127.0.0.1:3000/api/datasources | grep -q '\"uid\":\"prometheus\"'"
echo ""

# 4. Dashboards
echo -e "${BLUE}4. Dashboard Provisioning${NC}"
check_step "Log Monitoring Dashboard" "curl -s -u $GRAFANA_USER:$GRAFANA_PASSWORD http://127.0.0.1:3000/api/search?query=Log%20Monitoring | grep -q 'log-monitoring'"
check_step "Data Store Dashboard" "curl -s -u $GRAFANA_USER:$GRAFANA_PASSWORD http://127.0.0.1:3000/api/search?query=Data%20Store | grep -q 'data-store'"
echo ""

# 5. Log Ingestion
echo -e "${BLUE}5. Log Ingestion into Loki${NC}"
# Wait a few seconds for ingestion if this is run right after start
sleep 5
check_step "Loki labels present" "curl -s http://127.0.0.1:3100/loki/api/v1/labels | grep -q 'miniapp'"
check_step "Recent logs found" "curl -s -G \"http://127.0.0.1:3100/loki/api/v1/query_range\" --data-urlencode \"query={miniapp=\\\"stock-miniapp\\\"}\" --data-urlencode \"limit=1\" | grep -q '\"result\":\\[{'"
echo ""

# 6. Promtail File Access
echo -e "${BLUE}6. Promtail Log Collection${NC}"
check_step "Promtail error-free" "! docker logs trainer_monitoring_promtail 2>&1 | grep -i \"error\" | grep -v \"failed to stat\" | tail -5 | grep -q \".\""
echo ""

echo "=================================================================================="
if [ $FAILED -eq 0 ]; then
  echo -e "                  ${GREEN}VERIFICATION SUCCESSFUL${NC}"
else
  echo -e "                  ${RED}VERIFICATION FAILED${NC}"
fi
echo "=================================================================================="
echo ""

exit $FAILED
