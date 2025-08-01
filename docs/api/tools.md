# Tools API Reference

## Overview

The Tools module provides a comprehensive collection of utility functions and helpers used throughout the IVEXES system. This module aggregates tools from different components including date utilities, sandbox operations, code browsing, vector database functionality, CVE search, and report generation, providing a centralized access point for all available tools.

The tools are organized into functional categories and designed for easy integration with IVEXES agents and components.

## Tool Categories

### Aggregated Tools

The main tools module (`ivexes.tools`) provides convenient access to all tool collections:

```python
from ivexes.tools import (
    date_tools,
    cve_tools,
    create_sandbox_tools,
    create_code_browser_tools,
    create_vectordb_tools,
    create_report_tools
)
```

### Tool Creation Functions

- `create_sandbox_tools()`: Containerized environment operations
- `create_code_browser_tools()`: Code analysis and browsing capabilities  
- `create_vectordb_tools()`: Vector database operations for knowledge retrieval
- `create_report_tools()`: Report generation and documentation

### Static Tool Collections

- `date_tools`: Date and time retrieval utilities
- `cve_tools`: CVE lookup and vulnerability research

## Date and Time Tools

### get_current_date()

Tool function for retrieving current date and time information.

```python
@function_tool(strict_mode=True)
def get_current_date() -> str
```

**Returns:**
- `str`: Current date and time in 'YYYY-MM-DD HH:MM:SS' format

**Example:**
```python
from ivexes.date.tools import get_current_date

# Get current timestamp
timestamp = get_current_date()
print(timestamp)  # Output: '2024-01-15 14:30:45'
```

### current_date()

Utility function for formatted current date/time (non-tool version).

```python
def current_date() -> str
```

**Returns:**
- `str`: Formatted current date and time

**Example:**
```python
from ivexes.date.tools import current_date

# Direct function call
now = current_date()
print(f"Analysis started at: {now}")
```

### Usage with Agents

```python
from ivexes.agents import SingleAgent
from ivexes.date.tools import date_tools
from ivexes.config import PartialSettings

settings = PartialSettings(model='openai/gpt-4o-mini')
agent = SingleAgent(settings=settings)

# date_tools is automatically available to agents
# Agents can call get_current_date() during analysis
```

## Token Management and Statistics

### get_text_statistics()

Analyze token, character, and word counts in text strings.

```python
def get_text_statistics(string: str, model: str = 'gpt-4') -> tuple[int, int, int]
```

**Parameters:**
- `string` (str): Input text to analyze
- `model` (str): Model name for token encoding (default: 'gpt-4')

**Returns:**
- `tuple[int, int, int]`: (token_count, character_count, word_count)

**Example:**
```python
from ivexes.token import get_text_statistics

text = "This is a sample vulnerability analysis report."
tokens, chars, words = get_text_statistics(text, model='gpt-4')

print(f"Analysis: {tokens} tokens, {chars} characters, {words} words")
# Output: Analysis: 12 tokens, 46 characters, 8 words
```

### get_file_statistics()

Analyze token, character, and word counts in files.

```python
def get_file_statistics(file_path: str) -> tuple[int, int, int]
```

**Parameters:**
- `file_path` (str): Path to file for analysis

**Returns:**
- `tuple[int, int, int]`: (token_count, character_count, word_count)

**Example:**
```python
from ivexes.token import get_file_statistics

# Analyze a source code file
tokens, chars, words = get_file_statistics('/path/to/vulnerable.c')

if tokens > 0:
    print(f"File analysis: {tokens} tokens, {chars} characters, {words} words")
else:
    print("File could not be analyzed (encoding issues or empty)")
```

### get_directory_statistics()

Analyze token, character, and word counts across entire directories.

```python
def get_directory_statistics(directory_path: str) -> tuple[int, int, int]
```

**Parameters:**
- `directory_path` (str): Path to directory for recursive analysis

**Returns:**
- `tuple[int, int, int]`: Total (token_count, character_count, word_count)

**Example:**
```python
from ivexes.token import get_directory_statistics

# Analyze entire codebase
total_tokens, total_chars, total_words = get_directory_statistics('/path/to/codebase')

print(f"Codebase Analysis:")
print(f"- Total tokens: {total_tokens:,}")
print(f"- Total characters: {total_chars:,}")  
print(f"- Total words: {total_words:,}")

# Estimate analysis cost
estimated_cost = total_tokens * 0.00001  # Example rate
print(f"- Estimated analysis cost: ${estimated_cost:.2f}")
```

## Container Management Utilities

### get_client()

Get or create a Docker client instance with singleton pattern.

```python
def get_client() -> DockerClient
```

**Returns:**
- `DockerClient`: Docker client instance

**Example:**
```python
from ivexes.container import get_client

client = get_client()
print(f"Docker client version: {client.version()}")
```

### find_by_name()

Find and optionally start a Docker container by name.

```python
def find_by_name(container_name: str, start: bool = True) -> Container | None
```

**Parameters:**
- `container_name` (str): Name of container to find
- `start` (bool): Whether to start container if found but not running

**Returns:**
- `Container | None`: Container instance or None if not found

**Example:**
```python
from ivexes.container import find_by_name

# Find and start container if needed
container = find_by_name('ivexes-analysis-container', start=True)

if container:
    print(f"Container {container.name} is {container.status}")
else:
    print("Container not found")
```

### cleanup()

Clean up containers with specific name prefix.

```python
def cleanup(prefix: str = 'ivexes-') -> None
```

**Parameters:**
- `prefix` (str): Prefix for containers to remove (default: 'ivexes-')

**Example:**
```python
from ivexes.container import cleanup

# Clean up all IVEXES containers
cleanup('ivexes-')

# Clean up test containers
cleanup('test-container-')
```

### remove_if_exists()

Remove a specific container if it exists.

```python
def remove_if_exists(container_name: str) -> bool
```

**Parameters:**
- `container_name` (str): Name of container to remove

**Returns:**
- `bool`: True if container was removed, False if it didn't exist

**Example:**
```python
from ivexes.container import remove_if_exists

# Clean up specific container
removed = remove_if_exists('old-analysis-container')
if removed:
    print("Container removed successfully")
else:
    print("Container did not exist")
```

### santize_name()

Sanitize container names by replacing invalid characters.

```python
def santize_name(name: str) -> str
```

**Parameters:**
- `name` (str): Original name to sanitize

**Returns:**
- `str`: Sanitized name with invalid characters replaced

**Example:**
```python
from ivexes.container import santize_name

# Sanitize problematic container name
raw_name = "My Analysis Container! (2024)"
safe_name = santize_name(raw_name)
print(safe_name)  # Output: "my-analysis-container-2024"

# Use for container creation
container_name = f"ivexes-{santize_name(analysis_id)}"
```

## Color Utilities

### Colors Class

ANSI escape sequences for colored terminal output.

```python
class Colors:
    HEADER = '\033[95m'      # Purple header
    OKBLUE = '\033[94m'      # Blue for info
    OKCYAN = '\033[96m'      # Cyan for highlights  
    OKGREEN = '\033[92m'     # Green for success
    WARNING = '\033[93m'     # Yellow for warnings
    FAIL = '\033[91m'        # Red for errors
    ENDC = '\033[0m'         # Reset color
    BOLD = '\033[1m'         # Bold text
    UNDERLINE = '\033[4m'    # Underlined text
```

**Example:**
```python
from ivexes.colors import Colors

# Colored output for analysis results
print(f"{Colors.HEADER}Vulnerability Analysis Report{Colors.ENDC}")
print(f"{Colors.OKGREEN}✓ Analysis completed successfully{Colors.ENDC}")
print(f"{Colors.WARNING}⚠ 3 potential vulnerabilities found{Colors.ENDC}")
print(f"{Colors.FAIL}✗ Critical security issue detected{Colors.ENDC}")

# Combined formatting
print(f"{Colors.BOLD}{Colors.UNDERLINE}Summary{Colors.ENDC}")
print(f"{Colors.OKCYAN}Total files analyzed: 42{Colors.ENDC}")
```

### Colored Logging Example

```python
import logging
from ivexes.colors import Colors

class ColoredFormatter(logging.Formatter):
    """Colored log formatter using IVEXES colors."""
    
    COLORS = {
        'DEBUG': Colors.OKCYAN,
        'INFO': Colors.OKGREEN,
        'WARNING': Colors.WARNING,
        'ERROR': Colors.FAIL,
        'CRITICAL': f"{Colors.BOLD}{Colors.FAIL}"
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Colors.ENDC}"
        return super().format(record)

# Setup colored logging
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(levelname)s - %(message)s'))
logger = logging.getLogger('ivexes')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Use colored logging
logger.info("Analysis started")
logger.warning("Potential vulnerability detected")
logger.error("Failed to connect to sandbox")
```

## Custom Exceptions

### Exception Hierarchy

```python
class IvexesError(Exception):
    """Base exception class for all IVEXES errors."""
    pass

class ConfigurationError(IvexesError):
    """Configuration validation failed."""
    pass

class SandboxError(IvexesError):
    """Sandbox operation failed."""
    pass

class CodeBrowserError(IvexesError):
    """Code browser operation failed."""
    pass

class VectorDatabaseError(IvexesError):
    """Vector database operation failed."""
    pass
```

### Exception Usage Examples

```python
from ivexes.exceptions import (
    IvexesError, 
    ConfigurationError, 
    SandboxError, 
    CodeBrowserError, 
    VectorDatabaseError
)

def robust_analysis_function():
    """Example of comprehensive error handling."""
    
    try:
        # Configuration validation
        if not validate_config():
            raise ConfigurationError("Invalid API key configuration")
        
        # Sandbox operations
        if not setup_sandbox():
            raise SandboxError("Failed to initialize analysis environment")
        
        # Code analysis
        if not analyze_code():
            raise CodeBrowserError("Code parsing failed")
        
        # Knowledge base queries
        if not query_vulnerabilities():
            raise VectorDatabaseError("Knowledge base unavailable")
    
    except ConfigurationError as e:
        print(f"Configuration issue: {e}")
        return {"error": "configuration", "details": str(e)}
    
    except SandboxError as e:
        print(f"Sandbox error: {e}")
        return {"error": "sandbox", "details": str(e)}
    
    except CodeBrowserError as e:
        print(f"Code analysis error: {e}")
        return {"error": "code_analysis", "details": str(e)}
    
    except VectorDatabaseError as e:
        print(f"Knowledge base error: {e}")
        return {"error": "knowledge_base", "details": str(e)}
    
    except IvexesError as e:
        print(f"General IVEXES error: {e}")
        return {"error": "general", "details": str(e)}
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "unexpected", "details": str(e)}
    
    return {"status": "success"}

# Usage with error handling
result = robust_analysis_function()
if "error" in result:
    print(f"Analysis failed: {result['error']} - {result['details']}")
else:
    print("Analysis completed successfully")
```

## Usage Examples

### Comprehensive Tool Integration

```python
"""Complete example integrating multiple tool categories."""

import asyncio
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings
from ivexes.tools import (
    date_tools, 
    cve_tools,
    create_sandbox_tools,
    create_vectordb_tools,
    create_report_tools
)
from ivexes.token import get_directory_statistics
from ivexes.container import cleanup, santize_name
from ivexes.colors import Colors
from ivexes.exceptions import IvexesError

async def comprehensive_vulnerability_analysis():
    """Complete vulnerability analysis using all available tools."""
    
    print(f"{Colors.HEADER}IVEXES Comprehensive Analysis{Colors.ENDC}")
    
    try:
        # Configuration
        settings = PartialSettings(
            model='openai/gpt-4o-mini',
            max_turns=25,
            codebase_path='/path/to/vulnerable/codebase',
            vulnerable_folder='vulnerable-v1.0',
            patched_folder='patched-v1.1',
            trace_name='comprehensive-analysis'
        )
        
        # Clean up any existing containers
        container_name = santize_name(f"analysis-{settings.trace_name}")
        cleanup(f'{container_name}-')
        
        # Analyze codebase size
        print(f"{Colors.OKCYAN}Analyzing codebase statistics...{Colors.ENDC}")
        tokens, chars, words = get_directory_statistics(settings.codebase_path)
        print(f"Codebase: {tokens:,} tokens, {chars:,} characters, {words:,} words")
        
        # Create all tools
        sandbox_tools = create_sandbox_tools(settings)
        vectordb_tools = create_vectordb_tools(settings=settings)
        report_tools = create_report_tools(settings)
        
        # Initialize agent with all tools
        agent = SingleAgent(
            bin_path='/usr/bin/vulnerable_service',
            settings=settings
        )
        
        print(f"{Colors.OKGREEN}Starting agent analysis...{Colors.ENDC}")
        
        # Agent has access to:
        # - date_tools: get_current_date
        # - cve_tools: search_cve_by_id  
        # - sandbox_tools: setup_sandbox, sandbox_run, etc.
        # - vectordb_tools: semantic_search_cwe, semantic_search_capec, etc.
        # - report_tools: create_report
        
        async for chunk in agent.run_streamed():
            print(chunk, end='', flush=True)
        
        print(f"\n{Colors.OKGREEN}Analysis completed successfully{Colors.ENDC}")
        
    except IvexesError as e:
        print(f"{Colors.FAIL}IVEXES Error: {e}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Unexpected Error: {e}{Colors.ENDC}")
    finally:
        # Cleanup
        print(f"{Colors.WARNING}Cleaning up resources...{Colors.ENDC}")
        cleanup(f'{container_name}-')

if __name__ == "__main__":
    asyncio.run(comprehensive_vulnerability_analysis())
```

### Custom Tool Development

```python
"""Example of creating custom tools that integrate with IVEXES."""

from typing import List, Dict, Any
from agents import function_tool, Tool
from ivexes.config import Settings
from ivexes.token import get_text_statistics
from ivexes.colors import Colors
from ivexes.date.tools import current_date
import json

def create_custom_analysis_tools(settings: Settings) -> List[Tool]:
    """Create custom tools for specialized analysis."""
    
    @function_tool
    def analyze_code_complexity(code: str) -> str:
        """Analyze code complexity metrics.
        
        Args:
            code: Source code to analyze
            
        Returns:
            JSON string with complexity metrics
        """
        lines = code.split('\n')
        
        metrics = {
            'timestamp': current_date(),
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'comment_lines': len([line for line in lines if line.strip().startswith('#') or line.strip().startswith('//')]),
            'function_count': code.count('def ') + code.count('function '),
            'class_count': code.count('class '),
            'import_count': code.count('import ') + code.count('from '),
            'complexity_score': 0
        }
        
        # Simple complexity calculation
        complexity_keywords = ['if', 'for', 'while', 'try', 'catch', 'switch', 'case']
        for keyword in complexity_keywords:
            metrics['complexity_score'] += code.lower().count(keyword)
        
        # Token analysis
        tokens, chars, words = get_text_statistics(code)
        metrics.update({
            'tokens': tokens,
            'characters': chars,
            'words': words,
            'token_density': tokens / len(lines) if lines else 0
        })
        
        return json.dumps(metrics, indent=2)
    
    @function_tool
    def security_keyword_scan(text: str, custom_keywords: str = "") -> str:
        """Scan text for security-related keywords.
        
        Args:
            text: Text to scan
            custom_keywords: Additional comma-separated keywords
            
        Returns:
            JSON string with scan results
        """
        # Default security keywords
        security_keywords = [
            'password', 'secret', 'token', 'key', 'auth', 'login',
            'sql', 'inject', 'xss', 'csrf', 'buffer', 'overflow',
            'vuln', 'exploit', 'backdoor', 'malware', 'attack'
        ]
        
        # Add custom keywords
        if custom_keywords:
            custom_list = [kw.strip().lower() for kw in custom_keywords.split(',')]
            security_keywords.extend(custom_list)
        
        text_lower = text.lower()
        found_keywords = {}
        
        for keyword in security_keywords:
            count = text_lower.count(keyword)
            if count > 0:
                found_keywords[keyword] = count
        
        results = {
            'timestamp': current_date(),
            'total_keywords_searched': len(security_keywords),
            'keywords_found': len(found_keywords),
            'total_matches': sum(found_keywords.values()),
            'keyword_matches': found_keywords,
            'risk_score': min(100, sum(found_keywords.values()) * 10)  # Simple risk scoring
        }
        
        return json.dumps(results, indent=2)
    
    @function_tool
    def create_analysis_summary(findings: str, severity: str = "medium") -> str:
        """Create formatted analysis summary.
        
        Args:
            findings: Analysis findings text
            severity: Severity level (low, medium, high, critical)
            
        Returns:
            Formatted summary with color coding
        """
        severity_colors = {
            'low': Colors.OKGREEN,
            'medium': Colors.WARNING,
            'high': Colors.FAIL,
            'critical': f"{Colors.BOLD}{Colors.FAIL}"
        }
        
        color = severity_colors.get(severity.lower(), Colors.OKCYAN)
        
        summary = f"""
{Colors.HEADER}Analysis Summary{Colors.ENDC}
{Colors.BOLD}Timestamp:{Colors.ENDC} {current_date()}
{Colors.BOLD}Severity:{Colors.ENDC} {color}{severity.upper()}{Colors.ENDC}
{Colors.BOLD}Trace:{Colors.ENDC} {settings.trace_name or 'N/A'}

{Colors.UNDERLINE}Findings:{Colors.ENDC}
{findings}

{Colors.OKCYAN}Generated by IVEXES Custom Analysis Tools{Colors.ENDC}
"""
        return summary
    
    return [
        analyze_code_complexity,
        security_keyword_scan,
        create_analysis_summary
    ]

# Usage example
from ivexes.agents import SingleAgent

settings = PartialSettings(
    model='openai/gpt-4o-mini',
    trace_name='custom-tool-analysis'
)

# Create custom tools
custom_tools = create_custom_analysis_tools(settings)

# Example manual usage
code_sample = """
def authenticate_user(username, password):
    if username == "admin" and password == "secret123":
        return True
    return False

def process_sql_query(query):
    # Potential SQL injection vulnerability
    cursor.execute("SELECT * FROM users WHERE id = " + query)
    return cursor.fetchall()
"""

# Test custom tools
complexity_result = custom_tools[0].func(code_sample)
security_scan = custom_tools[1].func(code_sample, "admin,secret,injection")
summary = custom_tools[2].func("Found potential SQL injection and hardcoded credentials", "high")

print("Complexity Analysis:")
print(complexity_result)
print("\nSecurity Scan:")
print(security_scan)
print("\nSummary:")
print(summary)
```

### Tool Performance Monitoring

```python
"""Performance monitoring and optimization for IVEXES tools."""

import time
import functools
from typing import Callable, Any, Dict
from ivexes.colors import Colors
from ivexes.date.tools import current_date

class ToolPerformanceMonitor:
    """Monitor and track performance of IVEXES tools."""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    def monitor_tool(self, tool_func: Callable) -> Callable:
        """Decorator to monitor tool performance."""
        
        @functools.wraps(tool_func)
        def wrapper(*args, **kwargs):
            tool_name = tool_func.__name__
            start_time = time.time()
            
            try:
                result = tool_func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Update metrics
                if tool_name not in self.metrics:
                    self.metrics[tool_name] = {
                        'total_calls': 0,
                        'total_time': 0,
                        'avg_time': 0,
                        'min_time': float('inf'),
                        'max_time': 0,
                        'last_called': None,
                        'errors': 0
                    }
                
                metrics = self.metrics[tool_name]
                metrics['total_calls'] += 1
                metrics['total_time'] += execution_time
                metrics['avg_time'] = metrics['total_time'] / metrics['total_calls']
                metrics['min_time'] = min(metrics['min_time'], execution_time)
                metrics['max_time'] = max(metrics['max_time'], execution_time)
                metrics['last_called'] = current_date()
                
                return result
                
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                
                if tool_name not in self.metrics:
                    self.metrics[tool_name] = {
                        'total_calls': 0, 'total_time': 0, 'avg_time': 0,
                        'min_time': float('inf'), 'max_time': 0, 
                        'last_called': None, 'errors': 0
                    }
                
                self.metrics[tool_name]['errors'] += 1
                self.metrics[tool_name]['total_calls'] += 1
                self.metrics[tool_name]['last_called'] = current_date()
                
                raise e
        
        return wrapper
    
    def get_performance_report(self) -> str:
        """Generate performance report for all monitored tools."""
        
        if not self.metrics:
            return f"{Colors.WARNING}No tool performance data available{Colors.ENDC}"
        
        report = f"{Colors.HEADER}Tool Performance Report{Colors.ENDC}\n"
        report += f"{Colors.BOLD}Generated: {current_date()}{Colors.ENDC}\n\n"
        
        # Sort tools by total execution time
        sorted_tools = sorted(
            self.metrics.items(), 
            key=lambda x: x[1]['total_time'], 
            reverse=True
        )
        
        for tool_name, metrics in sorted_tools:
            success_rate = ((metrics['total_calls'] - metrics['errors']) / 
                          metrics['total_calls'] * 100) if metrics['total_calls'] > 0 else 0
            
            color = Colors.OKGREEN if success_rate > 95 else Colors.WARNING if success_rate > 80 else Colors.FAIL
            
            report += f"{Colors.UNDERLINE}{tool_name}{Colors.ENDC}\n"
            report += f"  Total calls: {metrics['total_calls']}\n"
            report += f"  Success rate: {color}{success_rate:.1f}%{Colors.ENDC}\n"
            report += f"  Total time: {metrics['total_time']:.3f}s\n"
            report += f"  Avg time: {metrics['avg_time']:.3f}s\n"
            report += f"  Min time: {metrics['min_time']:.3f}s\n"
            report += f"  Max time: {metrics['max_time']:.3f}s\n"
            report += f"  Last called: {metrics['last_called']}\n"
            if metrics['errors'] > 0:
                report += f"  {Colors.FAIL}Errors: {metrics['errors']}{Colors.ENDC}\n"
            report += "\n"
        
        return report
    
    def reset_metrics(self):
        """Reset all performance metrics."""
        self.metrics.clear()

# Usage example
monitor = ToolPerformanceMonitor()

# Monitor existing tools
from ivexes.token import get_text_statistics, get_directory_statistics
from ivexes.container import find_by_name, cleanup

# Wrap tools with monitoring
monitored_get_text_statistics = monitor.monitor_tool(get_text_statistics)
monitored_get_directory_statistics = monitor.monitor_tool(get_directory_statistics)
monitored_find_by_name = monitor.monitor_tool(find_by_name)

# Use monitored tools
test_text = "This is a test vulnerability analysis with multiple security keywords like password and sql injection."

# Perform operations
stats1 = monitored_get_text_statistics(test_text)
stats2 = monitored_get_text_statistics(test_text * 10)  # Larger text
container = monitored_find_by_name('nonexistent-container', start=False)

# Generate performance report
print(monitor.get_performance_report())
```

## Integration Patterns

### Agent Tool Integration

All tools are designed to work seamlessly with IVEXES agents:

```python
from ivexes.agents import SingleAgent
from ivexes.tools import *
from ivexes.config import PartialSettings

# Tools are automatically available to agents
settings = PartialSettings(model='openai/gpt-4o-mini')
agent = SingleAgent(settings=settings)

# Agent can use:
# - get_current_date() for timestamps
# - search_cve_by_id() for vulnerability research
# - All sandbox, code browser, and vector DB tools
# - create_report() for documentation
```

### Multi-Agent Tool Sharing

```python
from ivexes.agents.multi_agent import MultiAgent
from ivexes.tools import create_vectordb_tools, create_report_tools

# Shared tools across multiple agents
vectordb_tools = create_vectordb_tools()
report_tools = create_report_tools(settings)

multi_agent = MultiAgent(settings=settings)
# All sub-agents have access to shared tool instances
```

## Best Practices

### Tool Selection

1. **Use Appropriate Tools**: Choose tools based on specific functionality needs
2. **Monitor Performance**: Use performance monitoring for optimization
3. **Handle Errors**: Implement comprehensive error handling
4. **Cache Results**: Cache expensive operations when possible
5. **Clean Resources**: Properly clean up containers and temporary files

### Error Handling

```python
from ivexes.exceptions import IvexesError

try:
    result = some_tool_function()
except IvexesError as e:
    # Handle IVEXES-specific errors
    logger.error(f"Tool error: {e}")
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
```

### Resource Management

```python
from ivexes.container import cleanup
import atexit

# Register cleanup on exit
atexit.register(lambda: cleanup('analysis-'))

# Use context managers where available
with Sandbox(settings) as sandbox:
    # Automatic cleanup
    pass
```

## See Also

- [Sandbox API](sandbox.md) - Sandbox tools and container management
- [Vector Database API](vector_db.md) - Knowledge base tools and search
- [CVE Search API](cve_search.md) - Vulnerability research tools
- [Configuration API](config.md) - Settings and configuration management
- [Examples Guide](../documentation/examples.md) - Practical usage examples