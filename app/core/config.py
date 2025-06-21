import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
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
    
    # Model Configuration - Using Claude 4 Sonnet as default for optimal performance/cost balance
    LEAD_AGENT_MODEL: str = os.getenv("LEAD_AGENT_MODEL", AVAILABLE_MODELS["claude-4-sonnet"])
    SUBAGENT_MODEL: str = os.getenv("SUBAGENT_MODEL", AVAILABLE_MODELS["claude-4-sonnet"])
    CITATION_MODEL: str = os.getenv("CITATION_MODEL", AVAILABLE_MODELS["claude-3-5-haiku"])
    
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
    
    @classmethod
    def get_model_info(cls) -> dict:
        """Get information about available models"""
        return {
            "available_models": cls.AVAILABLE_MODELS,
            "current_config": {
                "lead_agent": cls().LEAD_AGENT_MODEL,
                "subagent": cls().SUBAGENT_MODEL, 
                "citation": cls().CITATION_MODEL
            },
            "recommended_configs": {
                "high_performance": {
                    "lead_agent": cls.AVAILABLE_MODELS["claude-4-opus"],
                    "subagent": cls.AVAILABLE_MODELS["claude-4-sonnet"],
                    "citation": cls.AVAILABLE_MODELS["claude-3-5-haiku"]
                },
                "balanced": {
                    "lead_agent": cls.AVAILABLE_MODELS["claude-4-sonnet"],
                    "subagent": cls.AVAILABLE_MODELS["claude-4-sonnet"],
                    "citation": cls.AVAILABLE_MODELS["claude-3-5-haiku"]
                },
                "cost_optimized": {
                    "lead_agent": cls.AVAILABLE_MODELS["claude-3-5-sonnet-latest"],
                    "subagent": cls.AVAILABLE_MODELS["claude-3-5-sonnet-latest"],
                    "citation": cls.AVAILABLE_MODELS["claude-3-5-haiku"]
                }
            }
        }
    
    @classmethod
    def validate_model(cls, model_name: str) -> bool:
        """Validate if a model name is supported"""
        return model_name in cls.AVAILABLE_MODELS.values()

settings = Settings()