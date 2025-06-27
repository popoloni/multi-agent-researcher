#!/bin/bash

echo "Stopping Multi-Agent Researcher services..."

# Stop backend API
echo "Stopping backend API..."
pkill -f "uvicorn.*main:app"

# Stop Ollama service
echo "Stopping Ollama service..."
pkill -f ollama

# Stop frontend (if running)
echo "Stopping frontend..."
pkill -f "npm start"

# Wait a moment for processes to terminate
sleep 2

echo "All services stopped."
echo ""
echo "To verify services are stopped:"
echo "- Backend API: curl http://localhost:12000/health (should fail)"
echo "- Ollama: curl http://localhost:11434/api/version (should fail)"
echo "- Frontend: http://localhost:3000 (should be unreachable)"