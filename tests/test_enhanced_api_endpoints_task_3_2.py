"""
Task 3.2: Enhanced API Endpoints - Comprehensive Test Suite

This test suite validates the enhanced API endpoints for research functionality,
including detailed status, progress tracking, history, analytics, and polling.

Test Coverage:
- Enhanced status endpoint returns detailed progress
- History endpoint with filtering and pagination  
- Analytics endpoints return accurate data
- Error handling for invalid research IDs
- API response validation and serialization
- Performance testing for concurrent requests
"""

import pytest
import asyncio
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.services.research_service import ResearchService
from app.models.schemas import (
    ResearchQuery, ResearchResult, ResearchProgress, DetailedResearchStatus,
    ResearchStage, ResearchHistoryItem, ResearchAnalytics, ProgressPollResponse,
    ResearchListResponse, ResearchStartResponse, AgentStatus, StageProgress,
    AgentActivity
)


class TestEnhancedAPIEndpointsTask32:
    """Test suite for Task 3.2: Enhanced API Endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_research_service(self):
        """Create mock research service"""
        return AsyncMock(spec=ResearchService)
    
    @pytest.fixture
    def sample_research_query(self):
        """Create sample research query"""
        return ResearchQuery(
            query="What are the latest AI developments in 2025?",
            max_subagents=3,
            max_iterations=5
        )
    
    @pytest.fixture
    def sample_research_progress(self):
        """Create sample research progress"""
        return ResearchProgress(
            research_id=uuid4(),
            current_stage=ResearchStage.EXECUTING,
            overall_progress_percentage=45,
            stage_progress=[
                StageProgress(
                    stage=ResearchStage.PLANNING,
                    progress_percentage=100,
                    start_time=datetime.now(timezone.utc) - timedelta(minutes=5),
                    end_time=datetime.now(timezone.utc) - timedelta(minutes=4),
                    message="Planning completed successfully",
                    details={"plan_created": True}
                ),
                StageProgress(
                    stage=ResearchStage.EXECUTING,
                    progress_percentage=45,
                    start_time=datetime.now(timezone.utc) - timedelta(minutes=4),
                    message="Research execution in progress",
                    details={"active_agents": 3}
                )
            ],
            agent_activities=[
                AgentActivity(
                    agent_id="agent_1",
                    agent_name="Search Agent Alpha",
                    status=AgentStatus.SEARCHING,
                    current_task="Finding AI research papers",
                    progress_percentage=60,
                    start_time=datetime.now(timezone.utc) - timedelta(minutes=4),
                    last_update=datetime.now(timezone.utc),
                    sources_found=5,
                    tokens_used=1200
                ),
                AgentActivity(
                    agent_id="agent_2",
                    agent_name="Analysis Agent Beta", 
                    status=AgentStatus.ANALYZING,
                    current_task="Analyzing market trends",
                    progress_percentage=45,
                    start_time=datetime.now(timezone.utc) - timedelta(minutes=4),
                    last_update=datetime.now(timezone.utc),
                    sources_found=3,
                    tokens_used=800
                ),
                AgentActivity(
                    agent_id="agent_3",
                    agent_name="Research Agent Gamma",
                    status=AgentStatus.SEARCHING,
                    current_task="Gathering industry reports",
                    progress_percentage=30,
                    start_time=datetime.now(timezone.utc) - timedelta(minutes=4),
                    last_update=datetime.now(timezone.utc),
                    sources_found=2,
                    tokens_used=600
                )
            ],
            start_time=datetime.now(timezone.utc) - timedelta(minutes=5),
            estimated_completion_time=datetime.now(timezone.utc) + timedelta(minutes=3),
            last_update=datetime.now(timezone.utc)
        )
    
    @pytest.fixture
    def sample_detailed_status(self, sample_research_progress):
        """Create sample detailed research status"""
        return DetailedResearchStatus(
            research_id=uuid4(),
            query="What are the latest AI developments in 2025?",
            status=ResearchStage.EXECUTING,
            progress=sample_research_progress,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            estimated_completion_time=datetime.now(timezone.utc) + timedelta(minutes=3)
        )
    
    @pytest.fixture
    def sample_history_items(self):
        """Create sample research history items"""
        return [
            ResearchHistoryItem(
                research_id=uuid4(),
                query="AI developments in 2025",
                status=ResearchStage.COMPLETED,
                created_at=datetime.now(timezone.utc) - timedelta(hours=1),
                completed_at=datetime.now(timezone.utc) - timedelta(minutes=50),
                execution_time=600.0,
                sources_count=15,
                tokens_used=5000,
                progress_percentage=100.0
            ),
            ResearchHistoryItem(
                research_id=uuid4(),
                query="Machine learning trends",
                status=ResearchStage.EXECUTING,
                created_at=datetime.now(timezone.utc) - timedelta(minutes=30),
                progress_percentage=65.0
            ),
            ResearchHistoryItem(
                research_id=uuid4(),
                query="Quantum computing advances",
                status=ResearchStage.FAILED,
                created_at=datetime.now(timezone.utc) - timedelta(hours=2),
                error_message="API rate limit exceeded"
            )
        ]
    
    @pytest.fixture
    def sample_analytics(self):
        """Create sample research analytics"""
        return ResearchAnalytics(
            total_research_sessions=25,
            active_sessions=3,
            completed_sessions=20,
            failed_sessions=2,
            average_execution_time=450.0,
            total_tokens_used=125000,
            total_sources_found=300,
            success_rate=80.0,
            most_common_queries=[
                "AI developments",
                "Machine learning trends", 
                "Technology innovations",
                "Market analysis",
                "Research insights"
            ],
            performance_trends={
                "average_tokens_per_session": 5000,
                "average_sources_per_session": 12,
                "completion_rate": 80.0,
                "active_session_ratio": 12.0
            }
        )
    
    # ===== TEST 3.2.1: Enhanced Status Endpoint Returns Detailed Progress =====
    
    @patch('app.main.research_service')
    def test_enhanced_status_endpoint_returns_detailed_progress(
        self, mock_service, client, sample_detailed_status
    ):
        """Test 3.2.1: Enhanced status endpoint returns detailed progress"""
        
        # Setup mock
        research_id = sample_detailed_status.research_id
        mock_service.get_detailed_status = AsyncMock(return_value=sample_detailed_status)
        
        # Make request
        response = client.get(f"/research/{research_id}/status")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify detailed status structure
        assert data["research_id"] == str(research_id)
        assert data["query"] == sample_detailed_status.query
        assert data["status"] == sample_detailed_status.status
        assert "progress" in data
        assert "created_at" in data
        assert "estimated_completion_time" in data
        
        # Verify progress details
        progress = data["progress"]
        assert progress["current_stage"] == ResearchStage.EXECUTING
        assert progress["overall_progress_percentage"] == 45.0
        assert "stage_progress" in progress
        assert "active_agents" in progress
        assert "estimated_completion_time" in progress
        
        # Verify service was called correctly
        mock_service.get_detailed_status.assert_called_once_with(research_id)
    
    @patch('app.main.research_service')
    def test_enhanced_status_endpoint_handles_not_found(self, mock_service, client):
        """Test enhanced status endpoint handles research not found"""
        
        # Setup mock to return None
        research_id = uuid4()
        mock_service.get_detailed_status = AsyncMock(return_value=None)
        
        # Make request
        response = client.get(f"/research/{research_id}/status")
        
        # Verify 404 response
        assert response.status_code == 404
        assert "Research ID not found" in response.json()["detail"]
    
    @patch('app.main.research_service')
    def test_enhanced_status_endpoint_handles_service_error(self, mock_service, client):
        """Test enhanced status endpoint handles service errors"""
        
        # Setup mock to raise exception
        research_id = uuid4()
        mock_service.get_detailed_status = AsyncMock(side_effect=Exception("Service error"))
        
        # Make request
        response = client.get(f"/research/{research_id}/status")
        
        # Verify 500 response
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]
    
    # ===== TEST 3.2.2: History Endpoint with Filtering and Pagination =====
    
    @patch('app.main.research_service')
    def test_history_endpoint_with_pagination(
        self, mock_service, client, sample_history_items
    ):
        """Test 3.2.2: History endpoint with filtering and pagination"""
        
        # Setup mock
        mock_service.get_research_history = AsyncMock(return_value=sample_history_items[:2])
        mock_service.get_research_count = AsyncMock(return_value=10)
        
        # Make request with pagination
        response = client.get("/research/history?limit=2&offset=0")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total_count" in data
        assert "page" in data
        assert "page_size" in data
        assert "has_next" in data
        assert "has_previous" in data
        
        # Verify pagination values
        assert data["total_count"] == 10
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["has_next"] is True
        assert data["has_previous"] is False
        
        # Verify items
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert "research_id" in item
            assert "query" in item
            assert "status" in item
            assert "created_at" in item
        
        # Verify service calls
        mock_service.get_research_history.assert_called_once_with(
            limit=2, offset=0, status_filter=None
        )
        mock_service.get_research_count.assert_called_once_with(None)
    
    @patch('app.main.research_service')
    def test_history_endpoint_with_status_filter(
        self, mock_service, client, sample_history_items
    ):
        """Test history endpoint with status filtering"""
        
        # Setup mock for completed research only
        completed_items = [item for item in sample_history_items 
                          if item.status == ResearchStage.COMPLETED]
        mock_service.get_research_history = AsyncMock(return_value=completed_items)
        mock_service.get_research_count = AsyncMock(return_value=len(completed_items))
        
        # Make request with status filter
        response = client.get("/research/history?status_filter=completed")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify all items are completed
        for item in data["items"]:
            assert item["status"] == "completed"
        
        # Verify service was called with filter
        mock_service.get_research_history.assert_called_once_with(
            limit=50, offset=0, status_filter=ResearchStage.COMPLETED
        )
    
    @patch('app.main.research_service')
    def test_history_endpoint_handles_empty_results(self, mock_service, client):
        """Test history endpoint handles empty results"""
        
        # Setup mock for empty results
        mock_service.get_research_history = AsyncMock(return_value=[])
        mock_service.get_research_count = AsyncMock(return_value=0)
        
        # Make request
        response = client.get("/research/history")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["items"] == []
        assert data["total_count"] == 0
        assert data["has_next"] is False
        assert data["has_previous"] is False
    
    # ===== TEST 3.2.3: Analytics Endpoints Return Accurate Data =====
    
    @patch('app.main.research_service')
    def test_analytics_endpoint_returns_accurate_data(
        self, mock_service, client, sample_analytics
    ):
        """Test 3.2.3: Analytics endpoints return accurate data"""
        
        # Setup mock
        mock_service.get_research_analytics = AsyncMock(return_value=sample_analytics)
        
        # Make request
        response = client.get("/research/analytics")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify analytics structure
        assert "total_research_sessions" in data
        assert "active_sessions" in data
        assert "completed_sessions" in data
        assert "failed_sessions" in data
        assert "average_execution_time" in data
        assert "total_tokens_used" in data
        assert "total_sources_found" in data
        assert "success_rate" in data
        assert "most_common_queries" in data
        assert "performance_trends" in data
        
        # Verify analytics values
        assert data["total_research_sessions"] == 25
        assert data["active_sessions"] == 3
        assert data["completed_sessions"] == 20
        assert data["failed_sessions"] == 2
        assert data["success_rate"] == 80.0
        assert len(data["most_common_queries"]) == 5
        
        # Verify performance trends
        trends = data["performance_trends"]
        assert "average_tokens_per_session" in trends
        assert "average_sources_per_session" in trends
        assert "completion_rate" in trends
        assert "active_session_ratio" in trends
        
        # Verify service was called
        mock_service.get_research_analytics.assert_called_once()
    
    @patch('app.main.research_service')
    def test_analytics_endpoint_handles_service_error(self, mock_service, client):
        """Test analytics endpoint handles service errors"""
        
        # Setup mock to raise exception
        mock_service.get_research_analytics = AsyncMock(side_effect=Exception("Analytics error"))
        
        # Make request
        response = client.get("/research/analytics")
        
        # Verify 500 response
        assert response.status_code == 500
        assert "Analytics error" in response.json()["detail"]
    
    # ===== TEST 3.2.4: Error Handling for Invalid Research IDs =====
    
    @patch('app.main.research_service')
    def test_progress_endpoint_handles_invalid_research_id(self, mock_service, client):
        """Test 3.2.4: Error handling for invalid research IDs"""
        
        # Setup mock to return None
        research_id = uuid4()
        mock_service.get_progress = AsyncMock(return_value=None)
        
        # Make request
        response = client.get(f"/research/{research_id}/progress")
        
        # Verify 404 response
        assert response.status_code == 404
        assert "Research progress not found" in response.json()["detail"]
    
    def test_invalid_uuid_format_handling(self, client):
        """Test handling of invalid UUID format"""
        
        # Make request with invalid UUID
        response = client.get("/research/invalid-uuid/progress")
        
        # Verify 422 response (validation error)
        assert response.status_code == 422
    
    @patch('app.main.research_service')
    def test_polling_endpoint_handles_invalid_research_id(self, mock_service, client):
        """Test polling endpoint handles invalid research ID"""
        
        # Setup mock for non-existent research
        research_id = uuid4()
        poll_response = ProgressPollResponse(
            research_id=research_id,
            has_updates=False,
            progress=None,
            last_update=datetime.now(timezone.utc),
            next_poll_interval=5
        )
        mock_service.poll_research_progress = AsyncMock(return_value=poll_response)
        
        # Make request
        response = client.get(f"/research/{research_id}/poll")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["has_updates"] is False
        assert data["progress"] is None
        assert data["next_poll_interval"] == 5
    
    # ===== TEST 3.2.5: API Response Validation and Serialization =====
    
    @patch('app.main.research_service')
    def test_api_response_validation_and_serialization(
        self, mock_service, client, sample_research_progress
    ):
        """Test 3.2.5: API response validation and serialization"""
        
        # Setup mock
        research_id = uuid4()
        mock_service.get_progress = AsyncMock(return_value=sample_research_progress)
        
        # Make request
        response = client.get(f"/research/{research_id}/progress")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present and properly serialized
        assert "current_stage" in data
        assert "overall_progress_percentage" in data
        assert "stage_progress" in data
        assert "active_agents" in data
        assert "estimated_completion_time" in data
        assert "last_update" in data
        
        # Verify data types
        assert isinstance(data["overall_progress_percentage"], (int, float))
        assert isinstance(data["active_agents"], list)
        assert isinstance(data["stage_progress"], dict)
        
        # Verify datetime serialization
        assert isinstance(data["last_update"], str)
        assert isinstance(data["estimated_completion_time"], str)
        
        # Verify enum serialization
        assert data["current_stage"] in [stage for stage in ResearchStage]
    
    @patch('app.main.research_service')
    def test_start_research_response_serialization(
        self, mock_service, client, sample_research_query
    ):
        """Test start research response serialization"""
        
        # Setup mock
        research_id = uuid4()
        mock_service.start_research = AsyncMock(return_value=research_id)
        
        # Make request
        response = client.post("/research/start", json=sample_research_query.model_dump())
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "research_id" in data
        assert "status" in data
        assert "message" in data
        assert "estimated_duration" in data
        assert "created_at" in data
        
        # Verify data types
        assert isinstance(data["research_id"], str)
        assert isinstance(data["estimated_duration"], int)
        assert isinstance(data["created_at"], str)
        
        # Verify UUID format
        UUID(data["research_id"])  # Should not raise exception
    
    # ===== TEST 3.2.6: Performance Testing for Concurrent Requests =====
    
    @patch('app.main.research_service')
    def test_concurrent_requests_performance(self, mock_service, client, sample_analytics):
        """Test 3.2.6: Performance testing for concurrent requests"""
        
        # Setup mock
        mock_service.get_research_analytics = AsyncMock(return_value=sample_analytics)
        
        # Function to make request
        def make_request():
            return client.get("/research/analytics")
        
        # Make concurrent requests
        import concurrent.futures
        import time
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            responses = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all requests succeeded
        for response in responses:
            assert response.status_code == 200
        
        # Verify reasonable performance (should complete within 5 seconds)
        assert execution_time < 5.0
        
        # Verify service was called for each request
        assert mock_service.get_research_analytics.call_count == 20
    
    @patch('app.main.research_service')
    def test_concurrent_progress_polling(self, mock_service, client, sample_research_progress):
        """Test concurrent progress polling performance"""
        
        # Setup mock
        research_id = uuid4()
        poll_response = ProgressPollResponse(
            research_id=research_id,
            has_updates=True,
            progress=sample_research_progress,
            last_update=datetime.now(timezone.utc),
            next_poll_interval=2
        )
        mock_service.poll_research_progress = AsyncMock(return_value=poll_response)
        
        # Function to make polling request
        def make_poll_request():
            return client.get(f"/research/{research_id}/poll")
        
        # Make concurrent polling requests
        import concurrent.futures
        import time
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_poll_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all requests succeeded
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["has_updates"] is True
            assert data["next_poll_interval"] == 2
        
        # Verify reasonable performance for polling
        assert execution_time < 3.0
        
        # Verify service was called for each request
        assert mock_service.poll_research_progress.call_count == 10
    
    @patch('app.main.research_service')
    def test_history_pagination_performance(
        self, mock_service, client, sample_history_items
    ):
        """Test history pagination performance with large datasets"""
        
        # Setup mock for large dataset
        mock_service.get_research_history = AsyncMock(return_value=sample_history_items)
        mock_service.get_research_count = AsyncMock(return_value=1000)
        
        # Function to make paginated request
        def make_paginated_request(offset):
            return client.get(f"/research/history?limit=50&offset={offset}")
        
        # Make multiple paginated requests
        import concurrent.futures
        import time
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(make_paginated_request, offset) 
                for offset in range(0, 200, 50)
            ]
            responses = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all requests succeeded
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert data["total_count"] == 1000
        
        # Verify reasonable performance for pagination
        assert execution_time < 2.0
        
        # Verify service was called for each request
        assert mock_service.get_research_history.call_count == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])