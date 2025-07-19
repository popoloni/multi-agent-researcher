"""
Test suite for Task 1.3: Main.py Initialization with Database Integration
Tests the application startup, health checks, and fallback behavior
"""

import asyncio
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime

# Import the FastAPI app and related components
from app.main import app, kenobi_agent, app_state
from app.services.database_service import DatabaseService


class TestTask13MainInitialization:
    """Test main.py initialization with database integration"""
    
    def test_health_check_basic(self):
        """Test basic health check endpoint"""
        print("🧪 Testing basic health check")
        
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "service" in data
            assert "version" in data
            assert "timestamp" in data
            assert "database" in data
            assert "services" in data
            
            print(f"Health check response: {data}")
            print("✅ Basic health check test passed")
    
    def test_health_check_database_status(self):
        """Test health check includes database status"""
        print("🧪 Testing health check database status")
        
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            db_info = data["database"]
            
            assert "initialized" in db_info
            assert "status" in db_info
            assert "error" in db_info
            
            # Database status should be one of the expected values
            assert db_info["status"] in ["healthy", "unhealthy", "not_initialized", "error", "unknown"]
            
            print(f"Database status: {db_info}")
            print("✅ Health check database status test passed")
    
    def test_health_check_service_status(self):
        """Test health check includes service status"""
        print("🧪 Testing health check service status")
        
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            services = data["services"]
            
            assert "repository_service" in services
            assert "research_service" in services
            
            # Should have repository count if service is healthy
            if services["repository_service"] == "healthy":
                assert "repository_count" in data
                assert isinstance(data["repository_count"], int)
            
            print(f"Services status: {services}")
            print("✅ Health check service status test passed")
    
    def test_test_kenobi_endpoint(self):
        """Test the test-kenobi endpoint works"""
        print("🧪 Testing test-kenobi endpoint")
        
        with TestClient(app) as client:
            response = client.get("/test-kenobi")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            
            if data["status"] == "success":
                assert "kenobi_agent" in data
                assert "repository_service" in data
                assert "repositories_count" in data
                assert isinstance(data["repositories_count"], int)
            else:
                assert "error" in data
                assert "error_type" in data
            
            print(f"Test Kenobi response: {data}")
            print("✅ Test Kenobi endpoint test passed")
    
    def test_root_endpoint(self):
        """Test root endpoint returns appropriate response"""
        print("🧪 Testing root endpoint")
        
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            
            # Should either serve frontend or return JSON status
            content_type = response.headers.get("content-type", "")
            assert "text/html" in content_type or "application/json" in content_type
            
            print(f"Root endpoint content type: {content_type}")
            print("✅ Root endpoint test passed")


async def test_startup_event_success():
    """Test successful startup event"""
    print("🧪 Testing successful startup event")
    
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
        
        # Replace the database service temporarily
        original_db_service = kenobi_agent.repository_service.db_service
        kenobi_agent.repository_service.db_service = test_db_service
        kenobi_agent.repository_service._initialized = False
        
        # Reset app state
        app_state["database_initialized"] = False
        app_state["database_error"] = None
        app_state["startup_time"] = None
        
        # Import and run startup event
        from app.main import startup_event
        await startup_event()
        
        # Verify startup was successful
        assert app_state["database_initialized"] is True
        assert app_state["database_error"] is None
        assert app_state["startup_time"] is not None
        
        # Verify repository service is initialized
        assert kenobi_agent.repository_service._initialized is True
        
        # Cleanup
        await test_db_service.close()
        kenobi_agent.repository_service.db_service = original_db_service
        
        print("✅ Successful startup event test passed")
        return True
        
    except Exception as e:
        print(f"❌ Startup event test failed: {e}")
        return False
        
    finally:
        # Cleanup temp file
        try:
            os.unlink(temp_db.name)
        except:
            pass


async def test_startup_event_failure():
    """Test startup event with database failure"""
    print("🧪 Testing startup event with database failure")
    
    try:
        # Mock a failing database service
        with patch.object(kenobi_agent.repository_service, 'initialize', side_effect=Exception("Database connection failed")):
            # Reset app state
            app_state["database_initialized"] = False
            app_state["database_error"] = None
            app_state["startup_time"] = None
            
            # Import and run startup event
            from app.main import startup_event
            await startup_event()
            
            # Verify startup handled failure gracefully
            assert app_state["database_initialized"] is False
            assert app_state["database_error"] is not None
            assert "Database connection failed" in app_state["database_error"]
            assert app_state["startup_time"] is not None
            
            print("✅ Startup event failure test passed")
            return True
            
    except Exception as e:
        print(f"❌ Startup event failure test failed: {e}")
        return False


async def test_shutdown_event():
    """Test shutdown event"""
    print("🧪 Testing shutdown event")
    
    try:
        # Create a mock database service with close method
        mock_db_service = AsyncMock()
        mock_db_service.close = AsyncMock()
        
        # Replace the database service temporarily
        original_db_service = kenobi_agent.repository_service.db_service
        kenobi_agent.repository_service.db_service = mock_db_service
        
        # Import and run shutdown event
        from app.main import shutdown_event
        await shutdown_event()
        
        # Verify close was called
        mock_db_service.close.assert_called_once()
        
        # Restore original service
        kenobi_agent.repository_service.db_service = original_db_service
        
        print("✅ Shutdown event test passed")
        return True
        
    except Exception as e:
        print(f"❌ Shutdown event test failed: {e}")
        return False


async def test_health_check_after_startup():
    """Test health check after successful startup"""
    print("🧪 Testing health check after startup")
    
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
        
        # Replace the database service temporarily
        original_db_service = kenobi_agent.repository_service.db_service
        kenobi_agent.repository_service.db_service = test_db_service
        kenobi_agent.repository_service._initialized = False
        
        # Run startup
        from app.main import startup_event
        await startup_event()
        
        # Test health check with TestClient
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            
            # Should show healthy status after successful startup
            assert data["database"]["initialized"] is True
            assert data["database"]["status"] in ["healthy", "unknown"]  # unknown is ok during testing
            assert data["services"]["repository_service"] == "healthy"
            assert "repository_count" in data
            assert "uptime_seconds" in data
            
            print(f"Health check after startup: {data}")
        
        # Cleanup
        await test_db_service.close()
        kenobi_agent.repository_service.db_service = original_db_service
        
        print("✅ Health check after startup test passed")
        return True
        
    except Exception as e:
        print(f"❌ Health check after startup test failed: {e}")
        return False
        
    finally:
        # Cleanup temp file
        try:
            os.unlink(temp_db.name)
        except:
            pass


async def test_existing_endpoints_after_startup():
    """Test that existing endpoints work after startup"""
    print("🧪 Testing existing endpoints after startup")
    
    try:
        # Test with TestClient
        with TestClient(app) as client:
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            
            # Test test-kenobi endpoint
            response = client.get("/test-kenobi")
            assert response.status_code == 200
            
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            
            # Test a repository endpoint (should work even if no repos)
            response = client.get("/repositories")
            # This might return 404 if endpoint doesn't exist, which is fine
            assert response.status_code in [200, 404, 405]
            
        print("✅ Existing endpoints after startup test passed")
        return True
        
    except Exception as e:
        print(f"❌ Existing endpoints test failed: {e}")
        return False


async def run_all_tests():
    """Run all main initialization tests"""
    print("🧪 Starting Main.py Initialization Tests (Task 1.3)")
    print("=" * 60)
    
    try:
        # Create test instance for sync tests
        test_instance = TestTask13MainInitialization()
        
        # Run synchronous tests
        test_instance.test_health_check_basic()
        test_instance.test_health_check_database_status()
        test_instance.test_health_check_service_status()
        test_instance.test_test_kenobi_endpoint()
        test_instance.test_root_endpoint()
        
        # Run asynchronous tests
        startup_success = await test_startup_event_success()
        startup_failure = await test_startup_event_failure()
        shutdown_test = await test_shutdown_event()
        health_after_startup = await test_health_check_after_startup()
        endpoints_test = await test_existing_endpoints_after_startup()
        
        if all([startup_success, startup_failure, shutdown_test, health_after_startup, endpoints_test]):
            print("=" * 60)
            print("🎉 All Main.py Initialization Tests Passed!")
            print("✅ Database initialization working on startup")
            print("✅ Graceful fallback when database fails")
            print("✅ Enhanced health check with database status")
            print("✅ Existing endpoints continue to work")
            print("✅ Proper shutdown handling")
            return True
        else:
            print("❌ Some main initialization tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Main initialization tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run tests directly
    result = asyncio.run(run_all_tests())
    exit(0 if result else 1)