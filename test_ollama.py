#!/usr/bin/env python3
"""
Test script for Ollama integration with the multi-agent research system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.model_providers import model_manager, ModelProvider
from app.agents.base_agent import BaseAgent
from app.models.schemas import ResearchQuery


class TestOllamaAgent(BaseAgent):
    """Simple test agent for Ollama verification"""
    
    def __init__(self, model: str):
        super().__init__(model, f"Test Ollama Agent ({model})")
        
    def get_system_prompt(self) -> str:
        return "You are a test agent. Respond briefly and clearly to confirm you're working correctly."


async def test_ollama_installation():
    """Test if Ollama is installed and running"""
    
    print("🔧 Testing Ollama Installation")
    print("=" * 40)
    
    try:
        ollama_provider = model_manager.providers[ModelProvider.OLLAMA]
        is_running = await ollama_provider.check_connection()
        
        if is_running:
            print("✅ Ollama is running and accessible")
            print(f"   Host: {settings.OLLAMA_HOST}")
            
            # Get available models
            available_models = await ollama_provider.list_available_models()
            print(f"   Available models: {len(available_models)}")
            
            if available_models:
                print("   Models:")
                for model in available_models[:5]:  # Show first 5
                    print(f"     - {model}")
                if len(available_models) > 5:
                    print(f"     ... and {len(available_models) - 5} more")
            else:
                print("   ⚠️  No models found. You may need to pull some models.")
                print("   Try: ollama pull llama3.2:3b")
                
            return True, available_models
            
        else:
            print("❌ Ollama is not running")
            print(f"   Host: {settings.OLLAMA_HOST}")
            print("   Help: Install Ollama from https://ollama.ai")
            print("   Then run: ollama serve")
            return False, []
            
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        print("   Help: Install Ollama from https://ollama.ai")
        return False, []


async def test_model_provider_system():
    """Test the model provider abstraction system"""
    
    print("\n🧪 Testing Model Provider System")
    print("=" * 40)
    
    # Test provider status
    provider_status = await model_manager.check_provider_status()
    
    print("Provider Status:")
    for provider, status in provider_status.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {provider}: {'Available' if status else 'Not available'}")
    
    # Test model classification
    print("\nModel Classification:")
    test_models = [
        "claude-4-sonnet-20241120",
        "llama3.1:8b", 
        "mistral:7b",
        "unknown-model"
    ]
    
    for model in test_models:
        provider = settings.get_provider_for_model(model)
        is_valid = settings.validate_model(model)
        print(f"  {model}: {provider} ({'valid' if is_valid else 'invalid'})")
    
    return provider_status


async def test_ollama_model_calls():
    """Test calling Ollama models directly"""
    
    print("\n🤖 Testing Ollama Model Calls")
    print("=" * 40)
    
    # Check if Ollama is available
    ollama_provider = model_manager.providers[ModelProvider.OLLAMA]
    is_running = await ollama_provider.check_connection()
    
    if not is_running:
        print("⚠️  Skipping model tests - Ollama not running")
        return False
    
    # Get available models
    available_models = await ollama_provider.list_available_models()
    
    if not available_models:
        print("⚠️  No models available for testing")
        print("   Try: ollama pull llama3.2:3b")
        return False
    
    # Test with the first available model
    test_model = available_models[0]
    print(f"Testing with model: {test_model}")
    
    try:
        # Create test agent
        test_agent = TestOllamaAgent(test_model)
        
        # Test simple call
        response = await test_agent._call_llm("Say 'Hello from Ollama!' and nothing else.", max_tokens=50)
        
        print(f"✅ Model response: {response[:100]}...")
        print(f"   Tokens used: {test_agent.total_tokens}")
        print(f"   Provider: {test_agent.provider}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False


async def test_mixed_provider_config():
    """Test using different providers for different agents"""
    
    print("\n🔀 Testing Mixed Provider Configuration")
    print("=" * 40)
    
    # Test different model configurations
    configs = [
        {
            "name": "All Anthropic",
            "lead": "claude-4-sonnet-20241120",
            "sub": "claude-4-sonnet-20241120", 
            "cite": "claude-3-5-haiku-20241022"
        },
        {
            "name": "All Ollama",
            "lead": "llama3.1:8b",
            "sub": "mistral:7b",
            "cite": "llama3.2:3b"
        },
        {
            "name": "Mixed (Claude + Ollama)",
            "lead": "claude-4-sonnet-20241120",
            "sub": "llama3.1:8b",
            "cite": "llama3.2:3b"
        }
    ]
    
    for config in configs:
        print(f"\n{config['name']}:")
        
        for role, model in [("Lead", config["lead"]), ("Sub", config["sub"]), ("Citation", config["cite"])]:
            provider = settings.get_provider_for_model(model)
            is_valid = settings.validate_model(model)
            
            status = "✅" if is_valid else "❌"
            print(f"  {status} {role}: {model} ({provider})")


async def test_ollama_installation_guide():
    """Provide installation guidance if Ollama is not available"""
    
    print("\n📋 Ollama Installation Guide")
    print("=" * 40)
    
    print("If Ollama is not installed or running:")
    print()
    print("1. Install Ollama:")
    print("   • Visit: https://ollama.ai")
    print("   • Download for your OS")
    print("   • Follow installation instructions")
    print()
    print("2. Start Ollama:")
    print("   ollama serve")
    print()
    print("3. Pull recommended models:")
    print("   ollama pull llama3.2:3b      # Lightweight (2GB)")
    print("   ollama pull llama3.1:8b      # Balanced (4.7GB)")
    print("   ollama pull mistral:7b       # Alternative (4.1GB)")
    print()
    print("4. Test the installation:")
    print("   ollama list")
    print("   ollama run llama3.2:3b")
    print()
    print("5. Configure the research system:")
    print("   export LEAD_AGENT_MODEL=llama3.1:8b")
    print("   export SUBAGENT_MODEL=mistral:7b")
    print("   export CITATION_MODEL=llama3.2:3b")


async def main():
    """Main test function"""
    
    print("🚀 Multi-Agent Research System - Ollama Integration Test")
    print("=" * 60)
    
    # Test 1: Ollama Installation
    ollama_available, available_models = await test_ollama_installation()
    
    # Test 2: Model Provider System
    provider_status = await test_model_provider_system()
    
    # Test 3: Ollama Model Calls (if available)
    if ollama_available and available_models:
        model_test_success = await test_ollama_model_calls()
    else:
        model_test_success = False
    
    # Test 4: Mixed Provider Configurations
    await test_mixed_provider_config()
    
    # Test 5: Installation Guide
    if not ollama_available:
        await test_ollama_installation_guide()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 40)
    
    anthropic_available = provider_status.get("anthropic", False)
    ollama_available = provider_status.get("ollama", False)
    
    print(f"Anthropic Provider: {'✅ Available' if anthropic_available else '❌ Not available'}")
    print(f"Ollama Provider: {'✅ Available' if ollama_available else '❌ Not available'}")
    
    if anthropic_available and ollama_available:
        print("\n🎉 Both providers available! You can use:")
        print("  • Anthropic models for high-quality reasoning")
        print("  • Ollama models for local, private processing")
        print("  • Mixed configurations for optimal cost/performance")
        
    elif anthropic_available:
        print("\n✅ Anthropic available - system fully functional")
        print("💡 Install Ollama for local model support")
        
    elif ollama_available:
        print("\n✅ Ollama available - local processing ready")
        print("💡 Add Anthropic API key for cloud model access")
        
    else:
        print("\n⚠️  No providers available")
        print("   Install Ollama or configure Anthropic API key")
    
    print("\nNext steps:")
    print("1. Configure your preferred models in .env")
    print("2. Run 'python run.py' to start the server")
    print("3. Test with 'curl http://localhost:12000/models/info'")
    
    return anthropic_available or ollama_available


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)