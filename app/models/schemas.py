from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum

class ResearchQuery(BaseModel):
    """User's research query"""
    query: str
    max_subagents: int = Field(default=3, ge=1, le=10)
    max_iterations: int = Field(default=5, ge=1, le=20)
    
    
class SubAgentTask(BaseModel):
    """Task definition for a subagent"""
    task_id: UUID = Field(default_factory=uuid4)
    objective: str
    search_focus: str
    expected_output_format: str
    max_searches: int = Field(default=5)
    status: Literal["pending", "running", "completed", "failed"] = "pending"

class SearchResult(BaseModel):
    """Result from a search operation"""
    url: str
    title: str
    snippet: str
    content: Optional[str] = None
    relevance_score: float = Field(ge=0.0, le=1.0)

class SubAgentResult(BaseModel):
    """Result from a subagent's research"""
    task_id: UUID
    findings: List[Dict[str, Any]]
    sources: List[SearchResult]
    summary: str
    token_count: int

class ResearchPlan(BaseModel):
    """Research plan created by lead agent"""
    plan_id: UUID = Field(default_factory=uuid4)
    strategy: str
    subtasks: List[SubAgentTask]
    estimated_complexity: Literal["simple", "moderate", "complex"]

class CitationInfo(BaseModel):
    """Information about a citation"""
    index: int
    title: str
    url: str
    times_cited: int

class ResearchResult(BaseModel):
    """Final research result"""
    research_id: UUID
    query: str
    report: str
    citations: List[CitationInfo]
    sources_used: List[SearchResult]
    total_tokens_used: int
    execution_time: float
    subagent_count: int
    report_sections: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ===== PROGRESS TRACKING DATA MODELS (Task 2.1) =====

class ResearchStage(str, Enum):
    """Research execution stages for progress tracking"""
    STARTED = "started"
    PLANNING = "planning"
    EXECUTING = "executing"
    SYNTHESIZING = "synthesizing"
    CITING = "citing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(str, Enum):
    """Individual agent status for activity tracking"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentActivity(BaseModel):
    """Individual agent activity tracking"""
    agent_id: str
    agent_name: str
    status: AgentStatus
    current_task: str
    progress_percentage: int = Field(ge=0, le=100)
    start_time: datetime
    last_update: datetime
    sources_found: int = 0
    tokens_used: int = 0
    error_message: Optional[str] = None
    
    class Config:
        use_enum_values = True


class StageProgress(BaseModel):
    """Progress information for a specific research stage"""
    stage: ResearchStage
    progress_percentage: int = Field(ge=0, le=100)
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class PerformanceMetrics(BaseModel):
    """Performance metrics for research execution"""
    total_execution_time: float
    planning_time: float = 0.0
    execution_time: float = 0.0
    synthesis_time: float = 0.0
    citation_time: float = 0.0
    total_tokens_used: int = 0
    total_sources_found: int = 0
    average_agent_efficiency: float = 0.0
    success_rate: float = 0.0
    
    def calculate_stage_efficiency(self) -> Dict[str, float]:
        """Calculate efficiency metrics for each stage"""
        total_time = self.total_execution_time
        if total_time == 0:
            return {}
        
        return {
            "planning_efficiency": (self.planning_time / total_time) * 100,
            "execution_efficiency": (self.execution_time / total_time) * 100,
            "synthesis_efficiency": (self.synthesis_time / total_time) * 100,
            "citation_efficiency": (self.citation_time / total_time) * 100
        }
    
    def calculate_tokens_per_second(self) -> float:
        """Calculate token processing rate"""
        if self.total_execution_time == 0:
            return 0.0
        return self.total_tokens_used / self.total_execution_time


class ResearchProgress(BaseModel):
    """Comprehensive research progress tracking"""
    research_id: UUID
    current_stage: ResearchStage
    overall_progress_percentage: int = Field(ge=0, le=100)
    stage_progress: List[StageProgress] = Field(default_factory=list)
    agent_activities: List[AgentActivity] = Field(default_factory=list)
    performance_metrics: Optional[PerformanceMetrics] = None
    start_time: datetime
    estimated_completion_time: Optional[datetime] = None
    last_update: datetime
    error_message: Optional[str] = None
    
    class Config:
        use_enum_values = True
    
    def get_current_stage_progress(self) -> Optional[StageProgress]:
        """Get progress information for the current stage"""
        for stage in reversed(self.stage_progress):
            if stage.stage == self.current_stage:
                return stage
        return None
    
    def get_active_agents(self) -> List[AgentActivity]:
        """Get list of currently active agents"""
        return [
            agent for agent in self.agent_activities 
            if agent.status not in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.IDLE]
        ]
    
    def calculate_overall_progress(self) -> int:
        """Calculate overall progress percentage based on stages and agents"""
        stage_weights = {
            ResearchStage.STARTED: 5,
            ResearchStage.PLANNING: 15,
            ResearchStage.EXECUTING: 60,
            ResearchStage.SYNTHESIZING: 15,
            ResearchStage.CITING: 5,
            ResearchStage.COMPLETED: 0,
            ResearchStage.FAILED: 0
        }
        
        completed_weight = 0
        current_stage_weight = stage_weights.get(self.current_stage, 0)
        
        # Add weight for completed stages
        for stage_progress in self.stage_progress:
            if stage_progress.end_time is not None:  # Stage completed
                completed_weight += stage_weights.get(stage_progress.stage, 0)
        
        # Add partial weight for current stage
        if self.current_stage in [ResearchStage.COMPLETED, ResearchStage.FAILED]:
            return 100 if self.current_stage == ResearchStage.COMPLETED else 0
        
        current_stage_progress = self.get_current_stage_progress()
        if current_stage_progress:
            partial_weight = (current_stage_weight * current_stage_progress.progress_percentage) / 100
            completed_weight += partial_weight
        
        return min(int(completed_weight), 100)
    
    def update_agent_activity(self, agent_id: str, status: AgentStatus, 
                            current_task: str, progress: int = 0, 
                            sources_found: int = 0, tokens_used: int = 0,
                            error_message: Optional[str] = None):
        """Update activity for a specific agent"""
        now = datetime.now(timezone.utc)
        
        # Find existing agent or create new one
        agent_activity = None
        for activity in self.agent_activities:
            if activity.agent_id == agent_id:
                agent_activity = activity
                break
        
        if agent_activity is None:
            agent_activity = AgentActivity(
                agent_id=agent_id,
                agent_name=f"Agent {agent_id}",
                status=status,
                current_task=current_task,
                progress_percentage=progress,
                start_time=now,
                last_update=now,
                sources_found=sources_found,
                tokens_used=tokens_used,
                error_message=error_message
            )
            self.agent_activities.append(agent_activity)
        else:
            agent_activity.status = status
            agent_activity.current_task = current_task
            agent_activity.progress_percentage = progress
            agent_activity.last_update = now
            agent_activity.sources_found = sources_found
            agent_activity.tokens_used = tokens_used
            agent_activity.error_message = error_message
        
        self.last_update = now
    
    def add_stage_progress(self, stage: ResearchStage, progress: int, 
                          message: str, details: Dict[str, Any] = None):
        """Add or update progress for a specific stage"""
        now = datetime.now(timezone.utc)
        details = details or {}
        
        # Find existing stage progress or create new one
        stage_progress = None
        for sp in self.stage_progress:
            if sp.stage == stage:
                stage_progress = sp
                break
        
        if stage_progress is None:
            stage_progress = StageProgress(
                stage=stage,
                progress_percentage=progress,
                start_time=now,
                message=message,
                details=details
            )
            self.stage_progress.append(stage_progress)
        else:
            stage_progress.progress_percentage = progress
            stage_progress.message = message
            stage_progress.details.update(details)
            
            # Mark stage as completed if progress is 100%
            if progress >= 100 and stage_progress.end_time is None:
                stage_progress.end_time = now
                stage_progress.duration_seconds = (now - stage_progress.start_time).total_seconds()
        
        self.current_stage = stage
        self.last_update = now
        
        # Recalculate overall progress
        self.overall_progress_percentage = self.calculate_overall_progress()


class DetailedResearchStatus(BaseModel):
    """Enhanced research status with comprehensive progress information"""
    research_id: UUID
    query: str
    status: ResearchStage
    progress: ResearchProgress
    created_at: datetime
    estimated_completion_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Quick access properties
    @property
    def is_active(self) -> bool:
        """Check if research is currently active"""
        return self.status not in [ResearchStage.COMPLETED, ResearchStage.FAILED]
    
    @property
    def is_completed(self) -> bool:
        """Check if research is completed"""
        return self.status == ResearchStage.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if research has failed"""
        return self.status == ResearchStage.FAILED
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()
    
    class Config:
        use_enum_values = True