# Code Style Guide

Coding standards and style guidelines for IVEXES development.

## Python Style

### PEP 8 Compliance
Follow PEP 8 guidelines with these specific rules:

- Line length: 88 characters (Black default)
- Indentation: 4 spaces
- Quotes: Double quotes for strings

### Code Formatting

Use automated tools:

```bash
# Format code
uv run ruff format

# Check style
uv run ruff check
```

### Import Organization

```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import numpy as np
import requests

# Local imports
from ivexes.agents import BaseAgent
from ivexes.config import Settings
```

## Type Hints

Use type hints throughout the codebase:

```python
from typing import List, Optional, Dict, Any

def analyze_code(code: str, options: Optional[Dict[str, Any]] = None) -> List[str]:
    """Analyze code and return findings."""
    return []
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def process_analysis(data: str, threshold: float = 0.8) -> Dict[str, Any]:
    """Process analysis data and return results.
    
    Args:
        data: The input data to analyze.
        threshold: Confidence threshold for results.
        
    Returns:
        Dictionary containing analysis results.
        
    Raises:
        ValueError: If data is invalid.
    """
    pass
```

### Comments

- Use comments sparingly
- Explain why, not what
- Keep comments up to date

## Naming Conventions

### Variables and Functions
- Use snake_case
- Use descriptive names
- Avoid abbreviations

```python
# Good
user_input_validation = True
max_retry_attempts = 3

# Bad
usr_inp_val = True
max_retry = 3
```

### Classes
- Use PascalCase
- Use nouns for class names

```python
class VulnerabilityScanner:
    pass

class AnalysisResult:
    pass
```

### Constants
- Use UPPER_SNAKE_CASE
- Define in module-level scope

```python
DEFAULT_TIMEOUT = 300
MAX_RETRIES = 3
SUPPORTED_FORMATS = ['json', 'xml', 'yaml']
```

## Error Handling

### Exception Handling

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Specific error occurred: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise RuntimeError(f"Operation failed: {e}") from e
```

### Custom Exceptions

```python
class IvexesError(Exception):
    """Base exception for IVEXES."""
    pass

class ConfigurationError(IvexesError):
    """Configuration-related errors."""
    pass
```

## Security Guidelines

### Input Validation

```python
def process_user_input(user_input: str) -> str:
    if not isinstance(user_input, str):
        raise ValueError("Input must be a string")
    
    if len(user_input) > MAX_INPUT_LENGTH:
        raise ValueError("Input too long")
    
    # Sanitize input
    sanitized = sanitize_input(user_input)
    return sanitized
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def secure_operation(data: str) -> None:
    logger.info("Starting secure operation")
    # Never log sensitive data
    logger.debug(f"Processing data of length {len(data)}")
```

## Testing Style

### Test Naming

```python
def test_agent_analysis_with_valid_input_returns_results():
    pass

def test_agent_analysis_with_invalid_input_raises_error():
    pass
```

### Test Structure

```python
def test_feature():
    # Arrange
    setup_data = create_test_data()
    
    # Act
    result = function_under_test(setup_data)
    
    # Assert
    assert result.status == "success"
    assert len(result.items) == 3
```

## Performance Guidelines

### Efficient Code

```python
# Use list comprehensions when appropriate
results = [process_item(item) for item in items if item.is_valid()]

# Use generators for large datasets
def process_large_dataset(dataset):
    for item in dataset:
        yield process_item(item)
```

### Memory Management

```python
# Use context managers for resource management
with open('file.txt', 'r') as f:
    content = f.read()

# Clean up large objects
large_data = process_data()
result = analyze(large_data)
del large_data  # Explicitly clean up
```

## Configuration

### ruff Configuration

```toml
[tool.ruff]
line-length = 88
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4"]
ignore = ["E501"]  # Line too long (handled by formatter)
```

### mypy Configuration

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Git Commit Style

### Commit Message Format

```
<type>(<scope>): <description>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

### Examples

```
feat(agents): add multi-agent coordination

Implement shared context and message passing between agents
for collaborative analysis workflows.

Closes #123
```

## See Also

- [Development Setup](development.md)
- [Testing Guide](testing.md)