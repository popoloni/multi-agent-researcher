"""
Documentation Service for Multi-Agent Researcher
Implements database persistence with cache-first strategy and vector preparation
"""

import uuid
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass

from app.services.database_service import database_service
from app.services.cache_service import cache_service
from app.database.models import Documentation, Repository
from app.engines.vector_service import VectorService
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


@dataclass
class DocumentationChunk:
    """Text chunk for vector embedding"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    start_index: int
    end_index: int


@dataclass
class DocumentationResult:
    """Result of documentation operations"""
    documentation: Documentation
    chunks: List[DocumentationChunk]
    cached: bool = False


class DocumentationService:
    """
    Documentation service with database persistence and cache-first strategy
    Prepares documentation for RAG integration with vector embeddings
    """
    
    def __init__(self):
        self.db_service = database_service
        self.vector_service = VectorService()
        self.cache_service = cache_service
        self._cache_prefix = "doc:"
        self._chunk_size = 1000  # Characters per chunk for vector embedding
        self._chunk_overlap = 200  # Overlap between chunks
        
    async def save_documentation(
        self, 
        repo_id: str, 
        documentation_data: Dict[str, Any],
        branch: str = "main"
    ) -> DocumentationResult:
        """
        Save documentation with database persistence and vector preparation
        
        Args:
            repo_id: Repository identifier
            documentation_data: Documentation content and metadata
            branch: Repository branch (for future multi-branch support)
            
        Returns:
            DocumentationResult with documentation and prepared chunks
        """
        try:
            # Generate unique documentation ID
            doc_id = self._generate_doc_id(repo_id, branch)
            
            # Extract content from documentation_data
            content = self._extract_content(documentation_data)
            
            # Create documentation object
            documentation = Documentation(
                id=doc_id,
                repository_id=repo_id,
                content=content,
                format="markdown",
                vector_indexed=False,  # Will be set to True when vector indexing is complete
                generated_at=datetime.utcnow()
            )
            
            # Save to database
            async with self.db_service.session_factory() as session:
                # Check if documentation already exists
                existing_doc = await session.get(Documentation, doc_id)
                if existing_doc:
                    # Update existing documentation
                    existing_doc.content = content
                    existing_doc.generated_at = datetime.utcnow()
                    existing_doc.vector_indexed = False
                    documentation = existing_doc
                else:
                    # Add new documentation
                    session.add(documentation)
                
                await session.commit()
                await session.refresh(documentation)
            
            # Prepare text chunks for vector embedding
            chunks = self._prepare_text_chunks(content, repo_id, doc_id)
            
            # Cache the documentation for fast retrieval
            cache_key = f"{self._cache_prefix}{doc_id}"
            await self.cache_service.set(
                cache_key,
                {
                    "documentation": documentation,
                    "chunks": chunks,
                    "cached_at": datetime.utcnow().isoformat()
                },
                ttl=3600  # Cache for 1 hour
            )
            
            logger.info(f"Documentation saved for repository {repo_id}, {len(chunks)} chunks prepared")
            
            return DocumentationResult(
                documentation=documentation,
                chunks=chunks,
                cached=False
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error saving documentation for {repo_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving documentation for {repo_id}: {e}")
            raise
    
    async def get_documentation(
        self, 
        repo_id: str, 
        branch: str = "main"
    ) -> Optional[DocumentationResult]:
        """
        Get documentation with cache-first strategy
        
        Args:
            repo_id: Repository identifier
            branch: Repository branch
            
        Returns:
            DocumentationResult if found, None otherwise
        """
        try:
            doc_id = self._generate_doc_id(repo_id, branch)
            cache_key = f"{self._cache_prefix}{doc_id}"
            
            # 1. Check cache first
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                logger.debug(f"Documentation cache hit for {repo_id}")
                return DocumentationResult(
                    documentation=cached_data["documentation"],
                    chunks=cached_data["chunks"],
                    cached=True
                )
            
            # 2. Fallback to database
            async with self.db_service.session_factory() as session:
                documentation = await session.get(Documentation, doc_id)
                
                if not documentation:
                    logger.debug(f"Documentation not found for {repo_id}")
                    return None
                
                # Prepare chunks from stored content
                chunks = self._prepare_text_chunks(
                    documentation.content, 
                    repo_id, 
                    doc_id
                )
                
                # 3. Cache result for future requests
                await self.cache_service.set(
                    cache_key,
                    {
                        "documentation": documentation,
                        "chunks": chunks,
                        "cached_at": datetime.utcnow().isoformat()
                    },
                    ttl=3600
                )
                
                logger.debug(f"Documentation loaded from database for {repo_id}")
                
                return DocumentationResult(
                    documentation=documentation,
                    chunks=chunks,
                    cached=False
                )
                
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving documentation for {repo_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving documentation for {repo_id}: {e}")
            return None
    
    async def list_documentation(self, limit: int = 100) -> List[Documentation]:
        """
        List all documentation entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of Documentation objects
        """
        try:
            async with self.db_service.session_factory() as session:
                result = await session.execute(
                    select(Documentation)
                    .order_by(Documentation.generated_at.desc())
                    .limit(limit)
                )
                return result.scalars().all()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error listing documentation: {e}")
            return []
        except Exception as e:
            logger.error(f"Error listing documentation: {e}")
            return []
    
    async def delete_documentation(self, repo_id: str, branch: str = "main") -> bool:
        """
        Delete documentation for a repository
        
        Args:
            repo_id: Repository identifier
            branch: Repository branch
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            doc_id = self._generate_doc_id(repo_id, branch)
            
            # Remove from database
            async with self.db_service.session_factory() as session:
                documentation = await session.get(Documentation, doc_id)
                if documentation:
                    await session.delete(documentation)
                    await session.commit()
                    
                    # Remove from cache
                    cache_key = f"{self._cache_prefix}{doc_id}"
                    await self.cache_service.delete(cache_key)
                    
                    logger.info(f"Documentation deleted for repository {repo_id}")
                    return True
                else:
                    logger.debug(f"Documentation not found for deletion: {repo_id}")
                    return False
                    
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting documentation for {repo_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting documentation for {repo_id}: {e}")
            return False
    
    async def migrate_from_memory_storage(self, memory_storage: Dict[str, Any]) -> int:
        """
        Migrate documentation from in-memory storage to database
        
        Args:
            memory_storage: Dictionary containing documentation data
            
        Returns:
            Number of documentation entries migrated
        """
        migrated_count = 0
        
        try:
            for doc_key, doc_data in memory_storage.items():
                try:
                    # Parse the key format: "repo_id:branch"
                    if ":" in doc_key:
                        repo_id, branch = doc_key.split(":", 1)
                    else:
                        repo_id = doc_key
                        branch = "main"
                    
                    # Extract documentation content
                    documentation_content = doc_data.get("documentation", "")
                    if not documentation_content:
                        logger.warning(f"Empty documentation for {doc_key}, skipping")
                        continue
                    
                    # Prepare documentation data
                    documentation_data = {
                        "documentation": documentation_content,
                        "repository_id": repo_id,
                        "branch": branch,
                        "generated_at": doc_data.get("generated_at"),
                        "status": doc_data.get("status", "success")
                    }
                    
                    # Save to database
                    await self.save_documentation(repo_id, documentation_data, branch)
                    migrated_count += 1
                    
                    logger.debug(f"Migrated documentation for {doc_key}")
                    
                except Exception as e:
                    logger.error(f"Error migrating documentation for {doc_key}: {e}")
                    continue
            
            logger.info(f"Migration completed: {migrated_count} documentation entries migrated")
            return migrated_count
            
        except Exception as e:
            logger.error(f"Error during documentation migration: {e}")
            return migrated_count
    
    def _generate_doc_id(self, repo_id: str, branch: str) -> str:
        """Generate unique documentation ID"""
        # Use a hash of repo_id and branch for consistent IDs
        content = f"{repo_id}:{branch}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _extract_content(self, documentation_data: Dict[str, Any]) -> str:
        """Extract text content from documentation data"""
        if isinstance(documentation_data, str):
            return documentation_data
        
        # Handle different data formats
        if "documentation" in documentation_data:
            return str(documentation_data["documentation"])
        elif "content" in documentation_data:
            return str(documentation_data["content"])
        else:
            # Convert entire dict to string as fallback
            return str(documentation_data)
    
    def _prepare_text_chunks(
        self, 
        content: str, 
        repo_id: str, 
        doc_id: str
    ) -> List[DocumentationChunk]:
        """
        Prepare text chunks for vector embedding
        
        Args:
            content: Documentation content
            repo_id: Repository identifier
            doc_id: Documentation identifier
            
        Returns:
            List of DocumentationChunk objects
        """
        chunks = []
        
        if not content or len(content.strip()) == 0:
            return chunks
        
        # Split content into chunks with overlap
        start = 0
        chunk_index = 0
        
        while start < len(content):
            # Calculate end position
            end = min(start + self._chunk_size, len(content))
            
            # Try to break at word boundary if not at end of content
            if end < len(content):
                # Look for last space within reasonable distance
                last_space = content.rfind(' ', start, end)
                if last_space > start + self._chunk_size * 0.8:  # At least 80% of chunk size
                    end = last_space
            
            # Extract chunk content
            chunk_content = content[start:end].strip()
            
            if chunk_content:  # Only add non-empty chunks
                chunk_id = f"{doc_id}_chunk_{chunk_index}"
                
                chunk = DocumentationChunk(
                    content=chunk_content,
                    metadata={
                        "repository_id": repo_id,
                        "documentation_id": doc_id,
                        "chunk_index": chunk_index,
                        "total_length": len(content),
                        "chunk_type": "documentation"
                    },
                    chunk_id=chunk_id,
                    start_index=start,
                    end_index=end
                )
                
                chunks.append(chunk)
                chunk_index += 1
            
            # Move start position with overlap
            start = max(end - self._chunk_overlap, start + 1)
            
            # Prevent infinite loop
            if start >= len(content):
                break
        
        return chunks
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for documentation service"""
        try:
            # Get cache service stats
            cache_stats = await self.cache_service.get_cache_stats()
            
            # Count documentation entries in cache
            doc_cache_count = 0
            if hasattr(self.cache_service, 'cache') and self.cache_service.cache:
                for key in self.cache_service.cache.keys():
                    if key.startswith(self._cache_prefix):
                        doc_cache_count += 1
            
            return {
                "cache_service_stats": cache_stats,
                "documentation_cache_entries": doc_cache_count,
                "cache_prefix": self._cache_prefix,
                "chunk_size": self._chunk_size,
                "chunk_overlap": self._chunk_overlap
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}


# Global documentation service instance
documentation_service = DocumentationService()