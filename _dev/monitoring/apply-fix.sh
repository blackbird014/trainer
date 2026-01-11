#!/bin/bash
# Script to apply the log collection fix

echo "Applying log collection fix..."
echo ""

# Regenerate Promtail config
echo "1. Regenerating Promtail configuration..."
cd "$(dirname "$0")"
python3 generate-promtail-config.py
if [ $? -eq 0 ]; then
    echo "   ✓ Configuration generated"
else
    echo "   ⚠ Warning: Config generation had issues, but continuing..."
fi
echo ""

# Restart Promtail
echo "2. Restarting Promtail..."
docker-compose restart promtail
if [ $? -eq 0 ]; then
    echo "   ✓ Promtail restarted"
else
    echo "   ✗ Failed to restart Promtail"
    exit 1
fi
echo ""

# Wait for Promtail to start
echo "3. Waiting for Promtail to initialize..."
sleep 5

# Check Promtail logs
echo "4. Checking Promtail status..."
docker logs trainer_monitoring_promtail 2>&1 | tail -20
echo ""

# Check if Loki has labels
echo "5. Checking if Loki is receiving logs..."
LABELS=$(curl -s http://localhost:3100/loki/api/v1/labels 2>/dev/null)
if [ -n "$LABELS" ]; then
    echo "   ✓ Loki has labels:"
    echo "$LABELS" | head -10
else
    echo "   ⚠ No labels found yet (logs may need time to appear)"
fi
echo ""

echo "Fix applied! Check Grafana at http://localhost:3000"
echo "Logs should appear within a few seconds of activity."

