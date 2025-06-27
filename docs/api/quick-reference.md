# API Quick Reference

## 🚀 Most Common Endpoints

### Repository Operations
```bash
# Index repository
POST /kenobi/repositories/index
{"path": "/path/to/repo", "name": "repo-name"}

# List repositories
GET /repositories

# Get repository details
GET /repositories/{id}
```

### Analysis Operations
```bash
# Comprehensive analysis
POST /kenobi/repositories/comprehensive-analysis
{"repository_path": "/path", "repository_name": "name"}

# Repository health
GET /kenobi/repositories/{id}/health

# Get insights
GET /kenobi/repositories/{id}/insights
```

### AI Operations
```bash
# Analyze code with AI
POST /kenobi/ai/analyze-code
{"code": "code_string", "language": "python"}

# Generate tests
POST /kenobi/ai/generate-tests
{"code": "code_string", "language": "python"}
```

### Dashboard & Monitoring
```bash
# System overview
GET /kenobi/dashboard/overview

# Repository dashboard
GET /kenobi/dashboard/repository/{id}

# Quality dashboard
GET /kenobi/dashboard/quality
```

## 📊 Response Formats

### Standard Success Response
```json
{
  "status": "success",
  "data": {},
  "timestamp": "2025-06-27T12:00:00Z"
}
```

### Repository Response
```json
{
  "repository_id": "uuid",
  "name": "string",
  "path": "string",
  "indexed_at": "datetime",
  "file_count": "number"
}
```

## ⚡ Quick Examples

### Complete Workflow
```bash
# 1. Index repository
REPO_ID=$(curl -s -X POST http://localhost:8080/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/my/repo", "name": "my-repo"}' | jq -r '.repository_id')

# 2. Run analysis
curl -X POST http://localhost:8080/kenobi/repositories/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/my/repo", "repository_name": "my-repo"}'

# 3. Get insights
curl -X GET http://localhost:8080/kenobi/repositories/$REPO_ID/insights
```

## 🔗 Related Documentation

- [Complete API Reference](./complete-api-reference.md)
- [Interactive Docs](http://localhost:8080/docs)