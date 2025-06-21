from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID, uuid4

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
    created_at: datetime = Field(default_factory=datetime.utcnow)