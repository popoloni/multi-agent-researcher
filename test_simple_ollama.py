#!/usr/bin/env python3
"""
Simple test for Ollama integration
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.model_providers import model_manager
from app.agents.base_agent import BaseAgent


class SimpleTestAgent(BaseAgent):
    def __init__(self):
        super().__init__("llama3.2:3b", "Simple Test Agent")
        
    def get_system_prompt(self) -> str:
        return "You are a helpful assistant. Respond briefly and clearly."


async def test_simple_ollama():
    """Test basic Ollama functionality"""
    
    print("🧪 Simple Ollama Test")
    print("=" * 30)
    
    try:
        # Test 1: Direct model call
        print("1. Testing direct model call...")
        response, tokens = await model_manager.call_model(
            model="llama3.2:3b",
            messages=[{"role": "user", "content": "Say 'Hello from Ollama' and nothing else."}],
            system_prompt="You are a helpful assistant.",
            max_tokens=20
        )
        print(f"   ✅ Response: {response}")
        print(f"   ✅ Tokens: {tokens}")
        
        # Test 2: Agent-based call
        print("\n2. Testing agent-based call...")
        agent = SimpleTestAgent()
        agent_response = await agent._call_llm("What is 2+2? Answer with just the number.", max_tokens=10)
        print(f"   ✅ Agent response: {agent_response}")
        print(f"   ✅ Agent tokens: {agent.total_tokens}")
        
        print("\n✅ All tests passed! Ollama integration is working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


async def main():
    success = await test_simple_ollama()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)