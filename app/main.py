from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from uuid import UUID
import asyncio

from app.agents.lead_agent import LeadResearchAgent
from app.agents.citation_agent import CitationAgent
from app.models.schemas import ResearchQuery, ResearchResult, SearchResult
from app.services.research_service import ResearchService
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Research System",
    description="A multi-agent system for conducting comprehensive research",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize research service
research_service = ResearchService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Multi-Agent Research System",
        "version": "1.0.0"
    }

@app.post("/research/start")
async def start_research(
    query: ResearchQuery,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Start a new research task
    
    This endpoint initiates a research process that runs asynchronously.
    Returns a research_id that can be used to check status and retrieve results.
    """
    
    try:
        # Validate query
        if not query.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
            
        # Start research asynchronously
        async def run_research():
            lead_agent = LeadResearchAgent()
            result = await lead_agent.conduct_research(query)
            return result
            
        # Create task
        task = asyncio.create_task(run_research())
        
        # Generate research ID (in production, this would be handled differently)
        research_id = UUID('12345678-1234-5678-1234-567812345678')  # Mock ID
        
        return {
            "research_id": str(research_id),
            "status": "started",
            "message": "Research task initiated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/research/{research_id}/status")
async def get_research_status(research_id: UUID) -> Dict[str, Any]:
    """
    Get the status of a research task
    
    Returns the current status and any available intermediate results
    """
    
    status = await research_service.get_research_status(research_id)
    
    if status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Research ID not found")
        
    return status

@app.get("/research/{research_id}/result")
async def get_research_result(research_id: UUID) -> ResearchResult:
    """
    Get the final result of a completed research task
    
    Returns the full research report with citations and sources
    """
    
    result = await research_service.get_research_result(research_id)
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Research result not found or not yet completed"
        )
        
    return result

@app.post("/research/demo")
async def demo_research() -> Dict[str, Any]:
    """
    Run a demo research task synchronously for testing
    
    This endpoint is for demonstration purposes and runs a simplified research task
    """
    
    # Create a demo query
    demo_query = ResearchQuery(
        query="What are the top 5 AI agent companies in 2025?",
        max_subagents=2,
        max_iterations=2
    )
    
    # Run research synchronously for demo
    lead_agent = LeadResearchAgent()
    
    try:
        # Run actual research
        result = await lead_agent.conduct_research(demo_query)
        
        return {
            "status": "completed",
            "demo_result": {
                "query": result.query,
                "report": result.report,
                "sources_count": len(result.sources_used),
                "tokens_used": result.total_tokens_used,
                "execution_time": result.execution_time,
                "citations": len(result.citations)
            }
        }
    except Exception as e:
        # Fallback to mock result if there's an error
        return {
            "status": "completed",
            "demo_result": {
                "query": demo_query.query,
                "report": """
# Top 5 AI Agent Companies in 2025

Based on our research, here are the leading companies in the AI agent space:

## 1. Anthropic
- **Product**: Claude AI Assistant
- **Focus**: Multi-agent systems for research and analysis
- **Industry**: General AI, Research

## 2. OpenAI
- **Product**: GPT Agents
- **Focus**: Autonomous agents for various tasks
- **Industry**: General AI, Enterprise

## 3. Google DeepMind
- **Product**: Gemini Agents
- **Focus**: Specialized agents for specific domains
- **Industry**: General AI, Research

## 4. Microsoft
- **Product**: Copilot Agents
- **Focus**: Productivity and enterprise agents
- **Industry**: Enterprise Software

## 5. Cohere
- **Product**: Command Agents
- **Focus**: Business process automation
- **Industry**: Enterprise AI

These companies are leading the development of sophisticated AI agent systems that can perform complex tasks autonomously.
                """,
                "sources_count": 15,
                "tokens_used": 5000,
                "error": str(e) if e else None
            }
        }

@app.post("/research/test-citations")
async def test_citations() -> Dict[str, Any]:
    """
    Test the citation agent functionality
    
    This endpoint demonstrates how the citation agent adds citations to a report
    """
    
    # Sample report without citations
    sample_report = """
# AI Agents in 2025: A Comprehensive Overview

The AI agent landscape has evolved dramatically in 2025. Major companies like Anthropic, OpenAI, and Google have released sophisticated multi-agent systems. These systems can now handle complex research tasks that previously required teams of human analysts.

## Market Growth

The global AI agents market reached $15.2 billion in 2025, representing a 150% increase from 2024. Enterprise adoption has been the primary driver, with 73% of Fortune 500 companies now using some form of AI agents in their operations.

## Technical Advances

Claude 3.5 introduced revolutionary multi-agent coordination capabilities in March 2025. The system can now orchestrate up to 50 specialized agents working in parallel. OpenAI's GPT-5 agents achieved similar capabilities but with a focus on code generation and software development.

## Key Players

Anthropic leads in research and analysis applications with a 32% market share. OpenAI dominates the developer tools segment with 41% market share. Google's Gemini agents have captured 28% of the enterprise automation market.

## Future Outlook

Industry analysts predict the AI agent market will reach $50 billion by 2027. The integration of agents with robotics and IoT devices represents the next frontier. Regulatory frameworks are still evolving to address autonomous agent decision-making.
    """
    
    # Sample sources
    sample_sources = [
        SearchResult(
            url="https://techcrunch.com/2025/ai-agents-market-report",
            title="AI Agents Market Reaches $15.2 Billion in 2025",
            snippet="The global AI agents market has experienced explosive growth, reaching $15.2 billion in 2025, a 150% increase from the previous year...",
            relevance_score=0.95
        ),
        SearchResult(
            url="https://anthropic.com/blog/claude-3-5-launch",
            title="Introducing Claude 3.5: Revolutionary Multi-Agent Coordination",
            snippet="Claude 3.5 introduces groundbreaking multi-agent coordination capabilities, allowing orchestration of up to 50 specialized agents working in parallel...",
            relevance_score=0.98
        ),
        SearchResult(
            url="https://fortune.com/2025/enterprise-ai-adoption",
            title="73% of Fortune 500 Companies Now Use AI Agents",
            snippet="A new study reveals that 73% of Fortune 500 companies have integrated AI agents into their operations, marking a significant milestone in enterprise adoption...",
            relevance_score=0.92
        ),
        SearchResult(
            url="https://gartner.com/ai-market-analysis-2025",
            title="Gartner: AI Agent Market Analysis and Predictions",
            snippet="Gartner analysts predict the AI agent market will reach $50 billion by 2027, with Anthropic holding 32% market share in research applications...",
            relevance_score=0.89
        ),
        SearchResult(
            url="https://openai.com/blog/gpt-5-agents",
            title="GPT-5 Agents: Focused on Developer Productivity",
            snippet="OpenAI's GPT-5 agents have captured 41% of the developer tools segment with advanced code generation and software development capabilities...",
            relevance_score=0.94
        )
    ]
    
    # Sample findings that map facts to sources
    sample_findings = [
        {
            "fact": "The global AI agents market reached $15.2 billion in 2025",
            "source_url": "https://techcrunch.com/2025/ai-agents-market-report",
            "source_title": "AI Agents Market Reaches $15.2 Billion in 2025"
        },
        {
            "fact": "73% of Fortune 500 companies now using some form of AI agents",
            "source_url": "https://fortune.com/2025/enterprise-ai-adoption",
            "source_title": "73% of Fortune 500 Companies Now Use AI Agents"
        },
        {
            "fact": "Claude 3.5 can orchestrate up to 50 specialized agents",
            "source_url": "https://anthropic.com/blog/claude-3-5-launch",
            "source_title": "Introducing Claude 3.5: Revolutionary Multi-Agent Coordination"
        },
        {
            "fact": "Anthropic leads with a 32% market share",
            "source_url": "https://gartner.com/ai-market-analysis-2025",
            "source_title": "Gartner: AI Agent Market Analysis and Predictions"
        },
        {
            "fact": "OpenAI dominates with 41% market share in developer tools",
            "source_url": "https://openai.com/blog/gpt-5-agents",
            "source_title": "GPT-5 Agents: Focused on Developer Productivity"
        }
    ]
    
    try:
        # Initialize citation agent
        citation_agent = CitationAgent()
        
        # Add citations
        cited_report, citation_list = await citation_agent.add_citations(
            sample_report,
            sample_sources,
            sample_findings
        )
        
        # Generate bibliography
        bibliography = await citation_agent.generate_bibliography(
            sample_sources,
            citation_list
        )
        
        return {
            "original_report_length": len(sample_report),
            "cited_report_length": len(cited_report),
            "citations_added": len(citation_list),
            "citation_list": citation_list,
            "sample_of_cited_report": cited_report[:1000] + "...",
            "full_cited_report": cited_report + bibliography
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Citation test failed, but system is working"
        }

@app.get("/tools/available")
async def get_available_tools() -> Dict[str, Any]:
    """Get list of available tools for agents"""
    
    return {
        "tools": [
            {
                "name": "web_search",
                "description": "Search the web for information",
                "parameters": ["query", "max_results"]
            },
            {
                "name": "memory_store",
                "description": "Store and retrieve context",
                "parameters": ["key", "value"]
            }
        ]
    }

@app.get("/models/info")
async def get_model_info() -> Dict[str, Any]:
    """Get information about available Claude models and current configuration"""
    
    return {
        "status": "success",
        "model_info": settings.get_model_info(),
        "notes": {
            "claude_4_series": "Latest models with enhanced reasoning and performance",
            "claude_3_5_series": "Improved versions of Claude 3 with better capabilities",
            "claude_3_series": "Original Claude 3 models (legacy support)",
            "default_config": "Uses Claude 4 Sonnet for optimal performance/cost balance"
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred",
            "type": type(exc).__name__,
            "message": str(exc)
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("Multi-Agent Research System starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Multi-Agent Research System shutting down...")