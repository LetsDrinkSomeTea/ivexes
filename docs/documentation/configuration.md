# Configuration Guide

## Overview

IVEXES provides a comprehensive configuration system built on Pydantic that manages all application settings through environment variables and programmatic overrides. The configuration system is designed for flexibility, validation, and ease of use across different deployment scenarios.

All configuration is centralized in the `Settings` class, which validates inputs and provides sensible defaults. You can customize behavior through environment variables, `.env` files, or programmatic configuration using `PartialSettings`.

## Configuration Architecture

### Settings Hierarchy

IVEXES uses a layered configuration approach:

1. **Default Values**: Built-in defaults for all settings
2. **Environment Variables**: Override defaults via environment variables
3. **Partial Settings**: Programmatic overrides for specific use cases
4. **Validation**: All values validated on load with clear error messages

### Configuration Categories

The configuration system is organized into logical groups:

- **API Settings**: Keys and endpoints for external services
- **Agent Settings**: LLM model configuration and behavior
- **Logging Settings**: Log levels and tracing configuration
- **Sandbox Settings**: Container and environment configuration
- **Codebase Settings**: Source code analysis paths
- **Embedding Settings**: Vector database and embedding configuration

## Core Configuration

### Required Settings

These settings must be configured for IVEXES to function:

#### API Keys

```bash
# Primary API key for LLM services
export LLM_API_KEY="sk-your-api-key-here"

# Alternative: OpenAI specific key (falls back to LLM_API_KEY)
export OPENAI_API_KEY="sk-your-openai-key-here"
```

#### LLM Configuration

```bash
# LLM service endpoint
export LLM_BASE_URL="https://api.openai.com/v1"

# Primary model for analysis
export MODEL="openai/gpt-4o-mini"

# Reasoning model for complex tasks
export REASONING_MODEL="openai/o1-mini"
```

### Agent Configuration

Control AI agent behavior and performance:

```bash
# Model creativity (0.0-2.0)
export MODEL_TEMPERATURE="0.3"

# Maximum conversation turns
export MAX_TURNS="10"

# Maximum retry attempts
export MAX_REPROMPTS="5"

# Session database location
export SESSION_DB_PATH="./sessions.sqlite"
```

### Logging and Tracing

Configure logging and observability:

```bash
# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export LOG_LEVEL="INFO"

# OpenAI tracing identifier
export TRACE_NAME="ivexes"
```

### Sandbox Configuration

Configure the execution environment:

```bash
# Docker image for sandbox
export SANDBOX_IMAGE="kali-ssh:latest"

# Archive to extract in sandbox (optional)
export SETUP_ARCHIVE="/path/to/setup.tar.gz"
```

### Codebase Analysis

Configure paths for code analysis:

```bash
# Root directory containing code versions
export CODEBASE_PATH="/path/to/project"

# Vulnerable version folder name
export VULNERABLE_CODEBASE_FOLDER="vulnerable"

# Patched version folder name
export PATCHED_CODEBASE_FOLDER="patched"
```

### Vector Database

Configure knowledge base and embeddings:

```bash
# ChromaDB storage path
export CHROMA_PATH="/tmp/ivexes/chromadb"

# Embedding provider (builtin, local, openai)
export EMBEDDING_PROVIDER="builtin"

# Embedding model
export EMBEDDING_MODEL="builtin"
```

## Configuration Files

### Environment Files

Create configuration files for different environments:

#### `.env` (Development)

```bash
# Development configuration
LLM_API_KEY=sk-dev-key-here
LLM_BASE_URL=http://localhost:4000/v1
MODEL=openai/gpt-4o-mini
MODEL_TEMPERATURE=0.3
LOG_LEVEL=DEBUG
TRACE_NAME=ivexes-dev

# Local development paths
CODEBASE_PATH=/home/user/projects/analysis
VULNERABLE_CODEBASE_FOLDER=vulnerable
PATCHED_CODEBASE_FOLDER=fixed

# Local ChromaDB
CHROMA_PATH=/tmp/ivexes-dev/chromadb
EMBEDDING_PROVIDER=builtin
```

#### `.secrets.env` (Production)

```bash
# Production secrets (never commit to version control)
LLM_API_KEY=sk-prod-key-secure
OPENAI_API_KEY=sk-openai-prod-key
```

#### `docker.env` (Container Deployment)

```bash
# Container-optimized configuration
LLM_BASE_URL=http://litellm:4000/v1
SANDBOX_IMAGE=kali-ssh:latest
CHROMA_PATH=/data/chromadb
SESSION_DB_PATH=/data/sessions.sqlite
LOG_LEVEL=INFO
```

## Programmatic Configuration

### Using PartialSettings

Override specific settings programmatically:

```python
from ivexes.config import PartialSettings, create_settings

# Basic configuration override
settings = create_settings(
    PartialSettings(
        model='openai/gpt-4',
        model_temperature=0.1,
        max_turns=20,
        log_level='DEBUG'
    )
)

# Agent-specific configuration
analysis_settings = PartialSettings(
    model='openai/gpt-4o-mini',
    reasoning_model='openai/o1-mini',
    codebase_path='/project/analysis',
    vulnerable_folder='v1.0-vulnerable',
    patched_folder='v1.1-fixed',
    max_turns=15
)

# Create settings with validation
settings = create_settings(analysis_settings)
```

### Agent Configuration Patterns

#### SingleAgent Configuration

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/analysis/target',
    vulnerable_folder='before',
    patched_folder='after',
    max_turns=15,
    model_temperature=0.2
)

agent = SingleAgent(
    bin_path='/sandbox/target_binary',
    settings=settings
)
```

#### MultiAgent Configuration

```python
from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings

# High-performance multi-agent setup
settings = PartialSettings(
    model='openai/gpt-4',
    reasoning_model='openai/o1-mini',
    model_temperature=0.1,
    max_turns=25,
    codebase_path='/large-project',
    vulnerable_folder='v2.0',
    patched_folder='v2.1',
    log_level='INFO'
)

multi_agent = MultiAgent(settings=settings)
```

## Validation and Error Handling

### Configuration Validation

The settings system provides comprehensive validation:

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
    # Output:
    # Configuration validation failed:
    #   - model_temperature: Temperature must be between 0.0 and 2.0
    #   - max_turns: Max turns must be a positive integer
    #   - log_level: Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Validation Rules

#### API Keys
- Must not be empty or whitespace-only
- Validated when `llm_api_key` is accessed

#### Model Temperature
- Must be between 0.0 and 2.0
- Controls randomness in model outputs

#### Max Turns
- Must be a positive integer
- Prevents infinite conversation loops

#### Log Level
- Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Case-insensitive input, normalized to uppercase

#### Base URL
- Must start with `http://` or `https://`
- Validates LLM endpoint format

#### Embedding Provider
- Must be one of: `builtin`, `local`, `openai`
- Determines vector database integration method

## Advanced Configuration Patterns

### Multi-Environment Setup

```python
import os
from ivexes.config import create_settings, PartialSettings

def get_settings_for_environment():
    """Get settings based on deployment environment."""
    env = os.environ.get('DEPLOYMENT_ENV', 'development')
    
    base_settings = PartialSettings(
        trace_name=f'ivexes-{env}',
        log_level='DEBUG' if env == 'development' else 'INFO'
    )
    
    if env == 'production':
        base_settings.update({
            'model': 'openai/gpt-4',
            'model_temperature': 0.1,
            'max_turns': 20
        })
    elif env == 'development':
        base_settings.update({
            'model': 'openai/gpt-4o-mini',
            'model_temperature': 0.3,
            'max_turns': 10
        })
    
    return create_settings(base_settings)
```

### Performance Optimization

```python
# High-performance configuration
performance_settings = PartialSettings(
    model='openai/gpt-4o-mini',      # Faster model
    model_temperature=0.1,            # More deterministic
    max_turns=5,                      # Limit conversation length
    log_level='WARNING',              # Reduce log noise
    embedding_provider='builtin'      # Fastest embedding option
)

# Resource-conscious configuration
resource_settings = PartialSettings(
    model='openai/gpt-4o-mini',
    max_turns=3,
    chroma_path='/tmp/small-chromadb',
    embedding_provider='builtin'
)
```

### Security-Focused Configuration

```python
# Security analysis optimized settings
security_settings = PartialSettings(
    model='openai/gpt-4',              # Most capable model
    reasoning_model='openai/o1-mini',   # Advanced reasoning
    model_temperature=0.0,              # Deterministic output
    max_turns=30,                       # Allow thorough analysis
    log_level='DEBUG',                  # Detailed logging
    trace_name='security-audit'        # Specific tracing
)
```

## Configuration Best Practices

### Security Considerations

1. **API Key Management**:
   - Never commit API keys to version control
   - Use `.secrets.env` files with proper permissions
   - Rotate keys regularly
   - Use different keys for different environments

2. **Path Security**:
   - Use absolute paths for codebase analysis
   - Validate path accessibility before analysis
   - Avoid world-writable directories for data storage

3. **Container Security**:
   - Use specific image tags, not `latest`
   - Regularly update sandbox images
   - Limit container capabilities

### Performance Optimization

1. **Model Selection**:
   - Use `gpt-4o-mini` for development and light analysis
   - Use `gpt-4` for production and complex analysis
   - Enable reasoning models for complex vulnerability analysis

2. **Resource Management**:
   - Set appropriate `max_turns` to prevent runaway conversations
   - Use local embedding providers when possible
   - Monitor ChromaDB storage growth

3. **Logging Configuration**:
   - Use `INFO` or `WARNING` in production
   - Use `DEBUG` only for troubleshooting
   - Configure log rotation for long-running services

### Development Workflow

1. **Environment Separation**:
   - Use different configuration files for each environment
   - Validate configuration in CI/CD pipelines
   - Test configuration changes in development first

2. **Configuration Validation**:
   - Always use `create_settings()` for validation
   - Handle `RuntimeError` exceptions for invalid configuration
   - Provide clear error messages for configuration issues

3. **Testing**:
   - Test with minimal viable configuration
   - Validate all environment variable combinations
   - Test configuration error scenarios

## Troubleshooting

### Common Configuration Issues

#### API Key Problems

```bash
# Error: API key cannot be empty
# Solution: Set your API key
export LLM_API_KEY="sk-your-key-here"

# Error: Invalid API key format
# Solution: Verify key format and permissions
curl -H "Authorization: Bearer $LLM_API_KEY" \
     https://api.openai.com/v1/models
```

#### Model Configuration Issues

```bash
# Error: Model not found
# Solution: Check model name and availability
export MODEL="openai/gpt-4o-mini"  # Not "gpt-4o-mini"

# Error: Temperature validation failed
# Solution: Use value between 0.0 and 2.0
export MODEL_TEMPERATURE="0.3"  # Not "3.0"
```

#### Path Configuration Issues

```python
# Error: Codebase path validation
settings = PartialSettings(
    codebase_path='/nonexistent/path',  # Will fail if path doesn't exist
    vulnerable_folder='vuln',
    patched_folder='patched'
)

# Solution: Verify paths exist
import os
codebase_path = '/path/to/project'
if not os.path.exists(codebase_path):
    raise ValueError(f"Codebase path does not exist: {codebase_path}")
```

#### ChromaDB Issues

```bash
# Error: Permission denied writing to ChromaDB
# Solution: Ensure directory is writable
mkdir -p /tmp/ivexes/chromadb
chmod 755 /tmp/ivexes/chromadb
export CHROMA_PATH="/tmp/ivexes/chromadb"
```

### Configuration Validation

```python
from ivexes.config import create_settings, PartialSettings

def validate_configuration():
    """Validate current configuration and report issues."""
    try:
        settings = create_settings()
        print("✅ Configuration valid")
        print(f"Model: {settings.model}")
        print(f"Base URL: {settings.llm_base_url}")
        print(f"Log Level: {settings.log_level}")
        
        # Test API connectivity
        if settings.llm_api_key:
            print("✅ API key configured")
        else:
            print("❌ API key missing")
            
    except RuntimeError as e:
        print("❌ Configuration validation failed:")
        print(e)
        return False
    
    return True

# Run validation
if __name__ == "__main__":
    validate_configuration()
```

## Related Topics

- [Installation Guide](installation.md) - Setting up the development environment
- [Usage Guide](usage.md) - Core workflows and agent execution modes
- [Configuration API](../api/config.md) - Detailed API reference for configuration classes
- [Development Guide](development.md) - Development setup and contributing guidelines

## Next Steps

After configuring IVEXES:

1. **Verify Installation**: Run configuration validation to ensure all settings are correct
2. **Test Basic Functionality**: Create a simple agent with your configuration
3. **Explore Usage Patterns**: Review the [Usage Guide](usage.md) for common workflows
4. **Review API Documentation**: Detailed reference in [Configuration API](../api/config.md)
5. **Set Up Development Environment**: Follow [Development Guide](development.md) for contributing