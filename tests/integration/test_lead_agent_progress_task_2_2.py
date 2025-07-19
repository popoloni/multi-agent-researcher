"""
Unit tests for LeadResearchAgent Progress Integration Task 2.2
Tests progress callback mechanism, stage transitions, individual subagent activities,
and progress callback integration with ResearchService.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from app.agents.lead_agent import LeadResearchAgent
from app.models.schemas import (
    ResearchQuery, ResearchStage, AgentStatus, ResearchProgress,
    PerformanceMetrics, SubAgentTask, SubAgentResult, SearchResult
)


class TestLeadAgentProgressTask22:
    """Test suite for Task 2.2: LeadResearchAgent Progress Integration"""
    
    @pytest.fixture
    def sample_query(self):
        """Create a sample research query"""
        return ResearchQuery(
            query="What are the latest developments in quantum computing?",
            max_subagents=2,
            max_iterations=2
        )
    
    @pytest.fixture
    def progress_callback(self):
        """Create a mock progress callback"""
        return AsyncMock()
    
    @pytest.fixture
    def lead_agent_with_callback(self, progress_callback):
        """Create LeadResearchAgent with progress callback"""
        return LeadResearchAgent(progress_callback=progress_callback)
    
    @pytest.fixture
    def sample_subagent_result(self):
        """Create a sample subagent result"""
        return SubAgentResult(
            task_id=uuid4(),
            findings=[
                {"title": "Quantum Computing Breakthrough", "content": "Recent advances..."},
                {"title": "IBM Quantum Update", "content": "IBM announced..."}
            ],
            sources=[
                SearchResult(
                    url="https://example.com/quantum1",
                    title="Quantum Computing News",
                    snippet="Latest quantum developments",
                    relevance_score=0.9
                ),
                SearchResult(
                    url="https://example.com/quantum2",
                    title="IBM Quantum Research",
                    snippet="IBM quantum computer advances",
                    relevance_score=0.8
                )
            ],
            summary="Recent quantum computing developments show significant progress",
            token_count=250
        )
    
    def test_lead_agent_progress_reporting(self, lead_agent_with_callback, progress_callback):
        """Test that LeadResearchAgent reports progress at each stage"""
        
        async def test_progress_reporting():
            research_id = uuid4()
            query = "Test query"
            
            # Initialize progress tracking
            lead_agent_with_callback._initialize_progress_tracking(research_id, query)
            
            # Verify initial progress setup
            assert lead_agent_with_callback.current_research_progress is not None
            assert lead_agent_with_callback.current_research_progress.research_id == research_id
            assert lead_agent_with_callback.current_research_progress.current_stage == ResearchStage.STARTED
            assert lead_agent_with_callback.performance_metrics is not None
            
            # Test stage progress updates
            await lead_agent_with_callback._update_stage_progress(
                ResearchStage.PLANNING, 50, "Planning in progress"
            )
            
            # Verify progress callback was called
            assert progress_callback.call_count >= 1
            
            # Verify stage progress was updated
            current_progress = lead_agent_with_callback.current_research_progress
            assert current_progress.current_stage == ResearchStage.PLANNING
            
            # Find planning stage progress
            planning_progress = None
            for stage_progress in current_progress.stage_progress:
                if stage_progress.stage == ResearchStage.PLANNING:
                    planning_progress = stage_progress
                    break
            
            assert planning_progress is not None
            assert planning_progress.progress_percentage == 50
            assert planning_progress.message == "Planning in progress"
            
            # Test stage completion
            await lead_agent_with_callback._update_stage_progress(
                ResearchStage.PLANNING, 100, "Planning completed"
            )
            
            # Verify stage completion was tracked
            planning_progress = current_progress.get_current_stage_progress()
            assert planning_progress.progress_percentage == 100
            assert planning_progress.end_time is not None
            assert planning_progress.duration_seconds is not None
        
        asyncio.run(test_progress_reporting())
    
    def test_stage_transitions_work_correctly(self, lead_agent_with_callback):
        """Test that stage transitions are properly tracked and reported"""
        
        async def test_stage_transitions():
            research_id = uuid4()
            query = "Test query"
            
            # Initialize progress tracking
            lead_agent_with_callback._initialize_progress_tracking(research_id, query)
            
            # Test all stage transitions
            stages_to_test = [
                (ResearchStage.PLANNING, "Planning phase"),
                (ResearchStage.EXECUTING, "Execution phase"),
                (ResearchStage.SYNTHESIZING, "Synthesis phase"),
                (ResearchStage.CITING, "Citation phase"),
                (ResearchStage.COMPLETED, "Completion phase")
            ]
            
            for stage, message in stages_to_test:
                await lead_agent_with_callback._update_stage_progress(
                    stage, 100, message
                )
                
                # Verify stage transition
                current_progress = lead_agent_with_callback.current_research_progress
                assert current_progress.current_stage == stage
                
                # Verify stage was added to progress list
                stage_found = False
                for stage_progress in current_progress.stage_progress:
                    if stage_progress.stage == stage:
                        stage_found = True
                        assert stage_progress.message == message
                        break
                
                assert stage_found, f"Stage {stage} not found in progress list"
            
            # Verify all stages are tracked
            assert len(lead_agent_with_callback.current_research_progress.stage_progress) >= 5
        
        asyncio.run(test_stage_transitions())
    
    def test_subagent_activity_tracking(self, lead_agent_with_callback):
        """Test that individual subagent activities are monitored"""
        
        async def test_agent_tracking():
            research_id = uuid4()
            query = "Test query"
            
            # Initialize progress tracking
            lead_agent_with_callback._initialize_progress_tracking(research_id, query)
            
            # Test agent activity updates
            agent_id = "test_agent_001"
            
            # Test agent initialization
            await lead_agent_with_callback._update_agent_activity(
                agent_id=agent_id,
                status=AgentStatus.INITIALIZING,
                current_task="Initializing search agent",
                progress=0
            )
            
            current_progress = lead_agent_with_callback.current_research_progress
            assert len(current_progress.agent_activities) == 1
            
            agent_activity = current_progress.agent_activities[0]
            assert agent_activity.agent_id == agent_id
            assert agent_activity.status == AgentStatus.INITIALIZING
            assert agent_activity.current_task == "Initializing search agent"
            assert agent_activity.progress_percentage == 0
            
            # Test agent progress update
            await lead_agent_with_callback._update_agent_activity(
                agent_id=agent_id,
                status=AgentStatus.SEARCHING,
                current_task="Searching for quantum computing papers",
                progress=50,
                sources_found=3,
                tokens_used=150
            )
            
            # Verify agent was updated (not duplicated)
            assert len(current_progress.agent_activities) == 1
            updated_agent = current_progress.agent_activities[0]
            assert updated_agent.status == AgentStatus.SEARCHING
            assert updated_agent.progress_percentage == 50
            assert updated_agent.sources_found == 3
            assert updated_agent.tokens_used == 150
            
            # Test agent completion
            await lead_agent_with_callback._update_agent_activity(
                agent_id=agent_id,
                status=AgentStatus.COMPLETED,
                current_task="Task completed successfully",
                progress=100,
                sources_found=8,
                tokens_used=300
            )
            
            completed_agent = current_progress.agent_activities[0]
            assert completed_agent.status == AgentStatus.COMPLETED
            assert completed_agent.progress_percentage == 100
            assert completed_agent.sources_found == 8
            assert completed_agent.tokens_used == 300
            
            # Test multiple agents
            await lead_agent_with_callback._update_agent_activity(
                agent_id="test_agent_002",
                status=AgentStatus.ANALYZING,
                current_task="Analyzing search results",
                progress=75,
                sources_found=5,
                tokens_used=200
            )
            
            assert len(current_progress.agent_activities) == 2
            
            # Test getting active agents
            active_agents = current_progress.get_active_agents()
            assert len(active_agents) == 1  # Only agent_002 is active
            assert active_agents[0].agent_id == "test_agent_002"
        
        asyncio.run(test_agent_tracking())
    
    def test_progress_callback_integration(self, lead_agent_with_callback, progress_callback):
        """Test that progress callbacks work with ResearchService integration"""
        
        async def test_callback_integration():
            research_id = uuid4()
            query = "Test query"
            
            # Initialize progress tracking
            lead_agent_with_callback._initialize_progress_tracking(research_id, query)
            
            # Reset callback call count
            progress_callback.reset_mock()
            
            # Test stage progress callback
            await lead_agent_with_callback._update_stage_progress(
                ResearchStage.PLANNING, 25, "Planning started"
            )
            
            # Verify callback was called with correct progress
            assert progress_callback.call_count == 1
            called_progress = progress_callback.call_args[0][0]
            assert isinstance(called_progress, ResearchProgress)
            assert called_progress.current_stage == ResearchStage.PLANNING
            
            # Test agent activity callback
            await lead_agent_with_callback._update_agent_activity(
                agent_id="test_agent",
                status=AgentStatus.SEARCHING,
                current_task="Searching",
                progress=30
            )
            
            # Verify callback was called again
            assert progress_callback.call_count == 2
            
            # Test multiple rapid updates
            for i in range(5):
                await lead_agent_with_callback._update_stage_progress(
                    ResearchStage.EXECUTING, 20 + i * 10, f"Execution step {i+1}"
                )
            
            # Verify all callbacks were made
            assert progress_callback.call_count >= 7  # 2 previous + 5 new
            
            # Verify final callback has correct data
            final_progress = progress_callback.call_args[0][0]
            assert final_progress.current_stage == ResearchStage.EXECUTING
            assert len(final_progress.agent_activities) == 1
        
        asyncio.run(test_callback_integration())
    
    def test_performance_metrics_tracking(self, lead_agent_with_callback):
        """Test that performance metrics are properly tracked"""
        
        async def test_metrics_tracking():
            research_id = uuid4()
            query = "Test query"
            
            # Initialize progress tracking
            lead_agent_with_callback._initialize_progress_tracking(research_id, query)
            
            # Verify initial metrics
            metrics = lead_agent_with_callback.performance_metrics
            assert metrics is not None
            assert metrics.total_execution_time == 0.0
            assert metrics.total_tokens_used == 0
            assert metrics.total_sources_found == 0
            
            # Add agent activities and verify metrics update
            await lead_agent_with_callback._update_agent_activity(
                agent_id="agent_1",
                status=AgentStatus.COMPLETED,
                current_task="Task 1",
                progress=100,
                sources_found=5,
                tokens_used=200
            )
            
            await lead_agent_with_callback._update_agent_activity(
                agent_id="agent_2",
                status=AgentStatus.COMPLETED,
                current_task="Task 2",
                progress=100,
                sources_found=3,
                tokens_used=150
            )
            
            # Verify metrics were updated
            updated_metrics = lead_agent_with_callback.performance_metrics
            assert updated_metrics.total_sources_found == 8  # 5 + 3
            assert updated_metrics.total_tokens_used >= 350  # 200 + 150 + lead agent tokens
            
            # Test stage timing - start planning first
            await lead_agent_with_callback._update_stage_progress(
                ResearchStage.PLANNING, 50, "Planning started"
            )
            
            # Add a small delay to ensure timing
            await asyncio.sleep(0.01)
            
            # Complete planning
            await lead_agent_with_callback._update_stage_progress(
                ResearchStage.PLANNING, 100, "Planning completed"
            )
            
            # Verify stage timing was recorded
            assert updated_metrics.planning_time > 0
            
            # Test finalization
            lead_agent_with_callback._finalize_progress_tracking(success=True)
            
            # Verify final metrics
            final_metrics = lead_agent_with_callback.performance_metrics
            assert final_metrics.total_execution_time > 0
            assert final_metrics.success_rate == 100.0
        
        asyncio.run(test_metrics_tracking())
    
    @pytest.mark.asyncio
    async def test_enhanced_research_plan_creation(self, lead_agent_with_callback, sample_query):
        """Test enhanced research plan creation with progress tracking"""
        
        # Mock the LLM call to return a valid plan
        with patch.object(lead_agent_with_callback, '_call_llm') as mock_llm:
            mock_llm.return_value = '''
            {
                "strategy": "Multi-faceted quantum computing research",
                "complexity": "moderate",
                "subtasks": [
                    {
                        "objective": "Find recent quantum computing breakthroughs",
                        "search_focus": "quantum computing 2024 2025 breakthroughs",
                        "expected_output": "List of recent developments"
                    },
                    {
                        "objective": "Research quantum computing applications",
                        "search_focus": "quantum computing applications industry",
                        "expected_output": "Application examples and use cases"
                    }
                ]
            }
            '''
            
            # Mock the think method
            with patch.object(lead_agent_with_callback, 'think') as mock_think:
                mock_think.return_value = "Analysis complete"
                
                # Initialize progress tracking
                research_id = uuid4()
                lead_agent_with_callback._initialize_progress_tracking(research_id, sample_query.query)
                
                # Test enhanced plan creation
                plan = await lead_agent_with_callback._create_research_plan_with_progress(sample_query)
                
                # Verify plan was created
                assert plan is not None
                assert plan.strategy == "Multi-faceted quantum computing research"
                assert plan.estimated_complexity == "moderate"
                assert len(plan.subtasks) == 2
                
                # Verify progress was tracked
                current_progress = lead_agent_with_callback.current_research_progress
                planning_stages = [sp for sp in current_progress.stage_progress if sp.stage == ResearchStage.PLANNING]
                assert len(planning_stages) > 0
                
                # Verify multiple progress updates were made during planning
                planning_progress = planning_stages[-1]  # Get the latest planning progress
                assert planning_progress.progress_percentage > 0
    
    @pytest.mark.asyncio
    async def test_subagent_execution_with_tracking(self, lead_agent_with_callback, sample_subagent_result):
        """Test subagent execution with progress tracking"""
        
        # Create a mock subagent
        mock_subagent = AsyncMock()
        mock_subagent.execute_task.return_value = sample_subagent_result
        
        # Create a sample task
        task = SubAgentTask(
            objective="Test objective",
            search_focus="test focus",
            expected_output_format="test format"
        )
        
        # Initialize progress tracking
        research_id = uuid4()
        lead_agent_with_callback._initialize_progress_tracking(research_id, "test query")
        
        # Execute subagent with tracking
        result = await lead_agent_with_callback._execute_subagent_with_tracking(
            mock_subagent, task, "test_agent_001"
        )
        
        # Verify result
        assert result == sample_subagent_result
        
        # Verify agent activity was tracked
        current_progress = lead_agent_with_callback.current_research_progress
        assert len(current_progress.agent_activities) == 1
        
        agent_activity = current_progress.agent_activities[0]
        assert agent_activity.agent_id == "test_agent_001"
        assert agent_activity.status == AgentStatus.COMPLETED
        assert agent_activity.progress_percentage == 100
        assert agent_activity.sources_found == len(sample_subagent_result.sources)
        assert agent_activity.tokens_used == sample_subagent_result.token_count
    
    @pytest.mark.asyncio
    async def test_subagent_execution_failure_tracking(self, lead_agent_with_callback):
        """Test subagent execution failure tracking"""
        
        # Create a mock subagent that fails
        mock_subagent = AsyncMock()
        mock_subagent.execute_task.side_effect = Exception("Test error")
        
        # Create a sample task
        task = SubAgentTask(
            objective="Test objective",
            search_focus="test focus",
            expected_output_format="test format"
        )
        
        # Initialize progress tracking
        research_id = uuid4()
        lead_agent_with_callback._initialize_progress_tracking(research_id, "test query")
        
        # Execute subagent with tracking (should fail)
        with pytest.raises(Exception, match="Test error"):
            await lead_agent_with_callback._execute_subagent_with_tracking(
                mock_subagent, task, "test_agent_001"
            )
        
        # Verify failure was tracked
        current_progress = lead_agent_with_callback.current_research_progress
        assert len(current_progress.agent_activities) == 1
        
        agent_activity = current_progress.agent_activities[0]
        assert agent_activity.agent_id == "test_agent_001"
        assert agent_activity.status == AgentStatus.FAILED
        assert agent_activity.progress_percentage == 0
        assert agent_activity.error_message == "Test error"
    
    def test_progress_finalization(self, lead_agent_with_callback):
        """Test progress tracking finalization"""
        
        research_id = uuid4()
        query = "Test query"
        
        # Initialize progress tracking
        lead_agent_with_callback._initialize_progress_tracking(research_id, query)
        
        # Add some agent activities
        asyncio.run(lead_agent_with_callback._update_agent_activity(
            agent_id="agent_1",
            status=AgentStatus.SEARCHING,
            current_task="Searching",
            progress=50
        ))
        
        # Test successful finalization
        lead_agent_with_callback._finalize_progress_tracking(success=True)
        
        # Verify finalization
        metrics = lead_agent_with_callback.performance_metrics
        progress = lead_agent_with_callback.current_research_progress
        
        assert metrics.total_execution_time > 0
        assert metrics.success_rate == 100.0
        assert progress.current_stage == ResearchStage.COMPLETED
        
        # Verify all agents were marked as completed
        for agent in progress.agent_activities:
            assert agent.status == AgentStatus.COMPLETED
            assert agent.progress_percentage == 100
        
        # Test failed finalization
        lead_agent_with_callback._finalize_progress_tracking(success=False)
        
        assert metrics.success_rate == 0.0
        assert progress.current_stage == ResearchStage.FAILED


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])