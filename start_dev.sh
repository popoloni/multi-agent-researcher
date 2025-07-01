#!/bin/bash
echo "🚀 Starting Multi-Agent Researcher Backend & Ollama..."

# Install Python dependencies if needed
if ! pip show fastapi uvicorn ollama spacy > /dev/null 2>&1; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    
    echo "📦 Installing spaCy language model..."
    pip install spacy
    python -m spacy download en_core_web_sm
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Check if Ollama is already running
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama is already running"
    OLLAMA_RUNNING=true
else
    echo "🔄 Starting Ollama service..."
    ollama serve > ollama.log 2>&1 &
    OLLAMA_PID=$!
    echo "✅ Ollama started with PID: $OLLAMA_PID"
    OLLAMA_RUNNING=false
    
    # Wait for Ollama to initialize
    echo "⏳ Waiting for Ollama to initialize..."
    for i in {1..10}; do
        if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
            echo "✅ Ollama is now running"
            break
        fi
        echo "  Waiting... ($i/10)"
        sleep 2
    done
fi

# Pull required model if not exists
echo "🔄 Ensuring llama3.2:1b model is available..."
ollama pull llama3.2:1b

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOL
# API Configuration
API_HOST=0.0.0.0
API_PORT=12000
DEBUG=true

# AI Provider Configuration
AI_PROVIDER=ollama  # Can be "ollama" or "anthropic"

# Ollama Configuration (default provider)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=

# Database Configuration
DATABASE_URL=sqlite:///./kenobi.db

# Logging
LOG_LEVEL=INFO
EOL
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