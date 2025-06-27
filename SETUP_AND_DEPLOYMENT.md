# Multi-Agent Researcher - Setup and Deployment Guide

This comprehensive guide covers all the steps needed to set up and run the Multi-Agent Researcher system, including the backend API, frontend UI, and all additional components.

## Table of Contents

1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Component Setup](#component-setup)
5. [Running the System](#running-the-system)
6. [API Documentation](#api-documentation)
7. [Troubleshooting](#troubleshooting)
8. [Development Scripts](#development-scripts)

## System Overview

The Multi-Agent Researcher is a comprehensive code analysis and chat system that consists of:

- **Backend API**: FastAPI-based REST API for repository analysis and AI chat
- **Frontend UI**: React-based web interface for interacting with the system
- **Ollama Integration**: Local AI model for code analysis and chat
- **Repository Indexing**: Code parsing and semantic search capabilities
- **Kenobi Agent**: AI assistant for code-related questions

## Prerequisites

### System Requirements
- Python 3.8+
- Node.js 16+
- npm or yarn
- Git
- At least 8GB RAM (for Ollama models)
- 10GB+ free disk space

### Operating System Support
- Linux (Ubuntu 20.04+ recommended)
- macOS 10.15+
- Windows 10+ (with WSL2 recommended)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/popoloni/multi-agent-researcher.git
cd multi-agent-researcher
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Install Additional Dependencies

```bash
# Install spaCy language model for NLP
python -m spacy download en_core_web_sm

# Install additional packages if needed
pip install uvicorn fastapi python-multipart
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Or using yarn
yarn install
```

### 4. Ollama Installation

#### Linux/macOS
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Pull the required model
ollama pull llama3.2:1b
```

#### Windows
```bash
# Download and install from https://ollama.ai/download
# Then run in PowerShell:
ollama serve
ollama pull llama3.2:1b
```

## Component Setup

### 1. Environment Configuration

Create a `.env` file in the root directory:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=12000
DEBUG=true

# Ollama Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3.2:1b

# Database Configuration (if using)
DATABASE_URL=sqlite:///./kenobi.db

# Logging
LOG_LEVEL=INFO
```

### 2. Directory Structure

Ensure the following directory structure exists:

```
multi-agent-researcher/
├── app/                    # Backend application
│   ├── agents/            # AI agents
│   ├── engines/           # AI engines
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── main.py           # FastAPI application
├── frontend/              # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── requirements.txt       # Python dependencies
├── start_dev.sh          # Development startup script
├── start_ui.sh           # UI startup script
└── SETUP_AND_DEPLOYMENT.md
```

## Running the System

### Method 1: Using Development Scripts (Recommended)

#### Start All Services
```bash
# Make scripts executable
chmod +x start_dev.sh start_ui.sh

# Start backend and Ollama
./start_dev.sh

# In a new terminal, start frontend
./start_ui.sh
```

#### Individual Service Scripts

**Backend + Ollama (`start_dev.sh`)**:
```bash
#!/bin/bash
echo "Starting Multi-Agent Researcher Development Environment..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Start Ollama service
echo "Starting Ollama service..."
ollama serve > ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama to start
sleep 5

# Pull required model if not exists
echo "Ensuring llama3.2:1b model is available..."
ollama pull llama3.2:1b

# Start backend API
echo "Starting backend API on port 12000..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload > server.log 2>&1 &
API_PID=$!

echo "Services started:"
echo "- Ollama: PID $OLLAMA_PID (logs: ollama.log)"
echo "- API: PID $API_PID (logs: server.log)"
echo "- API URL: http://localhost:12000"
echo "- Health Check: curl http://localhost:12000/health"
echo ""
echo "To stop services: pkill -f ollama && pkill -f uvicorn"
```

**Frontend (`start_ui.sh`)**:
```bash
#!/bin/bash
echo "Starting Multi-Agent Researcher Frontend..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start development server
echo "Starting React development server on port 3000..."
npm start
```

### Method 2: Manual Startup

#### 1. Start Ollama Service
```bash
# Start Ollama in background
ollama serve > ollama.log 2>&1 &

# Verify Ollama is running
curl http://localhost:11434/api/version

# Pull the model
ollama pull llama3.2:1b
```

#### 2. Start Backend API
```bash
# From project root
python -m uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload

# Or in background
python -m uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload > server.log 2>&1 &
```

#### 3. Start Frontend
```bash
# Navigate to frontend directory
cd frontend

# Start development server
npm start

# Or using yarn
yarn start
```

### Method 3: Production Deployment

#### Backend (Production)
```bash
# Install production ASGI server
pip install gunicorn

# Start with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:12000
```

#### Frontend (Production)
```bash
cd frontend

# Build for production
npm run build

# Serve with a static server
npm install -g serve
serve -s build -l 3000
```

## API Documentation

### Health Check
```bash
curl http://localhost:12000/health
```

### Repository Management

#### Index a Repository
```bash
curl -X POST "http://localhost:12000/kenobi/repositories/index" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/repository",
    "name": "My Repository"
  }'
```

#### List Repositories
```bash
curl http://localhost:12000/kenobi/repositories
```

#### Get Repository Details
```bash
curl http://localhost:12000/kenobi/repositories/{repository_id}
```

### Chat with Kenobi

#### Send Chat Message
```bash
curl -X POST "http://localhost:12000/kenobi/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the main architecture of this project?",
    "repository_id": "your-repo-id",
    "branch": "main"
  }'
```

#### Get Chat History
```bash
curl "http://localhost:12000/kenobi/chat/history?repository_id=your-repo-id&branch=main"
```

### Code Search

#### Semantic Search
```bash
curl -X POST "http://localhost:12000/kenobi/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "authentication functions",
    "repository_id": "your-repo-id",
    "max_results": 10
  }'
```

## Service URLs

When running locally:
- **Backend API**: http://localhost:12000
- **Frontend UI**: http://localhost:3000
- **Ollama API**: http://localhost:11434
- **API Documentation**: http://localhost:12000/docs (Swagger UI)

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Restart Ollama
pkill ollama
ollama serve &

# Check logs
tail -f ollama.log
```

#### 2. Backend API Errors
```bash
# Check API health
curl http://localhost:12000/health

# Check logs
tail -f server.log

# Restart API
pkill -f uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload &
```

#### 3. Frontend Connection Issues
```bash
# Check if backend is running
curl http://localhost:12000/health

# Restart frontend
cd frontend
npm start
```

#### 4. Repository Indexing Fails
```bash
# Check repository path exists
ls -la /path/to/repository

# Check API logs for errors
tail -f server.log

# Try with a smaller repository first
```

#### 5. Memory Issues with Ollama
```bash
# Use a smaller model
ollama pull llama3.2:1b

# Check system memory
free -h

# Restart Ollama with memory limits
ollama serve --max-memory 4GB
```

### Port Conflicts

If default ports are in use:

#### Change Backend Port
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

#### Change Frontend Port
```bash
cd frontend
PORT=3001 npm start
```

#### Change Ollama Port
```bash
OLLAMA_HOST=0.0.0.0 OLLAMA_PORT=11435 ollama serve
```

### Performance Optimization

#### Backend Optimization
```bash
# Use multiple workers for production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:12000

# Increase timeout for large repositories
gunicorn app.main:app --timeout 300 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:12000
```

#### Ollama Optimization
```bash
# Use GPU acceleration (if available)
ollama serve --gpu

# Adjust model parameters
ollama run llama3.2:1b --num-ctx 4096
```

## Development Scripts

### Available Scripts

#### `start_dev.sh` - Development Environment
- Starts Ollama service
- Pulls required AI model
- Starts backend API with hot reload
- Provides service status and logs

#### `start_ui.sh` - Frontend Development
- Installs dependencies if needed
- Starts React development server
- Enables hot reload for UI changes

#### Custom Scripts

You can create additional scripts for specific needs:

**`stop_services.sh`**:
```bash
#!/bin/bash
echo "Stopping all services..."
pkill -f ollama
pkill -f uvicorn
pkill -f "npm start"
echo "All services stopped."
```

**`restart_backend.sh`**:
```bash
#!/bin/bash
echo "Restarting backend services..."
pkill -f uvicorn
pkill -f ollama
sleep 2
ollama serve > ollama.log 2>&1 &
sleep 3
python -m uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload > server.log 2>&1 &
echo "Backend restarted."
```

**`check_status.sh`**:
```bash
#!/bin/bash
echo "Service Status Check:"
echo "====================="

# Check Ollama
if curl -s http://localhost:11434/api/version > /dev/null; then
    echo "✅ Ollama: Running"
else
    echo "❌ Ollama: Not running"
fi

# Check Backend API
if curl -s http://localhost:12000/health > /dev/null; then
    echo "✅ Backend API: Running"
else
    echo "❌ Backend API: Not running"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend: Running"
else
    echo "❌ Frontend: Not running"
fi
```

## Testing the System

### 1. Basic Functionality Test
```bash
# 1. Check all services are running
./check_status.sh

# 2. Test repository indexing
curl -X POST "http://localhost:12000/kenobi/repositories/index" \
  -H "Content-Type: application/json" \
  -d '{"path": "/workspace/multi-agent-researcher", "name": "Test Repo"}'

# 3. Test chat functionality
curl -X POST "http://localhost:12000/kenobi/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What files are in this repository?", "repository_id": "your-repo-id", "branch": "main"}'
```

### 2. Frontend Test
1. Open http://localhost:3000
2. Navigate to "Repositories" page
3. Index a repository
4. Go to "Kenobi Chat" page
5. Select the repository and send a message

## Security Considerations

### Production Deployment
- Use environment variables for sensitive configuration
- Enable HTTPS for production
- Implement authentication and authorization
- Restrict API access with rate limiting
- Use secure headers and CORS policies

### Example Production Configuration
```bash
# Use environment variables
export API_HOST=0.0.0.0
export API_PORT=443
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434
export SSL_CERT_PATH=/path/to/cert.pem
export SSL_KEY_PATH=/path/to/key.pem
```

## Support and Maintenance

### Log Files
- Backend API: `server.log`
- Ollama: `ollama.log`
- Frontend: Console output

### Monitoring
```bash
# Monitor API performance
curl http://localhost:12000/metrics

# Monitor system resources
htop
df -h
```

### Updates
```bash
# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update Node.js dependencies
cd frontend && npm update

# Update Ollama models
ollama pull llama3.2:1b
```

This documentation provides a complete guide for setting up, running, and maintaining the Multi-Agent Researcher system. For additional support, refer to the project's GitHub repository or create an issue for specific problems.