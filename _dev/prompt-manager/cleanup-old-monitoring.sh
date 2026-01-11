#!/bin/bash
# Cleanup script for old prompt-manager monitoring containers

echo "Cleaning up old prompt-manager monitoring containers..."

# Stop and remove old containers
docker stop prompt_manager_grafana prompt_manager_prometheus 2>/dev/null
docker rm prompt_manager_grafana prompt_manager_prometheus 2>/dev/null

# Check if containers still exist
if docker ps -a | grep -q "prompt_manager"; then
    echo "Found remaining prompt_manager containers:"
    docker ps -a | grep prompt_manager
    echo ""
    echo "To remove them, run:"
    echo "  docker stop <container_name> && docker rm <container_name>"
else
    echo "✓ All old prompt_manager containers cleaned up"
fi

echo ""
echo "Note: The new centralized monitoring is in _dev/monitoring/"
echo "Access Grafana at: http://localhost:3000 (not 3001)"

