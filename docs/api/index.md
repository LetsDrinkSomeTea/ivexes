# API Reference

This section provides comprehensive documentation for all IVEXES classes, functions, and modules. The API documentation is automatically generated from the source code docstrings.

## Package Structure

IVEXES is organized into several key modules:

### Core Modules

| Module | Description |
|--------|-------------|
| [`ivexes.agents`](agents.md) | AI agent implementations for vulnerability analysis |
| [`ivexes.config`](config.md) | Configuration management and settings |
| [`ivexes.tools`](tools.md) | Utility functions and helper tools |
| [`ivexes.exceptions`](exceptions.md) | Custom exception classes |

### Analysis Components

| Module | Description |
|--------|-------------|
| [`ivexes.code_browser`](code-browser.md) | Code analysis and LSP integration |
| [`ivexes.sandbox`](sandbox.md) | Isolated execution environments |
| [`ivexes.vector_db`](vector-db.md) | Knowledge base and vector database |
| [`ivexes.cve_search`](cve-search.md) | CVE lookup and vulnerability search |

### Support Modules

| Module | Description |
|--------|-------------|
| [`ivexes.printer`](printer.md) | Output formatting and display |
| [`ivexes.prompts`](prompts.md) | Agent prompt templates |
| [`ivexes.report`](report.md) | Report generation utilities |
| [`ivexes.date`](date.md) | Date and time utilities |

## Quick Navigation

### Most Used Classes

- **[`SingleAgent`](agents.md#ivexes.agents.single_agent.SingleAgent)** - Individual vulnerability analysis agent
- **[`MultiAgent`](agents.md#ivexes.agents.multi_agent.MultiAgent)** - Coordinated multi-agent analysis
- **[`Settings`](config.md#ivexes.config.settings.Settings)** - Configuration management
- **[`CodeBrowser`](code-browser.md#ivexes.code_browser.code_browser.CodeBrowser)** - Code analysis interface
- **[`VectorDatabase`](vector-db.md#ivexes.vector_db.vector_db.VectorDatabase)** - Knowledge base interface

### Key Functions

- **[`create_agent()`](agents.md#ivexes.agents.create_agent)** - Factory function for creating agents
- **[`setup_logging()`](config.md#ivexes.config.log.setup_logging)** - Configure logging system
- **[`search_cve()`](cve-search.md#ivexes.cve_search.tools.search_cve)** - Search CVE database

## Usage Patterns

### Basic Agent Creation

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

# Create agent with custom settings
settings = PartialSettings(model='openai/gpt-4o-mini')
agent = SingleAgent(settings=settings)
```

### Configuration Management

```python
from ivexes.config import Settings

# Load configuration from environment
settings = Settings()
print(f"Using model: {settings.model}")
```

### Code Analysis

```python
from ivexes.code_browser import CodeBrowser

# Analyze codebase
browser = CodeBrowser(codebase='/path/to/code')
results = await browser.analyze_security_patterns()
```

## Type Annotations

IVEXES makes extensive use of Python type hints for better code clarity and IDE support. All public APIs include comprehensive type annotations:

```python
from typing import List, Optional, Dict, Any
from ivexes.agents.base import BaseAgent

def create_agent(
    agent_type: str,
    settings: Optional[PartialSettings] = None,
    **kwargs: Any
) -> BaseAgent:
    """Create an agent instance of the specified type."""
    ...
```

## Error Handling

IVEXES defines custom exception classes for different error conditions:

```python
from ivexes.exceptions import (
    IvexesError,           # Base exception
    ConfigurationError,    # Configuration issues
    AgentError,           # Agent-related errors
    SandboxError,         # Sandbox execution errors
)

try:
    agent = SingleAgent(settings=invalid_settings)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Async/Await Support

Many IVEXES operations are asynchronous for better performance:

```python
import asyncio
from ivexes.agents import SingleAgent

async def main():
    agent = SingleAgent()
    result = await agent.run_interactive()
    return result

# Run async function
result = asyncio.run(main())
```

## Deprecation Notices

!!! warning "Deprecated APIs"
    Some APIs are marked as deprecated and will be removed in future versions:
    
    - `legacy_function()` - Use `new_function()` instead
    - `OldClass` - Replaced by `NewClass`

## Contributing to API Documentation

The API documentation is automatically generated from docstrings. To improve it:

1. Follow [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
2. Include type hints for all parameters and return values
3. Provide examples for complex functions
4. Document exceptions that may be raised

Example docstring format:

```python
def example_function(param1: str, param2: int = 10) -> List[str]:
    """Brief description of the function.

    Longer description providing more details about what the function
    does and how to use it.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter with default value.

    Returns:
        A list of strings containing the results.

    Raises:
        ValueError: If param1 is empty.
        TypeError: If param2 is not an integer.

    Example:
        Basic usage example:

        >>> result = example_function("hello", 5)
        >>> print(result)
        ['hello', 'world']
    """
    ...
```

---

**Browse the modules** using the navigation menu or search for specific functions using the search box above.