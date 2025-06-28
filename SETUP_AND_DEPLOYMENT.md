# Multi-Agent Researcher - Streamlined Setup and Deployment Guide

This guide provides a simplified approach to setting up and running the Multi-Agent Researcher system with minimal hassle.

## Table of Contents

1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Component Details](#component-details)
5. [Troubleshooting](#troubleshooting)
6. [API Documentation](#api-documentation)

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
- npm
- Git
- At least 8GB RAM (for Ollama models)
- 10GB+ free disk space

## Quick Start

### One-Command Setup and Launch

The easiest way to get started is using our all-in-one script:

```bash
# Clone the repository if you haven't already
git clone https://github.com/popoloni/multi-agent-researcher.git
cd multi-agent-researcher

# Make scripts executable
chmod +x start_all.sh start_dev.sh start_ui.sh

# Start everything with one command
./start_all.sh
```

This script will:
1. Install all required dependencies (Python packages, Node.js modules, Ollama)
2. Configure environment settings
3. Start the backend API, Ollama service, and frontend UI
4. Show you the status and access URLs

### Accessing the System

Once started, you can access:
- **Frontend UI**: http://localhost:12001
- **Backend API**: http://localhost:12000
- **API Documentation**: http://localhost:12000/docs

### Managing the System

```bash
# Start all services
./start_all.sh

# Check system status
./start_all.sh status
# or
./check_status.sh

# Stop all services
./start_all.sh stop
# or
./stop_all.sh

# Restart all services
./start_all.sh restart

# Start only the backend and Ollama
./start_dev.sh

# Start only the frontend
./start_ui.sh
```

## Component Details

### Backend API (Port 12000)

The backend provides:
- Repository indexing and analysis
- AI-powered code chat via Kenobi agent
- Semantic code search
- Documentation generation

### Frontend UI (Port 12001)

The frontend offers:
- Repository management
- Chat interface with Kenobi
- Code search and exploration
- Documentation viewing

### Ollama Integration (Port 11434)

Ollama provides:
- Local AI model execution (llama3.2:1b)
- No data sent to external services
- Customizable model parameters

## Troubleshooting

### Common Issues and Solutions

#### All Services Not Starting
```bash
# Stop any running services first
./start_all.sh stop

# Check for port conflicts
lsof -i :12000
lsof -i :12001
lsof -i :11434

# Start with fresh logs
rm -f server.log ollama.log frontend.log

# Try starting again
./start_all.sh
```

#### Frontend Dependency Issues
```bash
# Reinstall frontend dependencies
cd frontend
rm -rf node_modules
npm install
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
cd ..
./start_ui.sh
```

#### Backend API Errors
```bash
# Check API health
curl http://localhost:12000/health

# View logs
tail -f server.log

# Restart API
pkill -f uvicorn
./start_dev.sh
```

#### Ollama Issues
```bash
# Check Ollama status
curl http://localhost:11434/api/version

# Restart Ollama
pkill -f ollama
ollama serve &
ollama pull llama3.2:1b
```

## API Documentation

### Core Endpoints

#### Health Check
```bash
curl http://localhost:12000/health
```

#### Repository Management
```bash
# Index a repository
curl -X POST "http://localhost:12000/kenobi/repositories/index" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/repository",
    "name": "My Repository"
  }'

# List repositories
curl http://localhost:12000/kenobi/repositories
```

#### Chat with Kenobi
```bash
# Send a message
curl -X POST "http://localhost:12000/kenobi/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the main architecture of this project?",
    "repository_id": "your-repo-id",
    "branch": "main"
  }'
```

For complete API documentation, visit http://localhost:12000/docs after starting the backend.

## Advanced Configuration

### Environment Variables

The system uses a `.env` file for configuration. Key settings:

```
# API Configuration
API_HOST=0.0.0.0
API_PORT=12000
DEBUG=true

# Ollama Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3.2:1b

# Database Configuration
DATABASE_URL=sqlite:///./kenobi.db
```

### Custom Ports

To use different ports:

1. Edit the `.env` file to change API_PORT
2. Update the proxy in frontend/package.json
3. Start the frontend with a custom port: `PORT=8080 npm start`

### Production Deployment

For production environments:

```bash
# Backend (Production)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:12000

# Frontend (Production)
cd frontend
npm run build
npm install -g serve
serve -s build -l 12001
```

## Support and Maintenance

### Log Files
- Backend API: `server.log`
- Ollama: `ollama.log`
- Frontend: `frontend.log`

### Updates
```bash
# Update dependencies
git pull
pip install -r requirements.txt --upgrade
cd frontend && npm update
ollama pull llama3.2:1b
```

For additional support, refer to the project's GitHub repository or create an issue for specific problems.