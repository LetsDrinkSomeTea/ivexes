# Configuration API

The config module handles all configuration management for IVEXES, including settings validation, environment variable loading, and configuration merging.

## Overview

IVEXES uses a flexible configuration system that supports multiple configuration sources with clear precedence rules. The configuration system is built on Pydantic for robust validation and type checking.

### Key Components

- **[Settings](#ivexes.config.settings.Settings)** - Main configuration class
- **[PartialSettings](#ivexes.config.settings.PartialSettings)** - Partial configuration for overrides
- **[setup_logging()](#ivexes.config.log.setup_logging)** - Logging configuration

## Usage Examples

### Basic Configuration

```python
from ivexes.config import Settings

# Load configuration from environment
settings = Settings()
print(f"Model: {settings.model}")
print(f"Max turns: {settings.max_turns}")
```

### Partial Configuration Override

```python
from ivexes.config import PartialSettings

# Override specific settings
partial = PartialSettings(
    model='openai/gpt-4',
    max_turns=20,
    log_level='DEBUG'
)

# Use with agents
from ivexes.agents import SingleAgent
agent = SingleAgent(settings=partial)
```

### Environment Variables

```python
import os
from ivexes.config import Settings

# Set environment variables
os.environ['MODEL'] = 'openai/gpt-4o-mini'
os.environ['MAX_TURNS'] = '15'

# Configuration picks up environment changes
settings = Settings()
```

### Logging Setup

```python
from ivexes.config.log import setup_logging

# Configure logging with custom settings
setup_logging(
    level='INFO',
    trace_name='my-analysis',
    enable_file_logging=True
)
```

## Configuration Precedence

Configuration values are resolved in this order (highest to lowest priority):

1. **Programmatic settings** - `PartialSettings` passed to agents
2. **Environment variables** - `MODEL`, `MAX_TURNS`, etc.
3. **`.env` file** - Loaded from current directory
4. **Default values** - Built-in sensible defaults

## Environment Variables Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LLM_API_KEY` | str | - | API key for LLM service (required) |
| `MODEL` | str | `openai/gpt-4o-mini` | Primary model for analysis |
| `REASONING_MODEL` | str | `openai/o4-mini` | Model for planning tasks |
| `MAX_TURNS` | int | 10 | Maximum conversation turns |
| `LOG_LEVEL` | str | `INFO` | Logging verbosity level |
| `CODEBASE_PATH` | str | - | Path to code for analysis |
| `SANDBOX_IMAGE` | str | `kali-ssh:latest` | Docker image for sandbox |

## Module Reference

::: ivexes.config
    options:
      show_root_heading: false
      show_root_toc_entry: false
      heading_level: 2