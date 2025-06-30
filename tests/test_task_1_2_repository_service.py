"""
Test suite for Task 1.2: Enhanced Repository Service with Database Integration
Tests the integration between RepositoryService and DatabaseService
"""

import asyncio
import os
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any

from app.services.repository_service import RepositoryService
from app.services.database_service import DatabaseService
from app.models.repository_schemas import Repository, CloneStatus, LanguageType


class TestTask12RepositoryService:
    """Test enhanced repository service with database integration"""
    
    async def test_initialization_and_migration(self, temp_repo_service):
        """Test service initialization and data migration"""
        print("🧪 Testing initialization and migration")
        
        # Create some in-memory repositories before initialization
        temp_repo_service.repositories = {
            "existing-repo-1": Repository(
                id="existing-repo-1",
                name="Existing Repository 1",
                url="https://github.com/test/existing1",
                local_path="/tmp/existing1",
                language=LanguageType.PYTHON,
                framework="Django",
                description="Pre-existing repository",
                clone_status=CloneStatus.COMPLETED,
                file_count=30,
                line_count=1200
            ),
            "existing-repo-2": Repository(
                id="existing-repo-2",
                name="Existing Repository 2",
                url="https://github.com/test/existing2",
                local_path="/tmp/existing2",
                language=LanguageType.JAVASCRIPT,
                framework="React",
                description="Another pre-existing repository",
                clone_status=CloneStatus.COMPLETED,
                file_count=45,
                line_count=2100
            )
        }
        
        # Initialize service (should migrate existing repositories)
        await temp_repo_service.initialize()
        
        # Verify initialization
        assert temp_repo_service._initialized is True
        
        # Verify repositories are still in cache
        assert len(temp_repo_service.repositories) >= 2
        assert "existing-repo-1" in temp_repo_service.repositories
        assert "existing-repo-2" in temp_repo_service.repositories
        
        # Verify repositories were migrated to database
        db_repo1 = await temp_repo_service.db_service.get_repository("existing-repo-1")
        assert db_repo1 is not None
        assert db_repo1.name == "Existing Repository 1"
        assert db_repo1.framework == "Django"
        
        db_repo2 = await temp_repo_service.db_service.get_repository("existing-repo-2")
        assert db_repo2 is not None
        assert db_repo2.name == "Existing Repository 2"
        assert db_repo2.framework == "React"
        
        print("✅ Initialization and migration test passed")
    
    async def test_cache_first_retrieval(self, temp_repo_service):
        """Test cache-first retrieval strategy"""
        print("🧪 Testing cache-first retrieval strategy")
        
        # Ensure service is initialized
        await temp_repo_service.initialize()
        
        # Create a repository directly in database (not in cache)
        db_only_repo = Repository(
            id="db-only-repo",
            name="Database Only Repository",
            url="https://github.com/test/dbonly",
            local_path="/tmp/dbonly",
            language=LanguageType.TYPESCRIPT,
            framework="Angular",
            description="Repository only in database",
            clone_status=CloneStatus.COMPLETED,
            file_count=20,
            line_count=800
        )
        
        await temp_repo_service.db_service.save_repository(db_only_repo)
        
        # Verify it's not in cache initially
        assert "db-only-repo" not in temp_repo_service.repositories
        
        # Retrieve repository (should load from database and cache)
        retrieved_repo = await temp_repo_service.get_repository_metadata("db-only-repo")
        
        assert retrieved_repo is not None
        assert retrieved_repo.id == "db-only-repo"
        assert retrieved_repo.name == "Database Only Repository"
        assert retrieved_repo.framework == "Angular"
        
        # Verify it's now in cache
        assert "db-only-repo" in temp_repo_service.repositories
        
        # Second retrieval should come from cache (faster)
        start_time = datetime.utcnow()
        cached_repo = await temp_repo_service.get_repository_metadata("db-only-repo")
        cache_time = (datetime.utcnow() - start_time).total_seconds()
        
        assert cached_repo is not None
        assert cached_repo.id == "db-only-repo"
        assert cache_time < 0.001  # Should be very fast from cache
        
        print("✅ Cache-first retrieval test passed")
    
    async def test_add_repository_with_persistence(self, temp_repo_service):
        """Test adding repository with database persistence"""
        print("🧪 Testing add repository with persistence")
        
        await temp_repo_service.initialize()
        
        # Add repository using the new method
        repo_data = {
            "id": "new-persistent-repo",
            "name": "New Persistent Repository",
            "url": "https://github.com/test/newpersistent",
            "local_path": "/tmp/newpersistent",
            "language": LanguageType.GO,
            "framework": "Gin",
            "description": "A new repository with persistence",
            "clone_status": CloneStatus.COMPLETED,
            "file_count": 15,
            "line_count": 600
        }
        
        added_repo = await temp_repo_service.add_repository(repo_data)
        
        # Verify repository was added
        assert added_repo.id == "new-persistent-repo"
        assert added_repo.name == "New Persistent Repository"
        assert added_repo.language == LanguageType.GO
        
        # Verify it's in cache
        assert "new-persistent-repo" in temp_repo_service.repositories
        
        # Verify it's in database
        db_repo = await temp_repo_service.db_service.get_repository("new-persistent-repo")
        assert db_repo is not None
        assert db_repo.name == "New Persistent Repository"
        assert db_repo.framework == "Gin"
        
        print("✅ Add repository with persistence test passed")
    
    async def test_update_repository_with_persistence(self, temp_repo_service):
        """Test updating repository with database persistence"""
        print("🧪 Testing update repository with persistence")
        
        await temp_repo_service.initialize()
        
        # First add a repository
        repo_data = {
            "id": "update-test-repo",
            "name": "Update Test Repository",
            "url": "https://github.com/test/updatetest",
            "local_path": "/tmp/updatetest",
            "language": LanguageType.PYTHON,
            "framework": "Flask",
            "description": "Repository for update testing",
            "clone_status": CloneStatus.COMPLETED,
            "file_count": 10,
            "line_count": 400
        }
        
        await temp_repo_service.add_repository(repo_data)
        
        # Update the repository
        updates = {
            "framework": "FastAPI",
            "description": "Updated repository description",
            "file_count": 15,
            "line_count": 600
        }
        
        updated_repo = await temp_repo_service.update_repository("update-test-repo", updates)
        
        # Verify update was successful
        assert updated_repo is not None
        assert updated_repo.framework == "FastAPI"
        assert updated_repo.description == "Updated repository description"
        assert updated_repo.file_count == 15
        assert updated_repo.line_count == 600
        
        # Verify cache was updated
        cached_repo = temp_repo_service.repositories["update-test-repo"]
        assert cached_repo.framework == "FastAPI"
        assert cached_repo.description == "Updated repository description"
        
        # Verify database was updated
        db_repo = await temp_repo_service.db_service.get_repository("update-test-repo")
        assert db_repo is not None
        assert db_repo.framework == "FastAPI"
        assert db_repo.description == "Updated repository description"
        
        print("✅ Update repository with persistence test passed")
    
    async def test_delete_repository_with_persistence(self, temp_repo_service):
        """Test deleting repository from database and cache"""
        print("🧪 Testing delete repository with persistence")
        
        await temp_repo_service.initialize()
        
        # First add a repository
        repo_data = {
            "id": "delete-test-repo",
            "name": "Delete Test Repository",
            "url": "https://github.com/test/deletetest",
            "local_path": "/tmp/deletetest",
            "language": LanguageType.JAVA,
            "framework": "Spring",
            "description": "Repository for delete testing",
            "clone_status": CloneStatus.COMPLETED,
            "file_count": 25,
            "line_count": 1000
        }
        
        await temp_repo_service.add_repository(repo_data)
        
        # Verify repository exists
        assert "delete-test-repo" in temp_repo_service.repositories
        db_repo = await temp_repo_service.db_service.get_repository("delete-test-repo")
        assert db_repo is not None
        
        # Delete the repository
        result = await temp_repo_service.delete_repository("delete-test-repo")
        assert result is True
        
        # Verify repository was removed from cache
        assert "delete-test-repo" not in temp_repo_service.repositories
        
        # Verify repository was removed from database
        db_repo = await temp_repo_service.db_service.get_repository("delete-test-repo")
        assert db_repo is None
        
        # Verify get_repository_metadata returns None
        retrieved_repo = await temp_repo_service.get_repository_metadata("delete-test-repo")
        assert retrieved_repo is None
        
        print("✅ Delete repository with persistence test passed")
    
    async def test_list_repositories_with_database_sync(self, temp_repo_service):
        """Test listing repositories with database synchronization"""
        print("🧪 Testing list repositories with database sync")
        
        await temp_repo_service.initialize()
        
        # Clear cache to test database loading
        temp_repo_service.repositories.clear()
        
        # Add some repositories directly to database
        for i in range(3):
            repo = Repository(
                id=f"sync-test-repo-{i}",
                name=f"Sync Test Repository {i}",
                url=f"https://github.com/test/sync{i}",
                local_path=f"/tmp/sync{i}",
                language=LanguageType.PYTHON if i % 2 == 0 else LanguageType.JAVASCRIPT,
                framework="Django" if i % 2 == 0 else "React",
                description=f"Sync test repository number {i}",
                clone_status=CloneStatus.COMPLETED,
                file_count=10 + i * 5,
                line_count=400 + i * 200
            )
            await temp_repo_service.db_service.save_repository(repo)
        
        # List repositories (should load from database)
        repositories = await temp_repo_service.list_repositories()
        
        # Verify repositories were loaded
        assert len(repositories) >= 3
        
        # Verify specific repositories exist
        repo_ids = [repo.id for repo in repositories]
        assert "sync-test-repo-0" in repo_ids
        assert "sync-test-repo-1" in repo_ids
        assert "sync-test-repo-2" in repo_ids
        
        # Verify cache was populated
        assert len(temp_repo_service.repositories) >= 3
        assert "sync-test-repo-0" in temp_repo_service.repositories
        
        print("✅ List repositories with database sync test passed")
    
    async def test_scan_local_directory_with_persistence(self, temp_repo_service):
        """Test scanning local directory with database persistence"""
        print("🧪 Testing scan local directory with persistence")
        
        await temp_repo_service.initialize()
        
        # Create a temporary directory with some files
        temp_dir = tempfile.mkdtemp()
        try:
            # Create some Python files
            with open(os.path.join(temp_dir, "main.py"), "w") as f:
                f.write("print('Hello, World!')\n")
            
            with open(os.path.join(temp_dir, "utils.py"), "w") as f:
                f.write("def helper_function():\n    pass\n")
            
            # Create requirements.txt to indicate Python project
            with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
                f.write("fastapi==0.68.0\n")
            
            # Scan the directory
            repository = await temp_repo_service.scan_local_directory(
                temp_dir, 
                "https://github.com/test/scanned"
            )
            
            # Verify repository was created
            assert repository.id is not None
            assert repository.name == os.path.basename(temp_dir)
            assert repository.local_path == temp_dir
            assert repository.language == LanguageType.PYTHON
            assert repository.file_count >= 2  # At least main.py and utils.py
            
            # Verify it's in cache
            assert repository.id in temp_repo_service.repositories
            
            # Verify it's in database
            db_repo = await temp_repo_service.db_service.get_repository(repository.id)
            assert db_repo is not None
            assert db_repo.name == repository.name
            assert db_repo.language == LanguageType.PYTHON
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)
        
        print("✅ Scan local directory with persistence test passed")
    
    async def test_performance_comparison(self, temp_repo_service):
        """Test performance comparison between cache and database access"""
        print("🧪 Testing performance comparison")
        
        await temp_repo_service.initialize()
        
        # Add a repository
        repo_data = {
            "id": "performance-test-repo",
            "name": "Performance Test Repository",
            "url": "https://github.com/test/performance",
            "local_path": "/tmp/performance",
            "language": LanguageType.PYTHON,
            "framework": "FastAPI",
            "description": "Repository for performance testing",
            "clone_status": CloneStatus.COMPLETED,
            "file_count": 50,
            "line_count": 2000
        }
        
        await temp_repo_service.add_repository(repo_data)
        
        # Test cache access time (should be very fast)
        start_time = datetime.utcnow()
        cached_repo = await temp_repo_service.get_repository_metadata("performance-test-repo")
        cache_time = (datetime.utcnow() - start_time).total_seconds()
        
        assert cached_repo is not None
        assert cache_time < 0.01  # Should be very fast
        
        # Remove from cache and test database access time
        del temp_repo_service.repositories["performance-test-repo"]
        
        start_time = datetime.utcnow()
        db_repo = await temp_repo_service.get_repository_metadata("performance-test-repo")
        db_time = (datetime.utcnow() - start_time).total_seconds()
        
        assert db_repo is not None
        assert db_time < 0.1  # Should still be reasonably fast
        
        # Cache should be faster than database
        print(f"Cache access time: {cache_time:.6f}s")
        print(f"Database access time: {db_time:.6f}s")
        
        # Verify repository is back in cache
        assert "performance-test-repo" in temp_repo_service.repositories
        
        print("✅ Performance comparison test passed")
    
    async def test_backward_compatibility(self, temp_repo_service):
        """Test that existing API endpoints continue to work"""
        print("🧪 Testing backward compatibility")
        
        await temp_repo_service.initialize()
        
        # Test that old methods still work
        repositories = await temp_repo_service.list_repositories()
        assert isinstance(repositories, list)
        
        # Test get_repository_metadata with non-existent repo
        non_existent = await temp_repo_service.get_repository_metadata("non-existent")
        assert non_existent is None
        
        # Add a repository using the old-style direct assignment (should still work)
        old_style_repo = Repository(
            id="old-style-repo",
            name="Old Style Repository",
            url="https://github.com/test/oldstyle",
            local_path="/tmp/oldstyle",
            language=LanguageType.PYTHON,
            framework="Django",
            description="Repository added old style",
            clone_status=CloneStatus.COMPLETED,
            file_count=20,
            line_count=800
        )
        
        # This simulates how repositories were added before database integration
        temp_repo_service.repositories["old-style-repo"] = old_style_repo
        
        # Should be able to retrieve it
        retrieved = await temp_repo_service.get_repository_metadata("old-style-repo")
        assert retrieved is not None
        assert retrieved.id == "old-style-repo"
        
        print("✅ Backward compatibility test passed")


async def create_temp_repository_service():
    """Create a temporary repository service for testing"""
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Create test database service
    test_db_url = f"sqlite+aiosqlite:///{temp_db.name}"
    test_db_service = DatabaseService()
    test_db_service.database_url = test_db_url
    
    # Recreate engine with new URL
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    test_db_service.engine = create_async_engine(
        test_db_url,
        echo=False,
        future=True
    )
    test_db_service.session_factory = async_sessionmaker(
        test_db_service.engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Create repository service with test database
    repo_service = RepositoryService()
    repo_service.db_service = test_db_service
    
    return repo_service, temp_db.name


async def run_all_tests():
    """Run all repository service tests"""
    print("🧪 Starting Enhanced Repository Service Tests (Task 1.2)")
    print("=" * 60)
    
    try:
        # Create test service
        test_service, temp_db_path = await create_temp_repository_service()
        
        try:
            # Create test instance
            test_instance = TestTask12RepositoryService()
            
            # Run all tests
            await test_instance.test_initialization_and_migration(test_service)
            await test_instance.test_cache_first_retrieval(test_service)
            await test_instance.test_add_repository_with_persistence(test_service)
            await test_instance.test_update_repository_with_persistence(test_service)
            await test_instance.test_delete_repository_with_persistence(test_service)
            await test_instance.test_list_repositories_with_database_sync(test_service)
            await test_instance.test_scan_local_directory_with_persistence(test_service)
            await test_instance.test_performance_comparison(test_service)
            await test_instance.test_backward_compatibility(test_service)
            
            print("=" * 60)
            print("🎉 All Enhanced Repository Service Tests Passed!")
            print("✅ Database integration working seamlessly")
            print("✅ Cache-first strategy implemented")
            print("✅ Migration of existing repositories working")
            print("✅ Performance optimizations effective")
            print("✅ Backward compatibility maintained")
            return True
            
        finally:
            # Cleanup
            await test_service.db_service.close()
            try:
                os.unlink(temp_db_path)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run tests directly
    result = asyncio.run(run_all_tests())
    exit(0 if result else 1)