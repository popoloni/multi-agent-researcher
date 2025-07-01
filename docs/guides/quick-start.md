# Quick Start Guide

Get up and running with the Multi-Agent Research System in 5 minutes!

## 🚀 Prerequisites

- Python 3.8+
- Git
- 4GB+ RAM
- 2GB+ disk space
- Ollama (optional, for AI features)

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

### 3. Start the System
```bash
# Make scripts executable
chmod +x start_all.sh start_dev.sh start_ui.sh

# Start everything with one command
./start_all.sh
```

The system will start with:
- **Backend API**: `http://localhost:12000`
- **Frontend UI**: `http://localhost:12001`

## 🎯 First Steps

### 1. Verify Installation
Open your browser and go to:
- **API Documentation**: `http://localhost:12000/docs`
- **Frontend Dashboard**: `http://localhost:12001`

### 2. Index Your First Repository
```bash
curl -X POST http://localhost:12000/kenobi/repositories/index \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/your/repository",
    "name": "my-first-repo"
  }'
```

### 3. Generate AI Documentation
```bash
curl -X POST http://localhost:12000/kenobi/repositories/{repository_id}/documentation \
  -H "Content-Type: application/json" \
  -d '{
    "options": {
      "include_architecture": true,
      "include_user_guide": true
    }
  }'
```

### 4. Chat About Your Code
```bash
# Create a chat session
curl -X POST http://localhost:12000/chat/repository/{repository_id}/session

# Send a message
curl -X POST http://localhost:12000/chat/repository/{repository_id} \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the main function",
    "session_id": "session123"
  }'
```

### 5. View Dashboard
```bash
curl -X GET http://localhost:12000/kenobi/dashboard/overview
```

## 📊 What You Get

After running the analysis, you'll have access to:

### 🔍 Repository Analysis
- **Code Quality Score**: Overall quality assessment
- **Security Analysis**: Vulnerability detection
- **Performance Metrics**: Performance bottlenecks
- **Dependency Analysis**: Dependency health and conflicts
- **Hierarchical Navigation**: Tree-view of code elements

### 🤖 AI-Powered Features
- **AI Documentation**: Professional documentation generation
- **Code Explanations**: AI-generated code documentation
- **Test Generation**: Automated test case creation
- **Improvement Suggestions**: AI-powered optimization recommendations
- **Pattern Detection**: Design patterns and anti-patterns
- **Repository Chat**: AI-powered conversations about your code

### 📈 Real-time Monitoring
- **System Health**: Live system status
- **Performance Metrics**: Response times and throughput
- **Quality Trends**: Quality evolution over time
- **Cache Statistics**: Performance optimization data
- **Progress Tracking**: Real-time updates for long operations

## 🎮 Interactive Examples

### Analyze a Python Function
```bash
curl -X POST http://localhost:12000/kenobi/ai/analyze-code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
    "language": "python"
  }'
```

### Generate Unit Tests
```bash
curl -X POST http://localhost:12000/kenobi/ai/generate-tests \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b): return a + b",
    "language": "python",
    "test_framework": "pytest"
  }'
```

### Search Code Semantically
```bash
curl -X POST http://localhost:12000/kenobi/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "authentication logic",
    "repository_id": "your-repo-id"
  }'
```

## 📱 Web Interface

### Access the Dashboard
1. Open `http://localhost:12001` for the main dashboard
2. Navigate to **Repositories** to manage your codebases
3. Use **Chat** to ask questions about your code
4. View **Documentation** for AI-generated docs
5. Explore **Functionalities** for hierarchical code navigation

### Key Features
- **Repository Management**: Clone, index, and analyze repositories
- **AI Chat**: Context-aware conversations about your code
- **Documentation Generator**: Professional AI-powered documentation
- **Functionalities Registry**: Tree-view of code elements
- **Real-time Monitoring**: Live system metrics and health

## 🚨 Troubleshooting

### Server Won't Start
```bash
# Check if ports are in use
lsof -i :12000
lsof -i :12001

# Try starting components individually
./start_dev.sh    # Backend only
./start_ui.sh     # Frontend only
```

### Analysis Fails
```bash
# Check repository path exists
ls -la /path/to/your/repository

# Verify repository has code files
find /path/to/your/repository -name "*.py" -o -name "*.js" -o -name "*.java"

# Check system status
./check_status.sh
```

### Documentation Generation Issues
```bash
# Check Ollama status
curl http://localhost:12000/ollama/status

# Verify Ollama is running
ollama list
```

## 📚 Next Steps

1. **[API Documentation](../api/README.md)** - Complete API reference with 90+ endpoints
2. **[Deployment Guide](./deployment.md)** - Production deployment
3. **[Architecture Documentation](../architecture/README.md)** - System design

## 🎉 Success!

You now have a fully functional Multi-Agent Research System! 

Key achievements:
- ✅ System installed and running
- ✅ First repository indexed
- ✅ AI documentation generated
- ✅ Chat functionality working
- ✅ Dashboard accessible
- ✅ All 90+ API endpoints available

## 🔗 Quick Links

- **Frontend**: http://localhost:12001
- **API Docs**: http://localhost:12000/docs
- **Health Check**: http://localhost:12000/health
- **System Status**: http://localhost:12000/kenobi/status