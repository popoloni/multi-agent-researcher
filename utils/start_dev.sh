#!/bin/bash
echo "🚀 Starting Multi-Agent Researcher Backend & Ollama..."

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if Ollama is already running
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama is already running"
else
    echo "🔄 Starting Ollama service..."
    ollama serve > ollama.log 2>&1 &
    OLLAMA_PID=$!
    echo "✅ Ollama started with PID: $OLLAMA_PID"
    
    # Wait for Ollama to initialize
    echo "⏳ Waiting for Ollama to initialize..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
            echo "✅ Ollama is now running"
            break
        fi
        echo "  Waiting... ($i/30)"
        sleep 2
    done
fi

# Check configured models from .env file
echo "🔄 Checking configured models..."
if [ -f .env ]; then
    # Extract all model names from .env
    MODELS=$(grep -E "(LEAD_AGENT_MODEL|SUBAGENT_MODEL|CITATION_MODEL|KENOBI_CHAT_MODEL|DOCUMENTATION_MODEL)" .env | grep -v "^#" | cut -d'=' -f2 | sort -u)
    AVAILABLE_MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' || echo "")
    
    for MODEL in $MODELS; do
        if [ ! -z "$MODEL" ]; then
            if echo "$AVAILABLE_MODELS" | grep -q "^$MODEL$"; then
                echo "  ✅ $MODEL (already downloaded)"
            else
                echo "  📦 Downloading model: $MODEL"
                ollama pull "$MODEL"
            fi
        fi
    done
else
    echo "  ⚠️  .env file not found, checking default model..."
    if ollama list 2>/dev/null | grep -q "llama3.2:1b"; then
        echo "  ✅ llama3.2:1b (already downloaded)"
    else
        echo "  📦 Downloading default model: llama3.2:1b"
        ollama pull llama3.2:1b
    fi
fi

# Start backend API
echo "🔄 Starting backend API on port 12000..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload > server.log 2>&1 &
API_PID=$!

echo "✅ Services started successfully!"
echo "📊 Status:"
echo "  - Ollama: Running on port 11434 (logs: ollama.log)"
echo "  - API: Running on port 12000 (logs: server.log)"
echo "  - API URL: http://localhost:12000"
echo "  - Health Check: curl http://localhost:12000/health"
echo ""
echo "💡 To stop services: pkill -f ollama && pkill -f uvicorn"
echo "💡 To start the frontend: ./start_ui.sh"