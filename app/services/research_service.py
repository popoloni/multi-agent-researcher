from typing import Optional, Dict, Any, Literal, List
from uuid import UUID, uuid4
import asyncio
import time
from datetime import datetime, timezone
from enum import Enum

from app.models.schemas import ResearchQuery, ResearchResult
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
    """Research task tracking"""
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

class ResearchService:
    """Service layer for research operations"""
    
    def __init__(self):
        self.memory_store = MemoryStore()
        self._active_research: Dict[UUID, ResearchTask] = {}
        self._completed_research: Dict[UUID, ResearchTask] = {}
        
    async def start_research(self, query: ResearchQuery) -> UUID:
        """Start a new research task with real LeadResearchAgent integration"""
        
        # Generate real UUID for research
        research_id = uuid4()
        
        # Create research task tracker
        research_task = ResearchTask(research_id, query)
        
        # Store in active research
        self._active_research[research_id] = research_task
        
        # Create and start real async research task
        research_task.task = asyncio.create_task(
            self._execute_research_with_progress(research_task)
        )
        
        # Initial status
        research_task.status = ResearchStatus.STARTED
        research_task.progress_percentage = 10
        research_task.message = "Research task initiated and starting..."
        
        return research_id
    
    async def _execute_research_with_progress(self, research_task: ResearchTask):
        """Execute research with progress tracking"""
        try:
            # Update status to planning
            research_task.status = ResearchStatus.PLANNING
            research_task.progress_percentage = 20
            research_task.message = "Creating research plan..."
            
            # Create lead agent
            lead_agent = LeadResearchAgent()
            
            # Override the conduct_research method to provide progress updates
            result = await self._conduct_research_with_tracking(lead_agent, research_task)
            
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
    
    async def _conduct_research_with_tracking(
        self, 
        lead_agent: LeadResearchAgent, 
        research_task: ResearchTask
    ) -> ResearchResult:
        """Conduct research with progress tracking"""
        start_time = time.time()
        query = research_task.query
        
        # Phase 1: Planning (20-40%)
        research_task.status = ResearchStatus.PLANNING
        research_task.progress_percentage = 25
        research_task.message = "Analyzing query and creating research plan..."
        
        plan = await lead_agent._create_research_plan(query)
        await lead_agent.memory_store.save_context(
            research_task.research_id,
            {"plan": plan.dict(), "status": "executing"}
        )
        
        # Phase 2: Executing (40-80%)
        research_task.status = ResearchStatus.EXECUTING
        research_task.progress_percentage = 45
        research_task.message = f"Executing research with {len(plan.subtasks)} agents..."
        
        results = await lead_agent._execute_research_plan(plan, query.max_iterations)
        
        research_task.progress_percentage = 70
        research_task.message = "Research execution completed, processing results..."
        
        # Phase 3: Synthesizing (80-90%)
        research_task.status = ResearchStatus.SYNTHESIZING
        research_task.progress_percentage = 80
        research_task.message = "Synthesizing findings into comprehensive report..."
        
        final_report = await lead_agent._synthesize_results(query.query, results)
        
        # Phase 4: Citations (90-95%)
        research_task.status = ResearchStatus.CITING
        research_task.progress_percentage = 90
        research_task.message = "Adding citations and finalizing report..."
        
        cited_report = await lead_agent._add_citations(final_report, results)
        sections = lead_agent._extract_report_sections(cited_report)
        
        # Convert citation_list to CitationInfo objects
        citation_infos = [
            CitationInfo(**citation)
            for citation in lead_agent.citation_list
        ]
        
        # Compile final result
        all_sources = []
        for result in results:
            all_sources.extend(result.sources)
            
        research_result = ResearchResult(
            research_id=research_task.research_id,
            query=query.query,
            report=cited_report,
            citations=citation_infos,
            sources_used=all_sources,
            total_tokens_used=lead_agent.total_tokens + sum(r.token_count for r in results),
            execution_time=time.time() - start_time,
            subagent_count=len(results),
            report_sections=sections
        )
        
        # Save final result
        await lead_agent.memory_store.save_result(research_task.research_id, research_result)
        
        return research_result
        
    async def get_research_status(self, research_id: UUID) -> Dict[str, Any]:
        """Get the status of a research task with detailed progress and meaningful data"""
        
        # Check active research
        if research_id in self._active_research:
            research_task = self._active_research[research_id]
            
            # Calculate elapsed time
            elapsed_time = (datetime.now(timezone.utc) - research_task.created_at).total_seconds()
            
            # Get additional context from memory store if available
            context = await self.memory_store.get_context(research_id)
            
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
            
            # Add plan information if available
            if context and "plan" in context:
                plan_data = context["plan"]
                status_data.update({
                    "plan": {
                        "strategy": plan_data.get("strategy", ""),
                        "subtask_count": len(plan_data.get("subtasks", [])),
                        "complexity": plan_data.get("estimated_complexity", "unknown")
                    }
                })
            
            # Add stage-specific information
            if research_task.status == ResearchStatus.EXECUTING:
                status_data["agents"] = [
                    {
                        "id": f"agent_{i+1}",
                        "status": "active" if i < research_task.query.max_subagents else "pending",
                        "task": f"Research subtask {i+1}"
                    }
                    for i in range(research_task.query.max_subagents)
                ]
            
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
        """Clean up old completed research tasks to prevent memory leaks"""
        if len(self._completed_research) > max_completed:
            # Keep only the most recent completed research
            sorted_completed = sorted(
                self._completed_research.items(),
                key=lambda x: x[1].created_at,
                reverse=True
            )
            
            # Keep only the most recent max_completed items
            self._completed_research = dict(sorted_completed[:max_completed])