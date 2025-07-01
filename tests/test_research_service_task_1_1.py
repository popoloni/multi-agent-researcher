"""
Unit tests for ResearchService Task 1.1: Basic ResearchService Structure
Tests real UUID generation, async task tracking, and basic status management
"""

import pytest
import asyncio
from uuid import UUID
from datetime import datetime

from app.services.research_service import ResearchService, ResearchStatus, ResearchTask
from app.models.schemas import ResearchQuery


class TestResearchServiceTask11:
    """Test suite for Task 1.1: Basic ResearchService Structure"""
    
    @pytest.fixture
    def research_service(self):
        """Create a fresh ResearchService instance for each test"""
        return ResearchService()
    
    @pytest.fixture
    def sample_query(self):
        """Create a sample research query"""
        return ResearchQuery(
            query="What are the latest AI developments in 2025?",
            max_subagents=3,
            max_iterations=5
        )
    
    def test_research_service_generates_real_uuid(self, research_service, sample_query):
        """Test that ResearchService generates real UUIDs, not mock ones"""
        # Start multiple research tasks
        research_ids = []
        
        async def start_multiple_research():
            for i in range(3):
                query = ResearchQuery(
                    query=f"Test query {i}",
                    max_subagents=2,
                    max_iterations=3
                )
                research_id = await research_service.start_research(query)
                research_ids.append(research_id)
        
        # Run the async function
        asyncio.run(start_multiple_research())
        
        # Verify all UUIDs are different (real UUIDs, not mocks)
        assert len(research_ids) == 3
        assert len(set(research_ids)) == 3  # All unique
        
        # Verify they are valid UUIDs
        for research_id in research_ids:
            assert isinstance(research_id, UUID)
            # Verify it's not the old mock UUID
            assert str(research_id) != '12345678-1234-5678-1234-567812345678'
    
    def test_async_task_tracking_works(self, research_service, sample_query):
        """Test that async task tracking mechanism works correctly"""
        
        async def test_tracking():
            # Start research
            research_id = await research_service.start_research(sample_query)
            
            # Verify task is tracked in active research
            assert research_id in research_service._active_research
            
            # Verify ResearchTask object is created correctly
            research_task = research_service._active_research[research_id]
            assert isinstance(research_task, ResearchTask)
            assert research_task.research_id == research_id
            assert research_task.query == sample_query
            assert research_task.status == ResearchStatus.STARTED
            assert isinstance(research_task.created_at, datetime)
            
            # Verify initial state
            assert research_task.progress_percentage == 10
            assert research_task.message == "Research task initiated and starting..."
            assert research_task.result is None
            assert research_task.error is None
            
            return research_id
        
        research_id = asyncio.run(test_tracking())
        
        # Verify tracking persists (might be in active or completed depending on timing)
        total_research = research_service.get_active_research_count() + research_service.get_completed_research_count()
        assert total_research == 1
    
    def test_basic_status_management(self, research_service, sample_query):
        """Test basic status management functionality"""
        
        async def test_status():
            # Start research
            research_id = await research_service.start_research(sample_query)
            
            # Get status
            status = await research_service.get_research_status(research_id)
            
            # Verify status structure
            assert status["status"] == "started"
            assert status["progress_percentage"] == 10
            assert status["message"] == "Research task initiated and starting..."
            assert "created_at" in status
            assert status["research_id"] == str(research_id)
            assert status["query"] == sample_query.query
            assert status["error"] is None
            
            # Test status for non-existent research
            fake_id = UUID('00000000-0000-0000-0000-000000000000')
            not_found_status = await research_service.get_research_status(fake_id)
            assert not_found_status["status"] == "not_found"
            assert not_found_status["message"] == "Research ID not found"
            assert not_found_status["research_id"] == str(fake_id)
        
        asyncio.run(test_status())
    
    def test_research_status_enum(self):
        """Test ResearchStatus enum values"""
        # Verify all expected status values exist
        expected_statuses = [
            "started", "planning", "executing", 
            "synthesizing", "citing", "completed", "failed"
        ]
        
        for status in expected_statuses:
            assert hasattr(ResearchStatus, status.upper())
            assert getattr(ResearchStatus, status.upper()).value == status
    
    def test_research_task_initialization(self, sample_query):
        """Test ResearchTask initialization"""
        research_id = UUID('11111111-1111-1111-1111-111111111111')
        task = ResearchTask(research_id, sample_query)
        
        assert task.research_id == research_id
        assert task.query == sample_query
        assert task.status == ResearchStatus.STARTED
        assert isinstance(task.created_at, datetime)
        assert task.progress_percentage == 0
        assert task.message == "Research initiated"
        assert task.task is None
        assert task.result is None
        assert task.error is None
    
    def test_concurrent_research_sessions(self, research_service):
        """Test that multiple concurrent research sessions work independently"""
        
        async def test_concurrent():
            # Start multiple research tasks concurrently
            queries = [
                ResearchQuery(query=f"Query {i}", max_subagents=2, max_iterations=3)
                for i in range(5)
            ]
            
            # Start all research tasks
            research_ids = []
            for query in queries:
                research_id = await research_service.start_research(query)
                research_ids.append(research_id)
            
            # Verify all are tracked independently
            assert len(research_ids) == 5
            assert len(set(research_ids)) == 5  # All unique
            assert research_service.get_active_research_count() == 5
            
            # Verify each has correct status
            for i, research_id in enumerate(research_ids):
                status = await research_service.get_research_status(research_id)
                assert status["status"] == "started"
                assert status["query"] == f"Query {i}"
                assert status["research_id"] == str(research_id)
        
        asyncio.run(test_concurrent())
    
    def test_cleanup_functionality(self, research_service):
        """Test cleanup functionality for completed research"""
        
        async def test_cleanup():
            # Simulate completed research by adding to completed dict
            for i in range(150):  # More than max_completed (100)
                research_id = UUID(f'{i:08d}-0000-0000-0000-000000000000')
                query = ResearchQuery(query=f"Query {i}")
                task = ResearchTask(research_id, query)
                task.status = ResearchStatus.COMPLETED
                research_service._completed_research[research_id] = task
            
            # Verify we have 150 completed research tasks
            assert research_service.get_completed_research_count() == 150
            
            # Run cleanup
            await research_service.cleanup_completed_research(max_completed=100)
            
            # Verify cleanup worked
            assert research_service.get_completed_research_count() == 100
        
        asyncio.run(test_cleanup())


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])