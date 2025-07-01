#!/usr/bin/env python3

"""
Debug script to test the research system and identify issues
"""

import asyncio
import sys
import os
import traceback
from uuid import uuid4

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.models.schemas import ResearchQuery
from app.services.research_service import ResearchService
from app.core.config import settings

async def test_research_system():
    """Test the research system step by step"""
    
    print("=== Research System Debug Test ===")
    print()
    
    # Test 1: Configuration
    print("1. Testing Configuration...")
    print(f"   AI_PROVIDER: {settings.AI_PROVIDER}")
    print(f"   ANTHROPIC_API_KEY: {'set' if settings.ANTHROPIC_API_KEY else 'not set'}")
    print(f"   OLLAMA_HOST: {settings.OLLAMA_HOST}")
    print(f"   LEAD_AGENT_MODEL: {settings.LEAD_AGENT_MODEL}")
    print()
    
    # Test 2: Model Provider
    print("2. Testing Model Provider...")
    try:
        from app.core.model_providers import model_manager
        provider_status = await model_manager.check_provider_status()
        print(f"   Provider Status: {provider_status}")
        
        available_models = await model_manager.get_all_available_models()
        print(f"   Available Models: {available_models}")
    except Exception as e:
        print(f"   ERROR: {e}")
        traceback.print_exc()
    print()
    
    # Test 3: Research Service Initialization
    print("3. Testing Research Service...")
    try:
        research_service = ResearchService()
        print("   ✓ Research service initialized successfully")
    except Exception as e:
        print(f"   ERROR: {e}")
        traceback.print_exc()
        return
    print()
    
    # Test 4: Simple Research Query
    print("4. Testing Simple Research Query...")
    try:
        query = ResearchQuery(
            query="What is artificial intelligence?",
            max_subagents=1,
            max_iterations=1
        )
        
        print(f"   Query: {query.query}")
        print("   Starting research...")
        
        research_id = await research_service.start_research(query)
        print(f"   ✓ Research started with ID: {research_id}")
        
        # Wait a bit and check status
        await asyncio.sleep(2)
        
        status = await research_service.get_research_status(research_id)
        print(f"   Status: {status}")
        
        # Wait for completion or timeout
        max_wait = 30  # 30 seconds
        wait_time = 0
        
        while wait_time < max_wait:
            status = await research_service.get_research_status(research_id)
            current_status = status.get('status', 'unknown')
            
            print(f"   [{wait_time}s] Status: {current_status} - {status.get('message', 'No message')}")
            
            if current_status in ['completed', 'failed']:
                break
                
            await asyncio.sleep(2)
            wait_time += 2
        
        # Final status
        final_status = await research_service.get_research_status(research_id)
        print(f"   Final Status: {final_status}")
        
        if final_status.get('status') == 'completed':
            result = await research_service.get_research_result(research_id)
            if result:
                print(f"   ✓ Research completed successfully!")
                print(f"   Report length: {len(result.report) if result.report else 0} characters")
            else:
                print("   ⚠ Research completed but no result found")
        else:
            print(f"   ✗ Research failed or timed out")
            
    except Exception as e:
        print(f"   ERROR: {e}")
        traceback.print_exc()
    print()
    
    print("=== Debug Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_research_system())