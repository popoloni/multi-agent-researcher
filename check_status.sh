#!/bin/bash

echo "Multi-Agent Researcher - Service Status Check"
echo "=============================================="
echo ""

# Configuration
OLLAMA_PORT=11434
API_PORT=12000
FRONTEND_PORT=12001

# Check Ollama
echo "🤖 Ollama Service:"
if curl -s http://localhost:$OLLAMA_PORT/api/version > /dev/null 2>&1; then
    echo "   ✅ Status: Running"
    echo "   📍 URL: http://localhost:$OLLAMA_PORT"
    OLLAMA_VERSION=$(curl -s http://localhost:$OLLAMA_PORT/api/version | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    echo "   📊 Version: $OLLAMA_VERSION"
    
    # Check if model is available
    if ollama list 2>/dev/null | grep -q "llama3.2:1b"; then
        echo "   🧠 Model: llama3.2:1b available"
    else
        echo "   ⚠️  Model: llama3.2:1b not found"
    fi
else
    echo "   ❌ Status: Not running"
    echo "   💡 Start with: ./start_dev.sh"
fi

echo ""

# Check Backend API
echo "🔧 Backend API:"
if curl -s http://localhost:$API_PORT/health > /dev/null 2>&1; then
    echo "   ✅ Status: Running"
    echo "   📍 URL: http://localhost:$API_PORT"
    echo "   📚 Docs: http://localhost:$API_PORT/docs"
    
    # Check API health details
    HEALTH_RESPONSE=$(curl -s http://localhost:$API_PORT/health)
    echo "   💓 Health: $HEALTH_RESPONSE"
    
    # Check if .env file exists
    if [ -f .env ]; then
        echo "   📝 Config: .env file present"
    else
        echo "   ⚠️  Config: .env file missing"
    fi
else
    echo "   ❌ Status: Not running"
    echo "   💡 Start with: ./start_dev.sh"
fi

echo ""

# Check Frontend
echo "🌐 Frontend UI:"
if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
    echo "   ✅ Status: Running"
    echo "   📍 URL: http://localhost:$FRONTEND_PORT"
    
    # Check if proxy is correctly configured
    if grep -q "\"proxy\": \"http://localhost:$API_PORT\"" frontend/package.json; then
        echo "   🔄 API Proxy: Correctly configured"
    else
        echo "   ⚠️  API Proxy: May be misconfigured"
    fi
else
    echo "   ❌ Status: Not running"
    echo "   💡 Start with: ./start_ui.sh"
fi

echo ""

# Check repositories
echo "📁 Repository Status:"
if curl -s http://localhost:$API_PORT/health > /dev/null 2>&1; then
    REPO_COUNT=$(curl -s http://localhost:$API_PORT/kenobi/repositories | jq -r '.total_repositories' 2>/dev/null || echo "unknown")
    echo "   📊 Indexed repositories: $REPO_COUNT"
    
    # If repositories exist, show them
    if [ "$REPO_COUNT" != "unknown" ] && [ "$REPO_COUNT" -gt 0 ]; then
        echo "   📋 Repository list:"
        curl -s http://localhost:$API_PORT/kenobi/repositories | jq -r '.repositories[] | "      - " + .name + " (" + .id + ")"' 2>/dev/null
    fi
else
    echo "   ❌ Cannot check - API not running"
fi

echo ""

# System resources
echo "💻 System Resources:"
echo "   🧠 Memory usage:"
free -h | grep -E "Mem|Swap" | sed 's/^/      /'

echo "   💾 Disk usage:"
df -h / | tail -1 | awk '{print "      Root: " $3 " used / " $2 " total (" $5 " full)"}'

echo ""

# Process information
echo "🔍 Process Information:"
OLLAMA_PID=$(pgrep -f "ollama serve" | head -1)
API_PID=$(pgrep -f "uvicorn.*main:app" | head -1)
FRONTEND_PID=$(pgrep -f "PORT=$FRONTEND_PORT npm start" | head -1)

if [ ! -z "$OLLAMA_PID" ]; then
    echo "   🤖 Ollama PID: $OLLAMA_PID"
fi

if [ ! -z "$API_PID" ]; then
    echo "   🔧 API PID: $API_PID"
fi

if [ ! -z "$FRONTEND_PID" ]; then
    echo "   🌐 Frontend PID: $FRONTEND_PID"
fi

echo ""

# Log files
echo "📋 Log Files:"
echo "   Backend: server.log"
echo "   Ollama: ollama.log"
echo "   Frontend: frontend.log"

echo ""

# Quick actions
echo "🚀 Quick Actions:"
echo "   Start all: ./start_all.sh"
echo "   Stop all: ./start_all.sh stop"
echo "   Restart all: ./start_all.sh restart"
echo "   Check status: ./start_all.sh status"
echo "   View logs: tail -f server.log ollama.log frontend.log"