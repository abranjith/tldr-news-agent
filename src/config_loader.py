"""Configuration loader for news summary agents."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigLoader:
    """Loads and manages configuration for news agents."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize config loader with optional custom config path."""
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}") from exc
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}") from e
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        return self._config
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        agents_config = self._config.get("agents", {})
        if agent_name not in agents_config:
            raise ValueError(f"Agent '{agent_name}' not found in configuration")
        return agents_config[agent_name]
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self._config.get("llm", {})
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search configuration."""
        return self._config.get("search", {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self._config.get("output", {})
    
    def get_orchestrator_config(self) -> Dict[str, Any]:
        """Get main orchestrator configuration."""
        return self._config.get("main_orchestrator", {})
    
    def get_llm_model_config(self, provider: Optional[str] = None) -> tuple[Dict[str, Any], str]:
        """Get LLM model configuration for the specified or default provider."""
        llm_config = self.get_llm_config()
        
        if provider is None:
            provider = llm_config.get("provider", "ollama")
        
        models_config = llm_config.get("models", {})
        if provider not in models_config:
            raise ValueError(f"LLM provider '{provider}' not found in configuration")
        
        model_config = models_config[provider].copy()
        
        # Load API key from environment if specified
        if "api_key_env" in model_config:
            api_key_env = model_config.pop("api_key_env")
            api_key = os.getenv(api_key_env)
            if api_key:
                model_config["api_key"] = api_key
        
        # Load endpoint from environment for Azure OpenAI
        if "endpoint_env" in model_config:
            endpoint_env = model_config.pop("endpoint_env")
            endpoint = os.getenv(endpoint_env)
            if endpoint:
                model_config["endpoint"] = endpoint
        
        return model_config, provider


# Legacy functions for backward compatibility
def load_config() -> Dict[str, Any]:
    """Load agent configuration from YAML file (legacy function)."""
    config_loader = ConfigLoader()
    return config_loader.config


def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """Get configuration for a specific agent (legacy function)."""
    config_loader = ConfigLoader()
    return config_loader.get_agent_config(agent_name)


def get_main_orchestrator_config() -> Dict[str, Any]:
    """Get configuration for the main orchestrator (legacy function)."""
    config_loader = ConfigLoader()
    return config_loader.get_orchestrator_config()


def get_output_config() -> Dict[str, Any]:
    """Get output configuration (legacy function)."""
    config_loader = ConfigLoader()
    return config_loader.get_output_config()
