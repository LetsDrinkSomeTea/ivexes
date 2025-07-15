# Code Browser

The Code Browser provides intelligent code analysis and navigation capabilities for security-focused source code review.

## Overview

The Code Browser is designed to help security analysts understand and navigate complex codebases efficiently. It provides:

- **Syntax-aware parsing** for multiple programming languages
- **Security-focused analysis** highlighting potential vulnerabilities
- **Interactive navigation** through code structures
- **Integration with editors** like Neovim for enhanced workflow

## Supported Languages

- C/C++
- Python
- JavaScript/TypeScript
- Java
- Go
- Rust
- PHP
- And more through extensible parsers

## Key Features

### Intelligent Parsing
- Abstract Syntax Tree (AST) generation
- Symbol table construction
- Control flow analysis
- Data flow tracking

### Security Analysis
- Vulnerability pattern detection
- Dangerous function identification
- Input validation analysis
- Authentication/authorization flow review

### Navigation Tools
- Function and class definitions
- Cross-references and call graphs
- Dependency tracking
- Code structure visualization

## Usage

### Basic Code Analysis

```python
from ivexes.code_browser import CodeBrowser

browser = CodeBrowser()

# Analyze a file
analysis = browser.analyze_file("/path/to/source.c")

# Get function definitions
functions = analysis.get_functions()

# Find security patterns
vulnerabilities = analysis.find_vulnerabilities()
```

### Interactive Navigation

```python
# Navigate to function definition
browser.goto_definition("vulnerable_function")

# Find all references
references = browser.find_references("user_input")

# Analyze call chains
call_chain = browser.trace_calls("main", "system")
```

### Integration with Analysis Tools

```python
# Use with sandbox for dynamic analysis
from ivexes.sandbox import Sandbox

sandbox = Sandbox()
browser = CodeBrowser()

# Static analysis first
static_results = browser.analyze_file("target.c")

# Then dynamic analysis
dynamic_results = sandbox.execute_with_analysis("target")

# Correlate findings
correlation = browser.correlate_static_dynamic(
    static_results, 
    dynamic_results
)
```

## Configuration

### Parser Settings

```python
from ivexes.code_browser import CodeBrowser, ParserConfig

config = ParserConfig(
    # Language-specific settings
    c_include_paths=["/usr/include", "/opt/local/include"],
    python_path=["/usr/lib/python3.9"],
    
    # Analysis depth
    max_depth=10,
    follow_includes=True,
    
    # Security focus
    enable_vulnerability_detection=True,
    custom_patterns="/path/to/patterns.yml"
)

browser = CodeBrowser(config=config)
```

### Editor Integration

#### Neovim Setup

1. Install the IVEXES Neovim plugin
2. Configure LSP integration
3. Set up keybindings for navigation

```vim
" .vimrc configuration
let g:ivexes_enable = 1
let g:ivexes_auto_analyze = 1

" Keybindings
nnoremap gd :IvexesGotoDefinition<CR>
nnoremap gr :IvexesFindReferences<CR>
nnoremap gs :IvexesSecurityAnalysis<CR>
```

## Security Analysis Features

### Vulnerability Detection

The Code Browser can identify common security vulnerabilities:

- **Buffer Overflows**: Array bounds checking, string manipulation
- **Injection Attacks**: SQL injection, command injection, XSS
- **Authentication Issues**: Weak authentication, session management
- **Cryptographic Problems**: Weak algorithms, key management
- **Race Conditions**: Thread safety, TOCTOU vulnerabilities

### Pattern Matching

Custom security patterns can be defined:

```yaml
# security_patterns.yml
patterns:
  - name: "SQL Injection"
    pattern: "sprintf.*%s.*query"
    severity: "high"
    description: "Potential SQL injection vulnerability"
  
  - name: "Buffer Overflow"
    pattern: "strcpy|strcat|sprintf"
    severity: "medium"
    description: "Unsafe string function usage"
```

### Code Quality Analysis

- **Complexity Metrics**: Cyclomatic complexity, nesting depth
- **Code Smells**: Long functions, large classes, duplicated code
- **Best Practices**: Security coding standards compliance
- **Documentation**: Function documentation coverage

## Best Practices

### Effective Code Review

1. **Start with Entry Points**: Analyze main functions, API endpoints
2. **Follow Data Flow**: Trace user input through the application
3. **Focus on Trust Boundaries**: Examine input validation and sanitization
4. **Review Error Handling**: Check for information leakage
5. **Analyze Authentication**: Verify access control mechanisms

### Performance Optimization

1. **Use Incremental Analysis**: Only re-analyze changed files
2. **Configure Parser Limits**: Set appropriate depth and timeout limits
3. **Cache Results**: Enable result caching for large codebases
4. **Selective Analysis**: Focus on security-critical components

## Troubleshooting

### Common Issues

**Parser Errors**
- Check include paths and dependencies
- Verify source code syntax
- Update parser configurations

**Performance Problems**
- Reduce analysis depth
- Enable incremental parsing
- Check system resources

**Missing Dependencies**
- Install required language parsers
- Configure environment paths
- Update parser plugins

## Advanced Features

### Custom Analyzers

```python
from ivexes.code_browser.parser import BaseAnalyzer

class CustomSecurityAnalyzer(BaseAnalyzer):
    def analyze_function(self, function_node):
        # Custom security analysis logic
        vulnerabilities = []
        
        # Check for specific patterns
        if self.has_unsafe_patterns(function_node):
            vulnerabilities.append({
                "type": "custom_vulnerability",
                "severity": "high",
                "location": function_node.location
            })
        
        return vulnerabilities

# Register custom analyzer
browser.register_analyzer(CustomSecurityAnalyzer())
```

### API Integration

```python
# RESTful API for code analysis
from ivexes.code_browser.api import CodeBrowserAPI

api = CodeBrowserAPI(browser)

# Analyze via HTTP endpoint
response = api.analyze_endpoint(
    "/api/analyze",
    {
        "file_path": "/path/to/code.c",
        "analysis_type": "security"
    }
)
```

## See Also

- [Sandbox Integration](sandbox.md)
- [API Reference](../api/code-browser.md)
- [Configuration Guide](../getting-started/configuration.md)