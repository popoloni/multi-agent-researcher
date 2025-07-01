from typing import List, Dict, Any, Optional, Callable, Awaitable
import asyncio
import json
from uuid import uuid4, UUID
import time
import re
from datetime import datetime, timezone

from app.agents.base_agent import BaseAgent
from app.agents.citation_agent import CitationAgent
from app.agents.search_agent import SearchSubAgent
from app.models.schemas import (
    ResearchQuery, ResearchPlan, SubAgentTask, 
    SubAgentResult, ResearchResult, CitationInfo,
    # Progress tracking models (Task 2.1)
    ResearchStage, AgentStatus, ResearchProgress, 
    PerformanceMetrics, AgentActivity, StageProgress
)
from app.core.prompts import LEAD_AGENT_PROMPT
from app.core.config import settings
from app.tools.memory_tools import MemoryStore

class LeadResearchAgent(BaseAgent):
    """Lead agent that orchestrates the research process with progress tracking"""
    
    def __init__(self, progress_callback: Optional[Callable[[ResearchProgress], Awaitable[None]]] = None):
        super().__init__(
            model=settings.LEAD_AGENT_MODEL,
            name="Lead Research Agent"
        )
        self.memory_store = MemoryStore()
        self.active_subagents: Dict[str, SearchSubAgent] = {}
        self.citation_list = []
        
        # Progress tracking (Task 2.2)
        self.progress_callback = progress_callback
        self.current_research_progress: Optional[ResearchProgress] = None
        self.stage_start_times: Dict[ResearchStage, datetime] = {}
        self.performance_metrics: Optional[PerformanceMetrics] = None
        
    def get_system_prompt(self) -> str:
        return LEAD_AGENT_PROMPT
    
    # ===== PROGRESS TRACKING METHODS (Task 2.2) =====
    
    def _initialize_progress_tracking(self, research_id: UUID, query: str) -> None:
        """Initialize progress tracking for a research session"""
        now = datetime.now(timezone.utc)
        
        # Initialize performance metrics
        self.performance_metrics = PerformanceMetrics(
            total_execution_time=0.0,
            planning_time=0.0,
            execution_time=0.0,
            synthesis_time=0.0,
            citation_time=0.0,
            total_tokens_used=0,
            total_sources_found=0,
            average_agent_efficiency=0.0,
            success_rate=0.0
        )
        
        # Initialize research progress
        self.current_research_progress = ResearchProgress(
            research_id=research_id,
            current_stage=ResearchStage.STARTED,
            overall_progress_percentage=0,
            performance_metrics=self.performance_metrics,
            start_time=now,
            last_update=now
        )
        
        # Track stage start time
        self.stage_start_times[ResearchStage.STARTED] = now
        
        # Add initial stage progress
        self.current_research_progress.add_stage_progress(
            ResearchStage.STARTED,
            100,
            "Research session initialized",
            {"query": query, "research_id": str(research_id)}
        )
    
    async def _update_stage_progress(self, stage: ResearchStage, progress: int, 
                                   message: str, details: Dict[str, Any] = None) -> None:
        """Update progress for a specific research stage"""
        if not self.current_research_progress:
            return
        
        now = datetime.now(timezone.utc)
        details = details or {}
        
        # Track stage start time if this is a new stage
        if stage not in self.stage_start_times:
            self.stage_start_times[stage] = now
        
        # Update stage progress
        self.current_research_progress.add_stage_progress(stage, progress, message, details)
        
        # Update performance metrics if stage is completed
        if progress >= 100 and stage in self.stage_start_times:
            stage_duration = (now - self.stage_start_times[stage]).total_seconds()
            
            if stage == ResearchStage.PLANNING:
                self.performance_metrics.planning_time = stage_duration
            elif stage == ResearchStage.EXECUTING:
                self.performance_metrics.execution_time = stage_duration
            elif stage == ResearchStage.SYNTHESIZING:
                self.performance_metrics.synthesis_time = stage_duration
            elif stage == ResearchStage.CITING:
                self.performance_metrics.citation_time = stage_duration
        
        # Call progress callback if available
        if self.progress_callback:
            await self.progress_callback(self.current_research_progress)
    
    async def _update_agent_activity(self, agent_id: str, status: AgentStatus, 
                                   current_task: str, progress: int = 0,
                                   sources_found: int = 0, tokens_used: int = 0,
                                   error_message: Optional[str] = None) -> None:
        """Update activity for a specific subagent"""
        if not self.current_research_progress:
            return
        
        # Update agent activity
        self.current_research_progress.update_agent_activity(
            agent_id=agent_id,
            status=status,
            current_task=current_task,
            progress=progress,
            sources_found=sources_found,
            tokens_used=tokens_used,
            error_message=error_message
        )
        
        # Update performance metrics
        if self.performance_metrics:
            # Recalculate total sources and tokens from all agents
            total_sources = sum(agent.sources_found for agent in self.current_research_progress.agent_activities)
            total_tokens = sum(agent.tokens_used for agent in self.current_research_progress.agent_activities)
            
            self.performance_metrics.total_sources_found = total_sources
            self.performance_metrics.total_tokens_used = total_tokens + self.total_tokens
            
            # Calculate average agent efficiency
            active_agents = self.current_research_progress.get_active_agents()
            if active_agents:
                avg_efficiency = sum(agent.progress_percentage for agent in active_agents) / len(active_agents)
                self.performance_metrics.average_agent_efficiency = avg_efficiency
        
        # Call progress callback if available
        if self.progress_callback:
            await self.progress_callback(self.current_research_progress)
    
    def _finalize_progress_tracking(self, success: bool = True) -> None:
        """Finalize progress tracking and calculate final metrics"""
        if not self.current_research_progress or not self.performance_metrics:
            return
        
        now = datetime.now(timezone.utc)
        
        # Calculate total execution time
        total_time = (now - self.current_research_progress.start_time).total_seconds()
        self.performance_metrics.total_execution_time = total_time
        
        # Set success rate
        self.performance_metrics.success_rate = 100.0 if success else 0.0
        
        # Update final stage
        final_stage = ResearchStage.COMPLETED if success else ResearchStage.FAILED
        final_message = "Research completed successfully" if success else "Research failed"
        
        self.current_research_progress.add_stage_progress(
            final_stage,
            100,
            final_message,
            {"total_execution_time": total_time, "success": success}
        )
        
        # Mark all agents as completed
        for agent in self.current_research_progress.agent_activities:
            if agent.status not in [AgentStatus.COMPLETED, AgentStatus.FAILED]:
                agent.status = AgentStatus.COMPLETED if success else AgentStatus.FAILED
                agent.progress_percentage = 100
                agent.last_update = now
        
    async def conduct_research(self, query: ResearchQuery, research_id: Optional[UUID] = None) -> ResearchResult:
        """Main entry point for conducting research with progress tracking"""
        start_time = time.time()

        if research_id is None:
            research_id = uuid4()
        
        try:
            # Initialize progress tracking (Task 2.2)
            self._initialize_progress_tracking(research_id, query.query)
            
            # Save initial context
            await self.memory_store.save_context(
                research_id, 
                {"query": query.dict(), "status": "planning"}
            )
            
            # Phase 1: Analyze query and create research plan
            await self._update_stage_progress(
                ResearchStage.PLANNING, 0, "Starting research planning phase"
            )
            
            plan = await self._create_research_plan_with_progress(query)
            
            await self._update_stage_progress(
                ResearchStage.PLANNING, 100, "Research plan created successfully",
                {"subtasks": len(plan.subtasks), "complexity": plan.estimated_complexity}
            )
            
            await self.memory_store.save_context(
                research_id,
                {"plan": plan.dict(), "status": "executing"}
            )
            
            # Phase 2: Execute research plan with subagents
            await self._update_stage_progress(
                ResearchStage.EXECUTING, 0, "Starting research execution phase"
            )
            
            results = await self._execute_research_plan_with_progress(plan, query.max_iterations)
            
            await self._update_stage_progress(
                ResearchStage.EXECUTING, 100, "Research execution completed",
                {"results_count": len(results), "total_sources": sum(len(r.sources) for r in results)}
            )
            
            # Phase 3: Synthesize results into final report
            await self._update_stage_progress(
                ResearchStage.SYNTHESIZING, 0, "Starting results synthesis"
            )
            
            final_report = await self._synthesize_results_with_progress(query.query, results)
            
            await self._update_stage_progress(
                ResearchStage.SYNTHESIZING, 100, "Results synthesis completed"
            )
            
            # Phase 4: Add citations
            await self._update_stage_progress(
                ResearchStage.CITING, 0, "Adding citations and references"
            )
            
            cited_report = await self._add_citations_with_progress(final_report, results)
            
            await self._update_stage_progress(
                ResearchStage.CITING, 100, "Citations added successfully"
            )
            
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
            
            # Finalize progress tracking
            self._finalize_progress_tracking(success=True)
            
            # Save final result
            await self.memory_store.save_result(research_id, research_result)
            
            return research_result
            
        except Exception as e:
            # Handle research failure
            self._finalize_progress_tracking(success=False)
            raise e
    
    # ===== ENHANCED METHODS WITH PROGRESS TRACKING (Task 2.2) =====
    
    async def _create_research_plan_with_progress(self, query: ResearchQuery) -> ResearchPlan:
        """Create a research plan with progress tracking"""
        
        # Update progress: Starting analysis
        await self._update_stage_progress(
            ResearchStage.PLANNING, 25, "Analyzing research query"
        )
        
        # Use thinking to analyze the query
        thinking_result = await self.think(f"Research query: {query.query}")
        
        # Update progress: Creating plan
        await self._update_stage_progress(
            ResearchStage.PLANNING, 50, "Creating detailed research plan"
        )
        
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
        
        # Update progress: Processing plan
        await self._update_stage_progress(
            ResearchStage.PLANNING, 75, "Processing and validating research plan"
        )
        
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
                
                plan = ResearchPlan(
                    strategy=plan_data["strategy"],
                    subtasks=subtasks,
                    estimated_complexity=plan_data["complexity"]
                )
                
                return plan
            
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
    
    async def _execute_research_plan_with_progress(
        self, 
        plan: ResearchPlan, 
        max_iterations: int
    ) -> List[SubAgentResult]:
        """Execute the research plan with progress tracking"""
        
        results = []
        remaining_tasks = plan.subtasks.copy()
        iteration = 0
        
        while remaining_tasks and iteration < max_iterations:
            iteration += 1
            
            # Update progress for current iteration
            iteration_progress = min(20 + (iteration * 60 // max_iterations), 80)
            await self._update_stage_progress(
                ResearchStage.EXECUTING, 
                iteration_progress, 
                f"Executing iteration {iteration}/{max_iterations}",
                {"iteration": iteration, "remaining_tasks": len(remaining_tasks)}
            )
            
            # Process tasks in batches (parallel execution)
            batch_size = min(len(remaining_tasks), settings.MAX_PARALLEL_SUBAGENTS)
            current_batch = remaining_tasks[:batch_size]
            remaining_tasks = remaining_tasks[batch_size:]
            
            # Create subagents for this batch and track them
            batch_tasks = []
            for i, task in enumerate(current_batch):
                agent_id = f"agent_{iteration}_{i+1}"
                subagent = SearchSubAgent(task.task_id)
                self.active_subagents[agent_id] = subagent
                
                # Initialize agent tracking
                await self._update_agent_activity(
                    agent_id=agent_id,
                    status=AgentStatus.INITIALIZING,
                    current_task=task.objective,
                    progress=0
                )
                
                batch_tasks.append(self._execute_subagent_with_tracking(subagent, task, agent_id))
                
            # Execute batch in parallel
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(batch_results):
                agent_id = f"agent_{iteration}_{i+1}"
                if isinstance(result, Exception):
                    print(f"Subagent failed: {result}")
                    await self._update_agent_activity(
                        agent_id=agent_id,
                        status=AgentStatus.FAILED,
                        current_task="Task failed",
                        progress=0,
                        error_message=str(result)
                    )
                else:
                    results.append(result)
                    await self._update_agent_activity(
                        agent_id=agent_id,
                        status=AgentStatus.COMPLETED,
                        current_task="Task completed successfully",
                        progress=100,
                        sources_found=len(result.sources),
                        tokens_used=result.token_count
                    )
                    
            # Check if we need more research based on results
            if await self._needs_more_research(results, plan.strategy):
                # Create additional tasks if needed
                new_tasks = await self._create_followup_tasks(results)
                remaining_tasks.extend(new_tasks)
                
        return results
    
    async def _execute_subagent_with_tracking(
        self, 
        subagent: SearchSubAgent, 
        task: SubAgentTask, 
        agent_id: str
    ) -> SubAgentResult:
        """Execute a subagent task with progress tracking and real-time updates"""
        try:
            # Update status: Starting task
            await self._update_agent_activity(
                agent_id=agent_id,
                status=AgentStatus.SEARCHING,
                current_task=f"Searching: {task.objective[:60]}... (step 0)",
                progress=0
            )
            # Define progress callback
            async def progress_callback(percent, current_task):
                await self._update_agent_activity(
                    agent_id=agent_id,
                    status=AgentStatus.SEARCHING if percent < 100 else AgentStatus.COMPLETED,
                    current_task=current_task,
                    progress=percent
                )
            # Execute the task with progress callback
            result = await subagent.execute_task(task, progress_callback=progress_callback)
            # Update status: Task completed
            await self._update_agent_activity(
                agent_id=agent_id,
                status=AgentStatus.COMPLETED,
                current_task=f"Completed: {task.objective[:60]}...",
                progress=100,
                sources_found=len(result.sources),
                tokens_used=result.token_count
            )
            return result
        except Exception as e:
            # Update status: Task failed
            await self._update_agent_activity(
                agent_id=agent_id,
                status=AgentStatus.FAILED,
                current_task="Task failed",
                progress=0,
                error_message=str(e)
            )
            raise e
    
    async def _synthesize_results_with_progress(
        self, 
        original_query: str,
        results: List[SubAgentResult]
    ) -> str:
        """Synthesize all results into a coherent report with progress tracking"""
        
        # Update progress: Compiling findings
        await self._update_stage_progress(
            ResearchStage.SYNTHESIZING, 25, "Compiling research findings"
        )
        
        # Compile all findings
        all_findings = []
        for result in results:
            all_findings.extend(result.findings)
        
        # Update progress: Creating synthesis
        await self._update_stage_progress(
            ResearchStage.SYNTHESIZING, 50, "Creating comprehensive synthesis"
        )
            
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
        
        # Update progress: Generating report
        await self._update_stage_progress(
            ResearchStage.SYNTHESIZING, 75, "Generating final report"
        )
        
        report = await self._call_llm(synthesis_prompt, max_tokens=8000)
        return report
    
    async def _add_citations_with_progress(
        self, 
        report: str, 
        results: List[SubAgentResult]
    ) -> str:
        """Add citations to the report with progress tracking"""
        
        # Update progress: Preparing citations
        await self._update_stage_progress(
            ResearchStage.CITING, 25, "Preparing citation sources"
        )
        
        # Initialize citation agent
        citation_agent = CitationAgent()
        
        # Compile all sources and findings
        all_sources = []
        all_findings = []
        
        for result in results:
            all_sources.extend(result.sources)
            all_findings.extend(result.findings)
        
        # Update progress: Processing sources
        await self._update_stage_progress(
            ResearchStage.CITING, 50, "Processing and deduplicating sources"
        )
        
        # Remove duplicate sources
        unique_sources = []
        seen_urls = set()
        
        for source in all_sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique_sources.append(source)
        
        # Update progress: Adding citations
        await self._update_stage_progress(
            ResearchStage.CITING, 75, "Adding citations to report"
        )
                
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