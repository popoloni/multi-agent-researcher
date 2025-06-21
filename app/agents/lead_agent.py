from typing import List, Dict, Any, Optional
import asyncio
import json
from uuid import uuid4
import time
import re

from app.agents.base_agent import BaseAgent
from app.agents.citation_agent import CitationAgent
from app.agents.search_agent import SearchSubAgent
from app.models.schemas import (
    ResearchQuery, ResearchPlan, SubAgentTask, 
    SubAgentResult, ResearchResult, CitationInfo
)
from app.core.prompts import LEAD_AGENT_PROMPT
from app.core.config import settings
from app.tools.memory_tools import MemoryStore

class LeadResearchAgent(BaseAgent):
    """Lead agent that orchestrates the research process"""
    
    def __init__(self):
        super().__init__(
            model=settings.LEAD_AGENT_MODEL,
            name="Lead Research Agent"
        )
        self.memory_store = MemoryStore()
        self.active_subagents: Dict[str, SearchSubAgent] = {}
        self.citation_list = []
        
    def get_system_prompt(self) -> str:
        return LEAD_AGENT_PROMPT
        
    async def conduct_research(self, query: ResearchQuery) -> ResearchResult:
        """Main entry point for conducting research"""
        start_time = time.time()

        research_id = uuid4()
        
        # Save initial context
        await self.memory_store.save_context(
            research_id, 
            {"query": query.dict(), "status": "planning"}
        )
        
        # Phase 1: Analyze query and create research plan
        plan = await self._create_research_plan(query)
        await self.memory_store.save_context(
            research_id,
            {"plan": plan.dict(), "status": "executing"}
        )
        
        # Phase 2: Execute research plan with subagents
        results = await self._execute_research_plan(plan, query.max_iterations)
        
        # Phase 3: Synthesize results into final report
        final_report = await self._synthesize_results(query.query, results)
        
        # Phase 4: Add citations
        cited_report = await self._add_citations(final_report, results)

        # Extract sections from report
        sections = self._extract_report_sections(cited_report)

        # Convert citation_list to CitationInfo objects
        citation_infos = [
            CitationInfo(**citation)
            for citation in self.citation_list
        ]
        
        # Compile final result
        all_sources = []
        for result in results:
            all_sources.extend(result.sources)
            
        research_result = ResearchResult(
            research_id=research_id,
            query=query.query,
            report=cited_report,
            citations=citation_infos,
            sources_used=all_sources,
            total_tokens_used=self.total_tokens + sum(r.token_count for r in results),
            execution_time=time.time() - start_time,
            subagent_count=len(results),
            report_sections=sections
        )
        
        # Save final result
        await self.memory_store.save_result(research_id, research_result)
        
        return research_result
        
    async def _create_research_plan(self, query: ResearchQuery) -> ResearchPlan:
        """Create a research plan based on the query"""
        
        # Use thinking to analyze the query
        thinking_result = await self.think(f"Research query: {query.query}")
        
        # Create planning prompt
        planning_prompt = f"""
        Create a research plan for the following query:
        
        Query: {query.query}
        
        Based on your analysis, create a detailed research plan with:
        1. Overall strategy
        2. Specific subtasks for search agents (max {query.max_subagents})
        3. Complexity assessment
        
        For each subtask, specify:
        - Clear objective
        - Search focus area
        - Expected output format
        
        Output as JSON:
        {{
            "strategy": "...",
            "complexity": "simple|moderate|complex",
            "subtasks": [
                {{
                    "objective": "...",
                    "search_focus": "...",
                    "expected_output": "..."
                }}
            ]
        }}
        """
        
        response = await self._call_llm(planning_prompt)
        
        # Parse response
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                plan_data = json.loads(json_str)
                
                subtasks = [
                    SubAgentTask(
                        objective=task["objective"],
                        search_focus=task["search_focus"],
                        expected_output_format=task.get("expected_output", "List of relevant findings")
                    )
                    for task in plan_data["subtasks"]
                ]
                
                return ResearchPlan(
                    strategy=plan_data["strategy"],
                    subtasks=subtasks,
                    estimated_complexity=plan_data["complexity"]
                )
            
        except Exception as e:
            print(f"Error parsing plan: {e}")
            
        # Fallback plan
        return ResearchPlan(
            strategy="Direct search for information",
            subtasks=[
                SubAgentTask(
                    objective=f"Find information about: {query.query}",
                    search_focus=query.query,
                    expected_output_format="Relevant findings and sources"
                )
            ],
            estimated_complexity="simple"
        )
            
    async def _execute_research_plan(
        self, 
        plan: ResearchPlan, 
        max_iterations: int
    ) -> List[SubAgentResult]:
        """Execute the research plan using subagents"""
        
        results = []
        remaining_tasks = plan.subtasks.copy()
        iteration = 0
        
        while remaining_tasks and iteration < max_iterations:
            iteration += 1
            
            # Process tasks in batches (parallel execution)
            batch_size = min(len(remaining_tasks), settings.MAX_PARALLEL_SUBAGENTS)
            current_batch = remaining_tasks[:batch_size]
            remaining_tasks = remaining_tasks[batch_size:]
            
            # Create subagents for this batch
            batch_tasks = []
            for task in current_batch:
                subagent = SearchSubAgent(task.task_id)
                self.active_subagents[str(task.task_id)] = subagent
                batch_tasks.append(subagent.execute_task(task))
                
            # Execute batch in parallel
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    print(f"Subagent failed: {result}")
                    # Could retry or handle error
                else:
                    results.append(result)
                    
            # Check if we need more research based on results
            if await self._needs_more_research(results, plan.strategy):
                # Create additional tasks if needed
                new_tasks = await self._create_followup_tasks(results)
                remaining_tasks.extend(new_tasks)
                
        return results
        
    async def _needs_more_research(
        self, 
        current_results: List[SubAgentResult], 
        strategy: str
    ) -> bool:
        """Determine if more research is needed"""
        
        # Simple heuristic - in production would be more sophisticated
        if not current_results:
            return True
            
        total_sources = sum(len(r.sources) for r in current_results)
        if total_sources == 0:
            return True
            
        avg_relevance = sum(
            sum(s.relevance_score for s in r.sources) / len(r.sources) 
            for r in current_results if r.sources
        ) / len(current_results)
        
        # Need more research if we have few sources or low relevance
        return total_sources < 5 or avg_relevance < 0.7
        
    async def _create_followup_tasks(
        self, 
        current_results: List[SubAgentResult]
    ) -> List[SubAgentTask]:
        """Create follow-up tasks based on current results"""
        
        # Analyze what we've found and what's missing
        summary = "\n".join(r.summary for r in current_results)
        
        prompt = f"""
        Based on the current research findings, identify gaps or areas that need more investigation.
        
        Current findings summary:
        {summary}
        
        Create up to 2 follow-up tasks that address gaps or dive deeper into important areas.
        
        Output as JSON:
        {{
            "followup_tasks": [
                {{
                    "objective": "...",
                    "search_focus": "...",
                    "reason": "..."
                }}
            ]
        }}
        """
        
        response = await self._call_llm(prompt)
        
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                return [
                    SubAgentTask(
                        objective=task["objective"],
                        search_focus=task["search_focus"],
                        expected_output_format="Detailed findings"
                    )
                    for task in data.get("followup_tasks", [])
                ]
        except Exception as e:
            print(f"Error parsing followup tasks: {e}")
            
        return []
            
    async def _synthesize_results(
        self, 
        original_query: str,
        results: List[SubAgentResult]
    ) -> str:
        """Synthesize all results into a coherent report"""
        
        # Compile all findings
        all_findings = []
        for result in results:
            all_findings.extend(result.findings)
            
        synthesis_prompt = f"""
        Synthesize the following research findings into a comprehensive report.
        
        Original Query: {original_query}
        
        Research Findings:
        {json.dumps(all_findings, indent=2)}
        
        Create a well-structured report that:
        1. Directly answers the user's query
        2. Organizes information logically
        3. Highlights key insights
        4. Notes any limitations or gaps in the research
        
        Format the report with clear sections and subsections as appropriate.
        Use markdown formatting for headers and structure.
        """
        
        report = await self._call_llm(synthesis_prompt, max_tokens=8000)
        return report
        
    async def _add_citations(
        self, 
        report: str, 
        results: List[SubAgentResult]
    ) -> str:
        """Add citations to the report using the Citation Agent"""
        
        # Initialize citation agent
        citation_agent = CitationAgent()
        
        # Compile all sources and findings
        all_sources = []
        all_findings = []
        
        for result in results:
            all_sources.extend(result.sources)
            all_findings.extend(result.findings)
            
        # Remove duplicate sources
        unique_sources = []
        seen_urls = set()
        
        for source in all_sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique_sources.append(source)
                
        # Add citations to the report
        cited_report, citation_list = await citation_agent.add_citations(
            report,
            unique_sources,
            all_findings
        )
        
        # Generate bibliography
        bibliography = await citation_agent.generate_bibliography(
            unique_sources,
            citation_list,
            style="MLA"
        )
        
        # Append bibliography to report
        final_report = cited_report + bibliography
        
        # Update the research result with citation information
        self.citation_list = citation_list
        
        return final_report
    
    def _extract_report_sections(self, report: str) -> List[str]:
        """Extract main sections from the report"""
        
        # Find headers (lines starting with #)
        headers = re.findall(r'^#+\s+(.+)$', report, re.MULTILINE)
        
        # Clean and return unique headers
        sections = []
        for header in headers:
            clean_header = header.strip()
            if clean_header and clean_header not in sections:
                sections.append(clean_header)
                
        return sections