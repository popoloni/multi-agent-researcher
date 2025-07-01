from typing import Optional, Dict, Any, Literal, List
from uuid import UUID, uuid4
import asyncio
import time
from datetime import datetime, timezone
from enum import Enum

from app.models.schemas import (
    ResearchQuery, ResearchResult, ResearchProgress, 
    DetailedResearchStatus, ResearchStage, CitationInfo
)
from app.agents.lead_agent import LeadResearchAgent
from app.tools.memory_tools import MemoryStore

class ResearchStatus(str, Enum):
    """Research status enumeration"""
    STARTED = "started"
    PLANNING = "planning"
    EXECUTING = "executing"
    SYNTHESIZING = "synthesizing"
    CITING = "citing"
    COMPLETED = "completed"
    FAILED = "failed"

class ResearchTask:
    """Research task tracking with enhanced progress information"""
    def __init__(self, research_id: UUID, query: ResearchQuery):
        self.research_id = research_id
        self.query = query
        self.status = ResearchStatus.STARTED
        self.created_at = datetime.now(timezone.utc)
        self.progress_percentage = 0
        self.message = "Research initiated"
        self.task: Optional[asyncio.Task] = None
        self.result: Optional[ResearchResult] = None
        self.error: Optional[str] = None
        
        # Enhanced progress tracking (Task 3.1)
        self.current_progress: Optional[ResearchProgress] = None
        self.last_progress_update: Optional[datetime] = None

class ResearchService:
    """Service layer for research operations with enhanced progress tracking"""
    
    def __init__(self):
        self.memory_store = MemoryStore()
        self._active_research: Dict[UUID, ResearchTask] = {}
        self._completed_research: Dict[UUID, ResearchTask] = {}
        
        # Progress storage for real-time updates (Task 3.1)
        self._progress_store: Dict[UUID, ResearchProgress] = {}
    
    # ===== PROGRESS STORAGE METHODS (Task 3.1) =====
    
    async def store_progress(self, research_id: UUID, progress: ResearchProgress) -> None:
        """Store progress update in memory store for real-time access"""
        self._progress_store[research_id] = progress
        
        # Update the research task if it exists
        if research_id in self._active_research:
            research_task = self._active_research[research_id]
            research_task.current_progress = progress
            research_task.last_progress_update = datetime.now(timezone.utc)
            
            # Update basic status fields for backward compatibility
            research_task.status = ResearchStatus(progress.current_stage if isinstance(progress.current_stage, str) else progress.current_stage.value)
            research_task.progress_percentage = progress.overall_progress_percentage
            research_task.message = progress.stage_progress[-1].message if progress.stage_progress else "Research in progress"
    
    async def get_progress(self, research_id: UUID) -> Optional[ResearchProgress]:
        """Retrieve current progress for research session"""
        return self._progress_store.get(research_id)
    
    async def get_detailed_status(self, research_id: UUID) -> Optional[DetailedResearchStatus]:
        """Get comprehensive research status with progress information"""
        # Check active research first
        if research_id in self._active_research:
            research_task = self._active_research[research_id]
            progress = self._progress_store.get(research_id)
            
            if progress:
                return DetailedResearchStatus(
                    research_id=research_id,
                    query=research_task.query.query,
                    status=ResearchStage(research_task.status.value),
                    progress=progress,
                    created_at=research_task.created_at,
                    error_message=research_task.error
                )
        
        # Check completed research
        if research_id in self._completed_research:
            research_task = self._completed_research[research_id]
            progress = self._progress_store.get(research_id)
            
            if progress:
                return DetailedResearchStatus(
                    research_id=research_id,
                    query=research_task.query.query,
                    status=ResearchStage(research_task.status.value),
                    progress=progress,
                    created_at=research_task.created_at,
                    error_message=research_task.error
                )
        
        return None
        
    async def start_research(self, query: ResearchQuery) -> UUID:
        """Start a new research task with enhanced progress tracking"""
        
        # Generate real UUID for research
        research_id = uuid4()
        
        # Create research task tracker
        research_task = ResearchTask(research_id, query)
        
        # Store in active research
        self._active_research[research_id] = research_task
        
        # Create and start real async research task with progress callback
        research_task.task = asyncio.create_task(
            self._execute_research_with_progress_callback(research_task)
        )
        
        # Initial status
        research_task.status = ResearchStatus.STARTED
        research_task.progress_percentage = 10
        research_task.message = "Research task initiated and starting..."
        
        return research_id
    
    async def _execute_research_with_progress_callback(self, research_task: ResearchTask):
        """Execute research with enhanced progress tracking using callback mechanism"""
        try:
            # Create progress callback that stores updates
            async def progress_callback(progress: ResearchProgress):
                """Callback to handle progress updates from LeadResearchAgent"""
                try:
                    await self.store_progress(research_task.research_id, progress)
                except Exception as e:
                    print(f"Error storing progress: {e}")
            
            # Create lead agent with progress callback
            lead_agent = LeadResearchAgent(progress_callback=progress_callback)
            
            # Execute research with real-time progress tracking
            result = await lead_agent.conduct_research(research_task.query, research_task.research_id)
            
            # Mark as completed
            research_task.status = ResearchStatus.COMPLETED
            research_task.progress_percentage = 100
            research_task.message = "Research completed successfully"
            research_task.result = result
            
            # Move to completed research
            self._completed_research[research_task.research_id] = research_task
            if research_task.research_id in self._active_research:
                del self._active_research[research_task.research_id]
                
        except Exception as e:
            # Handle research failure
            research_task.status = ResearchStatus.FAILED
            research_task.progress_percentage = 0
            research_task.message = f"Research failed: {str(e)}"
            research_task.error = str(e)
            
            # Move to completed research (even if failed)
            self._completed_research[research_task.research_id] = research_task
            if research_task.research_id in self._active_research:
                del self._active_research[research_task.research_id]
    
    # Legacy method removed - now using LeadResearchAgent.conduct_research with progress callback
        
    def _get_enum_value(self, enum_obj):
        """Helper to safely get enum value"""
        return enum_obj.value if hasattr(enum_obj, 'value') else enum_obj
    
    async def get_research_status(self, research_id: UUID) -> Dict[str, Any]:
        """Get the status of a research task with enhanced progress information"""
        
        # Try to get detailed status first
        detailed_status = await self.get_detailed_status(research_id)
        if detailed_status:
            # Convert DetailedResearchStatus to dict format for API compatibility
            progress = detailed_status.progress
            
            status_data = {
                "status": self._get_enum_value(detailed_status.status),
                "progress_percentage": progress.overall_progress_percentage,
                "message": progress.get_current_stage_progress().message if progress.get_current_stage_progress() else self._get_enum_value(progress.current_stage),
                "created_at": detailed_status.created_at.isoformat(),
                "research_id": str(detailed_status.research_id),
                "query": detailed_status.query,
                "error": detailed_status.error_message,
                "elapsed_time": detailed_status.elapsed_time,
                
                # Enhanced progress information
                "current_stage": self._get_enum_value(progress.current_stage),
                "stage_progress": [
                    {
                        "stage": self._get_enum_value(sp.stage),
                        "progress_percentage": sp.progress_percentage,
                        "message": sp.message,
                        "start_time": sp.start_time.isoformat(),
                        "end_time": sp.end_time.isoformat() if sp.end_time else None,
                        "duration_seconds": sp.duration_seconds
                    }
                    for sp in progress.stage_progress
                ],
                "agent_activities": [
                    {
                        "agent_id": aa.agent_id,
                        "agent_name": aa.agent_name,
                        "status": self._get_enum_value(aa.status),
                        "current_task": aa.current_task,
                        "progress_percentage": aa.progress_percentage,
                        "sources_found": aa.sources_found,
                        "tokens_used": aa.tokens_used,
                        "start_time": aa.start_time.isoformat(),
                        "last_update": aa.last_update.isoformat(),
                        "error_message": aa.error_message
                    }
                    for aa in progress.agent_activities
                ],
                "performance_metrics": {
                    "total_sources_found": progress.performance_metrics.total_sources_found,
                    "total_tokens_used": progress.performance_metrics.total_tokens_used,
                    "total_execution_time": progress.performance_metrics.total_execution_time,
                    "planning_time": progress.performance_metrics.planning_time,
                    "execution_time": progress.performance_metrics.execution_time,
                    "synthesis_time": progress.performance_metrics.synthesis_time,
                    "citation_time": progress.performance_metrics.citation_time,
                    "average_agent_efficiency": progress.performance_metrics.average_agent_efficiency,
                    "success_rate": progress.performance_metrics.success_rate
                } if progress.performance_metrics else None
            }
            
            return status_data
        
        # Fallback to basic status for backward compatibility
        # Check active research
        if research_id in self._active_research:
            research_task = self._active_research[research_id]
            
            # Calculate elapsed time
            elapsed_time = (datetime.now(timezone.utc) - research_task.created_at).total_seconds()
            
            status_data = {
                "status": research_task.status.value,
                "progress_percentage": research_task.progress_percentage,
                "message": research_task.message,
                "created_at": research_task.created_at.isoformat(),
                "research_id": str(research_task.research_id),
                "query": research_task.query.query,
                "error": research_task.error,
                "elapsed_time": elapsed_time,
                "max_subagents": research_task.query.max_subagents,
                "max_iterations": research_task.query.max_iterations
            }
            
            return status_data
        
        # Check completed research
        if research_id in self._completed_research:
            research_task = self._completed_research[research_id]
            
            # Calculate total execution time
            if research_task.result:
                execution_time = research_task.result.execution_time
            else:
                execution_time = (datetime.now(timezone.utc) - research_task.created_at).total_seconds()
            
            status_data = {
                "status": research_task.status.value,
                "progress_percentage": 100 if research_task.status == ResearchStatus.COMPLETED else 0,
                "message": research_task.message,
                "created_at": research_task.created_at.isoformat(),
                "research_id": str(research_task.research_id),
                "query": research_task.query.query,
                "error": research_task.error,
                "completed": True,
                "execution_time": execution_time
            }
            
            # Add result summary if available
            if research_task.result:
                status_data.update({
                    "result_summary": {
                        "sources_count": len(research_task.result.sources_used),
                        "citations_count": len(research_task.result.citations),
                        "tokens_used": research_task.result.total_tokens_used,
                        "subagent_count": research_task.result.subagent_count,
                        "sections_count": len(research_task.result.report_sections)
                    }
                })
            
            return status_data
            
        return {
            "status": "not_found",
            "message": "Research ID not found",
            "research_id": str(research_id)
        }
        
    async def get_research_result(self, research_id: UUID) -> Optional[ResearchResult]:
        """Get the result of a completed research task with complete data retrieval"""
        
        # Check completed research first
        if research_id in self._completed_research:
            research_task = self._completed_research[research_id]
            if research_task.result:
                # Ensure the result has the research_id set correctly
                research_task.result.research_id = research_id
                return research_task.result
        
        # Check active research (might be completed but not moved yet)
        if research_id in self._active_research:
            research_task = self._active_research[research_id]
            if research_task.result:
                # Ensure the result has the research_id set correctly
                research_task.result.research_id = research_id
                return research_task.result
        
        # Fallback to memory store for backward compatibility
        result = await self.memory_store.get_result(research_id)
        if result:
            # Ensure the result has the research_id set correctly
            result.research_id = research_id
        
        return result
    
    async def cancel_research(self, research_id: UUID) -> bool:
        """Cancel an active research task"""
        if research_id in self._active_research:
            research_task = self._active_research[research_id]
            
            # Cancel the async task if it exists
            if research_task.task and not research_task.task.done():
                research_task.task.cancel()
                
            # Update status
            research_task.status = ResearchStatus.FAILED
            research_task.message = "Research cancelled by user"
            research_task.error = "Cancelled"
            
            # Move to completed research
            self._completed_research[research_id] = research_task
            del self._active_research[research_id]
            
            return True
        
        return False
    
    def get_research_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get research history with summary information"""
        history = []
        
        # Combine active and completed research
        all_research = {**self._active_research, **self._completed_research}
        
        # Sort by creation time (most recent first)
        sorted_research = sorted(
            all_research.items(),
            key=lambda x: x[1].created_at,
            reverse=True
        )
        
        for research_id, research_task in sorted_research[:limit]:
            history_item = {
                "research_id": str(research_id),
                "query": research_task.query.query,
                "status": research_task.status.value,
                "created_at": research_task.created_at.isoformat(),
                "progress_percentage": research_task.progress_percentage,
                "message": research_task.message
            }
            
            # Add completion info if available
            if research_task.result:
                history_item.update({
                    "execution_time": research_task.result.execution_time,
                    "sources_count": len(research_task.result.sources_used),
                    "citations_count": len(research_task.result.citations),
                    "tokens_used": research_task.result.total_tokens_used
                })
            
            history.append(history_item)
        
        return history
    
    def get_active_research_count(self) -> int:
        """Get the number of active research tasks"""
        return len(self._active_research)
    
    def get_completed_research_count(self) -> int:
        """Get the number of completed research tasks"""
        return len(self._completed_research)
    
    async def cleanup_completed_research(self, max_completed: int = 100):
        """Clean up old completed research tasks and progress data to prevent memory leaks"""
        if len(self._completed_research) > max_completed:
            # Keep only the most recent completed research
            sorted_completed = sorted(
                self._completed_research.items(),
                key=lambda x: x[1].created_at,
                reverse=True
            )
            
            # Get IDs to remove
            ids_to_remove = [research_id for research_id, _ in sorted_completed[max_completed:]]
            
            # Clean up progress store for removed research
            for research_id in ids_to_remove:
                if research_id in self._progress_store:
                    del self._progress_store[research_id]
            
            # Keep only the most recent max_completed items
            self._completed_research = dict(sorted_completed[:max_completed])
    
    def get_progress_store_size(self) -> int:
        """Get the number of progress entries stored"""
        return len(self._progress_store)