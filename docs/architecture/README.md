# System Architecture

Comprehensive documentation of the Multi-Agent Research System architecture.

## 🏗️ Architecture Overview

The Multi-Agent Research System is built with a modular, scalable architecture designed for production deployment.

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                        │
│                  (FastAPI + Uvicorn)                       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Agent Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Kenobi    │  │ Repository  │  │ Dependency  │        │
│  │   Agent     │  │   Agent     │  │   Agent     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Cache     │  │  Dashboard  │  │   Vector    │        │
│  │  Service    │  │   Service   │  │  Service    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### Agent Layer
- **Kenobi Agent**: Master orchestrator for complex analysis workflows
- **Repository Agent**: Specialized in repository-level analysis and insights
- **Dependency Agent**: Handles cross-repository dependency analysis

### Service Layer
- **Cache Service**: Redis + in-memory caching with TTL management
- **Dashboard Service**: Real-time metrics aggregation and monitoring
- **Vector Service**: ChromaDB integration for semantic search

### Engine Layer
- **AI Analysis Engine**: 8 analysis types with fallback mechanisms
- **Code Quality Engine**: 10 quality metrics with grading system
- **Vector Database**: Semantic embeddings and similarity search

## 🔧 Technical Stack

- **Backend**: FastAPI + Uvicorn
- **AI**: Ollama, ChromaDB, Sentence Transformers
- **Caching**: Redis + in-memory fallback
- **Storage**: File system + vector database

## 🚀 Scalability Features

- **Stateless Design**: No server-side session storage
- **Multi-level Caching**: Redis + in-memory caching
- **Async Processing**: Non-blocking I/O operations
- **Horizontal Scaling**: Multiple instance support