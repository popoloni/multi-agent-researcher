# API Documentation

Complete API reference for the Multi-Agent Research System with 61 endpoints.

## 📚 Documentation Files

- **[Complete API Reference](./complete-api-reference.md)** - Detailed documentation of all endpoints
- **[Quick Reference](./quick-reference.md)** - Common endpoints and examples

## 📊 API Overview

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Core Services** | 21 | Basic repository operations |
| **Repository Management** | 13 | Advanced repository analysis |
| **AI Analysis** | 4 | AI-powered code analysis |
| **Advanced Analysis** | 5 | Cross-repository analysis |
| **Dashboard & Monitoring** | 6 | Real-time monitoring |
| **Quality Analysis** | 4 | Code quality assessment |
| **Vector Operations** | 3 | Semantic search |
| **Cache Management** | 2 | Cache performance |
| **Analytics** | 2 | System analytics |
| **Code Analysis** | 1 | Individual file analysis |

**Total: 61 Endpoints**

## 🚀 Quick Start

```bash
# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8080

# Index repository
curl -X POST http://localhost:8080/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repo", "name": "my-repo"}'

# Run analysis
curl -X POST http://localhost:8080/kenobi/repositories/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo", "repository_name": "my-repo"}'
```

## 🔗 Interactive Documentation

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **OpenAPI Spec**: `http://localhost:8080/openapi.json`