# Multi-Agent Research System - API Quick Reference

## 🚀 Quick Start Commands

### Basic Repository Operations
```bash
# Health Check
curl http://localhost:8080/

# Index Repository
curl -X POST http://localhost:8080/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repo", "name": "repo-name"}'

# List Repositories
curl http://localhost:8080/kenobi/repositories

# Get Repository Details
curl http://localhost:8080/kenobi/repositories/{repo-id}
```

### Analysis Operations
```bash
# Comprehensive Analysis
curl -X POST http://localhost:8080/kenobi/repositories/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path", "repository_name": "name"}'

# Repository Health
curl http://localhost:8080/kenobi/repositories/{repo-id}/health

# Repository Insights
curl http://localhost:8080/kenobi/repositories/{repo-id}/insights

# Batch Analysis
curl -X POST http://localhost:8080/kenobi/repositories/batch-analysis \
  -H "Content-Type: application/json" \
  -d '{"repository_paths": ["/path1", "/path2"]}'
```

### Comparison & Analytics
```bash
# Compare Repositories
curl -X POST http://localhost:8080/kenobi/repositories/compare \
  -H "Content-Type: application/json" \
  -d '{"repository_ids": ["id1", "id2"]}'

# Dashboard Overview
curl http://localhost:8080/dashboard/overview

# Quality Trends
curl http://localhost:8080/dashboard/quality-trends?time_range=30d
```

### System Monitoring
```bash
# System Health
curl http://localhost:8080/monitoring/health

# Performance Metrics
curl http://localhost:8080/monitoring/metrics

# Cache Statistics
curl http://localhost:8080/cache/stats
```

## 📊 Response Formats

### Repository Index Response
```json
{
  "repository_id": "uuid",
  "name": "string",
  "path": "string",
  "indexed_at": "datetime",
  "total_files": "integer"
}
```

### Health Score Response
```json
{
  "repository_id": "uuid",
  "overall_health_score": "float",
  "health_metrics": {
    "code_quality": "float",
    "security_score": "float",
    "performance_score": "float"
  }
}
```

### Comprehensive Analysis Response
```json
{
  "repository_name": "string",
  "overall_health_score": "float",
  "analysis_results": {
    "security_analysis": {},
    "performance_analysis": {},
    "code_quality": {},
    "test_coverage": {}
  }
}
```

## 🔧 Common Parameters

### Analysis Types
- `security` - Security vulnerability analysis
- `performance` - Performance bottleneck detection
- `quality` - Code quality assessment
- `testing` - Test coverage analysis
- `documentation` - Documentation completeness
- `dependencies` - Dependency health check
- `architecture` - Architectural analysis
- `ai_insights` - AI-powered recommendations

### Comparison Aspects
- `structure` - File and directory structure
- `quality` - Code quality metrics
- `dependencies` - Dependency comparison
- `complexity` - Complexity analysis

### Time Ranges
- `7d` - Last 7 days
- `30d` - Last 30 days
- `90d` - Last 90 days

## ⚡ Performance Tips

1. **Use Caching**: Results are automatically cached for faster subsequent requests
2. **Batch Operations**: Use batch analysis for multiple repositories
3. **Selective Analysis**: Specify analysis types to reduce processing time
4. **Monitor Health**: Regular health checks prevent issues

## 🚨 Error Handling

### Common Error Codes
- `400` - Bad Request (invalid parameters)
- `404` - Repository not found
- `500` - Internal server error

### Error Response Format
```json
{
  "detail": "Error description"
}
```

## 📈 Endpoint Categories

### Core (6 endpoints)
- Repository management and basic operations

### Analysis (8 endpoints)  
- Code analysis and quality assessment

### AI & Vector (6 endpoints)
- AI-powered analysis and semantic search

### Phase 4 Advanced (8+ endpoints)
- Dashboard, monitoring, and production features

**Total: 28+ Production-Ready Endpoints**

---

*For complete documentation, see API_DOCUMENTATION.md*