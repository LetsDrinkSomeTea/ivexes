# Quick Start Guide

Get up and running with IVEXES in just a few minutes! This guide will walk you through your first vulnerability analysis.

## Prerequisites

Before starting, ensure you have:

- [x] IVEXES installed ([Installation Guide](installation.md))
- [x] Environment configured ([Configuration Guide](configuration.md))
- [x] API key for LLM access
- [x] Docker running for sandbox functionality

## Your First Analysis

### 1. Verify Installation

First, let's make sure everything is working:

```bash
# Check IVEXES installation
python -c "import ivexes; print('IVEXES is ready!')"

# Verify Docker access
docker ps

# Check configuration
python -c "from ivexes.config import Settings; s = Settings(); print(f'Model: {s.model}')"
```

### 2. Single Agent Analysis

Let's start with a simple single-agent vulnerability analysis:

```python
# quickstart_example.py
import asyncio
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

async def main():
    # Configure the agent
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=5,
        log_level='INFO'
    )
    
    # Create and run agent
    agent = SingleAgent(settings=settings)
    
    # Interactive mode - agent will prompt for input
    await agent.run_interactive()

# Run the example
if __name__ == "__main__":
    asyncio.run(main())
```

Save this as `quickstart_example.py` and run:

```bash
python quickstart_example.py
```

### 3. Analyze a Code Repository

Now let's analyze an actual codebase for vulnerabilities:

```python
# code_analysis_example.py
import asyncio
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

async def analyze_codebase():
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        codebase_path='/path/to/your/project',  # Update this path
        vulnerable_folder='vulnerable-version',
        patched_folder='patched-version',
        max_turns=10
    )
    
    agent = SingleAgent(settings=settings)
    
    # Start with a specific vulnerability analysis query
    initial_message = """
    Please analyze this codebase for potential security vulnerabilities.
    Focus on:
    1. Input validation issues
    2. Authentication bypass
    3. Injection vulnerabilities
    4. Memory safety issues
    
    Provide a comprehensive security assessment.
    """
    
    await agent.run_streamed(initial_message)

if __name__ == "__main__":
    asyncio.run(analyze_codebase())
```

### 4. Multi-Agent Coordination

For complex analysis, use multiple specialized agents:

```python
# multi_agent_example.py
from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings

def multi_agent_analysis():
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        reasoning_model='openai/o4-mini',
        codebase_path='/path/to/complex/project',
        max_turns=15
    )
    
    # Multi-agent system coordinates multiple specialists
    multi_agent = MultiAgent(settings=settings)
    
    # Run comprehensive analysis
    multi_agent.run()

if __name__ == "__main__":
    multi_agent_analysis()
```

## Command Line Interface

IVEXES includes a comprehensive CLI for quick tasks:

```bash
# Get CLI help
python manual.py --help

# Run single agent with specific settings
python manual.py single-agent --model gpt-4o-mini --codebase /path/to/code

# Start multi-agent analysis
python manual.py multi-agent --reasoning-model o4-mini

# Vector database operations
python manual.py vector-db --download-mitre-attack
```

## Common Use Cases

### Security Code Review

```python
async def security_review():
    settings = PartialSettings(
        model='openai/gpt-4',  # Use more powerful model for thorough review
        codebase_path='/path/to/review',
        max_turns=20
    )
    
    agent = SingleAgent(settings=settings)
    
    query = """
    Perform a security-focused code review of this application.
    Check for:
    - OWASP Top 10 vulnerabilities
    - Business logic flaws
    - Access control issues
    - Data validation problems
    
    Provide specific recommendations for each finding.
    """
    
    await agent.run_streamed(query)
```

### CVE Analysis

```python
async def cve_analysis():
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=10
    )
    
    agent = SingleAgent(settings=settings)
    
    query = """
    Analyze CVE-2023-12345 (example):
    1. Understand the vulnerability mechanism
    2. Identify affected code patterns
    3. Suggest detection strategies
    4. Recommend remediation approaches
    
    Use the MITRE ATT&CK framework for context.
    """
    
    await agent.run_interactive()
```

### Penetration Testing Preparation

```python
async def pentest_prep():
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        sandbox_image='kali-ssh:latest',
        codebase_path='/target/application',
        max_turns=15
    )
    
    agent = SingleAgent(settings=settings)
    
    query = """
    Prepare a penetration testing strategy for this application:
    1. Identify attack surfaces
    2. Map potential entry points
    3. Suggest testing methodologies
    4. Recommend tools and techniques
    
    Focus on ethical, authorized testing approaches.
    """
    
    await agent.run_streamed(query)
```

## Interactive Examples

### Exploring Vector Database

```python
from ivexes.vector_db import VectorDatabase

# Initialize vector database
db = VectorDatabase()

# Search for attack patterns
results = db.search("SQL injection", limit=5)
for result in results:
    print(f"Technique: {result['technique']}")
    print(f"Description: {result['description'][:100]}...")
    print("---")

# Find related vulnerabilities
cwe_results = db.search_cwe("improper input validation")
for cwe in cwe_results:
    print(f"CWE-{cwe['id']}: {cwe['name']}")
```

### Code Browser Integration

```python
from ivexes.code_browser import CodeBrowser

async def explore_code():
    browser = CodeBrowser(
        codebase='/path/to/project',
        vulnerable_folder='v1.0',
        patched_folder='v1.1'
    )
    
    # Find security-relevant functions
    functions = await browser.find_functions("authenticate")
    
    for func in functions:
        print(f"Function: {func['name']}")
        print(f"File: {func['file']}:{func['line']}")
        
        # Get function details
        details = await browser.get_function_details(func['name'])
        print(f"Parameters: {details['parameters']}")
        print("---")
```

## Troubleshooting Quick Start

### Common Issues

!!! failure "Import Error"
    ```bash
    # If you see "No module named 'ivexes'"
    pip install -e .
    # Or check if you're in the right virtual environment
    which python
    ```

!!! failure "API Key Error"
    ```bash
    # Ensure your API key is set
    echo $LLM_API_KEY
    # If empty, set it:
    export LLM_API_KEY=your-key-here
    ```

!!! failure "Docker Error"
    ```bash
    # Check Docker is running
    docker ps
    # If not, start Docker service
    sudo systemctl start docker  # Linux
    # Or start Docker Desktop (Windows/Mac)
    ```

!!! failure "Permission Error"
    ```bash
    # Check file permissions
    ls -la /path/to/codebase
    # Ensure IVEXES can read the target directory
    chmod -R 755 /path/to/codebase
    ```

### Performance Tips

1. **Model Selection**: Use `gpt-4o-mini` for faster responses, `gpt-4` for complex analysis
2. **Turn Limits**: Start with lower `max_turns` (5-10) for initial testing
3. **Codebase Size**: Test with smaller projects first (~1000 files or less)
4. **Docker Resources**: Ensure Docker has sufficient memory (4GB+)

## What's Next?

Now that you have IVEXES running:

1. **Learn the Components**: Explore the [User Guide](../user-guide/index.md)
2. **Try Examples**: Check out more [Examples](../examples/index.md)
3. **Understand Architecture**: Read about [System Architecture](../architecture/index.md)
4. **Advanced Usage**: Review the [API Reference](../api/index.md)

## Getting Help

If you need assistance:

- Review the [User Guide](../user-guide/index.md) for detailed component documentation
- Check [Examples](../examples/index.md) for more usage patterns
- Visit [GitHub Issues](https://github.com/LetsDrinkSomeTea/ivexes/issues) for support
- Read the [FAQ](../contributing/index.md#faq) for common questions

---

**Congratulations!** You've successfully run your first IVEXES analysis. The framework is now ready for more advanced vulnerability research and security analysis tasks.