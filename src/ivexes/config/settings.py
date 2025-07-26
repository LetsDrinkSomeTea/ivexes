"""Settings configuration module.

This module defines the application settings using Pydantic models with
environment variable support and lazy loading capabilities.
"""

import os
import pprint
from typing import Literal, Optional

LogLevels = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

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
from typing_extensions import TypedDict


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
    max_reprompts: int = Field(
        default_factory=lambda: int(os.environ.get('MAX_REPROMPTS', '5'))
    )
    # Agent settings
    model: str = Field(
        default_factory=lambda: os.environ.get('MODEL', 'openai/gpt-4o-mini')
    )
    model_temperature: float = Field(
        default_factory=lambda: float(os.environ.get('MODEL_TEMPERATURE', '0.3'))
    )
    reasoning_model: str = Field(
        default_factory=lambda: os.environ.get('REASONING_MODEL', 'openai/o4-mini')
    )
    max_turns: int = Field(
        default_factory=lambda: int(os.environ.get('MAX_TURNS', '10'))
    )
    session_db_path: str = Field(
        default_factory=lambda: os.environ.get('SESSION_DB_PATH', './sessions.sqlite')
    )

    # Logging
    log_level: LogLevels = Field(
        default_factory=lambda: os.environ.get('LOG_LEVEL', 'INFO')
    )  # type: ignore
    trace_name: str = Field(
        default_factory=lambda: os.environ.get('TRACE_NAME', 'ivexes')
    )

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

    @field_validator('trace_name')
    @classmethod
    def validate_trace_name(cls, v: str) -> str:
        """Convert trace name to lowercase."""
        return v.lower()

    @field_validator('embedding_provider')
    @classmethod
    def validate_embedding_provider(cls, v: str) -> str:
        """Validate embedding provider is either 'builtin', 'local' or 'openai'."""
        if v not in ['builtin', 'local', 'openai']:
            raise ValueError(
                'embedding_provider must be one of: builtin, local, openai'
            )
        return v

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


class PartialSettings(TypedDict, total=False):
    """Partial settings type for overriding global settings.

    This type allows any subset of Settings fields to be specified
    for overriding global configuration. All fields are optional.
    """

    openai_api_key: Optional[str]
    brave_search_api_key: Optional[str]
    llm_api_key: str
    llm_base_url: str
    model: str
    model_temperature: float
    reasoning_model: str
    max_turns: int
    trace_name: str
    sandbox_image: str
    setup_archive: Optional[str]
    codebase_path: Optional[str]
    vulnerable_folder: Optional[str]
    patched_folder: Optional[str]
    chroma_path: str
    embedding_model: str
    embedding_provider: str


def create_settings(partial_settings: Optional[PartialSettings] = None) -> Settings:
    """Create a Settings instance by merging environment variables with partial overrides.

    This function creates a new Settings instance by first loading from environment
    variables (without validation) and then applying any partial settings overrides.
    Final validation is performed on the merged result to ensure all required fields
    are properly set.

    Args:
        partial_settings: Optional dictionary containing settings to override.
                         Only the specified fields will be updated.

    Returns:
        Settings: A new settings instance with merged configuration.

    Raises:
        RuntimeError: If settings validation fails with details about
            which configuration values are invalid.

    Example:
        >>> # Use environment variables only
        >>> settings = create_settings()
        >>> # Override specific values
        >>> settings = create_settings(
        ...     {
        ...         'model': 'openai/gpt-4',
        ...         'model_temperature': 0.7,
        ...         'max_turns': 20,
        ...         'llm_api_key': 'sk-custom-key',
        ...     }
        ... )
        >>> print(settings.model)  # 'openai/gpt-4'
    """
    try:
        # Create base settings from environment variables without validation
        # We use model_validate with from_attributes=False to skip validation
        env_data = {}
        for field_name, field_info in Settings.model_fields.items():
            default_factory = getattr(field_info, 'default_factory', None)
            if default_factory is not None:
                env_data[field_name] = default_factory()
            elif hasattr(field_info, 'default') and field_info.default is not None:
                env_data[field_name] = field_info.default

        if partial_settings:
            # Update with partial settings - partial_settings is a dict
            env_data.update(partial_settings)

        # Create final settings instance with full validation
        return Settings(**env_data)

    except ValidationError as e:
        error_msg = 'Configuration validation failed:\n'
        for error in e.errors():
            field = error.get('loc', ['unknown'])[0]
            msg = error.get('msg', 'Invalid value')
            error_msg += f'  - {field}: {msg}\n'
        raise RuntimeError(error_msg) from e


def get_run_config(settings: Settings) -> RunConfig:
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

    client = AsyncOpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)

    class CustomModelProvider(ModelProvider):
        def get_model(self, model_name: str | None) -> Model:
            """Get OpenAI model instance with configured client."""
            return OpenAIChatCompletionsModel(
                model=model_name or settings.model, openai_client=client
            )

    run_config: RunConfig = RunConfig(
        model_provider=CustomModelProvider(),
        model_settings=ModelSettings(
            temperature=settings.model_temperature,
            parallel_tool_calls=False,
        ),
    )

    logger.info(
        f'Runnning with url={settings.llm_base_url} and api_key={settings.llm_api_key[:10]}...'
    )
    logger.debug(f'run_config=\n{pprint.pformat(run_config)}')

    return run_config
