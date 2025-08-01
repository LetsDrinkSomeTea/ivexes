# Examples Guide

## Overview

This guide provides practical examples and use cases for the IVEXES framework, demonstrating how to use different agents for vulnerability analysis tasks. Examples range from basic vulnerability analysis to complex multi-agent orchestration and custom agent development.

## Basic Vulnerability Analysis

### Single Agent Analysis

The SingleAgent provides comprehensive vulnerability analysis for binary analysis tasks with full tool integration.

```python
"""Basic single agent vulnerability analysis."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings, setup_default_logging

# Load environment variables
load_dotenv(verbose=True, override=True)
setup_default_logging()

# Configure analysis settings
settings = PartialSettings(
    trace_name='vulnerability_analysis',
    model='openai/gpt-4o-mini',
    model_temperature=0.1,
    max_turns=25,
    codebase_path='/path/to/codebase',
    vulnerable_folder='vulnerable-version',
    patched_folder='patched-version',
    setup_archive='/path/to/analysis.tgz'
)

# Create and run agent
agent = SingleAgent(
    bin_path='/usr/bin/target_binary',
    settings=settings
)

async def main():
    """Run basic vulnerability analysis."""
    # Interactive mode for exploration
    await agent.run_interactive()
    
    # Or streaming mode for automated processing
    async for chunk in agent.run_streamed():
        print(chunk, end='')

if __name__ == '__main__':
    asyncio.run(main())
```

### MVP Agent Analysis

The MVPAgent provides minimal viable product implementation for quick vulnerability assessment.

```python
"""MVP agent for rapid vulnerability analysis."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import MVPAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging()

settings = PartialSettings(
    trace_name='mvp_analysis',
    model='anthropic/claude-sonnet-4-20250514',
    model_temperature=0.1,
    max_turns=50,
    embedding_model='text-embedding-3-large',
    embedding_provider='openai',
    setup_archive='/path/to/screen_analysis/upload.tgz'
)

agent = MVPAgent(
    vulnerable_version='vulnerable-screen-4.5.0',
    patched_version='patched-screen-4.5.1',
    settings=settings
)

async def main():
    """Run MVP vulnerability analysis."""
    result = await agent.run()
    print(f"Analysis completed: {result}")

if __name__ == '__main__':
    asyncio.run(main())
```

## Multi-Agent Orchestration

### Collaborative Analysis Team

The MultiAgent system orchestrates specialized agents for comprehensive analysis.

```python
"""Multi-agent collaborative vulnerability analysis."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging('WARNING')  # Reduce log noise

settings = PartialSettings(
    trace_name='Multi-Agent Analysis',
    model='openai/gpt-4o-mini',
    reasoning_model='openai/o4-mini',
    model_temperature=0.1,
    max_turns=50,
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct',
    setup_archive='/path/to/analysis/upload.tgz',
    codebase_path='/path/to/codebase',
    vulnerable_folder='vulnerable-version',
    patched_folder='patched-version'
)

agent = MultiAgent(settings=settings)

async def main():
    """Run multi-agent analysis with report generation."""
    # Generate comprehensive report
    report, context = await agent.run_ensured_report()
    
    print(f"Report generated: {report}")
    print(f"Analysis context: {context}")
    
    # Access shared context for detailed insights
    if context.shared_memory:
        print(f"Findings: {context.shared_memory.findings}")
        print(f"Vulnerabilities: {context.shared_memory.vulnerabilities}")

if __name__ == '__main__':
    asyncio.run(main())
```

### Specialized Agent Coordination

```python
"""Advanced multi-agent coordination example."""

import asyncio
from ivexes.agents.multi_agent import MultiAgent, MultiAgentContext
from ivexes.config import PartialSettings

async def coordinated_analysis():
    """Example of coordinated multi-agent analysis."""
    
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=30,
        codebase_path='/path/to/complex_codebase',
        vulnerable_folder='v1.0-vulnerable',
        patched_folder='v1.1-patched'
    )
    
    agent = MultiAgent(settings=settings)
    
    # Custom analysis with specific focus areas
    context = MultiAgentContext()
    context.focus_areas = [
        'buffer overflow vulnerabilities',
        'authentication bypass',
        'privilege escalation'
    ]
    
    report, final_context = await agent.run_with_context(context)
    
    # Process results by specialist
    for specialist_type, findings in final_context.specialist_findings.items():
        print(f"{specialist_type} findings:")
        for finding in findings:
            print(f"  - {finding}")
    
    return report, final_context

# Usage
asyncio.run(coordinated_analysis())
```

## HTB Challenge Analysis

### Hack The Box Challenge Agent

The HTBChallengeAgent is specialized for analyzing Hack The Box challenges.

```python
"""HTB Challenge analysis example."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import HTBChallengeAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging()

settings = PartialSettings(
    trace_name='htb_challenge',
    model='openai/gpt-4.1-mini',
    model_temperature=0.1,
    max_turns=25,
    setup_archive='/path/to/htb_challenge/upload.tgz'
)

agent = HTBChallengeAgent(
    program='challenge_binary',
    challenge='Reverse engineering challenge: find the hidden flag in the binary',
    settings=settings
)

async def main():
    """Analyze HTB challenge."""
    # Interactive mode for step-by-step analysis
    await agent.run_interactive()

if __name__ == '__main__':
    asyncio.run(main())
```

### Complex HTB Challenge

```python
"""Advanced HTB challenge with custom configuration."""

import asyncio
from ivexes.agents import HTBChallengeAgent
from ivexes.config import PartialSettings

async def analyze_complex_challenge():
    """Analyze complex HTB challenge with advanced settings."""
    
    settings = PartialSettings(
        trace_name='complex_htb',
        model='openai/gpt-4o-mini',
        reasoning_model='openai/o4-mini',
        model_temperature=0.05,  # Lower temperature for precision
        max_turns=40,
        embedding_provider='openai',
        embedding_model='text-embedding-3-large',
        setup_archive='/path/to/complex_challenge.tgz'
    )
    
    agent = HTBChallengeAgent(
        program='advanced_challenge',
        challenge='''
        Multi-stage challenge: 
        1. Reverse engineer the protection mechanism
        2. Find the authentication bypass
        3. Exploit the buffer overflow
        4. Extract the final flag
        ''',
        settings=settings
    )
    
    # Stream results for real-time feedback
    async for chunk in agent.run_streamed():
        print(chunk, end='', flush=True)
    
    return agent

# Usage
asyncio.run(analyze_complex_challenge())
```

## Custom Agent Development

### Creating a Specialized Agent

```python
"""Example of creating a custom specialized agent."""

from typing import Optional
from agents import Agent

from ivexes.agents.base import BaseAgent
from ivexes.config import PartialSettings
from ivexes.sandbox.tools import create_sandbox_tools
from ivexes.vector_db import create_vectordb_tools

class WebVulnAgent(BaseAgent):
    """Custom agent specialized for web vulnerability analysis."""
    
    def __init__(self, target_url: str, settings: Optional[PartialSettings] = None):
        """Initialize Web Vulnerability Agent.
        
        Args:
            target_url: Target web application URL
            settings: Optional configuration settings
        """
        self.target_url = target_url
        super().__init__(settings or {})
    
    def _setup_agent(self):
        """Set up the web vulnerability agent."""
        # Custom system message for web vulnerabilities
        self.system_msg = f"""
        You are a web vulnerability assessment specialist focused on analyzing
        web applications for security vulnerabilities including:
        
        - SQL injection
        - Cross-site scripting (XSS)
        - Cross-site request forgery (CSRF)
        - Authentication and authorization flaws
        - Input validation issues
        
        Target URL: {self.target_url}
        
        Use the available tools to conduct thorough security assessment.
        """
        
        # Create specialized tool set
        sandbox_tools = create_sandbox_tools(self.settings)
        vector_tools = create_vectordb_tools(self.settings)
        
        # Add web-specific tools
        web_tools = self._create_web_tools()
        
        tools = sandbox_tools + vector_tools + web_tools
        
        self.agent = Agent(
            model=self.settings.model,
            tools=tools,
            system_message=self.system_msg
        )
    
    def _create_web_tools(self):
        """Create web-specific analysis tools."""
        # Implementation would include web scanning tools
        return []

# Usage example
async def analyze_web_app():
    """Analyze web application for vulnerabilities."""
    
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=20
    )
    
    agent = WebVulnAgent(
        target_url='https://example-vulnerable-app.com',
        settings=settings
    )
    
    await agent.run_interactive()

# Run the analysis
asyncio.run(analyze_web_app())
```

### Agent with Custom Tools

```python
"""Custom agent with domain-specific tools."""

from typing import List, Dict, Any
from agents import Agent, tool

from ivexes.agents.base import BaseAgent
from ivexes.config import PartialSettings

class NetworkSecurityAgent(BaseAgent):
    """Agent specialized for network security analysis."""
    
    def __init__(self, target_network: str, settings: Optional[PartialSettings] = None):
        self.target_network = target_network
        super().__init__(settings or {})
    
    def _setup_agent(self):
        """Set up network security agent with custom tools."""
        
        @tool
        def scan_network_ports(target: str) -> Dict[str, Any]:
            """Scan network ports for open services.
            
            Args:
                target: Network target to scan
                
            Returns:
                Dict containing scan results
            """
            # Implementation would use nmap or similar
            return {
                'target': target,
                'open_ports': [22, 80, 443, 8080],
                'services': {
                    '22': 'ssh',
                    '80': 'http',
                    '443': 'https',
                    '8080': 'http-proxy'
                }
            }
        
        @tool
        def analyze_ssl_configuration(host: str, port: int = 443) -> Dict[str, Any]:
            """Analyze SSL/TLS configuration.
            
            Args:
                host: Target hostname
                port: SSL port (default 443)
                
            Returns:
                SSL analysis results
            """
            # Implementation would use testssl.sh or similar
            return {
                'host': host,
                'port': port,
                'ssl_version': 'TLSv1.3',
                'cipher_suites': ['TLS_AES_256_GCM_SHA384'],
                'vulnerabilities': []
            }
        
        tools = [scan_network_ports, analyze_ssl_configuration]
        
        self.agent = Agent(
            model=self.settings.model,
            tools=tools,
            system_message=f"""
            You are a network security specialist analyzing: {self.target_network}
            
            Focus on:
            - Open service enumeration
            - SSL/TLS configuration analysis
            - Network vulnerability assessment
            - Security recommendations
            """
        )

# Usage
async def network_security_analysis():
    """Perform network security analysis."""
    
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        temperature=0.1,
        max_turns=15
    )
    
    agent = NetworkSecurityAgent(
        target_network='192.168.1.0/24',
        settings=settings
    )
    
    await agent.run_interactive()

asyncio.run(network_security_analysis())
```

## Integration Examples

### Vector Database Integration

```python
"""Example of ChromaDB vector database integration."""

from typing import cast
from chromadb import EmbeddingFunction, Client
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

async def vector_db_integration_example():
    """Demonstrate vector database integration."""
    
    # Setup ChromaDB
    chroma_client = Client()
    
    ef = SentenceTransformerEmbeddingFunction(
        model_name='intfloat/multilingual-e5-large-instruct'
    )
    
    ef = cast(EmbeddingFunction, ef)
    collection = chroma_client.create_collection(
        name='vulnerability_knowledge', 
        embedding_function=ef
    )
    
    # Add vulnerability knowledge
    collection.add(
        ids=['cve-2021-44228', 'cve-2021-45046'],
        documents=[
            'Log4j JNDI injection vulnerability allows remote code execution',
            'Log4j denial of service vulnerability in message lookup substitution'
        ],
        metadatas=[
            {'severity': 'critical', 'cvss': 10.0},
            {'severity': 'high', 'cvss': 9.0}
        ]
    )
    
    # Query for related vulnerabilities
    results = collection.query(
        query_texts=['remote code execution java logging'],
        n_results=2
    )
    
    print(f"Related vulnerabilities: {results}")
    
    # Use with agent
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        embedding_provider='local',
        embedding_model='intfloat/multilingual-e5-large-instruct',
        chroma_path='/tmp/ivexes_vectordb'
    )
    
    agent = SingleAgent(
        bin_path='/usr/bin/java_app',
        settings=settings
    )
    
    await agent.run_interactive()

asyncio.run(vector_db_integration_example())
```

### Sandbox Integration

```python
"""Example of sandbox integration for dynamic analysis."""

import asyncio
from ivexes.sandbox import Sandbox
from ivexes.config import PartialSettings

async def sandbox_integration_example():
    """Demonstrate sandbox integration."""
    
    settings = PartialSettings(
        sandbox_image='kali-ssh:latest',
        setup_archive='/path/to/analysis_environment.tgz'
    )
    
    # Create sandbox environment
    sandbox = Sandbox(settings)
    
    try:
        # Start sandbox
        await sandbox.start()
        
        # Execute analysis commands
        result = await sandbox.execute_command('file /usr/bin/target_binary')
        print(f"File analysis: {result}")
        
        result = await sandbox.execute_command('strings /usr/bin/target_binary | head -20')
        print(f"String analysis: {result}")
        
        # Run dynamic analysis
        result = await sandbox.execute_command('ltrace -c /usr/bin/target_binary')
        print(f"Library trace: {result}")
        
    finally:
        # Clean up
        await sandbox.stop()

asyncio.run(sandbox_integration_example())
```

## Advanced Use Cases

### Batch Analysis Pipeline

```python
"""Batch vulnerability analysis pipeline."""

import asyncio
from pathlib import Path
from typing import List, Dict, Any

from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings

class BatchAnalysisPipeline:
    """Pipeline for batch vulnerability analysis."""
    
    def __init__(self, settings: PartialSettings):
        self.settings = settings
        self.results: List[Dict[str, Any]] = []
    
    async def analyze_targets(self, targets: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Analyze multiple targets in batch.
        
        Args:
            targets: List of target configurations
            
        Returns:
            List of analysis results
        """
        results = []
        
        for target in targets:
            print(f"Analyzing {target['name']}...")
            
            # Configure target-specific settings
            target_settings = PartialSettings(
                **self.settings.model_dump(),
                **target
            )
            
            agent = MultiAgent(settings=target_settings)
            
            try:
                report, context = await agent.run_ensured_report()
                
                result = {
                    'target': target['name'],
                    'status': 'completed',
                    'report': report,
                    'vulnerabilities': len(context.shared_memory.vulnerabilities) if context.shared_memory else 0,
                    'findings': context.shared_memory.findings if context.shared_memory else []
                }
                
            except Exception as e:
                result = {
                    'target': target['name'],
                    'status': 'failed',
                    'error': str(e)
                }
            
            results.append(result)
            
        return results
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate summary report from batch results."""
        
        total_targets = len(results)
        successful = len([r for r in results if r['status'] == 'completed'])
        failed = total_targets - successful
        
        total_vulnerabilities = sum(
            r.get('vulnerabilities', 0) for r in results 
            if r['status'] == 'completed'
        )
        
        summary = f"""
# Batch Analysis Summary

## Overview
- Total targets analyzed: {total_targets}
- Successful analyses: {successful}
- Failed analyses: {failed}
- Total vulnerabilities found: {total_vulnerabilities}

## Detailed Results
"""
        
        for result in results:
            if result['status'] == 'completed':
                summary += f"""
### {result['target']}
- Status: ✅ Completed
- Vulnerabilities: {result['vulnerabilities']}
- Key findings: {len(result['findings'])}
"""
            else:
                summary += f"""
### {result['target']}
- Status: ❌ Failed
- Error: {result.get('error', 'Unknown error')}
"""
        
        return summary

# Usage example
async def run_batch_analysis():
    """Run batch vulnerability analysis."""
    
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=30,
        embedding_provider='local'
    )
    
    targets = [
        {
            'name': 'screen-vulnerability',
            'codebase_path': '/path/to/screen/codebase',
            'vulnerable_folder': 'vulnerable-4.5.0',
            'patched_folder': 'patched-4.5.1',
            'setup_archive': '/path/to/screen.tgz'
        },
        {
            'name': 'sudo-vulnerability',
            'codebase_path': '/path/to/sudo/codebase',
            'vulnerable_folder': 'vulnerable-1.8.0',
            'patched_folder': 'patched-1.8.1',
            'setup_archive': '/path/to/sudo.tgz'
        }
    ]
    
    pipeline = BatchAnalysisPipeline(settings)
    results = await pipeline.analyze_targets(targets)
    
    # Generate and save summary
    summary = pipeline.generate_summary_report(results)
    
    with open('batch_analysis_summary.md', 'w') as f:
        f.write(summary)
    
    print("Batch analysis completed. Summary saved to batch_analysis_summary.md")
    
    return results

# Run the pipeline
asyncio.run(run_batch_analysis())
```

## Related Topics

- [Architecture Guide](architecture.md) - System design and components
- [Installation Guide](installation.md) - Setup and configuration
- [Development Guide](development.md) - Extending and customizing IVEXES
- [API Reference](../api/agents.md) - Detailed API documentation

## Next Steps

1. **Start with Basic Examples**: Try the SingleAgent and MVPAgent examples to understand core functionality
2. **Explore Multi-Agent**: Experiment with MultiAgent coordination for complex analyses
3. **Customize Agents**: Create specialized agents for your specific use cases
4. **Integrate Components**: Combine vector database, sandbox, and code browser capabilities
5. **Build Pipelines**: Develop automated analysis pipelines for batch processing

For more advanced usage patterns and customization options, see the [Development Guide](development.md) and [API Reference](../api/agents.md).