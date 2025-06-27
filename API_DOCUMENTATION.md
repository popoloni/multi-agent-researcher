# Multi-Agent Research System - Complete API Documentation

## Overview
This document provides comprehensive documentation for all API endpoints implemented in the Multi-Agent Research System. The system includes 25+ endpoints across 4 phases of development, providing advanced code analysis, repository management, and real-time monitoring capabilities.

## Base URL
```
http://localhost:8080
```

## Authentication
Currently, no authentication is required for API access.

---

## 📊 CORE REPOSITORY MANAGEMENT ENDPOINTS

### 1. Health Check
**GET** `/`
- **Description**: Basic health check for the service
- **Parameters**: None
- **Response**:
```json
{
  "status": "healthy",
  "service": "Multi-Agent Research System",
  "version": "1.0.0"
}
```

### 2. Index Repository
**POST** `/kenobi/repositories/index`
- **Description**: Index a repository for analysis
- **Request Body**:
```json
{
  "path": "string",     // Local path to repository
  "name": "string"      // Repository name
}
```
- **Response**:
```json
{
  "repository_id": "uuid",
  "name": "string",
  "path": "string",
  "indexed_at": "datetime",
  "total_files": "integer",
  "total_elements": "integer"
}
```

### 3. List Repositories
**GET** `/kenobi/repositories`
- **Description**: Get list of all indexed repositories
- **Parameters**: None
- **Response**:
```json
{
  "repositories": [
    {
      "id": "uuid",
      "name": "string",
      "path": "string",
      "indexed_at": "datetime",
      "file_count": "integer"
    }
  ],
  "total_count": "integer"
}
```

### 4. Get Repository Details
**GET** `/kenobi/repositories/{repository_id}`
- **Description**: Get detailed information about a specific repository
- **Parameters**:
  - `repository_id` (path): Repository UUID
- **Response**:
```json
{
  "id": "uuid",
  "name": "string",
  "path": "string",
  "indexed_at": "datetime",
  "file_count": "integer",
  "total_elements": "integer",
  "analysis_history": []
}
```

### 5. Delete Repository
**DELETE** `/kenobi/repositories/{repository_id}`
- **Description**: Remove repository from index
- **Parameters**:
  - `repository_id` (path): Repository UUID
- **Response**:
```json
{
  "message": "Repository deleted successfully",
  "repository_id": "uuid"
}
```

---

## 🔍 CODE ANALYSIS ENDPOINTS

### 6. Analyze Code
**POST** `/kenobi/analyze`
- **Description**: Analyze code snippet or file
- **Request Body**:
```json
{
  "code": "string",           // Code to analyze
  "language": "string",       // Programming language
  "analysis_type": "string"   // Type of analysis
}
```
- **Response**:
```json
{
  "analysis_id": "uuid",
  "code_quality_score": "float",
  "issues": [],
  "suggestions": [],
  "metrics": {},
  "timestamp": "datetime"
}
```

### 7. Get File Analysis
**GET** `/kenobi/repositories/{repository_id}/files/{file_path}/analysis`
- **Description**: Get analysis for specific file in repository
- **Parameters**:
  - `repository_id` (path): Repository UUID
  - `file_path` (path): File path within repository
- **Response**:
```json
{
  "file_path": "string",
  "analysis": {
    "quality_score": "float",
    "complexity": "integer",
    "issues": [],
    "suggestions": []
  },
  "timestamp": "datetime"
}
```

### 8. Repository Quality Analysis
**GET** `/kenobi/repositories/{repository_id}/quality`
- **Description**: Get comprehensive quality analysis for repository
- **Parameters**:
  - `repository_id` (path): Repository UUID
- **Response**:
```json
{
  "repository_id": "uuid",
  "overall_quality_score": "float",
  "metrics": {
    "maintainability": "float",
    "complexity": "float",
    "test_coverage": "float",
    "documentation": "float"
  },
  "file_analyses": [],
  "recommendations": []
}
```

---

## 🧠 AI-POWERED ANALYSIS ENDPOINTS

### 9. AI Code Analysis
**POST** `/kenobi/ai-analysis`
- **Description**: Advanced AI-powered code analysis
- **Request Body**:
```json
{
  "code": "string",
  "context": "string",
  "analysis_depth": "string"  // "basic" | "detailed" | "comprehensive"
}
```
- **Response**:
```json
{
  "analysis_id": "uuid",
  "ai_insights": {
    "code_quality": {},
    "security_analysis": {},
    "performance_insights": {},
    "refactoring_suggestions": []
  },
  "confidence_score": "float",
  "processing_time": "float"
}
```

### 10. Repository AI Analysis
**POST** `/kenobi/repositories/{repository_id}/ai-analysis`
- **Description**: AI analysis for entire repository
- **Parameters**:
  - `repository_id` (path): Repository UUID
- **Request Body**:
```json
{
  "analysis_types": ["string"],  // Array of analysis types
  "depth": "string"              // Analysis depth
}
```
- **Response**:
```json
{
  "repository_id": "uuid",
  "ai_analysis": {
    "architecture_analysis": {},
    "code_patterns": {},
    "security_assessment": {},
    "performance_analysis": {},
    "maintainability_score": "float"
  },
  "recommendations": [],
  "timestamp": "datetime"
}
```

---

## 🔗 VECTOR SEARCH & SIMILARITY ENDPOINTS

### 11. Semantic Search
**POST** `/kenobi/search/semantic`
- **Description**: Semantic search across indexed repositories
- **Request Body**:
```json
{
  "query": "string",
  "repository_ids": ["uuid"],  // Optional: specific repositories
  "limit": "integer",          // Default: 10
  "similarity_threshold": "float"  // Default: 0.7
}
```
- **Response**:
```json
{
  "query": "string",
  "results": [
    {
      "repository_id": "uuid",
      "file_path": "string",
      "code_snippet": "string",
      "similarity_score": "float",
      "context": "string"
    }
  ],
  "total_results": "integer"
}
```

### 12. Find Similar Code
**POST** `/kenobi/repositories/{repository_id}/similar`
- **Description**: Find similar code patterns within repository
- **Parameters**:
  - `repository_id` (path): Repository UUID
- **Request Body**:
```json
{
  "code_snippet": "string",
  "similarity_threshold": "float",
  "max_results": "integer"
}
```
- **Response**:
```json
{
  "query_code": "string",
  "similar_patterns": [
    {
      "file_path": "string",
      "code_snippet": "string",
      "similarity_score": "float",
      "line_numbers": [1, 10]
    }
  ]
}
```

---

## 📈 PHASE 4: ADVANCED ANALYTICS & MONITORING

### 13. Comprehensive Repository Analysis
**POST** `/kenobi/repositories/comprehensive-analysis`
- **Description**: Complete multi-dimensional repository analysis
- **Request Body**:
```json
{
  "repository_path": "string",
  "repository_name": "string",
  "analysis_types": ["string"]  // Optional: specific analysis types
}
```
- **Response**:
```json
{
  "repository_name": "string",
  "repository_path": "string",
  "overall_health_score": "float",
  "analysis_results": {
    "security_analysis": {
      "security_score": "float",
      "vulnerabilities": [],
      "security_recommendations": []
    },
    "performance_analysis": {
      "performance_score": "float",
      "bottlenecks": [],
      "optimization_suggestions": []
    },
    "code_quality": {
      "quality_score": "float",
      "maintainability": "float",
      "complexity_metrics": {}
    },
    "test_coverage": {
      "coverage_percentage": "float",
      "test_files": [],
      "coverage_recommendations": []
    },
    "documentation_analysis": {
      "documentation_score": "float",
      "missing_docs": [],
      "documentation_quality": {}
    },
    "dependency_analysis": {
      "dependency_health": "float",
      "outdated_dependencies": [],
      "security_vulnerabilities": []
    },
    "architecture_analysis": {
      "architecture_score": "float",
      "design_patterns": [],
      "architectural_issues": []
    },
    "ai_insights": {
      "ai_recommendations": [],
      "code_patterns": [],
      "refactoring_opportunities": []
    }
  },
  "recommendations": [],
  "analysis_timestamp": "datetime"
}
```

### 14. Repository Health Monitoring
**GET** `/kenobi/repositories/{repository_id}/health`
- **Description**: Real-time health monitoring for repository
- **Parameters**:
  - `repository_id` (path): Repository UUID
- **Response**:
```json
{
  "repository_id": "uuid",
  "overall_health_score": "float",
  "health_metrics": {
    "code_quality": "float",
    "security_score": "float",
    "performance_score": "float",
    "test_coverage": "float",
    "documentation_score": "float",
    "dependency_health": "float"
  },
  "alerts": [],
  "last_updated": "datetime",
  "trend_analysis": {
    "improving_metrics": [],
    "declining_metrics": [],
    "stable_metrics": []
  }
}
```

### 15. Batch Repository Analysis
**POST** `/kenobi/repositories/batch-analysis`
- **Description**: Analyze multiple repositories in batch
- **Request Body**:
```json
{
  "repository_paths": ["string"],
  "analysis_types": ["string"],
  "parallel_processing": "boolean"
}
```
- **Response**:
```json
{
  "batch_id": "uuid",
  "total_repositories": "integer",
  "completed_analyses": "integer",
  "failed_analyses": "integer",
  "results": [
    {
      "repository_path": "string",
      "status": "string",
      "analysis_summary": {},
      "processing_time": "float"
    }
  ],
  "batch_summary": {
    "average_health_score": "float",
    "total_issues_found": "integer",
    "common_patterns": []
  }
}
```

### 16. Repository Comparison
**POST** `/kenobi/repositories/compare`
- **Description**: Compare multiple repositories across various metrics
- **Request Body**:
```json
{
  "repository_ids": ["uuid"],
  "comparison_aspects": ["string"]  // Optional: specific aspects to compare
}
```
- **Response**:
```json
{
  "repository_1": {
    "id": "uuid",
    "name": "string",
    "path": "string"
  },
  "repository_2": {
    "id": "uuid",
    "name": "string",
    "path": "string"
  },
  "comparison_results": {
    "structure": {
      "repository_1": {
        "total_files": "integer",
        "python_files": "integer",
        "directories": "integer"
      },
      "repository_2": {
        "total_files": "integer",
        "python_files": "integer",
        "directories": "integer"
      }
    },
    "quality": {
      "repository_1": {"estimated_quality_score": "float"},
      "repository_2": {"estimated_quality_score": "float"}
    },
    "dependencies": {
      "repository_1": {
        "external_dependencies": "integer",
        "internal_modules": "integer"
      },
      "repository_2": {
        "external_dependencies": "integer",
        "internal_modules": "integer"
      }
    },
    "complexity": {
      "repository_1": {"complexity_score": "float"},
      "repository_2": {"complexity_score": "float"}
    }
  },
  "summary": {
    "larger_repository": "string",
    "more_complex": "string",
    "higher_quality": "string"
  },
  "comparison_timestamp": "datetime",
  "comparison_aspects": ["string"]
}
```

### 17. Repository Insights Generation
**GET** `/kenobi/repositories/{repository_id}/insights`
- **Description**: Generate actionable insights for repository improvement
- **Parameters**:
  - `repository_id` (path): Repository UUID
- **Query Parameters**:
  - `insight_types` (optional): Comma-separated list of insight types
- **Response**:
```json
{
  "repository_id": "uuid",
  "repository_name": "string",
  "insights": {
    "optimization_insights": [
      {
        "category": "string",
        "priority": "string",
        "description": "string",
        "impact": "string",
        "effort": "string",
        "files_affected": ["string"]
      }
    ],
    "refactoring_insights": [],
    "testing_insights": [],
    "documentation_insights": [],
    "security_insights": []
  },
  "summary": {
    "total_insights": "integer",
    "high_priority_count": "integer",
    "estimated_improvement_score": "float"
  },
  "generated_at": "datetime"
}
```

---

## 📊 DASHBOARD & ANALYTICS ENDPOINTS

### 18. Dashboard Overview
**GET** `/dashboard/overview`
- **Description**: Get comprehensive dashboard overview
- **Parameters**: None
- **Response**:
```json
{
  "total_repositories": "integer",
  "total_analyses": "integer",
  "average_health_score": "float",
  "recent_activity": [],
  "top_repositories": [],
  "system_metrics": {
    "uptime": "string",
    "memory_usage": "float",
    "cpu_usage": "float"
  },
  "alerts": []
}
```

### 19. Repository Analytics
**GET** `/dashboard/repositories/{repository_id}/analytics`
- **Description**: Detailed analytics for specific repository
- **Parameters**:
  - `repository_id` (path): Repository UUID
- **Response**:
```json
{
  "repository_id": "uuid",
  "analytics": {
    "quality_trends": [],
    "issue_trends": [],
    "performance_metrics": {},
    "activity_timeline": []
  },
  "insights": [],
  "recommendations": []
}
```

### 20. Quality Trends
**GET** `/dashboard/quality-trends`
- **Description**: Get quality trends across all repositories
- **Query Parameters**:
  - `time_range` (optional): Time range for trends (7d, 30d, 90d)
- **Response**:
```json
{
  "time_range": "string",
  "trends": {
    "overall_quality": [],
    "security_trends": [],
    "performance_trends": [],
    "test_coverage_trends": []
  },
  "summary": {
    "improving_repositories": "integer",
    "declining_repositories": "integer",
    "stable_repositories": "integer"
  }
}
```

---

## ⚡ PERFORMANCE & CACHING ENDPOINTS

### 21. Cache Statistics
**GET** `/cache/stats`
- **Description**: Get cache performance statistics
- **Parameters**: None
- **Response**:
```json
{
  "cache_type": "string",
  "total_keys": "integer",
  "hit_rate": "float",
  "miss_rate": "float",
  "memory_usage": "string",
  "uptime": "string"
}
```

### 22. Clear Cache
**DELETE** `/cache/clear`
- **Description**: Clear all cached data
- **Query Parameters**:
  - `pattern` (optional): Pattern to match for selective clearing
- **Response**:
```json
{
  "message": "Cache cleared successfully",
  "keys_cleared": "integer",
  "timestamp": "datetime"
}
```

### 23. Cache Health
**GET** `/cache/health`
- **Description**: Check cache service health
- **Parameters**: None
- **Response**:
```json
{
  "status": "string",
  "redis_connected": "boolean",
  "fallback_active": "boolean",
  "response_time": "float"
}
```

---

## 🔧 MONITORING & SYSTEM ENDPOINTS

### 24. System Health
**GET** `/monitoring/health`
- **Description**: Comprehensive system health check
- **Parameters**: None
- **Response**:
```json
{
  "status": "string",
  "services": {
    "database": "string",
    "cache": "string",
    "vector_store": "string",
    "ai_engine": "string"
  },
  "metrics": {
    "uptime": "string",
    "memory_usage": "float",
    "cpu_usage": "float",
    "disk_usage": "float"
  },
  "timestamp": "datetime"
}
```

### 25. Performance Metrics
**GET** `/monitoring/metrics`
- **Description**: Get detailed performance metrics
- **Query Parameters**:
  - `time_range` (optional): Time range for metrics
- **Response**:
```json
{
  "time_range": "string",
  "metrics": {
    "api_response_times": {},
    "analysis_performance": {},
    "cache_performance": {},
    "resource_utilization": {}
  },
  "alerts": [],
  "recommendations": []
}
```

### 26. System Alerts
**GET** `/monitoring/alerts`
- **Description**: Get current system alerts
- **Parameters**: None
- **Response**:
```json
{
  "active_alerts": [
    {
      "id": "uuid",
      "severity": "string",
      "message": "string",
      "timestamp": "datetime",
      "source": "string"
    }
  ],
  "alert_summary": {
    "critical": "integer",
    "warning": "integer",
    "info": "integer"
  }
}
```

---

## 🎯 ADVANCED ANALYSIS ENDPOINTS

### 27. Dependency Analysis
**GET** `/analysis/repositories/{repository_id}/dependencies`
- **Description**: Comprehensive dependency analysis
- **Parameters**:
  - `repository_id` (path): Repository UUID
- **Response**:
```json
{
  "repository_id": "uuid",
  "dependency_analysis": {
    "external_dependencies": [],
    "internal_dependencies": [],
    "circular_dependencies": [],
    "outdated_dependencies": [],
    "security_vulnerabilities": []
  },
  "dependency_graph": {},
  "recommendations": []
}
```

### 28. Cross-Repository Dependencies
**POST** `/analysis/cross-repository-dependencies`
- **Description**: Analyze dependencies across multiple repositories
- **Request Body**:
```json
{
  "repository_ids": ["uuid"]
}
```
- **Response**:
```json
{
  "analysis_id": "uuid",
  "repositories": ["uuid"],
  "cross_dependencies": [],
  "shared_dependencies": [],
  "dependency_conflicts": [],
  "recommendations": []
}
```

---

## 📝 ERROR RESPONSES

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error message describing the bad request"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

---

## 🚀 USAGE EXAMPLES

### Example 1: Index and Analyze Repository
```bash
# 1. Index repository
curl -X POST http://localhost:8080/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repo", "name": "my-repo"}'

# 2. Get comprehensive analysis
curl -X POST http://localhost:8080/kenobi/repositories/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo", "repository_name": "my-repo"}'
```

### Example 2: Monitor Repository Health
```bash
# Get repository health
curl -X GET http://localhost:8080/kenobi/repositories/{repo-id}/health

# Get insights
curl -X GET http://localhost:8080/kenobi/repositories/{repo-id}/insights
```

### Example 3: Compare Repositories
```bash
curl -X POST http://localhost:8080/kenobi/repositories/compare \
  -H "Content-Type: application/json" \
  -d '{"repository_ids": ["repo-id-1", "repo-id-2"]}'
```

---

## 📊 IMPLEMENTATION STATUS

✅ **Phase 1**: Core Repository Management (6 endpoints)
✅ **Phase 2**: Code Analysis & AI Integration (6 endpoints)  
✅ **Phase 3**: Vector Search & Advanced Analysis (6 endpoints)
✅ **Phase 4**: Analytics, Monitoring & Production Features (10+ endpoints)

**Total Endpoints**: 28+ fully implemented and tested
**Production Ready**: ✅ All endpoints operational
**Documentation**: ✅ Complete API documentation
**Testing**: ✅ Comprehensive testing completed

---

*Last Updated: June 27, 2025*
*Version: 4.0.0 - Production Ready*