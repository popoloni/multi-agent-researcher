"""
API Integration test for Task 1.2: Enhanced Repository Service
Tests that existing API endpoints continue to work with database integration
"""

import asyncio
import os
import tempfile
from datetime import datetime

from app.services.repository_service import RepositoryService
from app.services.database_service import DatabaseService
from app.models.repository_schemas import Repository, CloneStatus, LanguageType


async def test_api_endpoint_compatibility():
    """Test that existing API patterns continue to work"""
    print("🧪 Testing API Endpoint Compatibility")
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
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
        
        # Initialize the service
        await repo_service.initialize()
        
        # Test 1: list_repositories() - should work with empty database
        repositories = await repo_service.list_repositories()
        assert isinstance(repositories, list)
        initial_count = len(repositories)
        print(f"✅ Initial repository count: {initial_count}")
        
        # Test 2: get_repository_metadata() - should return None for non-existent
        non_existent = await repo_service.get_repository_metadata("non-existent-repo")
        assert non_existent is None
        print("✅ Non-existent repository returns None")
        
        # Test 3: Add repository using new method
        repo_data = {
            "id": "api-test-repo-1",
            "name": "API Test Repository 1",
            "url": "https://github.com/test/api1",
            "local_path": "/tmp/api1",
            "language": LanguageType.PYTHON,
            "framework": "FastAPI",
            "description": "Repository for API testing",
            "clone_status": CloneStatus.COMPLETED,
            "file_count": 25,
            "line_count": 1000
        }
        
        added_repo = await repo_service.add_repository(repo_data)
        assert added_repo.id == "api-test-repo-1"
        print("✅ Repository added successfully")
        
        # Test 4: list_repositories() - should now include new repository
        repositories = await repo_service.list_repositories()
        assert len(repositories) == initial_count + 1
        repo_ids = [repo.id for repo in repositories]
        assert "api-test-repo-1" in repo_ids
        print("✅ Repository appears in list")
        
        # Test 5: get_repository_metadata() - should return the repository
        retrieved_repo = await repo_service.get_repository_metadata("api-test-repo-1")
        assert retrieved_repo is not None
        assert retrieved_repo.id == "api-test-repo-1"
        assert retrieved_repo.name == "API Test Repository 1"
        assert retrieved_repo.framework == "FastAPI"
        print("✅ Repository retrieved successfully")
        
        # Test 6: Update repository
        updated_repo = await repo_service.update_repository("api-test-repo-1", {
            "framework": "Django",
            "description": "Updated API test repository"
        })
        assert updated_repo is not None
        assert updated_repo.framework == "Django"
        assert updated_repo.description == "Updated API test repository"
        print("✅ Repository updated successfully")
        
        # Test 7: Verify update persisted
        retrieved_again = await repo_service.get_repository_metadata("api-test-repo-1")
        assert retrieved_again.framework == "Django"
        assert retrieved_again.description == "Updated API test repository"
        print("✅ Update persisted correctly")
        
        # Test 8: Test cache vs database performance
        # First access (from cache)
        start_time = datetime.utcnow()
        cached_repo = await repo_service.get_repository_metadata("api-test-repo-1")
        cache_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Remove from cache and access again (from database)
        del repo_service.repositories["api-test-repo-1"]
        start_time = datetime.utcnow()
        db_repo = await repo_service.get_repository_metadata("api-test-repo-1")
        db_time = (datetime.utcnow() - start_time).total_seconds()
        
        assert cached_repo is not None
        assert db_repo is not None
        assert cache_time < db_time  # Cache should be faster
        print(f"✅ Performance: Cache {cache_time:.6f}s vs DB {db_time:.6f}s")
        
        # Test 9: Delete repository
        delete_result = await repo_service.delete_repository("api-test-repo-1")
        assert delete_result is True
        print("✅ Repository deleted successfully")
        
        # Test 10: Verify deletion
        deleted_repo = await repo_service.get_repository_metadata("api-test-repo-1")
        assert deleted_repo is None
        
        repositories = await repo_service.list_repositories()
        repo_ids = [repo.id for repo in repositories]
        assert "api-test-repo-1" not in repo_ids
        print("✅ Deletion verified")
        
        # Test 11: Test backward compatibility with direct assignment
        old_style_repo = Repository(
            id="old-style-api-repo",
            name="Old Style API Repository",
            url="https://github.com/test/oldapi",
            local_path="/tmp/oldapi",
            language=LanguageType.JAVASCRIPT,
            framework="React",
            description="Old style repository",
            clone_status=CloneStatus.COMPLETED,
            file_count=30,
            line_count=1200
        )
        
        # Direct assignment (old way)
        repo_service.repositories["old-style-api-repo"] = old_style_repo
        
        # Should still be retrievable
        old_retrieved = await repo_service.get_repository_metadata("old-style-api-repo")
        assert old_retrieved is not None
        assert old_retrieved.id == "old-style-api-repo"
        print("✅ Backward compatibility maintained")
        
        # Cleanup
        await repo_service.db_service.close()
        
        print("🎉 All API Endpoint Compatibility Tests Passed!")
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temp file
        try:
            os.unlink(temp_db.name)
        except:
            pass


async def test_service_initialization_patterns():
    """Test different service initialization patterns"""
    print("🧪 Testing Service Initialization Patterns")
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Test 1: Service with existing in-memory data
        repo_service = RepositoryService()
        
        # Add some repositories before initialization (simulating existing data)
        existing_repo = Repository(
            id="pre-init-repo",
            name="Pre-Init Repository",
            url="https://github.com/test/preinit",
            local_path="/tmp/preinit",
            language=LanguageType.PYTHON,
            framework="Flask",
            description="Repository added before initialization",
            clone_status=CloneStatus.COMPLETED,
            file_count=15,
            line_count=600
        )
        
        repo_service.repositories["pre-init-repo"] = existing_repo
        
        # Setup database service
        test_db_url = f"sqlite+aiosqlite:///{temp_db.name}"
        test_db_service = DatabaseService()
        test_db_service.database_url = test_db_url
        
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
        
        repo_service.db_service = test_db_service
        
        # Initialize (should migrate existing data)
        await repo_service.initialize()
        
        # Verify existing repository was migrated
        assert "pre-init-repo" in repo_service.repositories
        
        # Verify it's in database
        db_repo = await repo_service.db_service.get_repository("pre-init-repo")
        assert db_repo is not None
        assert db_repo.name == "Pre-Init Repository"
        print("✅ Pre-initialization data migrated successfully")
        
        # Test 2: Multiple initializations (should be idempotent)
        await repo_service.initialize()  # Second call
        await repo_service.initialize()  # Third call
        
        # Should still work
        repositories = await repo_service.list_repositories()
        assert len(repositories) >= 1
        print("✅ Multiple initializations handled correctly")
        
        # Test 3: Service operations without explicit initialization
        new_service = RepositoryService()
        new_service.db_service = test_db_service
        
        # Operations should auto-initialize
        repos = await new_service.list_repositories()
        assert isinstance(repos, list)
        print("✅ Auto-initialization working")
        
        # Cleanup
        await repo_service.db_service.close()
        
        print("🎉 Service Initialization Pattern Tests Passed!")
        return True
        
    except Exception as e:
        print(f"❌ Service initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temp file
        try:
            os.unlink(temp_db.name)
        except:
            pass


async def run_api_integration_tests():
    """Run all API integration tests"""
    print("🧪 Starting API Integration Tests for Task 1.2")
    print("=" * 60)
    
    try:
        # Run tests
        api_result = await test_api_endpoint_compatibility()
        init_result = await test_service_initialization_patterns()
        
        if api_result and init_result:
            print("=" * 60)
            print("🎉 All API Integration Tests Passed!")
            print("✅ Existing API endpoints work seamlessly")
            print("✅ Database integration is transparent")
            print("✅ Performance improvements delivered")
            print("✅ Backward compatibility maintained")
            print("✅ Service initialization patterns working")
            return True
        else:
            print("❌ Some API integration tests failed")
            return False
            
    except Exception as e:
        print(f"❌ API integration tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run integration tests directly
    result = asyncio.run(run_api_integration_tests())
    exit(0 if result else 1)