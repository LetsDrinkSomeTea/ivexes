# Configuration Guide

This guide covers how to configure IVEXES for your specific environment and use cases.

## Configuration Overview

IVEXES uses a flexible configuration system that supports:

- Environment variables
- `.env` files
- Programmatic configuration
- Default settings with smart fallbacks

Configuration precedence (highest to lowest):
1. Programmatically passed settings
2. Environment variables
3. `.env` file values
4. Default settings

## Basic Configuration

### 1. Create Environment File

Create a `.env` file in your project root:

```bash
# Navigate to your IVEXES directory
cd /path/to/ivexes

# Create configuration file
cat > .env << 'EOF'
# Required: LLM API Configuration
LLM_API_KEY=your_openai_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
MODEL=openai/gpt-4o-mini
REASONING_MODEL=openai/o4-mini
MODEL_TEMPERATURE=0.3

# Optional: Logging Configuration
LOG_LEVEL=INFO
TRACE_NAME=ivexes

# Optional: Agent Configuration
MAX_TURNS=10

# Optional: Vector Database
EMBEDDING_PROVIDER=builtin
CHROMA_PATH=/tmp/ivexes/chromadb

# Optional: Codebase Analysis
CODEBASE_PATH=/path/to/your/test/codebase
VULNERABLE_CODEBASE_FOLDER=vulnerable-version
PATCHED_CODEBASE_FOLDER=patched-version

# Optional: Sandbox Configuration
SANDBOX_IMAGE=kali-ssh:latest
SETUP_ARCHIVE=/path/to/setup.tar.gz
EOF
```

### 2. Secure Your API Keys

!!! warning "Security Best Practices"
    - Never commit `.env` files to version control
    - Use strong, unique API keys
    - Rotate keys regularly
    - Limit API key permissions where possible

```bash
# Add .env to .gitignore if not already present
echo ".env" >> .gitignore

# Set appropriate permissions
chmod 600 .env
```

## Configuration Sections

### LLM Configuration

Configure your Language Model access:

```bash
# Primary API key (required)
LLM_API_KEY=sk-your-openai-key-here

# API endpoint (optional, defaults to OpenAI)
LLM_BASE_URL=https://api.openai.com/v1

# Models to use
MODEL=openai/gpt-4o-mini              # Primary model for analysis
REASONING_MODEL=openai/o4-mini        # Model for planning/reasoning
MODEL_TEMPERATURE=0.3                 # Creativity vs consistency (0.0-2.0)
```

#### Alternative LLM Providers

=== "OpenAI Compatible"
    ```bash
    LLM_BASE_URL=https://your-provider.com/v1
    LLM_API_KEY=your-provider-key
    MODEL=your-provider/model-name
    ```

=== "Local Models (via LiteLLM)"
    ```bash
    LLM_BASE_URL=http://localhost:4000
    MODEL=local/llama-2-7b
    # Start LiteLLM proxy separately
    ```

=== "Azure OpenAI"
    ```bash
    LLM_BASE_URL=https://your-resource.openai.azure.com/
    LLM_API_KEY=your-azure-key
    MODEL=azure/gpt-4
    ```

### Agent Configuration

Control agent behavior and limits:

```bash
# Maximum conversation turns before timeout
MAX_TURNS=10

# Agent-specific settings
AGENT_TIMEOUT=300                     # Timeout in seconds
ENABLE_MULTI_AGENT=true              # Enable multi-agent coordination
AGENT_MEMORY_SIZE=1000               # Context window management
```

### Vector Database Configuration

Configure knowledge base integration:

```bash
# Embedding provider options: builtin, local, openai
EMBEDDING_PROVIDER=builtin

# ChromaDB storage location
CHROMA_PATH=/tmp/ivexes/chromadb

# Knowledge base sources
ENABLE_MITRE_ATTACK=true
ENABLE_CWE_DATABASE=true
ENABLE_CVE_SEARCH=true

# Embedding model (if using local)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Codebase Analysis Configuration

Set up vulnerability analysis targets:

```bash
# Root directory containing code to analyze
CODEBASE_PATH=/path/to/your/project

# Subdirectories for comparison analysis
VULNERABLE_CODEBASE_FOLDER=vulnerable-v1.0
PATCHED_CODEBASE_FOLDER=patched-v1.1

# Analysis options
INCLUDE_PATTERNS=*.py,*.js,*.java     # File patterns to analyze
EXCLUDE_PATTERNS=tests/*,docs/*      # Patterns to exclude
MAX_FILE_SIZE=1048576                # Max file size in bytes (1MB)
```

### Sandbox Configuration

Configure isolated execution environments:

```bash
# Docker image for sandbox
SANDBOX_IMAGE=kali-ssh:latest

# Setup archive for sandbox initialization
SETUP_ARCHIVE=/path/to/setup.tar.gz

# Sandbox limits
SANDBOX_MEMORY_LIMIT=2g
SANDBOX_CPU_LIMIT=2
SANDBOX_TIMEOUT=600                   # Timeout in seconds

# Network configuration
SANDBOX_NETWORK_MODE=bridge
SANDBOX_PORT_RANGE=8000-8099
```

### Logging Configuration

Control logging output and verbosity:

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Trace name for distributed tracing
TRACE_NAME=ivexes

# Log output destinations
LOG_FILE=/var/log/ivexes/ivexes.log
ENABLE_CONSOLE_LOGGING=true
ENABLE_FILE_LOGGING=false

# Structured logging
LOG_FORMAT=json                      # json or text
ENABLE_PERFORMANCE_LOGGING=true
```

## Advanced Configuration

### Programmatic Configuration

For advanced use cases, configure IVEXES programmatically:

```python
from ivexes.config import PartialSettings

# Create custom configuration
settings = PartialSettings(
    model='openai/gpt-4o-mini',
    max_turns=15,
    codebase_path='/custom/path',
    vulnerable_folder='before-fix',
    patched_folder='after-fix',
    log_level='DEBUG'
)

# Use with agents
from ivexes.agents import SingleAgent
agent = SingleAgent(settings=settings)
```

### Environment-Specific Configurations

=== "Development"
    ```bash
    # .env.dev
    LOG_LEVEL=DEBUG
    MODEL=openai/gpt-4o-mini
    MAX_TURNS=5
    ENABLE_PERFORMANCE_LOGGING=true
    ```

=== "Production"
    ```bash
    # .env.prod
    LOG_LEVEL=WARNING
    MODEL=openai/gpt-4
    MAX_TURNS=20
    ENABLE_FILE_LOGGING=true
    ```

=== "Testing"
    ```bash
    # .env.test
    LOG_LEVEL=CRITICAL
    MODEL=mock
    CHROMA_PATH=/tmp/test-chromadb
    ```

### Docker Configuration

When running in containers, use environment variables:

```yaml
# docker-compose.yml
services:
  ivexes:
    build: .
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - MODEL=openai/gpt-4o-mini
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock
```

## Configuration Validation

### Check Your Configuration

```python
# Validate configuration
from ivexes.config import Settings

try:
    settings = Settings()
    print("✓ Configuration is valid")
    print(f"Model: {settings.model}")
    print(f"Log Level: {settings.log_level}")
except Exception as e:
    print(f"✗ Configuration error: {e}")
```

### Common Configuration Issues

!!! failure "Missing API Key"
    ```bash
    # Error: No LLM_API_KEY provided
    # Solution: Set your API key
    export LLM_API_KEY=your-key-here
    ```

!!! failure "Invalid Model Name"
    ```bash
    # Error: Model 'invalid-model' not found
    # Solution: Use supported model names
    MODEL=openai/gpt-4o-mini
    ```

!!! failure "Path Not Found"
    ```bash
    # Error: CODEBASE_PATH does not exist
    # Solution: Use absolute paths
    CODEBASE_PATH=/absolute/path/to/code
    ```

## Security Considerations

### API Key Security

- Use dedicated API keys for IVEXES
- Implement key rotation policies
- Monitor API usage and costs
- Use environment-specific keys

### Network Security

```bash
# Restrict sandbox network access
SANDBOX_NETWORK_MODE=none

# Use specific port ranges
SANDBOX_PORT_RANGE=8000-8010

# Enable network monitoring
ENABLE_NETWORK_LOGGING=true
```

### File System Security

```bash
# Restrict file access
SANDBOX_READ_ONLY=true
SANDBOX_TEMP_DIR=/tmp/ivexes-sandbox

# Set file size limits
MAX_FILE_SIZE=10485760  # 10MB
MAX_TOTAL_SIZE=104857600  # 100MB
```

## Next Steps

After configuring IVEXES:

1. [Run the quickstart tutorial](quickstart.md)
2. [Explore example configurations](../examples/index.md)
3. [Learn about agents](../user-guide/agents.md)

## Configuration Reference

For a complete list of all configuration options, see the [API Reference](../api/config.md).