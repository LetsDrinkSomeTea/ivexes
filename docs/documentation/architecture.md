# Architecture Guide

## Overview

IVEXES (Intelligent Vulnerability Extraction & Exploit Synthesis) is a Python framework designed for cybersecurity vulnerability analysis and exploitation using multi-agent AI systems. It combines knowledge bases (CWE, CAPEC, MITRE ATT&CK) with dynamic analysis capabilities for automated security assessment.

The system follows a modular architecture with clear separation of concerns, enabling extensibility and maintainability while providing powerful vulnerability analysis capabilities.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         IVEXES Framework                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │     Agents      │    │  Code Browser   │    │    Sandbox     │  │
│  │                 │    │                 │    │                 │  │
│  │  • BaseAgent    │◄──►│  • CodeBrowser  │◄──►│  • Sandbox     │  │
│  │  • SingleAgent  │    │  • Nvim LSP     │    │  • Container   │  │
│  │  • MultiAgent   │    │  • Parser       │    │  • Kali Linux  │  │
│  │  • MVPAgent     │    │  • Navigation   │    │  • Isolation   │  │
│  │  • HTBAgent     │    │                 │    │                 │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│           │                       │                       │         │
│           │                       │                       │         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   Vector DB     │    │  Configuration  │    │     Printer     │  │
│  │                 │    │                 │    │                 │  │
│  │  • ChromaDB     │◄──►│  • Settings     │◄──►│  • Formatter   │  │
│  │  • Embeddings   │    │  • Environment  │    │  • Components  │  │
│  │  • MITRE Data   │    │  • Validation   │    │  • Output      │  │
│  │  • CVE Search   │    │                 │    │                 │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Relationships

The architecture is built around several key components that work together:

1. **Agents** serve as the intelligence layer, orchestrating analysis workflows
2. **Code Browser** provides code analysis and navigation capabilities
3. **Sandbox** offers isolated execution environments for dynamic analysis
4. **Vector Database** stores and retrieves vulnerability knowledge
5. **Configuration** manages settings and environment parameters
6. **Printer** handles formatted output and reporting

## Core Components

### Agent System

The agent system forms the core intelligence layer of IVEXES, implementing different analysis strategies:

#### BaseAgent (Abstract)
- **Purpose**: Provides common functionality and interface for all agents
- **Key Features**:
  - Settings management and validation
  - Execution modes (sync, streaming, interactive)
  - Session tracking and persistence
  - Resource cleanup and lifecycle management
- **Design Pattern**: Template Method Pattern

#### SingleAgent
- **Purpose**: Individual vulnerability analysis with comprehensive toolset
- **Key Features**:
  - Code browser integration for source analysis
  - Sandbox tools for dynamic testing
  - Vector database integration for knowledge retrieval
  - CVE search capabilities
- **Use Cases**: Focused vulnerability assessment, binary analysis

#### MultiAgent
- **Purpose**: Orchestrated multi-agent analysis for complex scenarios
- **Key Features**:
  - Shared context management across agents
  - Coordinated workflow execution
  - Distributed analysis capabilities
  - Result aggregation and synthesis
- **Use Cases**: Large-scale assessments, collaborative analysis

#### Specialized Agents
- **MVPAgent**: Minimal viable product implementation for basic functionality
- **HTBChallengeAgent**: Specialized for Hack The Box challenge analysis
- **DefaultAgent**: General-purpose implementation with standard configuration

### Code Browser System

The code browser provides sophisticated code analysis capabilities through LSP integration:

#### Architecture
```
┌─────────────────┐
│   CodeBrowser   │
├─────────────────┤
│ • Structure     │◄──┐
│ • Navigation    │   │
│ • Diff Analysis │   │
└─────────────────┘   │
         │             │
         ▼             │
┌─────────────────┐   │
│   Nvim LSP      │   │
├─────────────────┤   │
│ • Language      │   │
│   Server        │   │
│ • Semantic      │   │
│   Analysis      │   │
│ • Completion    │   │
└─────────────────┘   │
         │             │
         ▼             │
┌─────────────────┐   │
│     Parser      │───┘
├─────────────────┤
│ • Tree-sitter   │
│ • AST Analysis  │
│ • Code Structure│
└─────────────────┘
```

#### Key Features
- **LSP Integration**: Leverages Language Server Protocol for accurate code analysis
- **Container Isolation**: Runs in isolated Docker environment for security
- **Multi-language Support**: Supports various programming languages through LSP
- **Diff Analysis**: Compares vulnerable and patched versions
- **Code Navigation**: Semantic code browsing and symbol resolution

### Sandbox System

The sandbox provides secure, isolated execution environments for dynamic analysis:

#### Architecture
```
┌─────────────────┐
│     Sandbox     │
├─────────────────┤
│ • Lifecycle     │
│ • Configuration │
│ • Tool Access   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ SandboxContainer│
├─────────────────┤
│ • Docker Mgmt   │
│ • File Transfer │
│ • Execution     │
│ • Monitoring    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Kali Linux     │
├─────────────────┤
│ • Security Tools│
│ • SSH Access    │
│ • Isolated Env  │
│ • Auto Setup    │
└─────────────────┘
```

#### Key Features
- **Container-based Isolation**: Docker containers for secure execution
- **Kali Linux Environment**: Pre-configured with security testing tools  
- **Automatic Setup**: Extracts and configures analysis targets from archives
- **SSH Integration**: Remote command execution and file transfer
- **Resource Management**: Container lifecycle and resource cleanup

### Vector Database System

The vector database manages vulnerability knowledge and enables semantic search:

#### Architecture
```
┌─────────────────┐
│    VectorDB     │
├─────────────────┤
│ • Query Interface│
│ • Embeddings    │
│ • Similarity    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│    ChromaDB     │
├─────────────────┤
│ • Storage       │
│ • Indexing      │
│ • Retrieval     │
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CWE/CAPEC     │    │  MITRE ATT&CK   │    │   CVE Search    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Weaknesses    │    │ • Tactics       │    │ • Vulnerabilities│
│ • Attack Patterns│    │ • Techniques    │    │ • Metadata      │
│ • Mitigations   │    │ • Procedures    │    │ • Scoring       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Key Features
- **Knowledge Integration**: CWE, CAPEC, and MITRE ATT&CK frameworks
- **Semantic Search**: Embedding-based similarity matching
- **Multiple Providers**: Support for various embedding providers
- **CVE Integration**: Real-time vulnerability data retrieval
- **Pattern Matching**: Vulnerability pattern recognition and correlation

## Data Flow

### Analysis Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │───►│   Agent     │◄──►│ Configuration│
│   Input     │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ Code Browser│
                   │   Analysis  │
                   └─────────────┘
                           │
                           ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Vector DB  │◄──►│   Agent     │◄──►│   Sandbox   │
│  Knowledge  │    │ Processing  │    │  Execution  │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │   Report    │
                   │ Generation  │
                   └─────────────┘
```

### Information Flow

1. **Input Processing**: User provides analysis target and configuration
2. **Code Analysis**: CodeBrowser examines source code structure and differences
3. **Knowledge Retrieval**: VectorDB searches for relevant vulnerability patterns
4. **Dynamic Analysis**: Sandbox executes tests in isolated environment
5. **Synthesis**: Agent combines static and dynamic analysis results
6. **Output Generation**: Printer formats and presents findings

## Design Patterns

### Template Method Pattern
**Used in**: BaseAgent class
**Purpose**: Define the skeleton of algorithm in superclass, let subclasses override specific steps
```python
class BaseAgent(ABC):
    def run(self):  # Template method
        self._check_settings()
        with trace():
            return self._execute()  # Abstract method
    
    @abstractmethod
    def _setup_agent(self):  # Primitive operation
        pass
```

### Strategy Pattern
**Used in**: Agent execution modes
**Purpose**: Define family of algorithms, make them interchangeable
- Synchronous execution (`run()`)
- Streaming execution (`run_streamed()`)
- Interactive execution (`run_interactive()`)

### Factory Pattern
**Used in**: Tool creation and agent initialization
**Purpose**: Create objects without specifying exact class
```python
def create_sandbox_tools(settings): ...
def create_code_browser_tools(browser): ...
def create_vectordb_tools(db): ...
```

### Observer Pattern
**Used in**: Streaming results and progress tracking
**Purpose**: Define one-to-many dependency between objects
- Result streaming callbacks
- Progress hooks
- Session tracking

### Dependency Injection
**Used in**: Settings and service configuration
**Purpose**: Provide dependencies from external source
```python
class BaseAgent:
    def __init__(self, settings: PartialSettings):
        self.settings = create_settings(settings)  # DI
        self.code_browser = CodeBrowser(self.settings)  # DI
```

## Extension Points

### Custom Agents
Create new agent types by extending BaseAgent:
```python
class CustomAgent(BaseAgent):
    def _setup_agent(self):
        # Configure agent-specific tools and prompts
        self.agent = Agent(name="Custom", tools=custom_tools)
        self.user_msg = "Custom analysis prompt"
```

### Tool Integration
Add new analysis tools by implementing the tool interface:
```python
def custom_analysis_tool(context: str) -> str:
    """Custom analysis functionality."""
    return analysis_result

tools = [custom_analysis_tool] + existing_tools
```

### Knowledge Sources
Extend vector database with new knowledge sources:
```python
class CustomKnowledgeDB(VectorDB):
    def load_custom_data(self):
        # Load and index custom vulnerability data
        pass
```

### Output Formats
Add new output formats through the printer system:
```python
class CustomFormatter(Formatter):
    def format_results(self, results):
        # Custom formatting logic
        return formatted_output
```

## Security Considerations

### Isolation
- **Container Sandboxing**: All dynamic analysis runs in isolated Docker containers
- **Network Isolation**: Containers have restricted network access
- **Resource Limits**: CPU, memory, and disk usage constraints
- **Temporary Filesystems**: Non-persistent storage for analysis artifacts

### Access Control
- **API Key Management**: Secure storage and rotation of service credentials
- **File System Permissions**: Restricted access to host file system
- **Service Authentication**: Secure communication with external services
- **Audit Logging**: Comprehensive logging of security-relevant events

### Data Protection
- **Sensitive Information**: Automatic detection and redaction of secrets
- **Encryption**: At-rest and in-transit encryption for sensitive data
- **Data Retention**: Configurable retention policies for analysis results
- **Privacy Compliance**: GDPR and other privacy regulation considerations

## Performance Characteristics

### Scalability
- **Horizontal Scaling**: Multiple agent instances can run in parallel
- **Vertical Scaling**: Resource allocation per analysis session
- **Caching**: Vector database and code analysis result caching
- **Streaming**: Real-time result delivery for long-running analyses

### Resource Management
- **Memory Usage**: Configurable memory limits for containers and processes
- **CPU Utilization**: Multi-core processing where applicable
- **Storage**: Efficient cleanup of temporary analysis artifacts
- **Network**: Bandwidth management for external service calls

## Related Topics

- [Installation Guide](../installation.md) - Setup and configuration
- [Configuration Guide](../configuration.md) - Settings and customization
- [Usage Guide](../usage.md) - Operational workflows
- [API Reference](../../api/) - Detailed class documentation

## Next Steps

1. **Installation**: Follow the [Installation Guide](../installation.md) to set up IVEXES
2. **Configuration**: Review [Configuration Guide](../configuration.md) for customization options
3. **Development**: See [Development Guide](../development.md) for extending the system
4. **Examples**: Explore [Examples Guide](../examples.md) for practical use cases