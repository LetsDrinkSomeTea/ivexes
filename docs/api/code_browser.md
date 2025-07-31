# Code Browser API Reference

## Overview

The code browser module provides comprehensive code analysis capabilities through Language Server Protocol (LSP) integration. It runs in a containerized Neovim environment to deliver consistent analysis across different programming languages and systems.

The module is designed for security-focused code analysis, offering symbol navigation, reference finding, code structure analysis, and diff generation capabilities. All operations run in isolated Docker containers to ensure security and reproducibility.

## Core Classes

### CodeBrowser

The main interface for LSP-based code analysis and navigation.

```python
from ivexes.code_browser import CodeBrowser
from ivexes.config import Settings
```

#### Class Definition

```python
class CodeBrowser:
    """LSP-based code browser for comprehensive code analysis.
    
    This class provides a high-level interface for analyzing codebases using
    Neovim's Language Server Protocol capabilities in a containerized environment.
    It supports various programming languages and provides symbol navigation,
    reference finding, and code structure analysis.
    """
```

#### Constructor

```python
def __init__(
    self,
    settings: Settings,
    port: int = 8080,
    load: Literal['lazy', 'eager'] = 'lazy',
) -> None:
    """Initialize the CodeBrowser with codebase and connection parameters.
    
    Args:
        settings: Settings instance containing codebase paths and configurations.
        port: Port number for Neovim TCP connection (default: 8080).
        load: Load mode - 'lazy' defers initialization, 'eager' initializes immediately.
        
    Raises:
        ValueError: If required codebase settings are missing.
        SystemExit: If connection to Neovim fails.
    """
```

#### Required Configuration

The CodeBrowser requires specific settings to be configured:

```python
from ivexes.config import PartialSettings

settings = PartialSettings(
    codebase_path="/path/to/project",      # Root directory containing code
    vulnerable_folder="vulnerable",        # Vulnerable version folder name
    patched_folder="patched"              # Patched version folder name
)
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `settings` | `Settings` | Complete configuration settings |
| `path` | `str` | Absolute path to the codebase directory |
| `vulnerable_folder` | `str` | Name of the vulnerable code folder |
| `patched_folder` | `str` | Name of the patched code folder |
| `port` | `int` | TCP port for Neovim connection |
| `container` | `Container` | Docker container instance |
| `nvim` | `pynvim.Nvim` | PyNvim client instance |

#### Core Methods

##### Initialization

```python
def initialize(self) -> None:
    """Initialize the CodeBrowser by setting up Docker container and Neovim connection.
    
    This method sets up the Docker container for the codebase and establishes
    a connection to Neovim using PyNvim for LSP capabilities.
    
    Raises:
        SystemExit: If connection to Neovim fails.
    """
```

##### File Content Analysis

```python
def get_file_content(
    self,
    file: str,
    offset: int = 0,
    limit: int = 50,
    encode: Literal['auto', 'raw'] = 'auto',
) -> str | None:
    """Get the content of a file from the container.
    
    Args:
        file: Path to the file within the container.
        offset: Start line number (0-indexed).
        limit: Maximum number of lines to return.
        encode: Encoding type - 'auto' uses chardet detection, 'raw' returns bytes.
        
    Returns:
        The file content as a string, or None if file not found.
    """
```

##### Codebase Structure

```python
def get_codebase_structure(self, n: int = 3) -> str:
    """Get the structure of the codebase using the tree command.
    
    Args:
        n: Maximum depth level of the tree.
        
    Returns:
        String representation of the codebase directory structure.
    """
```

##### Symbol Analysis

```python
def get_symbols(self, file: str) -> list[tuple[str, str, int, tuple[int, int]]]:
    """Get all symbols in the specified file using LSP.
    
    Args:
        file: Path to the file to analyze.
        
    Returns:
        List of tuples containing:
        - symbol_name (str): Name of the symbol
        - symbol_type (str): Type of symbol (function, class, variable, etc.)
        - line_number (int): Line number where symbol is defined
        - range (tuple): Symbol range as (start_col, end_col)
    """
```

##### Reference Finding

```python
def get_references(
    self, symbol: str
) -> list[tuple[str, str, int, tuple[int, int]]]:
    """Get all references to a symbol in the codebase using LSP.
    
    Args:
        symbol: The symbol name to find references for.
        
    Returns:
        List of tuples containing:
        - file_path (str): Path to the file containing the reference
        - code_context (str): The line of code containing the reference
        - line_number (int): Line number where reference appears
        - range (tuple): Reference range as (start_col, end_col)
    """
```

##### Definition Location

```python
def get_definition(self, symbol: str) -> tuple[str, str, int, int]:
    """Find the definition of a symbol using LSP.
    
    Args:
        symbol: The symbol name to find the definition for.
        
    Returns:
        Tuple containing (definition_content, file_path, begin_line, end_line).
    """
```

##### Diff Generation

```python
def get_diff(
    self,
    options: Optional[list[str]] = None,
    file1: Optional[str] = None,
    file2: Optional[str] = None,
) -> list[str]:
    """Generate diff between vulnerable and patched versions.
    
    Args:
        options: Diff command options (default: ['-u', '-w']).
        file1: First file/directory path (default: vulnerable_folder).
        file2: Second file/directory path (default: patched_folder).
        
    Returns:
        List of strings, each containing the diff for one file.
    """
```

#### Usage Examples

##### Basic Code Analysis

```python
from ivexes.code_browser import CodeBrowser
from ivexes.config import PartialSettings

# Configure code browser
settings = PartialSettings(
    codebase_path='/project/analysis',
    vulnerable_folder='vulnerable-v1.0',
    patched_folder='patched-v1.1'
)

# Create browser instance
browser = CodeBrowser(settings=settings, port=8080)

# Get codebase structure
structure = browser.get_codebase_structure(n=3)
print("Project structure:")
print(structure)

# Analyze file symbols
symbols = browser.get_symbols('src/main.c')
for name, type_info, line, (start, end) in symbols:
    print(f"{name} ({type_info}) at line {line}, columns {start}-{end}")
```

##### Symbol Reference Analysis

```python
# Find all references to a function
references = browser.get_references('vulnerable_function')
print(f"Found {len(references)} references:")

for file_path, code_context, line, (start, end) in references:
    print(f"  {file_path}:{line}:{start}-{end}")
    print(f"    {code_context}")
```

##### Definition Retrieval

```python
# Get function definition
definition, file_path, start_line, end_line = browser.get_definition('malloc')
print(f"Definition found in {file_path} (lines {start_line}-{end_line}):")
print(definition)
```

##### Code Comparison

```python
# Generate diff between versions
diffs = browser.get_diff(options=['-u', '-w'])
print(f"Found differences in {len(diffs)} files:")

for diff in diffs:
    print("=" * 50)
    print(diff)
```

##### File Content Reading

```python
# Read file with pagination
content = browser.get_file_content(
    file='src/vulnerable.c',
    offset=100,    # Start from line 100
    limit=50,      # Read 50 lines
    encode='auto'  # Auto-detect encoding
)
print("File content (lines 100-150):")
print(content)
```

### Container Management

#### setup_container

Container setup and lifecycle management for Neovim LSP analysis.

```python
from ivexes.code_browser.nvim import setup_container
from ivexes.config import Settings
```

#### Function Definition

```python
def setup_container(
    code_base: str, 
    settings: Settings, 
    port: int = 8080, 
    renew: bool = False
) -> Container:
    """Set up a Docker container with codebase mounted for Neovim LSP analysis.
    
    Args:
        code_base: Path to the codebase directory to be mounted.
        settings: Configuration settings for the container.
        port: Port number to expose from the container.
        renew: Whether to remove existing container and create new one.
        
    Returns:
        Docker container object configured for LSP analysis.
        
    Raises:
        ContainerError: If container creation fails.
        ImageNotFound: If nvim-lsp image is not available.
    """
```

#### Container Configuration

The setup function creates containers with:

- **Image**: `nvim-lsp:latest` with pre-configured LSP servers
- **Volume Mount**: Codebase mounted read-only at `/codebase`
- **Port Mapping**: Neovim TCP server exposed on specified port
- **Auto-removal**: Container removed when stopped
- **Startup Delay**: 30-second initialization period

#### Usage Example

```python
from ivexes.code_browser.nvim import setup_container
from ivexes.config import create_settings

settings = create_settings()
container = setup_container(
    code_base='/path/to/project',
    settings=settings,
    port=8080,
    renew=True  # Force new container creation
)

print(f"Container {container.name} running on port 8080")
```

## Parser Functions

### Symbol Parsing

#### parse_symbols

Parse LSP symbol output into structured data.

```python
from ivexes.code_browser.parser import parse_symbols
from pynvim.api import Buffer
```

#### Function Definition

```python
def parse_symbols(buffer: Buffer) -> list[tuple[str, str, int, tuple[int, int]]]:
    """Parse symbol information from LSP output lines.
    
    Args:
        buffer: Buffer containing LSP output in format:
            <filename>|<line> col <col_start>-<col_end>| [<type>] <name>
            
    Returns:
        List of tuples: (name, type, line_no, (col_start, col_end))
    """
```

#### Expected Input Format

```
src/main.c|45 col 12-25| [function] vulnerable_func
src/main.c|67 col 5-15| [variable] buffer_size
include/header.h|23 col 8-20| [struct] user_data
```

#### Usage Example

```python
# Parse symbols from LSP buffer
symbols = parse_symbols(nvim_buffer)
for name, symbol_type, line, (start, end) in symbols:
    print(f"Symbol: {name} ({symbol_type}) at {line}:{start}-{end}")
```

### Reference Parsing

#### parse_references

Parse LSP reference output into structured data.

```python
from ivexes.code_browser.parser import parse_references
```

#### Function Definition

```python
def parse_references(buffer: Buffer) -> list[tuple[str, str, int, tuple[int, int]]]:
    """Parse reference information from LSP output lines.
    
    Args:
        buffer: Buffer containing LSP output in format:
            <filename>|<line> col <col_start>-<col_end>| <code>
            
    Returns:
        List of tuples: (filename, code, line_no, (col_start, col_end))
    """
```

#### Expected Input Format

```
src/main.c|45 col 12-25| vulnerable_func(user_input);
src/utils.c|78 col 8-21| if (vulnerable_func(data) < 0)
test/test.c|34 col 16-29| result = vulnerable_func(buffer);
```

#### Usage Example

```python
# Parse references from LSP buffer
references = parse_references(nvim_buffer)
for filename, code, line, (start, end) in references:
    print(f"Reference in {filename}:{line}:{start}-{end}")
    print(f"  Code: {code}")
```

## Agent Integration Tools

### Code Browser Tools

Agent-compatible tools that wrap CodeBrowser functionality for multi-agent systems.

```python
from ivexes.code_browser.tools import create_code_browser_tools
from ivexes.code_browser import CodeBrowser
from ivexes.config import Settings
```

#### Tool Factory

```python
def create_code_browser_tools(
    code_browser: Optional[CodeBrowser] = None, 
    settings: Optional[Settings] = None
) -> list[Tool]:
    """Create code browser tools with dependency injection.
    
    Args:
        code_browser: Existing CodeBrowser instance (optional).
        settings: Settings for creating new CodeBrowser if needed.
        
    Returns:
        List of agent-compatible tools for code analysis.
    """
```

#### Available Tools

##### codebrowser_get_definition
```python
@function_tool
def codebrowser_get_definition(symbol: str) -> str:
    """Find the definition of a symbol in the codebase.
    
    Args:
        symbol: The symbol name to find the definition for.
        
    Returns:
        Formatted definition with location information.
    """
```

##### codebrowser_get_references
```python
@function_tool
def codebrowser_get_references(symbol: str) -> str:
    """Find all references to a symbol in the codebase.
    
    Args:
        symbol: The symbol name to find references for.
        
    Returns:
        Formatted list of all references with locations.
    """
```

##### codebrowser_get_symbols
```python
@function_tool
def codebrowser_get_symbols(file: str) -> str:
    """Get all symbols in a file.
    
    Args:
        file: Path to the file within the codebase to analyze.
        
    Returns:
        Formatted list of all symbols with types and locations.
    """
```

##### codebrowser_get_file_content
```python
@function_tool
def codebrowser_get_file_content(
    file: str,
    offset: int = 0,
    limit: int = 50,
    encode: Literal['auto', 'raw'] = 'auto',
) -> str:
    """Get the content of a file in the codebase.
    
    Args:
        file: Path to the file within the codebase.
        offset: Line number to start reading from (0-based).
        limit: Maximum number of lines to read.
        encode: Encoding type - 'auto' or 'raw'.
        
    Returns:
        Formatted file content.
    """
```

##### codebrowser_get_file_structure
```python
@function_tool
def codebrowser_get_file_structure(depth: int = 3) -> str:
    """Get the tree of files in the codebase.
    
    Args:
        depth: Maximum depth level of the tree.
        
    Returns:
        Formatted directory tree structure.
    """
```

##### codebrowser_get_diff
```python
@function_tool
def codebrowser_get_diff(
    file1: str = 'vulnerable_folder',
    file2: str = 'patched_folder',
    options: Optional[list[str]] = None,
) -> str:
    """Get the diff between code versions.
    
    Args:
        file1: First file/directory to compare.
        file2: Second file/directory to compare.
        options: Diff command options.
        
    Returns:
        Formatted diff output.
    """
```

#### Agent Integration Example

```python
from ivexes.code_browser.tools import create_code_browser_tools
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

# Create agent with code browser tools
settings = PartialSettings(
    codebase_path='/analysis/project',
    vulnerable_folder='vulnerable',
    patched_folder='patched'
)

# Tools are automatically integrated into agents
agent = SingleAgent(bin_path='/target/binary', settings=settings)

# Agent can now use code browser capabilities
result = agent.run("""
Analyze the codebase structure, find the main function, 
and identify any vulnerable functions it calls.
""")
```

## Error Handling

### Common Error Scenarios

#### Container Setup Errors

```python
from docker.errors import ContainerError, ImageNotFound

try:
    browser = CodeBrowser(settings=settings)
    browser.initialize()
except ContainerError as e:
    print(f"Container failed to start: {e}")
    # Check Docker daemon and container configuration
except ImageNotFound as e:
    print(f"Required image not found: {e}")
    # Build or pull the nvim-lsp:latest image
```

#### Configuration Errors

```python
from ivexes.code_browser import CodeBrowser
from ivexes.config import PartialSettings

try:
    settings = PartialSettings()  # Missing required paths
    browser = CodeBrowser(settings=settings)
except ValueError as e:
    print(f"Configuration error: {e}")
    # Ensure codebase_path, vulnerable_folder, and patched_folder are set
```

#### LSP Analysis Errors

```python
try:
    symbols = browser.get_symbols('nonexistent_file.c')
except Exception as e:
    print(f"Symbol analysis failed: {e}")
    # Check file path and LSP server status

try:
    references = browser.get_references('unknown_symbol')
    if not references:
        print("No references found - symbol may not exist")
except Exception as e:
    print(f"Reference search failed: {e}")
```

### Best Practices

#### Resource Management

```python
import logging
from ivexes.code_browser import CodeBrowser

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Use lazy loading for performance
browser = CodeBrowser(settings=settings, load='lazy')

# Initialize only when needed
if analysis_needed:
    browser.initialize()
```

#### Performance Optimization

```python
# Limit file content reading
content = browser.get_file_content(
    file='large_file.c',
    offset=0,
    limit=100  # Read only first 100 lines
)

# Use appropriate tree depth
structure = browser.get_codebase_structure(n=2)  # Shallow structure for overview
```

#### Container Management

```python
from ivexes.code_browser.nvim import setup_container

# Force container renewal for clean state
container = setup_container(
    code_base='/path/to/code',
    settings=settings,
    renew=True  # Clean container
)

# Use unique ports for parallel analysis
browser1 = CodeBrowser(settings=settings1, port=8080)
browser2 = CodeBrowser(settings=settings2, port=8081)
```

## Performance Considerations

### Container Optimization

- **Container Reuse**: Containers are reused by default to improve performance
- **Image Preparation**: Ensure `nvim-lsp:latest` image is pre-built and cached
- **Volume Mounting**: Read-only mounts improve security and performance

### LSP Server Performance

- **Language Support**: Different LSP servers have varying performance characteristics
- **Project Size**: Large codebases may require longer initialization times
- **Symbol Caching**: LSP servers cache symbol information for better performance

### Memory Management

- **File Reading**: Use `offset` and `limit` parameters for large files
- **Symbol Analysis**: Results are processed incrementally to manage memory
- **Container Limits**: Consider Docker memory constraints for large codebases

## Examples

### Complete Vulnerability Analysis

```python
import asyncio
from ivexes.code_browser import CodeBrowser
from ivexes.config import PartialSettings

async def vulnerability_analysis():
    """Complete vulnerability analysis using code browser."""
    
    settings = PartialSettings(
        codebase_path='/analysis/vulnerable-app',
        vulnerable_folder='v1.0-vulnerable',
        patched_folder='v1.1-fixed'
    )
    
    browser = CodeBrowser(settings=settings)
    
    print("=== Codebase Structure ===")
    structure = browser.get_codebase_structure(n=3)
    print(structure)
    
    print("\n=== Main Function Analysis ===")
    main_symbols = browser.get_symbols('src/main.c')
    for name, type_info, line, range_info in main_symbols:
        if 'main' in name.lower():
            print(f"Found {name} ({type_info}) at line {line}")
    
    print("\n=== Vulnerability Search ===")
    vulnerable_functions = ['strcpy', 'strcat', 'sprintf', 'gets']
    
    for func in vulnerable_functions:
        references = browser.get_references(func)
        if references:
            print(f"\n{func} used in {len(references)} locations:")
            for file_path, code, line, _ in references:
                print(f"  {file_path}:{line} - {code.strip()}")
    
    print("\n=== Code Changes Analysis ===")
    diffs = browser.get_diff()
    for i, diff in enumerate(diffs):
        print(f"\n--- File Change {i+1} ---")
        print(diff[:500] + "..." if len(diff) > 500 else diff)

asyncio.run(vulnerability_analysis())
```

### Multi-File Symbol Search

```python
def search_symbols_across_files(browser, symbol_pattern):
    """Search for symbols matching a pattern across multiple files."""
    
    # Get all C files in the project
    structure = browser.get_codebase_structure(n=5)
    
    # Extract .c and .h files (simple pattern matching)
    import re
    files = re.findall(r'[^\s]+\.c(?:pp)?|[^\s]+\.h(?:pp)?', structure)
    
    results = {}
    for file in files[:10]:  # Limit to first 10 files
        try:
            symbols = browser.get_symbols(file)
            matching_symbols = [
                (name, type_info, line, range_info) 
                for name, type_info, line, range_info in symbols
                if symbol_pattern.lower() in name.lower()
            ]
            if matching_symbols:
                results[file] = matching_symbols
        except Exception as e:
            print(f"Error analyzing {file}: {e}")
    
    return results

# Usage
browser = CodeBrowser(settings=settings)
buffer_symbols = search_symbols_across_files(browser, 'buffer')

for file, symbols in buffer_symbols.items():
    print(f"\nBuffer-related symbols in {file}:")
    for name, type_info, line, _ in symbols:
        print(f"  {name} ({type_info}) at line {line}")
```

## See Also

- [Agents API](agents.md) - Agent classes that integrate code browser functionality
- [Configuration API](config.md) - Settings and configuration management
- [Sandbox API](sandbox.md) - Execution environment management for dynamic analysis
- [Tools API](tools.md) - Additional utility functions and tools
- [Usage Guide](../documentation/usage.md) - Common workflows and best practices