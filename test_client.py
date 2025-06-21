import asyncio
import httpx
import json
from app.models.schemas import ResearchQuery, SubAgentTask, SearchResult
from app.agents.lead_agent import LeadResearchAgent
from app.agents.search_agent import SearchSubAgent
from app.agents.citation_agent import CitationAgent


async def test_full_research_pipeline():
    """Test the complete multi-agent research pipeline"""
    
    print("=== Testing Multi-Agent Research System ===\n")
    
    # 1. Test Citation Agent independently
    print("1. Testing Citation Agent...")
    
    citation_agent = CitationAgent()
    
    test_report = """
    Recent studies show that AI adoption in healthcare has increased by 45% in 2025.
    Major hospitals are using AI for diagnosis, with accuracy rates reaching 94%.
    The FDA has approved 23 new AI-powered medical devices this year.
    """
    
    test_sources = [
        SearchResult(
            url="https://healthtech.com/ai-adoption-2025",
            title="Healthcare AI Adoption Surges 45% in 2025",
            snippet="A comprehensive study reveals that AI adoption in healthcare has increased by 45% in 2025...",
            relevance_score=0.95
        ),
        SearchResult(
            url="https://fda.gov/ai-medical-devices-2025",
            title="FDA Approves 23 AI-Powered Medical Devices in 2025",
            snippet="The FDA has approved 23 new AI-powered medical devices this year, marking a significant milestone...",
            relevance_score=0.93
        )
    ]
    
    try:
        cited_report, citations = await citation_agent.add_citations(test_report, test_sources)
        print(f"✓ Citation Agent added {len(citations)} citations\n")
    except Exception as e:
        print(f"✗ Citation Agent failed: {e}\n")
    
    # 2. Test Search Subagent
    print("2. Testing Search Subagent...")
    
    test_task = SubAgentTask(
        objective="Find information about AI agents in healthcare",
        search_focus="AI medical diagnosis accuracy statistics 2025",
        expected_output_format="List of statistics with sources"
    )
    
    try:
        search_agent = SearchSubAgent(test_task.task_id)
        result = await search_agent.execute_task(test_task)
        
        print(f"✓ Search Agent found {len(result.sources)} sources")
        print(f"✓ Extracted {len(result.findings)} findings\n")
    except Exception as e:
        print(f"✗ Search Agent failed: {e}\n")
    
    # 3. Test Full Pipeline
    print("3. Testing Complete Research Pipeline...")
    
    research_query = ResearchQuery(
        query="What are the latest breakthroughs in AI-powered medical diagnosis in 2025?",
        max_subagents=2,
        max_iterations=2
    )
    
    try:
        lead_agent = LeadResearchAgent()
        research_result = await lead_agent.conduct_research(research_query)
        
        print(f"✓ Research completed!")
        print(f"✓ Total tokens used: {research_result.total_tokens_used}")
        print(f"✓ Sources found: {len(research_result.sources_used)}")
        print(f"✓ Report length: {len(research_result.report)} characters")
        
        # Show a sample of the report with citations
        print("\n=== Sample of Final Report ===")
        print(research_result.report[:500] + "...")
        
        # Check that citations were added
        citation_pattern = r'\[\d+\]'
        import re
        citations_found = len(re.findall(citation_pattern, research_result.report))
        print(f"\n✓ Citations in report: {citations_found}")
        
    except Exception as e:
        print(f"✗ Full pipeline failed: {e}")
    
    print("\n=== Test Complete ===")


async def test_api_endpoints():
    """Test the API endpoints"""
    
    print("\n=== Testing API Endpoints ===\n")
    
    base_url = "http://localhost:12000"
    
    async with httpx.AsyncClient() as client:
        # Test health check
        try:
            response = await client.get(f"{base_url}/")
            print(f"✓ Health check: {response.status_code}")
            print(f"  Response: {response.json()}")
        except Exception as e:
            print(f"✗ Health check failed: {e}")
        
        # Test demo endpoint
        try:
            response = await client.post(f"{base_url}/research/demo")
            print(f"✓ Demo endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Demo completed with {data['demo_result']['sources_count']} sources")
        except Exception as e:
            print(f"✗ Demo endpoint failed: {e}")
        
        # Test citation endpoint
        try:
            response = await client.post(f"{base_url}/research/test-citations")
            print(f"✓ Citation test: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Added {data.get('citations_added', 0)} citations")
        except Exception as e:
            print(f"✗ Citation test failed: {e}")


if __name__ == "__main__":
    # Run the tests
    print("Starting Multi-Agent Research System Tests...\n")
    
    # Test the core pipeline
    asyncio.run(test_full_research_pipeline())
    
    # Test API endpoints (requires server to be running)
    print("\nTo test API endpoints, start the server with 'python run.py' and run:")
    print("asyncio.run(test_api_endpoints())")