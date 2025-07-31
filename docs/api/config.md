# Configuration API Reference

## Overview

The configuration module provides robust settings management for IVEXES using Pydantic models with environment variable support, validation, and type safety. It centralizes all application configuration and provides flexible override mechanisms for different deployment scenarios.

The module is designed around two main concepts: the complete `Settings` class that contains all configuration options, and `PartialSettings` for selective overrides. All settings support environment variable configuration with automatic type conversion and validation.

## Core Classes

### Settings

The main configuration class that defines all application settings with validation and environment variable support.

```python
from ivexes.config import Settings
from pydantic_settings import BaseSettings
```

#### Class Definition

```python
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
    """
```

#### Configuration Groups

##### API Settings

LLM service configuration and authentication:

| Field | Type | Environment Variable | Default | Description |
|-------|------|---------------------|---------|-------------|
| `openai_api_key` | `str \| None` | `OPENAI_API_KEY` | `None` | OpenAI-specific API key |
| `llm_api_key` | `str` | `LLM_API_KEY`, `OPENAI_API_KEY` | `""` | Primary LLM API key |
| `llm_base_url` | `str` | `LLM_BASE_URL` | `"https://api.openai.com/v1"` | LLM service endpoint |
| `max_reprompts` | `int` | `MAX_REPROMPTS` | `5` | Maximum retry attempts |

##### Agent Settings

AI model configuration and behavior:

| Field | Type | Environment Variable | Default | Description |
|-------|------|---------------------|---------|-------------|
| `model` | `str` | `MODEL` | `"openai/gpt-4o-mini"` | Primary analysis model |
| `model_temperature` | `float` | `MODEL_TEMPERATURE` | `0.3` | Model creativity (0.0-2.0) |
| `reasoning_model` | `str` | `REASONING_MODEL` | `"openai/o4-mini"` | Advanced reasoning model |
| `max_turns` | `int` | `MAX_TURNS` | `10` | Conversation turn limit |
| `session_db_path` | `str` | `SESSION_DB_PATH` | `"./sessions.sqlite"` | Session database location |

##### Logging Settings

Observability and debugging configuration:

| Field | Type | Environment Variable | Default | Description |
|-------|------|---------------------|---------|-------------|
| `log_level` | `LogLevels` | `LOG_LEVEL` | `"INFO"` | Logging verbosity level |
| `trace_name` | `str` | `TRACE_NAME` | `"ivexes"` | OpenAI tracing identifier |

##### Sandbox Settings

Container execution environment:

| Field | Type | Environment Variable | Default | Description |
|-------|------|---------------------|---------|-------------|
| `sandbox_image` | `str` | `SANDBOX_IMAGE` | `"kali-ssh:latest"` | Docker image for analysis |
| `setup_archive` | `str \| None` | `SETUP_ARCHIVE` | `None` | Archive to extract in sandbox |

##### Codebase Settings

Source code analysis configuration:

| Field | Type | Environment Variable | Default | Description |
|-------|------|---------------------|---------|-------------|
| `codebase_path` | `str \| None` | `CODEBASE_PATH` | `None` | Root project directory |
| `vulnerable_folder` | `str \| None` | `VULNERABLE_CODEBASE_FOLDER` | `None` | Vulnerable version folder |
| `patched_folder` | `str \| None` | `PATCHED_CODEBASE_FOLDER` | `None` | Patched version folder |

##### Embedding Settings

Vector database and knowledge base configuration:

| Field | Type | Environment Variable | Default | Description |
|-------|------|---------------------|---------|-------------|
| `chroma_path` | `str` | `CHROMA_PATH` | `"/tmp/ivexes/chromadb"` | ChromaDB storage path |
| `embedding_model` | `str` | `EMBEDDING_MODEL` | `"builtin"` | Embedding model identifier |
| `embedding_provider` | `str` | `EMBEDDING_PROVIDER` | `"builtin"` | Embedding service provider |

#### Validation Methods

The Settings class includes comprehensive field validation:

##### API Key Validation

```python
@field_validator('llm_api_key')
@classmethod
def validate_api_keys(cls, v: str) -> str:
    """Validate API keys are not empty.
    
    Raises:
        ValueError: If API key is empty or whitespace-only.
    """
```

##### Temperature Validation

```python
@field_validator('model_temperature')
@classmethod
def validate_temperature(cls, v: float) -> float:
    """Validate temperature is between 0.0 and 2.0.
    
    Raises:
        ValueError: If temperature is outside valid range.
    """
```

##### Turn Limit Validation

```python
@field_validator('max_turns')
@classmethod
def validate_max_turns(cls, v: int) -> int:
    """Validate max turns is a positive integer.
    
    Raises:
        ValueError: If max_turns is less than 1.
    """
```

##### Log Level Validation

```python
@field_validator('log_level')
@classmethod
def validate_log_level(cls, v: str) -> str:
    """Validate log level is a valid Python logging level.
    
    Raises:
        ValueError: If log level is not one of: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
```

##### URL Validation

```python
@field_validator('llm_base_url')
@classmethod
def validate_base_url(cls, v: str) -> str:
    """Validate base URL starts with http:// or https://.
    
    Raises:
        ValueError: If URL doesn't start with valid protocol.
    """
```

##### Embedding Provider Validation

```python
@field_validator('embedding_provider')
@classmethod
def validate_embedding_provider(cls, v: str) -> str:
    """Validate embedding provider is supported.
    
    Raises:
        ValueError: If provider is not one of: builtin, local, openai.
    """
```

##### Trace Name Normalization

```python
@field_validator('trace_name')
@classmethod
def validate_trace_name(cls, v: str) -> str:
    """Convert trace name to lowercase for consistency."""
```

#### Usage Example

```python
import os
from ivexes.config import Settings

# Set environment variables
os.environ['LLM_API_KEY'] = 'sk-your-api-key'
os.environ['MODEL'] = 'openai/gpt-4'
os.environ['MODEL_TEMPERATURE'] = '0.1'
os.environ['LOG_LEVEL'] = 'DEBUG'

# Create settings instance
settings = Settings()

print(f"Model: {settings.model}")
print(f"Temperature: {settings.model_temperature}")  
print(f"API Key: {settings.llm_api_key[:10]}...")
print(f"Base URL: {settings.llm_base_url}")
```

### PartialSettings

A TypedDict that allows specifying any subset of Settings fields for configuration overrides.

```python
from ivexes.config import PartialSettings
from typing_extensions import TypedDict
```

#### Class Definition

```python
class PartialSettings(TypedDict, total=False):
    """Partial settings type for overriding global settings.
    
    This type allows any subset of Settings fields to be specified
    for overriding global configuration. All fields are optional.
    """
```

#### Available Fields

All fields from the Settings class are available as optional fields:

```python
# API Settings
openai_api_key: Optional[str]
llm_api_key: str
llm_base_url: str

# Agent Settings  
model: str
model_temperature: float
reasoning_model: str
max_turns: int

# Logging Settings
trace_name: str
log_level: LogLevels

# Sandbox Settings
sandbox_image: str
setup_archive: Optional[str]

# Codebase Settings
codebase_path: Optional[str]
vulnerable_folder: Optional[str]
patched_folder: Optional[str]

# Embedding Settings
chroma_path: str
embedding_model: str
embedding_provider: Literal['builtin', 'local', 'openai']

# UI Settings
rich_console: Optional[Console]
```

#### Usage Examples

##### Basic Override

```python
from ivexes.config import PartialSettings

# Override specific settings
overrides = PartialSettings(
    model='openai/gpt-4',
    model_temperature=0.1,
    max_turns=20,
    log_level='DEBUG'
)
```

##### Agent-Specific Configuration

```python
# Configuration for vulnerability analysis
vuln_analysis_settings = PartialSettings(
    model='openai/gpt-4',
    reasoning_model='openai/o1-mini',
    model_temperature=0.0,  # Deterministic output
    max_turns=25,
    codebase_path='/analysis/target',
    vulnerable_folder='vulnerable-v1.2',
    patched_folder='patched-v1.3',
    trace_name='vuln-analysis',
    log_level='INFO'
)
```

##### Environment-Specific Settings

```python
# Development environment
dev_settings = PartialSettings(
    model='openai/gpt-4o-mini',  # Faster, cheaper
    log_level='DEBUG',
    trace_name='dev-testing',
    chroma_path='/tmp/dev-chromadb'
)

# Production environment
prod_settings = PartialSettings(
    model='openai/gpt-4',         # Most capable
    model_temperature=0.1,        # More consistent
    log_level='WARNING',          # Less verbose
    trace_name='production',
    chroma_path='/data/chromadb'
)
```

## Factory Functions

### create_settings

Creates a Settings instance by merging environment variables with optional partial settings overrides.

```python
from ivexes.config import create_settings, PartialSettings
```

#### Function Definition

```python
def create_settings(partial_settings: Optional[PartialSettings] = None) -> Settings:
    """Create Settings instance by merging environment variables with partial overrides.
    
    This function creates a new Settings instance by first loading from environment
    variables and then applying any partial settings overrides. Final validation
    is performed on the merged result.
    
    Args:
        partial_settings: Optional dictionary containing settings to override.
                         Only the specified fields will be updated.
                         
    Returns:
        Settings: A new settings instance with merged configuration.
        
    Raises:
        RuntimeError: If settings validation fails with details about
            which configuration values are invalid.
    """
```

#### Merge Process

1. **Environment Loading**: Load all settings from environment variables
2. **Partial Override**: Apply any provided partial settings
3. **Validation**: Perform comprehensive validation on merged configuration
4. **Error Reporting**: Provide detailed error messages for invalid values

#### Usage Examples

##### Basic Usage

```python
from ivexes.config import create_settings

# Use environment variables only
settings = create_settings()
print(f"Using model: {settings.model}")
```

##### With Overrides

```python
from ivexes.config import create_settings, PartialSettings

# Override specific values
settings = create_settings(
    PartialSettings(
        model='openai/gpt-4',
        model_temperature=0.7,
        max_turns=20,
        log_level='DEBUG'
    )
)

print(f"Model: {settings.model}")
print(f"Temperature: {settings.model_temperature}")
```

##### Error Handling

```python
from ivexes.config import create_settings, PartialSettings

try:
    settings = create_settings(
        PartialSettings(
            model_temperature=3.0,  # Invalid: > 2.0
            max_turns=-1,           # Invalid: negative
            log_level='INVALID'     # Invalid: not a valid level
        )
    )
except RuntimeError as e:
    print("Configuration validation failed:")
    print(e)
    # Output shows specific validation errors for each field
```

### get_run_config

Creates a RunConfig instance configured with current settings for agent execution.

```python
from ivexes.config import get_run_config, Settings
from agents import RunConfig
```

#### Function Definition

```python
def get_run_config(settings: Optional[Settings] = None) -> RunConfig:
    """Get RunConfig for the application, configured with current settings.
    
    This function creates a RunConfig instance that contains all necessary
    configuration for running AI agents, including model settings, provider
    configuration, and temperature settings.
    
    Args:
        settings: Settings instance containing application configuration.
                 If not provided, loads from environment variables.
                 
    Returns:
        RunConfig: Configured run configuration for agent execution.
    """
```

#### Configuration Details

The function creates a RunConfig with:

- **Custom Model Provider**: Configured with LLM base URL and API key
- **Model Settings**: Temperature and parallel tool call configuration
- **OpenAI Client**: Async client with proper authentication

#### Usage Example

```python
from ivexes.config import get_run_config, PartialSettings

# Use with custom settings
settings = create_settings(
    PartialSettings(
        model='openai/gpt-4',
        model_temperature=0.1,
        llm_base_url='https://api.openai.com/v1'
    )
)

run_config = get_run_config(settings)

# Use with agents
from agents import Agent
agent = Agent(name="Analyzer", instructions="Analyze code")
result = await agent.run("Analyze this code", run_config=run_config)
```

## Type Definitions

### LogLevels

Type alias for valid Python logging levels.

```python
from ivexes.config import LogLevels
from typing import Literal

LogLevels = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
```

#### Usage

```python
from ivexes.config import LogLevels, PartialSettings

def configure_logging(level: LogLevels):
    """Configure logging with type safety."""
    settings = PartialSettings(log_level=level)
    return create_settings(settings)

# Type-safe usage
settings = configure_logging('DEBUG')  # Valid
settings = configure_logging('TRACE')  # Type error
```

## Advanced Usage Patterns

### Configuration Factories

```python
from ivexes.config import create_settings, PartialSettings

class ConfigurationFactory:
    """Factory for creating specialized configurations."""
    
    @staticmethod
    def development_config() -> Settings:
        """Configuration optimized for development."""
        return create_settings(
            PartialSettings(
                model='openai/gpt-4o-mini',
                model_temperature=0.3,
                log_level='DEBUG',
                trace_name='development',
                max_turns=10
            )
        )
    
    @staticmethod
    def production_config() -> Settings:
        """Configuration optimized for production."""
        return create_settings(
            PartialSettings(
                model='openai/gpt-4',
                model_temperature=0.1,
                log_level='INFO',
                trace_name='production',
                max_turns=20
            )
        )
    
    @staticmethod
    def security_analysis_config() -> Settings:
        """Configuration optimized for security analysis."""
        return create_settings(
            PartialSettings(
                model='openai/gpt-4',
                reasoning_model='openai/o1-mini',
                model_temperature=0.0,  # Deterministic
                max_turns=30,           # Thorough analysis
                log_level='INFO',
                trace_name='security-analysis'
            )
        )

# Usage
dev_settings = ConfigurationFactory.development_config()
prod_settings = ConfigurationFactory.production_config()
security_settings = ConfigurationFactory.security_analysis_config()
```

### Environment-Based Configuration

```python
import os
from ivexes.config import create_settings, PartialSettings

def get_environment_config() -> Settings:
    """Get configuration based on environment."""
    env = os.environ.get('ENVIRONMENT', 'development')
    
    base_config = PartialSettings(
        trace_name=f'ivexes-{env}'
    )
    
    if env == 'production':
        base_config.update({
            'model': 'openai/gpt-4',
            'model_temperature': 0.1,
            'log_level': 'WARNING',
            'max_turns': 25
        })
    elif env == 'staging':
        base_config.update({
            'model': 'openai/gpt-4o-mini',
            'model_temperature': 0.2,
            'log_level': 'INFO',
            'max_turns': 15
        })
    else:  # development
        base_config.update({
            'model': 'openai/gpt-4o-mini',
            'model_temperature': 0.3,
            'log_level': 'DEBUG',
            'max_turns': 10
        })
    
    return create_settings(base_config)

# Usage
settings = get_environment_config()
```

### Configuration Validation

```python
from ivexes.config import create_settings, PartialSettings
import os

def validate_configuration() -> bool:
    """Validate current configuration and report issues."""
    try:
        settings = create_settings()
        
        # Basic validation
        print("✅ Configuration loaded successfully")
        
        # API key validation
        if not settings.llm_api_key:
            print("❌ LLM_API_KEY is required")
            return False
        
        # Model validation
        if not settings.model.startswith(('openai/', 'anthropic/')):
            print(f"⚠️  Unknown model provider: {settings.model}")
        
        # Path validation
        if settings.codebase_path and not os.path.exists(settings.codebase_path):
            print(f"❌ Codebase path does not exist: {settings.codebase_path}")
            return False
        
        # ChromaDB path validation
        chroma_dir = os.path.dirname(settings.chroma_path)
        if not os.path.exists(chroma_dir):
            try:
                os.makedirs(chroma_dir, exist_ok=True)
                print(f"✅ Created ChromaDB directory: {chroma_dir}")
            except OSError as e:
                print(f"❌ Cannot create ChromaDB directory: {e}")
                return False
        
        print("✅ All configuration validation checks passed")
        return True
        
    except RuntimeError as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

# Usage
if validate_configuration():
    print("Ready to run IVEXES")
else:
    print("Fix configuration issues before proceeding")
```

### Configuration Debugging

```python
from ivexes.config import create_settings, PartialSettings
import os

def debug_configuration():
    """Debug configuration loading and overrides."""
    print("=== Environment Variables ===")
    config_vars = [
        'LLM_API_KEY', 'LLM_BASE_URL', 'MODEL', 'MODEL_TEMPERATURE',
        'REASONING_MODEL', 'MAX_TURNS', 'LOG_LEVEL', 'TRACE_NAME',
        'CODEBASE_PATH', 'VULNERABLE_CODEBASE_FOLDER', 'PATCHED_CODEBASE_FOLDER'
    ]
    
    for var in config_vars:
        value = os.environ.get(var, 'NOT SET')
        if 'API_KEY' in var and value != 'NOT SET':
            value = f"{value[:10]}..."  # Hide API keys
        print(f"{var}: {value}")
    
    print("\n=== Loaded Settings ===")
    try:
        settings = create_settings()
        print(f"Model: {settings.model}")
        print(f"Temperature: {settings.model_temperature}")
        print(f"Max Turns: {settings.max_turns}")
        print(f"Log Level: {settings.log_level}")
        print(f"Base URL: {settings.llm_base_url}")
        print(f"API Key: {settings.llm_api_key[:10] if settings.llm_api_key else 'NOT SET'}...")
        
    except Exception as e:
        print(f"Error loading settings: {e}")
    
    print("\n=== With Overrides ===")
    try:
        override_settings = create_settings(
            PartialSettings(
                model='openai/gpt-4',
                model_temperature=0.1,
                log_level='DEBUG'
            )
        )
        print(f"Overridden Model: {override_settings.model}")
        print(f"Overridden Temperature: {override_settings.model_temperature}")
        print(f"Overridden Log Level: {override_settings.log_level}")
        
    except Exception as e:
        print(f"Error with overrides: {e}")

# Usage
debug_configuration()
```

## Error Handling

### Validation Errors

```python
from ivexes.config import create_settings, PartialSettings

def handle_validation_errors():
    """Demonstrate validation error handling."""
    
    invalid_configs = [
        # Temperature out of range
        PartialSettings(model_temperature=3.0),
        
        # Negative max turns  
        PartialSettings(max_turns=-1),
        
        # Invalid log level
        PartialSettings(log_level='TRACE'),
        
        # Invalid embedding provider
        PartialSettings(embedding_provider='invalid'),
        
        # Invalid URL format
        PartialSettings(llm_base_url='not-a-url')
    ]
    
    for i, config in enumerate(invalid_configs):
        try:
            settings = create_settings(config)
            print(f"Config {i+1}: ✅ Valid")
        except RuntimeError as e:
            print(f"Config {i+1}: ❌ Invalid")
            print(f"  Error: {e}")

handle_validation_errors()
```

### Missing Dependencies

```python
from ivexes.config import create_settings

def check_dependencies():
    """Check for missing configuration dependencies."""
    
    try:
        settings = create_settings()
        
        # Check required API key
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY must be set")
        
        # Check codebase configuration for code analysis
        if settings.codebase_path:
            if not settings.vulnerable_folder:
                raise ValueError("VULNERABLE_CODEBASE_FOLDER required when CODEBASE_PATH is set")
            if not settings.patched_folder:
                raise ValueError("PATCHED_CODEBASE_FOLDER required when CODEBASE_PATH is set")
        
        print("✅ All dependencies satisfied")
        
    except ValueError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    return True

# Usage
if check_dependencies():
    print("Ready to start analysis")
```

## Examples

### Complete Configuration Setup

```python
import os
from dotenv import load_dotenv
from ivexes.config import create_settings, PartialSettings

def setup_complete_configuration():
    """Complete configuration setup example."""
    
    # Load environment variables from .env file
    load_dotenv('.env')
    
    # Define analysis-specific overrides
    analysis_config = PartialSettings(
        # Model configuration
        model='openai/gpt-4',
        reasoning_model='openai/o1-mini',
        model_temperature=0.1,
        max_turns=25,
        
        # Analysis paths
        codebase_path='/analysis/vulnerable-app',
        vulnerable_folder='v1.0-vulnerable',
        patched_folder='v1.1-patched',
        
        # Environment setup
        sandbox_image='kali-ssh:latest',
        setup_archive='/archives/analysis-tools.tar.gz',
        
        # Logging and tracing
        log_level='INFO',
        trace_name='vulnerability-analysis',
        
        # Vector database
        chroma_path='/data/analysis-chromadb',
        embedding_provider='openai',
        embedding_model='text-embedding-3-large'
    )
    
    # Create final settings
    settings = create_settings(analysis_config)
    
    print("=== Configuration Summary ===")
    print(f"Model: {settings.model}")
    print(f"Reasoning Model: {settings.reasoning_model}")
    print(f"Temperature: {settings.model_temperature}")
    print(f"Max Turns: {settings.max_turns}")
    print(f"Codebase: {settings.codebase_path}")
    print(f"Log Level: {settings.log_level}")
    print(f"Trace Name: {settings.trace_name}")
    
    return settings

# Usage
settings = setup_complete_configuration()
```

### Agent Integration

```python
from ivexes.config import create_settings, PartialSettings, get_run_config
from ivexes.agents import SingleAgent

def create_configured_agent():
    """Create agent with complete configuration."""
    
    # Define agent-specific configuration
    agent_settings = PartialSettings(
        model='openai/gpt-4o-mini',
        model_temperature=0.2,
        max_turns=15,
        codebase_path='/project/analysis',
        vulnerable_folder='vulnerable',
        patched_folder='patched',
        trace_name='single-agent-analysis'
    )
    
    # Create settings and run config
    settings = create_settings(agent_settings)
    run_config = get_run_config(settings)
    
    # Create agent with configuration
    agent = SingleAgent(
        bin_path='/target/binary',
        settings=agent_settings  # Pass partial settings to agent
    )
    
    print(f"Agent configured with:")
    print(f"  Model: {settings.model}")
    print(f"  Temperature: {settings.model_temperature}")
    print(f"  Max Turns: {settings.max_turns}")
    print(f"  Codebase: {settings.codebase_path}")
    
    return agent, run_config

# Usage
agent, run_config = create_configured_agent()
```

## See Also

- [Configuration Guide](../documentation/configuration.md) - Complete configuration setup and examples
- [Usage Guide](../documentation/usage.md) - Agent execution modes and workflows
- [Agents API](agents.md) - Agent classes that use configuration
- [Installation Guide](../documentation/installation.md) - Environment setup and prerequisites