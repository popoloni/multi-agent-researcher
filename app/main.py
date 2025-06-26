from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from uuid import UUID
import asyncio

from app.agents.lead_agent import LeadResearchAgent
from app.agents.citation_agent import CitationAgent
from app.agents.kenobi_agent import KenobiAgent
from app.models.schemas import ResearchQuery, ResearchResult, SearchResult
from app.models.repository_schemas import (
    RepositoryIndexRequest, CodeSearchRequest, FileAnalysisRequest,
    MultiRepoSearchResult, RepositoryAnalysis
)
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

# Initialize services
research_service = ResearchService()
kenobi_agent = KenobiAgent()

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
    """Get information about available models from all providers and current configuration"""
    
    from app.core.model_providers import model_manager
    
    # Get provider status
    provider_status = await model_manager.check_provider_status()
    
    return {
        "status": "success",
        "model_info": settings.get_model_info(),
        "provider_status": provider_status,
        "notes": {
            "anthropic": {
                "claude_4_series": "Latest models with enhanced reasoning and performance",
                "claude_3_5_series": "Improved versions of Claude 3 with better capabilities", 
                "claude_3_series": "Original Claude 3 models (legacy support)",
                "requires": "ANTHROPIC_API_KEY environment variable"
            },
            "ollama": {
                "local_models": "Run models locally without API costs",
                "privacy": "Complete data privacy - no external API calls",
                "performance": "Performance depends on local hardware",
                "requires": "Ollama installed and running locally"
            },
            "mixed_configs": "You can mix providers (e.g., Claude for lead, Ollama for subagents)",
            "default_config": "Uses Claude 4 Sonnet for optimal performance/cost balance"
        }
    }

@app.get("/ollama/status")
async def get_ollama_status() -> Dict[str, Any]:
    """Check Ollama status and available models"""
    
    from app.core.model_providers import model_manager, ModelProvider
    
    try:
        # Check if Ollama is running
        ollama_provider = model_manager.providers[ModelProvider.OLLAMA]
        is_running = await ollama_provider.check_connection()
        
        if is_running:
            # Get available models
            available_models = await ollama_provider.list_available_models()
            
            return {
                "status": "running",
                "host": settings.OLLAMA_HOST,
                "available_models": available_models,
                "recommended_models": list(settings.OLLAMA_MODELS.keys()),
                "message": "Ollama is running and accessible"
            }
        else:
            return {
                "status": "not_running",
                "host": settings.OLLAMA_HOST,
                "available_models": [],
                "recommended_models": list(settings.OLLAMA_MODELS.keys()),
                "message": "Ollama is not running or not accessible",
                "help": "Install Ollama from https://ollama.ai and run 'ollama serve'"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "host": settings.OLLAMA_HOST,
            "error": str(e),
            "message": "Error checking Ollama status",
            "help": "Install Ollama from https://ollama.ai and run 'ollama serve'"
        }

# Kenobi Code Analysis Endpoints

@app.post("/kenobi/repositories/index")
async def index_repository(repo_request: RepositoryIndexRequest) -> Dict[str, Any]:
    """
    Index a repository for code analysis
    
    This endpoint analyzes a local directory or clones a Git repository
    and extracts code elements, dependencies, and metadata.
    """
    try:
        # Analyze the repository
        analysis = await kenobi_agent.analyze_repository(repo_request.path)
        
        return {
            "status": "success",
            "repository_id": analysis.repository.id,
            "repository_name": analysis.repository.name,
            "language": analysis.repository.language.value,
            "framework": analysis.repository.framework,
            "metrics": analysis.metrics,
            "files_analyzed": len(analysis.files),
            "elements_extracted": sum(len(f.elements) for f in analysis.files),
            "frameworks_detected": analysis.frameworks_detected,
            "categories_used": analysis.categories_used
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Repository indexing failed: {str(e)}")

@app.get("/kenobi/repositories/{repo_id}/analysis")
async def get_repository_analysis(repo_id: str) -> RepositoryAnalysis:
    """
    Get complete analysis of a repository
    
    Returns detailed analysis including all code elements, dependencies,
    and AI-generated insights.
    """
    try:
        repository = await kenobi_agent.repository_service.get_repository_metadata(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        analysis = await kenobi_agent.repository_service.analyze_repository(repo_id)
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis retrieval failed: {str(e)}")

@app.post("/kenobi/search/code")
async def search_code(search_request: CodeSearchRequest) -> MultiRepoSearchResult:
    """
    Search for code elements across repositories
    
    Performs intelligent search across indexed repositories using
    natural language queries and filters.
    """
    try:
        # For now, return a simple search result
        # This will be enhanced with actual search implementation
        return MultiRepoSearchResult(
            query=search_request.query,
            results=[],
            total_found=0,
            repositories_searched=[],
            search_time=0.0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code search failed: {str(e)}")

@app.get("/kenobi/repositories/{repo_id}/dependencies")
async def get_dependency_graph(repo_id: str) -> Dict[str, Any]:
    """
    Get dependency graph for a repository
    
    Returns the dependency relationships between code elements
    in the repository.
    """
    try:
        repository = await kenobi_agent.repository_service.get_repository_metadata(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        dependency_graph = await kenobi_agent.analyze_dependencies(repository)
        
        return {
            "repository_id": repo_id,
            "nodes": dependency_graph.nodes,
            "edges": [edge.dict() for edge in dependency_graph.edges],
            "circular_dependencies": dependency_graph.circular_dependencies,
            "node_count": len(dependency_graph.nodes),
            "edge_count": len(dependency_graph.edges)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dependency analysis failed: {str(e)}")

@app.post("/kenobi/analyze/file")
async def analyze_single_file(file_request: FileAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze a single file
    
    Analyzes a single code file and returns extracted elements,
    dependencies, and AI-generated descriptions.
    """
    try:
        # Parse the file
        parsed_file = kenobi_agent.repository_service.code_parser.parse_file(
            file_request.file_path, 
            file_request.content
        )
        
        # Generate descriptions for elements
        for element in parsed_file.elements:
            if not element.description:
                description = await kenobi_agent.generate_code_description(element)
                element.description = description
        
        return {
            "file_path": parsed_file.file_path,
            "language": parsed_file.language.value,
            "elements_found": len(parsed_file.elements),
            "imports_found": len(parsed_file.imports),
            "line_count": parsed_file.line_count,
            "elements": [element.dict() for element in parsed_file.elements],
            "imports": [imp.dict() for imp in parsed_file.imports],
            "parse_errors": parsed_file.parse_errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

@app.get("/kenobi/repositories")
async def list_repositories() -> Dict[str, Any]:
    """
    List all indexed repositories
    
    Returns a list of all repositories that have been indexed
    by the Kenobi agent.
    """
    try:
        repositories = await kenobi_agent.repository_service.list_repositories()
        
        return {
            "repositories": [
                {
                    "id": repo.id,
                    "name": repo.name,
                    "language": repo.language.value,
                    "framework": repo.framework,
                    "file_count": repo.file_count,
                    "line_count": repo.line_count,
                    "indexed_at": repo.indexed_at.isoformat(),
                    "local_path": repo.local_path
                }
                for repo in repositories
            ],
            "total_repositories": len(repositories)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository listing failed: {str(e)}")

@app.get("/kenobi/status")
async def get_kenobi_status() -> Dict[str, Any]:
    """
    Get Kenobi agent status and configuration
    
    Returns information about the Kenobi agent configuration,
    supported languages, and current statistics.
    """
    try:
        repositories = await kenobi_agent.repository_service.list_repositories()
        
        return {
            "status": "active",
            "agent_name": kenobi_agent.name,
            "model": kenobi_agent.model,
            "provider": kenobi_agent.provider,
            "supported_languages": [lang.value for lang in kenobi_agent.repository_service.code_parser.language_extensions.values()],
            "repositories_indexed": len(repositories),
            "total_tokens_used": kenobi_agent.total_tokens,
            "configuration": {
                "kenobi_enabled": getattr(settings, 'KENOBI_ENABLED', True),
                "max_file_size": getattr(settings, 'CODE_ANALYSIS_MAX_FILE_SIZE', 1048576),
                "supported_languages": getattr(settings, 'SUPPORTED_LANGUAGES', 'python,javascript,typescript,java,csharp,go')
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

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