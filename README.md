# Multi-Agent Research System

An advanced AI-powered code analysis and repository management platform with 61 comprehensive API endpoints, intelligent agents, and real-time monitoring capabilities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/popoloni/multi-agent-researcher)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/popoloni/multi-agent-researcher.git
cd multi-agent-researcher

# Start all services (backend + Ollama)
./start_dev.sh

# In a new terminal, start the frontend
./start_ui.sh

# Check service status
./check_status.sh
```

**📖 For detailed setup instructions, see [SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md)**

### Access the Application
- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:12000
- **API Documentation**: http://localhost:12000/docs

## ✨ Key Features

- **🤖 AI-Powered Analysis** - Code quality, security, performance analysis with 8 analysis types
- **📊 Real-time Dashboard** - Live monitoring, health scoring (7.75-7.93/10), and analytics
- **🔍 Semantic Search** - Vector-based code search using ChromaDB
- **⚡ Production Ready** - Redis caching (20% hit rate), graceful degradation, 61 API endpoints
- **🏗️ Multi-Agent Architecture** - Specialized agents for orchestration, analysis, and dependencies

## 📊 API Overview

| Category | Endpoints | Key Features |
|----------|-----------|--------------|
| **Core Services** | 21 | Repository management, indexing, health monitoring |
| **Kenobi Management** | 13 | Advanced analysis, batch processing, optimization |
| **AI Analysis** | 4 | Code analysis, test generation, improvements |
| **Advanced Analysis** | 5 | Cross-repository dependencies, impact assessment |
| **Dashboard & Monitoring** | 6 | Real-time metrics, quality dashboards |
| **Quality Analysis** | 4 | Quality assessment, trends, recommendations |
| **Vector Operations** | 3 | Semantic search, similarity, clustering |
| **Cache & Analytics** | 5 | Cache management, system metrics |

**Total: 61 Production-Ready Endpoints**

## 🎯 Use Cases

### For Development Teams
- **Code Quality Assessment** - Automated quality scoring with A+ grade capability
- **AI-Powered Insights** - Code explanations, test generation, improvement suggestions
- **Technical Debt Management** - Identify and prioritize technical debt
- **Cross-Repository Analysis** - Dependency mapping and conflict detection

### For DevOps & Engineering Managers
- **Real-time Monitoring** - System health, performance metrics, quality trends
- **Batch Processing** - Analyze multiple repositories efficiently
- **Quality Dashboards** - Visual metrics and team insights
- **Production Deployment** - Docker, Kubernetes, cloud-ready architecture

## 🔧 Configuration

### Basic Setup
```bash
# Optional: Enhanced caching with Redis
REDIS_URL=redis://localhost:6379

# Optional: AI model configuration
OLLAMA_BASE_URL=http://localhost:11434
```

### Production Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports: ["8080:8080"]
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on: [redis]
  redis:
    image: redis:alpine
```

## 📱 Web Interface

- **[Interactive API Docs](http://localhost:8080/docs)** - Swagger UI with all 61 endpoints
- **[System Dashboard](http://localhost:8080/kenobi/dashboard/overview)** - Real-time monitoring
- **[Health Check](http://localhost:8080/health)** - System status

## 📚 Documentation

### 🚀 [Quick Start Guide](docs/guides/quick-start.md)
Get up and running in 5 minutes with step-by-step instructions.

### 📖 [Complete Documentation](docs/README.md)
Comprehensive documentation including:
- **[API Reference](docs/api/README.md)** - All 61 endpoints with examples
- **[User Guides](docs/guides/README.md)** - Feature guides and tutorials  
- **[Architecture](docs/architecture/README.md)** - System design and components
- **[Deployment Guide](docs/guides/deployment.md)** - Production deployment
- **[Implementation Reports](docs/reports/README.md)** - Development phases and metrics

## 🏆 System Metrics

- **Development Time**: 4 weeks, 4 phases
- **Code Quality**: 7.75-7.93/10 health score achieved
- **Performance**: 20% cache hit rate, <100ms response times
- **Functionality**: 61 endpoints, 8 AI analysis types, production-ready
- **Architecture**: Multi-agent system with graceful degradation

## 🤝 Contributing

See our [Contributing Guide](docs/guides/contributing.md) for development setup and contribution workflow.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**[📚 Full Documentation](docs/README.md)** | **[🚀 Quick Start](docs/guides/quick-start.md)** | **[📊 API Reference](docs/api/README.md)** | **[🏗️ Architecture](docs/architecture/README.md)**