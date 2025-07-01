# System Architecture

Comprehensive documentation of the Multi-Agent Research System architecture.

## 🏗️ Architecture Overview

The Multi-Agent Research System is built with a modular, scalable architecture designed for production deployment with 90+ API endpoints.

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│                  (React + Port 12001)                      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                        │
│                  (FastAPI + Port 12000)                    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Agent Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Kenobi    │  │ Repository  │  │ Dependency  │        │
│  │   Agent     │  │   Agent     │  │   Agent     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Search    │  │ Categorize  │  │   Code      │        │
│  │   Agent     │  │   Agent     │  │  Search     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Repository  │  │Documentation│  │   Analysis  │        │
│  │  Service    │  │  Service    │  │   Service   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   GitHub    │  │     RAG     │  │    Chat     │        │
│  │  Service    │  │  Service    │  │  History    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Vector    │  │   Cache     │  │  Dashboard  │        │
│  │  Database   │  │  Service    │  │  Service    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Engine Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │     AI      │  │  Analytics  │  │   Quality   │        │
│  │   Engine    │  │   Engine    │  │   Engine    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   SQLite    │  │  ChromaDB   │  │   File      │        │
│  │  Database   │  │   Vector    │  │   System    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### Agent Layer
- **Kenobi Agent**: Master orchestrator for complex analysis workflows (51KB, 1215 lines)
- **Repository Agent**: Specialized in repository-level analysis and insights (35KB, 776 lines)
- **Dependency Agent**: Handles cross-repository dependency analysis (49KB, 1049 lines)
- **Search Agent**: Code search and semantic analysis (8.6KB, 282 lines)
- **Categorization Agent**: Code element categorization (25KB, 589 lines)
- **Code Search Agent**: Advanced code search capabilities (18KB, 451 lines)
- **Repository Analysis Agent**: Repository-specific analysis (31KB, 706 lines)
- **Dependency Analysis Agent**: Advanced dependency analysis (38KB, 876 lines)

### Service Layer
- **Repository Service**: Repository management and indexing (31KB, 795 lines)
- **Documentation Service**: AI-powered documentation generation (16KB, 440 lines)
- **Analysis Service**: Code analysis and quality assessment (24KB, 550 lines)
- **GitHub Service**: GitHub API integration (16KB, 441 lines)
- **RAG Service**: Retrieval-Augmented Generation (20KB, 486 lines)
- **Chat History Service**: Chat session management (20KB, 546 lines)
- **Vector Database Service**: ChromaDB integration (26KB, 677 lines)
- **Content Indexing Service**: Content processing and indexing (33KB, 865 lines)
- **Cache Service**: Redis + in-memory caching (19KB, 577 lines)
- **Dashboard Service**: Real-time metrics and monitoring (25KB, 582 lines)
- **Database Service**: SQLite database operations (17KB, 361 lines)
- **Indexing Service**: Search indexing (21KB, 554 lines)

### Engine Layer
- **AI Engine**: Ollama integration for AI analysis
- **Analytics Engine**: Real-time analytics and monitoring
- **Quality Engine**: Code quality assessment and scoring
- **Vector Service**: Semantic embeddings and similarity search

## 🔧 Technical Stack

### Backend
- **Framework**: FastAPI + Uvicorn
- **Language**: Python 3.8+
- **Port**: 12000 (Backend API)
- **Port**: 12001 (Frontend UI)

### AI & ML
- **LLM**: Ollama (llama3.2:1b)
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence Transformers

### Storage
- **Database**: SQLite (async)
- **Vector Store**: ChromaDB
- **Cache**: Redis + in-memory fallback
- **File System**: Local storage

### Frontend
- **Framework**: React
- **Styling**: Tailwind CSS
- **Build**: Create React App

## 🚀 Scalability Features

- **Stateless Design**: No server-side session storage
- **Multi-level Caching**: Redis + in-memory caching with TTL
- **Async Processing**: Non-blocking I/O operations with background tasks
- **Horizontal Scaling**: Multiple instance support
- **Extended Timeouts**: 5-minute timeout for long-running operations

## 📊 Data Flow

### Repository Analysis Workflow
```
1. Repository Indexing
   ├── GitHub Integration (search, clone, branch management)
   ├── File Discovery and Parsing
   ├── Code Element Extraction
   └── Metadata Generation

2. Vector Processing
   ├── Code Embedding Generation
   ├── Similarity Calculation
   └── Clustering Analysis

3. Quality Analysis
   ├── Complexity Metrics
   ├── Maintainability Assessment
   └── Security Scanning

4. AI Analysis
   ├── Pattern Recognition
   ├── Improvement Suggestions
   └── Test Generation

5. Documentation Generation
   ├── AI-Powered Content Creation
   ├── Architecture Analysis
   └── User Guide Generation

6. Results Aggregation
   ├── Health Score Calculation
   ├── Insight Generation
   └── Recommendation Synthesis
```

### Chat & RAG Workflow
```
1. Session Management
   ├── Create Chat Session
   ├── Context Retrieval
   └── History Management

2. Query Processing
   ├── Message Analysis
   ├── Context Enhancement
   └── RAG Integration

3. Response Generation
   ├── AI Model Processing
   ├── Source Attribution
   └── Response Formatting
```

## 🔐 Security Architecture

### Authentication & Authorization
- **API Key Authentication**: Optional enhanced access
- **Rate Limiting**: Request throttling and abuse prevention
- **Input Validation**: Comprehensive request validation with Pydantic

### Data Security
- **Secure Storage**: Encrypted sensitive data
- **Access Control**: Role-based permissions
- **Audit Logging**: Security event tracking

## 📈 Monitoring & Observability

### Health Monitoring
- **System Health Checks**: Automated health verification
- **Performance Metrics**: Response time and throughput tracking
- **Error Tracking**: Comprehensive error monitoring with graceful degradation

### Analytics
- **Usage Analytics**: API usage patterns and trends
- **Performance Analytics**: System performance insights
- **Quality Analytics**: Code quality trends and patterns
- **Real-time Monitoring**: Live system metrics

### Dashboard Features
- **System Overview**: High-level system status
- **Repository Dashboard**: Per-repository metrics
- **Quality Dashboard**: Code quality insights
- **Dependencies Dashboard**: Dependency visualization
- **Search Dashboard**: Search analytics
- **Real-time Dashboard**: Live monitoring

## 🔗 API Architecture

### Endpoint Categories (90+ Total)
- **Repository Management**: 25 endpoints
- **Documentation**: 8 endpoints
- **Chat & RAG**: 6 endpoints
- **Analysis & Quality**: 15 endpoints
- **Vector Operations**: 6 endpoints
- **Dashboard & Monitoring**: 10 endpoints
- **GitHub Integration**: 10 endpoints
- **Cache & Analytics**: 6 endpoints
- **Research (Mock)**: 4 endpoints

### Response Patterns
- **Standard Success**: JSON with status, data, timestamp
- **Async Operations**: Task ID with status tracking
- **Error Handling**: Structured error responses with details
- **Progress Tracking**: Real-time progress updates (0-100%)

## 🎯 Production Features

### Performance Optimizations
- **Background Tasks**: Async processing for long operations
- **Caching Strategy**: Multi-level caching with intelligent invalidation
- **Connection Pooling**: Database connection optimization
- **Memory Management**: Efficient memory usage patterns

### Reliability Features
- **Graceful Degradation**: Fallback mechanisms for service failures
- **Error Recovery**: Automatic retry and recovery mechanisms
- **Timeout Handling**: Extended timeouts for complex operations
- **Health Checks**: Comprehensive system health monitoring

## 🔗 Related Documentation

- [API Documentation](../api/README.md)
- [Deployment Guide](../guides/deployment.md)
- [User Guides](../guides/README.md)
- [Implementation Reports](../reports/README.md)