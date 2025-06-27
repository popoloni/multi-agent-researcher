# User Guides

Comprehensive guides for using the Multi-Agent Researcher system effectively.

## 📋 Guide Overview

This section provides practical guides for different user types and use cases, from basic repository analysis to advanced AI-powered insights.

## 👥 User Types

### 🔰 **Beginners**
New users getting started with code analysis and repository insights.

### 👨‍💻 **Developers**
Software developers using the system for code quality and analysis.

### 🏗️ **Architects**
System architects analyzing codebases and dependencies.

### 📊 **Managers**
Project managers tracking code quality and team productivity.

## 🚀 Quick Start Guides

### Getting Started (5 minutes)
1. **Start the System**
   ```bash
   python main.py
   ```

2. **Index Your First Repository**
   ```bash
   curl -X POST "http://localhost:8080/kenobi/repositories/index" \
     -H "Content-Type: application/json" \
     -d '{"path": "/path/to/your/repository"}'
   ```

3. **Get Analysis Results**
   ```bash
   curl "http://localhost:8080/kenobi/repositories/{repo_id}/analysis"
   ```

4. **View Dashboard**
   Open `http://localhost:8080/docs` for interactive API documentation

### Repository Analysis Workflow
1. **Index Repository** → **Analyze Code** → **Get Insights** → **Monitor Quality**

## 📖 Feature Guides

### 🔍 **Code Analysis**
Learn how to analyze code quality, complexity, and maintainability.

**Key Features:**
- **Quality Metrics**: 10+ code quality indicators
- **Complexity Analysis**: Cyclomatic complexity and maintainability
- **Pattern Detection**: Code patterns and anti-patterns
- **AI Insights**: AI-powered code recommendations

**Example Workflow:**
```bash
# 1. Analyze repository quality
curl "http://localhost:8080/kenobi/quality/repository/{repo_id}"

# 2. Get AI insights
curl "http://localhost:8080/kenobi/repositories/{repo_id}/insights"

# 3. Analyze specific file
curl -X POST "http://localhost:8080/kenobi/analyze/file" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "src/main.py", "repository_id": "repo_id"}'
```

### 🔎 **Search & Discovery**
Master the search capabilities for finding code patterns and similar implementations.

**Search Types:**
- **Semantic Search**: AI-powered meaning-based search
- **Code Pattern Search**: Find specific coding patterns
- **Cross-Repository Search**: Search across multiple repositories
- **Similarity Search**: Find similar code implementations

**Example Workflow:**
```bash
# 1. Semantic search
curl -X POST "http://localhost:8080/kenobi/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication function", "repository_id": "repo_id"}'

# 2. Pattern search
curl -X POST "http://localhost:8080/kenobi/search/patterns" \
  -H "Content-Type: application/json" \
  -d '{"pattern": "try-catch blocks", "repository_id": "repo_id"}'
```

### 🕸️ **Dependency Analysis**
Understand and manage dependencies across repositories.

**Capabilities:**
- **Dependency Mapping**: Visual dependency graphs
- **Impact Analysis**: Change impact assessment
- **Health Monitoring**: Dependency health tracking
- **Cross-Repository Analysis**: Multi-repo dependency tracking

**Example Workflow:**
```bash
# 1. Get repository dependencies
curl "http://localhost:8080/kenobi/repositories/{repo_id}/dependencies"

# 2. Analyze dependency health
curl "http://localhost:8080/kenobi/analysis/dependency-health/{repo_id}"

# 3. Cross-repository analysis
curl -X POST "http://localhost:8080/kenobi/analysis/cross-repository-dependencies" \
  -H "Content-Type: application/json" \
  -d '{"repository_ids": ["repo1", "repo2", "repo3"]}'
```

### 📊 **Dashboard & Analytics**
Monitor system performance and repository health in real-time.

**Dashboard Features:**
- **System Overview**: High-level system metrics
- **Repository Health**: Individual repository status
- **Quality Trends**: Code quality over time
- **Performance Analytics**: System performance metrics

**Example Workflow:**
```bash
# 1. System overview
curl "http://localhost:8080/kenobi/dashboard/overview"

# 2. Repository dashboard
curl "http://localhost:8080/kenobi/dashboard/repository/{repo_id}"

# 3. Real-time analytics
curl "http://localhost:8080/kenobi/analytics/real-time"
```

## 🎯 Use Case Scenarios

### **Scenario 1: New Project Analysis**
**Goal**: Analyze a new codebase for quality and maintainability

**Steps:**
1. Index the repository
2. Run comprehensive analysis
3. Review quality metrics
4. Get AI recommendations
5. Set up monitoring

### **Scenario 2: Code Review Assistance**
**Goal**: Use AI insights to improve code review process

**Steps:**
1. Analyze changed files
2. Get AI suggestions
3. Check quality trends
4. Review dependency impacts
5. Generate improvement recommendations

### **Scenario 3: Technical Debt Assessment**
**Goal**: Identify and prioritize technical debt

**Steps:**
1. Run quality analysis across all repositories
2. Identify code smells and anti-patterns
3. Analyze complexity trends
4. Prioritize refactoring efforts
5. Track improvement progress

### **Scenario 4: Architecture Review**
**Goal**: Analyze system architecture and dependencies

**Steps:**
1. Map repository dependencies
2. Analyze architectural patterns
3. Identify coupling issues
4. Review component relationships
5. Generate architecture insights

## 🔧 Advanced Features

### **Batch Processing**
Process multiple repositories simultaneously for large-scale analysis.

```bash
curl -X POST "http://localhost:8080/kenobi/repositories/batch-analysis" \
  -H "Content-Type: application/json" \
  -d '{"repository_paths": ["/repo1", "/repo2", "/repo3"]}'
```

### **Custom Analysis**
Configure custom analysis parameters for specific needs.

```bash
curl -X POST "http://localhost:8080/kenobi/analysis/repository-comprehensive" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": "repo_id",
    "analysis_types": ["quality", "complexity", "dependencies"],
    "include_ai_insights": true,
    "depth": "deep"
  }'
```

### **Real-time Monitoring**
Set up continuous monitoring for repository health.

```bash
# Start monitoring
curl -X POST "http://localhost:8080/kenobi/monitoring/start" \
  -H "Content-Type: application/json" \
  -d '{"repository_ids": ["repo1", "repo2"]}'

# Check monitoring status
curl "http://localhost:8080/kenobi/dashboard/real-time"
```

## 📚 Best Practices

### **Repository Management**
- **Regular Analysis**: Run analysis after major changes
- **Quality Gates**: Set quality thresholds for CI/CD
- **Monitoring**: Enable continuous monitoring for critical repositories
- **Documentation**: Keep repository metadata updated

### **Performance Optimization**
- **Caching**: Leverage caching for frequently accessed data
- **Batch Operations**: Use batch processing for multiple repositories
- **Incremental Analysis**: Focus on changed files for faster analysis
- **Resource Management**: Monitor system resources during analysis

### **Team Collaboration**
- **Shared Dashboards**: Use dashboards for team visibility
- **Quality Metrics**: Establish team quality standards
- **Regular Reviews**: Schedule regular code quality reviews
- **Knowledge Sharing**: Share insights and best practices

---

**Guide Version**: v1.0.0  
**Last Updated**: June 27, 2025  
**Coverage**: All System Features