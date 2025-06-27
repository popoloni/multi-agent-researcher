# Multi-Agent Researcher

> **Advanced AI-powered code analysis platform with specialized agents**

A comprehensive multi-agent system for intelligent code analysis, repository management, and AI-powered insights. Built with FastAPI, Ollama, and ChromaDB for production-ready performance.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/popoloni/multi-agent-researcher)

## 🎯 What It Does

Transform your code analysis workflow with AI-powered insights:

- **🔍 Intelligent Code Analysis**: Deep repository analysis with 10+ quality metrics
- **🤖 AI-Powered Insights**: 8 types of AI analysis including explanations and improvements
- **📊 Real-time Dashboard**: Live monitoring with 6 dashboard services
- **🕸️ Dependency Analysis**: Cross-repository dependency mapping and impact assessment
- **⚡ High Performance**: Redis caching with sub-2-second response times
- **🔎 Semantic Search**: Vector-based code search with ChromaDB

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
# Clone the repository
git clone https://github.com/popoloni/multi-agent-researcher.git
cd multi-agent-researcher

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py

# Open API documentation
open http://localhost:8080/docs
```

**First Analysis:**
```bash
# Index a repository
curl -X POST "http://localhost:8080/kenobi/repositories/index" \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/your/repository"}'

# Get AI insights
curl "http://localhost:8080/kenobi/repositories/{repo_id}/insights"
```

## 🏗️ Architecture

Built on a modern, scalable multi-agent architecture:

```
Kenobi Lead Agent
├── Repository Analysis Agent    # Specialized repository analysis
├── Dependency Analysis Agent    # Cross-repo dependency tracking
└── Code Search Agent           # Semantic search capabilities

Production Services
├── Cache Service (Redis)       # High-performance caching
├── Dashboard Service          # Real-time data aggregation
├── Analytics Engine          # Performance tracking
└── Vector Database (ChromaDB) # Semantic embeddings
```

## 📊 System Capabilities

### 🤖 **3 Specialized Agents**
- **Kenobi Agent**: Lead coordination and comprehensive analysis
- **Repository Analysis Agent**: Deep code analysis and quality assessment
- **Dependency Analysis Agent**: Cross-repository dependency tracking

### 🌐 **61 API Endpoints**
- **Repository Management**: 11 endpoints for indexing and management
- **Code Analysis**: 7 endpoints for comprehensive analysis
- **Search & Discovery**: 6 endpoints for semantic search
- **Dashboard Services**: 6 endpoints for real-time visualization
- **AI Analysis**: 4 endpoints for AI-powered insights
- **Analytics & Monitoring**: 4 endpoints for performance tracking

### 🏭 **Production Features**
- **Redis Caching**: High-performance caching with fallback
- **Real-time Analytics**: Performance and usage tracking
- **Horizontal Scaling**: Production-ready architecture
- **Comprehensive Testing**: 100% validation coverage

## 📖 Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) directory:

- **[📖 Complete Documentation](./docs/)** - Full documentation hub
- **[🌐 API Reference](./docs/api/)** - Complete API documentation with 61 endpoints
- **[🏗️ Implementation Guide](./docs/implementation/)** - Architecture and development guides
- **[🧪 Testing Guide](./docs/testing/)** - Testing procedures and validation
- **[🚀 Deployment Guide](./docs/deployment/)** - Production deployment instructions
- **[📖 User Guides](./docs/guides/)** - Practical usage guides

## 🔧 Key Features

### Code Analysis
- **Quality Metrics**: 10+ comprehensive quality indicators
- **Complexity Analysis**: Cyclomatic complexity and maintainability scores
- **Pattern Detection**: Code patterns and anti-patterns identification
- **AI Explanations**: Natural language code explanations

### Search & Discovery
- **Semantic Search**: AI-powered meaning-based code search
- **Pattern Search**: Find specific coding patterns across repositories
- **Cross-Repository Search**: Search across multiple codebases
- **Similarity Detection**: Find similar code implementations

### Monitoring & Analytics
- **Real-time Dashboard**: Live system and repository monitoring
- **Performance Analytics**: Response times and system metrics
- **Quality Trends**: Code quality tracking over time
- **Usage Statistics**: System utilization and performance data

## 🚀 Performance

- **Response Times**: < 2 seconds for most operations
- **Concurrent Users**: Up to 100 simultaneous users
- **Cache Hit Rate**: 25-80% depending on usage patterns
- **Uptime**: 99.9% availability target
- **Scalability**: Horizontal scaling ready

## 🔒 Security

- **Input Validation**: Comprehensive Pydantic model validation
- **Error Handling**: Graceful error responses and logging
- **CORS Support**: Configurable cross-origin request handling
- **Production Ready**: Security headers and best practices

## 📈 Implementation Status

| Component | Status | Endpoints |
|-----------|--------|-----------|
| **Repository Management** | ✅ Complete | 11 endpoints |
| **Code Analysis** | ✅ Complete | 7 endpoints |
| **Search & Discovery** | ✅ Complete | 6 endpoints |
| **Dashboard Services** | ✅ Complete | 6 endpoints |
| **AI Analysis** | ✅ Complete | 4 endpoints |
| **Analytics & Monitoring** | ✅ Complete | 4 endpoints |
| **Production Features** | ✅ Complete | Redis, Caching, Monitoring |

**Total**: 61 API endpoints, 100% implementation complete

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Ollama**: Local AI model integration for code analysis
- **ChromaDB**: Vector database for semantic search and embeddings
- **Redis**: High-performance caching and session management
- **NetworkX**: Dependency graph analysis and visualization
- **Pydantic**: Data validation and serialization

## 📋 Requirements

- **Python**: 3.8 or higher
- **Ollama**: For AI model integration
- **Redis**: For caching (optional, has fallback)
- **Memory**: 4GB+ recommended
- **Storage**: 2GB+ for models and data

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./docs/guides/README.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **[📚 Documentation](./docs/)** - Complete documentation
- **[🌐 API Docs](http://localhost:8080/docs)** - Interactive API documentation
- **[🔧 GitHub Repository](https://github.com/popoloni/multi-agent-researcher)** - Source code

---

**Built with ❤️ for the developer community**

*Multi-Agent Researcher - Transforming code analysis with AI*