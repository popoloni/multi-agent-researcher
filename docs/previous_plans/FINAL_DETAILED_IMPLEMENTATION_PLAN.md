# Final Detailed Implementation Plan: Database Persistence + RAG-Based Chat

## 🎯 **STRATEGIC OBJECTIVES**

This plan combines two critical objectives into a cohesive implementation strategy:

1. **Database Persistence with Performance**: Implement SQLite persistence with in-memory caching for optimal performance
2. **RAG-Based Documentation Chat**: Enhance chat system with document and code context using existing AI infrastructure

## 📊 **CURRENT CODE ANALYSIS**

### ✅ **EXISTING INFRASTRUCTURE ANALYSIS**
- **Repository Service**: In-memory storage with `self.repositories: Dict[str, Repository] = {}`
- **Documentation Storage**: Global `documentation_storage = {}` in main.py
- **Cache Service**: Sophisticated caching with Redis fallback to in-memory
- **Vector Service**: ChromaDB integration with embedding tools available
- **Chat System**: `chat_about_repository()` method exists but uses basic code search only
- **Database Models**: SQLAlchemy models defined but not integrated

### ⚠️ **INTEGRATION POINTS IDENTIFIED**
- **Repository Service**: Needs database integration while maintaining cache performance
- **Documentation Storage**: Must migrate from global dict to database with vector indexing
- **Chat Enhancement**: Existing method needs RAG context integration
- **Vector Service**: Ready for use but not connected to documentation pipeline

---

## 🚀 **PHASE-BY-PHASE DETAILED IMPLEMENTATION**

## 📋 **PHASE 1: DATABASE FOUNDATION WITH CACHING (Days 1-3)**
*Objective: Implement persistence without breaking existing functionality*

### **Day 1: Database Service Integration**

#### **Task 1.1: Create Database Service Layer**
**File**: `app/services/database_service.py` (NEW)
**Integration Point**: Replace in-memory storage in `RepositoryService`

```python
class DatabaseService:
    def __init__(self):
        # Use SQLite for development, PostgreSQL for production
        database_url = settings.DATABASE_URL or "sqlite:///./kenobi.db"
        self.engine = create_async_engine(database_url)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
    
    async def initialize(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def save_repository(self, repository: Repository) -> Repository:
        """Save repository with immediate cache update"""
        async with self.session_factory() as session:
            # Convert from current Repository model to database model
            db_repo = DatabaseRepository(
                id=repository.id,
                name=repository.name,
                url=repository.url,
                github_owner=getattr(repository, 'github_owner', None),
                github_repo=getattr(repository, 'github_repo', None),
                clone_status=repository.clone_status,
                created_at=datetime.utcnow()
            )
            session.add(db_repo)
            await session.commit()
            return repository
    
    async def get_repository(self, repo_id: str) -> Optional[Repository]:
        """Get repository from database"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(DatabaseRepository).where(DatabaseRepository.id == repo_id)
            )
            db_repo = result.scalar_one_or_none()
            
            if db_repo:
                # Convert back to current Repository model
                return Repository(
                    id=db_repo.id,
                    name=db_repo.name,
                    url=db_repo.url,
                    clone_status=db_repo.clone_status,
                    # ... other fields
                )
            return None
```

**Value Increment**: Database persistence foundation without breaking existing API
**Test Requirements**:
- Test database connection and table creation
- Test repository save/load operations
- Test backward compatibility with existing Repository model
- Test database initialization on startup

#### **Task 1.2: Enhance Repository Service with Database Integration**
**File**: `app/services/repository_service.py` (ENHANCE EXISTING)
**Integration Point**: Modify existing `__init__` and storage methods

```python
class RepositoryService:
    def __init__(self):
        self.code_parser = CodeParser()
        self.repositories: Dict[str, Repository] = {}  # Keep for cache
        self.analyses: Dict[str, RepositoryAnalysis] = {}
        self.clone_progress_callbacks: Dict[str, Callable] = {}
        
        # NEW: Add database service
        self.db_service = DatabaseService()
        self.cache_service = cache_service
    
    async def initialize(self):
        """Initialize database and migrate existing data"""
        await self.db_service.initialize()
        await self._migrate_existing_repositories()
    
    async def _migrate_existing_repositories(self):
        """Migrate existing in-memory repositories to database"""
        for repo_id, repository in self.repositories.items():
            try:
                await self.db_service.save_repository(repository)
                logger.info(f"Migrated repository {repo_id} to database")
            except Exception as e:
                logger.error(f"Failed to migrate repository {repo_id}: {e}")
    
    async def add_repository(self, repo_data: Dict[str, Any]) -> Repository:
        """Add repository with database persistence"""
        repository = Repository(**repo_data)
        
        # Save to database first
        await self.db_service.save_repository(repository)
        
        # Update cache
        self.repositories[repository.id] = repository
        
        return repository
    
    async def get_repository_metadata(self, repo_id: str) -> Optional[Repository]:
        """Get repository with cache-first strategy"""
        # Try cache first
        if repo_id in self.repositories:
            return self.repositories[repo_id]
        
        # Fallback to database
        repository = await self.db_service.get_repository(repo_id)
        if repository:
            # Update cache
            self.repositories[repo_id] = repository
        
        return repository
```

**Value Increment**: Seamless database integration with existing cache performance
**Test Requirements**:
- Test cache-first retrieval strategy
- Test database fallback when cache misses
- Test migration of existing repositories
- Test performance comparison (cache vs database)
- Test that existing API endpoints continue to work

#### **Task 1.3: Update Main.py Initialization**
**File**: `app/main.py` (ENHANCE EXISTING)
**Integration Point**: Add database initialization to startup

```python
# Add database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Initialize repository service with database
        await kenobi_agent.repository_service.initialize()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Continue with in-memory storage as fallback
```

**Value Increment**: Graceful startup with database initialization and fallback
**Test Requirements**:
- Test successful database initialization
- Test fallback behavior when database fails
- Test that existing endpoints work after startup
- Test health check includes database status

### **Day 2: Documentation Persistence with Vector Integration**

#### **Task 2.1: Create Documentation Service**
**File**: `app/services/documentation_service.py` (NEW)
**Integration Point**: Replace global `documentation_storage` in main.py

```python
class DocumentationService:
    def __init__(self):
        self.db_service = DatabaseService()
        self.vector_service = VectorService()
        self.cache_service = cache_service
    
    async def save_documentation(self, repo_id: str, documentation_data: Dict[str, Any]) -> Documentation:
        """Save documentation with vector indexing"""
        # Create documentation record
        documentation = Documentation(
            id=f"{repo_id}_{datetime.utcnow().timestamp()}",
            repository_id=repo_id,
            content=json.dumps(documentation_data),
            format="json",
            generated_at=datetime.utcnow(),
            vector_indexed=False
        )
        
        # Save to database
        async with self.db_service.session_factory() as session:
            session.add(documentation)
            await session.commit()
        
        # Create vector embeddings for RAG
        await self._create_vector_embeddings(documentation)
        
        # Update vector_indexed flag
        documentation.vector_indexed = True
        async with self.db_service.session_factory() as session:
            await session.merge(documentation)
            await session.commit()
        
        # Update cache
        self.cache_service.set(f"doc_{repo_id}", documentation_data, ttl=3600)
        
        return documentation
    
    async def get_documentation(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get documentation with cache-first strategy"""
        # Try cache first
        cached = self.cache_service.get(f"doc_{repo_id}")
        if cached:
            return cached
        
        # Fallback to database
        async with self.db_service.session_factory() as session:
            result = await session.execute(
                select(Documentation)
                .where(Documentation.repository_id == repo_id)
                .order_by(Documentation.generated_at.desc())
            )
            doc = result.scalar_one_or_none()
            
            if doc:
                doc_data = json.loads(doc.content)
                self.cache_service.set(f"doc_{repo_id}", doc_data, ttl=3600)
                return doc_data
        
        return None
    
    async def _create_vector_embeddings(self, documentation: Documentation):
        """Create vector embeddings for RAG retrieval"""
        doc_data = json.loads(documentation.content)
        vector_docs = []
        
        # Process each documentation section
        for section_type, content in doc_data.items():
            if isinstance(content, str) and content.strip():
                # Split into chunks for better retrieval
                chunks = self._split_content(content, max_chunk_size=500)
                
                for i, chunk in enumerate(chunks):
                    vector_doc = VectorDocument(
                        id=f"{documentation.id}_{section_type}_chunk_{i}",
                        content=chunk,
                        metadata={
                            "repository_id": documentation.repository_id,
                            "doc_type": section_type,
                            "chunk_index": i,
                            "source": "documentation",
                            "generated_at": documentation.generated_at.isoformat()
                        }
                    )
                    vector_docs.append(vector_doc)
        
        # Store in vector database
        if vector_docs:
            await self.vector_service.add_documents(vector_docs)
    
    def _split_content(self, content: str, max_chunk_size: int = 500) -> List[str]:
        """Split content into chunks for vector storage"""
        # Simple sentence-based splitting
        sentences = content.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
```

**Value Increment**: Documentation persistence with RAG-ready vector embeddings
**Test Requirements**:
- Test documentation save with vector embedding creation
- Test cache-first retrieval strategy
- Test vector document creation and storage
- Test content chunking for optimal retrieval
- Test migration from existing documentation_storage

#### **Task 2.2: Migrate Documentation Endpoints**
**File**: `app/main.py` (ENHANCE EXISTING)
**Integration Point**: Replace global documentation_storage usage

```python
# Initialize documentation service
documentation_service = DocumentationService()

@app.post("/kenobi/repositories/{repository_id}/documentation")
async def generate_documentation(repository_id: str, background_tasks: BackgroundTasks, options: Dict[str, Any] = None):
    """Generate documentation with database persistence"""
    # ... existing validation logic ...
    
    async def generate_documentation_async():
        try:
            # ... existing generation logic ...
            
            # NEW: Save to database instead of in-memory storage
            await documentation_service.save_documentation(repository_id, final_documentation)
            
            # Update task status
            documentation_generation_storage[task_id].update({
                "status": "completed",
                "documentation": final_documentation,
                "completed_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            # ... existing error handling ...

@app.get("/kenobi/repositories/{repository_id}/documentation")
async def get_documentation(repository_id: str, branch: str = "main"):
    """Get documentation from database with cache"""
    try:
        documentation = await documentation_service.get_documentation(repository_id)
        
        if documentation:
            return {
                "documentation": documentation,
                "last_generated": datetime.utcnow().isoformat(),
                "source": "database"
            }
        else:
            # Fallback to existing in-memory storage for backward compatibility
            doc_key = f"{repository_id}:{branch}"
            if doc_key in documentation_storage:
                return {
                    "documentation": documentation_storage[doc_key],
                    "last_generated": datetime.utcnow().isoformat(),
                    "source": "memory"
                }
            
            return {
                "documentation": {},
                "last_generated": None,
                "source": "none"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documentation: {str(e)}")
```

**Value Increment**: Seamless migration with backward compatibility
**Test Requirements**:
- Test documentation generation saves to database
- Test documentation retrieval from database
- Test backward compatibility with existing storage
- Test vector embedding creation during generation
- Test API response format consistency

### **Day 3: Database Migration and Integration Testing**

#### **Task 3.1: Data Migration Script**
**File**: `app/database/migration.py` (NEW)
**Integration Point**: Migrate existing data to database

```python
class DataMigration:
    def __init__(self):
        self.db_service = DatabaseService()
        self.documentation_service = DocumentationService()
    
    async def migrate_all_data(self):
        """Migrate all existing data to database"""
        await self._migrate_repositories()
        await self._migrate_documentation()
    
    async def _migrate_repositories(self):
        """Migrate repositories from RepositoryService cache"""
        from app.main import kenobi_agent
        
        migrated_count = 0
        for repo_id, repository in kenobi_agent.repository_service.repositories.items():
            try:
                await self.db_service.save_repository(repository)
                migrated_count += 1
                logger.info(f"Migrated repository: {repo_id}")
            except Exception as e:
                logger.error(f"Failed to migrate repository {repo_id}: {e}")
        
        logger.info(f"Migrated {migrated_count} repositories to database")
    
    async def _migrate_documentation(self):
        """Migrate documentation from global storage"""
        from app.main import documentation_storage
        
        migrated_count = 0
        for doc_key, doc_data in documentation_storage.items():
            try:
                repo_id, branch = doc_key.split(':')
                await self.documentation_service.save_documentation(repo_id, doc_data)
                migrated_count += 1
                logger.info(f"Migrated documentation: {doc_key}")
            except Exception as e:
                logger.error(f"Failed to migrate documentation {doc_key}: {e}")
        
        logger.info(f"Migrated {migrated_count} documentation records to database")

# Add migration endpoint for manual trigger
@app.post("/admin/migrate-data")
async def migrate_data():
    """Migrate existing data to database"""
    try:
        migration = DataMigration()
        await migration.migrate_all_data()
        return {"status": "success", "message": "Data migration completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")
```

**Value Increment**: Safe data migration with rollback capability
**Test Requirements**:
- Test repository migration preserves all data
- Test documentation migration with vector embedding creation
- Test migration idempotency (can run multiple times safely)
- Test rollback capability if migration fails
- Test system continues to work during migration

#### **Task 3.2: Comprehensive Integration Testing**
**File**: `tests/test_phase1_integration.py` (NEW)

```python
class TestPhase1Integration:
    async def test_repository_persistence_workflow(self):
        """Test complete repository persistence workflow"""
        # 1. Add repository
        repo_data = {
            "id": "test-repo-persist",
            "name": "Test Repository",
            "url": "https://github.com/test/repo"
        }
        
        repository = await repository_service.add_repository(repo_data)
        assert repository.id == "test-repo-persist"
        
        # 2. Verify cache hit
        cached_repo = await repository_service.get_repository_metadata("test-repo-persist")
        assert cached_repo.name == "Test Repository"
        
        # 3. Clear cache and verify database retrieval
        repository_service.repositories.clear()
        db_repo = await repository_service.get_repository_metadata("test-repo-persist")
        assert db_repo.name == "Test Repository"
        
        # 4. Verify performance (cache should be faster)
        start_time = time.time()
        for _ in range(100):
            await repository_service.get_repository_metadata("test-repo-persist")
        cache_time = time.time() - start_time
        
        repository_service.repositories.clear()
        start_time = time.time()
        for _ in range(100):
            await repository_service.get_repository_metadata("test-repo-persist")
        db_time = time.time() - start_time
        
        assert cache_time < db_time  # Cache should be faster
    
    async def test_documentation_with_vector_embeddings(self):
        """Test documentation persistence with vector embedding creation"""
        doc_data = {
            "overview": "This is a comprehensive test repository for Python development",
            "api_reference": "API documentation with detailed endpoint descriptions",
            "architecture": "System architecture using microservices pattern"
        }
        
        # Save documentation
        documentation = await documentation_service.save_documentation("test-repo", doc_data)
        assert documentation.vector_indexed == True
        
        # Verify vector embeddings were created
        search_results = await vector_service.search(
            query="Python development",
            filters={"repository_id": "test-repo", "source": "documentation"},
            limit=5
        )
        
        assert len(search_results) > 0
        assert any("Python development" in result.content for result in search_results)
    
    async def test_backward_compatibility(self):
        """Test that existing API endpoints continue to work"""
        # Test existing documentation endpoint
        response = await client.get("/kenobi/repositories/test-repo/documentation")
        assert response.status_code == 200
        
        # Test existing repository endpoints
        response = await client.get("/kenobi/repositories")
        assert response.status_code == 200
    
    async def test_migration_safety(self):
        """Test that migration doesn't break existing data"""
        # Create test data in old format
        documentation_storage["test-repo:main"] = {"overview": "Test content"}
        repository_service.repositories["test-repo"] = Repository(
            id="test-repo", name="Test", url="https://test.com"
        )
        
        # Run migration
        migration = DataMigration()
        await migration.migrate_all_data()
        
        # Verify data is accessible through new system
        doc = await documentation_service.get_documentation("test-repo")
        assert doc["overview"] == "Test content"
        
        repo = await repository_service.get_repository_metadata("test-repo")
        assert repo.name == "Test"
```

**Value Increment**: Confidence in system reliability and performance
**Test Requirements**:
- Performance benchmarks (cache vs database)
- Data integrity verification
- Backward compatibility confirmation
- Migration safety validation
- Error handling and recovery testing

---

## 📋 **PHASE 2: RAG CONTEXT INTEGRATION (Days 4-6)**
*Objective: Enhance chat with documentation and code context*

### **Day 4: Context Retrieval System**

#### **Task 4.1: Create Context Service**
**File**: `app/services/context_service.py` (NEW)
**Integration Point**: Enhance existing `chat_about_repository` method

```python
class ContextService:
    def __init__(self):
        self.vector_service = VectorService()
        self.documentation_service = DocumentationService()
        self.repository_service = RepositoryService()
        self.indexing_service = IndexingService()
    
    async def get_relevant_context(
        self, 
        query: str, 
        repository_id: str, 
        max_chunks: int = 5,
        include_documentation: bool = True,
        include_code: bool = True
    ) -> Dict[str, Any]:
        """Get relevant context for RAG-enhanced chat"""
        
        context_results = {
            "documentation": [],
            "code": [],
            "combined_score": 0.0,
            "sources": []
        }
        
        # Get documentation context if requested
        if include_documentation:
            doc_context = await self._get_documentation_context(query, repository_id, max_chunks)
            context_results["documentation"] = doc_context
        
        # Get code context if requested
        if include_code:
            code_context = await self._get_code_context(query, repository_id, max_chunks)
            context_results["code"] = code_context
        
        # Combine and rank all contexts
        all_contexts = context_results["documentation"] + context_results["code"]
        all_contexts.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Extract sources for display
        context_results["sources"] = self._extract_sources(all_contexts[:max_chunks])
        context_results["combined_score"] = sum(ctx["relevance_score"] for ctx in all_contexts[:max_chunks])
        
        return context_results
    
    async def _get_documentation_context(self, query: str, repository_id: str, max_chunks: int) -> List[Dict]:
        """Retrieve relevant documentation chunks using vector search"""
        try:
            search_results = await self.vector_service.search(
                query=query,
                filters={"repository_id": repository_id, "source": "documentation"},
                limit=max_chunks
            )
            
            return [
                {
                    "content": result.content,
                    "metadata": result.metadata,
                    "relevance_score": result.score,
                    "source_type": "documentation",
                    "doc_type": result.metadata.get("doc_type", "unknown")
                }
                for result in search_results
            ]
        except Exception as e:
            logger.error(f"Error retrieving documentation context: {e}")
            return []
    
    async def _get_code_context(self, query: str, repository_id: str, max_chunks: int) -> List[Dict]:
        """Retrieve relevant code chunks using existing indexing service"""
        try:
            # Use existing code search functionality
            search_filters = SearchFilters()
            search_filters.repositories = [repository_id]
            search_filters.max_results = max_chunks
            
            # Search for relevant code elements
            search_results = await self.indexing_service.search_code_elements(
                query=query,
                filters=search_filters
            )
            
            return [
                {
                    "content": result.code_snippet or result.description,
                    "metadata": {
                        "file_path": result.file_path,
                        "element_name": result.name,
                        "element_type": result.element_type.value,
                        "line_number": getattr(result, 'line_number', 0)
                    },
                    "relevance_score": getattr(result, 'relevance_score', 0.5),
                    "source_type": "code"
                }
                for result in search_results
            ]
        except Exception as e:
            logger.error(f"Error retrieving code context: {e}")
            return []
    
    def _extract_sources(self, contexts: List[Dict]) -> List[Dict]:
        """Extract source information for UI display"""
        sources = []
        for ctx in contexts:
            source = {
                "source_type": ctx["source_type"],
                "relevance_score": ctx["relevance_score"]
            }
            
            if ctx["source_type"] == "documentation":
                source["doc_type"] = ctx.get("doc_type", "unknown")
                source["display_name"] = f"Documentation: {source['doc_type']}"
            else:
                source["file_path"] = ctx["metadata"].get("file_path", "unknown")
                source["element_name"] = ctx["metadata"].get("element_name", "unknown")
                source["display_name"] = f"Code: {source['element_name']}"
            
            sources.append(source)
        
        return sources
```

**Value Increment**: Intelligent context retrieval for RAG-enhanced responses
**Test Requirements**:
- Test documentation context retrieval with vector search
- Test code context retrieval with existing indexing
- Test context ranking and scoring
- Test source extraction for UI display
- Test error handling when services are unavailable

#### **Task 4.2: Enhance Kenobi Agent with RAG**
**File**: `app/agents/kenobi_agent.py` (ENHANCE EXISTING)
**Integration Point**: Modify existing `chat_about_repository` method

```python
class KenobiAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # ... existing initialization ...
        
        # NEW: Add context service for RAG
        self.context_service = ContextService()
    
    async def chat_about_repository(
        self, 
        message: str, 
        repository_id: str, 
        branch: str = "main",
        use_documentation: bool = True,
        use_code: bool = True
    ) -> Dict[str, Any]:
        """
        Enhanced chat with RAG context from documentation and code
        """
        try:
            # Get repository metadata (existing logic)
            repository = await self.repository_service.get_repository_metadata(repository_id)
            if not repository:
                return {
                    "answer": "Repository not found. Please make sure the repository is indexed.",
                    "sources": [],
                    "context_used": [],
                    "timestamp": datetime.now().isoformat()
                }

            # NEW: Get relevant context using RAG
            context = await self.context_service.get_relevant_context(
                query=message,
                repository_id=repository_id,
                max_chunks=5,
                include_documentation=use_documentation,
                include_code=use_code
            )
            
            # Build enhanced prompt with context
            enhanced_prompt = self._build_rag_prompt(message, context, repository)
            
            # Generate response using existing AI engine
            response = await self._call_llm(enhanced_prompt, max_tokens=1000)
            
            return {
                "answer": response.strip(),
                "sources": context["sources"],
                "context_used": context["sources"],
                "documentation_chunks": len(context["documentation"]),
                "code_chunks": len(context["code"]),
                "combined_score": context["combined_score"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in RAG chat: {e}")
            # Fallback to existing basic chat
            return await self._fallback_chat(message, repository_id, branch)
    
    def _build_rag_prompt(self, message: str, context: Dict, repository: Repository) -> str:
        """Build enhanced prompt with RAG context"""
        prompt_parts = [
            f"You are an expert code analyst for the repository '{repository.name}'.",
            f"Answer the user's question using the provided context from documentation and code.",
            f"\nUser Question: {message}\n"
        ]
        
        # Add documentation context
        if context["documentation"]:
            prompt_parts.append("## Relevant Documentation:")
            for doc in context["documentation"]:
                doc_type = doc.get("doc_type", "unknown")
                content_preview = doc["content"][:300] + "..." if len(doc["content"]) > 300 else doc["content"]
                prompt_parts.append(f"**{doc_type.title()}**: {content_preview}")
        
        # Add code context
        if context["code"]:
            prompt_parts.append("\n## Relevant Code:")
            for code in context["code"]:
                file_path = code["metadata"].get("file_path", "unknown")
                element_name = code["metadata"].get("element_name", "unknown")
                content_preview = code["content"][:200] + "..." if len(code["content"]) > 200 else code["content"]
                prompt_parts.append(f"**{file_path}** - {element_name}:")
                prompt_parts.append(f"```\n{content_preview}\n```")
        
        prompt_parts.extend([
            "\n## Instructions:",
            "1. Provide a comprehensive answer based on the context above",
            "2. Reference specific documentation sections or code elements when relevant",
            "3. If the context doesn't contain enough information, say so clearly",
            "4. Be technical but accessible in your explanation"
        ])
        
        return "\n".join(prompt_parts)
    
    async def _fallback_chat(self, message: str, repository_id: str, branch: str) -> Dict[str, Any]:
        """Fallback to existing chat functionality if RAG fails"""
        # Use existing search logic as fallback
        search_context = {
            "repository_id": repository_id,
            "max_results": 10,
            "branch": branch
        }
        
        # ... existing search and response logic ...
        
        return {
            "answer": "I encountered an issue with enhanced search. Using basic search instead.",
            "sources": [],
            "context_used": [],
            "timestamp": datetime.now().isoformat()
        }
```

**Value Increment**: RAG-enhanced chat with graceful fallback to existing functionality
**Test Requirements**:
- Test RAG-enhanced responses include relevant context
- Test fallback to existing chat when RAG fails
- Test prompt building with documentation and code context
- Test response quality improvement with context
- Test backward compatibility with existing chat API

### **Day 5: Chat UI Enhancement for RAG**

#### **Task 5.1: Enhance Chat Component**
**File**: `frontend/src/components/chat/KenobiChat.jsx` (ENHANCE EXISTING)
**Integration Point**: Add context controls to existing chat interface

```jsx
const KenobiChat = ({ repositoryId }) => {
  // Existing state
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // NEW: RAG context controls
  const [useDocumentation, setUseDocumentation] = useState(true);
  const [useCode, setUseCode] = useState(true);
  const [contextSources, setContextSources] = useState([]);
  const [showContextDetails, setShowContextDetails] = useState(false);

  const sendMessage = async (message) => {
    setIsLoading(true);
    try {
      const response = await chatService.sendMessage({
        message,
        repository_id: repositoryId,
        use_documentation: useDocumentation,
        use_code: useCode
      });
      
      // Update context sources for display
      setContextSources(response.context_used || []);
      
      // Add message and response to chat
      const newMessages = [
        ...messages,
        { type: 'user', content: message, timestamp: new Date() },
        { 
          type: 'assistant', 
          content: response.response, 
          timestamp: new Date(),
          contextSources: response.context_used,
          documentationChunks: response.documentation_chunks,
          codeChunks: response.code_chunks
        }
      ];
      
      setMessages(newMessages);
      return response;
    } catch (error) {
      console.error('Chat error:', error);
      // Add error message
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Sorry, I encountered an error processing your message.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="kenobi-chat h-full flex flex-col">
      {/* Context Controls */}
      <div className="context-controls mb-4 p-3 bg-gray-50 rounded-lg border">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-sm font-medium text-gray-700">Context Sources</h4>
          <button
            onClick={() => setShowContextDetails(!showContextDetails)}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            {showContextDetails ? 'Hide Details' : 'Show Details'}
          </button>
        </div>
        
        <div className="flex gap-4">
          <label className="flex items-center">
            <input 
              type="checkbox" 
              checked={useDocumentation}
              onChange={(e) => setUseDocumentation(e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm">Use Documentation Context</span>
          </label>
          <label className="flex items-center">
            <input 
              type="checkbox" 
              checked={useCode}
              onChange={(e) => setUseCode(e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm">Use Code Context</span>
          </label>
        </div>
        
        {showContextDetails && contextSources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="text-xs text-gray-600 mb-2">
              Last response used {contextSources.length} context sources:
            </div>
            <ContextSourcesDisplay sources={contextSources} compact={true} />
          </div>
        )}
      </div>

      {/* Chat Messages */}
      <div className="chat-messages flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((message, index) => (
          <ChatMessage 
            key={index} 
            message={message} 
            showContextSources={showContextDetails}
          />
        ))}
        {isLoading && (
          <div className="flex items-center space-x-2 text-gray-500">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            <span className="text-sm">Analyzing context and generating response...</span>
          </div>
        )}
      </div>

      {/* Message Input */}
      <MessageInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
};
```

**Value Increment**: Enhanced chat UI with context awareness and transparency
**Test Requirements**:
- Test context controls toggle functionality
- Test context sources display
- Test chat message display with context information
- Test loading states during RAG processing
- Test error handling and fallback display

#### **Task 5.2: Create Context Sources Component**
**File**: `frontend/src/components/chat/ContextSourcesDisplay.jsx` (NEW)

```jsx
const ContextSourcesDisplay = ({ sources, compact = false }) => {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className={`context-sources ${compact ? 'text-xs' : 'text-sm'}`}>
      {!compact && (
        <h4 className="font-medium mb-2 text-blue-800">Context Sources Used:</h4>
      )}
      
      <div className="sources-list space-y-1">
        {sources.map((source, index) => (
          <div key={index} className="source-item flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className={`source-type px-2 py-1 rounded text-xs font-medium ${
                source.source_type === 'documentation' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-purple-100 text-purple-800'
              }`}>
                {source.source_type}
              </span>
              
              <span className="source-detail text-gray-600 truncate max-w-xs">
                {source.source_type === 'documentation' 
                  ? source.doc_type 
                  : source.element_name || source.file_path}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="relevance-score text-xs text-gray-500">
                {(source.relevance_score * 100).toFixed(0)}%
              </span>
              
              {!compact && (
                <button 
                  className="text-xs text-blue-600 hover:text-blue-800"
                  onClick={() => {/* TODO: Show full context */}}
                >
                  View
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {!compact && sources.length > 3 && (
        <div className="mt-2 text-xs text-gray-500">
          Showing top {sources.length} most relevant sources
        </div>
      )}
    </div>
  );
};
```

**Value Increment**: Transparent context source display for user understanding
**Test Requirements**:
- Test source display for different types (documentation vs code)
- Test compact vs full display modes
- Test relevance score display
- Test truncation of long source names
- Test click handlers for viewing full context

### **Day 6: Chat API Integration & Testing**

#### **Task 6.1: Update Chat Service**
**File**: `frontend/src/services/chat.js` (ENHANCE EXISTING)

```javascript
export const chatService = {
  sendMessage: async (data) => {
    try {
      const response = await api.post('/kenobi/chat', {
        message: data.message,
        repository_id: data.repository_id,
        branch: data.branch || 'main',
        use_documentation: data.use_documentation !== false,
        use_code: data.use_code !== false
      });
      
      return {
        response: response.data.response,
        context_used: response.data.context_used || [],
        documentation_chunks: response.data.documentation_chunks || 0,
        code_chunks: response.data.code_chunks || 0,
        combined_score: response.data.combined_score || 0,
        timestamp: response.data.timestamp
      };
    } catch (error) {
      console.error('Chat service error:', error);
      throw new Error('Failed to send message. Please try again.');
    }
  },

  // NEW: Get context preview without sending message
  getContextPreview: async (repositoryId, query) => {
    try {
      const response = await api.get(`/kenobi/repositories/${repositoryId}/context`, {
        params: { query }
      });
      
      return {
        documentation_available: response.data.documentation_available,
        code_available: response.data.code_available,
        sources: response.data.sources
      };
    } catch (error) {
      console.error('Context preview error:', error);
      return { documentation_available: 0, code_available: 0, sources: [] };
    }
  }
};
```

**Value Increment**: Enhanced chat service with context preview capability
**Test Requirements**:
- Test enhanced message sending with context parameters
- Test context preview functionality
- Test error handling and user-friendly error messages
- Test backward compatibility with existing chat
- Test API response parsing and validation

#### **Task 6.2: Update Chat Endpoint**
**File**: `app/main.py` (ENHANCE EXISTING)
**Integration Point**: Enhance existing chat endpoint

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    repository_id: str
    branch: str = "main"
    use_documentation: bool = True
    use_code: bool = True

@app.post("/kenobi/chat")
async def chat_with_repository(request: ChatRequest):
    """Enhanced chat with RAG context"""
    try:
        # Validate repository exists
        repository = await kenobi_agent.repository_service.get_repository_metadata(request.repository_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Generate RAG-enhanced response
        response = await kenobi_agent.chat_about_repository(
            message=request.message,
            repository_id=request.repository_id,
            branch=request.branch,
            use_documentation=request.use_documentation,
            use_code=request.use_code
        )
        
        return {
            "response": response.get("answer", "I couldn't generate a response for your question."),
            "context_used": response.get("context_used", []),
            "documentation_chunks": response.get("documentation_chunks", 0),
            "code_chunks": response.get("code_chunks", 0),
            "combined_score": response.get("combined_score", 0.0),
            "sources": response.get("sources", []),
            "repository_id": request.repository_id,
            "branch": request.branch,
            "timestamp": response.get("timestamp")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")

@app.get("/kenobi/repositories/{repository_id}/context")
async def get_repository_context(repository_id: str, query: str):
    """Get available context for a query without generating response"""
    try:
        context_service = ContextService()
        context = await context_service.get_relevant_context(
            query=query,
            repository_id=repository_id,
            max_chunks=3
        )
        
        return {
            "documentation_available": len(context["documentation"]),
            "code_available": len(context["code"]),
            "sources": context["sources"][:3],  # Preview only
            "total_score": context["combined_score"]
        }
        
    except Exception as e:
        logger.error(f"Context preview error: {e}")
        return {
            "documentation_available": 0,
            "code_available": 0,
            "sources": [],
            "total_score": 0.0
        }
```

**Value Increment**: Production-ready chat API with comprehensive error handling
**Test Requirements**:
- Test enhanced chat endpoint with all parameters
- Test context preview endpoint
- Test error handling for missing repositories
- Test response format consistency
- Test performance under load

#### **Task 6.3: Comprehensive RAG Testing**
**File**: `tests/test_phase2_rag.py` (NEW)

```python
class TestRAGIntegration:
    async def test_complete_rag_workflow(self):
        """Test complete RAG workflow from documentation to chat"""
        # 1. Create repository with documentation
        repo_data = {"id": "rag-test", "name": "RAG Test Repo", "url": "https://test.com"}
        repository = await repository_service.add_repository(repo_data)
        
        # 2. Add documentation with vector embeddings
        doc_data = {
            "overview": "This is a Python web framework for building REST APIs",
            "api_reference": "The authentication system uses JWT tokens for security"
        }
        await documentation_service.save_documentation("rag-test", doc_data)
        
        # 3. Test context retrieval
        context = await context_service.get_relevant_context(
            query="How does authentication work?",
            repository_id="rag-test"
        )
        
        assert len(context["documentation"]) > 0
        auth_context = [c for c in context["documentation"] if "authentication" in c["content"].lower()]
        assert len(auth_context) > 0
        assert auth_context[0]["relevance_score"] > 0.7
        
        # 4. Test RAG-enhanced chat
        response = await kenobi_agent.chat_about_repository(
            message="How does authentication work in this system?",
            repository_id="rag-test",
            use_documentation=True
        )
        
        assert response["documentation_chunks"] > 0
        assert "JWT" in response["answer"] or "authentication" in response["answer"].lower()
        assert len(response["context_used"]) > 0
    
    async def test_context_relevance_scoring(self):
        """Test that context relevance scoring works correctly"""
        # Create documentation with different relevance levels
        doc_data = {
            "authentication": "JWT tokens are used for user authentication",
            "database": "PostgreSQL is used for data storage",
            "caching": "Redis is used for caching frequently accessed data"
        }
        await documentation_service.save_documentation("relevance-test", doc_data)
        
        # Test authentication query
        context = await context_service.get_relevant_context(
            query="How do I authenticate users?",
            repository_id="relevance-test"
        )
        
        # Authentication context should have highest relevance
        auth_contexts = [c for c in context["documentation"] if "authentication" in c["content"].lower()]
        other_contexts = [c for c in context["documentation"] if "authentication" not in c["content"].lower()]
        
        if auth_contexts and other_contexts:
            assert auth_contexts[0]["relevance_score"] > other_contexts[0]["relevance_score"]
    
    async def test_fallback_behavior(self):
        """Test graceful fallback when RAG components fail"""
        # Test with non-existent repository
        response = await kenobi_agent.chat_about_repository(
            message="Test question",
            repository_id="non-existent",
            use_documentation=True
        )
        
        assert "not found" in response["answer"].lower()
        assert response["documentation_chunks"] == 0
        assert response["code_chunks"] == 0
    
    async def test_context_controls(self):
        """Test that context controls work correctly"""
        # Test with documentation only
        response1 = await kenobi_agent.chat_about_repository(
            message="What does this repository do?",
            repository_id="rag-test",
            use_documentation=True,
            use_code=False
        )
        
        # Test with code only
        response2 = await kenobi_agent.chat_about_repository(
            message="What does this repository do?",
            repository_id="rag-test",
            use_documentation=False,
            use_code=True
        )
        
        # Responses should be different based on context sources
        assert response1["documentation_chunks"] > 0
        assert response1["code_chunks"] == 0
        assert response2["documentation_chunks"] == 0
```

**Value Increment**: Comprehensive testing ensures RAG functionality works correctly
**Test Requirements**:
- Test complete RAG workflow end-to-end
- Test context relevance and scoring accuracy
- Test fallback behavior when components fail
- Test context control functionality
- Test performance and response quality

---

## 📋 **PHASE 3: REAL SEARCH & LLM PROVIDER INTEGRATION (Days 7-8)**
*Objective: Complete research functionality and multi-provider support*

### **Day 7: Real Search API Integration**

#### **Task 7.1: Replace Mock Search with Tavily API**
**File**: `app/tools/search_tools.py` (ENHANCE EXISTING)
**Integration Point**: Replace mock implementation with real API

```python
class WebSearchTool:
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.client = httpx.AsyncClient(timeout=30)
        self.cache_service = cache_service
        
        # Fallback to mock if no API key
        self.use_mock = not self.api_key
        if self.use_mock:
            logger.warning("No Tavily API key found, using mock search")
    
    async def search(self, query: str, search_type: str = "general") -> List[SearchResult]:
        """Search with real API and caching"""
        
        # Check cache first
        cache_key = f"search_{hashlib.md5(query.encode()).hexdigest()}"
        cached_results = self.cache_service.get(cache_key)
        if cached_results:
            logger.info(f"Returning cached search results for: {query}")
            return cached_results
        
        # Use real API if available, otherwise fallback to mock
        if self.use_mock:
            results = await self._mock_search(query)
        else:
            results = await self._tavily_search(query, search_type)
        
        # Cache results for 6 hours
        self.cache_service.set(cache_key, results, ttl=21600)
        
        return results
    
    async def _tavily_search(self, query: str, search_type: str) -> List[SearchResult]:
        """Real search using Tavily API"""
        try:
            search_payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "include_raw_content": True,
                "max_results": 10
            }
            
            # Adjust search parameters based on type
            if search_type == "academic":
                search_payload["include_domains"] = ["scholar.google.com", "arxiv.org", "pubmed.ncbi.nlm.nih.gov"]
            elif search_type == "news":
                search_payload["search_depth"] = "basic"
                search_payload["max_results"] = 15
            
            response = await self.client.post(
                "https://api.tavily.com/search",
                json=search_payload
            )
            response.raise_for_status()
            
            results_data = response.json()
            results = []
            
            for result in results_data.get("results", []):
                search_result = SearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    content=result.get("content", ""),
                    relevance_score=result.get("score", 0.5),
                    source_type=search_type,
                    published_date=result.get("published_date"),
                    domain=result.get("url", "").split("//")[-1].split("/")[0] if result.get("url") else ""
                )
                results.append(search_result)
            
            logger.info(f"Tavily search returned {len(results)} results for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            # Fallback to mock search
            return await self._mock_search(query)
    
    async def _mock_search(self, query: str) -> List[SearchResult]:
        """Enhanced mock search for development/fallback"""
        # ... existing mock implementation enhanced with better relevance scoring ...
        
        mock_results = [
            SearchResult(
                title=f"Mock Result for '{query}' - Technical Documentation",
                url=f"https://example.com/docs/{query.replace(' ', '-')}",
                content=f"This is a mock search result for '{query}'. In production, this would be replaced with real search results from Tavily API.",
                relevance_score=0.8,
                source_type="documentation"
            ),
            SearchResult(
                title=f"Mock Result for '{query}' - Implementation Guide",
                url=f"https://example.com/guide/{query.replace(' ', '-')}",
                content=f"Implementation guide for '{query}' with step-by-step instructions and best practices.",
                relevance_score=0.7,
                source_type="tutorial"
            )
        ]
        
        return mock_results
```

**Value Increment**: Real search capability with graceful fallback to mock
**Test Requirements**:
- Test real API integration with valid API key
- Test fallback to mock when API key missing
- Test caching functionality and TTL
- Test different search types (general, academic, news)
- Test error handling and API failure recovery

### **Day 8: LLM Provider Integration**

#### **Task 8.1: Create LLM Provider Service**
**File**: `app/services/llm_service.py` (NEW)
**Integration Point**: Centralize LLM provider management

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import httpx
import json

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, model: str = None, **kwargs) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available"""
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass

class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL or "http://localhost:11434"
        self.client = httpx.AsyncClient(timeout=60)
        self.current_model = settings.OLLAMA_MODEL or "llama3.2:1b"
    
    async def generate(self, prompt: str, model: str = None, **kwargs) -> str:
        """Generate response using Ollama"""
        model_name = model or self.current_model
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 1000)
                    }
                }
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    async def get_available_models(self) -> List[str]:
        """Get available Ollama models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except:
            pass
        return [self.current_model]

class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.client = httpx.AsyncClient(timeout=60)
        self.current_model = "claude-3-sonnet-20240229"
    
    async def generate(self, prompt: str, model: str = None, **kwargs) -> str:
        """Generate response using Anthropic Claude"""
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")
        
        model_name = model or self.current_model
        
        try:
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": model_name,
                    "max_tokens": kwargs.get("max_tokens", 1000),
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.get("temperature", 0.7)
                }
            )
            response.raise_for_status()
            
            result = response.json()
            return result["content"][0]["text"]
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Check if Anthropic API is available"""
        return bool(self.api_key)
    
    async def get_available_models(self) -> List[str]:
        """Get available Anthropic models"""
        if self.api_key:
            return ["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229"]
        return []

class LLMService:
    """Centralized LLM service with provider management"""
    
    def __init__(self):
        self.providers = {
            "ollama": OllamaProvider(),
            "anthropic": AnthropicProvider(),
        }
        self.current_provider = settings.DEFAULT_LLM_PROVIDER or "ollama"
    
    async def generate_response(self, prompt: str, provider: str = None, model: str = None, **kwargs) -> str:
        """Generate response using specified or default provider"""
        provider_name = provider or self.current_provider
        provider_instance = self.providers.get(provider_name)
        
        if not provider_instance:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        # Check if provider is available
        if not await provider_instance.is_available():
            # Fallback to Ollama if available
            if provider_name != "ollama" and await self.providers["ollama"].is_available():
                logger.warning(f"Provider {provider_name} unavailable, falling back to Ollama")
                provider_instance = self.providers["ollama"]
            else:
                raise ValueError(f"Provider {provider_name} is not available")
        
        return await provider_instance.generate(prompt, model, **kwargs)
    
    async def switch_provider(self, provider: str, model: str = None):
        """Switch default LLM provider"""
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        if not await self.providers[provider].is_available():
            raise ValueError(f"Provider {provider} is not available")
        
        self.current_provider = provider
        if model:
            self.providers[provider].current_model = model
    
    async def get_available_providers(self) -> Dict[str, Any]:
        """Get available providers and their models"""
        providers_info = {}
        for name, provider in self.providers.items():
            providers_info[name] = {
                "available": await provider.is_available(),
                "models": await provider.get_available_models(),
                "current_model": getattr(provider, 'current_model', None)
            }
        return providers_info
```

**Value Increment**: Multi-provider LLM support with automatic fallback
**Test Requirements**:
- Test each provider individually
- Test provider switching functionality
- Test fallback behavior when providers fail
- Test model selection within providers
- Test availability checking

#### **Task 8.2: Integrate LLM Service with Kenobi Agent**
**File**: `app/agents/kenobi_agent.py` (ENHANCE EXISTING)
**Integration Point**: Replace direct LLM calls with service

```python
class KenobiAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # ... existing initialization ...
        
        # NEW: Use centralized LLM service
        self.llm_service = LLMService()
    
    async def _call_llm(self, prompt: str, max_tokens: int = 500, provider: str = None, model: str = None) -> str:
        """Enhanced LLM call with provider selection"""
        try:
            response = await self.llm_service.generate_response(
                prompt=prompt,
                provider=provider,
                model=model,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."
```

**Value Increment**: Centralized LLM management with improved reliability
**Test Requirements**:
- Test LLM service integration with existing agent
- Test provider selection in chat responses
- Test error handling and fallback
- Test performance comparison between providers
- Test backward compatibility with existing functionality

---

## 📋 **PHASE 4: PRODUCTION MONITORING & TESTING (Days 9-10)**
*Objective: Production-ready monitoring, logging, and comprehensive testing*

### **Day 9: Production Monitoring & Logging**

#### **Task 9.1: Enhanced Logging System**
**File**: `app/monitoring/logging_config.py` (NEW)

```python
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar

# Context variable for correlation IDs
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id.get(''),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'repository_id'):
            log_entry['repository_id'] = record.repository_id
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        
        return json.dumps(log_entry)

class LoggingConfig:
    def __init__(self):
        self.setup_structured_logging()
    
    def setup_structured_logging(self):
        """Setup structured logging with correlation IDs"""
        # Create structured formatter
        formatter = StructuredFormatter()
        
        # Setup file handler
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(formatter)
        
        # Setup console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    @staticmethod
    def set_correlation_id(corr_id: str = None):
        """Set correlation ID for request tracking"""
        if corr_id is None:
            corr_id = str(uuid.uuid4())
        correlation_id.set(corr_id)
        return corr_id
    
    @staticmethod
    def log_operation(operation: str, repository_id: str = None, duration: float = None, **kwargs):
        """Log operation with structured data"""
        logger = logging.getLogger("operations")
        logger.info(
            f"Operation: {operation}",
            extra={
                "operation": operation,
                "repository_id": repository_id,
                "duration": duration,
                **kwargs
            }
        )
```

**Value Increment**: Structured logging for production monitoring and debugging
**Test Requirements**:
- Test correlation ID tracking across requests
- Test structured log format and parsing
- Test log aggregation and searching
- Test performance impact of logging
- Test log rotation and retention

#### **Task 9.2: Health Monitoring System**
**File**: `app/monitoring/health_monitor.py` (NEW)

```python
class HealthMonitor:
    def __init__(self):
        self.db_service = DatabaseService()
        self.llm_service = LLMService()
        self.vector_service = VectorService()
        self.cache_service = cache_service
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        health_checks = await asyncio.gather(
            self._check_database_health(),
            self._check_llm_providers_health(),
            self._check_vector_service_health(),
            self._check_cache_health(),
            return_exceptions=True
        )
        
        database_health, llm_health, vector_health, cache_health = health_checks
        
        # Determine overall system status
        all_healthy = all(
            isinstance(check, dict) and check.get("status") == "healthy"
            for check in health_checks
            if not isinstance(check, Exception)
        )
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": database_health if not isinstance(database_health, Exception) else {"status": "error", "error": str(database_health)},
                "llm_providers": llm_health if not isinstance(llm_health, Exception) else {"status": "error", "error": str(llm_health)},
                "vector_service": vector_health if not isinstance(vector_health, Exception) else {"status": "error", "error": str(vector_health)},
                "cache": cache_health if not isinstance(cache_health, Exception) else {"status": "error", "error": str(cache_health)}
            }
        }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        start_time = time.time()
        try:
            # Test database connection
            async with self.db_service.session_factory() as session:
                await session.execute(text("SELECT 1"))
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "connection_pool_size": getattr(self.db_service.engine.pool, 'size', 'unknown')
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round((time.time() - start_time) * 1000, 2)
            }
    
    async def _check_llm_providers_health(self) -> Dict[str, Any]:
        """Check LLM provider availability"""
        providers_status = {}
        
        for name, provider in self.llm_service.providers.items():
            try:
                is_available = await provider.is_available()
                models = await provider.get_available_models() if is_available else []
                
                providers_status[name] = {
                    "status": "healthy" if is_available else "unavailable",
                    "available_models": len(models),
                    "models": models[:3]  # Show first 3 models
                }
            except Exception as e:
                providers_status[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Overall LLM health
        any_healthy = any(p.get("status") == "healthy" for p in providers_status.values())
        
        return {
            "status": "healthy" if any_healthy else "unhealthy",
            "providers": providers_status,
            "current_provider": self.llm_service.current_provider
        }
    
    async def _check_vector_service_health(self) -> Dict[str, Any]:
        """Check vector service health"""
        try:
            # Test vector service with a simple operation
            test_doc = VectorDocument(
                id="health_check",
                content="health check test",
                metadata={"test": True}
            )
            
            # This should not actually store the document
            start_time = time.time()
            # await self.vector_service.search("test", limit=1)  # Simple search test
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "backend": "chromadb" if CHROMADB_AVAILABLE else "in_memory"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache service health"""
        try:
            # Test cache operations
            test_key = "health_check"
            test_value = {"timestamp": datetime.utcnow().isoformat()}
            
            # Test set/get
            self.cache_service.set(test_key, test_value, ttl=60)
            retrieved = self.cache_service.get(test_key)
            
            cache_working = retrieved == test_value
            
            return {
                "status": "healthy" if cache_working else "degraded",
                "backend": "redis" if hasattr(self.cache_service, 'redis_client') else "in_memory",
                "test_passed": cache_working
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Add health endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_monitor = HealthMonitor()
    return await health_monitor.get_system_health()

@app.get("/health/simple")
async def simple_health_check():
    """Simple health check for load balancers"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
```

**Value Increment**: Comprehensive health monitoring for production deployment
**Test Requirements**:
- Test health check accuracy for each component
- Test health check performance and timeout handling
- Test health status aggregation logic
- Test health endpoint response format
- Test monitoring integration with alerting systems

### **Day 10: Comprehensive Testing & Performance Optimization**

#### **Task 10.1: End-to-End Integration Testing**
**File**: `tests/test_complete_system.py` (NEW)

```python
class TestCompleteSystem:
    """Comprehensive end-to-end system testing"""
    
    async def test_complete_workflow_with_persistence(self):
        """Test complete workflow with database persistence"""
        # 1. Add repository
        repo_data = {
            "id": "e2e-test-repo",
            "name": "End-to-End Test Repository",
            "url": "https://github.com/test/e2e-repo"
        }
        
        repository = await repository_service.add_repository(repo_data)
        assert repository.id == "e2e-test-repo"
        
        # 2. Generate documentation
        doc_data = {
            "overview": "This is a comprehensive test repository for end-to-end testing",
            "api_reference": "API endpoints for user authentication and data management",
            "architecture": "Microservices architecture with event-driven communication"
        }
        
        documentation = await documentation_service.save_documentation("e2e-test-repo", doc_data)
        assert documentation.vector_indexed == True
        
        # 3. Test RAG-enhanced chat
        response = await kenobi_agent.chat_about_repository(
            message="How is the system architected?",
            repository_id="e2e-test-repo",
            use_documentation=True,
            use_code=True
        )
        
        assert response["documentation_chunks"] > 0
        assert "microservices" in response["answer"].lower() or "architecture" in response["answer"].lower()
        assert len(response["context_used"]) > 0
        
        # 4. Test persistence across restart simulation
        # Clear caches to simulate restart
        repository_service.repositories.clear()
        cache_service.clear_all()
        
        # Verify data is still accessible
        persisted_repo = await repository_service.get_repository_metadata("e2e-test-repo")
        assert persisted_repo.name == "End-to-End Test Repository"
        
        persisted_doc = await documentation_service.get_documentation("e2e-test-repo")
        assert persisted_doc["overview"] == doc_data["overview"]
        
        # 5. Test search functionality
        search_results = await search_tool.search("microservices architecture")
        assert len(search_results) > 0
    
    async def test_performance_benchmarks(self):
        """Test system performance under load"""
        # Test repository operations performance
        start_time = time.time()
        
        # Create multiple repositories
        tasks = []
        for i in range(10):
            repo_data = {
                "id": f"perf-test-{i}",
                "name": f"Performance Test Repository {i}",
                "url": f"https://github.com/test/perf-{i}"
            }
            tasks.append(repository_service.add_repository(repo_data))
        
        await asyncio.gather(*tasks)
        creation_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        retrieval_tasks = [
            repository_service.get_repository_metadata(f"perf-test-{i}")
            for i in range(10)
        ]
        await asyncio.gather(*retrieval_tasks)
        retrieval_time = time.time() - start_time
        
        # Performance assertions
        assert creation_time < 5.0  # Should create 10 repos in under 5 seconds
        assert retrieval_time < 1.0  # Should retrieve 10 repos in under 1 second (cached)
        
        # Test chat performance
        start_time = time.time()
        response = await kenobi_agent.chat_about_repository(
            message="What does this repository do?",
            repository_id="perf-test-0",
            use_documentation=True
        )
        chat_time = time.time() - start_time
        
        assert chat_time < 10.0  # Chat should respond within 10 seconds
        assert len(response["answer"]) > 10  # Should generate meaningful response
    
    async def test_error_handling_and_recovery(self):
        """Test system behavior under error conditions"""
        # Test with invalid repository ID
        response = await kenobi_agent.chat_about_repository(
            message="Test question",
            repository_id="non-existent-repo"
        )
        assert "not found" in response["answer"].lower()
        
        # Test with database unavailable (mock)
        # This would require dependency injection to mock database failures
        
        # Test with LLM provider unavailable
        # Save current provider
        original_provider = kenobi_agent.llm_service.current_provider
        
        # Switch to unavailable provider
        try:
            await kenobi_agent.llm_service.switch_provider("invalid-provider")
            assert False, "Should have raised exception"
        except ValueError:
            pass  # Expected
        
        # Verify system still works with original provider
        assert kenobi_agent.llm_service.current_provider == original_provider
    
    async def test_concurrent_operations(self):
        """Test system behavior under concurrent load"""
        # Test concurrent documentation generation
        tasks = []
        for i in range(5):
            repo_id = f"concurrent-test-{i}"
            doc_data = {
                "overview": f"Concurrent test repository {i}",
                "api_reference": f"API documentation for repository {i}"
            }
            tasks.append(documentation_service.save_documentation(repo_id, doc_data))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All operations should succeed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 5
        
        # Test concurrent chat operations
        chat_tasks = []
        for i in range(3):
            chat_tasks.append(kenobi_agent.chat_about_repository(
                message=f"What is the purpose of repository {i}?",
                repository_id=f"concurrent-test-{i}"
            ))
        
        chat_results = await asyncio.gather(*chat_tasks, return_exceptions=True)
        successful_chats = [r for r in chat_results if not isinstance(r, Exception)]
        assert len(successful_chats) >= 2  # At least 2 should succeed
```

**Value Increment**: Comprehensive system validation and performance benchmarking
**Test Requirements**:
- Test complete workflow end-to-end
- Test performance under various load conditions
- Test error handling and recovery mechanisms
- Test concurrent operations and race conditions
- Test data persistence and system restart scenarios

#### **Task 10.2: Performance Optimization**
**File**: `app/performance/optimization.py` (NEW)

```python
class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    def __init__(self):
        self.metrics = {}
    
    async def optimize_database_queries(self):
        """Optimize database query performance"""
        # Add database indexes for common queries
        async with db_service.engine.begin() as conn:
            # Index for repository lookups
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_repositories_id ON repositories(id)"
            ))
            
            # Index for documentation lookups
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_documentation_repo_id ON documentation(repository_id)"
            ))
            
            # Index for documentation by generation date
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_documentation_generated_at ON documentation(generated_at DESC)"
            ))
    
    async def optimize_vector_search(self):
        """Optimize vector search performance"""
        # Configure vector service for better performance
        if hasattr(vector_service, 'configure_performance'):
            await vector_service.configure_performance({
                "batch_size": 100,
                "cache_size": 1000,
                "index_type": "hnsw"  # Hierarchical Navigable Small World
            })
    
    async def optimize_cache_settings(self):
        """Optimize cache configuration"""
        # Configure cache TTL based on data type
        cache_service.configure_ttl({
            "repositories": 3600,  # 1 hour
            "documentation": 1800,  # 30 minutes
            "search_results": 21600,  # 6 hours
            "context_results": 900  # 15 minutes
        })
    
    def track_performance_metric(self, operation: str, duration: float, success: bool):
        """Track performance metrics"""
        if operation not in self.metrics:
            self.metrics[operation] = {
                "total_calls": 0,
                "total_duration": 0.0,
                "success_count": 0,
                "failure_count": 0,
                "avg_duration": 0.0,
                "success_rate": 0.0
            }
        
        metric = self.metrics[operation]
        metric["total_calls"] += 1
        metric["total_duration"] += duration
        
        if success:
            metric["success_count"] += 1
        else:
            metric["failure_count"] += 1
        
        metric["avg_duration"] = metric["total_duration"] / metric["total_calls"]
        metric["success_rate"] = metric["success_count"] / metric["total_calls"]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": self.metrics,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        for operation, metric in self.metrics.items():
            if metric["avg_duration"] > 5.0:
                recommendations.append(f"Consider optimizing {operation} - average duration {metric['avg_duration']:.2f}s")
            
            if metric["success_rate"] < 0.95:
                recommendations.append(f"Improve reliability of {operation} - success rate {metric['success_rate']:.1%}")
        
        return recommendations

# Initialize performance optimizer
performance_optimizer = PerformanceOptimizer()

# Add performance tracking middleware
@app.middleware("http")
async def performance_tracking_middleware(request: Request, call_next):
    """Track request performance"""
    start_time = time.time()
    correlation_id = LoggingConfig.set_correlation_id()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        success = response.status_code < 400
        
        # Track performance
        operation = f"{request.method} {request.url.path}"
        performance_optimizer.track_performance_metric(operation, duration, success)
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        operation = f"{request.method} {request.url.path}"
        performance_optimizer.track_performance_metric(operation, duration, False)
        raise

@app.get("/admin/performance")
async def get_performance_metrics():
    """Get system performance metrics"""
    return performance_optimizer.get_performance_report()
```

**Value Increment**: Production-ready performance monitoring and optimization
**Test Requirements**:
- Test performance optimization effectiveness
- Test metrics collection accuracy
- Test performance tracking middleware
- Test database index creation and effectiveness
- Test cache optimization impact

---

## 🎯 **COMPREHENSIVE SUCCESS CRITERIA**

### **Phase 1 Success Criteria (Database Foundation)**
- ✅ All repository data persists across service restarts
- ✅ Database operations complete within 100ms (cached) / 500ms (uncached)
- ✅ Cache hit rate > 80% for frequently accessed data
- ✅ Zero data loss during database operations
- ✅ Existing documentation migrated successfully
- ✅ Backward compatibility maintained with existing APIs

### **Phase 2 Success Criteria (RAG Integration)**
- ✅ Chat responses include relevant documentation context
- ✅ Context relevance score > 70% for user queries
- ✅ Response time < 3 seconds for RAG-enhanced chat
- ✅ Users can see and understand context sources used
- ✅ Vector embeddings created for all documentation
- ✅ Graceful fallback when RAG components fail

### **Phase 3 Success Criteria (Search & LLM Integration)**
- ✅ Real search API integration with < 2 second response time
- ✅ Search results cached for 6 hours to reduce API calls
- ✅ LLM provider switching functional (Ollama, Anthropic)
- ✅ Provider selection UI working with model management
- ✅ Automatic fallback between providers when one fails

### **Phase 4 Success Criteria (Production Ready)**
- ✅ Comprehensive logging with correlation IDs
- ✅ Health monitoring endpoints functional
- ✅ Test coverage > 80% for critical components
- ✅ Performance benchmarks within acceptable limits
- ✅ Error handling and recovery mechanisms tested
- ✅ System performs well under concurrent load

---

## 📊 **TESTING STRATEGY SUMMARY**

### **Continuous Testing Approach**
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user workflows
- **Performance Tests**: Validate system performance under load
- **Regression Tests**: Ensure new changes don't break existing functionality

### **Test Execution Schedule**
- **After Each Task**: Unit tests for new/modified components
- **End of Each Day**: Integration tests for daily deliverables
- **End of Each Phase**: Comprehensive end-to-end testing
- **Before Production**: Full regression and performance testing

### **Quality Gates**
- All tests must pass before proceeding to next task
- Performance benchmarks must be met
- Code coverage must exceed 80% for critical paths
- Manual testing must confirm user experience improvements

This detailed implementation plan ensures each phase delivers valuable increments while maintaining system stability and providing comprehensive testing coverage.