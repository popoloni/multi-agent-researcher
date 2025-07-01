"""
Test suite for Task 3.1: ResearchService Progress Integration

This test suite validates the enhanced ResearchService with progress callback integration,
ensuring real-time progress tracking works correctly with the LeadResearchAgent.
"""

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.research_service import ResearchService, ResearchTask
from app.models.schemas import (
    ResearchQuery, ResearchProgress, DetailedResearchStatus, 
    ResearchStage, AgentStatus, AgentActivity, StageProgress, PerformanceMetrics
)


class TestResearchServiceProgressIntegrationTask31:
    """Test suite for Task 3.1: ResearchService Progress Integration"""
    
    @pytest.fixture
    def research_service(self):
        """Create a ResearchService instance for testing"""
        return ResearchService()
    
    @pytest.fixture
    def sample_query(self):
        """Create a sample research query"""
        return ResearchQuery(
            query="Test research query for progress integration",
            max_subagents=3,
            max_iterations=5
        )
    
    @pytest.fixture
    def sample_progress(self):
        """Create a sample ResearchProgress object"""
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
                    message="Planning completed",
                    details={}
                ),
                StageProgress(
                    stage=ResearchStage.EXECUTING,
                    progress_percentage=45,
                    start_time=now,
                    message="Executing research with agents",
                    details={}
                )
            ],
            agent_activities=[
                AgentActivity(
                    agent_id="agent_1",
                    agent_name="Search Agent Alpha",
                    status=AgentStatus.SEARCHING,
                    current_task="Finding recent studies",
                    progress_percentage=60,
                    start_time=now,
                    last_update=now,
                    sources_found=5,
                    tokens_used=150
                )
            ],
            performance_metrics=PerformanceMetrics(
                total_execution_time=10.0,
                planning_time=2.0,
                execution_time=6.0,
                synthesis_time=1.5,
                citation_time=0.5,
                total_tokens_used=150,
                total_sources_found=5,
                average_agent_efficiency=0.85,
                success_rate=1.0
            ),
            start_time=now,
            last_update=now
        )
    
    @pytest.mark.asyncio
    async def test_progress_callback_integration_works_correctly(self, research_service, sample_query):
        """Test 3.1.1: Progress callback integration works correctly"""
        
        # Mock LeadResearchAgent to capture the progress callback
        captured_callback = None
        
        def mock_lead_agent_init(progress_callback=None):
            nonlocal captured_callback
            captured_callback = progress_callback
            mock_agent = AsyncMock()
            mock_agent.conduct_research = AsyncMock()
            return mock_agent
        
        with patch('app.services.research_service.LeadResearchAgent', side_effect=mock_lead_agent_init):
            # Start research
            research_id = await research_service.start_research(sample_query)
            
            # Wait a moment for the task to start
            await asyncio.sleep(0.1)
            
            # Verify callback was captured
            assert captured_callback is not None, "Progress callback should be passed to LeadResearchAgent"
            
            # Test the callback with sample progress
            sample_progress = ResearchProgress(
                research_id=research_id,
                current_stage=ResearchStage.PLANNING,
                overall_progress_percentage=25,
                stage_progress=[],
                agent_activities=[],
                performance_metrics=PerformanceMetrics(total_execution_time=1.0, total_tokens_used=0, total_sources_found=0, average_agent_efficiency=0.0, success_rate=0.0),
                start_time=datetime.now(timezone.utc),
                last_update=datetime.now(timezone.utc)
            )
            
            # Call the callback
            await captured_callback(sample_progress)
            
            # Verify progress was stored
            stored_progress = await research_service.get_progress(research_id)
            assert stored_progress is not None
            assert stored_progress.research_id == research_id
            assert stored_progress.current_stage == ResearchStage.PLANNING
            assert stored_progress.overall_progress_percentage == 25
    
    @pytest.mark.asyncio
    async def test_progress_storage_and_retrieval_functions_properly(self, research_service, sample_progress):
        """Test 3.1.2: Progress storage and retrieval functions properly"""
        
        research_id = sample_progress.research_id
        
        # Store progress
        await research_service.store_progress(research_id, sample_progress)
        
        # Retrieve progress
        retrieved_progress = await research_service.get_progress(research_id)
        
        # Verify retrieval
        assert retrieved_progress is not None
        assert retrieved_progress.research_id == research_id
        assert retrieved_progress.current_stage == sample_progress.current_stage
        assert retrieved_progress.overall_progress_percentage == sample_progress.overall_progress_percentage
        assert len(retrieved_progress.stage_progress) == len(sample_progress.stage_progress)
        assert len(retrieved_progress.agent_activities) == len(sample_progress.agent_activities)
        
        # Verify agent activity details
        assert retrieved_progress.agent_activities[0].agent_id == "agent_1"
        assert retrieved_progress.agent_activities[0].status == AgentStatus.SEARCHING
        assert retrieved_progress.agent_activities[0].sources_found == 5
        assert retrieved_progress.agent_activities[0].tokens_used == 150
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_research_sessions_handled_correctly(self, research_service, sample_query):
        """Test 3.1.3: Multiple concurrent research sessions handled correctly"""
        
        # Mock LeadResearchAgent to avoid actual research execution
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.conduct_research = AsyncMock()
            mock_agent_class.return_value = mock_agent
            
            # Start multiple research sessions
            research_id_1 = await research_service.start_research(sample_query)
            research_id_2 = await research_service.start_research(sample_query)
            research_id_3 = await research_service.start_research(sample_query)
            
            # Create different progress for each session
            progress_1 = ResearchProgress(
                research_id=research_id_1,
                current_stage=ResearchStage.PLANNING,
                overall_progress_percentage=20,
                stage_progress=[],
                agent_activities=[],
                performance_metrics=PerformanceMetrics(total_execution_time=1.0, total_tokens_used=0, total_sources_found=0, average_agent_efficiency=0.0, success_rate=0.0),
                start_time=datetime.now(timezone.utc),
                last_update=datetime.now(timezone.utc)
            )
            
            progress_2 = ResearchProgress(
                research_id=research_id_2,
                current_stage=ResearchStage.EXECUTING,
                overall_progress_percentage=50,
                stage_progress=[],
                agent_activities=[],
                performance_metrics=PerformanceMetrics(total_execution_time=1.0, total_tokens_used=0, total_sources_found=0, average_agent_efficiency=0.0, success_rate=0.0),
                start_time=datetime.now(timezone.utc),
                last_update=datetime.now(timezone.utc)
            )
            
            progress_3 = ResearchProgress(
                research_id=research_id_3,
                current_stage=ResearchStage.SYNTHESIZING,
                overall_progress_percentage=80,
                stage_progress=[],
                agent_activities=[],
                performance_metrics=PerformanceMetrics(total_execution_time=1.0, total_tokens_used=0, total_sources_found=0, average_agent_efficiency=0.0, success_rate=0.0),
                start_time=datetime.now(timezone.utc),
                last_update=datetime.now(timezone.utc)
            )
            
            # Store progress for each session
            await research_service.store_progress(research_id_1, progress_1)
            await research_service.store_progress(research_id_2, progress_2)
            await research_service.store_progress(research_id_3, progress_3)
            
            # Verify each session has correct progress
            retrieved_1 = await research_service.get_progress(research_id_1)
            retrieved_2 = await research_service.get_progress(research_id_2)
            retrieved_3 = await research_service.get_progress(research_id_3)
            
            assert retrieved_1.current_stage == ResearchStage.PLANNING
            assert retrieved_1.overall_progress_percentage == 20
            
            assert retrieved_2.current_stage == ResearchStage.EXECUTING
            assert retrieved_2.overall_progress_percentage == 50
            
            assert retrieved_3.current_stage == ResearchStage.SYNTHESIZING
            assert retrieved_3.overall_progress_percentage == 80
            
            # Verify sessions are independent
            assert research_service.get_active_research_count() == 3
            assert research_service.get_progress_store_size() == 3
    
    @pytest.mark.asyncio
    async def test_progress_updates_trigger_appropriate_callbacks(self, research_service, sample_query):
        """Test 3.1.4: Progress updates trigger appropriate callbacks"""
        
        callback_calls = []
        
        # Mock LeadResearchAgent to capture callback calls
        def mock_lead_agent_init(progress_callback=None):
            mock_agent = AsyncMock()
            
            async def mock_conduct_research(query, research_id):
                # Simulate progress updates during research
                if progress_callback:
                    # Planning stage
                    planning_progress = ResearchProgress(
                        research_id=research_id,
                        current_stage=ResearchStage.PLANNING,
                        overall_progress_percentage=25,
                        stage_progress=[],
                        agent_activities=[],
                        performance_metrics=PerformanceMetrics(total_execution_time=1.0, total_tokens_used=0, total_sources_found=0, average_agent_efficiency=0.0, success_rate=0.0),
                        start_time=datetime.now(timezone.utc),
                        last_update=datetime.now(timezone.utc)
                    )
                    await progress_callback(planning_progress)
                    callback_calls.append("planning")
                    
                    # Executing stage
                    executing_progress = ResearchProgress(
                        research_id=research_id,
                        current_stage=ResearchStage.EXECUTING,
                        overall_progress_percentage=60,
                        stage_progress=[],
                        agent_activities=[],
                        performance_metrics=PerformanceMetrics(total_execution_time=1.0, total_tokens_used=0, total_sources_found=0, average_agent_efficiency=0.0, success_rate=0.0),
                        start_time=datetime.now(timezone.utc),
                        last_update=datetime.now(timezone.utc)
                    )
                    await progress_callback(executing_progress)
                    callback_calls.append("executing")
                
                # Return mock result
                from app.models.schemas import ResearchResult
                return ResearchResult(
                    research_id=research_id,
                    query=query.query,
                    report="Mock research report",
                    citations=[],
                    sources_used=[],
                    total_tokens_used=100,
                    execution_time=1.0,
                    subagent_count=1,
                    report_sections=[]
                )
            
            mock_agent.conduct_research = mock_conduct_research
            return mock_agent
        
        with patch('app.services.research_service.LeadResearchAgent', side_effect=mock_lead_agent_init):
            # Start research
            research_id = await research_service.start_research(sample_query)
            
            # Wait for research to complete
            await asyncio.sleep(0.2)
            
            # Verify callbacks were triggered
            assert "planning" in callback_calls
            assert "executing" in callback_calls
            
            # Verify progress was stored for both stages
            final_progress = await research_service.get_progress(research_id)
            assert final_progress is not None
            assert final_progress.current_stage == ResearchStage.EXECUTING
    
    @pytest.mark.asyncio
    async def test_error_handling_during_progress_updates(self, research_service, sample_progress):
        """Test 3.1.5: Error handling during progress updates"""
        
        research_id = sample_progress.research_id
        
        # Test storing progress with invalid data
        invalid_progress = ResearchProgress(
            research_id=research_id,
            current_stage=ResearchStage.PLANNING,
            overall_progress_percentage=25,
            stage_progress=[],
            agent_activities=[],
            performance_metrics=PerformanceMetrics(total_execution_time=1.0, total_tokens_used=0, total_sources_found=0, average_agent_efficiency=0.0, success_rate=0.0),
            start_time=datetime.now(timezone.utc),
            last_update=datetime.now(timezone.utc)
        )
        
        # This should not raise an exception
        await research_service.store_progress(research_id, invalid_progress)
        
        # Verify progress was still stored
        retrieved = await research_service.get_progress(research_id)
        assert retrieved is not None
        
        # Test retrieving non-existent progress
        non_existent_id = uuid4()
        non_existent_progress = await research_service.get_progress(non_existent_id)
        assert non_existent_progress is None
        
        # Test detailed status for non-existent research
        non_existent_status = await research_service.get_detailed_status(non_existent_id)
        assert non_existent_status is None
    
    @pytest.mark.asyncio
    async def test_memory_cleanup_after_research_completion(self, research_service, sample_query):
        """Test 3.1.6: Memory cleanup after research completion"""
        
        # Mock LeadResearchAgent
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            
            # Mock successful research completion
            from app.models.schemas import ResearchResult
            mock_result = ResearchResult(
                research_id=uuid4(),
                query=sample_query.query,
                report="Mock research report",
                citations=[],
                sources_used=[],
                total_tokens_used=100,
                execution_time=1.0,
                subagent_count=1,
                report_sections=[]
            )
            mock_agent.conduct_research = AsyncMock(return_value=mock_result)
            mock_agent_class.return_value = mock_agent
            
            # Start multiple research sessions
            research_ids = []
            for i in range(5):
                research_id = await research_service.start_research(sample_query)
                research_ids.append(research_id)
                
                # Add some progress data
                progress = ResearchProgress(
                    research_id=research_id,
                    current_stage=ResearchStage.PLANNING,
                    overall_progress_percentage=25,
                    stage_progress=[],
                    agent_activities=[],
                    performance_metrics=PerformanceMetrics(total_execution_time=1.0, total_tokens_used=0, total_sources_found=0, average_agent_efficiency=0.0, success_rate=0.0),
                    start_time=datetime.now(timezone.utc),
                    last_update=datetime.now(timezone.utc)
                )
                await research_service.store_progress(research_id, progress)
            
            # Wait for research to complete
            await asyncio.sleep(0.2)
            
            # Verify progress store has data
            assert research_service.get_progress_store_size() == 5
            
            # Test cleanup with max_completed = 2
            await research_service.cleanup_completed_research(max_completed=2)
            
            # Verify cleanup worked
            assert research_service.get_completed_research_count() <= 2
            assert research_service.get_progress_store_size() <= 2
    
    @pytest.mark.asyncio
    async def test_detailed_status_integration(self, research_service, sample_query, sample_progress):
        """Test detailed status integration with progress data"""
        
        # Create a research task
        research_id = await research_service.start_research(sample_query)
        
        # Store progress
        sample_progress.research_id = research_id
        await research_service.store_progress(research_id, sample_progress)
        
        # Get detailed status
        detailed_status = await research_service.get_detailed_status(research_id)
        
        # Verify detailed status
        assert detailed_status is not None
        assert detailed_status.research_id == research_id
        assert detailed_status.query == sample_query.query
        assert detailed_status.status == sample_progress.current_stage
        assert detailed_status.progress.research_id == research_id
        assert detailed_status.progress.overall_progress_percentage == sample_progress.overall_progress_percentage
        
        # Test properties
        assert detailed_status.is_active == True
        assert detailed_status.is_completed == False
        assert detailed_status.is_failed == False
        assert detailed_status.elapsed_time > 0
    
    @pytest.mark.asyncio
    async def test_enhanced_get_research_status(self, research_service, sample_query, sample_progress):
        """Test enhanced get_research_status method with progress data"""
        
        # Create a research task
        research_id = await research_service.start_research(sample_query)
        
        # Store progress with detailed information
        sample_progress.research_id = research_id
        await research_service.store_progress(research_id, sample_progress)
        
        # Get research status
        status = await research_service.get_research_status(research_id)
        
        # Verify enhanced status information
        assert status is not None
        assert status["research_id"] == str(research_id)
        assert status["status"] == (sample_progress.current_stage.value if hasattr(sample_progress.current_stage, 'value') else sample_progress.current_stage)
        assert status["progress_percentage"] == sample_progress.overall_progress_percentage
        assert "current_stage" in status
        assert "stage_progress" in status
        assert "agent_activities" in status
        assert "performance_metrics" in status
        
        # Verify stage progress details
        assert len(status["stage_progress"]) == len(sample_progress.stage_progress)
        if status["stage_progress"]:
            stage_progress = status["stage_progress"][0]
            assert "stage" in stage_progress
            assert "progress_percentage" in stage_progress
            assert "message" in stage_progress
            assert "start_time" in stage_progress
        
        # Verify agent activities details
        assert len(status["agent_activities"]) == len(sample_progress.agent_activities)
        if status["agent_activities"]:
            agent_activity = status["agent_activities"][0]
            assert "agent_id" in agent_activity
            assert "agent_name" in agent_activity
            assert "status" in agent_activity
            assert "current_task" in agent_activity
            assert "sources_found" in agent_activity
            assert "tokens_used" in agent_activity
        
        # Verify performance metrics
        if status["performance_metrics"]:
            metrics = status["performance_metrics"]
            assert "total_sources_found" in metrics
            assert "total_tokens_used" in metrics
            assert "total_execution_time" in metrics
            assert "average_agent_efficiency" in metrics
            assert "success_rate" in metrics


if __name__ == "__main__":
    pytest.main([__file__])