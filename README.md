# Multi-Agent Research System

An advanced AI-powered code analysis and repository management platform with 90+ comprehensive API endpoints, intelligent agents, and real-time monitoring capabilities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/popoloni/multi-agent-researcher)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/popoloni/multi-agent-researcher.git
cd multi-agent-researcher

# Make scripts executable
chmod +x start_all.sh start_dev.sh start_ui.sh

# Start everything with one command
./start_all.sh

# Or start components individually:
# ./start_dev.sh    # Start backend + Ollama
# ./start_ui.sh     # Start frontend
```

**📖 For detailed setup instructions, see [SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md)**

### Access the Application
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
```

## ✨ Key Features

- **🤖 AI-Powered Documentation** - Professional documentation generation using Ollama LLM with real-time progress tracking
- **📊 Hierarchical Code Analysis** - Tree-view functionalities registry with GitHub source code integration  
- **🔍 Semantic Search** - Vector-based code search using ChromaDB
- **⚡ Production Ready** - Extended timeout handling, graceful error recovery, 90+ API endpoints
- **🏗️ Multi-Agent Architecture** - Specialized agents for orchestration, analysis, and dependencies
- **🎯 Complete Workflow** - GitHub search → clone → index → AI documentation → documentation-aware chat

## 🎉 Latest Improvements (v1.3.0)

### 💬 Fully Functional Chat System
- **AI-Powered Conversations**: Working chat interface with Ollama llama3.2:1b integration
- **Repository Context Awareness**: Chat understands repository structure and answers code-specific questions
- **Session Management**: Create and manage chat sessions with unique session IDs
- **Modern UI**: Professional blue theme with enhanced message bubbles and loading animations

### 🚀 AI-Powered Documentation Generation
- **Professional Content**: AI-generated descriptions using Ollama llama3.2:1b model
- **Asynchronous Processing**: Background task processing with real-time progress tracking (0-100%)
- **No More Timeouts**: Handles long-running generation (2-3 minutes) gracefully
- **Rich Context**: Generates comprehensive overviews, architecture analysis, and user guides

### 🗂️ Enhanced Functionalities Registry
- **Hierarchical Structure**: Tree view grouping functions by source files
- **Smart Organization**: Logical sorting (Classes → Functions → Methods → Variables)
- **Functional Buttons**: Eye button opens GitHub source code, doc button navigates to documentation
- **Multiple Views**: Both hierarchical and flat view options

### 🔧 System Stability Improvements
- **Database Architecture**: Fixed async SQLite driver issues and unified database connections
- **Service Integration**: All services now work harmoniously with proper error handling
- **Extended Timeouts**: 5-minute timeout for repository operations (cloning, parsing, AI analysis)
- **Enhanced Error Handling**: User-friendly error messages with automatic clearing

## 📊 API Overview

| Category | Endpoints | Key Features |
|----------|-----------|--------------|
| **Repository Management** | 25 | GitHub integration, cloning, indexing, analysis |
| **Documentation** | 8 | AI-powered generation, progress tracking, async processing |
| **Chat & RAG** | 6 | AI-powered conversations, session management |
| **Analysis & Quality** | 15 | Code analysis, quality assessment, AI insights |
| **Vector Operations** | 6 | Semantic search, similarity, clustering |
| **Dashboard & Monitoring** | 10 | Real-time metrics, quality dashboards |
| **GitHub Integration** | 10 | Repository search, cloning, branch management |
| **Cache & Analytics** | 6 | Cache management, system metrics |

**Total: 90+ Production-Ready Endpoints**

## 🎯 Use Cases

### For Development Teams
- **AI Documentation Generation** - Automated professional documentation with contextual descriptions
- **Code Quality Assessment** - Automated quality scoring with A+ grade capability
- **Hierarchical Code Navigation** - Tree-view exploration with direct GitHub source links
- **Technical Debt Management** - Identify and prioritize technical debt

### For DevOps & Engineering Managers
- **Real-time Progress Monitoring** - Track documentation generation and repository processing
- **Batch Processing** - Analyze multiple repositories efficiently with extended timeout handling
- **Quality Dashboards** - Visual metrics and team insights
- **Production Deployment** - Docker, Kubernetes, cloud-ready architecture

## 🔧 Configuration

### Basic Setup
```bash
# Optional: Enhanced caching with Redis
REDIS_URL=redis://localhost:6379

# Optional: AI model configuration
OLLAMA_BASE_URL=http://localhost:11434

# GitHub integration
GITHUB_TOKEN=your_github_token_here
```

### Production Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports: ["12000:12000"]
    environment:
      - REDIS_URL=redis://redis:6379
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    depends_on: [redis, ollama]
  frontend:
    build: ./frontend
    ports: ["12001:3000"]
  redis:
    image: redis:alpine
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
```

## 📱 Web Interface

- **[Interactive API Docs](http://localhost:12000/docs)** - Swagger UI with all 90+ endpoints
- **[Frontend Dashboard](http://localhost:12001)** - Complete UI with AI documentation generation
- **[Repository Management](http://localhost:12001/repositories)** - Clone, analyze, and manage repositories
- **[Kenobi Chat](http://localhost:12001/chat)** - AI-powered chat about your codebase
- **[Functionalities Registry](http://localhost:12001/repositories/{id}/functionalities)** - Hierarchical code exploration
- **[Documentation Viewer](http://localhost:12001/repositories/{id}/documentation)** - AI-generated documentation

## 📚 Documentation

### 🚀 [Quick Start Guide](docs/guides/quick-start.md)
Get up and running in 5 minutes with step-by-step instructions.

### 📖 [Complete Documentation](docs/README.md)
Comprehensive documentation including:
- **[API Reference](docs/api/README.md)** - All 90+ endpoints with examples
- **[User Guides](docs/guides/README.md)** - Feature guides and tutorials  
- **[Architecture](docs/architecture/README.md)** - System design and components
- **[Deployment Guide](docs/guides/deployment.md)** - Production deployment
- **[Implementation Reports](docs/reports/README.md)** - Development phases and metrics

### 📋 [Changelog](CHANGELOG.md)
See [CHANGELOG.md](CHANGELOG.md) for detailed information about recent improvements and bug fixes.

## 🏆 System Metrics

- **Development Time**: 4 weeks, 4 phases + debugging session improvements
- **Code Quality**: 85% complete with high-quality foundations
- **Performance**: Extended timeout handling, real-time progress tracking
- **Functionality**: 90+ endpoints, AI-powered documentation, hierarchical navigation
- **Architecture**: Multi-agent system with graceful error handling

## 🧪 Testing

### Verified Working Features
- ✅ **Chat System**: AI-powered conversations with repository context awareness
- ✅ **GitHub Integration**: Complete API with search, cloning, repository info
- ✅ **AI Documentation**: Professional content generation with Ollama integration
- ✅ **Repository Processing**: 5-minute timeout handling for complex repositories
- ✅ **Functionalities Registry**: Hierarchical navigation with GitHub source links
- ✅ **Database Operations**: Async SQLite with proper service integration
- ✅ **Progress Tracking**: Real-time updates for long-running operations
- ✅ **Error Handling**: User-friendly messages with automatic recovery

### Test Coverage
```bash
# Run comprehensive tests
./verify_application.sh

# Test specific workflows
python demo/demo_working_features.py
python demo/add_repository.py
python demo/demo_documentation_generation.py
```

## 🤝 Contributing

See our [Contributing Guide](docs/guides/contributing.md) for development setup and contribution workflow.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**[📚 Full Documentation](docs/README.md)** | **[🚀 Quick Start](docs/guides/quick-start.md)** | **[📊 API Reference](docs/api/README.md)** | **[🏗️ Architecture](docs/architecture/README.md)** | **[📋 Changelog](CHANGELOG.md)**