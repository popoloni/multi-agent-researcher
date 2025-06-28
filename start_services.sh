#!/bin/bash

echo "=== Multi-Agent Researcher Service Startup Script ==="
echo "Starting backend and frontend services..."

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true

sleep 2

# Start backend
echo "Starting backend on port 12000..."
cd /workspace/multi-agent-researcher
python -m uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Test backend
if curl -s http://localhost:12000/health > /dev/null; then
    echo "✅ Backend is running on port 12000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "Starting frontend on port 12001..."
cd /workspace/multi-agent-researcher/frontend
REACT_APP_API_URL=https://work-1-ejtkhcyzotgqadin.prod-runtime.all-hands.dev \
DANGEROUSLY_DISABLE_HOST_CHECK=true \
PORT=12001 \
HOST=0.0.0.0 \
npm start > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 15

# Test frontend
if curl -s http://localhost:12001 | grep -q "Multi-Agent Researcher"; then
    echo "✅ Frontend is running on port 12001"
else
    echo "❌ Frontend failed to start"
    exit 1
fi

echo ""
echo "=== Service Status ==="
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend URL: https://work-1-ejtkhcyzotgqadin.prod-runtime.all-hands.dev"
echo "Frontend URL: https://work-2-ejtkhcyzotgqadin.prod-runtime.all-hands.dev"
echo ""
echo "=== Testing API Endpoints ==="
echo "Health check:"
curl -s http://localhost:12000/health | jq .

echo ""
echo "Repositories:"
curl -s http://localhost:12000/kenobi/repositories | jq '.total_repositories'

echo ""
echo "✅ All services are running successfully!"
echo "You can now access the application at: https://work-2-ejtkhcyzotgqadin.prod-runtime.all-hands.dev"