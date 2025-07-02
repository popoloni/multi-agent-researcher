"""
Settings API endpoints for managing environment configuration
"""

import os
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import asyncio
from dotenv import load_dotenv, set_key, find_dotenv

from app.core.config import settings
from app.core.model_providers import model_manager, ModelProvider

router = APIRouter()

class SettingValue(BaseModel):
    """Individual setting value"""
    key: str
    value: str
    description: str
    type: str = "text"  # text, select, number, boolean, password
    options: Optional[List[str]] = None
    category: str = "general"
    requires_restart: bool = False

class SettingsUpdate(BaseModel):
    """Settings update request"""
    settings: Dict[str, str]

class ModelConfiguration(BaseModel):
    """Model configuration"""
    provider: str
    model: str
    display_name: str
    description: str = ""

class ProviderStatus(BaseModel):
    """Provider connection status"""
    provider: str
    connected: bool
    models: List[str]
    error: Optional[str] = None

@router.get("/api/settings/all")
async def get_all_settings() -> Dict[str, Any]:
    """Get all configurable settings with their current values and metadata"""
    
    # Load current environment
    load_dotenv()
    
    # Get available models from providers
    try:
        available_models = await model_manager.get_all_available_models()
        provider_status = await model_manager.check_provider_status()
    except Exception as e:
        available_models = {"anthropic": [], "ollama": [], "mock": []}
        provider_status = {"anthropic": False, "ollama": False, "mock": True}
    
    # Define all configurable settings
    settings_config = {
        # API Configuration
        "API_HOST": SettingValue(
            key="API_HOST",
            value=os.getenv("API_HOST", "0.0.0.0"),
            description="Host address for the API server",
            type="text",
            category="api",
            requires_restart=True
        ),
        "API_PORT": SettingValue(
            key="API_PORT", 
            value=os.getenv("API_PORT", "12000"),
            description="Port for the API server",
            type="number",
            category="api",
            requires_restart=True
        ),
        "DEBUG": SettingValue(
            key="DEBUG",
            value=os.getenv("DEBUG", "false"),
            description="Enable debug mode",
            type="boolean",
            category="api",
            requires_restart=True
        ),
        
        # AI Provider Configuration
        "AI_PROVIDER": SettingValue(
            key="AI_PROVIDER",
            value=os.getenv("AI_PROVIDER", "ollama"),
            description="Primary AI provider to use",
            type="select",
            options=["anthropic", "ollama", "mock"],
            category="ai",
            requires_restart=False
        ),
        
        # Anthropic Configuration
        "ANTHROPIC_API_KEY": SettingValue(
            key="ANTHROPIC_API_KEY",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            description="Anthropic API key for Claude models",
            type="password",
            category="anthropic",
            requires_restart=False
        ),
        
        # Ollama Configuration
        "OLLAMA_HOST": SettingValue(
            key="OLLAMA_HOST",
            value=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            description="Ollama server host URL",
            type="text",
            category="ollama",
            requires_restart=False
        ),
        "OLLAMA_PORT": SettingValue(
            key="OLLAMA_PORT",
            value=os.getenv("OLLAMA_PORT", "11434"),
            description="Ollama server port",
            type="number",
            category="ollama",
            requires_restart=False
        ),
        
        # Model Configuration
        "LEAD_AGENT_MODEL": SettingValue(
            key="LEAD_AGENT_MODEL",
            value=os.getenv("LEAD_AGENT_MODEL", settings.LEAD_AGENT_MODEL),
            description="Model for lead research agent",
            type="select",
            options=_get_all_model_options(available_models),
            category="models",
            requires_restart=False
        ),
        "SUBAGENT_MODEL": SettingValue(
            key="SUBAGENT_MODEL", 
            value=os.getenv("SUBAGENT_MODEL", settings.SUBAGENT_MODEL),
            description="Model for sub-research agents",
            type="select",
            options=_get_all_model_options(available_models),
            category="models",
            requires_restart=False
        ),
        "CITATION_MODEL": SettingValue(
            key="CITATION_MODEL",
            value=os.getenv("CITATION_MODEL", settings.CITATION_MODEL),
            description="Model for citation generation",
            type="select", 
            options=_get_all_model_options(available_models),
            category="models",
            requires_restart=False
        ),
        "KENOBI_MODEL": SettingValue(
            key="KENOBI_MODEL",
            value=os.getenv("KENOBI_MODEL", settings.KENOBI_MODEL),
            description="Model for Kenobi chat assistant",
            type="select",
            options=_get_all_model_options(available_models),
            category="models",
            requires_restart=False
        ),
        "DOCUMENTATION_MODEL": SettingValue(
            key="DOCUMENTATION_MODEL",
            value=os.getenv("DOCUMENTATION_MODEL", settings.DOCUMENTATION_MODEL),
            description="Model for documentation generation",
            type="select",
            options=_get_all_model_options(available_models),
            category="models",
            requires_restart=False
        ),
        
        # Database Configuration
        "DATABASE_URL": SettingValue(
            key="DATABASE_URL",
            value=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./kenobi.db"),
            description="Database connection URL",
            type="text",
            category="database",
            requires_restart=True
        ),
        
        # Logging Configuration
        "LOG_LEVEL": SettingValue(
            key="LOG_LEVEL",
            value=os.getenv("LOG_LEVEL", "INFO"),
            description="Logging level",
            type="select",
            options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            category="logging",
            requires_restart=True
        ),
        
        # Search Configuration
        "GOOGLE_API_KEY": SettingValue(
            key="GOOGLE_API_KEY",
            value=os.getenv("GOOGLE_API_KEY", ""),
            description="Google API key for search functionality",
            type="password",
            category="search",
            requires_restart=False
        ),
        "GOOGLE_CSE_ID": SettingValue(
            key="GOOGLE_CSE_ID",
            value=os.getenv("GOOGLE_CSE_ID", ""),
            description="Google Custom Search Engine ID",
            type="text",
            category="search",
            requires_restart=False
        ),
        
        # Redis Configuration
        "REDIS_URL": SettingValue(
            key="REDIS_URL",
            value=os.getenv("REDIS_URL", "redis://localhost:6379"),
            description="Redis connection URL for caching",
            type="text",
            category="cache",
            requires_restart=True
        )
    }
    
    return {
        "settings": {key: setting.dict() for key, setting in settings_config.items()},
        "categories": {
            "api": "API Configuration",
            "ai": "AI Provider",
            "anthropic": "Anthropic (Claude)",
            "ollama": "Ollama (Local Models)",
            "models": "Model Selection",
            "database": "Database",
            "logging": "Logging",
            "search": "Search Engine",
            "cache": "Caching"
        },
        "provider_status": provider_status,
        "available_models": available_models,
        "model_presets": _get_model_presets()
    }

@router.post("/api/settings/update")
async def update_settings(update: SettingsUpdate) -> Dict[str, Any]:
    """Update environment settings"""
    
    try:
        env_file = find_dotenv()
        if not env_file:
            env_file = ".env"
        
        updated_settings = []
        restart_required = False
        
        # Define settings that require restart
        restart_settings = {
            "API_HOST", "API_PORT", "DEBUG", "DATABASE_URL", 
            "LOG_LEVEL", "REDIS_URL"
        }
        
        for key, value in update.settings.items():
            # Validate the setting
            if not _validate_setting(key, value):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid value for setting {key}: {value}"
                )
            
            # Update the .env file
            set_key(env_file, key, value)
            updated_settings.append(key)
            
            # Check if restart is required
            if key in restart_settings:
                restart_required = True
        
        # Reload environment variables
        load_dotenv(override=True)
        
        return {
            "success": True,
            "updated_settings": updated_settings,
            "restart_required": restart_required,
            "message": f"Updated {len(updated_settings)} settings successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@router.get("/api/settings/providers/status")
async def get_provider_status() -> Dict[str, ProviderStatus]:
    """Get the connection status of all AI providers"""
    
    try:
        provider_status = await model_manager.check_provider_status()
        available_models = await model_manager.get_all_available_models()
        
        result = {}
        
        for provider_name in ["anthropic", "ollama", "mock"]:
            models = available_models.get(provider_name, [])
            connected = provider_status.get(provider_name, False)
            
            error = None
            if not connected and provider_name != "mock":
                if provider_name == "anthropic":
                    if not os.getenv("ANTHROPIC_API_KEY"):
                        error = "API key not configured"
                    else:
                        error = "Connection failed - check API key"
                elif provider_name == "ollama":
                    error = "Ollama server not accessible"
            
            result[provider_name] = ProviderStatus(
                provider=provider_name,
                connected=connected,
                models=models,
                error=error
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get provider status: {str(e)}")

@router.get("/api/settings/models/available")
async def get_available_models() -> Dict[str, Any]:
    """Get all available models from all providers"""
    
    try:
        available_models = await model_manager.get_all_available_models()
        
        # Add model metadata
        enriched_models = {}
        
        for provider, models in available_models.items():
            enriched_models[provider] = []
            
            for model in models:
                model_info = model_manager.get_model_info(model)
                enriched_models[provider].append({
                    "name": model,
                    "display_name": model_info.display_name,
                    "description": model_info.description,
                    "context_length": model_info.context_length,
                    "recommended_use": model_info.recommended_use,
                    "provider": provider
                })
        
        return {
            "models": enriched_models,
            "presets": _get_model_presets()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")

@router.post("/api/settings/models/preset/{preset_name}")
async def apply_model_preset(preset_name: str) -> Dict[str, Any]:
    """Apply a predefined model configuration preset"""
    
    presets = _get_model_presets()
    
    if preset_name not in presets:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found")
    
    preset = presets[preset_name]
    
    # Update the settings
    update_data = SettingsUpdate(settings={
        "LEAD_AGENT_MODEL": preset["lead_agent"],
        "SUBAGENT_MODEL": preset["subagent"], 
        "CITATION_MODEL": preset["citation"],
        "KENOBI_MODEL": preset["lead_agent"],  # Use lead agent model for Kenobi
        "DOCUMENTATION_MODEL": preset["lead_agent"]  # Use lead agent model for docs
    })
    
    return await update_settings(update_data)

@router.post("/api/settings/test-connection/{provider}")
async def test_provider_connection(provider: str) -> Dict[str, Any]:
    """Test connection to a specific AI provider"""
    
    if provider not in ["anthropic", "ollama"]:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    try:
        if provider == "anthropic":
            from app.core.model_providers import AnthropicProvider
            provider_instance = AnthropicProvider()
        else:
            from app.core.model_providers import OllamaProvider
            provider_instance = OllamaProvider()
        
        connected = await provider_instance.check_connection()
        
        if connected:
            models = await provider_instance.list_available_models()
            return {
                "success": True,
                "connected": True,
                "models": models,
                "message": f"Successfully connected to {provider}"
            }
        else:
            return {
                "success": False,
                "connected": False,
                "models": [],
                "message": f"Failed to connect to {provider}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "connected": False,
            "models": [],
            "error": str(e),
            "message": f"Error testing {provider} connection: {str(e)}"
        }

@router.get("/api/settings/export")
async def export_settings() -> Dict[str, Any]:
    """Export current settings configuration"""
    
    load_dotenv()
    
    # Get all environment variables that are configurable
    configurable_vars = [
        "API_HOST", "API_PORT", "DEBUG", "AI_PROVIDER",
        "ANTHROPIC_API_KEY", "OLLAMA_HOST", "OLLAMA_PORT",
        "LEAD_AGENT_MODEL", "SUBAGENT_MODEL", "CITATION_MODEL",
        "KENOBI_MODEL", "DOCUMENTATION_MODEL", "DATABASE_URL",
        "LOG_LEVEL", "GOOGLE_API_KEY", "GOOGLE_CSE_ID", "REDIS_URL"
    ]
    
    exported_settings = {}
    for var in configurable_vars:
        value = os.getenv(var, "")
        # Don't export sensitive values in plain text
        if "API_KEY" in var or "PASSWORD" in var:
            exported_settings[var] = "***REDACTED***" if value else ""
        else:
            exported_settings[var] = value
    
    return {
        "settings": exported_settings,
        "export_timestamp": "2025-07-02T07:35:00Z",
        "version": "1.0"
    }

def _get_all_model_options(available_models: Dict[str, List[str]]) -> List[str]:
    """Get all available model options from all providers"""
    all_models = []
    
    # Add Anthropic models
    for model in settings.AVAILABLE_MODELS.values():
        all_models.append(model)
    
    # Add Ollama models
    for model in settings.OLLAMA_MODELS.keys():
        all_models.append(model)
    
    # Add any additional models from live providers
    for provider_models in available_models.values():
        for model in provider_models:
            if model not in all_models:
                all_models.append(model)
    
    return sorted(all_models)

def _get_model_presets() -> Dict[str, Dict[str, str]]:
    """Get predefined model configuration presets"""
    return {
        "anthropic_high_performance": {
            "name": "Anthropic High Performance",
            "description": "Best quality with Claude 4 Opus for complex tasks",
            "lead_agent": settings.AVAILABLE_MODELS["claude-4-opus"],
            "subagent": settings.AVAILABLE_MODELS["claude-4-sonnet"],
            "citation": settings.AVAILABLE_MODELS["claude-3-5-haiku"],
            "provider": "anthropic"
        },
        "anthropic_balanced": {
            "name": "Anthropic Balanced",
            "description": "Good quality and speed with Claude 4 Sonnet",
            "lead_agent": settings.AVAILABLE_MODELS["claude-4-sonnet"],
            "subagent": settings.AVAILABLE_MODELS["claude-4-sonnet"],
            "citation": settings.AVAILABLE_MODELS["claude-3-5-haiku"],
            "provider": "anthropic"
        },
        "anthropic_cost_optimized": {
            "name": "Anthropic Cost Optimized",
            "description": "Lower cost with Claude 3.5 models",
            "lead_agent": settings.AVAILABLE_MODELS["claude-3-5-sonnet-latest"],
            "subagent": settings.AVAILABLE_MODELS["claude-3-5-sonnet-latest"],
            "citation": settings.AVAILABLE_MODELS["claude-3-5-haiku"],
            "provider": "anthropic"
        },
        "ollama_high_performance": {
            "name": "Ollama High Performance",
            "description": "Best local performance with Llama 3.1 70B",
            "lead_agent": "llama3.1:70b",
            "subagent": "llama3.1:8b",
            "citation": "llama3.2:3b",
            "provider": "ollama"
        },
        "ollama_balanced": {
            "name": "Ollama Balanced",
            "description": "Good balance of performance and resource usage",
            "lead_agent": "llama3.1:8b",
            "subagent": "mistral:7b",
            "citation": "llama3.2:3b",
            "provider": "ollama"
        },
        "ollama_lightweight": {
            "name": "Ollama Lightweight",
            "description": "Fast and resource-efficient local models",
            "lead_agent": "mistral:7b",
            "subagent": "llama3.2:3b",
            "citation": "phi3:3.8b",
            "provider": "ollama"
        },
        "ollama_ultra_fast": {
            "name": "Ollama Ultra Fast",
            "description": "Fastest inference with minimal resource usage",
            "lead_agent": "llama3.2:1b",
            "subagent": "llama3.2:1b",
            "citation": "llama3.2:1b",
            "provider": "ollama"
        }
    }

def _validate_setting(key: str, value: str) -> bool:
    """Validate a setting value"""
    
    # Port validation
    if key in ["API_PORT", "OLLAMA_PORT"]:
        try:
            port = int(value)
            return 1 <= port <= 65535
        except ValueError:
            return False
    
    # Boolean validation
    if key == "DEBUG":
        return value.lower() in ["true", "false", "1", "0", "yes", "no"]
    
    # URL validation (basic)
    if key in ["DATABASE_URL", "REDIS_URL", "OLLAMA_HOST"]:
        return len(value.strip()) > 0
    
    # Provider validation
    if key == "AI_PROVIDER":
        return value in ["anthropic", "ollama", "mock"]
    
    # Log level validation
    if key == "LOG_LEVEL":
        return value in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    # Model validation
    if key.endswith("_MODEL"):
        return len(value.strip()) > 0  # Basic validation, could be enhanced
    
    return True