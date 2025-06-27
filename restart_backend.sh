#!/bin/bash

echo "Restarting Multi-Agent Researcher backend services..."

# Stop existing services
echo "Stopping existing services..."
pkill -f "uvicorn.*main:app"
pkill -f ollama

# Wait for processes to terminate
sleep 3

# Start Ollama service
echo "Starting Ollama service..."
ollama serve > ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama to start
echo "Waiting for Ollama to initialize..."
sleep 5

# Verify Ollama is running and pull model if needed
echo "Ensuring llama3.2:1b model is available..."
if ! ollama list | grep -q "llama3.2:1b"; then
    echo "Pulling llama3.2:1b model..."
    ollama pull llama3.2:1b
fi

# Start backend API
echo "Starting backend API..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload > server.log 2>&1 &
API_PID=$!

# Wait for API to start
sleep 3

# Verify services are running
echo ""
echo "Verifying services..."

if curl -s http://localhost:11434/api/version > /dev/null; then
    echo "✅ Ollama: Running (PID: $OLLAMA_PID)"
else
    echo "❌ Ollama: Failed to start"
fi

if curl -s http://localhost:12000/health > /dev/null; then
    echo "✅ Backend API: Running (PID: $API_PID)"
else
    echo "❌ Backend API: Failed to start"
fi

echo ""
echo "Backend services restarted."
echo "- Ollama logs: tail -f ollama.log"
echo "- API logs: tail -f server.log"
echo "- API URL: http://localhost:12000"