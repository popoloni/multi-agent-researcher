# Kenobi Agent Specialization Plan

## Overview
Based on the transcript analysis, Kenobi is a specialized multi-repository code analysis agent that performs reverse engineering and code understanding tasks. This plan outlines the detailed steps to clone and implement Kenobi's capabilities within the existing multi-agent research system.

## What is Kenobi?
From the transcript, Kenobi is described as:
- A multi-repository analysis agent
- Part of a reverse engineering system
- Capable of indexing code with intelligent categorization
- Uses vector DB for descriptions and document DB for actual code
- Understands code dependencies and imports
- Provides context-aware code analysis
- Supports different programming languages with specialized indexing

## Core Capabilities to Implement

### 1. Repository Management System
**Objective**: Create a system to manage and index multiple code repositories

**Components**:
- Repository discovery and cloning
- Multi-language support (JavaScript, Python, Java, etc.)
- Repository metadata management
- Version control integration

**Implementation**:
- `app/services/repository_service.py` - Repository management
- `app/models/repository_schemas.py` - Repository data models
- `app/tools/git_tools.py` - Git operations and repository handling

### 2. Code Analysis and Indexing Engine
**Objective**: Parse, analyze, and index code with intelligent categorization

**Components**:
- Abstract Syntax Tree (AST) parsing for multiple languages
- Code element extraction (classes, functions, imports, etc.)
- Dependency graph construction
- Code quality assessment
- Contextual description generation

**Implementation**:
- `app/agents/code_analysis_agent.py` - Main code analysis agent
- `app/tools/code_parser.py` - Multi-language code parsing
- `app/tools/dependency_analyzer.py` - Dependency graph analysis
- `app/services/indexing_service.py` - Code indexing and storage

### 3. Intelligent Categorization System
**Objective**: Automatically categorize code elements using predefined and learned categories

**Categories** (based on transcript):
- **Architectural Patterns**: MVC, MVP, MVVM, Microservices, etc.
- **Design Patterns**: Singleton, Factory, Observer, etc.
- **Code Elements**: Classes, Functions, Interfaces, Enums, etc.
- **Language-Specific**: Components (React), Services (Angular), Controllers, etc.
- **Functionality**: Authentication, Database, API, UI, etc.

**Implementation**:
- `app/services/categorization_service.py` - Category management
- `app/models/category_schemas.py` - Category definitions
- `config/categories/` - Language-specific category definitions

### 4. Dual Storage Strategy
**Objective**: Implement the storage strategy described in transcript

**Vector Database Storage**:
- Code descriptions with context
- Dependency information
- Categorization metadata
- Search embeddings

**Document Database Storage**:
- Actual source code
- File metadata
- Repository structure
- Version information

**Implementation**:
- `app/services/vector_store_service.py` - Vector database operations
- `app/services/document_store_service.py` - Document storage
- `app/tools/embedding_tools.py` - Text embedding generation

### 5. Context-Aware Search System
**Objective**: Implement intelligent code search with context understanding

**Features**:
- Natural language queries about code
- Dependency-aware search
- Cross-repository search
- Code similarity detection
- Intent-based query expansion

**Implementation**:
- `app/agents/code_search_agent.py` - Specialized search agent
- `app/tools/code_search_tools.py` - Code-specific search tools
- `app/services/query_expansion_service.py` - Query enhancement

### 6. Multi-Language Support
**Objective**: Support multiple programming languages with specialized handling

**Supported Languages** (Phase 1):
- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- Java (.java)
- C# (.cs)
- Go (.go)

**Language-Specific Features**:
- Custom AST parsers
- Language-specific categories
- Framework detection (React, Angular, Spring, etc.)
- Import/dependency resolution

**Implementation**:
- `app/parsers/` - Language-specific parsers
- `app/parsers/python_parser.py`
- `app/parsers/javascript_parser.py`
- `app/parsers/java_parser.py`
- etc.

## Detailed Implementation Plan

### Phase 1: Foundation (Week 1-2)

#### 1.1 Repository Management
```python
# app/services/repository_service.py
class RepositoryService:
    async def clone_repository(self, repo_url: str) -> Repository
    async def scan_local_directory(self, path: str) -> Repository
    async def get_repository_metadata(self, repo_id: str) -> RepositoryMetadata
    async def list_repositories(self) -> List[Repository]
```

#### 1.2 Basic Code Parsing
```python
# app/tools/code_parser.py
class CodeParser:
    def parse_file(self, file_path: str, language: str) -> ParsedFile
    def extract_classes(self, ast_tree) -> List[ClassInfo]
    def extract_functions(self, ast_tree) -> List[FunctionInfo]
    def extract_imports(self, ast_tree) -> List[ImportInfo]
```

#### 1.3 Data Models
```python
# app/models/repository_schemas.py
class Repository(BaseModel):
    id: str
    name: str
    url: Optional[str]
    local_path: str
    language: str
    framework: Optional[str]
    indexed_at: datetime
    
class CodeElement(BaseModel):
    id: str
    repository_id: str
    file_path: str
    element_type: str  # class, function, interface, etc.
    name: str
    description: str
    categories: List[str]
    dependencies: List[str]
    code_snippet: str
```

### Phase 2: Core Analysis Engine (Week 3-4)

#### 2.1 Kenobi Agent Implementation
```python
# app/agents/kenobi_agent.py
class KenobiAgent(BaseAgent):
    """Specialized agent for code analysis and reverse engineering"""
    
    async def analyze_repository(self, repo_path: str) -> RepositoryAnalysis
    async def generate_code_description(self, code_element: CodeElement) -> str
    async def categorize_code_element(self, code_element: CodeElement) -> List[str]
    async def analyze_dependencies(self, repository: Repository) -> DependencyGraph
```

#### 2.2 Dependency Analysis
```python
# app/tools/dependency_analyzer.py
class DependencyAnalyzer:
    def build_dependency_graph(self, repository: Repository) -> DependencyGraph
    def find_circular_dependencies(self, graph: DependencyGraph) -> List[CircularDependency]
    def calculate_coupling_metrics(self, graph: DependencyGraph) -> CouplingMetrics
```

#### 2.3 Indexing Service
```python
# app/services/indexing_service.py
class IndexingService:
    async def index_repository(self, repository: Repository) -> IndexingResult
    async def update_index(self, repository: Repository, changed_files: List[str])
    async def search_code(self, query: str, filters: SearchFilters) -> List[SearchResult]
```

### Phase 3: Advanced Features (Week 5-6)

#### 3.1 Context-Aware Description Generation
- Implement the strategy from transcript: include imported class descriptions
- Generate rich context for each code element
- Use dependency information to enhance descriptions

#### 3.2 Intelligent Categorization
```python
# app/services/categorization_service.py
class CategorizationService:
    def load_categories_for_language(self, language: str) -> List[Category]
    async def categorize_with_ai(self, code_element: CodeElement) -> List[str]
    def validate_categories(self, categories: List[str], language: str) -> bool
```

#### 3.3 Multi-Repository Search
```python
# app/agents/code_search_agent.py
class CodeSearchAgent(BaseAgent):
    async def search_across_repositories(self, query: str) -> MultiRepoSearchResult
    async def find_similar_code(self, code_snippet: str) -> List[SimilarCode]
    async def explain_code_functionality(self, code_element: CodeElement) -> str
```

### Phase 4: Integration and API (Week 7-8)

#### 4.1 API Endpoints
```python
# New endpoints in app/main.py
@app.post("/kenobi/repositories/index")
async def index_repository(repo_request: RepositoryIndexRequest)

@app.get("/kenobi/repositories/{repo_id}/analysis")
async def get_repository_analysis(repo_id: str)

@app.post("/kenobi/search/code")
async def search_code(search_request: CodeSearchRequest)

@app.get("/kenobi/repositories/{repo_id}/dependencies")
async def get_dependency_graph(repo_id: str)

@app.post("/kenobi/analyze/file")
async def analyze_single_file(file_analysis_request: FileAnalysisRequest)
```

#### 4.2 Dashboard Integration
- Repository overview dashboard
- Code analysis metrics
- Dependency visualization
- Search interface

## Technical Architecture

### Storage Architecture
```
Vector Database (Embeddings)
├── Code Descriptions
├── Dependency Metadata
├── Category Information
└── Search Embeddings

Document Database (Raw Data)
├── Source Code Files
├── Repository Metadata
├── Dependency Graphs
└── Analysis Results

Cache Layer (Redis)
├── Parsed AST Trees
├── Analysis Results
└── Search Results
```

### Agent Hierarchy
```
Kenobi Lead Agent
├── Repository Analysis Agent
├── Code Search Agent
├── Dependency Analysis Agent
└── Categorization Agent
```

## Configuration

### Language-Specific Categories
```json
// config/categories/javascript.json
{
  "architectural_patterns": ["MVC", "MVP", "Component-Based"],
  "frameworks": ["React", "Angular", "Vue", "Express"],
  "code_elements": ["Component", "Hook", "Service", "Controller"],
  "functionality": ["Authentication", "API", "State Management", "Routing"]
}
```

### Environment Variables
```bash
# Kenobi-specific configuration
KENOBI_ENABLED=true
KENOBI_MODEL=claude-4-sonnet-20241120
VECTOR_DB_URL=http://localhost:6333  # Qdrant
DOCUMENT_DB_URL=mongodb://localhost:27017
CODE_ANALYSIS_MAX_FILE_SIZE=1048576  # 1MB
SUPPORTED_LANGUAGES=python,javascript,typescript,java,csharp,go
```

## Testing Strategy

### Unit Tests
- Code parser tests for each language
- Dependency analyzer tests
- Categorization service tests
- Vector/document storage tests

### Integration Tests
- End-to-end repository indexing
- Multi-repository search
- API endpoint tests
- Performance benchmarks

### Test Repositories
- Create sample repositories for each supported language
- Include various architectural patterns
- Test edge cases and complex dependencies

## Performance Considerations

### Optimization Strategies
1. **Incremental Indexing**: Only re-index changed files
2. **Parallel Processing**: Analyze multiple files concurrently
3. **Caching**: Cache parsed AST trees and analysis results
4. **Batch Operations**: Bulk insert into vector/document databases
5. **Language-Specific Optimizations**: Tailored parsing strategies

### Scalability
- Horizontal scaling for analysis workers
- Database sharding for large codebases
- Queue-based processing for large repositories
- Memory-efficient AST processing

## Success Metrics

### Functional Metrics
- Repository indexing speed (files per minute)
- Search accuracy and relevance
- Dependency detection accuracy
- Category classification precision

### Performance Metrics
- Query response time < 500ms
- Repository indexing time < 5 minutes for typical repos
- Memory usage < 2GB for analysis workers
- 99.9% uptime for search API

## Deployment Plan

### Development Environment
1. Set up local vector database (Qdrant)
2. Set up document database (MongoDB)
3. Configure language parsers
4. Create test repositories

### Production Environment
1. Containerized deployment with Docker
2. Kubernetes orchestration for scaling
3. Monitoring and logging setup
4. Backup and disaster recovery

## Timeline Summary

- **Week 1-2**: Foundation (Repository management, basic parsing)
- **Week 3-4**: Core engine (Kenobi agent, dependency analysis)
- **Week 5-6**: Advanced features (Context-aware descriptions, categorization)
- **Week 7-8**: Integration and API (Endpoints, dashboard)

## Implementation Status

### ✅ Completed
- [x] Plan creation and documentation
- [x] Branch "obione" created for development

### 🚧 In Progress
- [ ] Phase 1: Foundation implementation using Ollama

### 📋 Current Implementation Strategy
**Using Ollama for Local, Cost-Effective Development:**
- **Kenobi Lead Agent**: `llama3.1:8b` (balanced performance)
- **Code Analysis Subagents**: `mistral:7b` (efficient for parsing tasks)
- **Categorization Agent**: `llama3.2:3b` (lightweight for classification)
- **Search Agent**: `qwen2.5:7b` (optimized for search tasks)

### Next Steps

1. **✅ CURRENT**: Start with Phase 1 implementation using Ollama
2. **Set up Ollama models** for development
3. **Create test repositories** for validation
4. **Implement basic repository service** and code parser
5. **Begin Kenobi agent development**

This plan provides a comprehensive roadmap for creating a Kenobi clone that matches the capabilities described in the transcript while leveraging the existing multi-agent research system architecture with cost-effective local models.