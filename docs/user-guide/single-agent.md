# Single Agent

The Single Agent provides focused, deterministic security analysis through a direct interaction model.

## Key Features

- **Focused Analysis**: Designed for specific security tasks and vulnerability research
- **Deterministic Behavior**: Consistent results for repeatable analysis
- **Specialized Prompts**: Task-specific prompts for different security scenarios
- **Resource Efficient**: Optimized for single-threaded analysis

## Use Cases

### Vulnerability Research
- CVE analysis and reproduction
- Exploit development assistance
- Security patch analysis

### Code Review
- Static analysis of specific components
- Security-focused code auditing
- Compliance checking

### CTF Challenges
- Binary analysis and reverse engineering
- Cryptographic challenge solving
- Web application security testing

## Configuration

The single agent can be configured with:

```python
from ivexes.agents.single_agent import SingleAgent
from ivexes.config import PartialSettings

settings = PartialSettings(
    # Agent-specific configuration
    max_iterations=50,
    tools_enabled=["sandbox", "code_browser"],
    # Add other configuration options
)

agent = SingleAgent(settings=settings)
```

## Example Usage

```python
# Initialize single agent
agent = SingleAgent()

# Run analysis
result = agent.run("Analyze this binary for buffer overflow vulnerabilities")

# Access results
print(result.findings)
print(result.recommendations)
```

## Best Practices

1. **Define Clear Objectives**: Provide specific, focused analysis goals
2. **Use Appropriate Tools**: Enable only the tools needed for your analysis
3. **Set Resource Limits**: Configure timeouts and iteration limits
4. **Review Results**: Always validate agent findings manually

## Limitations

- Single perspective analysis
- No collaborative capabilities
- Limited parallel processing
- May miss complex multi-stage attacks

## See Also

- [Multi Agent Guide](multi-agent.md)
- [Agent Configuration](agents.md)
- [API Reference](../api/agents.md)