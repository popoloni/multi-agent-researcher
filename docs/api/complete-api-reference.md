# Complete API Reference

**Version**: Phase 4 Complete  
**Total Endpoints**: 61  
**Base URL**: `http://localhost:8080`  

## 📊 API Categories

### 🔧 Core Services (21 Endpoints)
- `POST /repositories/index` - Index a repository
- `GET /repositories` - List all repositories
- `GET /repositories/{id}` - Get repository details
- `DELETE /repositories/{id}` - Delete repository
- `GET /repositories/{id}/files` - Get repository files
- `GET /repositories/{id}/stats` - Repository statistics
- `GET /repositories/{id}/elements` - Code elements
- `GET /repositories/{id}/dependencies` - Dependencies
- `GET /repositories/{id}/clusters` - Code clusters
- `GET /repositories/{id}/patterns` - Design patterns
- `GET /repositories/{id}/metrics` - Quality metrics
- `GET /repositories/{id}/summary` - Executive summary
- `GET /repositories/{id}/files/{path}` - File analysis
- `GET /repositories/search` - Search repositories
- `GET /repositories/{id}/health` - Health check
- `GET /repositories/{id}/trends` - Quality trends
- `POST /repositories/compare` - Compare repositories
- `POST /repositories/bulk` - Bulk operations
- `GET /repositories/{id}/export` - Export data
- `GET /health` - System health
- `GET /` - Root endpoint

### 📁 Kenobi Repository Management (13 Endpoints)
- `POST /kenobi/repositories/index` - Kenobi repository indexing
- `GET /kenobi/repositories/{id}/health` - Health monitoring
- `GET /kenobi/repositories/{id}/insights` - Actionable insights
- `POST /kenobi/repositories/comprehensive-analysis` - Full analysis
- `POST /kenobi/repositories/batch-analysis` - Batch processing
- `POST /kenobi/repositories/compare` - Repository comparison
- `POST /kenobi/repositories/{id}/optimize` - Optimization
- `POST /kenobi/repositories/{id}/refactor` - Refactoring
- `POST /kenobi/repositories/{id}/testing` - Testing recommendations
- `POST /kenobi/repositories/{id}/documentation` - Documentation
- `POST /kenobi/repositories/{id}/security` - Security analysis
- `POST /kenobi/repositories/{id}/performance` - Performance analysis
- `POST /kenobi/repositories/{id}/migration` - Migration planning

### 🤖 AI Analysis (4 Endpoints)
- `POST /kenobi/ai/analyze-code` - AI code analysis
- `POST /kenobi/ai/explain-code` - Code explanation
- `POST /kenobi/ai/generate-tests` - Test generation
- `POST /kenobi/ai/suggest-improvements` - Improvement suggestions

### 🔬 Advanced Analysis (5 Endpoints)
- `POST /kenobi/analysis/cross-repository-dependencies` - Cross-repo dependencies
- `GET /kenobi/analysis/dependency-health/{id}` - Dependency health
- `POST /kenobi/analysis/dependency-impact` - Impact assessment
- `GET /kenobi/analysis/dependency-patterns/{id}` - Dependency patterns
- `POST /kenobi/analysis/repository-comprehensive` - Comprehensive analysis

### 📊 Dashboard & Monitoring (6 Endpoints)
- `GET /kenobi/dashboard/overview` - System overview
- `GET /kenobi/dashboard/repository/{id}` - Repository dashboard
- `GET /kenobi/dashboard/quality` - Quality dashboard
- `GET /kenobi/dashboard/dependencies` - Dependencies dashboard
- `GET /kenobi/dashboard/real-time` - Real-time monitoring
- `GET /kenobi/dashboard/performance` - Performance dashboard

### 🔍 Quality Analysis (4 Endpoints)
- `POST /kenobi/quality/assess` - Quality assessment
- `GET /kenobi/quality/trends/{id}` - Quality trends
- `POST /kenobi/quality/compare` - Quality comparison
- `GET /kenobi/quality/recommendations/{id}` - Quality recommendations

### 🧮 Vector Operations (3 Endpoints)
- `POST /kenobi/vector/search` - Vector search
- `POST /kenobi/vector/similarity` - Similarity search
- `POST /kenobi/vector/cluster` - Vector clustering

### 🗄️ Cache Management (2 Endpoints)
- `GET /kenobi/cache/stats` - Cache statistics
- `POST /kenobi/cache/clear` - Clear cache

### 📈 Analytics (2 Endpoints)
- `GET /kenobi/analytics/metrics` - System metrics
- `GET /kenobi/analytics/real-time` - Real-time analytics

### 🔍 Code Analysis (1 Endpoint)
- `POST /kenobi/analyze/file` - Individual file analysis

## 📝 Request/Response Examples

### Repository Indexing
```bash
curl -X POST http://localhost:8080/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repo", "name": "my-repo"}'
```

### Comprehensive Analysis
```bash
curl -X POST http://localhost:8080/kenobi/repositories/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/repo",
    "repository_name": "my-repo",
    "analysis_types": ["security", "performance", "quality"]
  }'
```

### Dashboard Overview
```bash
curl -X GET http://localhost:8080/kenobi/dashboard/overview
```

## 🚀 Getting Started

1. Start the server: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
2. Index a repository: `POST /kenobi/repositories/index`
3. Run analysis: `POST /kenobi/repositories/comprehensive-analysis`
4. View dashboard: `GET /kenobi/dashboard/overview`

For detailed endpoint documentation, see the interactive docs at `/docs`.