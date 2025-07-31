# Agents API Reference

## Overview

The agents module provides the core intelligence layer of IVEXES, implementing various analysis strategies through specialized AI agents. Each agent is designed for specific vulnerability analysis tasks, from individual assessments to complex multi-agent orchestrations.

The agents system follows a hierarchical architecture with a common base class that provides shared functionality, and specialized implementations for different analysis scenarios.

## Base Classes

### BaseAgent

The foundational abstract class that provides common functionality for all agents in the system.

```python
from ivexes.agents import BaseAgent
from ivexes.config import PartialSettings
```

#### Class Definition

```python
class BaseAgent(ABC):
    """Base class for all agents providing common functionality and interface.
    
    This abstract base class defines the common interface and functionality
    for all agents in the system. It handles settings management, agent
    initialization, and provides different execution modes.
    """
```

#### Constructor

```python
def __init__(self, settings: PartialSettings):
    """Initialize the base agent with settings.
    
    Args:
        settings: Partial settings to configure the agent. Settings not provided
            will be loaded from environment variables.
    """
```

#### Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `settings` | `Settings` | Complete configuration settings |
| `turns_left` | `int` | Remaining conversation turns |
| `agent` | `Optional[Agent]` | Underlying AI agent instance |
| `user_msg` | `Optional[str]` | Default user message |
| `session` | `SQLiteSession` | Session tracking database |
| `code_browser` | `Optional[CodeBrowser]` | Code analysis service |
| `printer` | `Printer` | Output formatting service |
| `vector_db` | `CweCapecAttackDatabase` | Vector database service |

#### Core Methods

##### Abstract Methods

```python
@abstractmethod
def _setup_agent(self):
    """Set up the agent instance.
    
    This method must be implemented by subclasses to initialize the agent
    and user message. Should set self.agent and self.user_msg.
    
    Raises:
        NotImplementedError: If not implemented by subclass.
    """
```

##### Execution Methods

```python
def run(self, user_msg: Optional[str] = None) -> RunResult:
    """Run the agent synchronously.
    
    Args:
        user_msg: Optional user message to override the default.
        
    Returns:
        RunResult: The result of the agent execution.
    """

def run_p(self, user_msg: Optional[str] = None) -> None:
    """Run the agent synchronously and print the result.
    
    Args:
        user_msg: Optional user message to override the default.
    """

def run_streamed(self, user_msg: Optional[str] = None) -> RunResultStreaming:
    """Run the agent with streaming results.
    
    Args:
        user_msg: Optional user message to override the default.
        
    Returns:
        RunResultStreaming: The streaming result of the agent execution.
    """

async def run_streamed_p(self, user_msg: Optional[str] = None) -> None:
    """Run the agent with streaming output.
    
    Args:
        user_msg: Optional user message to override the default.
    """

async def run_interactive(
    self,
    user_msg: Optional[str] = None,
    result_hook: Callable[[RunResultStreaming], None] | None = None,
) -> None:
    """Run the agent in interactive mode with continuous user input.
    
    Allows users to have a conversation with the agent. The session continues
    until the user types 'exit', 'quit', or 'q'.
    
    Args:
        user_msg: Optional user message to override the default.
        result_hook: Optional callback function to process results.
    """
```

##### Utility Methods

```python
def _check_settings(self, user_msg: Optional[str]):
    """Validate that agent and user message are properly configured.
    
    Raises:
        ValueError: If agent or user_msg are not set.
    """

def _get_runner_config(self) -> Dict[str, Any]:
    """Get common Runner configuration parameters.
    
    Returns:
        Dict containing common Runner parameters.
    """
```

#### Usage Example

```python
from ivexes.agents import BaseAgent
from ivexes.config import PartialSettings

class CustomAgent(BaseAgent):
    def _setup_agent(self):
        # Configure your custom agent
        self.user_msg = "Analyze this code for vulnerabilities"
        self.agent = Agent(
            name="Custom",
            instructions="You are a custom security analyst",
            tools=custom_tools
        )

# Usage
settings = PartialSettings(model='openai/gpt-4o-mini')
agent = CustomAgent(settings)
result = agent.run()
```

## Specialized Agent Classes

### SingleAgent

A comprehensive agent for individual vulnerability analysis with full toolset integration.

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings
```

#### Class Definition

```python
class SingleAgent(BaseAgent):
    """Agent specialized for single agent analysis tasks.
    
    This agent is configured with sandbox tools, code browser tools,
    and vector database tools for comprehensive analysis.
    """
```

#### Constructor

```python
def __init__(self, bin_path: str, settings: Optional[PartialSettings] = None):
    """Initialize Single Agent.
    
    Args:
        bin_path: Path to the binary to analyze inside the sandbox
        settings: Optional partial settings to configure the agent
    """
```

#### Features

- **Comprehensive Toolset**: Sandbox, code browser, vector database, CVE search
- **Code Analysis**: Source code structure analysis and diff comparison
- **Dynamic Testing**: Isolated sandbox execution environment
- **Knowledge Integration**: Access to CWE, CAPEC, MITRE ATT&CK databases
- **Vulnerability Search**: Real-time CVE lookup and correlation

#### Required Configuration

The SingleAgent requires specific configuration settings:

```python
settings = PartialSettings(
    codebase_path="/path/to/code",
    vulnerable_folder="vulnerable-version",
    patched_folder="patched-version"
)
```

#### Usage Example

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/path/to/analysis',
    vulnerable_folder='vuln-v1.0',
    patched_folder='patched-v1.1'
)

agent = SingleAgent(
    bin_path='/sandbox/target_binary',
    settings=settings
)

# Synchronous execution
result = agent.run()

# Interactive mode
await agent.run_interactive()
```

### MultiAgent

An orchestrating agent that coordinates multiple specialized agents for complex analysis scenarios.

```python
from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings
```

#### Class Definition

```python
class MultiAgent(BaseAgent):
    """Agent specialized for multi-agent coordination tasks.
    
    This agent creates a planning agent that coordinates multiple
    specialized agents including security specialist, code analyst,
    red team operator, and report journalist.
    """
```

#### Constructor

```python
def __init__(
    self,
    settings: Optional[PartialSettings] = None,
    subagent_run_config: Optional[RunConfig] = None,
):
    """Initialize Multi Agent.
    
    Args:
        settings: Optional partial settings to configure the agent
        subagent_run_config: Optional run configuration for subagents
    """
```

#### Architecture

The MultiAgent system consists of:

1. **Planning Agent**: Coordinates the overall analysis workflow
2. **Security Specialist**: Expert in CVE, CWE, CAPEC, and ATT&CK frameworks
3. **Code Analyst**: Analyzes code structure, functions, and differences
4. **Red Team Operator**: Performs exploitation and penetration testing
5. **Report Journalist**: Generates comprehensive vulnerability reports

#### Specialized Sub-Agents

##### Security Specialist
- **Purpose**: Provides security vulnerability analysis and threat intelligence
- **Tools**: Vector database tools, CVE search, shared memory
- **Expertise**: CVE, CWE, CAPEC, MITRE ATT&CK frameworks
- **Capabilities**: Attack pattern identification, mitigation strategies

##### Code Analyst
- **Purpose**: Analyzes source code structure and identifies vulnerabilities
- **Tools**: Code browser tools, shared memory
- **Expertise**: Code structure, functions, diffs, classes
- **Capabilities**: Static code analysis, vulnerability identification

##### Red Team Operator
- **Purpose**: Performs active exploitation and penetration testing
- **Tools**: Sandbox tools, shared memory
- **Expertise**: Exploitation techniques, payload development
- **Capabilities**: Dynamic analysis, exploit development

##### Report Journalist
- **Purpose**: Creates comprehensive vulnerability assessment reports
- **Tools**: Report generation tools, shared memory
- **Expertise**: Technical writing, vulnerability documentation
- **Capabilities**: Report generation, finding synthesis

#### Shared Context System

The MultiAgent uses a sophisticated shared context system for coordination:

```python
@dataclass
class MultiAgentContext:
    """Combined context with agent memories and shared data."""
    
    shared_memory: SharedMemory
    start_time: datetime
    agents_usage: dict[str, Usage]
    report_generated: bool
    times_reprompted: int
```

##### SharedMemory

```python
class SharedMemory:
    """Simple key-value based shared object for cross-agent information."""
    
    def set(self, key: str, value: str):
        """Store a value in shared memory."""
    
    def get(self, key: str, default=None):
        """Retrieve a value from shared memory."""
    
    def keys(self) -> list[str]:
        """Get all available keys."""
    
    def summary(self) -> str:
        """Get a summary of shared memory contents."""
```

#### Usage Example

```python
from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings

settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/path/to/analysis',
    vulnerable_folder='vuln-version',
    patched_folder='fixed-version'
)

agent = MultiAgent(settings=settings)

# Stream results with progress tracking
await agent.run_streamed_p("Perform comprehensive security analysis")

# Access shared context information
print(agent.context.get_usage())
print(agent.context.shared_memory.summary())
```

### MVPAgent

A minimal viable product agent for basic vulnerability analysis with sandbox capabilities.

```python
from ivexes.agents import MVPAgent
from ivexes.config import PartialSettings
```

#### Class Definition

```python
class MVPAgent(BaseAgent):
    """Agent specialized for MVP (Minimum Viable Product) analysis.
    
    This agent is configured to handle MVP tasks with sandbox tools
    and specific MVP prompts.
    """
```

#### Constructor

```python
def __init__(
    self,
    vulnerable_version: str,
    patched_version: str,
    settings: Optional[PartialSettings] = None,
):
    """Initialize MVP Agent.
    
    Args:
        vulnerable_version: Path to vulnerable version
        patched_version: Path to patched version
        settings: Optional partial settings to configure the agent
    """
```

#### Features

- **Minimal Configuration**: Basic setup for quick analysis
- **Sandbox Integration**: Isolated execution environment
- **Version Comparison**: Vulnerable vs. patched version analysis
- **Streamlined Workflow**: Simplified analysis process

#### Usage Example

```python
from ivexes.agents import MVPAgent
from ivexes.config import PartialSettings

agent = MVPAgent(
    vulnerable_version="vulnerable-1.0",
    patched_version="patched-1.1",
    settings=PartialSettings(model='openai/gpt-4o-mini')
)

# Run basic analysis
result = agent.run()
print(result.data)
```

### HTBChallengeAgent

A specialized agent for Hack The Box challenge exploitation and analysis.

```python
from ivexes.agents import HTBChallengeAgent
from ivexes.config import PartialSettings
```

#### Class Definition

```python
class HTBChallengeAgent(BaseAgent):
    """Agent specialized for Hack The Box challenge exploitation.
    
    This agent is configured to handle HTB challenges with sandbox tools
    and specific reversing prompts.
    """
```

#### Constructor

```python
def __init__(
    self,
    program: str,
    challenge: str,
    settings: Optional[PartialSettings] = None
):
    """Initialize HTB Challenge Agent.
    
    Args:
        program: Program name for the challenge
        challenge: Challenge description
        settings: Optional partial settings to configure the agent
    """
```

#### Features

- **CTF-Focused**: Optimized for Capture The Flag challenges
- **Reversing Capabilities**: Binary analysis and exploitation
- **Report Generation**: Automated challenge solution reports
- **Sandbox Environment**: Isolated challenge execution

#### Usage Example

```python
from ivexes.agents import HTBChallengeAgent
from ivexes.config import PartialSettings

agent = HTBChallengeAgent(
    program="ghost",
    challenge="Find the hidden flag in this binary",
    settings=PartialSettings(model='openai/gpt-4o-mini')
)

# Analyze HTB challenge
result = agent.run()
```

### DefaultAgent

A general-purpose agent with standard configuration for common use cases.

```python
from ivexes.agents import DefaultAgent
from ivexes.config import PartialSettings
```

#### Class Definition

```python
class DefaultAgent(BaseAgent):
    """Default agent implementation with standard configuration."""
```

#### Features

- **Standard Configuration**: Pre-configured with common settings
- **General Purpose**: Suitable for various analysis tasks
- **Balanced Toolset**: Moderate tool selection for versatility

## Execution Modes

All agents support three execution modes:

### Synchronous Mode

```python
# Basic synchronous execution
result = agent.run("Analyze this vulnerability")

# With output printing
agent.run_p("Analyze this vulnerability")
```

### Streaming Mode

```python
# Streaming execution
result_stream = agent.run_streamed("Analyze this vulnerability")

# With streaming output
await agent.run_streamed_p("Analyze this vulnerability")
```

### Interactive Mode

```python
# Interactive conversation
await agent.run_interactive("Start vulnerability analysis")

# With result hooks
def process_result(result):
    print(f"Tokens used: {result.usage.total_tokens}")

await agent.run_interactive(
    "Start analysis",
    result_hook=process_result
)
```

## Settings Integration

All agents accept `PartialSettings` for configuration override:

```python
from ivexes.config import PartialSettings

# Common settings patterns
basic_settings = PartialSettings(
    model='openai/gpt-4o-mini',
    temperature=0.3,
    max_turns=10
)

advanced_settings = PartialSettings(
    model='openai/gpt-4',
    reasoning_model='openai/o1-mini',
    temperature=0.1,
    max_turns=20,
    codebase_path='/analysis/target',
    vulnerable_folder='vuln',
    patched_folder='fixed'
)

# Agent with custom settings
agent = SingleAgent(
    bin_path='/sandbox/binary',
    settings=advanced_settings
)
```

## Error Handling

Agents provide comprehensive error handling:

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

try:
    agent = SingleAgent(
        bin_path='/sandbox/binary',
        settings=PartialSettings()
    )
    result = agent.run()
except ValueError as e:
    print(f"Configuration error: {e}")
except MaxTurnsExceeded as e:
    print(f"Conversation limit exceeded: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

### Resource Management

```python
# Configure resource limits
settings = PartialSettings(
    max_turns=5,           # Limit conversation turns
    model='gpt-4o-mini',   # Use smaller model
    temperature=0.1        # More deterministic output
)

# Monitor usage
result = agent.run()
print(f"Tokens used: {result.usage.total_tokens}")
```

### Parallel Execution

```python
import asyncio
from ivexes.agents import SingleAgent, MultiAgent

async def parallel_analysis():
    """Run multiple agents in parallel."""
    tasks = []
    
    # Create multiple agent instances
    agent1 = SingleAgent('binary1', settings1)
    agent2 = SingleAgent('binary2', settings2)
    
    # Run in parallel
    tasks.append(agent1.run_streamed_p("Analyze binary1"))
    tasks.append(agent2.run_streamed_p("Analyze binary2"))
    
    await asyncio.gather(*tasks)

# Execute parallel analysis
asyncio.run(parallel_analysis())
```

## Examples

### Basic Vulnerability Analysis

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

# Configure for vulnerability analysis
settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/analysis/target',
    vulnerable_folder='vulnerable',
    patched_folder='patched',
    max_turns=15
)

# Create and run agent
agent = SingleAgent(
    bin_path='/sandbox/vulnerable_binary',
    settings=settings
)

# Synchronous analysis
result = agent.run("Perform comprehensive vulnerability analysis")
print("Analysis complete:", result.data)
```

### Multi-Agent Coordination

```python
from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings

# Configure multi-agent system
settings = PartialSettings(
    model='openai/gpt-4',
    reasoning_model='openai/o1-mini',
    codebase_path='/large-project',
    vulnerable_folder='v1.0',
    patched_folder='v1.1'
)

# Create multi-agent system
multi_agent = MultiAgent(settings=settings)

# Stream coordinated analysis
await multi_agent.run_streamed_p(
    "Perform comprehensive security assessment with detailed reporting"
)

# Review coordination results
print("Multi-agent analysis complete")
print("Usage summary:", multi_agent.context.get_usage())
print("Shared findings:", multi_agent.context.shared_memory.summary())
```

### Interactive Analysis Session

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

# Setup interactive agent
agent = SingleAgent(
    bin_path='/sandbox/target',
    settings=PartialSettings(model='openai/gpt-4o-mini')
)

# Define result processing
def save_findings(result):
    """Save important findings to file."""
    with open('findings.txt', 'a') as f:
        f.write(f"Finding: {result.data}\n")

# Run interactive session
await agent.run_interactive(
    "Begin interactive vulnerability analysis",
    result_hook=save_findings
)
```

## See Also

- [Configuration API](config.md) - Settings and configuration management
- [Code Browser API](code_browser.md) - Code analysis and navigation
- [Sandbox API](sandbox.md) - Execution environment management
- [Vector Database API](vector_db.md) - Knowledge base integration
- [Tools API](tools.md) - Shared utilities and helpers