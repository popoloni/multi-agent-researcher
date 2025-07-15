#!/bin/bash
set -e  # Exit on any error

echo "🚀 Multi-Agent Researcher Control Script"

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if we're on a supported platform
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    echo "⚠️  Windows detected. For better Windows support, use:"
    echo "   start_all.bat or python start_all.py"
    echo ""
fi

# Function to check dependencies
check_dependencies() {
    local missing_deps=()
    
    # Check for required commands
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    if ! command -v ollama &> /dev/null; then
        missing_deps+=("ollama")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo "❌ Missing dependencies: ${missing_deps[*]}"
        echo "   Please install the missing dependencies and try again."
        echo ""
        echo "   Installation guides:"
        echo "   - Python: https://www.python.org/downloads/"
        echo "   - Node.js/npm: https://nodejs.org/"
        echo "   - Ollama: https://ollama.ai/"
        echo "   - curl: Usually pre-installed on most systems"
        return 1
    fi
    
    return 0
}

# Configuration
OLLAMA_PORT=11434
API_PORT=12000
FRONTEND_PORT=12001

# Function to check and pull missing models
check_models() {
    if [ ! -f .env ]; then
        echo "⚠️  No .env file found. Creating default configuration..."
        return 0
    fi
    
    echo "🔄 Checking configured models..."
    MODELS=$(grep -E "(LEAD_AGENT_MODEL|SUBAGENT_MODEL|CITATION_MODEL|KENOBI_CHAT_MODEL|DOCUMENTATION_MODEL)" .env | grep -v "^#" | cut -d'=' -f2 | sort -u)
    AVAILABLE_MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' || echo "")
    
    MISSING_MODELS=""
    AVAILABLE_COUNT=0
    
    for MODEL in $MODELS; do
        if [ ! -z "$MODEL" ]; then
            if echo "$AVAILABLE_MODELS" | grep -q "^$MODEL$"; then
                AVAILABLE_COUNT=$((AVAILABLE_COUNT + 1))
            else
                MISSING_MODELS="$MISSING_MODELS $MODEL"
            fi
        fi
    done
    
    if [ ! -z "$MISSING_MODELS" ]; then
        echo "📦 Missing models detected:$MISSING_MODELS"
        echo "   Run with 'pull-models' to download them:"
        echo "   ./utils/start_all.sh pull-models"
        echo ""
        return 1
    fi
    
    echo "✅ All $AVAILABLE_COUNT configured models are available"
    return 0
}

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
        pkill -f ollama 2>/dev/null || true
        sleep 1
        # Check if Ollama is still running (it might be a system service)
        if check_service "Ollama" $OLLAMA_PORT "api/version"; then
            echo "  ℹ️  Ollama appears to be running as a system service (auto-restart enabled)"
        fi
    fi
    
    # Check if Backend API is running before trying to kill it
    if check_service "Backend API" $API_PORT "health"; then
        echo "  Stopping Backend API..."
        pkill -f uvicorn
    fi
    
    # Check if Frontend is running before trying to kill it
    if pgrep -f "npm start" > /dev/null || pgrep -f "react-scripts" > /dev/null; then
        echo "  Stopping Frontend..."
        pkill -f "npm start" 2>/dev/null || true
        pkill -f "react-scripts" 2>/dev/null || true
    fi
    
    # Wait a moment to ensure processes are terminated
    sleep 2
    
    # Verify all services are stopped
    if ! check_service "Ollama" $OLLAMA_PORT "api/version" && \
       ! check_service "Backend API" $API_PORT "health" && \
       ! pgrep -f "npm start" > /dev/null && \
       ! pgrep -f "react-scripts" > /dev/null; then
        echo "✅ All services successfully stopped"
    else
        echo "⚠️ Some services may still be running. Check status with './utils/start_all.sh status'"
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
        
        # Check if configured models are available
        if [ -f .env ]; then
            MODELS=$(grep -E "(LEAD_AGENT_MODEL|SUBAGENT_MODEL|CITATION_MODEL|KENOBI_CHAT_MODEL|DOCUMENTATION_MODEL)" .env | grep -v "^#" | cut -d'=' -f2 | sort -u)
            LOADED_MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' || echo "")
            
            echo "   Configured Models:"
            for MODEL in $MODELS; do
                if [ ! -z "$MODEL" ]; then
                    if echo "$LOADED_MODELS" | grep -q "^$MODEL$"; then
                        echo "     ✅ $MODEL (loaded)"
                    else
                        echo "     ❌ $MODEL (not loaded)"
                    fi
                fi
            done
        else
            # Fallback to default model check
            if ollama list 2>/dev/null | grep -q "llama3.2:1b"; then
                echo "   Model: llama3.2:1b (loaded)"
            else
                echo "   Model: llama3.2:1b (not loaded)"
            fi
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
    echo "  - Start all: ./utils/start_all.sh"
    echo "  - Stop all: ./utils/start_all.sh stop"
    echo "  - Check status: ./utils/start_all.sh status"
    echo "  - Restart all: ./utils/start_all.sh restart"
    echo "  - Start backend only: ./utils/start_dev.sh"
    echo "  - Start frontend only: ./utils/start_ui.sh"
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
    
    # Check dependencies first
    if ! check_dependencies; then
        echo "❌ Dependency check failed. Cannot start services."
        exit 1
    fi
    
    # Start backend and Ollama if not already running
    if ! check_service "Backend API" $API_PORT "health" || ! check_service "Ollama" $OLLAMA_PORT "api/version"; then
        echo "  Starting backend and Ollama..."
        ./utils/start_dev.sh
    else
        echo "  Backend and Ollama already running"
    fi
    
    # Start frontend if not already running
    if ! curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo "  Starting frontend..."
        ./utils/start_ui.sh
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
    pull-models)
        echo "🔄 Checking configured models..."
        if [ -f .env ]; then
            MODELS=$(grep -E "(LEAD_AGENT_MODEL|SUBAGENT_MODEL|CITATION_MODEL|KENOBI_CHAT_MODEL|DOCUMENTATION_MODEL)" .env | grep -v "^#" | cut -d'=' -f2 | sort -u)
            AVAILABLE_MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' || echo "")
            
            DOWNLOADED_COUNT=0
            SKIPPED_COUNT=0
            
            for MODEL in $MODELS; do
                if [ ! -z "$MODEL" ]; then
                    if echo "$AVAILABLE_MODELS" | grep -q "^$MODEL$"; then
                        echo "  ✅ $MODEL (already downloaded)"
                        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
                    else
                        echo "  📦 Downloading model: $MODEL"
                        ollama pull "$MODEL"
                        DOWNLOADED_COUNT=$((DOWNLOADED_COUNT + 1))
                    fi
                fi
            done
            
            echo ""
            echo "📊 Summary:"
            echo "  ✅ Already available: $SKIPPED_COUNT models"
            echo "  📦 Downloaded: $DOWNLOADED_COUNT models"
            echo "✅ All configured models are now available!"
        else
            echo "❌ No .env file found. Please create one first."
            exit 1
        fi
        exit 0
        ;;
    help|-h|--help)
        echo "🚀 Multi-Agent Researcher Control Script"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  start        Start all services (default)"
        echo "  stop         Stop all services"
        echo "  restart      Restart all services"
        echo "  status       Show status of all services"
        echo "  pull-models  Check and download missing models only"
        echo "  help         Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0           # Start all services"
        echo "  $0 status    # Check service status"
        echo "  $0 pull-models  # Download all models from .env"
        echo ""
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