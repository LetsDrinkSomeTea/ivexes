# Usage Guide

## Overview

This guide covers the core workflows and best practices for using IVEXES effectively. IVEXES provides multiple execution modes and agent types designed for different vulnerability analysis scenarios, from quick assessments to comprehensive multi-agent orchestrations.

The framework emphasizes flexibility through its agent-based architecture, allowing you to choose the right tool for your analysis needs while maintaining consistent interfaces across all execution modes.

## Getting Started

### Basic Setup

Before using IVEXES agents, ensure your environment is properly configured:

```python
from dotenv import load_dotenv
from ivexes.config import setup_default_logging

# Load environment variables
load_dotenv(verbose=True, override=True)

# Configure logging
setup_default_logging('INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Quick Start Example

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings
import asyncio

# Configure the agent
settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/path/to/analysis',
    vulnerable_folder='vulnerable',
    patched_folder='patched',
    max_turns=10
)

# Create and run the agent
agent = SingleAgent(bin_path='/target/binary', settings=settings)
result = await agent.run_interactive()
```

## Agent Execution Modes

All IVEXES agents support three execution modes, each optimized for different use cases:

### 1. Synchronous Mode

Best for: Batch processing, automated analysis, scripting

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

agent = SingleAgent(bin_path='/target/binary', settings=settings)

# Basic synchronous execution
result = agent.run("Analyze this binary for buffer overflow vulnerabilities")
print("Analysis result:", result.data)
print("Tokens used:", result.usage.total_tokens)

# With automatic output printing
agent.run_p("Perform security assessment")
```

**When to use**: Automated security pipelines, batch analysis, CI/CD integration

### 2. Streaming Mode

Best for: Real-time feedback, long-running analysis, user interfaces

```python
import asyncio

async def streaming_analysis():
    agent = SingleAgent(bin_path='/target/binary', settings=settings)
    
    # Stream results as they're generated
    result_stream = agent.run_streamed("Comprehensive vulnerability analysis")
    
    # Process streaming results
    async for chunk in result_stream:
        print("Analysis progress:", chunk)
    
    # Alternative: Stream with automatic printing
    await agent.run_streamed_p("Analyze binary for memory corruption issues")

# Run streaming analysis
asyncio.run(streaming_analysis())
```

**When to use**: Interactive applications, progress monitoring, real-time dashboards

### 3. Interactive Mode

Best for: Exploratory analysis, iterative investigation, learning

```python
import asyncio

async def interactive_session():
    agent = SingleAgent(bin_path='/target/binary', settings=settings)
    
    # Start interactive conversation
    await agent.run_interactive("Begin security analysis of this binary")
    
    # Session continues until user types 'exit', 'quit', or 'q'
    # Users can ask follow-up questions and refine analysis

# Custom result processing
def save_findings(result):
    """Save important findings to file."""
    with open('vulnerability_findings.txt', 'a') as f:
        f.write(f"Finding: {result.data}\n")
        f.write(f"Tokens: {result.usage.total_tokens}\n\n")

async def interactive_with_hooks():
    agent = SingleAgent(bin_path='/target/binary', settings=settings)
    
    await agent.run_interactive(
        "Start vulnerability assessment",
        result_hook=save_findings
    )

asyncio.run(interactive_session())
```

**When to use**: Security research, learning, detailed investigation, hypothesis testing

## Agent Types and Use Cases

### SingleAgent

**Purpose**: Comprehensive individual analysis with full toolset integration

**Best for**:
- Focused vulnerability analysis
- Binary reverse engineering
- Code diff analysis
- CVE research and correlation

**Features**:
- Complete toolset: sandbox, code browser, vector database, CVE search
- Isolated execution environment
- Source code analysis and comparison
- Knowledge base integration

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

# Standard configuration
settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/analysis/project',
    vulnerable_folder='v1.0-vuln',
    patched_folder='v1.1-fixed',
    max_turns=15,
    model_temperature=0.2
)

agent = SingleAgent(
    bin_path='/sandbox/target_binary',
    settings=settings
)

# Synchronous analysis
result = agent.run("Identify memory corruption vulnerabilities")

# Interactive exploration
await agent.run_interactive("Investigate potential buffer overflows")
```

### MultiAgent

**Purpose**: Coordinated multi-agent analysis for complex scenarios

**Best for**:
- Large-scale security assessments
- Multi-perspective analysis
- Comprehensive reporting
- Complex vulnerability chains

**Architecture**:
- **Planning Agent**: Orchestrates the analysis workflow
- **Security Specialist**: CVE, CWE, CAPEC, ATT&CK expertise
- **Code Analyst**: Source code structure and vulnerability analysis
- **Red Team Operator**: Exploitation and penetration testing
- **Report Journalist**: Comprehensive vulnerability reporting

```python
from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings

# High-performance multi-agent setup
settings = PartialSettings(
    model='openai/gpt-4',
    reasoning_model='openai/o1-mini',
    model_temperature=0.1,
    max_turns=25,
    codebase_path='/large-project',
    vulnerable_folder='v2.0',
    patched_folder='v2.1'
)

multi_agent = MultiAgent(settings=settings)

# Coordinated analysis with automatic reporting
report_data, shared_context = await multi_agent.run_ensured_report()

# Stream coordinated analysis
await multi_agent.run_streamed_p(
    "Perform comprehensive security assessment with detailed reporting"
)

# Access coordination results
print("Multi-agent analysis complete")
print("Usage summary:", multi_agent.context.get_usage())
print("Shared findings:", multi_agent.context.shared_memory.summary())
```

### MVPAgent

**Purpose**: Minimal viable product analysis for quick assessments

**Best for**:
- Quick vulnerability checks
- Proof-of-concept analysis
- Resource-constrained environments
- Initial assessment before deeper analysis

```python
from ivexes.agents import MVPAgent
from ivexes.config import PartialSettings

agent = MVPAgent(
    vulnerable_version="vulnerable-1.0",
    patched_version="patched-1.1",
    settings=PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=5
    )
)

# Quick analysis
result = agent.run("Identify key vulnerabilities and their fixes")
```

### HTBChallengeAgent

**Purpose**: Specialized for Hack The Box and CTF challenges

**Best for**:
- Capture The Flag competitions
- Binary exploitation challenges
- Reverse engineering puzzles
- Educational security exercises

```python
from ivexes.agents import HTBChallengeAgent
from ivexes.config import PartialSettings

agent = HTBChallengeAgent(
    program="ghost",
    challenge="Find the hidden flag in this binary",
    settings=PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=20
    )
)

# CTF analysis
result = agent.run("Solve this reverse engineering challenge")
```

## Common Workflows

### 1. Binary Vulnerability Analysis

Complete workflow for analyzing a vulnerable binary:

```python
import asyncio
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

async def binary_analysis_workflow():
    """Complete binary vulnerability analysis workflow."""
    
    # Configuration for binary analysis
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=20,
        model_temperature=0.1,  # More deterministic for security analysis
        setup_archive='/analysis/target.tar.gz',  # Archive to extract
        codebase_path='/analysis/source',
        vulnerable_folder='vulnerable',
        patched_folder='patched'
    )
    
    agent = SingleAgent(bin_path='/target/vulnerable_binary', settings=settings)
    
    # Phase 1: Initial reconnaissance
    print("Phase 1: Binary reconnaissance...")
    await agent.run_streamed_p(
        "Analyze the binary structure, identify interesting functions and potential attack surfaces"
    )
    
    # Phase 2: Vulnerability identification  
    print("\nPhase 2: Vulnerability identification...")
    await agent.run_streamed_p(
        "Identify specific vulnerabilities in the binary, focusing on memory corruption and logic flaws"
    )
    
    # Phase 3: Exploitation assessment
    print("\nPhase 3: Exploitation assessment...")
    await agent.run_streamed_p(
        "Assess exploitability of identified vulnerabilities and develop proof-of-concept exploits"
    )
    
    # Phase 4: Mitigation analysis
    print("\nPhase 4: Mitigation analysis...")
    await agent.run_streamed_p(
        "Compare vulnerable and patched versions to understand fixes and their effectiveness"
    )

asyncio.run(binary_analysis_workflow())
```

### 2. Multi-Agent Security Assessment

Comprehensive security assessment using specialized agents:

```python
import asyncio
from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings

async def comprehensive_security_assessment():
    """Multi-perspective security assessment."""
    
    settings = PartialSettings(
        model='openai/gpt-4',
        reasoning_model='openai/o1-mini',
        model_temperature=0.1,
        max_turns=30,
        codebase_path='/project',
        vulnerable_folder='vulnerable',
        patched_folder='fixed',
        trace_name='security-assessment'
    )
    
    multi_agent = MultiAgent(settings=settings)
    
    # Comprehensive analysis with automatic reporting
    print("Starting comprehensive security assessment...")
    report_data, context = await multi_agent.run_ensured_report()
    
    # Extract insights from shared context
    shared_memory = context.shared_memory
    
    print("\n=== Analysis Summary ===")
    print(f"Total runtime: {context.start_time}")
    print(f"Report generated: {context.report_generated}")
    
    print("\n=== Agent Usage ===")
    print(context.get_usage())
    
    print("\n=== Shared Findings ===")
    print(shared_memory.summary())

asyncio.run(comprehensive_security_assessment())
```

### 3. Interactive Investigation Session

Exploratory analysis with iterative questioning:

```python
import asyncio
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

class InvestigationTracker:
    """Track findings during interactive investigation."""
    
    def __init__(self):
        self.findings = []
        self.questions = []
    
    def process_result(self, result):
        """Process and store investigation results."""
        if result.data:
            self.findings.append({
                'content': result.data,
                'tokens': result.usage.total_tokens,
                'timestamp': result.context_wrapper.start_time
            })
        
        # Save to file for persistence
        with open('investigation_log.txt', 'a') as f:
            f.write(f"Result: {result.data}\n")
            f.write(f"Usage: {result.usage.total_tokens} tokens\n\n")

async def interactive_investigation():
    """Interactive vulnerability investigation session."""
    
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=25,
        codebase_path='/investigation/target',
        vulnerable_folder='vulnerable',
        patched_folder='patched'
    )
    
    agent = SingleAgent(bin_path='/target/binary', settings=settings)
    tracker = InvestigationTracker()
    
    print("Starting interactive investigation session...")
    print("Commands: 'exit', 'quit', or 'q' to end session")
    print("Ask questions about vulnerabilities, exploits, or mitigations\n")
    
    await agent.run_interactive(
        "Begin detailed vulnerability investigation of this binary",
        result_hook=tracker.process_result
    )
    
    print(f"\nInvestigation complete. Found {len(tracker.findings)} key insights.")

asyncio.run(interactive_investigation())
```

### 4. Automated Security Pipeline

Integration with CI/CD for automated vulnerability detection:

```python
import asyncio
import sys
from ivexes.agents import MVPAgent
from ivexes.config import PartialSettings

async def automated_security_check(project_path, vulnerable_tag, fixed_tag):
    """Automated security check for CI/CD pipeline."""
    
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=10,
        model_temperature=0.0,  # Deterministic for consistent results
        log_level='WARNING',    # Minimal logging for CI/CD
        trace_name='ci-security-check'
    )
    
    agent = MVPAgent(
        vulnerable_version=vulnerable_tag,
        patched_version=fixed_tag,
        settings=settings
    )
    
    try:
        # Quick security assessment
        result = agent.run(
            "Identify critical security vulnerabilities and assess severity"
        )
        
        # Parse results for CI/CD decisions
        has_critical_vulns = "critical" in result.data.lower()
        
        if has_critical_vulns:
            print("❌ Critical vulnerabilities detected")
            print(result.data)
            return 1  # Fail CI/CD pipeline
        else:
            print("✅ No critical vulnerabilities found")
            return 0  # Pass CI/CD pipeline
            
    except Exception as e:
        print(f"❌ Security check failed: {e}")
        return 2  # Error status

# Usage in CI/CD
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: script.py <project_path> <vulnerable_tag> <fixed_tag>")
        sys.exit(1)
    
    exit_code = asyncio.run(
        automated_security_check(sys.argv[1], sys.argv[2], sys.argv[3])
    )
    sys.exit(exit_code)
```

## Best Practices

### Performance Optimization

#### Model Selection
```python
# For development and quick analysis
development_settings = PartialSettings(
    model='openai/gpt-4o-mini',  # Fast and cost-effective
    max_turns=5,                 # Limit conversation length
    model_temperature=0.3        # Balance creativity and consistency
)

# For production security analysis
production_settings = PartialSettings(
    model='openai/gpt-4',             # Most capable model
    reasoning_model='openai/o1-mini',  # Advanced reasoning
    max_turns=20,                     # Allow thorough analysis
    model_temperature=0.1             # More deterministic
)
```

#### Resource Management
```python
# Monitor token usage
result = agent.run("Analyze vulnerabilities")
print(f"Analysis used {result.usage.total_tokens} tokens")

# Set reasonable limits
resource_conscious_settings = PartialSettings(
    max_turns=10,           # Prevent runaway conversations
    model_temperature=0.1,  # More predictable output
    log_level='WARNING'     # Reduce logging overhead
)
```

### Security Considerations

#### Sandbox Configuration
```python
# Secure sandbox setup
secure_settings = PartialSettings(
    sandbox_image='kali-ssh:latest',  # Use specific image versions
    setup_archive='/secure/analysis.tar.gz',  # Controlled environment
    log_level='INFO'  # Audit trail
)
```

#### API Key Management
```python
import os
from dotenv import load_dotenv

# Load secrets securely
load_dotenv('.secrets.env')  # Never commit this file

# Validate API key availability
if not os.environ.get('LLM_API_KEY'):
    raise ValueError("LLM_API_KEY must be set for security analysis")
```

### Error Handling

#### Robust Error Handling
```python
import asyncio
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

async def robust_analysis():
    """Analysis with comprehensive error handling."""
    
    try:
        settings = PartialSettings(
            model='openai/gpt-4o-mini',
            max_turns=10
        )
        
        agent = SingleAgent(bin_path='/target/binary', settings=settings)
        result = agent.run("Analyze for vulnerabilities")
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        return None
        
    except ConnectionError as e:
        print(f"API connection failed: {e}")
        return None
        
    except Exception as e:
        print(f"Unexpected error during analysis: {e}")
        return None
    
    return result

result = await robust_analysis()
if result:
    print("Analysis successful:", result.data)
else:
    print("Analysis failed - check configuration and connectivity")
```

#### Graceful Degradation
```python
async def analysis_with_fallback():
    """Analysis with model fallback strategy."""
    
    models_to_try = [
        'openai/gpt-4',
        'openai/gpt-4o-mini',
        'anthropic/claude-3-sonnet'
    ]
    
    for model in models_to_try:
        try:
            settings = PartialSettings(model=model, max_turns=5)
            agent = SingleAgent(bin_path='/target', settings=settings)
            result = agent.run("Quick vulnerability scan")
            
            print(f"✅ Analysis successful with {model}")
            return result
            
        except Exception as e:
            print(f"❌ Failed with {model}: {e}")
            continue
    
    print("❌ All models failed - check configuration")
    return None
```

### Logging and Monitoring

#### Structured Logging
```python
import logging
from ivexes.config import setup_default_logging

# Configure structured logging
setup_default_logging('INFO')
logger = logging.getLogger(__name__)

async def monitored_analysis():
    """Analysis with comprehensive logging."""
    
    logger.info("Starting vulnerability analysis")
    
    try:
        agent = SingleAgent(bin_path='/target', settings=settings)
        
        logger.info("Agent initialized successfully")
        result = agent.run("Comprehensive security analysis")
        
        logger.info(f"Analysis complete - {result.usage.total_tokens} tokens used")
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise

result = await monitored_analysis()
```

#### Performance Monitoring
```python
import time
from datetime import datetime

class PerformanceMonitor:
    """Monitor analysis performance and resource usage."""
    
    def __init__(self):
        self.start_time = None
        self.metrics = {}
    
    def start_analysis(self, analysis_type):
        self.start_time = time.time()
        self.metrics['analysis_type'] = analysis_type
        self.metrics['start_time'] = datetime.now().isoformat()
    
    def end_analysis(self, result):
        duration = time.time() - self.start_time
        self.metrics.update({
            'duration_seconds': duration,
            'tokens_used': result.usage.total_tokens,
            'tokens_per_second': result.usage.total_tokens / duration,
            'end_time': datetime.now().isoformat()
        })
        
        # Log performance metrics
        print(f"Analysis completed in {duration:.2f}s")
        print(f"Token usage: {result.usage.total_tokens}")
        print(f"Rate: {self.metrics['tokens_per_second']:.2f} tokens/sec")

# Usage
monitor = PerformanceMonitor()
monitor.start_analysis("binary_vulnerability_scan")
result = agent.run("Analyze binary for vulnerabilities")
monitor.end_analysis(result)
```

## Advanced Usage Patterns

### Parallel Analysis
```python
import asyncio
from ivexes.agents import SingleAgent

async def parallel_binary_analysis(binaries, settings):
    """Analyze multiple binaries in parallel."""
    
    async def analyze_binary(binary_path):
        agent = SingleAgent(bin_path=binary_path, settings=settings)
        return await agent.run_streamed("Analyze for vulnerabilities")
    
    # Create analysis tasks
    tasks = [analyze_binary(binary) for binary in binaries]
    
    # Run analyses in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Analysis failed for {binaries[i]}: {result}")
        else:
            print(f"Analysis complete for {binaries[i]}")
    
    return results

# Analyze multiple binaries
binaries = ['/target/bin1', '/target/bin2', '/target/bin3']
results = await parallel_binary_analysis(binaries, settings)
```

### Custom Agent Workflows
```python
from ivexes.agents.base import BaseAgent
from ivexes.config import PartialSettings

class CustomSecurityAgent(BaseAgent):
    """Custom agent with specialized security analysis workflow."""
    
    def __init__(self, target_type, settings):
        self.target_type = target_type
        super().__init__(settings)
    
    def _setup_agent(self):
        # Configure specialized tools based on target type
        if self.target_type == 'web_app':
            # Web application security tools
            self.user_msg = "Analyze web application for OWASP Top 10 vulnerabilities"
        elif self.target_type == 'binary':
            # Binary analysis tools
            self.user_msg = "Perform binary security analysis focusing on memory corruption"
        
        # Setup agent with appropriate tools
        self.agent = self._create_specialized_agent()
    
    def _create_specialized_agent(self):
        # Implementation specific to your needs
        pass

# Usage
custom_agent = CustomSecurityAgent('binary', settings)
result = await custom_agent.run_interactive()
```

## Related Topics

- [Configuration Guide](configuration.md) - Complete configuration reference
- [Installation Guide](installation.md) - Setup and environment preparation
- [Agents API](../api/agents.md) - Detailed API reference for all agent classes
- [Code Browser API](../api/code_browser.md) - Code analysis capabilities
- [Examples Guide](examples.md) - Additional usage examples and patterns

## Next Steps

After mastering the core usage patterns:

1. **Explore Advanced Features**: Review specialized agent capabilities and custom workflows
2. **Integrate with Tools**: Connect IVEXES with your existing security toolchain
3. **Develop Custom Agents**: Create specialized agents for your specific use cases
4. **Optimize Performance**: Fine-tune settings for your analysis requirements
5. **Contribute Back**: Share your patterns and improvements with the community