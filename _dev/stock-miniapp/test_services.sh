#!/bin/bash

# Service Status Test Script
# Tests all services and ports, showing service names and status

set -e

echo "=================================================================================="
echo "                    SERVICE STATUS TEST"
echo "=================================================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Service definitions (port:name)
get_service_name() {
    case $1 in
        3000) echo "Grafana (Monitoring)" ;;
        3001) echo "Grafana/SSH (Monitoring)" ;;
        3002) echo "Orchestrator (Stock Mini-App)" ;;
        3003) echo "Web UI (Stock Mini-App)" ;;
        8000) echo "prompt-manager" ;;
        8001) echo "llm-provider" ;;
        8002) echo "prompt-security (optional)" ;;
        8003) echo "data-retriever" ;;
        8004) echo "format-converter" ;;
        8005) echo "model-trainer" ;;
        8006) echo "test-agent" ;;
        8007) echo "data-store" ;;
        8008) echo "monitoring-service" ;;
        *) echo "Unknown" ;;
    esac
}

# All ports to test
ALL_PORTS=(3000 3001 3002 3003 8000 8001 8002 8003 8004 8005 8006 8007 8008)

# Required services for prompt flow
REQUIRED_PORTS=(3002 3003 8000 8001 8003 8004 8007)

test_port() {
    local port=$1
    local name=$2
    local required=$3
    
    printf "Port %-4s %-30s " "$port" "$name"
    
    # Try health endpoint first
    response=$(curl -s -m 2 http://localhost:$port/health 2>&1)
    if echo "$response" | grep -q "healthy\|ok\|name\|service"; then
        echo -e "${GREEN}✅ RUNNING${NC}"
        echo "$response" | head -1 | sed 's/^/  → /' | cut -c1-70
        return 0
    fi
    
    # Try root endpoint
    response=$(curl -s -m 2 http://localhost:$port/ 2>&1)
    if echo "$response" | grep -q "html\|name\|service\|version"; then
        echo -e "${GREEN}✅ RUNNING${NC}"
        echo "$response" | head -1 | cut -c1-70 | sed 's/^/  → /'
        return 0
    fi
    
    if [ "$required" = "true" ]; then
        echo -e "${RED}❌ NOT RUNNING (REQUIRED)${NC}"
    else
        echo -e "${YELLOW}⚠️  NOT RUNNING (optional)${NC}"
    fi
    return 1
}

echo "=== Testing All Services ==="
echo ""

running_count=0
required_running=0
total_required=${#REQUIRED_PORTS[@]}

for port in "${ALL_PORTS[@]}"; do
    name=$(get_service_name "$port")
    required="false"
    
    # Check if this is a required port
    for req_port in "${REQUIRED_PORTS[@]}"; do
        if [ "$port" = "$req_port" ]; then
            required="true"
            break
        fi
    done
    
    if test_port "$port" "$name" "$required"; then
        running_count=$((running_count + 1))
        if [ "$required" = "true" ]; then
            required_running=$((required_running + 1))
        fi
    fi
    echo ""
done

echo "=================================================================================="
echo "                              SUMMARY"
echo "=================================================================================="
echo ""
echo "Running Services: $running_count / ${#ALL_PORTS[@]}"
echo "Required Services: $required_running / $total_required"
echo ""

if [ $required_running -eq $total_required ]; then
    echo -e "${GREEN}✅ All required services are running!${NC}"
    echo ""
    echo "Ready to test:"
    echo "  → Web UI: http://localhost:3003"
    echo "  → Orchestrator: http://localhost:3002"
    echo ""
    echo "Test the prompt flow by clicking 'Analyze' on any company row."
else
    echo -e "${RED}❌ Missing required services!${NC}"
    echo ""
    echo "Missing required services:"
    for port in "${REQUIRED_PORTS[@]}"; do
        response=$(curl -s -m 1 http://localhost:$port/health 2>&1)
        if ! echo "$response" | grep -q "healthy\|ok\|name\|service"; then
            response=$(curl -s -m 1 http://localhost:$port/ 2>&1)
            if ! echo "$response" | grep -q "html\|name\|service\|version"; then
                name=$(get_service_name "$port")
                echo "  - Port $port: $name"
            fi
        fi
    done
    echo ""
    echo "To start missing services, see README.md in each module directory."
fi

echo ""
echo "=================================================================================="
echo ""

# Optional: Test the prompt flow
if [ $required_running -eq $total_required ]; then
    echo "Testing prompt flow..."
    echo ""
    result=$(curl -s -X POST http://localhost:3003/api/prompt/run \
        -H "Content-Type: application/json" \
        -d '{"ticker":"SMR"}' 2>&1)
    
    if echo "$result" | grep -q '"success":true'; then
        echo -e "${GREEN}✅ Prompt flow test: SUCCESS${NC}"
        run_id=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('run_id', 'N/A'))" 2>/dev/null || echo "N/A")
        echo "  Run ID: $run_id"
    else
        echo -e "${YELLOW}⚠️  Prompt flow test: FAILED${NC}"
        error=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown error')[:60])" 2>/dev/null || echo "Unknown error")
        echo "  Error: $error"
    fi
    echo ""
fi

