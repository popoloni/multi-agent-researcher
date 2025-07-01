# Complete API Reference

**Version**: v1.3.0 Production Ready  
**Total Endpoints**: 90+  
**Base URL**: `http://localhost:12000`  

## 📊 API Categories

### 🏠 Core System (3 Endpoints)
- `GET /` - Serve React frontend
- `GET /health` - System health check
- `GET /test-kenobi` - Test Kenobi agent functionality

### 🔬 Research (Mock Implementation) (4 Endpoints)
- `POST /research/start` - Start research task (mock)
- `GET /research/{research_id}/status` - Get research status (mock)
- `GET /research/{research_id}/result` - Get research result (mock)
- `POST /research/demo` - Demo research functionality (mock)
- `POST /research/test-citations` - Test citation functionality (mock)

### 🛠️ System Tools (3 Endpoints)
- `GET /tools/available` - Get available tools
- `GET /models/info` - Get model information
- `GET /ollama/status` - Check Ollama status

### 📁 Repository Management (25 Endpoints)
- `POST /kenobi/repositories/index` - Index a repository
- `POST /kenobi/repositories/index-advanced` - Advanced repository indexing
- `GET /kenobi/repositories` - List all repositories
- `GET /kenobi/repositories/{repository_id}` - Get repository details
- `DELETE /kenobi/repositories/{repository_id}` - Delete repository
- `GET /kenobi/repositories/{repository_id}/functionalities` - Get repository functionalities
- `GET /kenobi/repositories/{repository_id}/branches` - Get repository branches
- `GET /kenobi/repositories/{repository_id}/context` - Get repository context
- `GET /kenobi/repositories/{repo_id}/analysis` - Get repository analysis
- `GET /kenobi/repositories/{repo_id}/dependencies` - Get dependency graph
- `GET /kenobi/repositories/{repo_id}/dependencies-advanced` - Get advanced dependency insights
- `GET /kenobi/repositories/{repo_id}/categorize` - Categorize repository elements
- `GET /kenobi/repositories/{repo_id}/architecture` - Analyze repository architecture
- `POST /kenobi/repositories/{repository_id}/documentation` - Generate documentation
- `GET /kenobi/repositories/{repository_id}/documentation` - Get documentation
- `GET /kenobi/repositories/{repository_id}/documentation/status/{task_id}` - Get documentation status
- `DELETE /kenobi/repositories/{repository_id}/documentation` - Delete documentation
- `GET /kenobi/documentation/list` - List all documentation
- `GET /kenobi/documentation/stats` - Get documentation statistics
- `POST /kenobi/repositories/comprehensive-analysis` - Comprehensive repository analysis
- `POST /kenobi/repositories/batch-analysis` - Batch analyze repositories
- `POST /kenobi/repositories/compare` - Compare repositories
- `GET /kenobi/repositories/{repository_id}/health` - Monitor repository health
- `GET /kenobi/repositories/{repository_id}/insights` - Generate repository insights

### 📚 Documentation (8 Endpoints)
- `POST /kenobi/repositories/{repository_id}/documentation` - Generate AI documentation
- `GET /kenobi/repositories/{repository_id}/documentation` - Get generated documentation
- `GET /kenobi/repositories/{repository_id}/documentation/status/{task_id}` - Track generation progress
- `DELETE /kenobi/repositories/{repository_id}/documentation` - Delete documentation
- `GET /kenobi/documentation/list` - List all documentation
- `GET /kenobi/documentation/stats` - Documentation statistics

### 💬 Chat & RAG (6 Endpoints)
- `POST /kenobi/chat` - Kenobi chat interface
- `POST /chat/repository/{repo_id}` - Enhanced chat about repository
- `GET /chat/repository/{repo_id}/history` - Get chat history
- `DELETE /chat/repository/{repo_id}/history` - Clear chat history
- `POST /chat/repository/{repo_id}/session` - Create chat session

### 🔍 Search & Analysis (15 Endpoints)
- `POST /kenobi/search/code` - Search code across repositories
- `POST /kenobi/search/semantic` - Semantic code search
- `POST /kenobi/search/similar` - Search similar code
- `POST /kenobi/search/patterns` - Find code patterns
- `POST /kenobi/search/cross-repository` - Cross-repository search
- `POST /kenobi/analyze/file` - Analyze single file
- `GET /kenobi/analysis/list` - List analysis results
- `DELETE /kenobi/repositories/{repository_id}/analysis` - Delete analysis results
- `GET /kenobi/analysis/search` - Search code snippets
- `GET /kenobi/analysis/stats` - Analysis statistics
- `POST /kenobi/analysis/repository-comprehensive` - Comprehensive analysis
- `POST /kenobi/analysis/dependency-impact` - Analyze dependency impact
- `POST /kenobi/analysis/cross-repository-dependencies` - Cross-repository dependencies
- `GET /kenobi/analysis/dependency-health/{repository_id}` - Dependency health
- `GET /kenobi/analysis/dependency-patterns/{repository_id}` - Dependency patterns

### 🤖 AI Analysis (4 Endpoints)
- `POST /kenobi/ai/analyze-code` - AI code analysis
- `POST /kenobi/ai/explain-code` - Code explanation
- `POST /kenobi/ai/suggest-improvements` - Improvement suggestions
- `POST /kenobi/ai/generate-tests` - Test generation

### 🧮 Vector Operations (6 Endpoints)
- `POST /kenobi/vectors/embed-repository` - Embed repository for vector search
- `POST /kenobi/vectors/similarity-search` - Vector similarity search
- `POST /kenobi/vectors/cluster-analysis` - Vector clustering analysis
- `GET /kenobi/statistics/vectors` - Vector statistics

### 🔍 Quality Analysis (4 Endpoints)
- `POST /kenobi/quality/analyze-element` - Analyze code element quality
- `GET /kenobi/quality/repository/{repository_id}` - Repository quality summary
- `GET /kenobi/quality/trends/{element_id}` - Quality trends analysis
- `POST /kenobi/quality/batch-analyze` - Batch quality analysis

### 📊 Dashboard & Monitoring (10 Endpoints)
- `GET /kenobi/dashboard/overview` - System overview dashboard
- `GET /kenobi/dashboard/real-time` - Real-time dashboard
- `GET /kenobi/dashboard/repository/{repository_id}` - Repository dashboard
- `GET /kenobi/dashboard/quality` - Quality dashboard
- `GET /kenobi/dashboard/dependencies` - Dependencies dashboard
- `GET /kenobi/dashboard/search` - Search dashboard
- `GET /kenobi/status` - Kenobi system status
- `GET /kenobi/statistics/ai` - AI statistics

### 🔗 GitHub Integration (10 Endpoints)
- `GET /github/search` - Search GitHub repositories
- `GET /github/repositories/{owner}/{repo}` - Get repository info
- `GET /github/repositories/{owner}/{repo}/branches` - List repository branches
- `POST /github/repositories/clone` - Clone GitHub repository
- `GET /github/repositories/{owner}/{repo}/contents` - Get repository contents
- `GET /github/user/repositories` - Get user repositories
- `GET /github/rate-limit` - Check GitHub rate limit
- `GET /github/clone-status/{repo_id}` - Get clone status
- `POST /github/clone-cancel/{repo_id}` - Cancel clone operation

### 🗄️ Cache & Analytics (6 Endpoints)
- `GET /kenobi/cache/stats` - Cache statistics
- `POST /kenobi/cache/clear` - Clear cache
- `GET /kenobi/analytics/metrics` - System metrics
- `GET /kenobi/analytics/real-time` - Real-time analytics
- `POST /kenobi/monitoring/start` - Start monitoring
- `POST /kenobi/monitoring/stop` - Stop monitoring

### 🔗 Element Analysis (2 Endpoints)
- `GET /kenobi/elements/{element_id}/relationships` - Analyze element relationships
- `GET /kenobi/elements/{element_id}/categories/suggest` - Suggest element categories

## 📝 Request/Response Examples

### Repository Indexing
```bash
curl -X POST http://localhost:12000/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repo", "name": "my-repo"}'
```

### AI Documentation Generation
```bash
curl -X POST http://localhost:12000/kenobi/repositories/{repository_id}/documentation \
  -H "Content-Type: application/json" \
  -d '{"options": {"include_architecture": true, "include_user_guide": true}}'
```

### Chat with Repository Context
```bash
curl -X POST http://localhost:12000/chat/repository/{repo_id} \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain the main function", "session_id": "session123"}'
```

### Comprehensive Analysis
```bash
curl -X POST http://localhost:12000/kenobi/repositories/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/repo",
    "repository_name": "my-repo",
    "analysis_types": ["security", "performance", "quality"]
  }'
```

### Dashboard Overview
```bash
curl -X GET http://localhost:12000/kenobi/dashboard/overview
```

## 🚀 Getting Started

1. Start the server: `uvicorn app.main:app --host 0.0.0.0 --port 12000`
2. Index a repository: `POST /kenobi/repositories/index`
3. Generate documentation: `POST /kenobi/repositories/{id}/documentation`
4. Chat about code: `POST /chat/repository/{id}`
5. View dashboard: `GET /kenobi/dashboard/overview`

## ⚠️ Important Notes

- **Research Functionality**: The research endpoints (`/research/*`) are mock implementations and not fully functional in v1.3.0
- **Port Configuration**: Backend runs on port 12000, frontend on port 12001
- **Async Operations**: Documentation generation and analysis are async operations with progress tracking
- **Session Management**: Chat sessions are managed with unique session IDs

For detailed endpoint documentation, see the interactive docs at `/docs`.