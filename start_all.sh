#!/bin/bash
echo "🚀 Multi-Agent Researcher Control Script"

# Configuration
OLLAMA_PORT=11434
API_PORT=12000
FRONTEND_PORT=12001

# Function to check if a service is running
check_service() {
    local service_name=$1
    local port=$2
    local endpoint=$3
    
    if curl -s "http://localhost:$port/$endpoint" > /dev/null 2>&1; then
        return 0  # Service is running
    else
        return 1  # Service is not running
    fi
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping all services..."
    
    # Check if Ollama is running before trying to kill it
    if check_service "Ollama" $OLLAMA_PORT "api/version"; then
        echo "  Stopping Ollama service..."
        pkill -f ollama
    fi
    
    # Check if Backend API is running before trying to kill it
    if check_service "Backend API" $API_PORT "health"; then
        echo "  Stopping Backend API..."
        pkill -f uvicorn
    fi
    
    # Check if Frontend is running before trying to kill it
    if pgrep -f "PORT=$FRONTEND_PORT npm start" > /dev/null; then
        echo "  Stopping Frontend..."
        pkill -f "PORT=$FRONTEND_PORT npm start"
    fi
    
    # Wait a moment to ensure processes are terminated
    sleep 2
    
    # Verify all services are stopped
    if ! check_service "Ollama" $OLLAMA_PORT "api/version" && \
       ! check_service "Backend API" $API_PORT "health" && \
       ! pgrep -f "PORT=$FRONTEND_PORT npm start" > /dev/null; then
        echo "✅ All services successfully stopped"
    else
        echo "⚠️ Some services may still be running. Check status with './start_all.sh status'"
    fi
}

# Function to display status
show_status() {
    echo ""
    echo "📊 Multi-Agent Researcher Status:"
    echo "=================================="
    
    # Check Ollama
    if check_service "Ollama" $OLLAMA_PORT "api/version"; then
        echo "✅ Ollama: Running on port $OLLAMA_PORT"
        OLLAMA_VERSION=$(curl -s http://localhost:$OLLAMA_PORT/api/version | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
        echo "   Version: $OLLAMA_VERSION"
        
        # Check if model is available
        if ollama list 2>/dev/null | grep -q "llama3.2:1b"; then
            echo "   Model: llama3.2:1b (loaded)"
        else
            echo "   Model: llama3.2:1b (not loaded)"
        fi
    else
        echo "❌ Ollama: Not running"
    fi
    
    # Check Backend API
    if check_service "Backend API" $API_PORT "health"; then
        echo "✅ Backend API: Running on port $API_PORT"
        API_VERSION=$(curl -s http://localhost:$API_PORT/health | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
        echo "   Version: $API_VERSION"
        
        # Check if .env file exists
        if [ -f .env ]; then
            echo "   Config: .env file present"
        else
            echo "   Config: .env file missing"
        fi
    else
        echo "❌ Backend API: Not running"
    fi
    
    # Check Frontend
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo "✅ Frontend: Running on port $FRONTEND_PORT"
        
        # Check if proxy is correctly configured
        if grep -q "\"proxy\": \"http://localhost:$API_PORT\"" frontend/package.json; then
            echo "   Config: API proxy correctly configured"
        else
            echo "   Config: API proxy may be misconfigured"
        fi
    else
        echo "❌ Frontend: Not running"
    fi
    
    echo ""
    echo "📝 Access URLs:"
    echo "  - Backend API: http://localhost:$API_PORT"
    echo "  - Frontend UI: http://localhost:$FRONTEND_PORT"
    echo "  - API Documentation: http://localhost:$API_PORT/docs"
    echo ""
    echo "📋 Log Files:"
    echo "  - Backend: server.log"
    echo "  - Ollama: ollama.log"
    echo "  - Frontend: frontend.log"
    echo ""
    echo "💡 Commands:"
    echo "  - Start all: ./start_all.sh"
    echo "  - Stop all: ./start_all.sh stop"
    echo "  - Check status: ./start_all.sh status"
    echo "  - Restart all: ./start_all.sh restart"
    echo "  - Start backend only: ./start_dev.sh"
    echo "  - Start frontend only: ./start_ui.sh"
}

# Function to restart all services
restart_services() {
    echo "🔄 Restarting all services..."
    stop_services
    sleep 2
    start_services
}

# Function to start all services
start_services() {
    echo "🚀 Starting all services..."
    
    # Start backend and Ollama if not already running
    if ! check_service "Backend API" $API_PORT "health" || ! check_service "Ollama" $OLLAMA_PORT "api/version"; then
        echo "  Starting backend and Ollama..."
        ./start_dev.sh
    else
        echo "  Backend and Ollama already running"
    fi
    
    # Start frontend if not already running
    if ! curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo "  Starting frontend..."
        ./start_ui.sh
    else
        echo "  Frontend already running"
    fi
    
    # Show status
    show_status
    
    echo "🎉 All components started successfully!"
}

# Handle command line arguments
case "$1" in
    stop)
        stop_services
        exit 0
        ;;
    status)
        show_status
        exit 0
        ;;
    restart)
        restart_services
        exit 0
        ;;
    *)
        # Default: start all services
        start_services
        ;;
esac

# If no arguments provided, keep script running to allow easy termination
if [ -z "$1" ]; then
    echo "Press Ctrl+C to stop all services when done"
    
    # Keep script running to allow easy termination of all services
    trap stop_services INT
    while true; do
        sleep 60
    done
fi