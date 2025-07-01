from typing import Optional, Dict, Any, Literal, List
from uuid import UUID, uuid4
import asyncio
import time
from datetime import datetime, timezone
from enum import Enum

from app.models.schemas import (
    ResearchQuery, ResearchResult, ResearchProgress, 
    DetailedResearchStatus, ResearchStage, CitationInfo,
    ResearchHistoryItem, ResearchAnalytics, ProgressPollResponse
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
    
    # ===== TASK 3.2: ENHANCED API METHODS =====
    
    async def get_research_history(
        self, 
        limit: int = 50, 
        offset: int = 0, 
        status_filter: Optional[ResearchStage] = None
    ) -> List[Dict[str, Any]]:
        """Get research history with filtering and pagination"""
        from app.models.schemas import ResearchHistoryItem
        
        # Combine active and completed research
        all_research = {}
        all_research.update(self._active_research)
        all_research.update(self._completed_research)
        
        # Convert to history items
        history_items = []
        for research_id, research_task in all_research.items():
            # Apply status filter if provided
            if status_filter and research_task.status.value != status_filter.value:
                continue
            
            # Get completion time and execution time
            completed_at = None
            execution_time = None
            if research_task.status in [ResearchStatus.COMPLETED, ResearchStatus.FAILED]:
                if hasattr(research_task, 'completed_at'):
                    completed_at = research_task.completed_at
                # Get execution time from result if available
                if research_task.result and hasattr(research_task.result, 'execution_time'):
                    execution_time = research_task.result.execution_time
            
            # Get sources and tokens from result if available
            sources_count = None
            tokens_used = None
            if research_task.result:
                sources_count = len(research_task.result.sources_used) if research_task.result.sources_used else 0
                tokens_used = research_task.result.total_tokens_used
            
            history_item = ResearchHistoryItem(
                research_id=research_id,
                query=research_task.query.query,
                status=ResearchStage(research_task.status.value),
                created_at=research_task.created_at,
                completed_at=completed_at,
                execution_time=execution_time,
                sources_count=sources_count,
                tokens_used=tokens_used,
                progress_percentage=research_task.progress_percentage,
                error_message=research_task.error
            )
            history_items.append(history_item)
        
        # Sort by creation time (newest first)
        history_items.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        start_idx = offset
        end_idx = offset + limit
        return history_items[start_idx:end_idx]
    
    async def get_research_analytics(self) -> Dict[str, Any]:
        """Get comprehensive research analytics"""
        from app.models.schemas import ResearchAnalytics
        from collections import Counter
        
        # Combine all research data
        all_research = {}
        all_research.update(self._active_research)
        all_research.update(self._completed_research)
        
        if not all_research:
            return ResearchAnalytics(
                total_research_sessions=0,
                active_sessions=0,
                completed_sessions=0,
                failed_sessions=0,
                average_execution_time=0.0,
                total_tokens_used=0,
                total_sources_found=0,
                success_rate=0.0,
                most_common_queries=[],
                performance_trends={}
            )
        
        # Calculate basic metrics
        total_sessions = len(all_research)
        active_sessions = len(self._active_research)
        completed_sessions = len([r for r in all_research.values() if r.status == ResearchStatus.COMPLETED])
        failed_sessions = len([r for r in all_research.values() if r.status == ResearchStatus.FAILED])
        
        # Calculate execution times
        execution_times = []
        total_tokens = 0
        total_sources = 0
        queries = []
        
        for research_task in all_research.values():
            queries.append(research_task.query.query)
            
            if hasattr(research_task, 'execution_time') and research_task.execution_time:
                execution_times.append(research_task.execution_time)
            
            if research_task.result:
                if research_task.result.total_tokens_used:
                    total_tokens += research_task.result.total_tokens_used
                if research_task.result.sources_used:
                    total_sources += len(research_task.result.sources_used)
        
        # Calculate averages
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        success_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
        
        # Find most common queries (top 5)
        query_counter = Counter(queries)
        most_common_queries = [query for query, _ in query_counter.most_common(5)]
        
        # Performance trends (simplified)
        performance_trends = {
            "average_tokens_per_session": total_tokens / total_sessions if total_sessions > 0 else 0,
            "average_sources_per_session": total_sources / total_sessions if total_sessions > 0 else 0,
            "completion_rate": success_rate,
            "active_session_ratio": (active_sessions / total_sessions * 100) if total_sessions > 0 else 0
        }
        
        return ResearchAnalytics(
            total_research_sessions=total_sessions,
            active_sessions=active_sessions,
            completed_sessions=completed_sessions,
            failed_sessions=failed_sessions,
            average_execution_time=avg_execution_time,
            total_tokens_used=total_tokens,
            total_sources_found=total_sources,
            success_rate=success_rate,
            most_common_queries=most_common_queries,
            performance_trends=performance_trends
        )
    
    async def get_research_count(self, status_filter: Optional[ResearchStage] = None) -> int:
        """Get total count of research sessions with optional status filter"""
        all_research = {}
        all_research.update(self._active_research)
        all_research.update(self._completed_research)
        
        if not status_filter:
            return len(all_research)
        
        return len([r for r in all_research.values() if r.status.value == status_filter.value])
    
    async def poll_research_progress(
        self, 
        research_id: UUID, 
        last_update: Optional[datetime] = None
    ) -> ProgressPollResponse:
        """Optimized polling endpoint with conditional updates"""
        from app.models.schemas import ProgressPollResponse
        
        # Get current progress
        progress = await self.get_progress(research_id)
        
        if not progress:
            # Research not found or no progress available
            return ProgressPollResponse(
                research_id=research_id,
                has_updates=False,
                progress=None,
                last_update=datetime.now(timezone.utc),
                next_poll_interval=5  # Longer interval for non-existent research
            )
        
        # Check if there are updates since last poll
        has_updates = True
        if last_update and progress.last_update <= last_update:
            has_updates = False
        
        # Determine next poll interval based on research status
        next_poll_interval = 2  # Default 2 seconds
        if progress.current_stage == ResearchStage.COMPLETED:
            next_poll_interval = 0  # No more polling needed
        elif progress.current_stage == ResearchStage.FAILED:
            next_poll_interval = 0  # No more polling needed
        elif progress.overall_progress_percentage > 80:
            next_poll_interval = 1  # More frequent polling near completion
        
        return ProgressPollResponse(
            research_id=research_id,
            has_updates=has_updates,
            progress=progress if has_updates else None,
            last_update=progress.last_update,
            next_poll_interval=next_poll_interval
        )