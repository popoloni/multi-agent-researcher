# Complete API Reference - Multi-Agent Research System

**Version**: Phase 4 Complete  
**Total Endpoints**: 61  
**Base URL**: `http://localhost:8080`  
**Generated**: June 27, 2025  

---

## 📊 API Overview

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Core Services** | 21 | Basic repository operations and system functions |
| **Repository Management** | 13 | Advanced repository analysis and management |
| **AI Analysis** | 4 | AI-powered code analysis and generation |
| **Advanced Analysis** | 5 | Cross-repository and dependency analysis |
| **Dashboard & Monitoring** | 6 | Real-time monitoring and visualization |
| **Quality Analysis** | 4 | Code quality assessment and trends |
| **Vector Operations** | 3 | Semantic search and similarity analysis |
| **Cache Management** | 2 | Cache performance and management |
| **Analytics** | 2 | System performance analytics |
| **Code Analysis** | 1 | Individual file analysis |

---

## 🔧 Core Services (21 Endpoints)

### 1. System Root
```http
GET /
```
**Description**: Welcome message and system status  
**Parameters**: None  
**Response**: System information and available services  

**Example Response**:
```json
{
  "message": "Multi-Agent Research System",
  "version": "Phase 4",
  "status": "operational",
  "endpoints": 61
}
```

### 2. Index Repository
```http
POST /repositories/index
```
**Description**: Index a repository for analysis  
**Content-Type**: `application/json`  

**Request Body**:
```json
{
  "path": "string (required)",
  "name": "string (required)"
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "name": "string",
  "path": "string",
  "indexed_at": "datetime",
  "file_count": "number",
  "element_count": "number"
}
```

### 3. List All Repositories
```http
GET /repositories
```
**Description**: Get all indexed repositories  
**Parameters**: None  

**Response**:
```json
[
  {
    "repository_id": "uuid",
    "name": "string",
    "path": "string",
    "indexed_at": "datetime",
    "file_count": "number"
  }
]
```

### 4. Get Repository Details
```http
GET /repositories/{repository_id}
```
**Description**: Get detailed repository information  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "name": "string",
  "path": "string",
  "metadata": {
    "language": "string",
    "framework": "string",
    "size": "number"
  },
  "statistics": {
    "files": "number",
    "lines_of_code": "number",
    "complexity": "number"
  }
}
```

### 5. Delete Repository
```http
DELETE /repositories/{repository_id}
```
**Description**: Remove repository from system  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "message": "Repository deleted successfully",
  "repository_id": "uuid"
}
```

### 6. Get Repository Files
```http
GET /repositories/{repository_id}/files
```
**Description**: List all files in repository  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "files": [
    {
      "path": "string",
      "type": "string",
      "size": "number",
      "language": "string"
    }
  ],
  "total_files": "number"
}
```

### 7. Repository Statistics
```http
GET /repositories/{repository_id}/stats
```
**Description**: Get repository statistics and metrics  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "statistics": {
    "total_files": "number",
    "total_lines": "number",
    "languages": ["string"],
    "complexity_score": "number",
    "maintainability_index": "number"
  }
}
```

### 8. Repository Code Elements
```http
GET /repositories/{repository_id}/elements
```
**Description**: Get code elements and structure  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "elements": [
    {
      "id": "string",
      "type": "string",
      "name": "string",
      "file_path": "string",
      "line_number": "number"
    }
  ],
  "total_elements": "number"
}
```

### 9. Repository Dependencies
```http
GET /repositories/{repository_id}/dependencies
```
**Description**: Get dependency analysis and graph  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "dependencies": {
    "external": ["string"],
    "internal": ["string"],
    "graph": {
      "nodes": ["string"],
      "edges": [["string", "string"]]
    }
  }
}
```

### 10. Repository Clusters
```http
GET /repositories/{repository_id}/clusters
```
**Description**: Get code clustering analysis  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "clusters": [
    {
      "cluster_id": "number",
      "elements": ["string"],
      "centroid": "string",
      "similarity_score": "number"
    }
  ]
}
```

### 11. Repository Patterns
```http
GET /repositories/{repository_id}/patterns
```
**Description**: Detect design patterns and anti-patterns  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "patterns": {
    "design_patterns": [
      {
        "pattern": "string",
        "instances": ["string"],
        "confidence": "number"
      }
    ],
    "anti_patterns": [
      {
        "pattern": "string",
        "instances": ["string"],
        "severity": "string"
      }
    ]
  }
}
```

### 12. Repository Metrics
```http
GET /repositories/{repository_id}/metrics
```
**Description**: Get comprehensive code quality metrics  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "metrics": {
    "complexity": "number",
    "maintainability": "number",
    "readability": "number",
    "test_coverage": "number",
    "documentation": "number"
  },
  "overall_score": "number",
  "grade": "string"
}
```

### 13. Repository Summary
```http
GET /repositories/{repository_id}/summary
```
**Description**: Get executive summary of repository  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "summary": {
    "overview": "string",
    "key_metrics": {},
    "recommendations": ["string"],
    "health_score": "number"
  }
}
```

### 14. File Analysis
```http
GET /repositories/{repository_id}/files/{file_path:path}
```
**Description**: Analyze individual file in detail  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID
- `file_path` (string, required): File path within repository

**Response**:
```json
{
  "file_path": "string",
  "analysis": {
    "complexity": "number",
    "quality_score": "number",
    "issues": ["string"],
    "suggestions": ["string"]
  }
}
```

### 15. Search Repositories
```http
GET /repositories/search
```
**Description**: Search and filter repositories  

**Query Parameters**:
- `query` (string, optional): Search query
- `language` (string, optional): Programming language filter
- `min_quality` (number, optional): Minimum quality score

**Response**:
```json
{
  "results": [
    {
      "repository_id": "uuid",
      "name": "string",
      "relevance_score": "number"
    }
  ],
  "total_results": "number"
}
```

### 16. Repository Health Check
```http
GET /repositories/{repository_id}/health
```
**Description**: Get repository health status  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "health": {
    "status": "string",
    "score": "number",
    "issues": ["string"],
    "recommendations": ["string"]
  }
}
```

### 17. Repository Trends
```http
GET /repositories/{repository_id}/trends
```
**Description**: Get quality and metric trends  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Query Parameters**:
- `days` (number, optional): Time window in days (default: 30)

**Response**:
```json
{
  "repository_id": "uuid",
  "trends": {
    "quality_trend": [
      {
        "date": "string",
        "score": "number"
      }
    ],
    "complexity_trend": [],
    "overall_direction": "string"
  }
}
```

### 18. Compare Repositories
```http
POST /repositories/compare
```
**Description**: Compare multiple repositories  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "repository_ids": ["uuid", "uuid"],
  "comparison_aspects": ["string"]
}
```

**Response**:
```json
{
  "comparison": {
    "repositories": [
      {
        "id": "uuid",
        "metrics": {}
      }
    ],
    "differences": {},
    "recommendations": ["string"]
  }
}
```

### 19. Bulk Repository Operations
```http
POST /repositories/bulk
```
**Description**: Perform bulk operations on repositories  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "operation": "string",
  "repository_ids": ["uuid"],
  "parameters": {}
}
```

**Response**:
```json
{
  "operation": "string",
  "results": [
    {
      "repository_id": "uuid",
      "status": "string",
      "result": {}
    }
  ]
}
```

### 20. Export Repository Data
```http
GET /repositories/{repository_id}/export
```
**Description**: Export repository data in various formats  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Query Parameters**:
- `format` (string, optional): Export format (json, csv, xml)

**Response**: Repository data in requested format

### 21. System Health Check
```http
GET /health
```
**Description**: System health and status check  
**Parameters**: None

**Response**:
```json
{
  "status": "healthy",
  "uptime": "string",
  "version": "string",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "ai_engine": "healthy"
  }
}
```

---

## 📁 Repository Management (13 Endpoints)

### 1. Kenobi Repository Index
```http
POST /kenobi/repositories/index
```
**Description**: Index repository with Kenobi agent  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "path": "string (required)",
  "name": "string (required)"
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "name": "string",
  "path": "string",
  "indexed_at": "datetime",
  "kenobi_analysis": {
    "initial_score": "number",
    "elements_processed": "number"
  }
}
```

### 2. Repository Health Monitoring
```http
GET /kenobi/repositories/{repository_id}/health
```
**Description**: Comprehensive health analysis with Kenobi  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "health_analysis": {
    "overall_health_score": "number",
    "security_score": "number",
    "performance_score": "number",
    "maintainability_score": "number",
    "recommendations": ["string"],
    "critical_issues": ["string"]
  },
  "analysis_timestamp": "datetime"
}
```

### 3. Repository Insights
```http
GET /kenobi/repositories/{repository_id}/insights
```
**Description**: Generate actionable optimization insights  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "repository_name": "string",
  "insights": {
    "optimization": {
      "performance_improvements": ["string"],
      "code_optimizations": ["string"]
    },
    "refactoring": {
      "suggested_refactors": ["string"],
      "priority_areas": ["string"]
    },
    "testing": {
      "coverage_gaps": ["string"],
      "test_suggestions": ["string"]
    },
    "documentation": {
      "missing_docs": ["string"],
      "improvement_areas": ["string"]
    },
    "security": {
      "vulnerabilities": ["string"],
      "security_improvements": ["string"]
    }
  },
  "generated_at": "datetime"
}
```

### 4. Comprehensive Analysis
```http
POST /kenobi/repositories/comprehensive-analysis
```
**Description**: Full repository analysis with all metrics  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "repository_path": "string (required)",
  "repository_name": "string (required)",
  "analysis_types": ["security", "performance", "quality", "dependencies"]
}
```

**Response**:
```json
{
  "repository_path": "string",
  "repository_name": "string",
  "overall_health_score": "number",
  "analysis_timestamp": "datetime",
  "security_analysis": {
    "score": "number",
    "vulnerabilities": ["string"],
    "recommendations": ["string"]
  },
  "performance_analysis": {
    "score": "number",
    "bottlenecks": ["string"],
    "optimizations": ["string"]
  },
  "quality_analysis": {
    "score": "number",
    "issues": ["string"],
    "grade": "string"
  },
  "dependency_analysis": {
    "external_deps": "number",
    "internal_deps": "number",
    "circular_deps": ["string"]
  }
}
```

### 5. Batch Analysis
```http
POST /kenobi/repositories/batch-analysis
```
**Description**: Analyze multiple repositories in batch  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "repository_paths": ["string"],
  "analysis_types": ["security", "performance", "quality"]
}
```

**Response**:
```json
{
  "batch_id": "uuid",
  "total_repositories": "number",
  "completed_repositories": "number",
  "results": [
    {
      "repository_path": "string",
      "status": "string",
      "health_score": "number",
      "analysis_summary": {}
    }
  ],
  "batch_timestamp": "datetime"
}
```

### 6. Repository Comparison
```http
POST /kenobi/repositories/compare
```
**Description**: Compare multiple repositories across dimensions  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "repository_ids": ["uuid", "uuid"],
  "comparison_aspects": ["structure", "quality", "dependencies", "complexity"]
}
```

**Response**:
```json
{
  "comparison_timestamp": "datetime",
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
      "repository_1": {"total_files": "number"},
      "repository_2": {"total_files": "number"}
    },
    "quality": {
      "repository_1": {"score": "number"},
      "repository_2": {"score": "number"}
    }
  },
  "summary": {
    "larger_repository": "string",
    "higher_quality": "string",
    "more_complex": "string"
  }
}
```

### 7. Repository Optimization
```http
POST /kenobi/repositories/{repository_id}/optimize
```
**Description**: Get optimization recommendations  
**Content-Type**: `application/json`

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Request Body**:
```json
{
  "optimization_types": ["performance", "memory", "security"]
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "optimizations": [
    {
      "type": "string",
      "description": "string",
      "impact": "string",
      "effort": "string"
    }
  ]
}
```

### 8. Repository Refactoring
```http
POST /kenobi/repositories/{repository_id}/refactor
```
**Description**: Get refactoring suggestions  
**Content-Type**: `application/json`

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Request Body**:
```json
{
  "refactoring_scope": "string",
  "target_patterns": ["string"]
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "refactoring_suggestions": [
    {
      "file": "string",
      "suggestion": "string",
      "reason": "string",
      "priority": "string"
    }
  ]
}
```

### 9. Repository Testing
```http
POST /kenobi/repositories/{repository_id}/testing
```
**Description**: Get testing recommendations  
**Content-Type**: `application/json`

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Request Body**:
```json
{
  "test_types": ["unit", "integration", "e2e"],
  "coverage_target": 80
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "testing_recommendations": {
    "missing_tests": ["string"],
    "coverage_gaps": ["string"],
    "test_suggestions": ["string"]
  }
}
```

### 10. Repository Documentation
```http
POST /kenobi/repositories/{repository_id}/documentation
```
**Description**: Get documentation suggestions  
**Content-Type**: `application/json`

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Request Body**:
```json
{
  "doc_types": ["api", "readme", "inline"],
  "format": "markdown"
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "documentation_suggestions": {
    "missing_docs": ["string"],
    "improvement_areas": ["string"],
    "generated_docs": ["string"]
  }
}
```

### 11. Repository Security
```http
POST /kenobi/repositories/{repository_id}/security
```
**Description**: Security analysis and recommendations  
**Content-Type**: `application/json`

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Request Body**:
```json
{
  "security_checks": ["vulnerabilities", "secrets", "dependencies"]
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "security_analysis": {
    "vulnerabilities": ["string"],
    "security_score": "number",
    "recommendations": ["string"],
    "critical_issues": ["string"]
  }
}
```

### 12. Repository Performance
```http
POST /kenobi/repositories/{repository_id}/performance
```
**Description**: Performance analysis and optimization  
**Content-Type**: `application/json`

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Request Body**:
```json
{
  "performance_metrics": ["speed", "memory", "scalability"]
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "performance_analysis": {
    "bottlenecks": ["string"],
    "optimizations": ["string"],
    "performance_score": "number"
  }
}
```

### 13. Repository Migration
```http
POST /kenobi/repositories/{repository_id}/migration
```
**Description**: Migration planning and recommendations  
**Content-Type**: `application/json`

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Request Body**:
```json
{
  "target_framework": "string",
  "migration_strategy": "string"
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "migration_plan": {
    "steps": ["string"],
    "risks": ["string"],
    "timeline": "string",
    "effort_estimate": "string"
  }
}
```

---

## 🤖 AI Analysis (4 Endpoints)

### 1. AI Code Analysis
```http
POST /kenobi/ai/analyze-code
```
**Description**: AI-powered code analysis  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "code": "string (required)",
  "language": "string (required)",
  "analysis_type": "string"
}
```

**Response**:
```json
{
  "analysis": {
    "complexity": "number",
    "quality_score": "number",
    "issues": ["string"],
    "suggestions": ["string"],
    "patterns": ["string"]
  },
  "ai_confidence": "number"
}
```

### 2. AI Code Explanation
```http
POST /kenobi/ai/explain-code
```
**Description**: Generate AI-powered code explanations  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "code": "string (required)",
  "language": "string (required)",
  "detail_level": "basic|detailed|expert"
}
```

**Response**:
```json
{
  "explanation": {
    "summary": "string",
    "detailed_explanation": "string",
    "key_concepts": ["string"],
    "examples": ["string"]
  }
}
```

### 3. AI Test Generation
```http
POST /kenobi/ai/generate-tests
```
**Description**: Generate unit tests using AI  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "code": "string (required)",
  "language": "string (required)",
  "test_framework": "string"
}
```

**Response**:
```json
{
  "generated_tests": [
    {
      "test_name": "string",
      "test_code": "string",
      "description": "string",
      "coverage_area": "string"
    }
  ],
  "coverage_estimate": "number"
}
```

### 4. AI Code Improvements
```http
POST /kenobi/ai/suggest-improvements
```
**Description**: AI-powered improvement suggestions  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "code": "string (required)",
  "language": "string (required)",
  "focus_areas": ["performance", "readability", "security"]
}
```

**Response**:
```json
{
  "improvements": [
    {
      "area": "string",
      "suggestion": "string",
      "improved_code": "string",
      "impact": "string",
      "confidence": "number"
    }
  ]
}
```

---

## 🔬 Advanced Analysis (5 Endpoints)

### 1. Cross-Repository Dependencies
```http
POST /kenobi/analysis/cross-repository-dependencies
```
**Description**: Analyze dependencies across multiple repositories  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "repository_ids": ["uuid", "uuid"]
}
```

**Response**:
```json
{
  "cross_dependencies": {
    "shared_dependencies": ["string"],
    "dependency_conflicts": ["string"],
    "optimization_opportunities": ["string"]
  },
  "dependency_graph": {
    "nodes": ["string"],
    "edges": [["string", "string"]]
  }
}
```

### 2. Dependency Health Assessment
```http
GET /kenobi/analysis/dependency-health/{repository_id}
```
**Description**: Assess health of repository dependencies  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "dependency_health": {
    "overall_score": "number",
    "outdated_dependencies": ["string"],
    "security_vulnerabilities": ["string"],
    "recommendations": ["string"]
  }
}
```

### 3. Dependency Impact Assessment
```http
POST /kenobi/analysis/dependency-impact
```
**Description**: Assess impact of dependency changes  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "repository_id": "uuid",
  "dependency_changes": [
    {
      "dependency": "string",
      "action": "add|remove|update",
      "version": "string"
    }
  ]
}
```

**Response**:
```json
{
  "impact_analysis": {
    "affected_components": ["string"],
    "risk_level": "string",
    "breaking_changes": ["string"],
    "recommendations": ["string"]
  }
}
```

### 4. Dependency Patterns
```http
GET /kenobi/analysis/dependency-patterns/{repository_id}
```
**Description**: Analyze dependency patterns and anti-patterns  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "patterns": {
    "circular_dependencies": ["string"],
    "unused_dependencies": ["string"],
    "dependency_clusters": ["string"],
    "optimization_suggestions": ["string"]
  }
}
```

### 5. Repository Comprehensive Analysis
```http
POST /kenobi/analysis/repository-comprehensive
```
**Description**: Comprehensive repository analysis  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "repository_path": "string (required)",
  "analysis_depth": "basic|standard|deep"
}
```

**Response**:
```json
{
  "comprehensive_analysis": {
    "code_quality": {},
    "security_assessment": {},
    "performance_analysis": {},
    "dependency_analysis": {},
    "architecture_analysis": {},
    "recommendations": ["string"]
  }
}
```

---

## 📊 Dashboard & Monitoring (6 Endpoints)

### 1. Dashboard Overview
```http
GET /kenobi/dashboard/overview
```
**Description**: System overview dashboard  
**Parameters**: None

**Response**:
```json
{
  "timestamp": "datetime",
  "system_health": {
    "status": "healthy|warning|critical",
    "score": "number",
    "uptime_hours": "number",
    "avg_response_time": "number",
    "error_rate": "number"
  },
  "repository_summary": {
    "total_repositories": "number",
    "total_code_elements": "number",
    "supported_languages": "number",
    "languages": ["string"],
    "avg_elements_per_repo": "number"
  },
  "quality_overview": {
    "average_quality_score": "number",
    "total_quality_issues": "number",
    "elements_analyzed": "number",
    "quality_grade": "string"
  },
  "performance_metrics": {
    "avg_response_time": "number",
    "max_response_time": "number",
    "p95_response_time": "number",
    "throughput": "number",
    "error_rate": "number"
  },
  "recent_activity": ["string"],
  "alerts": ["string"]
}
```

### 2. Repository Dashboard
```http
GET /kenobi/dashboard/repository/{repository_id}
```
**Description**: Repository-specific dashboard  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "repository_name": "string",
  "dashboard_data": {
    "health_score": "number",
    "quality_metrics": {},
    "recent_changes": ["string"],
    "alerts": ["string"],
    "trends": {}
  }
}
```

### 3. Quality Dashboard
```http
GET /kenobi/dashboard/quality
```
**Description**: Quality metrics dashboard  
**Parameters**: None

**Response**:
```json
{
  "quality_overview": {
    "average_score": "number",
    "distribution": {},
    "trends": {},
    "top_issues": ["string"]
  },
  "repository_rankings": [
    {
      "repository_id": "uuid",
      "name": "string",
      "quality_score": "number"
    }
  ]
}
```

### 4. Dependencies Dashboard
```http
GET /kenobi/dashboard/dependencies
```
**Description**: Dependency visualization dashboard  
**Parameters**: None

**Response**:
```json
{
  "dependency_overview": {
    "total_dependencies": "number",
    "outdated_count": "number",
    "vulnerable_count": "number",
    "most_used": ["string"]
  },
  "dependency_graph": {
    "nodes": ["string"],
    "edges": [["string", "string"]]
  }
}
```

### 5. Real-time Dashboard
```http
GET /kenobi/dashboard/real-time
```
**Description**: Real-time system monitoring  
**Parameters**: None

**Response**:
```json
{
  "timestamp": "datetime",
  "live_metrics": {
    "active_requests": "number",
    "response_time": "number",
    "memory_usage": "number",
    "cpu_usage": "number"
  },
  "recent_events": ["string"],
  "system_alerts": ["string"]
}
```

### 6. Performance Dashboard
```http
GET /kenobi/dashboard/performance
```
**Description**: Performance monitoring dashboard  
**Parameters**: None

**Response**:
```json
{
  "performance_overview": {
    "avg_response_time": "number",
    "throughput": "number",
    "error_rate": "number",
    "uptime": "number"
  },
  "performance_trends": {},
  "bottlenecks": ["string"]
}
```

---

## 🔍 Quality Analysis (4 Endpoints)

### 1. Quality Assessment
```http
POST /kenobi/quality/assess
```
**Description**: Comprehensive quality assessment  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "repository_id": "uuid",
  "quality_metrics": ["complexity", "maintainability", "readability"]
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "quality_assessment": {
    "overall_score": "number",
    "grade": "string",
    "metrics": {
      "complexity": "number",
      "maintainability": "number",
      "readability": "number"
    },
    "issues": ["string"],
    "recommendations": ["string"]
  }
}
```

### 2. Quality Trends
```http
GET /kenobi/quality/trends/{repository_id}
```
**Description**: Quality trend analysis  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Query Parameters**:
- `time_window` (string, optional): Time window (7d, 30d, 90d)

**Response**:
```json
{
  "repository_id": "uuid",
  "trends": {
    "quality_trend": [
      {
        "date": "string",
        "score": "number"
      }
    ],
    "trend_direction": "improving|declining|stable",
    "key_changes": ["string"]
  }
}
```

### 3. Quality Comparison
```http
POST /kenobi/quality/compare
```
**Description**: Compare quality across repositories  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "repository_ids": ["uuid", "uuid"]
}
```

**Response**:
```json
{
  "comparison": {
    "repositories": [
      {
        "id": "uuid",
        "name": "string",
        "quality_score": "number"
      }
    ],
    "best_practices": ["string"],
    "improvement_areas": ["string"]
  }
}
```

### 4. Quality Recommendations
```http
GET /kenobi/quality/recommendations/{repository_id}
```
**Description**: Quality improvement recommendations  

**Path Parameters**:
- `repository_id` (string, required): Repository UUID

**Response**:
```json
{
  "repository_id": "uuid",
  "recommendations": [
    {
      "category": "string",
      "recommendation": "string",
      "impact": "string",
      "effort": "string",
      "priority": "string"
    }
  ]
}
```

---

## 🧮 Vector Operations (3 Endpoints)

### 1. Vector Search
```http
POST /kenobi/vector/search
```
**Description**: Semantic code search using vectors  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "query": "string (required)",
  "repository_id": "uuid",
  "limit": 10
}
```

**Response**:
```json
{
  "query": "string",
  "results": [
    {
      "element_id": "string",
      "similarity_score": "number",
      "code_snippet": "string",
      "file_path": "string"
    }
  ]
}
```

### 2. Vector Similarity
```http
POST /kenobi/vector/similarity
```
**Description**: Find similar code elements  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "code_element_id": "string (required)",
  "threshold": 0.8
}
```

**Response**:
```json
{
  "source_element": "string",
  "similar_elements": [
    {
      "element_id": "string",
      "similarity_score": "number",
      "code_snippet": "string"
    }
  ]
}
```

### 3. Vector Clustering
```http
POST /kenobi/vector/cluster
```
**Description**: Cluster code elements by similarity  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "repository_id": "uuid (required)",
  "cluster_count": 5
}
```

**Response**:
```json
{
  "repository_id": "uuid",
  "clusters": [
    {
      "cluster_id": "number",
      "elements": ["string"],
      "centroid_description": "string",
      "similarity_threshold": "number"
    }
  ]
}
```

---

## 🗄️ Cache Management (2 Endpoints)

### 1. Cache Statistics
```http
GET /kenobi/cache/stats
```
**Description**: Cache performance statistics  
**Parameters**: None

**Response**:
```json
{
  "service_stats": {
    "hits": "number",
    "misses": "number",
    "sets": "number",
    "deletes": "number",
    "errors": "number"
  },
  "redis_enabled": "boolean",
  "redis_available": "boolean",
  "memory_stats": {
    "total_entries": "number",
    "expired_entries": "number",
    "active_entries": "number",
    "total_accesses": "number",
    "cache_type": "string",
    "max_size": "number"
  },
  "hit_rate": "number"
}
```

### 2. Clear Cache
```http
POST /kenobi/cache/clear
```
**Description**: Clear cache entries  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "cache_type": "all|redis|memory",
  "pattern": "string"
}
```

**Response**:
```json
{
  "cleared": "boolean",
  "entries_cleared": "number",
  "cache_type": "string"
}
```

---

## 📈 Analytics (2 Endpoints)

### 1. System Metrics
```http
GET /kenobi/analytics/metrics
```
**Description**: System performance metrics  
**Parameters**: None

**Response**:
```json
{
  "metrics": {
    "response_times": {
      "avg": "number",
      "p50": "number",
      "p95": "number",
      "p99": "number"
    },
    "throughput": "number",
    "error_rates": {
      "total": "number",
      "by_endpoint": {}
    },
    "resource_usage": {
      "memory": "number",
      "cpu": "number"
    }
  }
}
```

### 2. Real-time Analytics
```http
GET /kenobi/analytics/real-time
```
**Description**: Real-time system analytics  
**Parameters**: None

**Response**:
```json
{
  "timestamp": "datetime",
  "real_time_data": {
    "active_connections": "number",
    "requests_per_second": "number",
    "current_response_time": "number",
    "memory_usage": "number"
  },
  "alerts": ["string"]
}
```

---

## 🔍 Code Analysis (1 Endpoint)

### 1. File Analysis
```http
POST /kenobi/analyze/file
```
**Description**: Analyze individual file  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "file_path": "string (required)",
  "repository_id": "uuid (required)",
  "analysis_types": ["complexity", "quality", "security"]
}
```

**Response**:
```json
{
  "file_path": "string",
  "repository_id": "uuid",
  "analysis": {
    "complexity": {
      "cyclomatic_complexity": "number",
      "cognitive_complexity": "number"
    },
    "quality": {
      "score": "number",
      "issues": ["string"]
    },
    "security": {
      "vulnerabilities": ["string"],
      "risk_level": "string"
    }
  }
}
```

---

## 🔐 Authentication & Security

### API Key Authentication (Optional)
```http
X-API-Key: your-api-key-here
```

### Rate Limiting
- **Default**: 100 requests/minute per IP
- **Authenticated**: 1000 requests/minute per API key

### Response Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## 📊 HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## 🚀 Quick Start Examples

### 1. Index and Analyze Repository
```bash
# Index repository
REPO_ID=$(curl -s -X POST http://localhost:8080/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repo", "name": "my-repo"}' | jq -r '.repository_id')

# Run comprehensive analysis
curl -X POST http://localhost:8080/kenobi/repositories/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo", "repository_name": "my-repo"}'

# Get insights
curl -X GET http://localhost:8080/kenobi/repositories/$REPO_ID/insights
```

### 2. Monitor System Health
```bash
# System overview
curl -X GET http://localhost:8080/kenobi/dashboard/overview

# Cache statistics
curl -X GET http://localhost:8080/kenobi/cache/stats

# Real-time metrics
curl -X GET http://localhost:8080/kenobi/analytics/real-time
```

### 3. AI-Powered Analysis
```bash
# Analyze code with AI
curl -X POST http://localhost:8080/kenobi/ai/analyze-code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
    "language": "python",
    "analysis_type": "performance"
  }'

# Generate tests
curl -X POST http://localhost:8080/kenobi/ai/generate-tests \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b): return a + b",
    "language": "python",
    "test_framework": "pytest"
  }'
```

---

## 📚 Additional Resources

- **Interactive Documentation**: `GET /docs`
- **OpenAPI Specification**: `GET /openapi.json`
- **System Health**: `GET /health`
- **Dashboard**: `GET /kenobi/dashboard/overview`

---

*Complete API Reference for Multi-Agent Research System Phase 4*  
*Generated: June 27, 2025*  
*Total Endpoints: 61*