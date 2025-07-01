#!/usr/bin/env python3

"""
Test script to check the research result content
"""

import asyncio
import sys
import os
from uuid import UUID

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.models.schemas import ResearchQuery
from app.services.research_service import ResearchService

async def test_research_result():
    """Test a research query and show the result"""
    
    print("=== Research Result Test ===")
    print()
    
    research_service = ResearchService()
    
    # Create a simple research query
    query = ResearchQuery(
        query="What are the main benefits of artificial intelligence?",
        max_subagents=1,
        max_iterations=1
    )
    
    print(f"Query: {query.query}")
    print("Starting research...")
    
    # Start research
    research_id = await research_service.start_research(query)
    print(f"Research ID: {research_id}")
    
    # Wait for completion
    max_wait = 30
    wait_time = 0
    
    while wait_time < max_wait:
        status = await research_service.get_research_status(research_id)
        current_status = status.get('status', 'unknown')
        
        print(f"[{wait_time}s] Status: {current_status}")
        
        if current_status in ['completed', 'failed']:
            break
            
        await asyncio.sleep(2)
        wait_time += 2
    
    # Get the final result
    if current_status == 'completed':
        result = await research_service.get_research_result(research_id)
        
        if result:
            print("\n" + "="*60)
            print("RESEARCH RESULT:")
            print("="*60)
            print(f"Query: {result.query}")
            print(f"Execution Time: {result.execution_time:.2f} seconds")
            print(f"Total Tokens: {result.total_tokens_used}")
            print(f"Sources Used: {len(result.sources_used)}")
            print(f"Citations: {len(result.citations)}")
            print("\nREPORT:")
            print("-" * 40)
            print(result.report)
            print("-" * 40)
            
            if result.citations:
                print("\nCITATIONS:")
                for i, citation in enumerate(result.citations, 1):
                    print(f"[{i}] {citation.title} - {citation.url}")
                    
        else:
            print("❌ No result found")
    else:
        print(f"❌ Research failed with status: {current_status}")

if __name__ == "__main__":
    asyncio.run(test_research_result())