"""LLM factory for creating agents with different LLM providers."""
import os
from typing import Any, Dict, Optional
from pydantic_ai import Agent, Tool
from pydantic_ai.models import Model

from .config_loader import ConfigLoader

class LLMFactory:
    """Factory class for creating LLM instances based on configuration."""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize the LLM factory with a config loader."""
        self.config_loader = config_loader
    
    def create_model(self, provider: Optional[str] = None) -> Model:
        """Create a model instance based on the provider configuration."""
        model_config, provider_name = self.config_loader.get_llm_model_config(provider)
        
        if provider_name == "openai":
            return self._create_openai_model(model_config)
        elif provider_name == "anthropic":
            return self._create_anthropic_model(model_config)
        elif provider_name == "ollama":
            return self._create_ollama_model(model_config)
        elif provider_name == "gemini":
            return self._create_gemini_model(model_config)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
    
    def _create_openai_model(self, config: Dict[str, Any]) -> Model:
        """Create an OpenAI model instance."""
        from pydantic_ai.models.openai import OpenAIModel
        from pydantic_ai.providers.openai import OpenAIProvider
        
        model_name = config.get("model")
        api_key_env = config.get("api_key_env", "OPENAI_API_KEY")
        api_key = os.environ.get(api_key_env)
        
        if not model_name:
            raise ValueError("OpenAI model name not found in configuration.")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")

        return OpenAIModel(model_name, provider=OpenAIProvider(api_key=api_key))

    def _create_anthropic_model(self, config: Dict[str, Any]) -> Model:
        """Create an Anthropic model instance."""
        from pydantic_ai.models.anthropic import AnthropicModel
        from pydantic_ai.providers.anthropic import AnthropicProvider
        
        model_name = config.get("model")
        api_key_env = config.get("api_key_env", "ANTHROPIC_API_KEY")
        api_key = os.environ.get(api_key_env)
        if not model_name:
            raise ValueError("Anthropic model name not found in configuration.")
        if not api_key:
            raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable.")
        
        return AnthropicModel(model_name, provider=AnthropicProvider(api_key=api_key))
    
    def _create_gemini_model(self, config: Dict[str, Any]) -> Model:
        """Create a Gemini model instance."""
        from pydantic_ai.models.google import GoogleModel
        from pydantic_ai.providers.google import GoogleProvider
        
        model_name = config.get("model")
        api_key_env = config.get("api_key_env", "GOOGLE_API_KEY")
        api_key = os.environ.get(api_key_env)
        
        if not model_name:
            raise ValueError("Gemini model name not found in configuration.")
        if not api_key:
            raise ValueError("Gemini API key not found. Please set GOOGLE_API_KEY environment variable.")
        
        return GoogleModel(model_name, provider=GoogleProvider(api_key=api_key))
    
    def _create_ollama_model(self, config: Dict[str, Any]) -> Model:
        """Create an Ollama model instance using OpenAI interface."""
        from pydantic_ai.models.openai import OpenAIModel
        from pydantic_ai.providers.openai import OpenAIProvider
        
        model_name = config.get("model")
        base_url = config.get("base_url")

        if not model_name:
            raise ValueError("Ollama model name not found in configuration.")
        if not base_url:
            raise ValueError("Ollama base URL not found in configuration.")

        # Ollama uses OpenAI-compatible API
        return OpenAIModel(model_name, provider=OpenAIProvider(base_url=base_url))


    def create_agent(self, system_prompt: str, provider: Optional[str] = None, tools: Optional[list[Tool]] = None, **kwargs) -> Agent:
        """Create a PydanticAI agent with the specified LLM model."""
        model = self.create_model(provider)
        
        return Agent(
            model=model,
            tools=tools or [],
            system_prompt=system_prompt,
            **kwargs
        )


def get_default_llm_factory() -> LLMFactory:
    """Get a default LLM factory instance."""
    config_loader = ConfigLoader()
    return LLMFactory(config_loader)
