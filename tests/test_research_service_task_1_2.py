"""
Unit tests for ResearchService Task 1.2: Research Lifecycle Management
Tests real research task initiation, meaningful progress data, complete results, and lifecycle management
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID
from datetime import datetime, timezone

from app.services.research_service import ResearchService, ResearchStatus
from app.models.schemas import ResearchQuery, ResearchResult, CitationInfo, SearchResult


class TestResearchServiceTask12:
    """Test suite for Task 1.2: Research Lifecycle Management"""
    
    @pytest.fixture
    def research_service(self):
        """Create a fresh ResearchService instance for each test"""
        return ResearchService()
    
    @pytest.fixture
    def sample_query(self):
        """Create a sample research query"""
        return ResearchQuery(
            query="What are the latest AI developments in 2025?",
            max_subagents=2,
            max_iterations=3
        )
    
    @pytest.fixture
    def mock_research_result(self):
        """Create a mock research result"""
        return ResearchResult(
            research_id=UUID('11111111-1111-1111-1111-111111111111'),
            query="Test query",
            report="# Test Report\n\nThis is a test report with findings.",
            citations=[
                CitationInfo(index=1, title="Test Source", url="https://test.com", times_cited=1)
            ],
            sources_used=[
                SearchResult(
                    url="https://test.com",
                    title="Test Source",
                    snippet="Test snippet",
                    relevance_score=0.9
                )
            ],
            total_tokens_used=1500,
            execution_time=45.5,
            subagent_count=2,
            report_sections=["Introduction", "Findings", "Conclusion"]
        )
    
    @pytest.mark.asyncio
    async def test_start_research_initiates_real_task(self, research_service, sample_query):
        """Test that start_research initiates real research tasks with LeadResearchAgent"""
        
        # Mock the LeadResearchAgent and its methods
        with patch('app.services.research_service.LeadResearchAgent') as mock_lead_agent_class:
            mock_lead_agent = AsyncMock()
            mock_lead_agent_class.return_value = mock_lead_agent
            
            # Mock the research execution methods
            mock_lead_agent._create_research_plan = AsyncMock()
            mock_lead_agent._execute_research_plan = AsyncMock(return_value=[])
            mock_lead_agent._synthesize_results = AsyncMock(return_value="Test report")
            mock_lead_agent._add_citations = AsyncMock(return_value="Test report with citations")
            mock_lead_agent._extract_report_sections = MagicMock(return_value=["Section 1"])
            mock_lead_agent.citation_list = []
            mock_lead_agent.total_tokens = 1000
            mock_lead_agent.memory_store = AsyncMock()
            mock_lead_agent.memory_store.save_context = AsyncMock()
            mock_lead_agent.memory_store.save_result = AsyncMock()
            
            # Start research
            research_id = await research_service.start_research(sample_query)
            
            # Verify research task was created and started
            assert research_id in research_service._active_research
            research_task = research_service._active_research[research_id]
            
            # Verify task is actually running
            assert research_task.task is not None
            assert isinstance(research_task.task, asyncio.Task)
            assert not research_task.task.done()  # Should still be running
            
            # Verify initial status
            assert research_task.status == ResearchStatus.STARTED
            assert research_task.progress_percentage == 10
            assert "initiated" in research_task.message.lower()
            
            # Wait a bit for the task to progress
            await asyncio.sleep(0.1)
            
            # Cancel the task to clean up
            await research_service.cancel_research(research_id)
    
    @pytest.mark.asyncio
    async def test_status_provides_meaningful_progress(self, research_service, sample_query):
        """Test that get_research_status returns meaningful progress data"""
        
        # Start research
        research_id = await research_service.start_research(sample_query)
        
        # Get status immediately (should be in started state)
        status = await research_service.get_research_status(research_id)
        
        # Verify meaningful progress data
        assert status["status"] in ["started", "planning", "executing", "synthesizing", "citing", "completed", "failed"]
        assert isinstance(status["progress_percentage"], int)
        assert 0 <= status["progress_percentage"] <= 100
        assert isinstance(status["message"], str)
        assert len(status["message"]) > 0
        
        # Verify detailed information
        assert status["research_id"] == str(research_id)
        assert status["query"] == sample_query.query
        assert "created_at" in status
        assert "elapsed_time" in status
        assert status["max_subagents"] == sample_query.max_subagents
        assert status["max_iterations"] == sample_query.max_iterations
        
        # Test status for active research
        if research_id in research_service._active_research:
            # Should have elapsed time
            assert status["elapsed_time"] >= 0
            
            # Should not have completion info yet
            assert "completed" not in status or not status["completed"]
        
        # Clean up
        await research_service.cancel_research(research_id)
    
    @pytest.mark.asyncio
    async def test_result_contains_complete_data(self, research_service, sample_query, mock_research_result):
        """Test that get_research_result provides complete results"""
        
        # Start research
        research_id = await research_service.start_research(sample_query)
        
        # Simulate completed research by directly setting result
        research_task = research_service._active_research[research_id]
        research_task.result = mock_research_result
        research_task.status = ResearchStatus.COMPLETED
        
        # Move to completed research
        research_service._completed_research[research_id] = research_task
        del research_service._active_research[research_id]
        
        # Get result
        result = await research_service.get_research_result(research_id)
        
        # Verify complete data
        assert result is not None
        assert isinstance(result, ResearchResult)
        assert result.research_id == research_id  # Should be set correctly
        assert result.query == mock_research_result.query
        assert result.report == mock_research_result.report
        assert len(result.citations) == 1
        assert len(result.sources_used) == 1
        assert result.total_tokens_used == 1500
        assert result.execution_time == 45.5
        assert result.subagent_count == 2
        assert len(result.report_sections) == 3
    
    @pytest.mark.asyncio
    async def test_research_lifecycle_management(self, research_service, sample_query):
        """Test complete research lifecycle management"""
        
        # Mock LeadResearchAgent for controlled execution
        with patch('app.services.research_service.LeadResearchAgent') as mock_lead_agent_class:
            mock_lead_agent = AsyncMock()
            mock_lead_agent_class.return_value = mock_lead_agent
            
            # Mock all methods to complete quickly
            mock_plan = MagicMock()
            mock_plan.subtasks = [MagicMock()]
            mock_plan.dict.return_value = {"strategy": "Test", "subtasks": [], "estimated_complexity": "simple"}
            
            mock_lead_agent._create_research_plan = AsyncMock(return_value=mock_plan)
            mock_lead_agent._execute_research_plan = AsyncMock(return_value=[])
            mock_lead_agent._synthesize_results = AsyncMock(return_value="Final report")
            mock_lead_agent._add_citations = AsyncMock(return_value="Final report with citations")
            mock_lead_agent._extract_report_sections = MagicMock(return_value=["Section 1"])
            mock_lead_agent.citation_list = []
            mock_lead_agent.total_tokens = 1000
            mock_lead_agent.memory_store = AsyncMock()
            mock_lead_agent.memory_store.save_context = AsyncMock()
            mock_lead_agent.memory_store.save_result = AsyncMock()
            
            # Start research
            research_id = await research_service.start_research(sample_query)
            
            # Verify initial state
            assert research_id in research_service._active_research
            assert research_service.get_active_research_count() == 1
            assert research_service.get_completed_research_count() == 0
            
            # Wait for research to complete
            research_task = research_service._active_research[research_id]
            await research_task.task
            
            # Verify completion
            assert research_id not in research_service._active_research
            assert research_id in research_service._completed_research
            assert research_service.get_active_research_count() == 0
            assert research_service.get_completed_research_count() == 1
            
            # Verify final status
            completed_task = research_service._completed_research[research_id]
            assert completed_task.status == ResearchStatus.COMPLETED
            assert completed_task.progress_percentage == 100
            assert completed_task.result is not None
    
    @pytest.mark.asyncio
    async def test_research_cancellation(self, research_service, sample_query):
        """Test research cancellation functionality"""
        
        # Mock LeadResearchAgent to prevent actual execution
        with patch('app.services.research_service.LeadResearchAgent') as mock_lead_agent_class:
            mock_lead_agent = AsyncMock()
            mock_lead_agent_class.return_value = mock_lead_agent
            
            # Mock methods to hang (simulate long-running research)
            mock_lead_agent._create_research_plan = AsyncMock()
            mock_lead_agent._create_research_plan.side_effect = asyncio.sleep(10)  # Long delay
            
            # Start research
            research_id = await research_service.start_research(sample_query)
            
            # Verify research is active
            assert research_id in research_service._active_research
            
            # Cancel research
            cancelled = await research_service.cancel_research(research_id)
            
            # Verify cancellation
            assert cancelled is True
            assert research_id not in research_service._active_research
            assert research_id in research_service._completed_research
            
            # Verify cancelled status
            cancelled_task = research_service._completed_research[research_id]
            assert cancelled_task.status == ResearchStatus.FAILED
            assert "cancelled" in cancelled_task.message.lower()
            assert cancelled_task.error == "Cancelled"
    
    @pytest.mark.asyncio
    async def test_research_error_handling(self, research_service, sample_query):
        """Test research error handling"""
        
        # Mock LeadResearchAgent to raise an error
        with patch('app.services.research_service.LeadResearchAgent') as mock_lead_agent_class:
            mock_lead_agent = AsyncMock()
            mock_lead_agent_class.return_value = mock_lead_agent
            
            # Mock conduct_research method to raise an error
            mock_lead_agent.conduct_research = AsyncMock()
            mock_lead_agent.conduct_research.side_effect = Exception("Test error")
            
            # Start research
            research_id = await research_service.start_research(sample_query)
            
            # Wait for error to occur
            research_task = research_service._active_research[research_id]
            await research_task.task
            
            # Verify error handling
            assert research_id not in research_service._active_research
            assert research_id in research_service._completed_research
            
            failed_task = research_service._completed_research[research_id]
            assert failed_task.status == ResearchStatus.FAILED
            assert "failed" in failed_task.message.lower()
            assert failed_task.error == "Test error"
    
    def test_research_history(self, research_service, sample_query, mock_research_result):
        """Test research history functionality"""
        
        # Create some research history
        research_id1 = UUID('11111111-1111-1111-1111-111111111111')
        research_id2 = UUID('22222222-2222-2222-2222-222222222222')
        
        # Add completed research
        from app.services.research_service import ResearchTask
        task1 = ResearchTask(research_id1, sample_query)
        task1.status = ResearchStatus.COMPLETED
        task1.result = mock_research_result
        research_service._completed_research[research_id1] = task1
        
        task2 = ResearchTask(research_id2, sample_query)
        task2.status = ResearchStatus.FAILED
        task2.error = "Test error"
        research_service._completed_research[research_id2] = task2
        
        # Get history
        history = research_service.get_research_history(limit=10)
        
        # Verify history
        assert len(history) == 2
        
        # Check first item (most recent)
        item1 = history[0]
        assert item1["research_id"] == str(research_id2)
        assert item1["status"] == "failed"
        assert item1["query"] == sample_query.query
        
        # Check second item
        item2 = history[1]
        assert item2["research_id"] == str(research_id1)
        assert item2["status"] == "completed"
        assert "execution_time" in item2
        assert "sources_count" in item2
        assert "citations_count" in item2
        assert "tokens_used" in item2


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])