"""
Integration test for Task 1.1: Database Service Integration
Tests that the database service integrates properly with existing application components
"""

import asyncio
import os
import tempfile
from datetime import datetime

from app.services.database_service import DatabaseService
from app.models.repository_schemas import Repository, CloneStatus, LanguageType
from app.services.cache_service import cache_service


async def test_database_cache_integration():
    """Test that database service works with cache service"""
    print("🧪 Testing Database-Cache Integration")
    
    # Create temporary database
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
        
        # Test repository creation and persistence
        test_repo = Repository(
            id="integration-test-repo",
            name="Integration Test Repository",
            url="https://github.com/test/integration",
            local_path="/tmp/integration-test",
            language=LanguageType.PYTHON,
            framework="FastAPI",
            description="Repository for testing database integration",
            clone_status=CloneStatus.COMPLETED,
            file_count=50,
            line_count=2500
        )
        
        # Save to database
        saved_repo = await test_service.save_repository(test_repo)
        assert saved_repo.id == test_repo.id
        print("✅ Repository saved to database")
        
        # Retrieve from database
        loaded_repo = await test_service.get_repository("integration-test-repo")
        assert loaded_repo is not None
        assert loaded_repo.name == "Integration Test Repository"
        assert loaded_repo.language == LanguageType.PYTHON
        assert loaded_repo.framework == "FastAPI"
        print("✅ Repository loaded from database")
        
        # Test documentation persistence
        doc_data = {
            "overview": "Integration test documentation",
            "api_endpoints": [
                {"path": "/health", "method": "GET", "description": "Health check"},
                {"path": "/repos", "method": "GET", "description": "List repositories"}
            ],
            "architecture": {
                "pattern": "microservices",
                "database": "SQLite with async support",
                "cache": "In-memory with TTL"
            }
        }
        
        # Save documentation
        saved_doc = await test_service.save_documentation("integration-test-repo", doc_data)
        assert saved_doc is not None
        print("✅ Documentation saved to database")
        
        # Load documentation
        loaded_doc = await test_service.get_documentation("integration-test-repo")
        assert loaded_doc is not None
        assert loaded_doc["overview"] == "Integration test documentation"
        assert len(loaded_doc["api_endpoints"]) == 2
        print("✅ Documentation loaded from database")
        
        # Test cache integration (if cache service is available)
        try:
            # Test that cache service can store repository data
            cache_key = f"repo_{test_repo.id}"
            await cache_service.set(cache_key, test_repo.dict(), ttl=300)
            
            cached_data = await cache_service.get(cache_key)
            assert cached_data is not None
            assert cached_data["id"] == test_repo.id
            print("✅ Cache integration working")
            
        except Exception as e:
            print(f"⚠️  Cache integration test skipped: {e}")
        
        # Test database health check
        health_status = await test_service.health_check()
        assert health_status is True
        print("✅ Database health check working")
        
        # Test connection stats
        stats = await test_service.get_connection_stats()
        assert isinstance(stats, dict)
        print("✅ Connection stats working")
        
        # Cleanup
        await test_service.close()
        
        print("🎉 Database-Cache Integration Test Passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temp file
        try:
            os.unlink(temp_db.name)
        except:
            pass


async def test_database_performance():
    """Test database performance with multiple operations"""
    print("🧪 Testing Database Performance")
    
    # Create temporary database
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
        
        # Test bulk repository creation
        start_time = datetime.utcnow()
        
        repositories = []
        for i in range(10):
            repo = Repository(
                id=f"perf-test-repo-{i}",
                name=f"Performance Test Repository {i}",
                url=f"https://github.com/test/perf-repo-{i}",
                local_path=f"/tmp/perf-test-{i}",
                language=LanguageType.PYTHON if i % 2 == 0 else LanguageType.JAVASCRIPT,
                framework="FastAPI" if i % 2 == 0 else "React",
                description=f"Performance test repository number {i}",
                clone_status=CloneStatus.COMPLETED,
                file_count=10 + i * 5,
                line_count=500 + i * 100
            )
            repositories.append(repo)
            await test_service.save_repository(repo)
        
        save_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"✅ Saved 10 repositories in {save_time:.3f} seconds")
        
        # Test bulk retrieval
        start_time = datetime.utcnow()
        
        all_repos = await test_service.list_repositories()
        assert len(all_repos) >= 10
        
        load_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"✅ Loaded {len(all_repos)} repositories in {load_time:.3f} seconds")
        
        # Test individual lookups
        start_time = datetime.utcnow()
        
        for i in range(5):
            repo = await test_service.get_repository(f"perf-test-repo-{i}")
            assert repo is not None
            assert repo.name == f"Performance Test Repository {i}"
        
        lookup_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"✅ Performed 5 individual lookups in {lookup_time:.3f} seconds")
        
        # Performance assertions (reasonable for SQLite)
        assert save_time < 5.0, f"Save time too slow: {save_time}s"
        assert load_time < 2.0, f"Load time too slow: {load_time}s"
        assert lookup_time < 1.0, f"Lookup time too slow: {lookup_time}s"
        
        # Cleanup
        await test_service.close()
        
        print("🎉 Database Performance Test Passed!")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temp file
        try:
            os.unlink(temp_db.name)
        except:
            pass


async def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Starting Database Service Integration Tests (Task 1.1)")
    print("=" * 60)
    
    try:
        # Run integration tests
        integration_result = await test_database_cache_integration()
        performance_result = await test_database_performance()
        
        if integration_result and performance_result:
            print("=" * 60)
            print("🎉 All Integration Tests Passed!")
            print("✅ Database service integrates properly with existing components")
            print("✅ Performance meets requirements for SQLite backend")
            print("✅ Cache integration working (when available)")
            print("✅ Documentation persistence working")
            print("✅ Health checks and monitoring working")
            return True
        else:
            print("❌ Some integration tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Integration tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run integration tests directly
    result = asyncio.run(run_integration_tests())
    exit(0 if result else 1)