from typing import List, Dict, Any, Optional
import asyncio
from uuid import UUID
import json

from app.agents.base_agent import BaseAgent
from app.models.schemas import SubAgentTask, SubAgentResult, SearchResult
from app.core.prompts import SEARCH_SUBAGENT_PROMPT
from app.core.config import settings
from app.tools.search_tools import WebSearchTool

class SearchSubAgent(BaseAgent):
    """Subagent specialized in searching for specific information"""
    
    def __init__(self, task_id: UUID):
        super().__init__(
            model=settings.SUBAGENT_MODEL,
            name=f"Search Subagent {task_id}"
        )
        self.task_id = task_id
        self.search_tool = WebSearchTool()
        
    def get_system_prompt(self) -> str:
        return SEARCH_SUBAGENT_PROMPT
        
    async def execute_task(self, task: SubAgentTask) -> SubAgentResult:
        """Execute the assigned research task"""
        
        # Think about approach
        thinking = await self.think(
            f"Task: {task.objective}\nFocus: {task.search_focus}"
        )
        
        # Execute searches based on plan
        all_results = []
        findings = []
        
        for step in thinking.get("steps", [])[:task.max_searches]:
            # Generate search query
            query = await self._generate_search_query(
                task.objective, 
                task.search_focus,
                step,
                all_results
            )
            
            # Perform search
            search_results = await self.search_tool.search(query)
            
            # Evaluate results
            relevant_results = await self._evaluate_results(
                search_results, 
                task.objective
            )
            
            all_results.extend(relevant_results)
            
            # Extract findings from relevant results
            extracted = await self._extract_findings(
                relevant_results,
                task.objective,
                task.expected_output_format
            )
            
            findings.extend(extracted)
            
            # Check if we have enough information
            if await self._has_sufficient_information(findings, task.objective):
                break
                
        # Summarize findings
        summary = await self._summarize_findings(findings, task.objective)
        
        return SubAgentResult(
            task_id=self.task_id,
            findings=findings,
            sources=all_results,
            summary=summary,
            token_count=self.total_tokens
        )
        
    async def _generate_search_query(
        self,
        objective: str,
        focus: str,
        step: str,
        previous_results: List[SearchResult]
    ) -> str:
        """Generate an effective search query"""
        
        prompt = f"""
        Generate a search query for the following:
        
        Objective: {objective}
        Focus Area: {focus}
        Current Step: {step}
        
        Previous searches found {len(previous_results)} results.
        
        Create a search query that:
        - Is concise (2-5 words preferred)
        - Targets the specific information needed
        - Avoids redundancy with previous searches
        
        Output only the search query, nothing else.
        """
        
        query = await self._call_llm(prompt, max_tokens=100)
        return query.strip().strip('"').strip("'")
        
    async def _evaluate_results(
        self,
        results: List[SearchResult],
        objective: str
    ) -> List[SearchResult]:
        """Evaluate search results for relevance"""
        
        if not results:
            return []
            
        # Create evaluation prompt
        results_summary = "\n".join([
            f"{i+1}. {r.title} - {r.snippet[:200]}..."
            for i, r in enumerate(results[:10])
        ])
        
        prompt = f"""
        Evaluate these search results for relevance to the objective.
        
        Objective: {objective}
        
        Search Results:
        {results_summary}
        
        For each result, rate its relevance from 0.0 to 1.0.
        Consider:
        - Direct relevance to the objective
        - Quality of the source
        - Uniqueness of information
        
        Output as JSON:
        {{
            "evaluations": [
                {{"index": 1, "relevance": 0.9, "reason": "..."}}
            ]
        }}
        """
        
        response = await self._call_llm(prompt, max_tokens=2000)
        
        # Parse evaluations and update relevance scores
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                
                for eval in data.get("evaluations", []):
                    idx = eval["index"] - 1
                    if 0 <= idx < len(results):
                        results[idx].relevance_score = eval["relevance"]
                        
                # Return only relevant results
                return [r for r in results if r.relevance_score >= 0.6]
            
        except Exception as e:
            print(f"Error parsing evaluations: {e}")
            
        # If parsing fails, return top results
        return results[:5]
            
    async def _extract_findings(
        self,
        results: List[SearchResult],
        objective: str,
        output_format: str
    ) -> List[Dict[str, Any]]:
        """Extract key findings from search results"""
        
        if not results:
            return []
            
        # Compile content from results
        content_summary = "\n\n".join([
            f"Source: {r.title}\nURL: {r.url}\nContent: {r.snippet}"
            for r in results
        ])
        
        prompt = f"""
        Extract key findings from these sources related to the objective.
        
        Objective: {objective}
        Expected Format: {output_format}
        
        Sources:
        {content_summary}
        
        Extract specific, factual findings that address the objective.
        
        Output as JSON:
        {{
            "findings": [
                {{
                    "fact": "...",
                    "source_url": "...",
                    "source_title": "...",
                    "relevance": "..."
                }}
            ]
        }}
        """
        
        response = await self._call_llm(prompt, max_tokens=3000)
        
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                return data.get("findings", [])
        except Exception as e:
            print(f"Error parsing findings: {e}")
            
        return []
            
    async def _has_sufficient_information(
        self,
        findings: List[Dict[str, Any]],
        objective: str
    ) -> bool:
        """Determine if we have enough information"""
        
        if len(findings) < 3:
            return False
            
        prompt = f"""
        Assess if we have sufficient information to address the objective.
        
        Objective: {objective}
        
        We have found {len(findings)} pieces of information.
        
        Do we have enough high-quality, relevant information to comprehensively address the objective?
        Answer with YES or NO and a brief reason.
        """
        
        response = await self._call_llm(prompt, max_tokens=200)
        
        return "YES" in response.upper()
        
    async def _summarize_findings(
        self,
        findings: List[Dict[str, Any]],
        objective: str
    ) -> str:
        """Create a summary of all findings"""
        
        findings_text = "\n".join([
            f"- {f.get('fact', 'Unknown')} (Source: {f.get('source_title', 'Unknown')})"
            for f in findings
        ])
        
        prompt = f"""
        Summarize these research findings in relation to the objective.
        
        Objective: {objective}
        
        Findings:
        {findings_text}
        
        Create a concise summary (2-3 paragraphs) that:
        1. Addresses the main objective
        2. Highlights the most important findings
        3. Notes any gaps or limitations
        """
        
        summary = await self._call_llm(prompt, max_tokens=1000)
        return summary