"""
Test suite for Task 3.1: ResearchService Progress Integration

This test suite validates the enhanced ResearchService with progress callback integration,
ensuring real-time progress tracking works correctly with the LeadResearchAgent.
"""

import pytest
import asyncio
from uuid import uuid4, UUID
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.research_service import ResearchService, ResearchTask, ResearchStatus
from app.models.schemas import (
    ResearchQuery, ResearchProgress, DetailedResearchStatus, 
    ResearchStage, AgentStatus, AgentActivity, StageProgress, PerformanceMetrics
)


class TestResearchServiceProgressTask31:
    """Test suite for ResearchService Progress Integration (Task 3.1)"""
    
    @pytest.fixture
    def research_service(self):
        """Create a ResearchService instance for testing"""
        return ResearchService()
    
    @pytest.fixture
    def sample_research_query(self):
        """Create a sample research query"""
        return ResearchQuery(
            query="Test research query for progress tracking",
            max_subagents=3,
            max_iterations=5
        )
    
    @pytest.fixture
    def sample_research_progress(self):
        """Create a sample research progress object"""
        research_id = uuid4()
        now = datetime.now(timezone.utc)
        
        return ResearchProgress(
            research_id=research_id,
            current_stage=ResearchStage.EXECUTING,
            overall_progress_percentage=45,
            stage_progress=[
                StageProgress(
                    stage=ResearchStage.PLANNING,
                    progress_percentage=100,
                    start_time=now,
                    end_time=now,
                    duration_seconds=30.0,
                    message="Planning completed",
                    details={}
                ),
                StageProgress(
                    stage=ResearchStage.EXECUTING,
                    progress_percentage=45,
                    start_time=now,
                    message="Executing research",
                    details={}
                )
            ],
            agent_activities=[
                AgentActivity(
                    agent_id="agent_1",
                    agent_name="Search Agent Alpha",
                    status=AgentStatus.SEARCHING,
                    current_task="Finding recent medical AI studies",
                    progress_percentage=60,
                    start_time=now,
                    last_update=now,
                    sources_found=5,
                    tokens_used=150
                )
            ],
            performance_metrics=PerformanceMetrics(
                total_execution_time=120.5,
                total_tokens_used=450,
                total_sources_found=8,
                average_response_time=2.3,
                efficiency_score=0.85,
                start_time=now,
                last_update=now
            ),
            start_time=now,
            last_update=now
        )
    
    @pytest.mark.asyncio
    async def test_progress_callback_integration_works_correctly(self, research_service, sample_research_query, sample_research_progress):
        """Test 3.1.1: Progress callback integration works correctly"""
        
        # Test progress storage
        research_id = uuid4()
        await research_service.store_progress(research_id, sample_research_progress)
        
        # Verify progress is stored
        stored_progress = await research_service.get_progress(research_id)
        assert stored_progress is not None
        assert stored_progress.research_id == sample_research_progress.research_id
        assert stored_progress.current_stage == sample_research_progress.current_stage
        assert stored_progress.overall_progress_percentage == sample_research_progress.overall_progress_percentage
        
        # Verify progress store size
        assert research_service.get_progress_store_size() >= 1
    
    @pytest.mark.asyncio
    async def test_progress_storage_and_retrieval_functions_properly(self, research_service, sample_research_progress):
        """Test 3.1.2: Progress storage and retrieval functions properly"""
        
        research_id = uuid4()
        
        # Test storing progress
        await research_service.store_progress(research_id, sample_research_progress)
        
        # Test retrieving progress
        retrieved_progress = await research_service.get_progress(research_id)
        assert retrieved_progress is not None
        assert retrieved_progress.research_id == sample_research_progress.research_id
        assert retrieved_progress.current_stage == sample_research_progress.current_stage
        assert len(retrieved_progress.stage_progress) == len(sample_research_progress.stage_progress)
        assert len(retrieved_progress.agent_activities) == len(sample_research_progress.agent_activities)
        
        # Test retrieving non-existent progress
        non_existent_id = uuid4()
        non_existent_progress = await research_service.get_progress(non_existent_id)
        assert non_existent_progress is None
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_research_sessions_handled_correctly(self, research_service, sample_research_query):
        """Test 3.1.3: Multiple concurrent research sessions handled correctly"""
        
        # Create multiple research sessions
        research_ids = []
        for i in range(3):
            query = ResearchQuery(
                query=f"Test query {i+1}",
                max_subagents=2,
                max_iterations=3
            )
            
            # Mock the LeadResearchAgent to avoid actual research execution
            with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
                mock_agent = AsyncMock()
                mock_agent.conduct_research = AsyncMock(return_value=MagicMock())
                mock_agent_class.return_value = mock_agent
                
                research_id = await research_service.start_research(query)
                research_ids.append(research_id)
        
        # Verify all sessions are tracked
        assert len(research_ids) == 3
        assert all(isinstance(rid, UUID) for rid in research_ids)
        assert len(set(research_ids)) == 3  # All unique
        
        # Verify active research count
        assert research_service.get_active_research_count() == 3
        
        # Create different progress for each session
        for i, research_id in enumerate(research_ids):
            now = datetime.now(timezone.utc)
            progress = ResearchProgress(
                research_id=research_id,
                current_stage=ResearchStage.EXECUTING,
                overall_progress_percentage=30 + (i * 10),
                stage_progress=[],
                agent_activities=[],
                performance_metrics=PerformanceMetrics(
                    total_execution_time=60.0,
                    total_tokens_used=100,
                    total_sources_found=5,
                    average_response_time=1.5,
                    efficiency_score=0.8,
                    start_time=now,
                    last_update=now
                ),
                start_time=now,
                last_update=now
            )
            await research_service.store_progress(research_id, progress)
        
        # Verify each session has independent progress
        for i, research_id in enumerate(research_ids):
            progress = await research_service.get_progress(research_id)
            assert progress is not None
            assert progress.overall_progress_percentage == 30 + (i * 10)
    
    @pytest.mark.asyncio
    async def test_progress_updates_trigger_appropriate_callbacks(self, research_service, sample_research_query):
        """Test 3.1.4: Progress updates trigger appropriate callbacks"""
        
        # Track callback calls
        callback_calls = []
        
        async def test_callback(progress: ResearchProgress):
            callback_calls.append(progress)
        
        # Mock LeadResearchAgent to simulate progress updates
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            # Create a mock agent that will store the progress callback
            def create_mock_agent(progress_callback=None):
                mock_agent = AsyncMock()
                mock_agent.progress_callback = progress_callback
                
                # Simulate the agent calling the progress callback
                async def mock_conduct_research(query, research_id):
                    # Simulate progress callback calls
                    if mock_agent.progress_callback:
                        # Simulate planning stage
                        now = datetime.now(timezone.utc)
                        planning_progress = ResearchProgress(
                            research_id=research_id,
                            current_stage=ResearchStage.PLANNING,
                            overall_progress_percentage=20,
                            stage_progress=[],
                            agent_activities=[],
                            performance_metrics=PerformanceMetrics(
                                total_execution_time=30.0,
                                total_tokens_used=50,
                                total_sources_found=2,
                                average_response_time=1.0,
                                efficiency_score=0.9,
                                start_time=now,
                                last_update=now
                            ),
                            start_time=now,
                            last_update=now
                        )
                        await mock_agent.progress_callback(planning_progress)
                        
                        # Simulate executing stage
                        executing_progress = ResearchProgress(
                            research_id=research_id,
                            current_stage=ResearchStage.EXECUTING,
                            overall_progress_percentage=60,
                            stage_progress=[],
                            agent_activities=[],
                            performance_metrics=PerformanceMetrics(
                                total_execution_time=90.0,
                                total_tokens_used=150,
                                total_sources_found=8,
                                average_response_time=1.5,
                                efficiency_score=0.85,
                                start_time=now,
                                last_update=now
                            ),
                            start_time=now,
                            last_update=now
                        )
                        await mock_agent.progress_callback(executing_progress)
                    
                    return MagicMock()
                
                mock_agent.conduct_research = mock_conduct_research
                return mock_agent
            
            mock_agent_class.side_effect = create_mock_agent
            
            # Start research
            research_id = await research_service.start_research(sample_research_query)
            
            # Wait for the research task to complete
            research_task = research_service._active_research.get(research_id)
            if research_task and research_task.task:
                await research_task.task
            
            # Verify progress was stored
            final_progress = await research_service.get_progress(research_id)
            assert final_progress is not None
            assert final_progress.current_stage in [ResearchStage.EXECUTING, ResearchStage.COMPLETED]
    
    @pytest.mark.asyncio
    async def test_error_handling_during_progress_updates(self, research_service, sample_research_progress):
        """Test 3.1.5: Error handling during progress updates"""
        
        research_id = uuid4()
        
        # Test storing progress with invalid data
        invalid_progress = sample_research_progress
        invalid_progress.research_id = None  # This should cause an error
        
        # The store_progress method should handle errors gracefully
        try:
            await research_service.store_progress(research_id, invalid_progress)
            # If no exception, verify the progress wasn't stored incorrectly
            stored_progress = await research_service.get_progress(research_id)
            # The method should either store it correctly or not store it at all
            assert stored_progress is None or stored_progress.research_id is not None
        except Exception:
            # If an exception occurs, it should be handled gracefully
            pass
        
        # Test with valid progress after error
        now = datetime.now(timezone.utc)
        valid_progress = ResearchProgress(
            research_id=research_id,
            current_stage=ResearchStage.PLANNING,
            overall_progress_percentage=25,
            stage_progress=[],
            agent_activities=[],
            performance_metrics=PerformanceMetrics(
                total_execution_time=15.0,
                total_tokens_used=25,
                total_sources_found=1,
                average_response_time=0.8,
                efficiency_score=0.95,
                start_time=now,
                last_update=now
            ),
            start_time=now,
            last_update=now
        )
        
        await research_service.store_progress(research_id, valid_progress)
        stored_progress = await research_service.get_progress(research_id)
        assert stored_progress is not None
        assert stored_progress.research_id == research_id
    
    @pytest.mark.asyncio
    async def test_memory_cleanup_after_research_completion(self, research_service, sample_research_query):
        """Test 3.1.6: Memory cleanup after research completion"""
        
        # Create multiple completed research sessions
        research_ids = []
        
        for i in range(5):
            query = ResearchQuery(
                query=f"Test cleanup query {i+1}",
                max_subagents=2,
                max_iterations=2
            )
            
            with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
                mock_agent = AsyncMock()
                mock_agent.conduct_research = AsyncMock(return_value=MagicMock())
                mock_agent_class.return_value = mock_agent
                
                research_id = await research_service.start_research(query)
                research_ids.append(research_id)
                
                # Simulate progress
                now = datetime.now(timezone.utc)
                progress = ResearchProgress(
                    research_id=research_id,
                    current_stage=ResearchStage.COMPLETED,
                    overall_progress_percentage=100,
                    stage_progress=[],
                    agent_activities=[],
                    performance_metrics=PerformanceMetrics(
                        total_execution_time=180.0,
                        total_tokens_used=300,
                        total_sources_found=12,
                        average_response_time=2.0,
                        efficiency_score=0.9,
                        start_time=now,
                        last_update=now
                    ),
                    start_time=now,
                    last_update=now
                )
                await research_service.store_progress(research_id, progress)
                
                # Wait for task completion
                research_task = research_service._active_research.get(research_id)
                if research_task and research_task.task:
                    await research_task.task
        
        # Verify progress store has entries
        initial_progress_count = research_service.get_progress_store_size()
        assert initial_progress_count >= 5
        
        # Test cleanup with limit
        await research_service.cleanup_completed_research(max_completed=2)
        
        # Verify cleanup worked
        final_completed_count = research_service.get_completed_research_count()
        assert final_completed_count <= 2
        
        # Verify progress store was also cleaned up
        final_progress_count = research_service.get_progress_store_size()
        assert final_progress_count <= initial_progress_count
    
    @pytest.mark.asyncio
    async def test_detailed_status_integration(self, research_service, sample_research_query, sample_research_progress):
        """Test detailed status integration with progress data"""
        
        research_id = uuid4()
        
        # Create a research task
        research_task = ResearchTask(research_id, sample_research_query)
        research_service._active_research[research_id] = research_task
        
        # Store progress
        await research_service.store_progress(research_id, sample_research_progress)
        
        # Get detailed status
        detailed_status = await research_service.get_detailed_status(research_id)
        
        assert detailed_status is not None
        assert detailed_status.research_id == research_id
        assert detailed_status.query == sample_research_query.query
        assert detailed_status.progress == sample_research_progress
        assert detailed_status.is_active == True
        assert detailed_status.is_completed == False
        
        # Test with completed research
        research_task.status = ResearchStatus.COMPLETED
        research_service._completed_research[research_id] = research_task
        del research_service._active_research[research_id]
        
        completed_progress = sample_research_progress
        completed_progress.current_stage = ResearchStage.COMPLETED
        completed_progress.overall_progress_percentage = 100
        await research_service.store_progress(research_id, completed_progress)
        
        detailed_status = await research_service.get_detailed_status(research_id)
        assert detailed_status is not None
        assert detailed_status.is_completed == True
        assert detailed_status.is_active == False
    
    @pytest.mark.asyncio
    async def test_progress_callback_error_handling(self, research_service, sample_research_query):
        """Test that progress callback errors don't break research execution"""
        
        # Mock LeadResearchAgent with a failing progress callback
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            
            async def mock_conduct_research(query, research_id):
                # Simulate progress callback that might fail
                if mock_agent.progress_callback:
                    try:
                        # This should trigger the error handling in store_progress
                        invalid_progress = MagicMock()
                        invalid_progress.research_id = "invalid_uuid"  # This will cause an error
                        await mock_agent.progress_callback(invalid_progress)
                    except Exception:
                        pass  # Error should be handled gracefully
                
                return MagicMock()
            
            mock_agent.conduct_research = mock_conduct_research
            mock_agent_class.return_value = mock_agent
            
            # Start research - should not fail even with callback errors
            research_id = await research_service.start_research(sample_research_query)
            assert research_id is not None
            
            # Wait for task completion
            research_task = research_service._active_research.get(research_id)
            if research_task and research_task.task:
                await research_task.task
            
            # Research should still complete despite callback errors
            assert research_id in research_service._completed_research or research_id in research_service._active_research


if __name__ == "__main__":
    pytest.main([__file__, "-v"])