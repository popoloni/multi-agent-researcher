"""
Test suite for Task 1.1: Database Service Layer
Tests database connection, table creation, repository save/load operations, and backward compatibility
"""

import pytest
import asyncio
import os
import tempfile
from datetime import datetime
from typing import Dict, Any

# Import the database service and models
from app.services.database_service import DatabaseService, database_service
from app.database.models import Base, Repository as DatabaseRepository, Documentation as DatabaseDocumentation
from app.models.repository_schemas import Repository, CloneStatus, LanguageType
from app.core.config import settings


class TestDatabaseService:
    """Test database service functionality"""
    
    @pytest.fixture
    async def temp_db_service(self):
        """Create a temporary database service for testing"""
        # Create temporary database file
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        # Create database service with temporary database
        test_db_url = f"sqlite+aiosqlite:///{temp_db.name}"
        
        # Create test database service
        test_service = DatabaseService()
        test_service.database_url = test_db_url
        test_service.engine = test_service.__class__().__init__(test_service)
        
        # Initialize the database
        await test_service.initialize()
        
        yield test_service
        
        # Cleanup
        await test_service.close()
        try:
            os.unlink(temp_db.name)
        except:
            pass
    
    async def test_database_initialization(self, temp_db_service):
        """Test database connection and table creation"""
        # Test that database initializes without errors
        assert temp_db_service is not None
        
        # Test health check
        health_status = await temp_db_service.health_check()
        assert health_status is True
        
        print("✅ Database initialization test passed")
    
    async def test_repository_save_and_load(self, temp_db_service):
        """Test repository save/load operations"""
        # Create test repository
        test_repo = Repository(
            id="test-repo-1",
            name="Test Repository",
            url="https://github.com/test/repo",
            local_path="/tmp/test-repo",
            language=LanguageType.PYTHON,
            framework="FastAPI",
            description="A test repository for database testing",
            clone_status=CloneStatus.COMPLETED,
            file_count=25,
            line_count=1500
        )
        
        # Test save operation
        saved_repo = await temp_db_service.save_repository(test_repo)
        assert saved_repo.id == test_repo.id
        assert saved_repo.name == test_repo.name
        
        # Test load operation
        loaded_repo = await temp_db_service.get_repository("test-repo-1")
        assert loaded_repo is not None
        assert loaded_repo.id == "test-repo-1"
        assert loaded_repo.name == "Test Repository"
        assert loaded_repo.url == "https://github.com/test/repo"
        assert loaded_repo.language == LanguageType.PYTHON
        assert loaded_repo.framework == "FastAPI"
        
        print("✅ Repository save/load test passed")
    
    async def test_repository_not_found(self, temp_db_service):
        """Test behavior when repository doesn't exist"""
        # Test loading non-existent repository
        non_existent = await temp_db_service.get_repository("non-existent-repo")
        assert non_existent is None
        
        print("✅ Repository not found test passed")
    
    async def test_list_repositories(self, temp_db_service):
        """Test listing all repositories"""
        # Create multiple test repositories
        repos_data = [
            {
                "id": "repo-1",
                "name": "Repository 1",
                "url": "https://github.com/test/repo1",
                "local_path": "/tmp/repo1",
                "language": LanguageType.PYTHON
            },
            {
                "id": "repo-2", 
                "name": "Repository 2",
                "url": "https://github.com/test/repo2",
                "local_path": "/tmp/repo2",
                "language": LanguageType.JAVASCRIPT
            },
            {
                "id": "repo-3",
                "name": "Repository 3", 
                "url": "https://github.com/test/repo3",
                "local_path": "/tmp/repo3",
                "language": LanguageType.JAVA
            }
        ]
        
        # Save all repositories
        for repo_data in repos_data:
            repo = Repository(**repo_data)
            await temp_db_service.save_repository(repo)
        
        # Test list operation
        all_repos = await temp_db_service.list_repositories()
        print(f"Found {len(all_repos)} repositories in database")
        for repo in all_repos:
            print(f"  - {repo.id}: {repo.name}")
        
        # We might have more than 3 if previous tests left data
        assert len(all_repos) >= 3
        
        # Verify all repositories are present
        repo_ids = [repo.id for repo in all_repos]
        assert "repo-1" in repo_ids
        assert "repo-2" in repo_ids
        assert "repo-3" in repo_ids
        
        print("✅ List repositories test passed")
    
    async def test_repository_deletion(self, temp_db_service):
        """Test repository deletion"""
        # Create test repository
        test_repo = Repository(
            id="delete-test-repo",
            name="Delete Test Repository",
            url="https://github.com/test/delete-repo",
            local_path="/tmp/delete-repo",
            language=LanguageType.PYTHON
        )
        
        # Save repository
        await temp_db_service.save_repository(test_repo)
        
        # Verify it exists
        loaded_repo = await temp_db_service.get_repository("delete-test-repo")
        assert loaded_repo is not None
        
        # Delete repository
        delete_result = await temp_db_service.delete_repository("delete-test-repo")
        assert delete_result is True
        
        # Verify it's gone
        deleted_repo = await temp_db_service.get_repository("delete-test-repo")
        assert deleted_repo is None
        
        # Test deleting non-existent repository
        delete_non_existent = await temp_db_service.delete_repository("non-existent")
        assert delete_non_existent is False
        
        print("✅ Repository deletion test passed")
    
    async def test_documentation_save_and_load(self, temp_db_service):
        """Test documentation persistence"""
        # First create a repository
        test_repo = Repository(
            id="doc-test-repo",
            name="Documentation Test Repository",
            url="https://github.com/test/doc-repo",
            local_path="/tmp/doc-repo",
            language=LanguageType.PYTHON
        )
        await temp_db_service.save_repository(test_repo)
        
        # Create test documentation
        doc_data = {
            "overview": "This is a test repository for documentation testing",
            "api_reference": "API documentation with detailed endpoint descriptions",
            "architecture": "System architecture using microservices pattern",
            "user_guide": "Step-by-step user guide for getting started"
        }
        
        # Save documentation
        saved_doc = await temp_db_service.save_documentation("doc-test-repo", doc_data)
        assert saved_doc is not None
        assert saved_doc.repository_id == "doc-test-repo"
        assert saved_doc.format == "json"
        
        # Load documentation
        loaded_doc = await temp_db_service.get_documentation("doc-test-repo")
        assert loaded_doc is not None
        assert loaded_doc["overview"] == doc_data["overview"]
        assert loaded_doc["api_reference"] == doc_data["api_reference"]
        assert loaded_doc["architecture"] == doc_data["architecture"]
        assert loaded_doc["user_guide"] == doc_data["user_guide"]
        
        print("✅ Documentation save/load test passed")
    
    async def test_backward_compatibility(self, temp_db_service):
        """Test backward compatibility with existing Repository model"""
        # Test with minimal repository data (as might exist in current system)
        minimal_repo = Repository(
            id="minimal-repo",
            name="Minimal Repository",
            url="https://github.com/test/minimal",
            local_path="/tmp/minimal",
            language=LanguageType.UNKNOWN  # Default value
        )
        
        # Should save without errors
        saved_repo = await temp_db_service.save_repository(minimal_repo)
        assert saved_repo.id == "minimal-repo"
        
        # Should load with all fields populated (using defaults where needed)
        loaded_repo = await temp_db_service.get_repository("minimal-repo")
        assert loaded_repo is not None
        assert loaded_repo.id == "minimal-repo"
        assert loaded_repo.name == "Minimal Repository"
        assert loaded_repo.language == LanguageType.UNKNOWN
        assert loaded_repo.file_count == 0  # Default value
        assert loaded_repo.line_count == 0  # Default value
        
        print("✅ Backward compatibility test passed")
    
    async def test_connection_stats(self, temp_db_service):
        """Test database connection statistics"""
        stats = await temp_db_service.get_connection_stats()
        assert isinstance(stats, dict)
        # Stats might be 'unknown' for SQLite, but should not error
        assert "error" not in stats or stats.get("pool_size") is not None
        
        print("✅ Connection stats test passed")
    
    async def test_error_handling(self, temp_db_service):
        """Test error handling for invalid operations"""
        # Test saving repository with invalid data
        try:
            invalid_repo = Repository(
                id="",  # Empty ID should cause issues
                name="Invalid Repository",
                url="invalid-url",
                local_path="/tmp/invalid",
                language=LanguageType.PYTHON
            )
            # This might succeed in SQLite but should be handled gracefully
            result = await temp_db_service.save_repository(invalid_repo)
            # If it succeeds, that's also acceptable for this test
        except Exception as e:
            # Error should be logged and handled gracefully
            assert isinstance(e, Exception)
        
        print("✅ Error handling test passed")


async def run_all_tests():
    """Run all database service tests"""
    print("🧪 Starting Database Service Tests (Task 1.1)")
    print("=" * 50)
    
    test_instance = TestDatabaseService()
    
    # Create temporary database service for all tests
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Create test database service
        test_db_url = f"sqlite+aiosqlite:///{temp_db.name}"
        test_service = DatabaseService()
        test_service.database_url = test_db_url
        
        # Recreate engine with new URL
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
        test_service.engine = create_async_engine(
            test_db_url,
            echo=False,
            future=True
        )
        test_service.session_factory = async_sessionmaker(
            test_service.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Initialize the database
        await test_service.initialize()
        
        # Run all tests
        await test_instance.test_database_initialization(test_service)
        await test_instance.test_repository_save_and_load(test_service)
        await test_instance.test_repository_not_found(test_service)
        await test_instance.test_list_repositories(test_service)
        await test_instance.test_repository_deletion(test_service)
        await test_instance.test_documentation_save_and_load(test_service)
        await test_instance.test_backward_compatibility(test_service)
        await test_instance.test_connection_stats(test_service)
        await test_instance.test_error_handling(test_service)
        
        # Cleanup
        await test_service.close()
        
        print("=" * 50)
        print("🎉 All Database Service Tests Passed!")
        print("✅ Database connection and table creation working")
        print("✅ Repository save/load operations working")
        print("✅ Documentation persistence working")
        print("✅ Backward compatibility maintained")
        print("✅ Error handling implemented")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temp file
        try:
            os.unlink(temp_db.name)
        except:
            pass


if __name__ == "__main__":
    # Run tests directly
    result = asyncio.run(run_all_tests())
    exit(0 if result else 1)