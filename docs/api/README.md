# API Documentation

Complete API reference for the Multi-Agent Research System with 90+ endpoints.

## 📚 Documentation Files

- **[Complete API Reference](./complete-api-reference.md)** - Detailed documentation of all endpoints
- **[Quick Reference](./quick-reference.md)** - Common endpoints and examples

## 📊 API Overview

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Repository Management** | 25 | GitHub integration, cloning, indexing, analysis |
| **Documentation** | 8 | AI-powered generation, progress tracking, async processing |
| **Chat & RAG** | 6 | AI-powered conversations, session management |
| **Analysis & Quality** | 15 | Code analysis, quality assessment, AI insights |
| **Vector Operations** | 6 | Semantic search, similarity, clustering |
| **Dashboard & Monitoring** | 10 | Real-time metrics, quality dashboards |
| **GitHub Integration** | 10 | Repository search, cloning, branch management |
| **Cache & Analytics** | 6 | Cache management, system metrics |
| **Research (Mock)** | 4 | Research functionality (mock implementation) |

**Total: 90+ Endpoints**

## 🚀 Quick Start

```bash
# Start server
uvicorn app.main:app --host 0.0.0.0 --port 12000

# Index repository
curl -X POST http://localhost:12000/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repo", "name": "my-repo"}'

# Run analysis
curl -X POST http://localhost:12000/kenobi/repositories/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo", "repository_name": "my-repo"}'
```

## 🔗 Interactive Documentation

- **Swagger UI**: `http://localhost:12000/docs`
- **ReDoc**: `http://localhost:12000/redoc`
- **OpenAPI Spec**: `http://localhost:12000/openapi.json`