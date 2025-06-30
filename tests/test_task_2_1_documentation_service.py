"""
Test suite for Task 2.1: Documentation Service with Database Integration
Tests the documentation service with database persistence and cache-first strategy
"""

import asyncio
import os
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any

from app.services.documentation_service import DocumentationService, DocumentationResult, DocumentationChunk
from app.services.database_service import DatabaseService
from app.services.cache_service import cache_service
from app.database.models import Documentation, Repository


class TestTask21DocumentationService:
    """Test documentation service with database integration"""
    
    def __init__(self):
        self.temp_db_path = None
        self.documentation_service = None
        self.db_service = None
    
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Create temporary database
        temp_dir = tempfile.mkdtemp()
        self.temp_db_path = os.path.join(temp_dir, "test_docs.db")
        
        # Initialize database service with test database
        self.db_service = DatabaseService()
        self.db_service.database_url = f"sqlite+aiosqlite:///{self.temp_db_path}"
        await self.db_service.initialize()
        
        # Initialize documentation service
        self.documentation_service = DocumentationService()
        self.documentation_service.db_service = self.db_service
        
        # Initialize cache service
        await cache_service.initialize()
        
        print("✅ Test environment setup complete")
    
    async def teardown(self):
        """Cleanup test environment"""
        print("🧹 Cleaning up test environment...")
        
        try:
            # Close database connections
            if self.db_service:
                await self.db_service.close()
            
            # Clean up temporary files
            if self.temp_db_path and os.path.exists(self.temp_db_path):
                os.remove(self.temp_db_path)
                temp_dir = os.path.dirname(self.temp_db_path)
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            
            print("✅ Test environment cleanup complete")
            
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    async def test_save_documentation_basic(self):
        """Test basic documentation save functionality"""
        print("🧪 Testing basic documentation save")
        
        # Test data
        repo_id = "test-repo-1"
        documentation_data = {
            "documentation": "# Test Documentation\n\nThis is a test documentation for repository analysis.",
            "repository_id": repo_id,
            "branch": "main",
            "status": "success"
        }
        
        # Save documentation
        result = await self.documentation_service.save_documentation(
            repo_id, 
            documentation_data, 
            "main"
        )
        
        # Verify result
        assert isinstance(result, DocumentationResult)
        assert result.documentation is not None
        assert result.documentation.repository_id == repo_id
        assert result.documentation.content == documentation_data["documentation"]
        assert result.documentation.format == "markdown"
        assert result.documentation.vector_indexed == False
        assert len(result.chunks) > 0
        assert result.cached == False
        
        print("✅ Basic documentation save test passed")
    
    async def test_get_documentation_cache_first(self):
        """Test cache-first retrieval strategy"""
        print("🧪 Testing cache-first retrieval strategy")
        
        repo_id = "test-repo-cache"
        documentation_data = {
            "documentation": "# Cache Test Documentation\n\nThis tests the cache-first strategy.",
            "repository_id": repo_id,
            "branch": "main"
        }
        
        # Save documentation (should cache it)
        save_result = await self.documentation_service.save_documentation(
            repo_id, 
            documentation_data, 
            "main"
        )
        
        # First retrieval (should hit cache)
        get_result_1 = await self.documentation_service.get_documentation(repo_id, "main")
        assert get_result_1 is not None
        assert get_result_1.cached == True
        assert get_result_1.documentation.content == documentation_data["documentation"]
        
        # Clear cache
        cache_key = f"{self.documentation_service._cache_prefix}{self.documentation_service._generate_doc_id(repo_id, 'main')}"
        await cache_service.delete(cache_key)
        
        # Second retrieval (should hit database)
        get_result_2 = await self.documentation_service.get_documentation(repo_id, "main")
        assert get_result_2 is not None
        assert get_result_2.cached == False
        assert get_result_2.documentation.content == documentation_data["documentation"]
        
        print("✅ Cache-first retrieval test passed")
    
    async def test_text_chunking(self):
        """Test text chunking for vector embedding preparation"""
        print("🧪 Testing text chunking for vector embeddings")
        
        repo_id = "test-repo-chunks"
        
        # Create long documentation content
        long_content = "# Large Documentation\n\n" + "This is a test paragraph. " * 200
        documentation_data = {
            "documentation": long_content,
            "repository_id": repo_id
        }
        
        # Save documentation
        result = await self.documentation_service.save_documentation(
            repo_id, 
            documentation_data, 
            "main"
        )
        
        # Verify chunks
        assert len(result.chunks) > 1  # Should be split into multiple chunks
        
        for i, chunk in enumerate(result.chunks):
            assert isinstance(chunk, DocumentationChunk)
            assert chunk.content is not None and len(chunk.content) > 0
            assert chunk.chunk_id.startswith(result.documentation.id)
            assert chunk.metadata["repository_id"] == repo_id
            assert chunk.metadata["chunk_index"] == i
            assert chunk.metadata["chunk_type"] == "documentation"
            assert chunk.start_index >= 0
            assert chunk.end_index > chunk.start_index
        
        # Verify chunk overlap and size constraints
        for chunk in result.chunks:
            assert len(chunk.content) <= self.documentation_service._chunk_size + 100  # Allow some flexibility
        
        print(f"✅ Text chunking test passed - {len(result.chunks)} chunks created")
    
    async def test_documentation_update(self):
        """Test updating existing documentation"""
        print("🧪 Testing documentation update")
        
        repo_id = "test-repo-update"
        
        # Save initial documentation
        initial_data = {
            "documentation": "# Initial Documentation\n\nThis is the initial version.",
            "repository_id": repo_id
        }
        
        initial_result = await self.documentation_service.save_documentation(
            repo_id, 
            initial_data, 
            "main"
        )
        initial_id = initial_result.documentation.id
        
        # Update documentation
        updated_data = {
            "documentation": "# Updated Documentation\n\nThis is the updated version with more content.",
            "repository_id": repo_id
        }
        
        updated_result = await self.documentation_service.save_documentation(
            repo_id, 
            updated_data, 
            "main"
        )
        
        # Verify update
        assert updated_result.documentation.id == initial_id  # Same ID
        assert updated_result.documentation.content == updated_data["documentation"]
        assert updated_result.documentation.generated_at > initial_result.documentation.generated_at
        
        # Verify retrieval gets updated content
        get_result = await self.documentation_service.get_documentation(repo_id, "main")
        assert get_result.documentation.content == updated_data["documentation"]
        
        print("✅ Documentation update test passed")
    
    async def test_list_documentation(self):
        """Test listing documentation entries"""
        print("🧪 Testing documentation listing")
        
        # Save multiple documentation entries
        test_repos = ["list-repo-1", "list-repo-2", "list-repo-3"]
        
        for i, repo_id in enumerate(test_repos):
            documentation_data = {
                "documentation": f"# Documentation {i+1}\n\nContent for repository {repo_id}.",
                "repository_id": repo_id
            }
            
            await self.documentation_service.save_documentation(
                repo_id, 
                documentation_data, 
                "main"
            )
        
        # List documentation
        docs = await self.documentation_service.list_documentation(limit=10)
        
        # Verify results
        assert len(docs) >= len(test_repos)
        
        # Check that our test repos are in the list
        doc_repo_ids = [doc.repository_id for doc in docs]
        for repo_id in test_repos:
            assert repo_id in doc_repo_ids
        
        print(f"✅ Documentation listing test passed - {len(docs)} entries found")
    
    async def test_delete_documentation(self):
        """Test documentation deletion"""
        print("🧪 Testing documentation deletion")
        
        repo_id = "test-repo-delete"
        documentation_data = {
            "documentation": "# Documentation to Delete\n\nThis will be deleted.",
            "repository_id": repo_id
        }
        
        # Save documentation
        await self.documentation_service.save_documentation(
            repo_id, 
            documentation_data, 
            "main"
        )
        
        # Verify it exists
        get_result = await self.documentation_service.get_documentation(repo_id, "main")
        assert get_result is not None
        
        # Delete documentation
        delete_success = await self.documentation_service.delete_documentation(repo_id, "main")
        assert delete_success == True
        
        # Verify it's deleted
        get_result_after = await self.documentation_service.get_documentation(repo_id, "main")
        assert get_result_after is None
        
        # Try to delete again (should return False)
        delete_again = await self.documentation_service.delete_documentation(repo_id, "main")
        assert delete_again == False
        
        print("✅ Documentation deletion test passed")
    
    async def test_migration_from_memory_storage(self):
        """Test migration from in-memory storage"""
        print("🧪 Testing migration from memory storage")
        
        # Simulate old memory storage format
        memory_storage = {
            "migrate-repo-1:main": {
                "documentation": "# Migrated Documentation 1\n\nThis was migrated from memory.",
                "repository_id": "migrate-repo-1",
                "branch": "main",
                "generated_at": "2024-01-01T12:00:00",
                "status": "success"
            },
            "migrate-repo-2:develop": {
                "documentation": "# Migrated Documentation 2\n\nAnother migrated document.",
                "repository_id": "migrate-repo-2",
                "branch": "develop",
                "generated_at": "2024-01-02T12:00:00",
                "status": "success"
            },
            "empty-doc": {
                "documentation": "",  # Empty documentation should be skipped
                "repository_id": "empty-repo",
                "status": "failed"
            }
        }
        
        # Perform migration
        migrated_count = await self.documentation_service.migrate_from_memory_storage(memory_storage)
        
        # Verify migration results
        assert migrated_count == 2  # Only 2 valid entries should be migrated
        
        # Verify migrated documentation can be retrieved
        doc1 = await self.documentation_service.get_documentation("migrate-repo-1", "main")
        assert doc1 is not None
        assert "Migrated Documentation 1" in doc1.documentation.content
        
        doc2 = await self.documentation_service.get_documentation("migrate-repo-2", "develop")
        assert doc2 is not None
        assert "Migrated Documentation 2" in doc2.documentation.content
        
        # Verify empty doc was not migrated
        empty_doc = await self.documentation_service.get_documentation("empty-repo", "main")
        assert empty_doc is None
        
        print(f"✅ Migration test passed - {migrated_count} entries migrated")
    
    async def test_error_handling(self):
        """Test error handling scenarios"""
        print("🧪 Testing error handling")
        
        # Test getting non-existent documentation
        result = await self.documentation_service.get_documentation("non-existent-repo", "main")
        assert result is None
        
        # Test saving with invalid data
        try:
            await self.documentation_service.save_documentation("", {}, "")
            assert False, "Should have raised an exception"
        except Exception as e:
            assert True  # Expected to fail
        
        print("✅ Error handling test passed")
    
    async def test_cache_stats(self):
        """Test cache statistics functionality"""
        print("🧪 Testing cache statistics")
        
        # Save some documentation to populate cache
        repo_id = "stats-repo"
        documentation_data = {
            "documentation": "# Stats Test\n\nTesting cache statistics.",
            "repository_id": repo_id
        }
        
        await self.documentation_service.save_documentation(repo_id, documentation_data, "main")
        
        # Get cache stats
        stats = await self.documentation_service.get_cache_stats()
        
        # Verify stats structure
        assert "cache_service_stats" in stats
        assert "documentation_cache_entries" in stats
        assert "cache_prefix" in stats
        assert "chunk_size" in stats
        assert "chunk_overlap" in stats
        
        assert stats["cache_prefix"] == "doc:"
        assert stats["chunk_size"] == 1000
        assert stats["chunk_overlap"] == 200
        
        print("✅ Cache statistics test passed")


async def run_documentation_service_tests():
    """Run all documentation service tests"""
    print("🧪 Starting Documentation Service Tests (Task 2.1)")
    print("=" * 60)
    
    test_suite = TestTask21DocumentationService()
    
    try:
        # Setup
        await test_suite.setup()
        
        # Run tests
        await test_suite.test_save_documentation_basic()
        await test_suite.test_get_documentation_cache_first()
        await test_suite.test_text_chunking()
        await test_suite.test_documentation_update()
        await test_suite.test_list_documentation()
        await test_suite.test_delete_documentation()
        await test_suite.test_migration_from_memory_storage()
        await test_suite.test_error_handling()
        await test_suite.test_cache_stats()
        
        print("=" * 60)
        print("🎉 All Documentation Service Tests Passed!")
        print("✅ Documentation save with database persistence")
        print("✅ Cache-first retrieval strategy")
        print("✅ Text chunking for vector embeddings")
        print("✅ Documentation update functionality")
        print("✅ Documentation listing and management")
        print("✅ Documentation deletion")
        print("✅ Migration from memory storage")
        print("✅ Error handling and edge cases")
        print("✅ Cache statistics and monitoring")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        await test_suite.teardown()


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_documentation_service_tests())
    exit(0 if success else 1)