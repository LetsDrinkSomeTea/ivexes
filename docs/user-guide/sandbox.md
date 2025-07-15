# Sandbox Environment

The Sandbox provides a secure, isolated environment for dynamic analysis and testing of potentially malicious code and binaries.

## Overview

The IVEXES Sandbox is designed for safe execution and analysis of untrusted code. It provides:

- **Containerized Isolation**: Docker-based sandboxing for maximum security
- **Dynamic Analysis**: Runtime behavior monitoring and analysis
- **Network Monitoring**: Traffic capture and analysis
- **System Call Tracking**: Detailed execution tracing
- **Resource Management**: CPU, memory, and time constraints

## Architecture

### Container-Based Isolation

The sandbox uses Docker containers to provide:
- Process isolation
- Filesystem separation
- Network segmentation
- Resource limitations

### Monitoring Systems

- **System Call Tracer**: Monitors all system interactions
- **Network Sniffer**: Captures and analyzes network traffic
- **File System Monitor**: Tracks file operations and changes
- **Process Monitor**: Observes process creation and behavior

## Key Features

### Secure Execution
- Isolated container environment
- No access to host system
- Configurable resource limits
- Automatic cleanup after analysis

### Dynamic Analysis
- Runtime behavior capture
- API call monitoring
- Memory usage tracking
- Network activity analysis

### Multi-Format Support
- Executable binaries (ELF, PE, Mach-O)
- Scripts (Python, JavaScript, shell)
- Archives and packed files
- Document formats with macros

## Usage

### Basic Sandbox Execution

```python
from ivexes.sandbox import Sandbox

sandbox = Sandbox()

# Execute binary in sandbox
result = sandbox.execute("/path/to/binary")

# Access analysis results
print("Exit code:", result.exit_code)
print("System calls:", result.system_calls)
print("Network activity:", result.network_traffic)
print("File operations:", result.file_operations)
```

### Advanced Configuration

```python
from ivexes.sandbox import Sandbox, SandboxConfig

config = SandboxConfig(
    # Resource limits
    memory_limit="512MB",
    cpu_limit="2",
    timeout=300,
    
    # Network settings
    network_enabled=True,
    internet_access=False,
    
    # Monitoring options
    capture_network=True,
    trace_syscalls=True,
    monitor_files=True,
    
    # Container settings
    image="ivexes/analysis:latest",
    privileged=False
)

sandbox = Sandbox(config)
```

### Script Analysis

```python
# Analyze potentially malicious script
script_content = """
import os
os.system('rm -rf /')  # Malicious command
"""

result = sandbox.execute_script(
    script_content,
    language="python",
    capture_output=True
)

# Check for dangerous operations
if "rm -rf" in result.executed_commands:
    print("WARNING: Destructive command detected!")
```

## Monitoring and Analysis

### System Call Analysis

```python
# Analyze system call patterns
syscalls = result.system_calls

# Look for suspicious patterns
suspicious_calls = [
    call for call in syscalls 
    if call.name in ['execve', 'socket', 'connect', 'unlink']
]

# Analyze file access patterns
file_accesses = [
    call for call in syscalls 
    if call.name in ['open', 'read', 'write']
]
```

### Network Traffic Analysis

```python
# Examine network behavior
traffic = result.network_traffic

# Check for data exfiltration
for packet in traffic:
    if packet.destination.is_external():
        print(f"External connection: {packet.destination}")
        print(f"Data size: {packet.size}")
```

### Behavioral Patterns

```python
# Analyze behavioral indicators
behavior = sandbox.analyze_behavior(result)

print("Persistence mechanisms:", behavior.persistence)
print("Privilege escalation:", behavior.privilege_escalation)
print("Anti-analysis techniques:", behavior.evasion_techniques)
print("Data collection:", behavior.data_harvesting)
```

## Security Considerations

### Isolation Boundaries

1. **Container Isolation**: Complete process and filesystem separation
2. **Network Segmentation**: Controlled network access
3. **Resource Limits**: Prevent resource exhaustion attacks
4. **Privilege Restrictions**: Non-privileged execution by default

### Data Protection

1. **Temporary Storage**: All sandbox data is ephemeral
2. **Secure Cleanup**: Automatic container destruction
3. **Log Sanitization**: Removal of sensitive information
4. **Access Controls**: Restricted sandbox access

## Configuration Options

### Resource Management

```python
config = SandboxConfig(
    # Memory constraints
    memory_limit="1GB",
    swap_limit="0",
    
    # CPU limitations
    cpu_limit="2.0",
    cpu_quota=100000,
    
    # Time constraints
    timeout=600,
    idle_timeout=60,
    
    # Disk space
    disk_limit="500MB"
)
```

### Network Configuration

```python
config = SandboxConfig(
    # Network access control
    network_enabled=True,
    internet_access=False,
    
    # DNS configuration
    dns_servers=["8.8.8.8", "1.1.1.1"],
    
    # Port restrictions
    allowed_ports=[80, 443, 8080],
    blocked_ports=[22, 23, 3389],
    
    # Traffic capture
    capture_network=True,
    pcap_file="/tmp/traffic.pcap"
)
```

### Monitoring Settings

```python
config = SandboxConfig(
    # System call tracing
    trace_syscalls=True,
    syscall_filter=["open", "write", "connect"],
    
    # File system monitoring
    monitor_files=True,
    watched_directories=["/tmp", "/var"],
    
    # Process monitoring
    monitor_processes=True,
    track_children=True,
    
    # Performance monitoring
    monitor_performance=True,
    sample_interval=1.0
)
```

## Integration with Other Tools

### Code Browser Integration

```python
from ivexes.code_browser import CodeBrowser
from ivexes.sandbox import Sandbox

# Static analysis first
browser = CodeBrowser()
static_analysis = browser.analyze_file("suspicious.c")

# Compile and run in sandbox
sandbox = Sandbox()
binary_result = sandbox.compile_and_execute("suspicious.c")

# Correlate static and dynamic findings
correlation = browser.correlate_analysis(
    static_analysis,
    binary_result
)
```

### Report Generation

```python
from ivexes.report import ReportGenerator

# Generate comprehensive analysis report
report = ReportGenerator()
analysis_report = report.generate_sandbox_report(
    sandbox_result=result,
    include_graphs=True,
    include_recommendations=True
)

# Export to various formats
report.export_pdf("analysis_report.pdf")
report.export_html("analysis_report.html")
```

## Best Practices

### Analysis Workflow

1. **Pre-Analysis**: Static analysis and metadata extraction
2. **Controlled Execution**: Run with appropriate constraints
3. **Monitoring**: Capture all relevant behavioral data
4. **Post-Analysis**: Correlate findings and generate reports
5. **Cleanup**: Ensure complete environment sanitization

### Security Guidelines

1. **Principle of Least Privilege**: Use minimal necessary permissions
2. **Defense in Depth**: Multiple isolation layers
3. **Regular Updates**: Keep sandbox images updated
4. **Monitoring**: Log all sandbox activities
5. **Incident Response**: Procedures for containment breaches

### Performance Optimization

1. **Resource Tuning**: Optimize container resource allocation
2. **Parallel Execution**: Run multiple sandboxes for batch analysis
3. **Caching**: Reuse base images and common dependencies
4. **Cleanup Automation**: Automated resource reclamation

## Troubleshooting

### Common Issues

**Container Startup Failures**
- Check Docker daemon status
- Verify image availability
- Review resource constraints

**Analysis Timeouts**
- Increase timeout limits
- Check for infinite loops
- Monitor resource usage

**Network Issues**
- Verify network configuration
- Check firewall rules
- Review DNS settings

### Debugging Tools

```python
# Enable debug logging
sandbox = Sandbox(debug=True)

# Access detailed logs
logs = sandbox.get_execution_logs()

# Monitor resource usage
stats = sandbox.get_resource_stats()

# Examine container state
container_info = sandbox.get_container_info()
```

## See Also

- [Code Browser Integration](code-browser.md)
- [API Reference](../api/sandbox.md)
- [Configuration Guide](../getting-started/configuration.md)
- [Security Best Practices](../architecture/security.md)