"""
Vector Database Service for RAG Integration
Task 3.1: Vector Database Integration

This service provides production-ready vector database capabilities for semantic search
and RAG integration, building on the existing VectorService foundation.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from app.services.database_service import database_service
from app.engines.vector_service import VectorDocument, SimilarityResult, EmbeddingModel
from app.services.cache_service import cache_service
from app.database.models import VectorIndex, VectorDocument as VectorDocumentModel

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Types of documents that can be indexed"""
    CODE_FILE = "code_file"
    DOCUMENTATION = "documentation"
    README = "readme"
    COMMENT = "comment"
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"


@dataclass
class IndexingResult:
    """Result of document indexing operation"""
    document_id: str
    success: bool
    embedding_dimension: int
    processing_time: float
    error_message: Optional[str] = None


@dataclass
class SearchResult:
    """Enhanced search result with metadata"""
    document: VectorDocument
    similarity_score: float
    document_type: DocumentType
    repository_id: str
    file_path: Optional[str] = None
    line_numbers: Optional[Tuple[int, int]] = None
    context: Optional[str] = None


class VectorDatabaseService:
    """
    Production-ready vector database service for semantic search and RAG integration.
    
    Features:
    - Hybrid search (keyword + semantic)
    - Document type classification
    - Repository-scoped search
    - Performance monitoring
    - Cache integration
    - Database persistence
    """
    
    def __init__(self):
        self.db_service = database_service
        # Use the global vector service instance to ensure shared memory store
        from app.engines.vector_service import vector_service
        self.vector_service = vector_service
        self.cache_service = cache_service
        
        # Performance tracking
        self.search_stats = {
            "total_searches": 0,
            "cache_hits": 0,
            "avg_search_time": 0.0,
            "last_search_time": None
        }
        
        # Cache configuration
        self._cache_prefix = "vector_search:"
        self._cache_ttl = 3600  # 1 hour
        
        logger.info("VectorDatabaseService initialized")
    
    async def index_document(
        self, 
        content: str, 
        metadata: Dict[str, Any],
        document_type: DocumentType = DocumentType.CODE_FILE,
        repository_id: Optional[str] = None
    ) -> IndexingResult:
        """
        Index a document for semantic search with database persistence.
        
        Args:
            content: Text content to index
            metadata: Document metadata (file_path, line_numbers, etc.)
            document_type: Type of document being indexed
            repository_id: Repository identifier for scoped search
            
        Returns:
            IndexingResult with indexing status and metrics
        """
        start_time = datetime.now()
        document_id = str(uuid.uuid4())
        
        try:
            logger.debug(f"Indexing document {document_id} of type {document_type.value}")
            
            # Generate embedding using existing VectorService
            embedding = await self.vector_service.generate_embedding(content)
            
            # Create vector document
            vector_doc = VectorDocument(
                id=document_id,
                content=content,
                metadata={
                    **metadata,
                    "document_type": document_type.value,
                    "repository_id": repository_id,
                    "indexed_at": datetime.now().isoformat()
                },
                embedding=embedding,
                created_at=datetime.now()
            )
            
            # Store in vector database (ChromaDB)
            await self._store_in_vector_db(vector_doc)
            
            # Store metadata in relational database for hybrid search
            await self._store_vector_metadata(vector_doc, repository_id)
            
            # Invalidate related caches
            await self._invalidate_search_cache(repository_id)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Successfully indexed document {document_id} in {processing_time:.3f}s")
            
            return IndexingResult(
                document_id=document_id,
                success=True,
                embedding_dimension=len(embedding),
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Failed to index document {document_id}: {e}")
            
            return IndexingResult(
                document_id=document_id,
                success=False,
                embedding_dimension=0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def search_documents(
        self,
        query: str,
        repository_id: Optional[str] = None,
        document_types: Optional[List[DocumentType]] = None,
        limit: int = 10,
        similarity_threshold: float = 0.3,
        use_hybrid_search: bool = True
    ) -> List[SearchResult]:
        """
        Search documents using semantic similarity with optional filters.
        
        Args:
            query: Search query
            repository_id: Limit search to specific repository
            document_types: Filter by document types
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            use_hybrid_search: Enable keyword + semantic search
            
        Returns:
            List of SearchResult objects ordered by relevance
        """
        start_time = datetime.now()
        
        try:
            # Check cache first
            cache_key = self._build_cache_key(query, repository_id, document_types, limit)
            cached_results = await self.cache_service.get(cache_key)
            
            if cached_results:
                self.search_stats["cache_hits"] += 1
                logger.debug(f"Cache hit for search query: {query[:50]}...")
                return self._deserialize_search_results(cached_results)
            
            # Perform semantic search
            semantic_results = await self._semantic_search(
                query, repository_id, document_types, limit, similarity_threshold
            )
            
            logger.info(f"Semantic search for '{query}' found {len(semantic_results)} results")
            
            # Enhance with hybrid search if enabled (only when using persistent storage)
            if use_hybrid_search and self.vector_service.collection:
                keyword_results = await self._keyword_search(
                    query, repository_id, document_types, limit
                )
                results = self._merge_search_results(semantic_results, keyword_results, limit)
            else:
                results = semantic_results
            
            # Cache results
            await self.cache_service.set(
                cache_key, 
                self._serialize_search_results(results),
                ttl=self._cache_ttl
            )
            
            # Update performance stats
            search_time = (datetime.now() - start_time).total_seconds()
            self._update_search_stats(search_time)
            
            logger.info(f"Search completed: {len(results)} results in {search_time:.3f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []
    
    async def get_document_by_id(self, document_id: str) -> Optional[VectorDocument]:
        """Retrieve a specific document by ID"""
        try:
            # Try vector database first
            if self.vector_service.collection:
                result = self.vector_service.collection.get(ids=[document_id])
                if result['ids']:
                    return self._build_vector_document_from_result(result, 0)
            
            # Fallback to in-memory store
            return self.vector_service.memory_store.get(document_id)
            
        except Exception as e:
            logger.error(f"Failed to retrieve document {document_id}: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the vector database"""
        try:
            # Delete from vector database
            if self.vector_service.collection:
                self.vector_service.collection.delete(ids=[document_id])
            
            # Delete from in-memory store
            self.vector_service.memory_store.pop(document_id, None)
            
            # Delete metadata from relational database
            from sqlalchemy import text
            async with self.db_service.session_factory() as session:
                result = await session.execute(
                    text("DELETE FROM vector_documents WHERE document_id = ?"),
                    (document_id,)
                )
                await session.commit()
            
            logger.info(f"Successfully deleted document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    async def get_repository_documents(
        self, 
        repository_id: str,
        document_types: Optional[List[DocumentType]] = None
    ) -> List[VectorDocument]:
        """Get all documents for a specific repository"""
        try:
            # Build filter conditions
            where_conditions = {"repository_id": repository_id}
            if document_types:
                where_conditions["document_type"] = {"$in": [dt.value for dt in document_types]}
            
            # Query vector database
            if self.vector_service.collection:
                results = self.vector_service.collection.get(where=where_conditions)
                return [
                    self._build_vector_document_from_result(results, i)
                    for i in range(len(results['ids']))
                ]
            
            # Fallback to in-memory search
            return [
                doc for doc in self.vector_service.memory_store.values()
                if doc.metadata.get("repository_id") == repository_id
                and (not document_types or 
                     DocumentType(doc.metadata.get("document_type", "code_file")) in document_types)
            ]
            
        except Exception as e:
            logger.error(f"Failed to get documents for repository {repository_id}: {e}")
            return []
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get vector database health status and performance metrics"""
        try:
            # Check vector database connectivity
            vector_db_status = "healthy" if self.vector_service.collection else "fallback"
            
            # Get collection stats
            collection_count = 0
            if self.vector_service.collection:
                try:
                    collection_count = self.vector_service.collection.count()
                except:
                    collection_count = len(self.vector_service.memory_store)
            else:
                collection_count = len(self.vector_service.memory_store)
            
            # Get cache stats
            cache_stats = await self.cache_service.get_stats() if hasattr(self.cache_service, 'get_stats') else {}
            
            return {
                "status": "healthy",
                "vector_database": {
                    "status": vector_db_status,
                    "backend": "chromadb" if self.vector_service.collection else "in_memory",
                    "document_count": collection_count,
                    "collection_name": self.vector_service.collection_name
                },
                "search_performance": self.search_stats,
                "cache_performance": cache_stats,
                "embedding_model": self.vector_service.embedding_model.value,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    # Private helper methods
    
    async def _store_in_vector_db(self, vector_doc: VectorDocument):
        """Store document in vector database (ChromaDB or in-memory)"""
        if self.vector_service.collection:
            # Store in ChromaDB
            self.vector_service.collection.add(
                ids=[vector_doc.id],
                documents=[vector_doc.content],
                metadatas=[vector_doc.metadata],
                embeddings=[vector_doc.embedding]
            )
        else:
            # Store in in-memory fallback
            self.vector_service.memory_store[vector_doc.id] = vector_doc
    
    async def _store_vector_metadata(self, vector_doc: VectorDocument, repository_id: Optional[str]):
        """Store vector document metadata in relational database for hybrid search"""
        try:
            async with self.db_service.session_factory() as session:
                # Create vector document record
                vector_doc_record = VectorDocumentModel(
                    document_id=vector_doc.id,
                    repository_id=repository_id,
                    document_type=vector_doc.metadata.get("document_type", "code_file"),
                    file_path=vector_doc.metadata.get("file_path"),
                    content_preview=vector_doc.content[:500],  # Store preview for keyword search
                    metadata_json=json.dumps(vector_doc.metadata),
                    embedding_dimension=len(vector_doc.embedding) if vector_doc.embedding else 0,
                    created_at=vector_doc.created_at
                )
                
                session.add(vector_doc_record)
                await session.commit()
                
        except Exception as e:
            logger.warning(f"Failed to store vector metadata: {e}")
    
    async def _semantic_search(
        self,
        query: str,
        repository_id: Optional[str],
        document_types: Optional[List[DocumentType]],
        limit: int,
        similarity_threshold: float
    ) -> List[SearchResult]:
        """Perform semantic similarity search"""
        try:
            # Generate query embedding
            query_embedding = await self.vector_service.generate_embedding(query)
            
            # Build filter conditions
            where_conditions = {}
            if repository_id:
                where_conditions["repository_id"] = repository_id
            if document_types:
                where_conditions["document_type"] = {"$in": [dt.value for dt in document_types]}
            
            # Search vector database
            if self.vector_service.collection:
                results = self.vector_service.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=where_conditions if where_conditions else None
                )
                
                return [
                    SearchResult(
                        document=self._build_vector_document_from_result(results, i),
                        similarity_score=1.0 - results['distances'][0][i],  # Convert distance to similarity
                        document_type=DocumentType(results['metadatas'][0][i].get("document_type", "code_file")),
                        repository_id=results['metadatas'][0][i].get("repository_id", ""),
                        file_path=results['metadatas'][0][i].get("file_path"),
                        context=results['documents'][0][i][:200] + "..." if len(results['documents'][0][i]) > 200 else results['documents'][0][i]
                    )
                    for i in range(len(results['ids'][0]))
                    if (1.0 - results['distances'][0][i]) >= similarity_threshold
                ]
            else:
                # Fallback to in-memory search
                return await self._in_memory_semantic_search(
                    query_embedding, repository_id, document_types, limit, similarity_threshold
                )
                
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def _keyword_search(
        self,
        query: str,
        repository_id: Optional[str],
        document_types: Optional[List[DocumentType]],
        limit: int
    ) -> List[SearchResult]:
        """Perform keyword-based search using database"""
        try:
            # Build SQL query for keyword search
            conditions = ["content_preview LIKE ?"]
            params = [f"%{query}%"]
            
            if repository_id:
                conditions.append("repository_id = ?")
                params.append(repository_id)
            
            if document_types:
                type_placeholders = ",".join("?" * len(document_types))
                conditions.append(f"document_type IN ({type_placeholders})")
                params.extend([dt.value for dt in document_types])
            
            from sqlalchemy import text
            
            sql = text(f"""
                SELECT document_id, repository_id, document_type, file_path, 
                       content_preview, metadata_json
                FROM vector_documents 
                WHERE {" AND ".join(conditions)}
                LIMIT ?
            """)
            params.append(limit)
            
            session = self.db_service.session_factory()
            try:
                result = await session.execute(sql, tuple(params))
                rows = result.fetchall()
                
                return [
                    SearchResult(
                        document=VectorDocument(
                            id=row[0],
                            content=row[4],  # content_preview
                            metadata=json.loads(row[5]) if row[5] else {},
                            created_at=datetime.now()
                        ),
                        similarity_score=0.8,  # Fixed score for keyword matches
                        document_type=DocumentType(row[2]),
                        repository_id=row[1],
                        file_path=row[3],
                        context=row[4]
                    )
                    for row in rows
                ]
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    async def _in_memory_semantic_search(
        self,
        query_embedding: List[float],
        repository_id: Optional[str],
        document_types: Optional[List[DocumentType]],
        limit: int,
        similarity_threshold: float
    ) -> List[SearchResult]:
        """Fallback in-memory semantic search"""
        try:
            results = []
            
            for doc in self.vector_service.memory_store.values():
                # Apply filters
                if repository_id and doc.metadata.get("repository_id") != repository_id:
                    continue
                
                if document_types:
                    doc_type = DocumentType(doc.metadata.get("document_type", "code_file"))
                    if doc_type not in document_types:
                        continue
                
                # Calculate similarity
                if doc.embedding:
                    similarity = self._calculate_cosine_similarity(query_embedding, doc.embedding)
                    if similarity >= similarity_threshold:
                        results.append(SearchResult(
                            document=doc,
                            similarity_score=similarity,
                            document_type=DocumentType(doc.metadata.get("document_type", "code_file")),
                            repository_id=doc.metadata.get("repository_id", ""),
                            file_path=doc.metadata.get("file_path"),
                            context=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                        ))
            
            # Sort by similarity and limit
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"In-memory semantic search failed: {e}")
            return []
    
    def _merge_search_results(
        self, 
        semantic_results: List[SearchResult], 
        keyword_results: List[SearchResult], 
        limit: int
    ) -> List[SearchResult]:
        """Merge and deduplicate semantic and keyword search results"""
        # Create a map to avoid duplicates
        results_map = {}
        
        # Add semantic results (higher priority)
        for result in semantic_results:
            results_map[result.document.id] = result
        
        # Add keyword results (if not already present)
        for result in keyword_results:
            if result.document.id not in results_map:
                results_map[result.document.id] = result
        
        # Sort by similarity score and limit
        merged_results = list(results_map.values())
        merged_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return merged_results[:limit]
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import numpy as np
            
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            
            return dot_product / (norm_v1 * norm_v2)
            
        except Exception:
            return 0.0
    
    def _build_vector_document_from_result(self, results: Dict, index: int) -> VectorDocument:
        """Build VectorDocument from ChromaDB query result"""
        return VectorDocument(
            id=results['ids'][0][index],
            content=results['documents'][0][index],
            metadata=results['metadatas'][0][index],
            embedding=results.get('embeddings', [None])[0][index] if results.get('embeddings') else None,
            created_at=datetime.now()
        )
    
    def _build_cache_key(
        self, 
        query: str, 
        repository_id: Optional[str], 
        document_types: Optional[List[DocumentType]], 
        limit: int
    ) -> str:
        """Build cache key for search results"""
        key_parts = [
            self._cache_prefix,
            query,
            repository_id or "all",
            ",".join([dt.value for dt in document_types]) if document_types else "all",
            str(limit)
        ]
        return ":".join(key_parts)
    
    async def _invalidate_search_cache(self, repository_id: Optional[str]):
        """Invalidate search cache for a repository"""
        # This is a simplified implementation
        # In production, you might want more sophisticated cache invalidation
        pass
    
    def _serialize_search_results(self, results: List[SearchResult]) -> str:
        """Serialize search results for caching"""
        try:
            serializable_results = []
            for result in results:
                serializable_results.append({
                    "document": asdict(result.document),
                    "similarity_score": result.similarity_score,
                    "document_type": result.document_type.value,
                    "repository_id": result.repository_id,
                    "file_path": result.file_path,
                    "context": result.context
                })
            return json.dumps(serializable_results)
        except Exception as e:
            logger.warning(f"Failed to serialize search results: {e}")
            return "[]"
    
    def _deserialize_search_results(self, serialized_results: str) -> List[SearchResult]:
        """Deserialize search results from cache"""
        try:
            data = json.loads(serialized_results)
            results = []
            
            for item in data:
                doc_data = item["document"]
                document = VectorDocument(
                    id=doc_data["id"],
                    content=doc_data["content"],
                    metadata=doc_data["metadata"],
                    embedding=doc_data.get("embedding"),
                    created_at=datetime.fromisoformat(doc_data["created_at"]) if doc_data.get("created_at") else datetime.now()
                )
                
                result = SearchResult(
                    document=document,
                    similarity_score=item["similarity_score"],
                    document_type=DocumentType(item["document_type"]),
                    repository_id=item["repository_id"],
                    file_path=item.get("file_path"),
                    context=item.get("context")
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.warning(f"Failed to deserialize search results: {e}")
            return []
    
    def _update_search_stats(self, search_time: float):
        """Update search performance statistics"""
        self.search_stats["total_searches"] += 1
        self.search_stats["last_search_time"] = search_time
        
        # Update rolling average
        total = self.search_stats["total_searches"]
        current_avg = self.search_stats["avg_search_time"]
        self.search_stats["avg_search_time"] = ((current_avg * (total - 1)) + search_time) / total


# Global instance
vector_database_service = VectorDatabaseService()