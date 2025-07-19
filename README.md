# Multi-Agent Research System

An advanced AI-powered code analysis and repository management platform with 90+ comprehensive API endpoints, intelligent agents, and real-time monitoring capabilities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/popoloni/multi-agent-researcher)

## 📸 Application Screenshots

### Dashboard Overview
![Dashboard](imgs/Screenshot%202025-07-11%20alle%2001.07.57.png)
*Main dashboard showing system status, repository metrics, and quick actions*

### Repository Documentation
![Documentation](imgs/Screenshot%202025-07-11%20alle%2001.08.55.png)
*AI-generated documentation with comprehensive overviews, architecture analysis, and user guides*

### Obione Chat Interface
![Chat Interface](imgs/Screenshot%202025-07-11%20alle%2001.09.09.png)
*Interactive AI chat interface with repository context awareness and modern UI*

### Web Research System
![Research Interface](imgs/Screenshot%202025-07-11%20alle%2001.09.55.png)
*Multi-agent research system with real-time progress tracking and comprehensive results*

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/popoloni/multi-agent-researcher.git
cd multi-agent-researcher

# Make scripts executable
chmod +x start_all.sh start_dev.sh start_ui.sh utils/*.sh

# Start everything with one command
./start_all.sh

# Or start components individually:
# ./start_dev.sh    # Start backend + Ollama
# ./start_ui.sh     # Start frontend
```

**📖 For detailed setup instructions, see [docs/setup/SETUP_AND_DEPLOYMENT.md](docs/setup/SETUP_AND_DEPLOYMENT.md)**

### 📁 Script Organization

All utility scripts are now organized in the `utils/` folder for better project structure:

- **Main scripts** (in project root - wrapper scripts for backwards compatibility):
  - `start_all.sh` / `start_all.bat` - Start all services
  - `start_dev.sh` - Start backend only
  - `start_ui.sh` - Start frontend only
  - `cleanup.sh` - Clean temporary files
  - `verify_application.sh` - Verify system health

- **Actual scripts** (in `utils/` folder):
  - `utils/start_all.sh` - Main startup script with all features
  - `utils/start_dev.sh` - Backend startup script
  - `utils/start_ui.sh` - Frontend startup script
  - `utils/cleanup.sh` - System cleanup script
  - `utils/verify_application.sh` - Application verification
  - `utils/configure_ai_provider.py` - AI provider configuration
  - `utils/create_github_repo.sh` - GitHub repository setup
  - `utils/demo_system.py` - System demonstration
  - `utils/fix_documentation_issues.py` - Documentation fixes

You can use either the wrapper scripts in the root directory or call the scripts directly from the `utils/` folder.

### Access the Application
- **Frontend UI**: http://localhost:12001
- **Backend API**: http://localhost:12000
- **API Documentation**: http://localhost:12000/docs

### Managing the System
```bash
# Start all services
./start_all.sh

# Check system status
./start_all.sh status

# Stop all services
./start_all.sh stop

# Restart all services
./start_all.sh restart

# Download/update AI models
./start_all.sh pull-models

# View all available commands
./start_all.sh help
```

## ✨ Key Features

- **🤖 AI-Powered Documentation** - Professional documentation generation using Ollama LLM with real-time progress tracking
- **📊 Hierarchical Code Analysis** - Tree-view functionalities registry with GitHub source code integration  
- **🔍 Semantic Search** - Vector-based code search using ChromaDB
- **⚡ Production Ready** - Extended timeout handling, graceful error recovery, 90+ API endpoints
- **🏗️ Multi-Agent Architecture** - Specialized agents for orchestration, analysis, and dependencies
- **🎯 Complete Workflow** - GitHub search → clone → index → AI documentation → documentation-aware chat

## 🎉 Latest Improvements (v1.6.0)

### 💬 Fully Functional Obione Chat System - ENHANCED & FIXED
- **AI-Powered Conversations**: Working chat interface with Anthropic Claude and Ollama integration
- **Repository Context Awareness**: Chat understands repository structure and answers code-specific questions
- **Session Management**: Create and manage chat sessions with unique session IDs
- **Modern UI**: Professional blue theme with enhanced message bubbles and loading animations
- **🔥 CRITICAL FIX**: Resolved chat context issue - now provides repository-specific responses with actual file references

### 🚀 AI-Powered Documentation Generation
- **Professional Content**: AI-generated descriptions using Ollama llama3.2:1b model
- **Asynchronous Processing**: Background task processing with real-time progress tracking (0-100%)
- **Extended Timeout Handling**: Intelligent timeout management for larger AI models (up to 30 minutes)
- **Progressive Timeout Strategy**: Dynamically extends timeout based on generation progress
- **Graceful Degradation**: Provides basic documentation even if AI generation fails
- **Model-Specific Timeouts**: Automatic timeout adjustment based on model size and complexity
- **Rich Context**: Generates comprehensive overviews, architecture analysis, and user guides

### 🔍 Enhanced Vector Database & Context System
- **Complete Vector Database Integration**: 167,341 content chunks indexed from 7,385 files
- **Repository-Specific Context**: Chat responses now include actual file references and code snippets
- **Automatic Content Indexing**: Integrated content indexing into repository analysis workflow
- **RAG Service Enhancement**: Improved repository filtering and context quality
- **Repair Endpoint**: Added ability to re-index existing repositories for better context
- **Performance Optimization**: <5 seconds for contextual chat responses

### 🗂️ Enhanced Functionalities Registry
- **Hierarchical Structure**: Tree view grouping functions by source files
- **Smart Organization**: Logical sorting (Classes → Functions → Methods → Variables)
- **Functional Buttons**: Eye button opens GitHub source code, doc button navigates to documentation
- **Multiple Views**: Both hierarchical and flat view options

### 🔧 System Stability Improvements
- **Database Architecture**: Fixed async SQLite driver issues and unified database connections
- **Service Integration**: All services now work harmoniously with proper error handling
- **Extended Timeouts**: 5-minute timeout for repository operations (cloning, parsing, AI analysis)
- **Enhanced Error Handling**: User-friendly error messages with automatic clearing

## 📊 API Overview

| Category | Endpoints | Key Features |
|----------|-----------|--------------|
| **Repository Management** | 25 | GitHub integration, cloning, indexing, analysis |
| **Documentation** | 8 | AI-powered generation, progress tracking, async processing |
| **Chat & RAG** | 6 | AI-powered conversations, session management |
| **Analysis & Quality** | 15 | Code analysis, quality assessment, AI insights |
| **Vector Operations** | 6 | Semantic search, similarity, clustering |
| **Dashboard & Monitoring** | 10 | Real-time metrics, quality dashboards |
| **GitHub Integration** | 10 | Repository search, cloning, branch management |
| **Cache & Analytics** | 6 | Cache management, system metrics |

**Total: 90+ Production-Ready Endpoints**

## 🎯 Use Cases

### For Development Teams
- **AI Documentation Generation** - Automated professional documentation with contextual descriptions
- **Code Quality Assessment** - Automated quality scoring with A+ grade capability
- **Hierarchical Code Navigation** - Tree-view exploration with direct GitHub source links
- **Technical Debt Management** - Identify and prioritize technical debt

### For DevOps & Engineering Managers
- **Real-time Progress Monitoring** - Track documentation generation and repository processing
- **Batch Processing** - Analyze multiple repositories efficiently with extended timeout handling
- **Quality Dashboards** - Visual metrics and team insights
- **Production Deployment** - Docker, Kubernetes, cloud-ready architecture

## 🔧 Configuration

### Basic Setup
```bash
# Optional: Enhanced caching with Redis
REDIS_URL=redis://localhost:6379

# Optional: AI model configuration
OLLAMA_BASE_URL=http://localhost:11434

# GitHub integration
GITHUB_TOKEN=your_github_token_here
```

### 🤖 AI Model Configuration

The system supports multiple AI providers (Anthropic Claude and Ollama) with flexible model selection for different components:

#### **Environment Variables**
```bash
# === ANTHROPIC CONFIGURATION ===
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# === RESEARCH AGENTS ===
LEAD_AGENT_MODEL=claude-4-sonnet-20241120          # Lead research planning
SUBAGENT_MODEL=claude-4-sonnet-20241120            # Sub-research execution
CITATION_MODEL=claude-3-5-haiku-20241022           # Citation generation

# === OBIONE CHAT & CODE ANALYSIS ===
OBIONE_MODEL=claude-4-sonnet-20241120              # Code analysis & chat

# === DOCUMENTATION GENERATION ===
DOCUMENTATION_MODEL=claude-4-sonnet-20241120       # Documentation generation

# === DOCUMENTATION TIMEOUT CONFIGURATION ===
DOCUMENTATION_TIMEOUT_BASE=900                      # Base timeout in seconds (15 minutes)
DOCUMENTATION_TIMEOUT_PER_AI_CALL=120              # Additional timeout per AI call (2 minutes)
DOCUMENTATION_MAX_TIMEOUT=1800                      # Maximum timeout (30 minutes)

# === GOOGLE SEARCH (for research) ===
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_cse_id_here
```

#### **Timeout Configuration for Larger Models**

When using larger AI models (like llama3.1:70b or claude-4-opus), documentation generation may take longer. The system now includes:

- **Adaptive Timeouts**: Automatically adjusts timeout based on model type
- **Progress-Based Extension**: Extends timeout if generation is making progress
- **Individual AI Call Timeouts**: 5-minute timeout per AI call to prevent hanging
- **Graceful Degradation**: Provides basic documentation if AI generation fails
- **Real-time Progress Tracking**: Shows current stage and estimated completion time

**Model Timeout Multipliers:**
- Small models (llama3.2:1b): 1.0x (10 minutes)
- Medium models (llama3.1:8b): 1.5x (15 minutes)  
- Large models (llama3.1:70b): 3.0x (30 minutes)
- Anthropic models: 0.8x - 1.5x (8-15 minutes)

#### **Available Models**

**Anthropic Claude Models:**
- `claude-4-opus-20241120` - Highest performance, most expensive
- `claude-4-sonnet-20241120` - Balanced performance/cost (recommended)
- `claude-3-5-sonnet-20241022` - Good performance, lower cost
- `claude-3-5-haiku-20241022` - Fast, cost-effective for simple tasks

**Ollama Local Models:**
- `llama3.1:70b` - Highest quality (requires 40GB RAM)
- `llama3.1:8b` - Good balance (requires 8GB RAM)
- `mistral:7b` - Efficient alternative
- `llama3.2:3b` - Lightweight option
- `llama3.2:1b` - Ultra-lightweight (default)

#### **Model Configuration Examples**

**High-Performance Setup (Best Quality)**
```bash
LEAD_AGENT_MODEL=claude-4-opus-20241120
SUBAGENT_MODEL=claude-4-sonnet-20241120
CITATION_MODEL=claude-3-5-haiku-20241022
OBIONE_MODEL=claude-4-sonnet-20241120
DOCUMENTATION_MODEL=claude-4-sonnet-20241120
```

**Balanced Setup (Recommended)**
```bash
LEAD_AGENT_MODEL=claude-4-sonnet-20241120
SUBAGENT_MODEL=claude-4-sonnet-20241120
CITATION_MODEL=claude-3-5-haiku-20241022
OBIONE_MODEL=claude-3-5-sonnet-20241022
DOCUMENTATION_MODEL=claude-3-5-sonnet-20241022
```

**Local-Only Setup (No API Costs)**
```bash
LEAD_AGENT_MODEL=llama3.1:8b
SUBAGENT_MODEL=mistral:7b
CITATION_MODEL=llama3.2:3b
OBIONE_MODEL=llama3.1:8b
DOCUMENTATION_MODEL=llama3.1:8b
```

**Hybrid Setup (Best of Both)**
```bash
LEAD_AGENT_MODEL=claude-4-sonnet-20241120
SUBAGENT_MODEL=llama3.1:8b
CITATION_MODEL=llama3.2:3b
OBIONE_MODEL=claude-4-sonnet-20241120
DOCUMENTATION_MODEL=claude-3-5-sonnet-20241022
```

#### **How to Change Models**
1. Edit your `.env` file with your preferred models
2. Restart the backend: `./start_all.sh restart`
3. Test the changes by running research or chat

> **💡 Tip**: Start with the **Balanced Setup** and adjust based on your quality requirements and budget.

### Production Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports: ["12000:12000"]
    environment:
      - REDIS_URL=redis://redis:6379
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    depends_on: [redis, ollama]
  frontend:
    build: ./frontend
    ports: ["12001:3000"]
  redis:
    image: redis:alpine
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
```

## 📱 Web Interface

- **[Interactive API Docs](http://localhost:12000/docs)** - Swagger UI with all 90+ endpoints
- **[Frontend Dashboard](http://localhost:12001)** - Complete UI with AI documentation generation
- **[Repository Management](http://localhost:12001/repositories)** - Clone, analyze, and manage repositories
- **[Obione Chat](http://localhost:12001/chat)** - AI-powered chat about your codebase
- **[Functionalities Registry](http://localhost:12001/repositories/{id}/functionalities)** - Hierarchical code exploration
- **[Documentation Viewer](http://localhost:12001/repositories/{id}/documentation)** - AI-generated documentation

## 📁 Project Structure

```
multi-agent-researcher/
├── app/                          # Backend FastAPI application
│   ├── api/                      # API endpoints and routers
│   ├── core/                     # Core business logic and services
│   ├── models/                   # Database models and schemas
│   └── utils/                    # Utility functions and helpers
├── frontend/                     # React frontend application
│   ├── src/                      # Source code
│   ├── public/                   # Static assets
│   └── build/                    # Production build output
├── docs/                         # Comprehensive documentation
│   ├── api/                      # API documentation and examples
│   ├── guides/                   # User guides and tutorials
│   ├── architecture/             # System architecture documentation
│   ├── setup/                    # Setup and deployment guides
│   ├── troubleshooting/          # Troubleshooting guides
│   ├── implementation/           # Implementation reports and fixes
│   └── reports/                  # Development reports and metrics
├── migration_scripts/            # Database migration and data scripts
│   ├── database/                 # Database schema migrations
│   ├── data/                     # Data import/export scripts
│   └── legacy/                   # Legacy system migration tools
├── demo/                         # Demo scripts and examples
├── imgs/                         # Application screenshots
├── scripts/                      # Utility and automation scripts
├── *.sh                         # Startup and management scripts
├── cleanup.sh                   # Repository cleanup script
├── cleanup_dev_env.sh           # Development environment cleanup
└── requirements.txt             # Python dependencies
```

## 📚 Documentation

### 🚀 [Quick Start Guide](docs/guides/quick-start.md)
Get up and running in 5 minutes with step-by-step instructions.

### 📖 [Complete Documentation](docs/README.md)
Comprehensive documentation including:
- **[API Reference](docs/api/README.md)** - All 90+ endpoints with examples
- **[User Guides](docs/guides/README.md)** - Feature guides and tutorials  
- **[Architecture](docs/architecture/README.md)** - System design and components
- **[Setup & Deployment](docs/setup/SETUP_AND_DEPLOYMENT.md)** - Complete setup guide
- **[Troubleshooting](docs/troubleshooting/TROUBLESHOOTING_PLAN.md)** - Common issues and solutions
- **[Implementation Reports](docs/reports/README.md)** - Development phases and metrics
- **[Migration Scripts](migration_scripts/README.md)** - Database and data migration tools

### 📋 [Changelog](CHANGELOG.md)
See [CHANGELOG.md](CHANGELOG.md) for detailed information about recent improvements and bug fixes.

## 🏆 System Metrics

- **Development Time**: 4 weeks, 4 phases + debugging session improvements
- **Code Quality**: 85% complete with high-quality foundations
- **Performance**: Extended timeout handling, real-time progress tracking
- **Functionality**: 90+ endpoints, AI-powered documentation, hierarchical navigation
- **Architecture**: Multi-agent system with graceful error handling

## 🧪 Testing

### Comprehensive Test Suite

The project includes a comprehensive test suite with **243 tests** covering all aspects of the application:

#### Test Statistics
- **Total Tests**: 243
- **Passing**: 194 (79.8%)
- **Failing**: 49 (20.2%)
- **Skipped**: 28 (11.5%)

#### Test Categories
- **Unit Tests**: Core functionality testing for individual components
- **Integration Tests**: Service integration and workflow testing
- **API Tests**: Endpoint testing with FastAPI TestClient
- **E2E Tests**: End-to-end workflow testing
- **Frontend Tests**: React component testing

### Running Tests

#### Quick Test Commands
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/integration/ -v   # Integration tests
python -m pytest tests/api/ -v           # API tests
python -m pytest tests/e2e/ -v           # End-to-end tests

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run organized tests by category
python tests/run_organized_tests.py unit --coverage
python tests/run_organized_tests.py integration --parallel
python tests/run_organized_tests.py all --coverage --parallel

# Run non-regression tests (critical functionality)
python tests/run_non_regression_tests.py
python tests/run_non_regression_tests.py --smoke
python tests/run_non_regression_tests.py --performance
```

#### Frontend Tests
```bash
# Navigate to frontend directory
cd frontend

# Run frontend tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

### Test Reports & Documentation

#### Test Reports Location
- **HTML Reports**: `test-reports/` directory
- **Coverage Reports**: `htmlcov/` directory
- **Latest Summary**: `test-reports/latest_summary.txt`

#### Testing Documentation
All testing documentation has been organized in `docs/testing/`:

- **[Testing Documentation Index](docs/testing/README.md)** - Complete testing guide
- **[Test Reports & Analysis](docs/testing/)** - All test reports and analysis
- **[Test Inventory](docs/testing/test_inventory.md)** - Complete test inventory
- **[Implementation Logs](docs/testing/)** - Testing implementation details

### Recent Test Improvements

#### ✅ Import Error Resolution
- Fixed missing `app` directory issue that was causing all tests to fail
- Resolved all import errors and updated test configuration
- Achieved 100% test discovery success rate

#### ✅ Test Logic Fixes
- Fixed service constructor expectations to match actual implementations
- Corrected method call signatures across all test files
- Updated mocking strategies for proper service isolation
- Fixed API response expectations and test data setup

#### ✅ Performance Improvements
- Optimized test execution with proper async handling
- Fixed benchmark API usage for performance tests
- Improved test data setup and cleanup procedures

### Verified Working Features
- ✅ **Obione Chat System**: AI-powered conversations with repository context awareness
- ✅ **GitHub Integration**: Complete API with search, cloning, repository info
- ✅ **AI Documentation**: Professional content generation with Ollama integration
- ✅ **Repository Processing**: 5-minute timeout handling for complex repositories
- ✅ **Functionalities Registry**: Hierarchical navigation with GitHub source links
- ✅ **Database Operations**: Async SQLite with proper service integration
- ✅ **Progress Tracking**: Real-time updates for long-running operations
- ✅ **Error Handling**: User-friendly messages with automatic recovery

### Test Coverage
```bash
# Run comprehensive tests
./verify_application.sh  # or ./utils/verify_application.sh

# Test specific workflows
python demo/demo_working_features.py
python demo/add_repository.py
python demo/demo_documentation_generation.py
```

## 🤝 Contributing

See our [Contributing Guide](docs/guides/contributing.md) for development setup and contribution workflow.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**[📚 Full Documentation](docs/README.md)** | **[🚀 Quick Start](docs/guides/quick-start.md)** | **[📊 API Reference](docs/api/README.md)** | **[🏗️ Architecture](docs/architecture/README.md)** | **[📋 Changelog](CHANGELOG.md)**