"""Settings configuration module.

This module defines the application settings using Pydantic models with
environment variable support and lazy loading capabilities.
"""

import os
import pprint

from agents import (
    Model,
    ModelProvider,
    ModelSettings,
    OpenAIChatCompletionsModel,
    RunConfig,
)
from openai import AsyncOpenAI
from pydantic import Field, field_validator, ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration management.

    This class defines all configuration options for the IVEXES system using
    Pydantic for validation and type checking. Settings can be configured via
    environment variables, which take precedence over default values.

    The settings are organized into logical groups:
    - API settings: Keys and endpoints for external services
    - Agent settings: LLM model configuration and behavior
    - Logging settings: Log levels and tracing configuration
    - Sandbox settings: Container and environment configuration
    - Codebase settings: Source code analysis paths
    - Embedding settings: Vector database and embedding configuration

    All settings are validated on initialization to ensure proper configuration.

    Example:
        Basic usage with environment variables:

        >>> import os
        >>> os.environ['OPENAI_API_KEY'] = 'sk-...'
        >>> os.environ['MODEL'] = 'openai/gpt-4'
        >>> settings = Settings()
        >>> print(settings.model)
        'openai/gpt-4'
    """

    # OpenAI API settings
    openai_api_key: str | None = Field(
        default_factory=lambda: os.environ.get('OPENAI_API_KEY', None)
    )
    brave_search_api_key: str | None = Field(
        default_factory=lambda: os.environ.get('BRAVE_SEARCH_API_KEY', None)
    )

    # gets used
    llm_api_key: str = Field(
        default_factory=lambda: os.environ.get(
            'LLM_API_KEY', os.environ.get('OPENAI_API_KEY', '')
        )
    )
    llm_base_url: str = Field(
        default_factory=lambda: os.environ.get(
            'LLM_BASE_URL', 'https://api.openai.com/v1'
        )
    )

    # Agent settings
    model: str = Field(
        default_factory=lambda: os.environ.get('MODEL', 'openai/gpt-4o-mini')
    )
    model_temperature: float = Field(
        default_factory=lambda: float(os.environ.get('TEMPERATURE', '0.3'))
    )
    reasoning_model: str = Field(
        default_factory=lambda: os.environ.get('REASONING_MODEL', 'openai/o4-mini')
    )
    max_turns: int = Field(
        default_factory=lambda: int(os.environ.get('MAX_TURNS', '10'))
    )

    # Logging
    log_level: str = Field(default_factory=lambda: os.environ.get('LOG_LEVEL', 'INFO'))
    trace_name: str = Field(
        default_factory=lambda: os.environ.get('TRACE_NAME', 'ivexes')
    )

    @field_validator('trace_name')
    @classmethod
    def validate_trace_name(cls, v: str) -> str:
        """Convert trace name to lowercase."""
        return v.lower()

    # Sandbox settings
    sandbox_image: str = Field(
        default_factory=lambda: os.environ.get('SANDBOX_IMAGE', 'kali-ssh:latest')
    )
    setup_archive: str | None = Field(
        default_factory=lambda: os.environ.get('SETUP_ARCHIVE', None)
    )

    # Codebase settings
    codebase_path: str | None = Field(
        default_factory=lambda: os.environ.get('CODEBASE_PATH', None)
    )
    vulnerable_folder: str | None = Field(
        default_factory=lambda: os.environ.get('VULNERABLE_CODEBASE_FOLDER', None)
    )
    patched_folder: str | None = Field(
        default_factory=lambda: os.environ.get('PATCHED_CODEBASE_FOLDER', None)
    )

    # Embedding settings
    chroma_path: str = Field(
        default_factory=lambda: os.environ.get('CHROMA_PATH', '/tmp/ivexes/chromadb')
    )
    embedding_model: str = Field(
        default_factory=lambda: os.environ.get('EMBEDDING_MODEL', 'builtin')
    )
    embedding_provider: str = Field(
        default_factory=lambda: os.environ.get('EMBEDDING_PROVIDER', 'builtin')
    )

    @field_validator('llm_api_key')
    @classmethod
    def validate_api_keys(cls, v: str) -> str:
        """Validate API keys are not empty."""
        if not v or v.strip() == '':
            raise ValueError('API key cannot be empty')
        return v

    @field_validator('model_temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is between 0.0 and 2.0."""
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v

    @field_validator('max_turns')
    @classmethod
    def validate_max_turns(cls, v: int) -> int:
        """Validate max turns is a positive integer."""
        if v < 1:
            raise ValueError('Max turns must be a positive integer')
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid Python logging level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {", ".join(valid_levels)}')
        return v.upper()

    @field_validator('llm_base_url')
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL starts with http:// or https://."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Base URL must start with http:// or https://')
        return v


# Global settings instance - lazily initialized
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the global settings instance, creating it if necessary.

    This function implements the singleton pattern for settings management,
    ensuring that only one Settings instance exists throughout the application
    lifecycle. It provides lazy initialization and proper error handling.

    Returns:
        Settings: The global settings instance.

    Raises:
        RuntimeError: If settings validation fails with details about
            which configuration values are invalid.

    Example:
        >>> settings = get_settings()
        >>> print(settings.model)
        >>> print(settings.log_level)
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except ValidationError as e:
            error_msg = 'Configuration validation failed:\n'
            for error in e.errors():
                field = error.get('loc', ['unknown'])[0]
                msg = error.get('msg', 'Invalid value')
                error_msg += f'  - {field}: {msg}\n'
            raise RuntimeError(error_msg) from e
    return _settings


def get_run_config() -> RunConfig:
    """Get the RunConfig for the application, configured with the current settings.

    This function creates a RunConfig instance that contains all necessary
    configuration for running AI agents, including model settings, provider
    configuration, and temperature settings. It uses the current application
    settings to configure the underlying OpenAI client.

    Returns:
        RunConfig: Configured run configuration for agent execution.

    Example:
        >>> run_config = get_run_config()
        >>> # Use run_config with OpenAI Agents SDK framework
        >>> result = await agent.run(input_data, run_config=run_config)
    """
    import logging

    logger = logging.getLogger(__name__)
    settings = get_settings()

    client = AsyncOpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)

    class CustomModelProvider(ModelProvider):
        def get_model(self, model_name: str | None) -> Model:
            """Get OpenAI model instance with configured client."""
            return OpenAIChatCompletionsModel(
                model=model_name or settings.model, openai_client=client
            )

    run_config: RunConfig = RunConfig(
        model=settings.model,
        model_provider=CustomModelProvider(),
        model_settings=ModelSettings(temperature=settings.model_temperature),
    )

    logger.info(
        f'Runnning with url={settings.llm_base_url} and api_key={settings.llm_api_key[:10]}...'
    )
    logger.debug(f'run_config=\n{pprint.pformat(run_config)}')

    return run_config
