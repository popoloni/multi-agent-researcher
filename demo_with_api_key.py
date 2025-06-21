"""
Demo script showing how to use the Multi-Agent Research System with a real API key.

To use this script:
1. Set your ANTHROPIC_API_KEY in the .env file
2. Run: python demo_with_api_key.py
"""

import asyncio
import os
from dotenv import load_dotenv
from app.models.schemas import ResearchQuery
from app.agents.lead_agent import LeadResearchAgent

# Load environment variables
load_dotenv()

async def run_research_demo():
    """Run a complete research demo"""
    
    # Check if API key is available
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ Please set your ANTHROPIC_API_KEY in the .env file")
        print("   Get your API key from: https://console.anthropic.com/")
        return
    
    print("🚀 Starting Multi-Agent Research Demo")
    print("=" * 50)
    
    # Create research query
    query = ResearchQuery(
        query="What are the latest developments in multi-agent AI systems in 2025?",
        max_subagents=3,
        max_iterations=3
    )
    
    print(f"📋 Research Query: {query.query}")
    print(f"🤖 Max Subagents: {query.max_subagents}")
    print(f"🔄 Max Iterations: {query.max_iterations}")
    print()
    
    try:
        # Initialize lead agent
        lead_agent = LeadResearchAgent()
        
        print("🧠 Lead Agent initialized")
        print("⏳ Starting research process...")
        print()
        
        # Conduct research
        result = await lead_agent.conduct_research(query)
        
        # Display results
        print("✅ Research completed successfully!")
        print("=" * 50)
        print(f"📊 Execution Time: {result.execution_time:.2f} seconds")
        print(f"🔢 Total Tokens Used: {result.total_tokens_used:,}")
        print(f"🤖 Subagents Used: {result.subagent_count}")
        print(f"📚 Sources Found: {len(result.sources_used)}")
        print(f"📝 Citations Added: {len(result.citations)}")
        print(f"📑 Report Sections: {len(result.report_sections)}")
        print()
        
        print("📋 Report Sections:")
        for i, section in enumerate(result.report_sections, 1):
            print(f"  {i}. {section}")
        print()
        
        print("🔗 Top Sources:")
        for i, source in enumerate(result.sources_used[:5], 1):
            print(f"  {i}. {source.title}")
            print(f"     {source.url}")
            print(f"     Relevance: {source.relevance_score:.2f}")
        print()
        
        print("📄 Report Preview (first 1000 characters):")
        print("-" * 50)
        print(result.report[:1000])
        if len(result.report) > 1000:
            print("...")
        print("-" * 50)
        
        # Save full report to file
        with open("research_report.md", "w") as f:
            f.write(result.report)
        print("💾 Full report saved to: research_report.md")
        
    except Exception as e:
        print(f"❌ Research failed: {e}")
        print("   This might be due to API rate limits or network issues")

if __name__ == "__main__":
    asyncio.run(run_research_demo())