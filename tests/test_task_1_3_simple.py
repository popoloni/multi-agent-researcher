"""
Simple test suite for Task 1.3: Main.py Initialization
Tests the core functionality without complex TestClient interactions
"""

import asyncio
import logging
from datetime import datetime
from fastapi.testclient import TestClient

# Set up logging
logging.basicConfig(level=logging.INFO)

from app.main import app, app_state, kenobi_agent, startup_event, shutdown_event


async def test_startup_event_functionality():
    """Test startup event functionality"""
    print("🧪 Testing startup event functionality")
    
    # Reset app state
    app_state["database_initialized"] = False
    app_state["database_error"] = None
    app_state["startup_time"] = None
    kenobi_agent.repository_service._initialized = False
    
    # Call startup event
    await startup_event()
    
    # Verify startup was successful
    assert app_state["database_initialized"] is True
    assert app_state["database_error"] is None
    assert app_state["startup_time"] is not None
    assert kenobi_agent.repository_service._initialized is True
    
    # Test repository service works
    repos = await kenobi_agent.repository_service.list_repositories()
    assert isinstance(repos, list)
    
    print("✅ Startup event functionality test passed")
    return True


async def test_shutdown_event_functionality():
    """Test shutdown event functionality"""
    print("🧪 Testing shutdown event functionality")
    
    try:
        # Call shutdown event
        await shutdown_event()
        print("✅ Shutdown event functionality test passed")
        return True
    except Exception as e:
        print(f"❌ Shutdown event test failed: {e}")
        return False


def test_health_check_endpoint():
    """Test health check endpoint"""
    print("🧪 Testing health check endpoint")
    
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert "database" in data
        assert "services" in data
        
        # Database info should be present
        db_info = data["database"]
        assert "initialized" in db_info
        assert "status" in db_info
        assert "error" in db_info
        
        # Services info should be present
        services = data["services"]
        assert "repository_service" in services
        assert "research_service" in services
        
    print("✅ Health check endpoint test passed")
    return True


def test_test_kenobi_endpoint():
    """Test test-kenobi endpoint"""
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
        
    print("✅ Test Kenobi endpoint test passed")
    return True


def test_root_endpoint():
    """Test root endpoint"""
    print("🧪 Testing root endpoint")
    
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        
        # Should return JSON response since frontend is not built
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "message" in data
        
    print("✅ Root endpoint test passed")
    return True


async def test_database_initialization_with_failure():
    """Test database initialization with simulated failure"""
    print("🧪 Testing database initialization with failure")
    
    # Mock a failure by temporarily replacing the initialize method
    original_initialize = kenobi_agent.repository_service.initialize
    
    async def failing_initialize():
        raise Exception("Simulated database failure")
    
    kenobi_agent.repository_service.initialize = failing_initialize
    
    try:
        # Reset app state
        app_state["database_initialized"] = False
        app_state["database_error"] = None
        app_state["startup_time"] = None
        
        # Call startup event (should handle failure gracefully)
        await startup_event()
        
        # Verify failure was handled gracefully
        assert app_state["database_initialized"] is False
        assert app_state["database_error"] is not None
        assert "Simulated database failure" in app_state["database_error"]
        assert app_state["startup_time"] is not None
        
        print("✅ Database initialization failure test passed")
        return True
        
    finally:
        # Restore original method
        kenobi_agent.repository_service.initialize = original_initialize


async def test_repository_service_integration():
    """Test repository service integration after initialization"""
    print("🧪 Testing repository service integration")
    
    # Ensure service is initialized
    if not kenobi_agent.repository_service._initialized:
        await kenobi_agent.repository_service.initialize()
    
    # Test basic operations
    repos = await kenobi_agent.repository_service.list_repositories()
    assert isinstance(repos, list)
    
    # Test get non-existent repository
    repo = await kenobi_agent.repository_service.get_repository_metadata("non-existent")
    assert repo is None
    
    print("✅ Repository service integration test passed")
    return True


async def run_all_tests():
    """Run all simple tests"""
    print("🧪 Starting Simple Main.py Initialization Tests (Task 1.3)")
    print("=" * 60)
    
    try:
        # Run async tests
        startup_test = await test_startup_event_functionality()
        shutdown_test = await test_shutdown_event_functionality()
        failure_test = await test_database_initialization_with_failure()
        integration_test = await test_repository_service_integration()
        
        # Run sync tests
        health_test = test_health_check_endpoint()
        kenobi_test = test_test_kenobi_endpoint()
        root_test = test_root_endpoint()
        
        if all([startup_test, shutdown_test, failure_test, integration_test, 
                health_test, kenobi_test, root_test]):
            print("=" * 60)
            print("🎉 All Simple Main.py Initialization Tests Passed!")
            print("✅ Startup event working correctly")
            print("✅ Shutdown event working correctly")
            print("✅ Database failure handling working")
            print("✅ Health check endpoint enhanced")
            print("✅ Repository service integration working")
            print("✅ Existing endpoints continue to work")
            return True
        else:
            print("❌ Some tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run tests directly
    result = asyncio.run(run_all_tests())
    exit(0 if result else 1)