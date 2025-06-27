#!/bin/bash

echo "Multi-Agent Researcher - Service Status Check"
echo "=============================================="
echo ""

# Check Ollama
echo "🤖 Ollama Service:"
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "   ✅ Status: Running"
    echo "   📍 URL: http://localhost:11434"
    
    # Check if model is available
    if ollama list 2>/dev/null | grep -q "llama3.2:1b"; then
        echo "   🧠 Model: llama3.2:1b available"
    else
        echo "   ⚠️  Model: llama3.2:1b not found"
    fi
else
    echo "   ❌ Status: Not running"
    echo "   💡 Start with: ollama serve"
fi

echo ""

# Check Backend API
echo "🔧 Backend API:"
if curl -s http://localhost:12000/health > /dev/null 2>&1; then
    echo "   ✅ Status: Running"
    echo "   📍 URL: http://localhost:12000"
    echo "   📚 Docs: http://localhost:12000/docs"
    
    # Check API health details
    HEALTH_RESPONSE=$(curl -s http://localhost:12000/health)
    echo "   💓 Health: $HEALTH_RESPONSE"
else
    echo "   ❌ Status: Not running"
    echo "   💡 Start with: python -m uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload"
fi

echo ""

# Check Frontend
echo "🌐 Frontend UI:"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Status: Running"
    echo "   📍 URL: http://localhost:3000"
else
    echo "   ❌ Status: Not running"
    echo "   💡 Start with: cd frontend && npm start"
fi

echo ""

# Check repositories
echo "📁 Repository Status:"
if curl -s http://localhost:12000/health > /dev/null 2>&1; then
    REPO_COUNT=$(curl -s http://localhost:12000/kenobi/repositories | jq -r '.total_repositories' 2>/dev/null || echo "unknown")
    echo "   📊 Indexed repositories: $REPO_COUNT"
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
FRONTEND_PID=$(pgrep -f "npm start" | head -1)

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

# Quick actions
echo "🚀 Quick Actions:"
echo "   Start all: ./start_dev.sh && ./start_ui.sh"
echo "   Stop all: ./stop_services.sh"
echo "   Restart backend: ./restart_backend.sh"
echo "   View logs: tail -f server.log ollama.log"