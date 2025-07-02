import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./kenobi.db")
    
    # AI Provider Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "anthropic")  # Default to anthropic, can be "ollama"
    
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Ollama Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # Available Claude Models (newest to oldest)
    AVAILABLE_MODELS = {
        # Claude 4 Series (Latest)
        "claude-4-opus": "claude-4-opus-20241120",
        "claude-4-sonnet": "claude-4-sonnet-20241120", 
        
        # Claude 3.5 Series
        "claude-3-5-sonnet-latest": "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet": "claude-3-5-sonnet-20240620",
        "claude-3-5-haiku": "claude-3-5-haiku-20241022",
        
        # Claude 3 Series (Legacy)
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229", 
        "claude-3-haiku": "claude-3-haiku-20240307"
    }
    
    # Available Ollama Models (Popular local models)
    OLLAMA_MODELS = {
        # Large Language Models
        "llama3.1:8b": {
            "display_name": "Llama 3.1 8B",
            "context_length": 128000,
            "description": "Meta's Llama 3.1 8B model - excellent for general tasks",
            "recommended_use": "General purpose, fast inference",
            "size": "4.7GB"
        },
        "llama3.1:70b": {
            "display_name": "Llama 3.1 70B", 
            "context_length": 128000,
            "description": "Meta's Llama 3.1 70B model - high performance",
            "recommended_use": "Complex reasoning, high quality output",
            "size": "40GB"
        },
        "llama3.2:3b": {
            "display_name": "Llama 3.2 3B",
            "context_length": 128000,
            "description": "Meta's Llama 3.2 3B model - lightweight and fast",
            "recommended_use": "Fast inference, resource-constrained environments",
            "size": "2.0GB"
        },
        "llama3.2:1b": {
            "display_name": "Llama 3.2 1B",
            "context_length": 128000,
            "description": "Meta's Llama 3.2 1B model - ultra-lightweight and fast",
            "recommended_use": "Very fast inference, minimal resource usage",
            "size": "1.3GB"
        },
        "mistral:7b": {
            "display_name": "Mistral 7B",
            "context_length": 32768,
            "description": "Mistral AI's 7B model - efficient and capable",
            "recommended_use": "Balanced performance and speed",
            "size": "4.1GB"
        },
        "mixtral:8x7b": {
            "display_name": "Mixtral 8x7B",
            "context_length": 32768,
            "description": "Mistral AI's mixture of experts model",
            "recommended_use": "High performance, complex tasks",
            "size": "26GB"
        },
        "qwen2.5:7b": {
            "display_name": "Qwen 2.5 7B",
            "context_length": 32768,
            "description": "Alibaba's Qwen 2.5 7B model",
            "recommended_use": "Multilingual tasks, coding",
            "size": "4.4GB"
        },
        "gemma2:9b": {
            "display_name": "Gemma 2 9B",
            "context_length": 8192,
            "description": "Google's Gemma 2 9B model",
            "recommended_use": "Research, safety-focused applications",
            "size": "5.4GB"
        },
        "phi3:3.8b": {
            "display_name": "Phi-3 3.8B",
            "context_length": 128000,
            "description": "Microsoft's Phi-3 3.8B model",
            "recommended_use": "Efficient reasoning, mobile deployment",
            "size": "2.3GB"
        }
    }
    
    # Model Configuration - Default to Ollama models, switch to Claude if AI_PROVIDER is anthropic
    @property
    def LEAD_AGENT_MODEL(self) -> str:
        if self.AI_PROVIDER == "anthropic" and self.ANTHROPIC_API_KEY:
            return os.getenv("LEAD_AGENT_MODEL", self.AVAILABLE_MODELS["claude-4-sonnet"])
        return os.getenv("LEAD_AGENT_MODEL", "llama3.2:1b")
    
    @property
    def SUBAGENT_MODEL(self) -> str:
        if self.AI_PROVIDER == "anthropic" and self.ANTHROPIC_API_KEY:
            return os.getenv("SUBAGENT_MODEL", self.AVAILABLE_MODELS["claude-4-sonnet"])
        return os.getenv("SUBAGENT_MODEL", "llama3.2:1b")
    
    @property
    def CITATION_MODEL(self) -> str:
        if self.AI_PROVIDER == "anthropic" and self.ANTHROPIC_API_KEY:
            return os.getenv("CITATION_MODEL", self.AVAILABLE_MODELS["claude-3-5-haiku"])
        return os.getenv("CITATION_MODEL", "llama3.2:1b")
    
    # Kenobi Chat and Code Analysis Model
    @property
    def KENOBI_MODEL(self) -> str:
        return os.getenv("KENOBI_MODEL", self.LEAD_AGENT_MODEL)
    
    # Documentation Generation Model
    @property
    def DOCUMENTATION_MODEL(self) -> str:
        return os.getenv("DOCUMENTATION_MODEL", self.LEAD_AGENT_MODEL)
    
    # Agent Configuration
    MAX_THINKING_LENGTH: int = 50000
    MAX_CONTEXT_LENGTH: int = 200000
    MAX_PARALLEL_SUBAGENTS: int = 5
    
    # Tool Configuration
    SEARCH_TIMEOUT: int = 30
    MAX_SEARCH_RESULTS: int = 10
    
    # Memory Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    MEMORY_TTL: int = 3600  # 1 hour
    
    # Rate Limiting
    MAX_TOKENS_PER_REQUEST: int = 100000
    
    # Google Custom Search API
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID: str = os.getenv("GOOGLE_CSE_ID", "")
    
    @classmethod
    def get_model_info(cls) -> dict:
        """Get information about available models from all providers"""
        return {
            "anthropic_models": cls.AVAILABLE_MODELS,
            "ollama_models": cls.OLLAMA_MODELS,
            "current_config": {
                "lead_agent": cls().LEAD_AGENT_MODEL,
                "subagent": cls().SUBAGENT_MODEL, 
                "citation": cls().CITATION_MODEL
            },
            "recommended_configs": {
                "anthropic_high_performance": {
                    "lead_agent": cls.AVAILABLE_MODELS["claude-4-opus"],
                    "subagent": cls.AVAILABLE_MODELS["claude-4-sonnet"],
                    "citation": cls.AVAILABLE_MODELS["claude-3-5-haiku"]
                },
                "anthropic_balanced": {
                    "lead_agent": cls.AVAILABLE_MODELS["claude-4-sonnet"],
                    "subagent": cls.AVAILABLE_MODELS["claude-4-sonnet"],
                    "citation": cls.AVAILABLE_MODELS["claude-3-5-haiku"]
                },
                "anthropic_cost_optimized": {
                    "lead_agent": cls.AVAILABLE_MODELS["claude-3-5-sonnet-latest"],
                    "subagent": cls.AVAILABLE_MODELS["claude-3-5-sonnet-latest"],
                    "citation": cls.AVAILABLE_MODELS["claude-3-5-haiku"]
                },
                "ollama_high_performance": {
                    "lead_agent": "llama3.1:70b",
                    "subagent": "llama3.1:8b",
                    "citation": "llama3.2:3b"
                },
                "ollama_balanced": {
                    "lead_agent": "llama3.1:8b",
                    "subagent": "mistral:7b",
                    "citation": "llama3.2:3b"
                },
                "ollama_lightweight": {
                    "lead_agent": "mistral:7b",
                    "subagent": "llama3.2:3b",
                    "citation": "phi3:3.8b"
                },
                "mixed_optimal": {
                    "lead_agent": cls.AVAILABLE_MODELS["claude-4-sonnet"],
                    "subagent": "llama3.1:8b",
                    "citation": "llama3.2:3b"
                }
            }
        }
    
    @classmethod
    def validate_model(cls, model_name: str) -> bool:
        """Validate if a model name is supported by any provider"""
        return (model_name in cls.AVAILABLE_MODELS.values() or 
                model_name in cls.OLLAMA_MODELS.keys())
    
    @classmethod
    def get_ollama_available_models(cls) -> list:
        """Get list of available Ollama models (would check with Ollama in practice)"""
        return list(cls.OLLAMA_MODELS.keys())
    
    @classmethod
    def get_provider_for_model(cls, model_name: str) -> str:
        """Get the provider for a given model"""
        if model_name in cls.AVAILABLE_MODELS.values():
            return "anthropic"
        elif model_name in cls.OLLAMA_MODELS.keys():
            return "ollama"
        else:
            return "unknown"

settings = Settings()