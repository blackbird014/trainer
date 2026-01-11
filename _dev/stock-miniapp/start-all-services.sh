#!/bin/bash

# Start All Services for Stock Mini-App
# This script starts all required services without prompting
# Run this script and it will start everything in the background

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PID file to track running services
PID_FILE="$SCRIPT_DIR/.service_pids"

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping all services...${NC}"
    if [ -f "$PID_FILE" ]; then
        while read pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

trap cleanup INT TERM

# Function to wait for service to be ready
wait_for_service() {
    local port=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    echo -n "Waiting for $name (port $port)... "
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1 || \
           curl -s -f "http://localhost:$port/" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    echo -e "${RED}✗ (timeout)${NC}"
    return 1
}

# Function to start a service in background
start_service() {
    local name=$1
    local dir=$2
    local script=$3
    local port=$4
    
    echo -e "${BLUE}Starting $name...${NC}"
    cd "$dir"
    
    # Create log directory if it doesn't exist
    mkdir -p "$SCRIPT_DIR/logs"
    
    # Start service in background and capture PID
    bash "$script" > "$SCRIPT_DIR/logs/${name}.log" 2>&1 &
    local pid=$!
    echo $pid >> "$PID_FILE"
    echo "  PID: $pid"
    echo "  Log: $SCRIPT_DIR/logs/${name}.log"
    
    # Wait a moment for service to start
    sleep 2
    
    return 0
}

echo "=================================================================================="
echo "                    STARTING ALL SERVICES FOR STOCK MINI-APP"
echo "=================================================================================="
echo ""

# Step 0: Ensure log directories exist for all modules
echo -e "${BLUE}Step 0: Ensuring log directories exist...${NC}"
mkdir -p "$PROJECT_ROOT/_dev/stock-miniapp/logs"
mkdir -p "$PROJECT_ROOT/_dev/data-store/logs"
mkdir -p "$PROJECT_ROOT/_dev/data-retriever/logs"
mkdir -p "$PROJECT_ROOT/_dev/prompt-manager/logs"
mkdir -p "$PROJECT_ROOT/_dev/llm-provider/logs"
mkdir -p "$PROJECT_ROOT/_dev/format-converter/logs"
echo -e "  ${GREEN}✓ Log directories ready${NC}"
echo ""

# Step 1: Start MongoDB
echo -e "${BLUE}Step 1: Setting up MongoDB...${NC}"
cd "$PROJECT_ROOT/_dev/data-store"
if ! docker ps --format '{{.Names}}' | grep -q "^mongodb$"; then
    if docker ps -a --format '{{.Names}}' | grep -q "^mongodb$"; then
        echo "  Starting existing MongoDB container..."
        docker start mongodb > /dev/null 2>&1
    else
        echo "  Creating MongoDB container..."
        ./setup_mongodb.sh > /dev/null 2>&1
    fi
    sleep 3
fi
if docker ps --format '{{.Names}}' | grep -q "^mongodb$"; then
    echo -e "  ${GREEN}✓ MongoDB is running${NC}"
else
    echo -e "  ${RED}✗ MongoDB failed to start${NC}"
    exit 1
fi
echo ""

# Step 2: Start data-store (port 8007)
echo -e "${BLUE}Step 2: Starting data-store (port 8007)...${NC}"
start_service "data-store" "$PROJECT_ROOT/_dev/data-store" "run_api.sh" 8007
wait_for_service 8007 "data-store"
echo ""

# Step 3: Start data-retriever (port 8003)
echo -e "${BLUE}Step 3: Starting data-retriever (port 8003)...${NC}"
start_service "data-retriever" "$PROJECT_ROOT/_dev/data-retriever" "run_api.sh" 8003
wait_for_service 8003 "data-retriever"
echo ""

# Step 4: Start prompt-manager (port 8000)
echo -e "${BLUE}Step 4: Starting prompt-manager (port 8000)...${NC}"
cd "$PROJECT_ROOT/_dev/prompt-manager"
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || true
elif [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi
python api_service.py > "$SCRIPT_DIR/logs/prompt-manager.log" 2>&1 &
PROMPT_MANAGER_PID=$!
echo $PROMPT_MANAGER_PID >> "$PID_FILE"
echo "  PID: $PROMPT_MANAGER_PID"
echo "  Log: $SCRIPT_DIR/logs/prompt-manager.log"
sleep 2
wait_for_service 8000 "prompt-manager"
echo ""

# Step 5: Start llm-provider (port 8001)
echo -e "${BLUE}Step 5: Starting llm-provider (port 8001)...${NC}"
start_service "llm-provider" "$PROJECT_ROOT/_dev/llm-provider" "run_api.sh" 8001
wait_for_service 8001 "llm-provider"
echo ""

# Step 6: Start format-converter (port 8004)
echo -e "${BLUE}Step 6: Starting format-converter (port 8004)...${NC}"
cd "$PROJECT_ROOT/_dev/format-converter"
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || true
elif [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi
python api_service.py > "$SCRIPT_DIR/logs/format-converter.log" 2>&1 &
FORMAT_CONVERTER_PID=$!
echo $FORMAT_CONVERTER_PID >> "$PID_FILE"
echo "  PID: $FORMAT_CONVERTER_PID"
echo "  Log: $SCRIPT_DIR/logs/format-converter.log"
sleep 2
wait_for_service 8004 "format-converter"
echo ""

# Step 7: Start orchestrator (port 3002)
echo -e "${BLUE}Step 7: Starting orchestrator (port 3002)...${NC}"
start_service "orchestrator" "$PROJECT_ROOT/_dev/stock-miniapp/api" "run_orchestrator.sh" 3002
wait_for_service 3002 "orchestrator"
echo ""

# Step 8: Build React app if needed
echo -e "${BLUE}Step 8: Checking React build...${NC}"
cd "$PROJECT_ROOT/_dev/stock-miniapp/web/client"

NEED_REBUILD=false

# Check if build exists
if [ ! -d "build" ] || [ ! -f "build/index.html" ]; then
    NEED_REBUILD=true
    echo "  Build directory missing, will rebuild..."
elif [ "${FORCE_REBUILD:-false}" = "true" ]; then
    NEED_REBUILD=true
    echo "  FORCE_REBUILD set, will rebuild..."
else
    # Check if source files are newer than build
    BUILD_TIME=$(stat -f "%m" build/index.html 2>/dev/null || echo "0")
    SOURCE_TIME=$(find src -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.css" \) 2>/dev/null | xargs stat -f "%m" 2>/dev/null | sort -r | head -1 || echo "0")
    
    if [ "$SOURCE_TIME" -gt "$BUILD_TIME" ]; then
        NEED_REBUILD=true
        echo "  Source files newer than build, will rebuild..."
    else
        # Check if key components exist in build (safety check)
        if ! grep -r "CollectionExplorer\|View Database" build/static/js/*.js build/index.html 2>/dev/null | grep -q .; then
            NEED_REBUILD=true
            echo "  Key components missing in build, will rebuild..."
        fi
    fi
fi

if [ "$NEED_REBUILD" = "true" ]; then
    echo "  Building React app..."
    if [ ! -d "node_modules" ]; then
        echo "  Installing npm dependencies..."
        npm install > /dev/null 2>&1
    fi
    npm run build > "$SCRIPT_DIR/logs/react-build.log" 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓ React app built${NC}"
    else
        echo -e "  ${RED}✗ React build failed (check logs/react-build.log)${NC}"
    fi
else
    echo -e "  ${GREEN}✓ React build is up to date${NC}"
fi
echo ""

# Step 9: Start monitoring stack (Prometheus, Grafana, Loki, Promtail)
echo -e "${BLUE}Step 9: Starting monitoring stack (Prometheus, Grafana, Loki, Promtail)...${NC}"
cd "$PROJECT_ROOT/_dev/monitoring"
if ! docker info > /dev/null 2>&1; then
    echo -e "  ${RED}✗ Docker is not running. Skipping monitoring stack.${NC}"
    echo ""
else
    bash "$PROJECT_ROOT/_dev/monitoring/bootstrap-monitoring.sh"
fi
echo ""

# Step 10: Start monitoring service (port 8008) - Optional but recommended
echo -e "${BLUE}Step 10: Starting monitoring service (port 8008)...${NC}"
# Use orchestrator's venv (monitoring package should be installed there)
cd "$PROJECT_ROOT/_dev/stock-miniapp/api"
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || true
elif [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi
# Install monitoring package if needed (editable install)
cd "$PROJECT_ROOT/_dev/monitoring"
if ! python -c "import monitoring" 2>/dev/null; then
    echo "  Installing monitoring package..."
    pip install -e . > /dev/null 2>&1 || echo -e "  ${YELLOW}⚠ Failed to install monitoring package${NC}"
fi
python api_service.py > "$SCRIPT_DIR/logs/monitoring.log" 2>&1 &
MONITORING_PID=$!
echo $MONITORING_PID >> "$PID_FILE"
echo "  PID: $MONITORING_PID"
echo "  Log: $SCRIPT_DIR/logs/monitoring.log"
sleep 2
wait_for_service 8008 "monitoring" || echo -e "  ${YELLOW}⚠ Monitoring service started but not ready (may need more time)${NC}"
echo ""

# Step 11: Start Express web server (port 3003)
echo -e "${BLUE}Step 11: Starting Express web server (port 3003)...${NC}"
cd "$PROJECT_ROOT/_dev/stock-miniapp/web"
if [ ! -d "node_modules" ]; then
    echo "  Installing npm dependencies..."
    npm install > /dev/null 2>&1
fi
node server.js > "$SCRIPT_DIR/logs/web-server.log" 2>&1 &
WEB_SERVER_PID=$!
echo $WEB_SERVER_PID >> "$PID_FILE"
echo "  PID: $WEB_SERVER_PID"
echo "  Log: $SCRIPT_DIR/logs/web-server.log"
sleep 3
wait_for_service 3003 "web-server"
echo ""

# Step 12: Final Verification
echo -e "${BLUE}Step 12: Final Verification...${NC}"
if [ -f "$PROJECT_ROOT/_dev/monitoring/verify-monitoring.sh" ]; then
    bash "$PROJECT_ROOT/_dev/monitoring/verify-monitoring.sh"
fi
bash "$SCRIPT_DIR/test_services.sh"

echo "=================================================================================="
echo -e "                    ${GREEN}ALL SERVICES STARTED SUCCESSFULLY!${NC}"
echo "=================================================================================="
echo ""
echo "Services running:"
echo "  - MongoDB:          http://localhost:27017"
echo "  - data-store:       http://localhost:8007"
echo "  - data-retriever:   http://localhost:8003"
echo "  - prompt-manager:  http://localhost:8000"
echo "  - llm-provider:     http://localhost:8001"
echo "  - format-converter: http://localhost:8004"
echo "  - orchestrator:    http://localhost:3002"
echo "  - monitoring:       http://localhost:8008"
echo "  - Web UI:           http://localhost:3003"
echo ""
echo "Monitoring stack:"
echo "  - Prometheus:       http://localhost:9090"
echo "  - Grafana:          http://localhost:3000 (admin/admin)"
echo "  - Loki:             http://localhost:3100"
echo "  - Promtail:         (collecting logs)"
echo ""
echo -e "${YELLOW}Logs are available in: $SCRIPT_DIR/logs/${NC}"
echo -e "${YELLOW}View logs in Grafana: http://localhost:3000 → Dashboards → Log Monitoring${NC}"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running
wait

