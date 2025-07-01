# Multi-Agent Researcher - Complete Setup and Deployment Guide

This guide provides a comprehensive, tested approach to setting up and running the Multi-Agent Researcher system with minimal hassle.

## Table of Contents

1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Recommended Setup Process](#recommended-setup-process)
4. [Quick Start](#quick-start)
5. [Component Details](#component-details)
6. [System Management](#system-management)
7. [Troubleshooting](#troubleshooting)
8. [API Documentation](#api-documentation)

## System Overview

The Multi-Agent Researcher is a comprehensive code analysis and chat system that consists of:

- **Backend API**: FastAPI-based REST API for repository analysis, AI chat, documentation, dashboard, and more (**90+ endpoints**)
- **Frontend UI**: React-based web interface for interacting with the system
- **Ollama Integration**: Local AI model for code analysis and chat
- **Repository Indexing**: Code parsing and semantic search capabilities
- **Kenobi Agent**: AI assistant for code-related questions
- **Documentation Generation**: AI-powered professional documentation
- **Dashboard & Monitoring**: Real-time system and repository metrics

## Prerequisites

### System Requirements
- Python 3.8+
- Node.js 16+
- npm
- Git
- Ollama (pre-installed)
- At least 8GB RAM (for Ollama models)
- 10GB+ free disk space

### ⚠️ Important Notes
- This guide assumes Ollama is already installed on your system
- A virtual environment is **strongly recommended** to avoid system conflicts
- The application requires `networkx` and `spacy` dependencies not originally listed

## Recommended Setup Process

### Step 1: Clone and Prepare Environment

```bash
# Clone the repository
git clone https://github.com/popoloni/multi-agent-researcher.git
cd multi-agent-researcher

# Create a clean virtual environment (RECOMMENDED)
python3 -m venv researcher-env

# Activate the virtual environment
source researcher-env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies (includes fixed requirements)
pip install -r requirements.txt

# Install spaCy language model (required for NLP features)
python -m spacy download en_core_web_sm

# Install frontend dependencies
cd frontend
npm install
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
cd ..
```

### Step 3: Configure Environment

```bash
# Create .env configuration file
cat > .env << 'EOL'
# API Configuration
API_HOST=0.0.0.0
API_PORT=12000
DEBUG=true

# Ollama Configuration (already installed)
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3.2:1b

# Database Configuration
DATABASE_URL=sqlite:///./kenobi.db

# Logging
LOG_LEVEL=INFO
EOL
```

### Step 4: Make Scripts Executable

```bash
chmod +x start_all.sh start_dev.sh start_ui.sh stop_all.sh check_status.sh restart_backend.sh
```

## Quick Start

### One-Command Launch (After Setup)

```bash
# Activate virtual environment (if not already active)
source researcher-env/bin/activate

# Start everything with one command
./start_all.sh
```

This script will:
1. Start Ollama service (if not running)
2. Download llama3.2:1b model (first time: ~1.3GB)
3. Start the backend API on port 12000
4. Start the frontend UI on port 12001
5. Show you the status and access URLs

**Alternative scripts:**
- `./start_dev.sh` — Start backend + Ollama only
- `./start_ui.sh` — Start frontend only
- `./stop_all.sh` — Stop all services
- `./check_status.sh` — Check status of all services
- `./restart_backend.sh` — Restart backend API only

### Accessing the System

Once started, you can access:
- **Frontend UI**: http://localhost:12001
- **Backend API**: http://localhost:12000
- **API Documentation**: http://localhost:12000/docs
- **Health Check**: http://localhost:12000/health

## Component Details

### Backend API (Port 12000)

The backend provides:
- **90+ production-ready API endpoints**
- Repository indexing and analysis
- AI-powered code chat via Kenobi agent
- Semantic code search with ChromaDB fallback
- Documentation generation
- Real-time health monitoring
- Dashboard and quality metrics
- GitHub integration (search, clone, branch management)
- Cache and analytics endpoints

### Frontend UI (Port 12001)

The frontend offers:
- Repository management interface
- Interactive chat with Kenobi agent
- Code search and exploration
- Documentation viewing
- System dashboard and monitoring
- Functionalities registry (tree-view code navigation)

### Ollama Integration (Port 11434)

Ollama provides:
- Local AI model execution (llama3.2:1b)
- No data sent to external services
- Customizable model parameters
- Model auto-download on first run

## System Management

### Service Control Commands

```bash
# Check system status
./start_all.sh status
# or
./check_status.sh

# Start all services
source researcher-env/bin/activate  # Always activate first
./start_all.sh

# Stop all services
./start_all.sh stop
# or
./stop_all.sh

# Restart all services
./start_all.sh restart
# or
./restart_backend.sh

# Start only backend and Ollama
source researcher-env/bin/activate
./start_dev.sh

# Start only frontend
./start_ui.sh
```

### Proper Restart Procedure

**Always follow this sequence for clean restarts:**

```bash
# 1. Stop all services
./start_all.sh stop
# or
./stop_all.sh

# 2. Verify all services are stopped
./start_all.sh status
# or
./check_status.sh

# 3. Activate virtual environment
source researcher-env/bin/activate
# 4. Start services
./start_all.sh
```

### Verification Commands

```bash
# Test backend health
curl http://localhost:12000/health

# Test Ollama
curl http://localhost:11434/api/version

# Test frontend
curl -s http://localhost:12001 | head -n 5

# Check running processes
lsof -i :12000 -i :12001 -i :11434
```

## Troubleshooting

### Critical Issues and Solutions

#### 1. Missing Dependencies Error
**Error**: `ModuleNotFoundError: No module named 'networkx'`

**Solution**:
```bash
source researcher-env/bin/activate
pip install networkx spacy
python -m spacy download en_core_web_sm
```

#### 2. Services Not Starting
```bash
# Complete cleanup and restart
./start_all.sh stop
./stop_all.sh
pkill -f ollama
pkill -f uvicorn
pkill -f "npm start"

# Check for port conflicts
lsof -i :12000 -i :12001 -i :11434

# Clean restart
source researcher-env/bin/activate
./start_all.sh
```

#### 3. Backend Import Errors
**Error**: Module import failures during startup

**Solution**:
```bash
# Test imports manually
source researcher-env/bin/activate
python -c "import app.main; print('Import successful')"

# If errors, check missing dependencies
pip install -r requirements.txt
```

#### 4. Frontend Dependency Issues
```bash
# Reinstall frontend dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
cd ..
```

#### 5. Ollama Model Issues
```bash
# Check Ollama status
curl http://localhost:11434/api/version

# Restart Ollama if needed
pkill -f ollama
ollama serve &
sleep 5
ollama pull llama3.2:1b
```

#### 6. Port Conflicts
```bash
# Find what's using ports
lsof -i :12000  # Backend
lsof -i :12001  # Frontend  
lsof -i :11434  # Ollama

# Kill conflicting processes
kill <PID>
```

### Advanced Troubleshooting

#### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf researcher-env
python3 -m venv researcher-env
source researcher-env/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### Log Analysis
```bash
# View real-time logs
tail -f server.log      # Backend API logs
tail -f ollama.log      # Ollama service logs
tail -f frontend.log    # Frontend React logs

# Clear logs for fresh start
rm -f *.log
```

## API Documentation

### Core Endpoints

#### Health Check
```bash
curl http://localhost:12000/health
# Expected: {"status":"healthy","service":"Multi-Agent Research System","version":"1.0.0"}
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

### Complete API Reference
For all 90+ endpoints with interactive testing, visit: http://localhost:12000/docs

## Advanced Configuration

### Environment Variables

Complete `.env` configuration options:

```bash
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

# Optional: Redis for caching
# REDIS_URL=redis://localhost:6379

# Optional: External AI models
# ANTHROPIC_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO
```

### 🤖 AI Model Configuration

The system supports multiple AI providers with flexible model selection for different components:

#### **Available Providers**
- **Anthropic Claude**: High-quality cloud models (requires API key)
- **Ollama**: Local models (free, but requires local resources)

#### **Model Configuration Variables**

```bash
# === ANTHROPIC CONFIGURATION ===
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# === RESEARCH AGENTS ===
LEAD_AGENT_MODEL=claude-4-sonnet-20241120          # Lead research planning
SUBAGENT_MODEL=claude-4-sonnet-20241120            # Sub-research execution
CITATION_MODEL=claude-3-5-haiku-20241022           # Citation generation

# === KENOBI CHAT & CODE ANALYSIS ===
KENOBI_MODEL=claude-4-sonnet-20241120              # Code analysis & chat

# === DOCUMENTATION GENERATION ===
DOCUMENTATION_MODEL=claude-4-sonnet-20241120       # Documentation generation

# === GOOGLE SEARCH (for research functionality) ===
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_cse_id_here
```

#### **Available Models**

**Anthropic Claude Models:**
- `claude-4-opus-20241120` - Highest performance, most expensive
- `claude-4-sonnet-20241120` - Balanced performance/cost (recommended)
- `claude-3-5-sonnet-20241022` - Good performance, lower cost
- `claude-3-5-haiku-20241022` - Fast, cost-effective for simple tasks

**Ollama Local Models:**
- `llama3.1:70b` - Highest quality (requires 40GB RAM)
- `llama3.1:8b` - Good balance (requires 8GB RAM)
- `mistral:7b` - Efficient alternative
- `llama3.2:3b` - Lightweight option
- `llama3.2:1b` - Ultra-lightweight (default)

#### **Configuration Examples**

**High-Performance Setup (Best Quality)**
```bash
LEAD_AGENT_MODEL=claude-4-opus-20241120
SUBAGENT_MODEL=claude-4-sonnet-20241120
CITATION_MODEL=claude-3-5-haiku-20241022
KENOBI_MODEL=claude-4-sonnet-20241120
DOCUMENTATION_MODEL=claude-4-sonnet-20241120
```

**Balanced Setup (Recommended)**
```bash
LEAD_AGENT_MODEL=claude-4-sonnet-20241120
SUBAGENT_MODEL=claude-4-sonnet-20241120
CITATION_MODEL=claude-3-5-haiku-20241022
KENOBI_MODEL=claude-3-5-sonnet-20241022
DOCUMENTATION_MODEL=claude-3-5-sonnet-20241022
```

**Local-Only Setup (No API Costs)**
```bash
LEAD_AGENT_MODEL=llama3.1:8b
SUBAGENT_MODEL=mistral:7b
CITATION_MODEL=llama3.2:3b
KENOBI_MODEL=llama3.1:8b
DOCUMENTATION_MODEL=llama3.1:8b
```

**Hybrid Setup (Best of Both)**
```bash
LEAD_AGENT_MODEL=claude-4-sonnet-20241120
SUBAGENT_MODEL=llama3.1:8b
CITATION_MODEL=llama3.2:3b
KENOBI_MODEL=claude-4-sonnet-20241120
DOCUMENTATION_MODEL=claude-3-5-sonnet-20241022
```

#### **How to Configure Models**

1. **Edit your `.env` file** with your preferred models
2. **Restart the system**: `./start_all.sh restart`
3. **Test the configuration** by running research or chat

#### **Model Selection Guidelines**

| Use Case | Recommended Setup | Reasoning |
|----------|-------------------|-----------|
| **Production Research** | High-Performance | Best quality results |
| **Development/Testing** | Balanced | Good quality, reasonable cost |
| **Experimentation** | Local-Only | No API costs, unlimited usage |
| **Budget-Conscious** | Local-Only or Hybrid | Minimal or controlled costs |

> **💡 Tip**: Start with the **Balanced Setup** and adjust based on your quality requirements and budget.

### Custom Ports

To use different ports:

1. Edit the `.env` file to change `API_PORT`
2. Update the proxy in `frontend/package.json`
3. Start the frontend with custom port: `PORT=8080 npm start`

### Production Deployment

For production environments:

```bash
# Backend (Production)
source researcher-env/bin/activate
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:12000

# Frontend (Production)
cd frontend
npm run build
npm install -g serve
serve -s build -l 12001
```

## System Metrics and Performance

### Expected Performance
- **Startup Time**: 30-60 seconds (first run with model download)
- **API Response**: <100ms for most endpoints
- **Memory Usage**: ~2-4GB (including Ollama model)
- **Model Download**: 1.3GB (llama3.2:1b, one-time)

### Health Scoring
The system provides real-time health scoring with grades typically ranging from 7.75-7.93/10.

## Support and Maintenance

### Regular Maintenance
```bash
# Update dependencies
git pull
source researcher-env/bin/activate
pip install -r requirements.txt --upgrade
cd frontend && npm update && cd ..
ollama pull llama3.2:1b
```

### Backup Important Data
- Repository analysis data: `kenobi.db`
- Configuration: `.env`
- Logs: `*.log` files

### Log Files Location
- Backend API: `server.log`
- Ollama: `ollama.log`
- Frontend: `frontend.log`

For additional support, refer to the project's GitHub repository or create an issue for specific problems.

---

**Last Updated**: Based on tested deployment experience with all known issues resolved.
