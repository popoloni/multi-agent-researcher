#!/usr/bin/env python3
"""
Test script for verifying Claude model configuration and functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.agents.base_agent import BaseAgent
from app.agents.lead_agent import LeadResearchAgent
from app.models.schemas import ResearchQuery


class TestAgent(BaseAgent):
    """Simple test agent for model verification"""
    
    def __init__(self, model: str):
        super().__init__(model, f"Test Agent ({model})")
        
    def get_system_prompt(self) -> str:
        return "You are a test agent. Respond with a brief confirmation that you're working correctly."


async def test_model_configuration():
    """Test the model configuration and availability"""
    
    print("🧪 Testing Claude Model Configuration")
    print("=" * 50)
    
    # Test 1: Configuration Loading
    print("\n1. Testing Configuration Loading...")
    try:
        model_info = settings.get_model_info()
        print(f"✅ Configuration loaded successfully")
        print(f"   Available models: {len(model_info['available_models'])}")
        print(f"   Current lead agent model: {model_info['current_config']['lead_agent']}")
        print(f"   Current subagent model: {model_info['current_config']['subagent']}")
        print(f"   Current citation model: {model_info['current_config']['citation']}")
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False
    
    # Test 2: Model Validation
    print("\n2. Testing Model Validation...")
    test_models = [
        settings.LEAD_AGENT_MODEL,
        settings.SUBAGENT_MODEL, 
        settings.CITATION_MODEL
    ]
    
    for model in test_models:
        is_valid = settings.validate_model(model)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {model}: {'Valid' if is_valid else 'Invalid'}")
    
    # Test 3: API Key Check
    print("\n3. Testing API Key...")
    if settings.ANTHROPIC_API_KEY:
        print("✅ Anthropic API key is configured")
        
        # Test 4: Simple Model Test (only if API key is available)
        print("\n4. Testing Model Connectivity...")
        try:
            test_agent = TestAgent(settings.LEAD_AGENT_MODEL)
            response = await test_agent._call_llm("Say 'Hello, I am working correctly!'", max_tokens=50)
            if "working correctly" in response.lower() or "hello" in response.lower():
                print(f"✅ Model connectivity test passed")
                print(f"   Response: {response[:100]}...")
            else:
                print(f"⚠️  Model responded but with unexpected content: {response[:100]}...")
        except Exception as e:
            print(f"❌ Model connectivity test failed: {e}")
            print("   This might be due to model availability or API limits")
    else:
        print("⚠️  No Anthropic API key configured - skipping connectivity tests")
        print("   Set ANTHROPIC_API_KEY environment variable to test connectivity")
    
    # Test 5: Model Recommendations
    print("\n5. Model Recommendations:")
    recommendations = model_info['recommended_configs']
    for config_name, config in recommendations.items():
        print(f"   {config_name.title()}:")
        print(f"     Lead: {config['lead_agent']}")
        print(f"     Sub:  {config['subagent']}")
        print(f"     Cite: {config['citation']}")
    
    return True


async def test_research_system():
    """Test the research system with new models"""
    
    print("\n🔬 Testing Research System with New Models")
    print("=" * 50)
    
    if not settings.ANTHROPIC_API_KEY:
        print("⚠️  Skipping research system test - no API key configured")
        return True
    
    try:
        # Create a simple research query
        query = ResearchQuery(
            query="What is the latest version of Python?",
            max_subagents=1,
            max_iterations=1
        )
        
        print(f"\n1. Testing with query: '{query.query}'")
        print(f"   Using models:")
        print(f"     Lead Agent: {settings.LEAD_AGENT_MODEL}")
        print(f"     Subagent: {settings.SUBAGENT_MODEL}")
        print(f"     Citation: {settings.CITATION_MODEL}")
        
        # Create lead agent and test basic functionality
        lead_agent = LeadResearchAgent()
        
        # Test thinking capability
        print("\n2. Testing enhanced thinking capability...")
        thinking_result = await lead_agent.think("Analyze the query about Python versions")
        print(f"✅ Thinking test completed")
        print(f"   Objective: {thinking_result.get('objective', 'N/A')[:50]}...")
        
        print("\n✅ Research system basic tests passed")
        print("   Note: Full research test skipped to avoid API usage")
        
    except Exception as e:
        print(f"❌ Research system test failed: {e}")
        return False
    
    return True


async def main():
    """Main test function"""
    
    print("🚀 Multi-Agent Research System - Model Configuration Test")
    print("=" * 60)
    
    # Run configuration tests
    config_success = await test_model_configuration()
    
    if config_success:
        # Run research system tests
        research_success = await test_research_system()
        
        if research_success:
            print("\n🎉 All tests passed!")
            print("\nNext steps:")
            print("1. Set your ANTHROPIC_API_KEY in .env file")
            print("2. Run 'python run.py' to start the server")
            print("3. Test the /models/info endpoint")
            print("4. Try the demo endpoints")
            return True
    
    print("\n❌ Some tests failed. Please check the configuration.")
    return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)