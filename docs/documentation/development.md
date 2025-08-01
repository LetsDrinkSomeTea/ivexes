# Development Guide

## Overview

This guide provides comprehensive information for developers who want to contribute to IVEXES or extend the system with custom functionality. It covers development setup, coding standards, testing guidelines, and best practices for creating custom agents and tools.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose
- Git for version control
- uv package manager (recommended) or pip

### Environment Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/LetsDrinkSomeTea/ivexes.git
   cd ivexes
   ```

2. **Install Development Dependencies**
   ```bash
   # Using uv (recommended)
   uv sync --all-extras --all-packages --group dev
   
   # Or using make
   make sync
   
   # Or using pip (legacy)
   pip install -e ".[dev]"
   ```

3. **Setup Container Images**
   ```bash
   # Build all required Docker images
   make build-images
   
   # Or manually
   docker compose --profile images build
   ```

4. **Start LiteLLM Proxy**
   ```bash
   # Start background services
   make run-litellm
   
   # Or manually
   docker compose up -d
   ```

5. **Complete Setup (All-in-One)**
   ```bash
   # Combines all setup steps
   make setup
   ```

### Environment Configuration

Create a `.env` file for development settings:

```bash
# LLM Configuration
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=http://localhost:4000
MODEL=openai/gpt-4o-mini
REASONING_MODEL=openai/o4-mini
TEMPERATURE=0.3

# Development Settings
LOG_LEVEL=DEBUG
TRACE_NAME=ivexes-dev

# Embedding Configuration
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=intfloat/multilingual-e5-large-instruct
CHROMA_PATH=/tmp/ivexes/chromadb

# Development Paths
CODEBASE_PATH=/path/to/test/codebase
VULNERABLE_CODEBASE_FOLDER=vulnerable-version
PATCHED_CODEBASE_FOLDER=patched-version
```

Create a `.secrets.env` file for sensitive data (never commit this):

```bash
# API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Database Credentials
DATABASE_URL=postgresql://user:pass@localhost:5432/ivexes
```

## Code Standards and Style

### Code Formatting

IVEXES uses Ruff for code formatting and linting with Google-style docstrings.

```bash
# Format code
make format
# Or manually:
uv run ruff format
uv run ruff check --fix

# Check formatting without changes
make format-check
# Or manually:
uv run ruff format --check

# Run linter only
make lint
# Or manually:
uv run ruff check
```

### Code Style Guidelines

1. **Docstring Convention**: Use Google-style docstrings
   ```python
   def analyze_vulnerability(cve_id: str, severity: str) -> Dict[str, Any]:
       """Analyze vulnerability details and impact.
       
       Args:
           cve_id: CVE identifier (e.g., 'CVE-2021-44228')
           severity: Vulnerability severity level
           
       Returns:
           Dictionary containing analysis results with keys:
           - 'impact': Impact assessment
           - 'exploitability': Exploitability score
           - 'recommendations': Mitigation recommendations
           
       Raises:
           ValueError: If CVE ID format is invalid
           NetworkError: If CVE database is unreachable
       """
   ```

2. **Type Annotations**: Use comprehensive type hints
   ```python
   from typing import Optional, Dict, List, Any, Union
   
   class VulnerabilityAnalyzer:
       def __init__(self, settings: PartialSettings) -> None:
           self.settings: Settings = create_settings(settings)
           self.results: List[Dict[str, Any]] = []
   ```

3. **Error Handling**: Use specific exceptions with clear messages
   ```python
   from ivexes.exceptions import IvexesError, ConfigurationError
   
   def validate_config(settings: Settings) -> None:
       """Validate configuration settings."""
       if not settings.llm_api_key:
           raise ConfigurationError(
               "LLM_API_KEY is required but not provided. "
               "Set it in environment variables or .secrets.env file."
           )
   ```

4. **Import Organization**: Follow PEP 8 import ordering
   ```python
   # Standard library imports
   import asyncio
   import json
   from pathlib import Path
   from typing import Dict, List, Optional
   
   # Third-party imports
   from agents import Agent, tool
   from pydantic import BaseModel
   
   # Local application imports
   from ..config import PartialSettings, Settings
   from ..exceptions import IvexesError
   from .base import BaseAgent
   ```

### Pre-commit Hooks

IVEXES uses pre-commit hooks to enforce code quality:

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

The pre-commit configuration includes:
- Ruff formatting and linting
- Trailing whitespace removal
- End-of-file fixing
- Large file detection

## Testing Guidelines

### Test Structure

Tests are organized in the `tests/cases/` directory using Python's unittest framework:

```
tests/
├── cases/
│   ├── __init__.py
│   ├── test_config.py       # Configuration testing
│   ├── test_container.py    # Container utilities testing
│   ├── test_downloader.py   # Data downloader testing
│   ├── test_embed.py        # Embedding functionality testing
│   ├── test_parser.py       # Parser testing
│   └── test_sandbox.py      # Sandbox testing
└── run_tests.py             # Test runner
```

### Running Tests

```bash
# Run all tests
make tests

# Or manually
uv run python -m unittest discover -s tests -v

# Run specific test file
uv run python -m unittest tests.cases.test_config -v

# Run with legacy test runner
uv run python tests/run_tests.py
```

### Writing Tests

1. **Test Class Structure**
   ```python
   """Test module for configuration functionality."""
   
   import unittest
   import tempfile
   from pathlib import Path
   
   from ivexes.config import Settings, PartialSettings, create_settings
   
   class TestConfiguration(unittest.TestCase):
       """Test cases for configuration management."""
       
       def setUp(self) -> None:
           """Set up test fixtures."""
           self.temp_dir = tempfile.mkdtemp()
           self.settings = PartialSettings(
               model='test/model',
               temperature=0.5
           )
       
       def tearDown(self) -> None:
           """Clean up test fixtures."""
           # Cleanup code here
           pass
       
       def test_settings_creation(self) -> None:
           """Test settings object creation."""
           settings = create_settings(self.settings)
           self.assertEqual(settings.model, 'test/model')
           self.assertEqual(settings.temperature, 0.5)
       
       def test_invalid_temperature(self) -> None:
           """Test validation of invalid temperature values."""
           with self.assertRaises(ValueError):
               create_settings(PartialSettings(temperature=5.0))
   
   if __name__ == '__main__':
       unittest.main()
   ```

2. **Async Test Support**
   ```python
   import asyncio
   import unittest
   
   class TestAsyncAgent(unittest.TestCase):
       """Test cases for async agent functionality."""
       
       def setUp(self) -> None:
           """Set up async test environment."""
           self.loop = asyncio.new_event_loop()
           asyncio.set_event_loop(self.loop)
       
       def tearDown(self) -> None:
           """Clean up async test environment."""
           self.loop.close()
       
       def test_async_agent_run(self) -> None:
           """Test async agent execution."""
           async def run_test():
               agent = TestAgent()
               result = await agent.run()
               self.assertIsNotNone(result)
           
           self.loop.run_until_complete(run_test())
   ```

3. **Mock External Dependencies**
   ```python
   import unittest
   from unittest.mock import Mock, patch
   
   class TestExternalIntegration(unittest.TestCase):
       """Test external service integration."""
       
       @patch('ivexes.vector_db.ChromaDB')
       def test_vector_db_integration(self, mock_chroma):
           """Test vector database integration with mocked ChromaDB."""
           mock_collection = Mock()
           mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
           
           # Test your integration
           from ivexes.vector_db import VectorDB
           db = VectorDB()
           db.query('test query')
           
           mock_collection.query.assert_called_once()
   ```

### Test Quality Standards

- **Coverage**: Aim for >80% code coverage
- **Isolation**: Each test should be independent
- **Clarity**: Test names should clearly describe what is being tested
- **Speed**: Unit tests should run quickly (<1s per test)
- **Reliability**: Tests should be deterministic and not flaky

## Creating Custom Agents

### Agent Architecture

All agents inherit from `BaseAgent` which provides common functionality:

```python
"""Custom agent implementation example."""

from typing import Optional, List
from agents import Agent, tool

from ivexes.agents.base import BaseAgent
from ivexes.config import PartialSettings
from ivexes.sandbox.tools import create_sandbox_tools
from ivexes.vector_db import create_vectordb_tools

class CustomSecurityAgent(BaseAgent):
    """Custom agent for specialized security analysis."""
    
    def __init__(self, target: str, settings: Optional[PartialSettings] = None):
        """Initialize custom security agent.
        
        Args:
            target: Target system or application to analyze
            settings: Optional configuration settings
        """
        self.target = target
        super().__init__(settings or {})
    
    def _setup_agent(self) -> None:
        """Set up the custom agent with specialized tools and prompts."""
        # Create custom system message
        self.system_msg = f"""
        You are a specialized security analyst focused on {self.target}.
        
        Your capabilities include:
        - Static code analysis
        - Dynamic behavior analysis  
        - Vulnerability assessment
        - Exploit development
        - Security recommendations
        
        Use the available tools systematically to conduct thorough analysis.
        """
        
        # Set up tools
        tools = self._create_tools()
        
        # Create agent with specialized configuration
        self.agent = Agent(
            model=self.settings.model,
            tools=tools,
            system_message=self.system_msg,
            max_turns=self.settings.max_turns,
            temperature=self.settings.temperature
        )
        
        # Set initial user message
        self.user_msg = f"Analyze {self.target} for security vulnerabilities."
    
    def _create_tools(self) -> List:
        """Create specialized tool set for this agent."""
        tools = []
        
        # Add standard tools
        if self.settings.enable_sandbox:
            tools.extend(create_sandbox_tools(self.settings))
        
        if self.settings.enable_vector_db:
            tools.extend(create_vectordb_tools(self.settings))
        
        # Add custom tools
        tools.extend(self._create_custom_tools())
        
        return tools
    
    def _create_custom_tools(self) -> List:
        """Create custom tools specific to this agent."""
        @tool
        def custom_security_scan(target_path: str) -> dict:
            """Run custom security scan on target.
            
            Args:
                target_path: Path to scan for security issues
                
            Returns:
                Dictionary with scan results
            """
            # Implementation of custom security scanning logic
            return {
                'target': target_path,
                'vulnerabilities': [],
                'recommendations': []
            }
        
        @tool
        def generate_exploit_template(vulnerability_type: str) -> str:
            """Generate exploit template for vulnerability type.
            
            Args:
                vulnerability_type: Type of vulnerability (e.g., 'buffer_overflow')
                
            Returns:
                Exploit template code
            """
            templates = {
                'buffer_overflow': '''
                # Buffer Overflow Exploit Template
                import struct
                
                def create_payload():
                    buffer = b"A" * 100  # Adjust buffer size
                    return buffer
                ''',
                'sql_injection': '''
                # SQL Injection Exploit Template
                payload = "' OR '1'='1' --"
                '''
            }
            
            return templates.get(vulnerability_type, "# No template available")
        
        return [custom_security_scan, generate_exploit_template]

# Usage example
async def main():
    """Example usage of custom agent."""
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=20,
        enable_sandbox=True,
        enable_vector_db=True
    )
    
    agent = CustomSecurityAgent(
        target='web-application',
        settings=settings
    )
    
    await agent.run_interactive()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

### Agent Best Practices

1. **Clear Responsibility**: Each agent should have a well-defined purpose
2. **Tool Selection**: Choose appropriate tools for the agent's domain
3. **Error Handling**: Implement robust error handling and recovery
4. **Documentation**: Provide comprehensive docstrings and examples
5. **Testing**: Write unit tests for custom agent functionality

## Creating Custom Tools

### Tool Development Pattern

```python
"""Custom tool implementation example."""

from typing import Dict, Any, List
from agents import tool
from pathlib import Path

@tool
def analyze_binary_strings(binary_path: str, min_length: int = 4) -> Dict[str, Any]:
    """Extract and analyze strings from binary file.
    
    Args:
        binary_path: Path to binary file to analyze
        min_length: Minimum string length to extract
        
    Returns:
        Dictionary containing:
        - 'strings': List of extracted strings
        - 'interesting': List of potentially interesting strings
        - 'count': Total number of strings found
        
    Raises:
        FileNotFoundError: If binary file doesn't exist
        PermissionError: If binary file can't be read
    """
    import re
    import string
    
    binary_file = Path(binary_path)
    if not binary_file.exists():
        raise FileNotFoundError(f"Binary file not found: {binary_path}")
    
    try:
        with open(binary_file, 'rb') as f:
            data = f.read()
    except PermissionError as e:
        raise PermissionError(f"Cannot read binary file: {e}")
    
    # Extract printable strings
    printable = set(string.printable) - set('\t\n\r\x0b\x0c')
    strings = []
    current_string = ""
    
    for byte in data:
        char = chr(byte)
        if char in printable:
            current_string += char
        else:
            if len(current_string) >= min_length:
                strings.append(current_string)
            current_string = ""
    
    # Add final string if it meets criteria
    if len(current_string) >= min_length:
        strings.append(current_string)
    
    # Identify interesting strings
    interesting_patterns = [
        r'password',
        r'key',
        r'token',
        r'secret',
        r'api',
        r'config',
        r'admin',
        r'root',
        r'http[s]?://',
        r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses
        r'[a-zA-Z0-9+/]{20,}={0,2}',  # Base64-like
    ]
    
    interesting = []
    for string_val in strings:
        for pattern in interesting_patterns:
            if re.search(pattern, string_val, re.IGNORECASE):
                interesting.append(string_val)
                break
    
    return {
        'strings': strings,
        'interesting': interesting,
        'count': len(strings),
        'file': str(binary_file)
    }

@tool
def calculate_entropy(data: str) -> float:
    """Calculate Shannon entropy of given data.
    
    Args:
        data: String data to analyze
        
    Returns:
        Entropy value (0.0 to 8.0, higher = more random)
    """
    import math
    from collections import Counter
    
    if not data:
        return 0.0
    
    # Count character frequencies
    char_counts = Counter(data)
    data_len = len(data)
    
    # Calculate entropy
    entropy = 0.0
    for count in char_counts.values():
        probability = count / data_len
        if probability > 0:
            entropy -= probability * math.log2(probability)
    
    return entropy

# Tool integration example
def create_binary_analysis_tools() -> List:
    """Create tools for binary analysis."""
    return [
        analyze_binary_strings,
        calculate_entropy,
    ]
```

### Tool Guidelines

1. **Single Responsibility**: Each tool should do one thing well
2. **Clear Interface**: Use descriptive names and comprehensive docstrings
3. **Error Handling**: Handle expected errors gracefully
4. **Type Safety**: Use type hints for all parameters and return values
5. **Testing**: Write unit tests for tool functionality

## Contributing Workflow

### Git Workflow

1. **Fork and Clone**
   ```bash
   # Fork repository on GitHub, then:
   git clone https://github.com/yourusername/ivexes.git
   cd ivexes
   git remote add upstream https://github.com/LetsDrinkSomeTea/ivexes.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Development Cycle**
   ```bash
   # Make changes
   git add .
   git commit -m "feat: add new vulnerability detection capability"
   
   # Run quality checks
   make check  # format-check + lint + tests
   
   # Push changes
   git push origin feature/your-feature-name
   ```

4. **Pull Request Process**
   - Create pull request on GitHub
   - Ensure all CI checks pass
   - Request review from maintainers
   - Address feedback and update as needed

### Commit Message Convention

Use conventional commit format:

```
type(scope): brief description

Detailed explanation if needed.

- Additional details
- Breaking changes noted with BREAKING CHANGE:
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `ci`: CI/CD changes

Examples:
```
feat(agents): add custom vulnerability detection agent

Add specialized agent for detecting custom vulnerability patterns
in legacy C applications.

- Implements static analysis capabilities
- Integrates with existing sandbox tools
- Includes comprehensive test coverage

fix(sandbox): resolve container cleanup issue

Containers were not being properly cleaned up after analysis,
causing resource leaks in long-running sessions.

docs(api): update agent API documentation

- Add examples for custom agent development
- Clarify tool integration patterns
- Fix broken cross-references
```

### Code Review Guidelines

**For Contributors:**
- Write clear, self-documenting code
- Include comprehensive tests
- Update documentation as needed
- Keep changes focused and atomic
- Respond promptly to review feedback

**For Reviewers:**
- Check code functionality and design
- Verify test coverage and quality
- Ensure documentation is updated
- Review security implications
- Provide constructive feedback

## Documentation Development

### MkDocs Setup

IVEXES uses MkDocs with Material theme for documentation:

```bash
# Build documentation
make build-docs

# Serve locally for development
make serve-docs

# Deploy to GitHub Pages
make deploy-docs
```

### Documentation Standards

1. **Structure**: Follow the established template patterns
2. **Examples**: Include working code examples
3. **Cross-references**: Link related sections appropriately
4. **API Documentation**: Use docstrings as the source of truth
5. **Clarity**: Write for both beginners and experts

### Adding New Documentation

1. Create new markdown files in appropriate directory
2. Update `mkdocs.yml` navigation structure
3. Add cross-references from related pages
4. Test documentation builds without errors
5. Verify all code examples work

## Architecture Guidelines

### Design Principles

1. **Modularity**: Components should be loosely coupled
2. **Extensibility**: Easy to add new agents and tools
3. **Testability**: Design for easy unit testing
4. **Security**: Security-first approach to all components
5. **Performance**: Optimize for analysis speed and accuracy

### Component Interaction

```python
"""Example of proper component interaction."""

from typing import Protocol, runtime_checkable

@runtime_checkable
class AnalysisProvider(Protocol):
    """Protocol for analysis providers."""
    
    async def analyze(self, target: str) -> Dict[str, Any]:
        """Analyze target and return results."""
        ...

class VulnerabilityAnalyzer:
    """Vulnerability analyzer with pluggable providers."""
    
    def __init__(self, providers: List[AnalysisProvider]):
        self.providers = providers
    
    async def comprehensive_analysis(self, target: str) -> Dict[str, Any]:
        """Run analysis using all available providers."""
        results = {}
        
        for provider in self.providers:
            try:
                provider_result = await provider.analyze(target)
                results[provider.__class__.__name__] = provider_result
            except Exception as e:
                results[provider.__class__.__name__] = {'error': str(e)}
        
        return results
```

### Performance Considerations

1. **Async Programming**: Use async/await for I/O operations
2. **Resource Management**: Properly clean up containers and connections
3. **Memory Usage**: Monitor memory usage in long-running analyses
4. **Caching**: Cache expensive operations where appropriate
5. **Parallelization**: Use concurrent execution where possible

## Troubleshooting Development Issues

### Common Issues

1. **Docker Permission Issues**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Log out and back in, or:
   newgrp docker
   ```

2. **LiteLLM Connection Issues**
   ```bash
   # Check container status
   docker compose ps
   
   # View logs
   docker compose logs litellm
   
   # Restart services
   docker compose restart
   ```

3. **Import Errors**
   ```bash
   # Ensure package is installed in development mode
   uv sync --all-extras --all-packages --group dev
   
   # Check Python path
   python -c "import sys; print('\n'.join(sys.path))"
   ```

4. **Test Failures**
   ```bash
   # Run specific test with verbose output
   uv run python -m unittest tests.cases.test_config.TestConfiguration.test_specific_method -v
   
   # Check test isolation
   uv run python -m unittest tests.cases.test_config -v
   ```

### Debugging Tips

1. **Use Logging**: Add debug logging to understand execution flow
2. **Test Isolation**: Run tests individually to isolate issues
3. **Container Inspection**: Use `docker exec` to inspect containers
4. **Environment Variables**: Double-check environment configuration
5. **Dependencies**: Verify all dependencies are correctly installed

## Performance Optimization

### Profiling

```python
"""Performance profiling example."""

import cProfile
import pstats
from typing import Any

def profile_agent_execution(agent: BaseAgent, target: str) -> Any:
    """Profile agent execution for performance analysis."""
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        result = asyncio.run(agent.run())
    finally:
        profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
    
    return result
```

### Optimization Strategies

1. **Tool Selection**: Use appropriate tools for each task
2. **Parallel Execution**: Run independent operations concurrently
3. **Resource Pooling**: Reuse expensive resources like containers
4. **Caching**: Cache results of expensive computations
5. **Memory Management**: Monitor and optimize memory usage

## Related Topics

- [Architecture Guide](architecture.md) - System design and components
- [Installation Guide](installation.md) - Setup and configuration
- [Examples Guide](examples.md) - Practical usage examples
- [API Reference](../api/agents.md) - Detailed API documentation

## Next Steps

1. **Set up Development Environment**: Follow the setup instructions
2. **Explore Codebase**: Read existing agent implementations
3. **Write Tests**: Practice with unit test development
4. **Create Custom Agent**: Develop a specialized agent for your use case
5. **Contribute**: Submit improvements and new features

For questions or support, please create issues in the GitHub repository or reach out to the maintainers.