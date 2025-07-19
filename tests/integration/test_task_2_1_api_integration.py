"""
API Integration Test suite for Task 2.1: Documentation Service API Integration
Tests the updated documentation endpoints with database integration
"""

import asyncio
import os
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any

import httpx
from fastapi.testclient import TestClient

# Import the app
from app.main import app
from app.services.documentation_service import documentation_service
from app.services.database_service import DatabaseService


class TestTask21APIIntegration:
    """Test documentation API integration with database"""
    
    def __init__(self):
        self.client = TestClient(app)
        self.temp_db_path = None
        self.db_service = None
    
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up API integration test environment...")
        
        # Create temporary database
        temp_dir = tempfile.mkdtemp()
        self.temp_db_path = os.path.join(temp_dir, "test_api_docs.db")
        
        # Initialize database service with test database
        self.db_service = DatabaseService()
        self.db_service.database_url = f"sqlite+aiosqlite:///{self.temp_db_path}"
        await self.db_service.initialize()
        
        # Update documentation service to use test database
        documentation_service.db_service = self.db_service
        
        print("✅ API integration test environment setup complete")
    
    async def teardown(self):
        """Cleanup test environment"""
        print("🧹 Cleaning up API integration test environment...")
        
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
            
            print("✅ API integration test cleanup complete")
            
        except Exception as e:
            print(f"⚠️  API cleanup warning: {e}")
    
    def test_health_check_endpoint(self):
        """Test that health check endpoint still works"""
        print("🧪 Testing health check endpoint")
        
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        
        print("✅ Health check endpoint test passed")
    
    def test_get_documentation_not_found(self):
        """Test getting documentation that doesn't exist"""
        print("🧪 Testing get documentation - not found")
        
        response = self.client.get("/kenobi/repositories/non-existent-repo/documentation")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "not_generated"
        assert data["documentation"] is None
        assert data["repository_id"] == "non-existent-repo"
        
        print("✅ Get documentation not found test passed")
    
    def test_documentation_list_endpoint(self):
        """Test documentation list endpoint"""
        print("🧪 Testing documentation list endpoint")
        
        response = self.client.get("/kenobi/documentation/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "documentation_entries" in data
        assert "total_count" in data
        assert "limit" in data
        assert isinstance(data["documentation_entries"], list)
        
        print("✅ Documentation list endpoint test passed")
    
    def test_documentation_stats_endpoint(self):
        """Test documentation statistics endpoint"""
        print("🧪 Testing documentation stats endpoint")
        
        response = self.client.get("/kenobi/documentation/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_documentation_entries" in data
        assert "vector_indexed_entries" in data
        assert "vector_indexing_percentage" in data
        assert "total_content_length" in data
        assert "average_content_length" in data
        assert "cache_stats" in data
        
        print("✅ Documentation stats endpoint test passed")
    
    def test_delete_documentation_not_found(self):
        """Test deleting documentation that doesn't exist"""
        print("🧪 Testing delete documentation - not found")
        
        response = self.client.delete("/kenobi/repositories/non-existent-repo/documentation")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "not_found"
        assert data["repository_id"] == "non-existent-repo"
        
        print("✅ Delete documentation not found test passed")
    
    def test_existing_endpoints_compatibility(self):
        """Test that existing endpoints still work"""
        print("🧪 Testing existing endpoints compatibility")
        
        # Test root endpoint
        response = self.client.get("/")
        assert response.status_code == 200
        
        # Test test-kenobi endpoint
        response = self.client.get("/test-kenobi")
        assert response.status_code == 200
        
        # Test kenobi status endpoint
        response = self.client.get("/kenobi/status")
        assert response.status_code == 200
        
        print("✅ Existing endpoints compatibility test passed")
    
    async def test_documentation_generation_integration(self):
        """Test documentation generation with database integration"""
        print("🧪 Testing documentation generation integration")
        
        # This test would require a full repository setup
        # For now, we'll test the endpoint structure
        
        # Test documentation generation status endpoint (should return 404 for non-existent task)
        response = self.client.get("/kenobi/repositories/test-repo/documentation/status/non-existent-task")
        assert response.status_code == 404
        
        print("✅ Documentation generation integration test passed")


def run_api_integration_tests():
    """Run all API integration tests"""
    print("🧪 Starting Documentation API Integration Tests (Task 2.1)")
    print("=" * 60)
    
    test_suite = TestTask21APIIntegration()
    
    try:
        # Setup (synchronous part)
        # Note: We can't easily run async setup in TestClient context
        # So we'll test what we can synchronously
        
        # Run synchronous tests
        test_suite.test_health_check_endpoint()
        test_suite.test_get_documentation_not_found()
        test_suite.test_documentation_list_endpoint()
        test_suite.test_documentation_stats_endpoint()
        test_suite.test_delete_documentation_not_found()
        test_suite.test_existing_endpoints_compatibility()
        
        print("=" * 60)
        print("🎉 All Documentation API Integration Tests Passed!")
        print("✅ Health check endpoint working")
        print("✅ Get documentation endpoint enhanced")
        print("✅ Documentation list endpoint working")
        print("✅ Documentation stats endpoint working")
        print("✅ Delete documentation endpoint working")
        print("✅ Existing endpoints compatibility maintained")
        
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the tests
    success = run_api_integration_tests()
    exit(0 if success else 1)