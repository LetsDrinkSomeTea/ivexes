# Examples

This section provides practical examples and tutorials for using IVEXES in various cybersecurity scenarios. Each example includes complete code, configuration, and explanations.

## Available Examples

### Basic Usage

| Example | Description | Difficulty |
|---------|-------------|------------|
| [First Analysis](first-analysis.md) | Your first vulnerability analysis | Beginner |
| [Configuration Examples](configuration-examples.md) | Different configuration patterns | Beginner |
| [Agent Comparison](agent-comparison.md) | Single vs Multi-agent approaches | Intermediate |

### Code Analysis

| Example | Description | Difficulty |
|---------|-------------|------------|
| [Web Application Security](webapp-security.md) | Analyzing web app vulnerabilities | Intermediate |
| [API Security Review](api-security.md) | REST API security assessment | Intermediate |
| [Mobile App Analysis](mobile-security.md) | Mobile application security | Advanced |

### Specialized Scenarios

| Example | Description | Difficulty |
|---------|-------------|------------|
| [CVE Research](cve-research.md) | Researching specific vulnerabilities | Advanced |
| [CTF Challenge Solving](ctf-challenges.md) | Capture The Flag scenarios | Advanced |
| [Incident Response](incident-response.md) | Security incident analysis | Expert |

### Integration Examples

| Example | Description | Difficulty |
|---------|-------------|------------|
| [CI/CD Integration](cicd-integration.md) | Automated security in pipelines | Intermediate |
| [IDE Integration](ide-integration.md) | Using IVEXES with development tools | Intermediate |
| [Custom Workflows](custom-workflows.md) | Building custom analysis workflows | Advanced |

## Example Categories

### 🎯 Quick Start Examples

Perfect for beginners getting started with IVEXES:

- **[Hello IVEXES](first-analysis.md)** - Basic agent interaction
- **[Configuration Basics](configuration-examples.md)** - Setting up your environment
- **[Simple Code Review](simple-review.md)** - First code analysis

### 🔍 Analysis Examples

Real-world vulnerability analysis scenarios:

- **[SQL Injection Detection](sql-injection.md)** - Finding injection vulnerabilities
- **[Authentication Bypass](auth-bypass.md)** - Analyzing authentication flaws
- **[Memory Safety Issues](memory-safety.md)** - Buffer overflows and memory bugs

### 🚀 Advanced Examples

Complex scenarios for experienced users:

- **[Multi-Vector Analysis](multi-vector.md)** - Comprehensive security assessment
- **[Zero-Day Research](zero-day.md)** - Novel vulnerability discovery
- **[Threat Modeling](threat-modeling.md)** - Systematic threat analysis

### 🔧 Integration Examples

Connecting IVEXES with other tools and workflows:

- **[GitHub Actions](github-actions.md)** - Automated security checks
- **[SIEM Integration](siem-integration.md)** - Security monitoring workflows
- **[Custom Dashboards](dashboards.md)** - Visualization and reporting

## Example Structure

Each example follows a consistent structure:

### 📋 Overview
- **Objective**: What you'll learn
- **Prerequisites**: Required knowledge and setup
- **Time**: Estimated completion time
- **Difficulty**: Beginner/Intermediate/Advanced/Expert

### 🔧 Setup
- Configuration requirements
- Environment preparation
- Required files or data

### 📝 Step-by-Step Guide
- Detailed instructions
- Code examples with explanations
- Expected outputs

### 🎯 Results
- What to expect
- How to interpret findings
- Next steps

### 🔗 Related Topics
- Connected examples
- Further reading
- Advanced variations

## Using the Examples

### Prerequisites

Before running examples, ensure you have:

1. **IVEXES installed** - Follow the [Installation Guide](../getting-started/installation.md)
2. **Environment configured** - See [Configuration Guide](../getting-started/configuration.md)
3. **API access** - Valid LLM API key
4. **Docker running** - For sandbox examples

### Running Examples

Most examples can be run in multiple ways:

=== "Interactive Mode"
    ```python
    # Copy the example code
    # Run interactively for exploration
    await agent.run_interactive()
    ```

=== "Script Mode"
    ```python
    # Run as a complete script
    # Good for automated workflows
    await agent.run_streamed(query)
    ```

=== "Notebook Mode"
    ```python
    # Use in Jupyter notebooks
    # Great for learning and experimentation
    from ivexes.agents import SingleAgent
    # ... notebook cells
    ```

### Example Data

Some examples use sample vulnerable code:

- **[DVWA](https://github.com/digininja/DVWA)** - Damn Vulnerable Web Application
- **[WebGoat](https://github.com/WebGoat/WebGoat)** - OWASP WebGoat
- **[Vulnerable Node.js Apps](https://github.com/cr0hn/vulnerable-node)** - Node.js vulnerabilities
- **[C Vulnerability Examples](https://github.com/hardik05/Damn_Vulnerable_C_Program)** - C programming flaws

### Contributing Examples

We welcome community examples! To contribute:

1. **Fork the repository**
2. **Create your example** following the structure above
3. **Test thoroughly** with different configurations
4. **Submit a pull request** with clear documentation

**Example types we're looking for:**
- Industry-specific scenarios (healthcare, finance, etc.)
- Programming language-specific examples
- Tool integration examples
- Educational scenarios for different skill levels

## Best Practices for Examples

### Writing Good Examples

**Clear Objectives:**
- State learning goals upfront
- Explain real-world relevance
- Define success criteria

**Complete Setup:**
- Include all required files
- Specify exact versions
- Provide troubleshooting tips

**Educational Value:**
- Explain the "why" not just the "how"
- Include common mistakes
- Suggest variations and extensions

### Security Considerations

**Ethical Guidelines:**
- Use only authorized test environments
- Clearly mark vulnerable code as examples
- Include proper disclaimers

**Safe Environments:**
- Provide isolated test setups
- Use containerized environments
- Include cleanup instructions

## Quick Reference

### Common Patterns

```python
# Basic analysis pattern
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/path/to/analyze'
)

agent = SingleAgent(settings=settings)
await agent.run_interactive()
```

### Useful Queries

- **"Analyze this code for security vulnerabilities"**
- **"Check for OWASP Top 10 issues"**
- **"Review authentication mechanisms"**
- **"Find input validation problems"**
- **"Suggest security improvements"**

---

**Ready to start?** Begin with [Your First Analysis](first-analysis.md) or jump to any example that matches your interests and skill level.