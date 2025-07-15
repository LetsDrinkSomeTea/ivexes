# User Guide

Welcome to the IVEXES User Guide! This comprehensive guide will help you understand and effectively use all the features of the Intelligent Vulnerability Exploration and Exploitation System.

## What is IVEXES?

IVEXES is an AI-driven cybersecurity framework that combines multiple specialized agents to perform comprehensive vulnerability analysis, code review, and security assessment. It integrates knowledge bases like MITRE ATT&CK, CWE, and CAPEC with dynamic analysis capabilities.

## Core Concepts

### Agents

IVEXES uses AI agents as the primary interface for vulnerability analysis:

- **Single Agent** - Individual analysis with focused expertise
- **Multi Agent** - Coordinated team approach for complex assessments
- **Specialized Agents** - Purpose-built for specific tasks (CTF, MVP, etc.)

### Knowledge Integration

The framework leverages multiple security knowledge bases:

- **MITRE ATT&CK** - Adversary tactics and techniques
- **CWE** - Common Weakness Enumeration
- **CAPEC** - Common Attack Pattern Enumeration
- **CVE Database** - Known vulnerabilities

### Analysis Components

IVEXES provides several analysis capabilities:

- **Code Browser** - LSP-powered code analysis
- **Sandbox Environment** - Safe execution isolation
- **Vector Database** - Similarity search and knowledge retrieval
- **Report Generation** - Structured output and documentation

## Getting Started

If you're new to IVEXES, we recommend following this learning path:

1. **[Installation](../getting-started/installation.md)** - Set up your environment
2. **[Configuration](../getting-started/configuration.md)** - Configure API keys and settings
3. **[Quick Start](../getting-started/quickstart.md)** - Run your first analysis
4. **[Agents Overview](agents.md)** - Understand the agent system
5. **[Single Agent Tutorial](single-agent.md)** - Learn individual agent usage

## Use Cases

### Security Code Review

Use IVEXES to perform comprehensive security reviews of your codebase:

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

settings = PartialSettings(
    model='openai/gpt-4',
    codebase_path='/path/to/your/project',
    max_turns=20
)

agent = SingleAgent(settings=settings)
await agent.run_interactive()
```

**Ask the agent:**
- "Perform a security code review focusing on OWASP Top 10"
- "Analyze authentication and authorization mechanisms"
- "Check for input validation vulnerabilities"

### Vulnerability Research

Research and understand specific vulnerabilities:

```python
query = """
Analyze CVE-2023-1234:
1. Understand the vulnerability mechanism
2. Identify similar patterns in this codebase
3. Suggest detection and remediation strategies
4. Map to MITRE ATT&CK techniques
"""

await agent.run_streamed(query)
```

### Penetration Testing Preparation

Prepare for ethical penetration testing:

```python
settings = PartialSettings(
    model='openai/gpt-4o-mini',
    sandbox_image='kali-ssh:latest',
    codebase_path='/target/application'
)

agent = SingleAgent(settings=settings)
```

**Ask the agent:**
- "Identify potential attack vectors in this application"
- "Suggest penetration testing methodologies"
- "Create a test plan for this web application"

### Educational Research

Use IVEXES for cybersecurity education and research:

- Understand vulnerability classes and patterns
- Learn about attack techniques and mitigations
- Explore security best practices
- Analyze real-world security issues

## Best Practices

### Security and Ethics

!!! danger "Ethical Use Only"
    IVEXES is designed for defensive security, education, and authorized testing only. Always ensure you have proper authorization before analyzing any system.

**Guidelines:**
- Only analyze systems you own or have explicit permission to test
- Use IVEXES for defensive security purposes
- Follow responsible disclosure for any findings
- Respect privacy and confidentiality

### Effective Agent Interaction

**Clear Communication:**
- Be specific about your analysis goals
- Provide context about the target system
- Ask follow-up questions for clarification

**Structured Queries:**
- Break complex requests into steps
- Use numbered lists for multiple requirements
- Reference specific files or functions when relevant

**Example Good Query:**
```
Please analyze the authentication system in this web application:
1. Review the login mechanism in auth.py
2. Check for common authentication bypasses
3. Analyze session management in session.py
4. Identify any privilege escalation opportunities
5. Suggest security improvements with code examples
```

### Performance Optimization

**Model Selection:**
- Use `gpt-4o-mini` for quick analysis and exploration
- Use `gpt-4` for complex, thorough security reviews
- Adjust `max_turns` based on analysis complexity

**Resource Management:**
- Start with smaller codebases for testing
- Use specific file patterns to focus analysis
- Monitor token usage for cost control

## Advanced Features

### Multi-Agent Coordination

For complex analysis requiring multiple perspectives:

```python
from ivexes.agents import MultiAgent

multi_agent = MultiAgent(settings=settings)
multi_agent.run()  # Agents coordinate automatically
```

### Custom Configurations

Tailor IVEXES for specific environments:

```python
# Research configuration
research_settings = PartialSettings(
    model='openai/gpt-4',
    reasoning_model='openai/o4-mini',
    max_turns=30,
    enable_vector_db=True
)

# Quick review configuration  
quick_settings = PartialSettings(
    model='openai/gpt-4o-mini',
    max_turns=10,
    log_level='WARNING'
)
```

### Integration with Development Workflows

Integrate IVEXES into your security workflows:

- **CI/CD Integration** - Automated security checks
- **Code Review Process** - AI-assisted security reviews
- **Incident Response** - Rapid vulnerability analysis
- **Security Training** - Interactive learning experiences

## Troubleshooting

### Common Issues

**Agent Not Responding:**
- Check API key configuration
- Verify model availability
- Review network connectivity

**Poor Analysis Quality:**
- Use more specific queries
- Provide additional context
- Try a more powerful model

**Performance Issues:**
- Reduce `max_turns` for quicker responses
- Use smaller code samples for testing
- Check system resources

### Getting Help

- **[Examples](../examples/index.md)** - Practical usage examples
- **[API Reference](../api/index.md)** - Detailed technical documentation
- **[GitHub Issues](https://github.com/LetsDrinkSomeTea/ivexes/issues)** - Report bugs and request features

## What's Next?

Explore specific components in detail:

- **[Agents](agents.md)** - Deep dive into agent capabilities
- **[Code Browser](code-browser.md)** - Advanced code analysis features
- **[Sandbox](sandbox.md)** - Safe execution environments
- **[Vector Database](vector-db.md)** - Knowledge base integration

---

**Ready to dive deeper?** Choose a specific component from the navigation menu or continue with the [Agents Overview](agents.md).