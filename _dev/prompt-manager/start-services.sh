#!/bin/bash

# Start both FastAPI and Express services
# Run this script to start both services in separate terminals

echo "=========================================="
echo "Starting Prompt Manager Services"
echo "=========================================="
echo ""

# Check if Python dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI not found. Installing dependencies..."
    pip install -e ".[api]" || pip install fastapi uvicorn prometheus-client
fi

# Check if Node dependencies are installed
if [ ! -d "express-app/node_modules" ]; then
    echo "⚠️  Node dependencies not found. Installing..."
    cd express-app
    npm install
    cd ..
fi

echo "Starting FastAPI service on port 8000..."
echo "Starting Express app on port 3000..."
echo ""
echo "Terminal 1: FastAPI Service"
echo "Terminal 2: Express App"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start FastAPI in background
python api_service.py &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 2

# Start Express
cd express-app
npm start &
EXPRESS_PID=$!

# Wait for user interrupt
trap "kill $FASTAPI_PID $EXPRESS_PID 2>/dev/null; exit" INT TERM

echo "Services started!"
echo "FastAPI: http://localhost:8000"
echo "Express: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait

