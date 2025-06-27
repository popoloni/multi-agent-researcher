# Quick Start Guide

Get up and running with the Multi-Agent Research System in 5 minutes!

## 🚀 Prerequisites

- Python 3.8+
- Git
- 4GB+ RAM
- 2GB+ disk space

## ⚡ Quick Installation

### 1. Clone the Repository
```bash
git clone https://github.com/popoloni/multi-agent-researcher.git
cd multi-agent-researcher
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

The server will start and be available at `http://localhost:8080`

## 🎯 First Steps

### 1. Verify Installation
Open your browser and go to `http://localhost:8080/docs` to see the interactive API documentation.

### 2. Index Your First Repository
```bash
curl -X POST http://localhost:8080/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/your/repository",
    "name": "my-first-repo"
  }'
```

### 3. Run Analysis
```bash
curl -X POST http://localhost:8080/kenobi/repositories/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/your/repository",
    "repository_name": "my-first-repo"
  }'
```

### 4. View Dashboard
```bash
curl -X GET http://localhost:8080/kenobi/dashboard/overview
```

## 📊 What You Get

After running the analysis, you'll have access to:

### 🔍 Repository Analysis
- **Code Quality Score**: Overall quality assessment
- **Security Analysis**: Vulnerability detection
- **Performance Metrics**: Performance bottlenecks
- **Dependency Analysis**: Dependency health and conflicts

### 🤖 AI-Powered Insights
- **Code Explanations**: AI-generated code documentation
- **Test Generation**: Automated test case creation
- **Improvement Suggestions**: AI-powered optimization recommendations
- **Pattern Detection**: Design patterns and anti-patterns

### 📈 Real-time Monitoring
- **System Health**: Live system status
- **Performance Metrics**: Response times and throughput
- **Quality Trends**: Quality evolution over time
- **Cache Statistics**: Performance optimization data

## 🎮 Interactive Examples

### Analyze a Python Function
```bash
curl -X POST http://localhost:8080/kenobi/ai/analyze-code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
    "language": "python"
  }'
```

### Generate Unit Tests
```bash
curl -X POST http://localhost:8080/kenobi/ai/generate-tests \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b): return a + b",
    "language": "python",
    "test_framework": "pytest"
  }'
```

## 📱 Web Interface

### Access the Dashboard
1. Open `http://localhost:8080/docs` for API documentation
2. Use the interactive interface to test endpoints
3. View real-time metrics and system health

## 🚨 Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
lsof -i :8080

# Try a different port
uvicorn app.main:app --host 0.0.0.0 --port 8081
```

### Analysis Fails
```bash
# Check repository path exists
ls -la /path/to/your/repository

# Verify repository has code files
find /path/to/your/repository -name "*.py" -o -name "*.js" -o -name "*.java"
```

## 📚 Next Steps

1. **[API Documentation](../api/README.md)** - Complete API reference
2. **[Deployment Guide](./deployment.md)** - Production deployment

## 🎉 Success!

You now have a fully functional Multi-Agent Research System! 

Key achievements:
- ✅ System installed and running
- ✅ First repository indexed
- ✅ Analysis completed
- ✅ Dashboard accessible
- ✅ AI features available