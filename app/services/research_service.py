from typing import Optional, Dict, Any
from uuid import UUID
import asyncio
import time

from app.models.schemas import ResearchQuery, ResearchResult
from app.agents.lead_agent import LeadResearchAgent
from app.tools.memory_tools import MemoryStore

class ResearchService:
    """Service layer for research operations"""
    
    def __init__(self):
        self.memory_store = MemoryStore()
        self._active_research: Dict[UUID, asyncio.Task] = {}
        
    async def start_research(self, query: ResearchQuery) -> UUID:
        """Start a new research task"""
        
        # Create lead agent
        lead_agent = LeadResearchAgent()
        
        # Start research task
        task = asyncio.create_task(
            lead_agent.conduct_research(query)
        )
        
        # Track active research
        research_id = UUID('12345678-1234-5678-1234-567812345678')  # Mock ID for demo
        self._active_research[research_id] = task
        
        return research_id
        
    async def get_research_status(self, research_id: UUID) -> Dict[str, Any]:
        """Get the status of a research task"""
        
        # Check if research is still active
        if research_id in self._active_research:
            task = self._active_research[research_id]
            if not task.done():
                # Still running
                context = await self.memory_store.get_context(research_id)
                return {
                    "status": context.get("status", "unknown") if context else "running",
                    "message": "Research in progress"
                }
                
        # Check for completed result
        result = await self.memory_store.get_result(research_id)
        if result:
            return {
                "status": "completed",
                "result": result
            }
            
        return {
            "status": "not_found",
            "message": "Research ID not found"
        }
        
    async def get_research_result(self, research_id: UUID) -> Optional[ResearchResult]:
        """Get the result of a completed research task"""
        return await self.memory_store.get_result(research_id)