#!/bin/bash
# Generate docker-compose volume mounts from mini-app log-sources.yml files

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.yml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: config.yml not found at $CONFIG_FILE" >&2
    exit 1
fi

# Check if yq is available, otherwise use Python
if command -v yq >/dev/null 2>&1; then
    USE_YQ=true
else
    USE_YQ=false
fi

# Extract mini-app names from config.yml
if [ "$USE_YQ" = true ]; then
    MINIAPP_NAMES=$(yq eval '.miniapps[].name' "$CONFIG_FILE" 2>/dev/null)
else
    # Use Python to parse YAML
    MINIAPP_NAMES=$(python3 -c "
import yaml
import sys
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f) or {}
    for miniapp in config.get('miniapps', []):
        print(miniapp.get('name', ''))
" 2>/dev/null)
fi

echo "# Generated volume mounts for Promtail"
echo "# Run this script and paste output into docker-compose.yml under promtail volumes:"
echo ""

# Process each mini-app
while IFS= read -r miniapp_name; do
    [ -z "$miniapp_name" ] && continue
    
    # Try to find log-sources.yml
    LOG_SOURCES_FILE="$PROJECT_ROOT/_dev/$miniapp_name/log-sources.yml"
    if [ ! -f "$LOG_SOURCES_FILE" ]; then
        LOG_SOURCES_FILE="$PROJECT_ROOT/$miniapp_name/log-sources.yml"
    fi
    
    if [ ! -f "$LOG_SOURCES_FILE" ]; then
        echo "# Warning: log-sources.yml not found for $miniapp_name" >&2
        continue
    fi
    
    # Extract log sources
    if [ "$USE_YQ" = true ]; then
        SOURCES=$(yq eval '.log_sources[] | select(.path != null) | "\(.path)|\(.name)"' "$LOG_SOURCES_FILE" 2>/dev/null)
    else
        # Use Python to parse
        SOURCES=$(python3 -c "
import yaml
import sys
from pathlib import Path

log_sources_file = Path('$LOG_SOURCES_FILE')
miniapp_dir = log_sources_file.parent

with open(log_sources_file, 'r') as f:
    data = yaml.safe_load(f) or {}
    for source in data.get('log_sources', []):
        path = source.get('path', '')
        name = source.get('name', '')
        if path:
            # Resolve path
            if not os.path.isabs(path):
                abs_path = (miniapp_dir / path).resolve()
            else:
                abs_path = Path(path)
            print(f'{abs_path}|{name}')
" 2>/dev/null)
    fi
    
    # Generate volume mounts
    echo "# Logs from $miniapp_name"
    while IFS='|' read -r path name; do
        [ -z "$path" ] && continue
        
        # Convert to absolute path if relative
        if [[ "$path" != /* ]]; then
            # Path is relative to mini-app directory
            MINIAPP_DIR="$PROJECT_ROOT/_dev/$miniapp_name"
            if [ ! -d "$MINIAPP_DIR" ]; then
                MINIAPP_DIR="$PROJECT_ROOT/$miniapp_name"
            fi
            ABS_PATH="$(cd "$MINIAPP_DIR" && cd "$(dirname "$path")" && pwd)/$(basename "$path")"
        else
            ABS_PATH="$path"
        fi
        
        # Check if path exists (directory or file pattern)
        if [ -d "$ABS_PATH" ] || [ -f "$ABS_PATH" ] || [[ "$ABS_PATH" == *"*"* ]]; then
            # Convert to container path (remove PROJECT_ROOT/_dev prefix if present)
            CONTAINER_PATH="${ABS_PATH#$PROJECT_ROOT/}"
            CONTAINER_PATH="/host-dev/${CONTAINER_PATH#_dev/}"
            
            # If it's a directory, mount the directory
            if [ -d "$ABS_PATH" ]; then
                echo "      - $ABS_PATH:$CONTAINER_PATH:ro"
            else
                # For file patterns, mount parent directory
                PARENT_DIR="$(dirname "$ABS_PATH")"
                echo "      - $PARENT_DIR:$CONTAINER_PATH:ro"
            fi
        else
            echo "      # Warning: Path does not exist: $ABS_PATH (for $name)" >&2
        fi
    done <<< "$SOURCES"
    echo ""
    
done <<< "$MINIAPP_NAMES"

echo "# End of generated volume mounts"

