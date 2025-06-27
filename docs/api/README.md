# API Documentation

Complete API reference for the Multi-Agent Researcher system with 61 endpoints covering all aspects of code analysis, repository management, and AI-powered insights.

## 📋 API Overview

**Base URL**: `http://localhost:8080`  
**Total Endpoints**: 61  
**API Version**: v1.0.0  
**Documentation Format**: OpenAPI 3.0

## 📚 Documentation Files

### [Complete API Documentation](./API_DOCUMENTATION_COMPLETE.md)
Comprehensive documentation with detailed request/response schemas, examples, and usage patterns for the 28 most important endpoints.

**Covers:**
- Repository Management (5 endpoints)
- Code Analysis (3 endpoints)
- Search & Discovery (2 endpoints)
- Quality Analysis (2 endpoints)
- AI Analysis (1 endpoint)
- Advanced Repository Operations (3 endpoints)
- Dashboard Services (6 endpoints)
- Analytics & Monitoring (4 endpoints)
- Cache Management (2 endpoints)

### [API Signatures Reference](./API_SIGNATURES_COMPLETE.md)
Complete list of all 61 endpoints extracted directly from the running FastAPI application.

**Includes:**
- System & Health (5 endpoints)
- Repository Management (11 endpoints)
- Code Analysis (7 endpoints)
- Search & Discovery (6 endpoints)
- Quality Analysis (4 endpoints)
- AI-Powered Analysis (4 endpoints)
- Dashboard & Visualization (6 endpoints)
- Analytics & Monitoring (4 endpoints)
- Vector Operations (3 endpoints)
- Cache Management (2 endpoints)
- Statistics (2 endpoints)
- Element Relationships (2 endpoints)
- Research & Demo (4 endpoints)

## 🚀 Quick Start

### 1. **Basic Repository Analysis**
```bash
# Index a repository
curl -X POST "http://localhost:8080/kenobi/repositories/index" \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repository"}'

# Get comprehensive analysis
curl -X POST "http://localhost:8080/kenobi/analysis/repository-comprehensive" \
  -H "Content-Type: application/json" \
  -d '{"repository_id": "your-repo-id"}'
```

### 2. **Search and Discovery**
```bash
# Semantic search
curl -X POST "http://localhost:8080/kenobi/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication function", "repository_id": "your-repo-id"}'
```

### 3. **Dashboard Data**
```bash
# System overview
curl "http://localhost:8080/kenobi/dashboard/overview"

# Quality metrics
curl "http://localhost:8080/kenobi/dashboard/quality"
```

## 🔧 Interactive Documentation

### Swagger UI
Access the interactive API documentation at:
`http://localhost:8080/docs`

### ReDoc
Alternative documentation interface at:
`http://localhost:8080/redoc`

---

**Last Updated**: June 27, 2025  
**API Version**: v1.0.0  
**Status**: Production Ready