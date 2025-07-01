"""
Unit tests for Progress Data Models Task 2.1
Tests comprehensive progress tracking data structures, agent activity monitoring, 
progress percentage calculation, and performance metrics.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.schemas import (
    ResearchStage, AgentStatus, AgentActivity, StageProgress, 
    PerformanceMetrics, ResearchProgress, DetailedResearchStatus
)


class TestProgressDataModelsTask21:
    """Test suite for Task 2.1: Progress Data Models"""
    
    @pytest.fixture
    def sample_research_id(self):
        """Create a sample research ID"""
        return uuid4()
    
    @pytest.fixture
    def sample_performance_metrics(self):
        """Create sample performance metrics"""
        return PerformanceMetrics(
            total_execution_time=120.5,
            planning_time=15.2,
            execution_time=80.3,
            synthesis_time=20.0,
            citation_time=5.0,
            total_tokens_used=2500,
            total_sources_found=15,
            average_agent_efficiency=85.5,
            success_rate=95.0
        )
    
    @pytest.fixture
    def sample_research_progress(self, sample_research_id, sample_performance_metrics):
        """Create sample research progress"""
        now = datetime.now(timezone.utc)
        return ResearchProgress(
            research_id=sample_research_id,
            current_stage=ResearchStage.EXECUTING,
            overall_progress_percentage=45,
            performance_metrics=sample_performance_metrics,
            start_time=now - timedelta(minutes=2),
            last_update=now
        )
    
    def test_research_status_model_completeness(self):
        """Test that ResearchStage enum contains all required fields"""
        
        # Verify all required stages are present
        required_stages = [
            "started", "planning", "executing", 
            "synthesizing", "citing", "completed", "failed"
        ]
        
        for stage in required_stages:
            assert hasattr(ResearchStage, stage.upper())
            assert ResearchStage[stage.upper()].value == stage
        
        # Verify enum values
        assert ResearchStage.STARTED == "started"
        assert ResearchStage.PLANNING == "planning"
        assert ResearchStage.EXECUTING == "executing"
        assert ResearchStage.SYNTHESIZING == "synthesizing"
        assert ResearchStage.CITING == "citing"
        assert ResearchStage.COMPLETED == "completed"
        assert ResearchStage.FAILED == "failed"
    
    def test_agent_activity_tracking_structure(self):
        """Test that AgentActivity model has all required fields for tracking"""
        
        now = datetime.now(timezone.utc)
        agent_activity = AgentActivity(
            agent_id="agent_001",
            agent_name="Search Agent Alpha",
            status=AgentStatus.SEARCHING,
            current_task="Finding recent AI research papers",
            progress_percentage=75,
            start_time=now - timedelta(minutes=1),
            last_update=now,
            sources_found=8,
            tokens_used=450,
            error_message=None
        )
        
        # Verify all required fields are present and correct
        assert agent_activity.agent_id == "agent_001"
        assert agent_activity.agent_name == "Search Agent Alpha"
        assert agent_activity.status == AgentStatus.SEARCHING
        assert agent_activity.current_task == "Finding recent AI research papers"
        assert agent_activity.progress_percentage == 75
        assert isinstance(agent_activity.start_time, datetime)
        assert isinstance(agent_activity.last_update, datetime)
        assert agent_activity.sources_found == 8
        assert agent_activity.tokens_used == 450
        assert agent_activity.error_message is None
        
        # Test with error message
        failed_agent = AgentActivity(
            agent_id="agent_002",
            agent_name="Search Agent Beta",
            status=AgentStatus.FAILED,
            current_task="Analyzing search results",
            progress_percentage=30,
            start_time=now,
            last_update=now,
            error_message="Connection timeout"
        )
        
        assert failed_agent.status == AgentStatus.FAILED
        assert failed_agent.error_message == "Connection timeout"
    
    def test_progress_percentage_calculation(self, sample_research_progress):
        """Test progress percentage calculation logic"""
        
        # Test initial progress calculation
        initial_progress = sample_research_progress.calculate_overall_progress()
        assert isinstance(initial_progress, int)
        assert 0 <= initial_progress <= 100
        
        # Add stage progress and test calculation
        sample_research_progress.add_stage_progress(
            ResearchStage.PLANNING, 100, "Planning completed"
        )
        sample_research_progress.add_stage_progress(
            ResearchStage.EXECUTING, 50, "Execution in progress"
        )
        
        progress_after_stages = sample_research_progress.calculate_overall_progress()
        assert progress_after_stages > initial_progress
        assert isinstance(progress_after_stages, int)
        
        # Test completed research
        sample_research_progress.current_stage = ResearchStage.COMPLETED
        completed_progress = sample_research_progress.calculate_overall_progress()
        assert completed_progress == 100
        
        # Test failed research
        sample_research_progress.current_stage = ResearchStage.FAILED
        failed_progress = sample_research_progress.calculate_overall_progress()
        assert failed_progress == 0
    
    def test_performance_metrics_structure(self, sample_performance_metrics):
        """Test performance metrics data structure and calculations"""
        
        # Verify all required fields
        assert sample_performance_metrics.total_execution_time == 120.5
        assert sample_performance_metrics.planning_time == 15.2
        assert sample_performance_metrics.execution_time == 80.3
        assert sample_performance_metrics.synthesis_time == 20.0
        assert sample_performance_metrics.citation_time == 5.0
        assert sample_performance_metrics.total_tokens_used == 2500
        assert sample_performance_metrics.total_sources_found == 15
        assert sample_performance_metrics.average_agent_efficiency == 85.5
        assert sample_performance_metrics.success_rate == 95.0
        
        # Test stage efficiency calculation
        efficiency = sample_performance_metrics.calculate_stage_efficiency()
        assert isinstance(efficiency, dict)
        assert "planning_efficiency" in efficiency
        assert "execution_efficiency" in efficiency
        assert "synthesis_efficiency" in efficiency
        assert "citation_efficiency" in efficiency
        
        # Verify efficiency percentages add up correctly
        total_efficiency = sum(efficiency.values())
        assert abs(total_efficiency - 100.0) < 0.1  # Allow for floating point precision
        
        # Test tokens per second calculation
        tokens_per_second = sample_performance_metrics.calculate_tokens_per_second()
        expected_rate = 2500 / 120.5
        assert abs(tokens_per_second - expected_rate) < 0.1
    
    def test_stage_progress_tracking(self):
        """Test stage progress tracking functionality"""
        
        now = datetime.now(timezone.utc)
        stage_progress = StageProgress(
            stage=ResearchStage.PLANNING,
            progress_percentage=100,
            start_time=now - timedelta(minutes=1),
            end_time=now,
            duration_seconds=60.0,
            message="Planning phase completed successfully",
            details={"subtasks_created": 3, "complexity": "moderate"}
        )
        
        # Verify all fields
        assert stage_progress.stage == ResearchStage.PLANNING
        assert stage_progress.progress_percentage == 100
        assert isinstance(stage_progress.start_time, datetime)
        assert isinstance(stage_progress.end_time, datetime)
        assert stage_progress.duration_seconds == 60.0
        assert stage_progress.message == "Planning phase completed successfully"
        assert stage_progress.details["subtasks_created"] == 3
        assert stage_progress.details["complexity"] == "moderate"
    
    def test_research_progress_agent_management(self, sample_research_progress):
        """Test agent activity management in ResearchProgress"""
        
        # Test adding agent activity
        sample_research_progress.update_agent_activity(
            agent_id="agent_001",
            status=AgentStatus.SEARCHING,
            current_task="Searching for AI papers",
            progress=50,
            sources_found=5,
            tokens_used=200
        )
        
        assert len(sample_research_progress.agent_activities) == 1
        agent = sample_research_progress.agent_activities[0]
        assert agent.agent_id == "agent_001"
        assert agent.status == AgentStatus.SEARCHING
        assert agent.progress_percentage == 50
        assert agent.sources_found == 5
        assert agent.tokens_used == 200
        
        # Test updating existing agent
        sample_research_progress.update_agent_activity(
            agent_id="agent_001",
            status=AgentStatus.ANALYZING,
            current_task="Analyzing search results",
            progress=75,
            sources_found=8,
            tokens_used=350
        )
        
        assert len(sample_research_progress.agent_activities) == 1  # Still one agent
        updated_agent = sample_research_progress.agent_activities[0]
        assert updated_agent.status == AgentStatus.ANALYZING
        assert updated_agent.progress_percentage == 75
        assert updated_agent.sources_found == 8
        assert updated_agent.tokens_used == 350
        
        # Test adding second agent
        sample_research_progress.update_agent_activity(
            agent_id="agent_002",
            status=AgentStatus.PROCESSING,
            current_task="Processing data",
            progress=25
        )
        
        assert len(sample_research_progress.agent_activities) == 2
        
        # Test getting active agents
        active_agents = sample_research_progress.get_active_agents()
        assert len(active_agents) == 2  # Both agents are active
        
        # Mark one agent as completed
        sample_research_progress.update_agent_activity(
            agent_id="agent_001",
            status=AgentStatus.COMPLETED,
            current_task="Task completed",
            progress=100
        )
        
        active_agents_after = sample_research_progress.get_active_agents()
        assert len(active_agents_after) == 1  # Only one active agent
        assert active_agents_after[0].agent_id == "agent_002"
    
    def test_research_progress_stage_management(self, sample_research_progress):
        """Test stage progress management in ResearchProgress"""
        
        # Test adding stage progress
        sample_research_progress.add_stage_progress(
            ResearchStage.PLANNING,
            50,
            "Creating research plan",
            {"subtasks": 2}
        )
        
        assert len(sample_research_progress.stage_progress) == 1
        assert sample_research_progress.current_stage == ResearchStage.PLANNING
        
        # Test getting current stage progress
        current_stage = sample_research_progress.get_current_stage_progress()
        assert current_stage is not None
        assert current_stage.stage == ResearchStage.PLANNING
        assert current_stage.progress_percentage == 50
        assert current_stage.details["subtasks"] == 2
        
        # Test completing a stage
        sample_research_progress.add_stage_progress(
            ResearchStage.PLANNING,
            100,
            "Planning completed",
            {"subtasks": 3}
        )
        
        completed_stage = sample_research_progress.get_current_stage_progress()
        assert completed_stage.progress_percentage == 100
        assert completed_stage.end_time is not None
        assert completed_stage.duration_seconds is not None
        assert completed_stage.duration_seconds > 0
        
        # Test moving to next stage
        sample_research_progress.add_stage_progress(
            ResearchStage.EXECUTING,
            25,
            "Starting execution",
            {"agents_started": 2}
        )
        
        assert len(sample_research_progress.stage_progress) == 2
        assert sample_research_progress.current_stage == ResearchStage.EXECUTING
    
    def test_detailed_research_status_properties(self, sample_research_id, sample_research_progress):
        """Test DetailedResearchStatus properties and functionality"""
        
        now = datetime.now(timezone.utc)
        
        # Test active research status
        active_status = DetailedResearchStatus(
            research_id=sample_research_id,
            query="Test research query",
            status=ResearchStage.EXECUTING,
            progress=sample_research_progress,
            created_at=now - timedelta(minutes=5)
        )
        
        assert active_status.is_active is True
        assert active_status.is_completed is False
        assert active_status.is_failed is False
        assert active_status.elapsed_time > 0
        
        # Test completed research status
        completed_status = DetailedResearchStatus(
            research_id=sample_research_id,
            query="Test research query",
            status=ResearchStage.COMPLETED,
            progress=sample_research_progress,
            created_at=now - timedelta(minutes=10)
        )
        
        assert completed_status.is_active is False
        assert completed_status.is_completed is True
        assert completed_status.is_failed is False
        
        # Test failed research status
        failed_status = DetailedResearchStatus(
            research_id=sample_research_id,
            query="Test research query",
            status=ResearchStage.FAILED,
            progress=sample_research_progress,
            created_at=now - timedelta(minutes=3),
            error_message="Test error"
        )
        
        assert failed_status.is_active is False
        assert failed_status.is_completed is False
        assert failed_status.is_failed is True
        assert failed_status.error_message == "Test error"
    
    def test_agent_status_enum_completeness(self):
        """Test that AgentStatus enum contains all required values"""
        
        required_statuses = [
            "idle", "initializing", "searching", "analyzing", 
            "processing", "completed", "failed"
        ]
        
        for status in required_statuses:
            assert hasattr(AgentStatus, status.upper())
            assert AgentStatus[status.upper()].value == status
        
        # Verify specific values
        assert AgentStatus.IDLE == "idle"
        assert AgentStatus.INITIALIZING == "initializing"
        assert AgentStatus.SEARCHING == "searching"
        assert AgentStatus.ANALYZING == "analyzing"
        assert AgentStatus.PROCESSING == "processing"
        assert AgentStatus.COMPLETED == "completed"
        assert AgentStatus.FAILED == "failed"
    
    def test_progress_calculation_edge_cases(self, sample_research_progress):
        """Test edge cases in progress calculation"""
        
        # Test with no stages
        empty_progress = sample_research_progress.calculate_overall_progress()
        assert isinstance(empty_progress, int)
        assert empty_progress >= 0
        
        # Test with all stages completed
        for stage in [ResearchStage.PLANNING, ResearchStage.EXECUTING, 
                     ResearchStage.SYNTHESIZING, ResearchStage.CITING]:
            sample_research_progress.add_stage_progress(stage, 100, f"{stage} completed")
        
        sample_research_progress.current_stage = ResearchStage.COMPLETED
        full_progress = sample_research_progress.calculate_overall_progress()
        assert full_progress == 100
        
        # Test with partial completion
        partial_progress = ResearchProgress(
            research_id=uuid4(),
            current_stage=ResearchStage.EXECUTING,
            overall_progress_percentage=0,
            performance_metrics=PerformanceMetrics(total_execution_time=60.0),
            start_time=datetime.now(timezone.utc),
            last_update=datetime.now(timezone.utc)
        )
        
        partial_progress.add_stage_progress(ResearchStage.PLANNING, 100, "Planning done")
        partial_progress.add_stage_progress(ResearchStage.EXECUTING, 50, "Half done")
        
        partial_result = partial_progress.calculate_overall_progress()
        assert 15 < partial_result < 50  # Should be between planning (15%) and half of execution
    
    def test_performance_metrics_edge_cases(self):
        """Test edge cases in performance metrics calculations"""
        
        # Test with zero execution time
        zero_time_metrics = PerformanceMetrics(
            total_execution_time=0.0,
            total_tokens_used=100
        )
        
        efficiency = zero_time_metrics.calculate_stage_efficiency()
        assert efficiency == {}
        
        tokens_per_second = zero_time_metrics.calculate_tokens_per_second()
        assert tokens_per_second == 0.0
        
        # Test with very small execution time
        small_time_metrics = PerformanceMetrics(
            total_execution_time=0.1,
            planning_time=0.05,
            execution_time=0.03,
            synthesis_time=0.02,
            total_tokens_used=10
        )
        
        efficiency = small_time_metrics.calculate_stage_efficiency()
        assert isinstance(efficiency, dict)
        assert len(efficiency) == 4
        
        tokens_per_second = small_time_metrics.calculate_tokens_per_second()
        assert tokens_per_second == 100.0  # 10 tokens / 0.1 seconds


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])