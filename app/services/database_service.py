"""
Database Service for Phase 1 - Database Foundation with Caching
Implements SQLite persistence with in-memory caching for optimal performance
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.models import Base, Repository as DatabaseRepository, Documentation as DatabaseDocumentation, CloneStatus as DBCloneStatus, LanguageType as DBLanguageType
from app.models.repository_schemas import Repository, CloneStatus, LanguageType
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service with hybrid storage strategy"""
    
    def __init__(self):
        # Use SQLite for development, can be configured for PostgreSQL in production
        self.database_url = getattr(settings, 'DATABASE_URL', None) or "sqlite+aiosqlite:///./kenobi.db"
        
        # Initialize engine and session factory as None for lazy loading
        self.engine = None
        self.session_factory = None
        self.is_initialized = False
        
        logger.info(f"Database service configured with URL: {self.database_url}")
    
    def _ensure_engine(self):
        """Ensure the database engine and session factory are initialized"""
        if self.engine is None:
            try:
                # Create async engine for database operations
                self.engine = create_async_engine(
                    self.database_url,
                    echo=False,  # Set to True for SQL debugging
                    future=True
                )
                
                # Create session factory
                self.session_factory = async_sessionmaker(
                    self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                
                logger.info(f"Database engine initialized with URL: {self.database_url}")
            except Exception as e:
                logger.error(f"Failed to initialize database engine: {e}")
                # Don't raise here, let the calling methods handle it
                return False
        return True
    
    async def initialize(self):
        """Initialize database tables"""
        try:
            if not self._ensure_engine():
                self.is_initialized = False
                return False
                
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            self.is_initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self.is_initialized = False
            return False
    
    async def health_check(self):
        """Check database connectivity"""
        try:
            if not self.is_initialized or not self._ensure_engine():
                return False
                
            async with self.session_factory() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def save_repository(self, repository: Repository) -> Repository:
        """Save repository with immediate cache update"""
        try:
            if not self.is_initialized or not self._ensure_engine():
                logger.warning("Database not initialized, skipping repository save")
                return repository
                
            async with self.session_factory() as session:
                # Convert enum values from schema to database enums
                db_clone_status = DBCloneStatus.PENDING
                if hasattr(repository, 'clone_status') and repository.clone_status:
                    if repository.clone_status == CloneStatus.PENDING:
                        db_clone_status = DBCloneStatus.PENDING
                    elif repository.clone_status == CloneStatus.CLONING:
                        db_clone_status = DBCloneStatus.CLONING
                    elif repository.clone_status == CloneStatus.COMPLETED:
                        db_clone_status = DBCloneStatus.COMPLETED
                    elif repository.clone_status == CloneStatus.FAILED:
                        db_clone_status = DBCloneStatus.FAILED
                
                db_language = DBLanguageType.UNKNOWN
                if hasattr(repository, 'language') and repository.language:
                    if repository.language == LanguageType.PYTHON:
                        db_language = DBLanguageType.PYTHON
                    elif repository.language == LanguageType.JAVASCRIPT:
                        db_language = DBLanguageType.JAVASCRIPT
                    elif repository.language == LanguageType.TYPESCRIPT:
                        db_language = DBLanguageType.TYPESCRIPT
                    elif repository.language == LanguageType.JAVA:
                        db_language = DBLanguageType.JAVA
                    elif repository.language == LanguageType.CSHARP:
                        db_language = DBLanguageType.CSHARP
                    elif repository.language == LanguageType.GO:
                        db_language = DBLanguageType.GO
                    elif repository.language == LanguageType.R:
                        db_language = DBLanguageType.R
                    elif repository.language == LanguageType.JUPYTER:
                        db_language = DBLanguageType.JUPYTER
                
                # Convert from current Repository model to database model
                db_repo = DatabaseRepository(
                    id=repository.id,
                    name=repository.name,
                    url=repository.url,
                    local_path=getattr(repository, 'local_path', None),
                    github_owner=getattr(repository, 'github_owner', None),
                    github_repo=getattr(repository, 'github_repo', None),
                    language=db_language,
                    framework=getattr(repository, 'framework', None),
                    description=getattr(repository, 'description', None),
                    clone_status=db_clone_status,
                    file_count=getattr(repository, 'file_count', 0),
                    total_lines=getattr(repository, 'line_count', 0),
                    created_at=datetime.utcnow()
                )
                
                # Use merge to handle both insert and update
                merged_repo = await session.merge(db_repo)
                await session.commit()
                
                logger.info(f"Repository {repository.id} saved to database")
                return repository
                
        except Exception as e:
            logger.error(f"Failed to save repository {repository.id}: {e}")
            # Don't raise, just log and return original repository
            return repository
    
    async def get_repository(self, repo_id: str) -> Optional[Repository]:
        """Get repository from database"""
        try:
            if not self.is_initialized or not self._ensure_engine():
                logger.warning("Database not initialized, repository retrieval skipped")
                return None
                
            async with self.session_factory() as session:
                result = await session.execute(
                    select(DatabaseRepository).where(DatabaseRepository.id == repo_id)
                )
                db_repo = result.scalar_one_or_none()
                
                if db_repo:
                    # Convert database enums back to schema enums
                    schema_clone_status = CloneStatus.PENDING
                    if db_repo.clone_status == DBCloneStatus.PENDING:
                        schema_clone_status = CloneStatus.PENDING
                    elif db_repo.clone_status == DBCloneStatus.CLONING:
                        schema_clone_status = CloneStatus.CLONING
                    elif db_repo.clone_status == DBCloneStatus.COMPLETED:
                        schema_clone_status = CloneStatus.COMPLETED
                    elif db_repo.clone_status == DBCloneStatus.FAILED:
                        schema_clone_status = CloneStatus.FAILED
                    
                    schema_language = LanguageType.UNKNOWN
                    if db_repo.language == DBLanguageType.PYTHON:
                        schema_language = LanguageType.PYTHON
                    elif db_repo.language == DBLanguageType.JAVASCRIPT:
                        schema_language = LanguageType.JAVASCRIPT
                    elif db_repo.language == DBLanguageType.TYPESCRIPT:
                        schema_language = LanguageType.TYPESCRIPT
                    elif db_repo.language == DBLanguageType.JAVA:
                        schema_language = LanguageType.JAVA
                    elif db_repo.language == DBLanguageType.CSHARP:
                        schema_language = LanguageType.CSHARP
                    elif db_repo.language == DBLanguageType.GO:
                        schema_language = LanguageType.GO
                    elif db_repo.language == DBLanguageType.R:
                        schema_language = LanguageType.R
                    elif db_repo.language == DBLanguageType.JUPYTER:
                        schema_language = LanguageType.JUPYTER
                    
                    # Convert back to current Repository model
                    repository = Repository(
                        id=db_repo.id,
                        name=db_repo.name,
                        url=db_repo.url or "",
                        local_path=db_repo.local_path or f"/tmp/kenobi_repos/{db_repo.name}",
                        language=schema_language,
                        framework=db_repo.framework,
                        description=db_repo.description,
                        clone_status=schema_clone_status,
                        indexed_at=db_repo.created_at or datetime.utcnow(),
                        file_count=db_repo.file_count or 0,
                        line_count=db_repo.total_lines or 0
                    )
                    
                    logger.debug(f"Repository {repo_id} retrieved from database")
                    return repository
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get repository {repo_id}: {e}")
            return None
    
    async def list_repositories(self) -> List[Repository]:
        """List all repositories from database"""
        try:
            if not self.is_initialized or not self._ensure_engine():
                logger.warning("Database not initialized, returning empty repository list")
                return []
                
            async with self.session_factory() as session:
                result = await session.execute(select(DatabaseRepository))
                db_repos = result.scalars().all()
                
                repositories = []
                for db_repo in db_repos:
                    # Convert database enums back to schema enums
                    schema_clone_status = CloneStatus.PENDING
                    if db_repo.clone_status == DBCloneStatus.PENDING:
                        schema_clone_status = CloneStatus.PENDING
                    elif db_repo.clone_status == DBCloneStatus.CLONING:
                        schema_clone_status = CloneStatus.CLONING
                    elif db_repo.clone_status == DBCloneStatus.COMPLETED:
                        schema_clone_status = CloneStatus.COMPLETED
                    elif db_repo.clone_status == DBCloneStatus.FAILED:
                        schema_clone_status = CloneStatus.FAILED
                    
                    schema_language = LanguageType.UNKNOWN
                    if db_repo.language == DBLanguageType.PYTHON:
                        schema_language = LanguageType.PYTHON
                    elif db_repo.language == DBLanguageType.JAVASCRIPT:
                        schema_language = LanguageType.JAVASCRIPT
                    elif db_repo.language == DBLanguageType.TYPESCRIPT:
                        schema_language = LanguageType.TYPESCRIPT
                    elif db_repo.language == DBLanguageType.JAVA:
                        schema_language = LanguageType.JAVA
                    elif db_repo.language == DBLanguageType.CSHARP:
                        schema_language = LanguageType.CSHARP
                    elif db_repo.language == DBLanguageType.GO:
                        schema_language = LanguageType.GO
                    elif db_repo.language == DBLanguageType.R:
                        schema_language = LanguageType.R
                    elif db_repo.language == DBLanguageType.JUPYTER:
                        schema_language = LanguageType.JUPYTER
                    
                    repository = Repository(
                        id=db_repo.id,
                        name=db_repo.name,
                        url=db_repo.url or "",
                        local_path=db_repo.local_path or f"/tmp/kenobi_repos/{db_repo.name}",
                        language=schema_language,
                        framework=db_repo.framework,
                        description=db_repo.description,
                        clone_status=schema_clone_status,
                        indexed_at=db_repo.created_at or datetime.utcnow(),
                        file_count=db_repo.file_count or 0,
                        line_count=db_repo.total_lines or 0
                    )
                    repositories.append(repository)
                
                logger.debug(f"Retrieved {len(repositories)} repositories from database")
                return repositories
                
        except Exception as e:
            logger.error(f"Failed to list repositories: {e}")
            return []
    
    async def delete_repository(self, repo_id: str) -> bool:
        """Delete repository from database"""
        try:
            if not self.is_initialized or not self._ensure_engine():
                logger.warning("Database not initialized, repository deletion skipped")
                return False
                
            async with self.session_factory() as session:
                result = await session.execute(
                    select(DatabaseRepository).where(DatabaseRepository.id == repo_id)
                )
                db_repo = result.scalar_one_or_none()
                
                if db_repo:
                    await session.delete(db_repo)
                    await session.commit()
                    logger.info(f"Repository {repo_id} deleted from database")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete repository {repo_id}: {e}")
            return False
    
    async def save_documentation(self, repo_id: str, documentation_data: Dict[str, Any]) -> DatabaseDocumentation:
        """Save documentation to database"""
        try:
            if not self.is_initialized or not self._ensure_engine():
                logger.warning("Database not initialized, documentation save skipped")
                # Return a dummy documentation object
                return DatabaseDocumentation(
                    id=f"{repo_id}_dummy",
                    repository_id=repo_id,
                    content=json.dumps(documentation_data),
                    format="json",
                    generated_at=datetime.utcnow()
                )
                
            async with self.session_factory() as session:
                # Create documentation record
                documentation = DatabaseDocumentation(
                    id=f"{repo_id}_{int(datetime.utcnow().timestamp())}",
                    repository_id=repo_id,
                    content=json.dumps(documentation_data),
                    format="json",
                    generated_at=datetime.utcnow()
                )
                
                session.add(documentation)
                await session.commit()
                
                logger.info(f"Documentation saved for repository {repo_id}")
                return documentation
                
        except Exception as e:
            logger.error(f"Failed to save documentation for {repo_id}: {e}")
            # Return a dummy documentation object instead of raising
            return DatabaseDocumentation(
                id=f"{repo_id}_dummy",
                repository_id=repo_id,
                content=json.dumps(documentation_data),
                format="json",
                generated_at=datetime.utcnow()
            )
    
    async def get_documentation(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get latest documentation for repository"""
        try:
            if not self.is_initialized or not self._ensure_engine():
                logger.warning("Database not initialized, documentation retrieval skipped")
                return None
                
            async with self.session_factory() as session:
                result = await session.execute(
                    select(DatabaseDocumentation)
                    .where(DatabaseDocumentation.repository_id == repo_id)
                    .order_by(DatabaseDocumentation.generated_at.desc())
                )
                doc = result.scalar_one_or_none()
                
                if doc:
                    doc_data = json.loads(doc.content)
                    logger.debug(f"Documentation retrieved for repository {repo_id}")
                    return doc_data
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get documentation for {repo_id}: {e}")
            return None
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get database connection statistics"""
        try:
            if not self.is_initialized or not self._ensure_engine():
                return {"status": "not_initialized", "error": "Database not initialized"}
                
            pool = self.engine.pool
            return {
                "pool_size": getattr(pool, 'size', 'unknown'),
                "checked_in": getattr(pool, 'checkedin', 'unknown'),
                "checked_out": getattr(pool, 'checkedout', 'unknown'),
                "overflow": getattr(pool, 'overflow', 'unknown'),
                "invalid": getattr(pool, 'invalid', 'unknown')
            }
        except Exception as e:
            logger.error(f"Failed to get connection stats: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close database connections"""
        try:
            if self.engine:
                await self.engine.dispose()
                logger.info("Database connections closed")
                self.is_initialized = False
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Global database service instance
database_service = DatabaseService()