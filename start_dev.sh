#!/bin/bash

# Multi-Agent Researcher Development Startup Script
echo "🚀 Starting Multi-Agent Researcher in Development Mode..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Function to start backend
start_backend() {
    echo "🔧 Starting FastAPI backend..."
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    echo "⚛️ Starting React frontend..."
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
    
    # Set environment variable for API URL
    export REACT_APP_API_URL=http://localhost:8080
    
    # Start development server
    npm start &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start services
start_backend
sleep 3
start_frontend

echo "✅ Development environment is running:"
echo "   - Backend API: http://localhost:8080"
echo "   - Frontend UI: http://localhost:3000"
echo "   - Press Ctrl+C to stop all services"

# Wait for services
wait