"""
Model provider abstraction layer for supporting multiple LLM providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import anthropic
import ollama
from dataclasses import dataclass
from enum import Enum

from app.core.config import settings


class ModelProvider(Enum):
    """Supported model providers"""
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


@dataclass
class ModelInfo:
    """Information about a model"""
    name: str
    provider: ModelProvider
    display_name: str
    context_length: int
    cost_per_token: Optional[float] = None
    description: str = ""
    recommended_use: str = ""


class BaseModelProvider(ABC):
    """Base class for model providers"""
    
    def __init__(self):
        self.provider_name = None
        self.client = None
        
    @abstractmethod
    async def call_model(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> Tuple[str, int]:
        """
        Call the model and return (response, token_count)
        """
        pass
        
    @abstractmethod
    async def list_available_models(self) -> List[str]:
        """List available models for this provider"""
        pass
        
    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """Validate if a model is available"""
        pass
        
    @abstractmethod
    async def check_connection(self) -> bool:
        """Check if the provider is available"""
        pass


class AnthropicProvider(BaseModelProvider):
    """Anthropic Claude model provider"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = ModelProvider.ANTHROPIC
        if settings.ANTHROPIC_API_KEY:
            self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            self.client = None
            
    async def call_model(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> Tuple[str, int]:
        """Call Anthropic Claude model"""
        
        if not self.client:
            raise ValueError("Anthropic API key not configured")
            
        try:
            message = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )
            
            response = message.content[0].text
            token_count = message.usage.total_tokens
            
            return response, token_count
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")
            
    async def list_available_models(self) -> List[str]:
        """List available Anthropic models"""
        return list(settings.AVAILABLE_MODELS.values())
        
    def validate_model(self, model: str) -> bool:
        """Validate Anthropic model"""
        return model in settings.AVAILABLE_MODELS.values()
        
    async def check_connection(self) -> bool:
        """Check Anthropic API connection"""
        if not self.client:
            return False
            
        try:
            # Try a minimal API call
            await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except:
            return False


class OllamaProvider(BaseModelProvider):
    """Ollama local model provider"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = ModelProvider.OLLAMA
        self.client = ollama.AsyncClient(host=settings.OLLAMA_HOST)
        
    async def call_model(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> Tuple[str, int]:
        """Call Ollama model"""
        
        try:
            # Prepare messages for Ollama format
            ollama_messages = []
            
            if system_prompt:
                ollama_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
                
            ollama_messages.extend(messages)
            
            # Call Ollama
            response = await self.client.chat(
                model=model,
                messages=ollama_messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            )
            
            content = response['message']['content']
            
            # Estimate token count (Ollama doesn't provide exact counts)
            token_count = len(content.split()) * 1.3  # Rough estimation
            
            return content, int(token_count)
            
        except Exception as e:
            raise Exception(f"Ollama API error: {e}")
            
    async def list_available_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            response = await self.client.list()
            # Handle both dict and object response formats
            if hasattr(response, 'models'):
                models = response.models
            else:
                models = response.get('models', [])
            
            model_names = []
            for model in models:
                if hasattr(model, 'model'):
                    model_names.append(model.model)
                elif isinstance(model, dict):
                    model_names.append(model.get('name', model.get('model', '')))
                    
            return model_names
        except Exception as e:
            print(f"Error listing Ollama models: {e}")
            return []
            
    def validate_model(self, model: str) -> bool:
        """Validate Ollama model"""
        # For Ollama, we'll check if the model is in our recommended list
        # or if it's available locally
        return model in settings.OLLAMA_MODELS or model in settings.get_ollama_available_models()
        
    async def check_connection(self) -> bool:
        """Check Ollama connection"""
        try:
            await self.client.list()
            return True
        except:
            return False


class ModelProviderManager:
    """Manager for multiple model providers"""
    
    def __init__(self):
        self.providers = {
            ModelProvider.ANTHROPIC: AnthropicProvider(),
            ModelProvider.OLLAMA: OllamaProvider()
        }
        
    def get_provider_for_model(self, model: str) -> BaseModelProvider:
        """Get the appropriate provider for a model"""
        
        # Check Anthropic models first
        if model in settings.AVAILABLE_MODELS.values():
            return self.providers[ModelProvider.ANTHROPIC]
            
        # Check Ollama models
        if model in settings.OLLAMA_MODELS or ":" in model:  # Ollama models often have tags
            return self.providers[ModelProvider.OLLAMA]
            
        # Default to Anthropic for unknown models
        return self.providers[ModelProvider.ANTHROPIC]
        
    async def call_model(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> Tuple[str, int]:
        """Call a model using the appropriate provider"""
        
        provider = self.get_provider_for_model(model)
        return await provider.call_model(
            model, messages, system_prompt, max_tokens, temperature
        )
        
    async def get_all_available_models(self) -> Dict[str, List[str]]:
        """Get all available models from all providers"""
        
        models = {}
        
        for provider_type, provider in self.providers.items():
            try:
                provider_models = await provider.list_available_models()
                models[provider_type.value] = provider_models
            except:
                models[provider_type.value] = []
                
        return models
        
    async def check_provider_status(self) -> Dict[str, bool]:
        """Check the status of all providers"""
        
        status = {}
        
        for provider_type, provider in self.providers.items():
            try:
                status[provider_type.value] = await provider.check_connection()
            except:
                status[provider_type.value] = False
                
        return status
        
    def get_model_info(self, model: str) -> ModelInfo:
        """Get information about a specific model"""
        
        # Anthropic models
        if model in settings.AVAILABLE_MODELS.values():
            return ModelInfo(
                name=model,
                provider=ModelProvider.ANTHROPIC,
                display_name=model,
                context_length=200000,  # Most Claude models
                description="Anthropic Claude model",
                recommended_use="High-quality reasoning and analysis"
            )
            
        # Ollama models
        if model in settings.OLLAMA_MODELS:
            model_info = settings.OLLAMA_MODELS[model]
            return ModelInfo(
                name=model,
                provider=ModelProvider.OLLAMA,
                display_name=model_info.get("display_name", model),
                context_length=model_info.get("context_length", 4096),
                description=model_info.get("description", "Local Ollama model"),
                recommended_use=model_info.get("recommended_use", "Local processing")
            )
            
        # Unknown model
        return ModelInfo(
            name=model,
            provider=ModelProvider.ANTHROPIC,  # Default
            display_name=model,
            context_length=4096,
            description="Unknown model",
            recommended_use="General use"
        )


# Global model provider manager instance
model_manager = ModelProviderManager()