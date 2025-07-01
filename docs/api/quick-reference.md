# API Quick Reference

Essential endpoints for the Multi-Agent Research System.

## 🚀 Getting Started

```bash
# Start server
uvicorn app.main:app --host 0.0.0.0 --port 12000

# Check health
curl http://localhost:12000/health
```

## 📁 Repository Management

### Basic Operations
```bash
# Index a repository
curl -X POST http://localhost:12000/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repo", "name": "my-repo"}'

# List repositories
curl http://localhost:12000/kenobi/repositories

# Get repository details
curl http://localhost:12000/kenobi/repositories/{repository_id}

# Delete repository
curl -X DELETE http://localhost:12000/kenobi/repositories/{repository_id}
```

### Repository Analysis
```bash
# Get repository analysis
curl http://localhost:12000/kenobi/repositories/{repo_id}/analysis

# Get dependencies
curl http://localhost:12000/kenobi/repositories/{repo_id}/dependencies

# Comprehensive analysis
curl -X POST http://localhost:12000/kenobi/repositories/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo", "repository_name": "my-repo"}'
```

## 📚 Documentation

### AI Documentation Generation
```bash
# Generate documentation
curl -X POST http://localhost:12000/kenobi/repositories/{repository_id}/documentation \
  -H "Content-Type: application/json" \
  -d '{"options": {"include_architecture": true}}'

# Check generation status
curl http://localhost:12000/kenobi/repositories/{repository_id}/documentation/status/{task_id}

# Get generated documentation
curl http://localhost:12000/kenobi/repositories/{repository_id}/documentation
```

## 💬 Chat & RAG

### Repository Chat
```bash
# Create chat session
curl -X POST http://localhost:12000/chat/repository/{repo_id}/session

# Send message
curl -X POST http://localhost:12000/chat/repository/{repo_id} \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain the main function", "session_id": "session123"}'

# Get chat history
curl http://localhost:12000/chat/repository/{repo_id}/history?session_id=session123
```

## 🔍 Search

### Code Search
```bash
# Search code
curl -X POST http://localhost:12000/kenobi/search/code \
  -H "Content-Type: application/json" \
  -d '{"query": "function main", "repository_id": "repo123"}'

# Semantic search
curl -X POST http://localhost:12000/kenobi/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication logic", "repository_id": "repo123"}'
```

## 🤖 AI Analysis

### Code Analysis
```bash
# Analyze code
curl -X POST http://localhost:12000/kenobi/ai/analyze-code \
  -H "Content-Type: application/json" \
  -d '{"code": "function test() {}", "language": "javascript"}'

# Explain code
curl -X POST http://localhost:12000/kenobi/ai/explain-code \
  -H "Content-Type: application/json" \
  -d '{"code": "function test() {}", "language": "javascript"}'

# Generate tests
curl -X POST http://localhost:12000/kenobi/ai/generate-tests \
  -H "Content-Type: application/json" \
  -d '{"code": "function test() {}", "language": "javascript"}'
```

## 🔗 GitHub Integration

### Repository Operations
```bash
# Search GitHub repositories
curl "http://localhost:12000/github/search?q=python+fastapi&sort=stars"

# Get repository info
curl http://localhost:12000/github/repositories/{owner}/{repo}

# Clone repository
curl -X POST http://localhost:12000/github/repositories/clone \
  -H "Content-Type: application/json" \
  -d '{"owner": "owner", "repo": "repo", "branch": "main"}'

# Check clone status
curl http://localhost:12000/github/clone-status/{repo_id}
```

## 📊 Dashboard & Monitoring

### System Overview
```bash
# Dashboard overview
curl http://localhost:12000/kenobi/dashboard/overview

# Real-time dashboard
curl http://localhost:12000/kenobi/dashboard/real-time

# Repository dashboard
curl http://localhost:12000/kenobi/dashboard/repository/{repository_id}

# System status
curl http://localhost:12000/kenobi/status
```

## 🗄️ Cache & Analytics

### Cache Management
```bash
# Cache statistics
curl http://localhost:12000/kenobi/cache/stats

# Clear cache
curl -X POST http://localhost:12000/kenobi/cache/clear

# System metrics
curl http://localhost:12000/kenobi/analytics/metrics
```

## 🧮 Vector Operations

### Vector Search
```bash
# Embed repository
curl -X POST http://localhost:12000/kenobi/vectors/embed-repository \
  -H "Content-Type: application/json" \
  -d '{"repository_id": "repo123"}'

# Similarity search
curl -X POST http://localhost:12000/kenobi/vectors/similarity-search \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "repository_id": "repo123"}'
```

## ⚠️ Important Notes

- **Base URL**: `http://localhost:12000`
- **Frontend**: `http://localhost:12001`
- **Research Endpoints**: Mock implementation in v1.3.0
- **Async Operations**: Documentation generation uses background tasks
- **Session Management**: Chat requires session IDs for context

## 🔗 Interactive Documentation

- **Swagger UI**: `http://localhost:12000/docs`
- **ReDoc**: `http://localhost:12000/redoc`