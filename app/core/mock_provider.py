"""
Mock AI provider for testing and development without API keys
"""

from typing import Dict, Any, List, Tuple
import asyncio
import random
from app.core.model_providers import BaseModelProvider

class MockProvider(BaseModelProvider):
    """Mock AI provider that generates realistic responses for testing"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = "mock"
        
    async def call_model(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> Tuple[str, int]:
        """Generate a mock response based on the input"""
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Generate response based on context
        response = self._generate_response(user_message, system_prompt)
        
        # Estimate token count
        token_count = len(response.split()) * 1.3
        
        return response, int(token_count)
        
    def _generate_response(self, user_message: str, system_prompt: str) -> str:
        """Generate a contextual mock response"""
        
        user_lower = user_message.lower()
        
        # Research planning responses
        if "research plan" in user_lower or "planning" in system_prompt.lower():
            return """
{
  "objective": "Conduct comprehensive research on the given topic",
  "approach": "Multi-agent collaborative research with web search and analysis",
  "steps": [
    "Analyze the research query and identify key topics",
    "Deploy specialized search agents to gather information",
    "Synthesize findings from multiple sources",
    "Generate comprehensive report with citations"
  ],
  "challenges": [
    "Ensuring information accuracy and relevance",
    "Managing multiple concurrent search operations",
    "Synthesizing diverse information sources"
  ]
}
"""
        
        # Search agent responses
        elif "search" in system_prompt.lower() or "find information" in user_lower:
            topics = ["artificial intelligence", "machine learning", "AI", "technology", "research"]
            topic = next((t for t in topics if t in user_lower), "the topic")
            
            return f"""
Based on my search, here are key findings about {topic}:

## Key Information
- {topic.title()} is a rapidly evolving field with significant impact across industries
- Recent developments include advances in large language models and neural networks
- Applications span from healthcare and finance to autonomous systems
- Current challenges include ethical considerations and responsible AI development

## Sources Found
1. Academic papers from leading AI conferences
2. Industry reports from major technology companies
3. Government policy documents on AI regulation
4. Expert interviews and analysis pieces

## Summary
The research indicates strong growth and innovation in this area, with both opportunities and challenges ahead.
"""
        
        # Citation responses
        elif "citation" in system_prompt.lower() or "cite" in user_lower:
            return """
[1] Smith, J. et al. (2024). "Advances in Artificial Intelligence Research." Journal of AI Studies, 15(3), 45-67.
[2] Technology Research Institute. (2024). "AI Industry Report 2024." TRI Publications.
[3] Johnson, M. (2024). "The Future of Machine Learning." AI Today Magazine, March 2024.
[4] National AI Policy Center. (2024). "Guidelines for Responsible AI Development." Policy Brief 2024-01.
"""
        
        # General research responses
        elif any(term in user_lower for term in ["artificial intelligence", "ai", "machine learning"]):
            return """
# Artificial Intelligence: A Comprehensive Overview

## Introduction
Artificial Intelligence (AI) represents one of the most transformative technologies of the 21st century. It encompasses the development of computer systems capable of performing tasks that typically require human intelligence.

## Key Areas
- **Machine Learning**: Algorithms that improve through experience
- **Natural Language Processing**: Understanding and generating human language
- **Computer Vision**: Interpreting and analyzing visual information
- **Robotics**: Physical AI systems that interact with the world

## Current Applications
- Healthcare diagnostics and treatment planning
- Financial fraud detection and risk assessment
- Autonomous vehicles and transportation systems
- Personal assistants and recommendation systems

## Future Outlook
The field continues to evolve rapidly, with ongoing research in areas such as:
- Artificial General Intelligence (AGI)
- Quantum machine learning
- Ethical AI and bias mitigation
- Human-AI collaboration frameworks

## Conclusion
AI technology offers tremendous potential for solving complex problems while requiring careful consideration of ethical implications and societal impact.
"""
        
        # Default response
        else:
            return f"""
Thank you for your query about: {user_message[:100]}...

I understand you're looking for information on this topic. Based on my analysis, this is an interesting area that would benefit from comprehensive research.

Key considerations include:
- Understanding the current state of knowledge
- Identifying reliable sources and expert perspectives
- Analyzing trends and developments
- Considering practical applications and implications

I would recommend a systematic approach to gathering and analyzing information from multiple authoritative sources to provide you with accurate and comprehensive insights.

Would you like me to elaborate on any specific aspect of this topic?
"""
    
    async def list_available_models(self) -> List[str]:
        """List mock models"""
        return ["mock-gpt-4", "mock-claude-3", "mock-llama-3"]
        
    def validate_model(self, model: str) -> bool:
        """All models are valid for mock provider"""
        return True
        
    async def check_connection(self) -> bool:
        """Mock provider is always available"""
        return True