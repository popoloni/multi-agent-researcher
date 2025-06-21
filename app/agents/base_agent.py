from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio
import anthropic
from app.core.config import settings
import json

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, model: str, name: str):
        self.model = model
        self.name = name
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.conversation_history: List[Dict[str, str]] = []
        self.total_tokens = 0
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
        
    async def think(self, context: str) -> Dict[str, Any]:
        """
        Use extended thinking mode to plan approach
        Returns structured thinking output
        """
        thinking_prompt = f"""
        <thinking>
        Context: {context}
        
        Please analyze this situation and plan your approach. Consider:
        1. What is the main objective?
        2. What tools or resources do I need?
        3. What steps should I take?
        4. What potential challenges might I face?
        
        Output your thinking as a JSON object with keys:
        - objective: string
        - approach: string
        - steps: list of strings
        - challenges: list of strings
        </thinking>
        """
        
        response = await self._call_llm(thinking_prompt, max_tokens=2000)
        
        # Parse thinking output
        try:
            # Look for JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
            
        # Fallback if parsing fails
        return {
            "objective": context,
            "approach": "Direct investigation",
            "steps": ["Analyze query", "Search for information", "Synthesize results"],
            "challenges": ["Unknown"]
        }
    
    async def _call_llm(self, prompt: str, max_tokens: int = 4000) -> str:
        """Make a call to the LLM"""
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,
                system=self.get_system_prompt(),
                messages=self.conversation_history + [{"role": "user", "content": prompt}]
            )
            
            response = message.content[0].text
            self.total_tokens += message.usage.total_tokens
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            raise
            
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        self.total_tokens = 0