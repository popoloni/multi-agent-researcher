import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Model Configuration
    LEAD_AGENT_MODEL: str = "claude-3-opus-20240229"
    SUBAGENT_MODEL: str = "claude-3-sonnet-20240229"
    CITATION_MODEL: str = "claude-3-haiku-20240307"
    
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

settings = Settings()