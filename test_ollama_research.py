#!/usr/bin/env python3
"""
Test script for Ollama integration with the research system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.schemas import ResearchQuery
from app.agents.lead_agent import LeadResearchAgent
from app.core.config import settings


async def test_ollama_research():
    """Test a complete research workflow using Ollama models"""
    
    print("🔬 Testing Ollama Research Integration")
    print("=" * 50)
    
    # Configure to use Ollama models
    os.environ["LEAD_AGENT_MODEL"] = "llama3.2:3b"
    os.environ["SUBAGENT_MODEL"] = "llama3.2:3b"
    os.environ["CITATION_MODEL"] = "llama3.2:3b"
    
    # Reload settings to pick up environment changes
    from importlib import reload
    from app.core import config
    reload(config)
    
    print(f"Lead Agent Model: {config.settings.LEAD_AGENT_MODEL}")
    print(f"Subagent Model: {config.settings.SUBAGENT_MODEL}")
    print(f"Citation Model: {config.settings.CITATION_MODEL}")
    print()
    
    # Create a simple research query
    query = ResearchQuery(
        query="What are the benefits of using local AI models?",
        max_subagents=1,  # Keep it simple for testing
        max_iterations=1
    )
    
    print(f"Research Query: {query.query}")
    print(f"Max Subagents: {query.max_subagents}")
    print(f"Max Iterations: {query.max_iterations}")
    print()
    
    try:
        # Create lead agent
        lead_agent = LeadResearchAgent()
        
        print("🤖 Starting research with Ollama models...")
        
        # Conduct research
        result = await lead_agent.conduct_research(query)
        
        print("✅ Research completed successfully!")
        print()
        print("📊 Results:")
        print(f"  • Total tokens used: {result.total_tokens_used}")
        print(f"  • Sources found: {len(result.sources_used)}")
        print(f"  • Execution time: {result.execution_time:.2f} seconds")
        print(f"  • Report length: {len(result.report)} characters")
        print()
        
        print("📝 Sample of Report:")
        print("-" * 40)
        print(result.report[:500] + "..." if len(result.report) > 500 else result.report)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Research failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mixed_provider_research():
    """Test research using mixed providers (if Anthropic is available)"""
    
    print("\n🔀 Testing Mixed Provider Research")
    print("=" * 50)
    
    # Check if Anthropic is available
    if not settings.ANTHROPIC_API_KEY:
        print("⚠️  Skipping mixed provider test - no Anthropic API key")
        return True
    
    # Configure mixed providers
    os.environ["LEAD_AGENT_MODEL"] = "claude-4-sonnet-20241120"  # Anthropic
    os.environ["SUBAGENT_MODEL"] = "llama3.2:3b"  # Ollama
    os.environ["CITATION_MODEL"] = "llama3.2:3b"  # Ollama
    
    # Reload settings
    from importlib import reload
    from app.core import config
    reload(config)
    
    print(f"Lead Agent Model: {config.settings.LEAD_AGENT_MODEL} (Anthropic)")
    print(f"Subagent Model: {config.settings.SUBAGENT_MODEL} (Ollama)")
    print(f"Citation Model: {config.settings.CITATION_MODEL} (Ollama)")
    print()
    
    query = ResearchQuery(
        query="Compare local vs cloud AI models",
        max_subagents=1,
        max_iterations=1
    )
    
    try:
        lead_agent = LeadResearchAgent()
        
        print("🤖 Starting mixed provider research...")
        
        result = await lead_agent.conduct_research(query)
        
        print("✅ Mixed provider research completed!")
        print(f"  • Total tokens used: {result.total_tokens_used}")
        print(f"  • Execution time: {result.execution_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Mixed provider research failed: {e}")
        return False


async def main():
    """Main test function"""
    
    print("🚀 Ollama Research Integration Test")
    print("=" * 60)
    
    # Test 1: Pure Ollama research
    ollama_success = await test_ollama_research()
    
    # Test 2: Mixed provider research (if possible)
    mixed_success = await test_mixed_provider_research()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 40)
    
    if ollama_success:
        print("✅ Ollama research: SUCCESS")
    else:
        print("❌ Ollama research: FAILED")
    
    if mixed_success:
        print("✅ Mixed provider research: SUCCESS")
    else:
        print("⚠️  Mixed provider research: SKIPPED/FAILED")
    
    overall_success = ollama_success
    
    if overall_success:
        print("\n🎉 Ollama integration is working correctly!")
        print("   You can now use local models for research tasks.")
        print("   Benefits:")
        print("   • No API costs")
        print("   • Complete data privacy")
        print("   • No internet dependency")
        print("   • Customizable model selection")
    else:
        print("\n❌ Ollama integration has issues")
        print("   Check the error messages above for details")
    
    return overall_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)