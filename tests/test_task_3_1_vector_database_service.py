"""
Test Suite for Task 3.1: Vector Database Service
Tests vector database integration, semantic search, and RAG foundation capabilities.
"""

import pytest
import pytest_asyncio
import asyncio
import tempfile
import shutil
from datetime import datetime
from typing import List

from app.services.vector_database_service import (
    VectorDatabaseService, 
    DocumentType, 
    IndexingResult, 
    SearchResult
)
from app.engines.vector_service import VectorDocument
from app.services.database_service import DatabaseService
from app.database.models import Base


class TestVectorDatabaseService:
    """Test suite for VectorDatabaseService"""
    
    @pytest_asyncio.fixture
    async def vector_db_service(self):
        """Create a test vector database service"""
        # Use temporary directory for testing
        service = VectorDatabaseService()
        
        # Initialize database tables
        await service.db_service.initialize_database()
        
        yield service
        
        # Cleanup
        await service.db_service.close()
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing"""
        return [
            {
                "content": "def calculate_fibonacci(n): return n if n <= 1 else calculate_fibonacci(n-1) + calculate_fibonacci(n-2)",
                "metadata": {
                    "file_path": "/src/math_utils.py",
                    "line_numbers": (1, 3),
                    "function_name": "calculate_fibonacci"
                },
                "document_type": DocumentType.FUNCTION,
                "repository_id": "test-repo-1"
            },
            {
                "content": "class DatabaseManager: def __init__(self): self.connection = None",
                "metadata": {
                    "file_path": "/src/database.py",
                    "line_numbers": (10, 15),
                    "class_name": "DatabaseManager"
                },
                "document_type": DocumentType.CLASS,
                "repository_id": "test-repo-1"
            },
            {
                "content": "# Vector Database Service\nThis service provides semantic search capabilities for code and documentation.",
                "metadata": {
                    "file_path": "/docs/vector_service.md",
                    "section": "Overview"
                },
                "document_type": DocumentType.DOCUMENTATION,
                "repository_id": "test-repo-1"
            },
            {
                "content": "async def process_user_request(request): validate_input(request); return await handle_request(request)",
                "metadata": {
                    "file_path": "/src/api.py",
                    "line_numbers": (25, 30),
                    "function_name": "process_user_request"
                },
                "document_type": DocumentType.FUNCTION,
                "repository_id": "test-repo-2"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, vector_db_service):
        """Test that the vector database service initializes correctly"""
        assert vector_db_service is not None
        assert vector_db_service.db_service is not None
        assert vector_db_service.vector_service is not None
        assert vector_db_service.cache_service is not None
        
        # Check initial stats
        assert vector_db_service.search_stats["total_searches"] == 0
        assert vector_db_service.search_stats["cache_hits"] == 0
    
    @pytest.mark.asyncio
    async def test_document_indexing_success(self, vector_db_service, sample_documents):
        """Test successful document indexing"""
        doc = sample_documents[0]
        
        result = await vector_db_service.index_document(
            content=doc["content"],
            metadata=doc["metadata"],
            document_type=doc["document_type"],
            repository_id=doc["repository_id"]
        )
        
        assert isinstance(result, IndexingResult)
        assert result.success is True
        assert result.document_id is not None
        assert result.embedding_dimension > 0
        assert result.processing_time > 0
        assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_document_indexing_multiple(self, vector_db_service, sample_documents):
        """Test indexing multiple documents"""
        results = []
        
        for doc in sample_documents:
            result = await vector_db_service.index_document(
                content=doc["content"],
                metadata=doc["metadata"],
                document_type=doc["document_type"],
                repository_id=doc["repository_id"]
            )
            results.append(result)
        
        # All should succeed
        assert all(r.success for r in results)
        assert len(set(r.document_id for r in results)) == len(results)  # All unique IDs
    
    @pytest.mark.asyncio
    async def test_semantic_search_basic(self, vector_db_service, sample_documents):
        """Test basic semantic search functionality"""
        # Index documents first
        for doc in sample_documents:
            await vector_db_service.index_document(
                content=doc["content"],
                metadata=doc["metadata"],
                document_type=doc["document_type"],
                repository_id=doc["repository_id"]
            )
        
        # Search for fibonacci-related content
        results = await vector_db_service.search_documents(
            query="fibonacci calculation recursive function",
            limit=5
        )
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Check result structure
        for result in results:
            assert isinstance(result, SearchResult)
            assert isinstance(result.document, VectorDocument)
            assert 0 <= result.similarity_score <= 1
            assert isinstance(result.document_type, DocumentType)
    
    @pytest.mark.asyncio
    async def test_repository_scoped_search(self, vector_db_service, sample_documents):
        """Test search scoped to specific repository"""
        # Index documents first
        for doc in sample_documents:
            await vector_db_service.index_document(
                content=doc["content"],
                metadata=doc["metadata"],
                document_type=doc["document_type"],
                repository_id=doc["repository_id"]
            )
        
        # Search only in test-repo-1
        results = await vector_db_service.search_documents(
            query="database function class",
            repository_id="test-repo-1",
            limit=10
        )
        
        # All results should be from test-repo-1
        for result in results:
            assert result.repository_id == "test-repo-1"
    
    @pytest.mark.asyncio
    async def test_document_type_filtering(self, vector_db_service, sample_documents):
        """Test filtering by document type"""
        # Index documents first
        for doc in sample_documents:
            await vector_db_service.index_document(
                content=doc["content"],
                metadata=doc["metadata"],
                document_type=doc["document_type"],
                repository_id=doc["repository_id"]
            )
        
        # Search only for functions
        results = await vector_db_service.search_documents(
            query="function calculation",
            document_types=[DocumentType.FUNCTION],
            limit=10
        )
        
        # All results should be functions
        for result in results:
            assert result.document_type == DocumentType.FUNCTION
    
    @pytest.mark.asyncio
    async def test_hybrid_search(self, vector_db_service, sample_documents):
        """Test hybrid search (semantic + keyword)"""
        # Index documents first
        for doc in sample_documents:
            await vector_db_service.index_document(
                content=doc["content"],
                metadata=doc["metadata"],
                document_type=doc["document_type"],
                repository_id=doc["repository_id"]
            )
        
        # Test with hybrid search enabled
        results_hybrid = await vector_db_service.search_documents(
            query="DatabaseManager",
            use_hybrid_search=True,
            limit=5
        )
        
        # Test with only semantic search
        results_semantic = await vector_db_service.search_documents(
            query="DatabaseManager",
            use_hybrid_search=False,
            limit=5
        )
        
        assert isinstance(results_hybrid, list)
        assert isinstance(results_semantic, list)
        
        # Hybrid search might return more or different results
        # At minimum, both should work without errors
    
    @pytest.mark.asyncio
    async def test_document_retrieval_by_id(self, vector_db_service, sample_documents):
        """Test retrieving specific document by ID"""
        doc = sample_documents[0]
        
        # Index document first
        result = await vector_db_service.index_document(
            content=doc["content"],
            metadata=doc["metadata"],
            document_type=doc["document_type"],
            repository_id=doc["repository_id"]
        )
        
        # Retrieve by ID
        retrieved_doc = await vector_db_service.get_document_by_id(result.document_id)
        
        assert retrieved_doc is not None
        assert retrieved_doc.id == result.document_id
        assert retrieved_doc.content == doc["content"]
    
    @pytest.mark.asyncio
    async def test_repository_documents_retrieval(self, vector_db_service, sample_documents):
        """Test retrieving all documents for a repository"""
        # Index documents first
        for doc in sample_documents:
            await vector_db_service.index_document(
                content=doc["content"],
                metadata=doc["metadata"],
                document_type=doc["document_type"],
                repository_id=doc["repository_id"]
            )
        
        # Get all documents for test-repo-1
        repo_docs = await vector_db_service.get_repository_documents("test-repo-1")
        
        # Should have 3 documents for test-repo-1
        assert len(repo_docs) == 3
        
        # All should be from the correct repository
        for doc in repo_docs:
            assert doc.metadata.get("repository_id") == "test-repo-1" or \
                   any("test-repo-1" in str(v) for v in doc.metadata.values())
    
    @pytest.mark.asyncio
    async def test_document_deletion(self, vector_db_service, sample_documents):
        """Test document deletion"""
        doc = sample_documents[0]
        
        # Index document first
        result = await vector_db_service.index_document(
            content=doc["content"],
            metadata=doc["metadata"],
            document_type=doc["document_type"],
            repository_id=doc["repository_id"]
        )
        
        # Verify it exists
        retrieved_doc = await vector_db_service.get_document_by_id(result.document_id)
        assert retrieved_doc is not None
        
        # Delete it
        deletion_success = await vector_db_service.delete_document(result.document_id)
        assert deletion_success is True
        
        # Verify it's gone
        retrieved_doc_after = await vector_db_service.get_document_by_id(result.document_id)
        assert retrieved_doc_after is None
    
    @pytest.mark.asyncio
    async def test_search_performance_tracking(self, vector_db_service, sample_documents):
        """Test that search performance is tracked"""
        # Index documents first
        for doc in sample_documents:
            await vector_db_service.index_document(
                content=doc["content"],
                metadata=doc["metadata"],
                document_type=doc["document_type"],
                repository_id=doc["repository_id"]
            )
        
        initial_searches = vector_db_service.search_stats["total_searches"]
        
        # Perform a search
        await vector_db_service.search_documents(
            query="test search",
            limit=5
        )
        
        # Check stats updated
        assert vector_db_service.search_stats["total_searches"] == initial_searches + 1
        assert vector_db_service.search_stats["last_search_time"] > 0
        assert vector_db_service.search_stats["avg_search_time"] > 0
    
    @pytest.mark.asyncio
    async def test_health_status(self, vector_db_service):
        """Test health status reporting"""
        health = await vector_db_service.get_health_status()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "vector_database" in health
        assert "search_performance" in health
        assert "embedding_model" in health
        assert "last_updated" in health
        
        # Vector database section
        vdb_status = health["vector_database"]
        assert "status" in vdb_status
        assert "backend" in vdb_status
        assert "document_count" in vdb_status
        assert "collection_name" in vdb_status
    
    @pytest.mark.asyncio
    async def test_search_with_similarity_threshold(self, vector_db_service, sample_documents):
        """Test search with similarity threshold filtering"""
        # Index documents first
        for doc in sample_documents:
            await vector_db_service.index_document(
                content=doc["content"],
                metadata=doc["metadata"],
                document_type=doc["document_type"],
                repository_id=doc["repository_id"]
            )
        
        # Search with high threshold (should return fewer results)
        results_high_threshold = await vector_db_service.search_documents(
            query="fibonacci calculation",
            similarity_threshold=0.9,
            limit=10
        )
        
        # Search with low threshold (should return more results)
        results_low_threshold = await vector_db_service.search_documents(
            query="fibonacci calculation",
            similarity_threshold=0.1,
            limit=10
        )
        
        # All results should meet the threshold
        for result in results_high_threshold:
            assert result.similarity_score >= 0.9
        
        for result in results_low_threshold:
            assert result.similarity_score >= 0.1
        
        # Low threshold should return at least as many results as high threshold
        assert len(results_low_threshold) >= len(results_high_threshold)
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self, vector_db_service):
        """Test search with no matching documents"""
        # Search without indexing any documents
        results = await vector_db_service.search_documents(
            query="nonexistent content that should not match anything",
            limit=10
        )
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_document(self, vector_db_service):
        """Test error handling for invalid document indexing"""
        # Try to index empty content
        result = await vector_db_service.index_document(
            content="",
            metadata={},
            document_type=DocumentType.CODE_FILE,
            repository_id="test-repo"
        )
        
        # Should handle gracefully (might succeed with empty content or fail gracefully)
        assert isinstance(result, IndexingResult)
        assert result.document_id is not None
    
    @pytest.mark.asyncio
    async def test_large_content_indexing(self, vector_db_service):
        """Test indexing large content"""
        large_content = "def large_function():\n" + "    # comment line\n" * 1000 + "    return True"
        
        result = await vector_db_service.index_document(
            content=large_content,
            metadata={"file_path": "/src/large_file.py"},
            document_type=DocumentType.FUNCTION,
            repository_id="test-repo"
        )
        
        assert result.success is True
        assert result.embedding_dimension > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_indexing(self, vector_db_service, sample_documents):
        """Test concurrent document indexing"""
        # Create indexing tasks
        tasks = []
        for i, doc in enumerate(sample_documents):
            task = vector_db_service.index_document(
                content=f"{doc['content']} - version {i}",
                metadata={**doc["metadata"], "version": i},
                document_type=doc["document_type"],
                repository_id=f"{doc['repository_id']}-{i}"
            )
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.success for r in results)
        assert len(set(r.document_id for r in results)) == len(results)  # All unique IDs


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])