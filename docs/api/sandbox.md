# Sandbox API Reference

## Overview

The Sandbox module provides secure containerized environments for executing potentially malicious code and performing dynamic analysis. It manages Docker containers with isolation, resource management, and interactive session support for tools like GDB, shell commands, and custom analysis scripts.

## Core Classes

### Sandbox

Main containerized sandbox environment for secure code execution.

```python
from ivexes.sandbox import Sandbox
from ivexes.config import PartialSettings

settings = PartialSettings(
    sandbox_image='kali-ssh:latest',
    setup_archive='/path/to/analysis.tgz'
)
sandbox = Sandbox(settings)
```

#### Constructor

```python
def __init__(
    self,
    settings: Settings,
    username: Literal['user', 'root'] = 'user',
    working_dir: str = '/home/user'
) -> None
```

**Parameters:**
- `settings` (Settings): Configuration settings containing Docker image, setup archive, and other options
- `username` (Literal['user', 'root']): Default username for container operations
- `working_dir` (str): Default working directory inside container

**Example:**
```python
from ivexes.config import PartialSettings

settings = PartialSettings(
    sandbox_image='kali-ssh:latest',
    setup_archive='/path/to/setup.tgz',
    trace_name='vulnerability_analysis'
)

sandbox = Sandbox(
    settings=settings,
    username='user',
    working_dir='/home/user'
)
```

#### Methods

##### connect()

Set up and connect to the Docker container.

```python
def connect(self, reset: bool = True) -> bool
```

**Parameters:**
- `reset` (bool): Whether to remove and recreate existing container

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
# Connect with container reset
if sandbox.connect(reset=True):
    print("Sandbox connected successfully")
else:
    print("Failed to connect to sandbox")

# Reuse existing container if available
if sandbox.connect(reset=False):
    print("Connected to existing container")
```

##### run()

Execute a command in the container with timeout support.

```python
def run(
    self,
    command: Union[str, bytes],
    user: Optional[str] = None,
    timeout: int = 60
) -> Tuple[int, str]
```

**Parameters:**
- `command` (Union[str, bytes]): Command to execute
- `user` (Optional[str]): User to run as (defaults to sandbox username)
- `timeout` (int): Timeout in seconds

**Returns:**
- `Tuple[int, str]`: Exit code and output
  - Exit code: 0 (success), 1 (error), 2 (timeout with partial results)
  - Output: Command output or error message

**Example:**
```python
# Basic command execution
exit_code, output = sandbox.run('ls -la')
if exit_code == 0:
    print(f"Directory listing:\n{output}")

# Run with specific user and timeout
exit_code, output = sandbox.run(
    'find / -name "*.so" | head -10',
    user='root',
    timeout=30
)

# Handle different exit codes
if exit_code == 0:
    print("Command completed successfully")
elif exit_code == 2:
    print("Command timed out, partial results available")
else:
    print(f"Command failed: {output}")
```

##### interactive()

Start an interactive session for tools like GDB or Python REPL.

```python
def interactive(
    self,
    command: str = '/bin/sh',
    user: Literal['user', 'root'] = 'root',
    session: Optional[str] = None,
    timeout: int = 60
) -> InteractiveSession
```

**Parameters:**
- `command` (str): Command to run interactively
- `user` (Literal['user', 'root']): User to run the session as
- `session` (Optional[str]): Session identifier for reuse
- `timeout` (int): Default timeout for session operations

**Returns:**
- `InteractiveSession`: Session object for interaction

**Example:**
```python
# Start GDB session
gdb_session = sandbox.interactive(
    command='gdb ./vulnerable_program',
    user='user',
    session='gdb_analysis',
    timeout=120
)

# Send commands to GDB
gdb_session.send('break main')
status, output = gdb_session.read()
print(f"GDB output: {output}")

gdb_session.send('run')
gdb_session.send('bt')

# Reuse existing session
same_session = sandbox.interactive(session='gdb_analysis')
```

##### write_file()

Create or overwrite a file in the container.

```python
def write_file(self, filename: str, content: str) -> bool
```

**Parameters:**
- `filename` (str): File path in container (absolute or relative)
- `content` (str): File content

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
# Write analysis script
script_content = """#!/bin/bash
echo "Starting vulnerability analysis..."
file /usr/bin/target
strings /usr/bin/target | grep -i password
"""

success = sandbox.write_file('/tmp/analysis.sh', script_content)
if success:
    sandbox.run('chmod +x /tmp/analysis.sh')
    exit_code, output = sandbox.run('/tmp/analysis.sh')

# Write Python analysis script
python_script = """
import os
import sys

def analyze_binary(path):
    if os.path.exists(path):
        print(f"Analyzing {path}")
        return True
    return False

if __name__ == "__main__":
    analyze_binary("/usr/bin/target")
"""

sandbox.write_file('analyze.py', python_script)
```

##### read_file()

Read a file from the container.

```python
def read_file(self, filename: str) -> Optional[str]
```

**Parameters:**
- `filename` (str): File path in container

**Returns:**
- `Optional[str]`: File content or None if failed

**Example:**
```python
# Read configuration file
config_content = sandbox.read_file('/etc/passwd')
if config_content:
    print("User accounts:")
    for line in config_content.split('\n'):
        if 'user' in line:
            print(line)

# Read analysis results
results = sandbox.read_file('/tmp/analysis_results.txt')
if results:
    print(f"Analysis completed:\n{results}")
else:
    print("No results file found")
```

##### is_running()

Check if the container is running.

```python
def is_running(self) -> bool
```

**Returns:**
- `bool`: True if container is running, False otherwise

**Example:**
```python
if sandbox.is_running():
    print("Container is active")
    exit_code, output = sandbox.run('uptime')
else:
    print("Container is not running, reconnecting...")
    sandbox.connect()
```

##### close()

Close sandbox and cleanup resources.

```python
def close(self) -> bool
```

**Returns:**
- `bool`: True if cleanup successful

**Example:**
```python
# Manual cleanup
success = sandbox.close()
if success:
    print("Sandbox closed successfully")

# Automatic cleanup with context manager
with Sandbox(settings) as sandbox:
    sandbox.run('echo "Analysis complete"')
# Automatic cleanup happens here
```

#### Context Manager Support

The Sandbox class supports context manager protocol for automatic resource management.

```python
# Automatic setup and cleanup
with Sandbox(settings) as sandbox:
    # Container is automatically connected
    exit_code, output = sandbox.run('whoami')
    print(f"Running as: {output}")
    
    # Interactive analysis
    gdb = sandbox.interactive('gdb /usr/bin/target')
    gdb.send('info functions')
    status, functions = gdb.read()
    
# Container is automatically cleaned up
```

#### Properties

- `settings` (Settings): Configuration settings
- `username` (str): Default username for operations
- `working_dir` (str): Default working directory
- `container` (Optional[Container]): Docker container instance
- `sessions` (dict): Active interactive sessions

### InteractiveSession

Manages interactive programs running in Docker containers using pexpect.

```python
# Created through Sandbox.interactive()
session = sandbox.interactive('gdb ./program')
```

#### Constructor

```python
def __init__(
    self,
    container: Container,
    command: str,
    working_dir: str,
    user: Literal['root', 'user'],
    timeout: int = 30
) -> None
```

**Parameters:**
- `container` (Container): Docker container instance
- `command` (str): Command to run interactively
- `working_dir` (str): Working directory for the command
- `user` (Literal['root', 'user']): User to run as
- `timeout` (int): Default timeout for operations

#### Methods

##### send()

Send text input to the interactive session.

```python
def send(self, text: Union[str, bytes]) -> None
```

**Parameters:**
- `text` (Union[str, bytes]): Text to send to the session

**Example:**
```python
# GDB interaction
gdb = sandbox.interactive('gdb ./vulnerable')
gdb.send('break main')
gdb.send('run AAAA')
gdb.send('continue')

# Python REPL interaction
python = sandbox.interactive('python3')
python.send('import os')
python.send('print(os.getcwd())')
python.send('exit()')
```

##### read()

Read available output without blocking.

```python
def read(self) -> Tuple[STATUS, str]
```

**Returns:**
- `Tuple[STATUS, str]`: Status and output text
  - STATUS.ALIVE: Session is active with output
  - STATUS.EMPTY: No output available
  - STATUS.EOF: End of file reached
  - STATUS.TIMEOUT: Read operation timed out

**Example:**
```python
session = sandbox.interactive('gdb ./program')
session.send('info registers')

status, output = session.read()
if status == InteractiveSession.STATUS.ALIVE:
    print(f"Registers:\n{output}")
elif status == InteractiveSession.STATUS.EMPTY:
    print("No output available yet")
elif status == InteractiveSession.STATUS.EOF:
    print("Session ended")
```

##### is_alive()

Check if the session process is still running.

```python
def is_alive(self) -> bool
```

**Returns:**
- `bool`: True if session is active

**Example:**
```python
session = sandbox.interactive('long_running_analysis')
session.send('start')

while session.is_alive():
    status, output = session.read()
    if output and output != "Nothing to read":
        print(f"Analysis output: {output}")
    time.sleep(1)
```

##### close()

Close the interactive session.

```python
def close(self) -> None
```

**Example:**
```python
session = sandbox.interactive('gdb ./program')
# Perform analysis
session.send('quit')
session.close()

# Or use context manager
with sandbox.interactive('python3') as python_session:
    python_session.send('print("Hello from sandbox")')
    status, output = python_session.read()
# Automatic cleanup
```

#### Status Enumeration

```python
class STATUS(Enum):
    ALIVE = 1    # Session is active
    CLOSED = 2   # Session is closed
    TIMEOUT = 3  # Operation timed out
    EMPTY = 4    # No data available
    EOF = 4      # End of file reached
    ERROR = 5    # Error occurred
```

## Container Management

### setup_container()

Create and configure a Docker container for sandbox use.

```python
from ivexes.sandbox.sandbox_container import setup_container

def setup_container(
    settings: Settings,
    docker_image: Optional[str] = None,
    renew: bool = True
) -> Container
```

**Parameters:**
- `settings` (Settings): Configuration settings
- `docker_image` (Optional[str]): Docker image to use (defaults to settings.sandbox_image)
- `renew` (bool): Whether to remove existing container

**Returns:**
- `Container`: Docker container ready for use

**Raises:**
- `ValueError`: If setup_archive is not .tar/.tgz format
- `RuntimeError`: If container setup fails
- `docker.errors.ImageNotFound`: If Docker image not found

**Example:**
```python
from ivexes.config import PartialSettings
from ivexes.sandbox.sandbox_container import setup_container

settings = PartialSettings(
    sandbox_image='kali-ssh:latest',
    setup_archive='/path/to/analysis_environment.tgz',
    trace_name='custom_analysis'
)

# Create new container
container = setup_container(settings, renew=True)
print(f"Container {container.name} is ready")

# Reuse existing container if available
container = setup_container(settings, renew=False)
```

## Tool Functions

### create_sandbox_tools()

Create sandbox tools for agent integration.

```python
from ivexes.sandbox.tools import create_sandbox_tools

def create_sandbox_tools(
    settings: Optional[Settings] = None,
    sandbox: Optional[Sandbox] = None
) -> List[Tool]
```

**Parameters:**
- `settings` (Optional[Settings]): Settings instance (loads from environment if not provided)
- `sandbox` (Optional[Sandbox]): Sandbox instance (creates new if not provided)

**Returns:**
- `List[Tool]`: List of sandbox tools for agent use

**Available Tools:**
- `setup_sandbox()`: Initialize sandbox environment
- `teardown_sandbox()`: Clean up sandbox resources
- `sandbox_run()`: Execute commands in sandbox
- `sandbox_write_file()`: Create files in sandbox

**Example:**
```python
from ivexes.agents import SingleAgent
from ivexes.sandbox.tools import create_sandbox_tools
from ivexes.config import PartialSettings

settings = PartialSettings(
    sandbox_image='kali-ssh:latest',
    setup_archive='/path/to/tools.tgz'
)

# Create tools for agent
tools = create_sandbox_tools(settings)

# Use with agent
agent = SingleAgent(bin_path='/usr/bin/target', settings=settings)
# Tools are automatically available to the agent
```

#### Tool: setup_sandbox()

Initialize Kali Linux sandbox environment.

**Returns:**
- `str`: Setup result message with environment information

**Example usage in agent:**
```python
# Agent can call this tool
result = setup_sandbox()
# Returns: "Sandbox setup successfully\nUsername: 'user' Password: 'passwd'..."
```

#### Tool: teardown_sandbox()

Clean up sandbox environment and resources.

**Returns:**
- `str`: Teardown result message

#### Tool: sandbox_run()

Execute commands in the sandbox environment.

**Parameters:**
- `input` (str): Command to execute
- `user` (Literal['root', 'user']): User context (default: 'user')
- `session` (Optional[str]): Session identifier for interactive commands
- `timeout` (int): Command timeout in seconds (default: 60)

**Returns:**
- `str`: Command output

**Example usage in agent:**
```python
# Basic command
output = sandbox_run('ls -la /usr/bin')

# Interactive session
python_output = sandbox_run('print("Hello")', session='python')

# Root access for system commands
system_info = sandbox_run('ps aux', user='root')
```

#### Tool: sandbox_write_file()

Create files in the sandbox environment.

**Parameters:**
- `file_path` (str): Target file path in container
- `content` (str): File content

**Returns:**
- `str`: Success or error message

**Example usage in agent:**
```python
# Create analysis script
result = sandbox_write_file(
    '/tmp/exploit.py',
    'print("Exploit code here")'
)
```

## Usage Examples

### Basic Sandbox Usage

```python
"""Basic sandbox operation example."""

from ivexes.sandbox import Sandbox
from ivexes.config import PartialSettings

# Configure sandbox
settings = PartialSettings(
    sandbox_image='kali-ssh:latest',
    setup_archive='/path/to/analysis_tools.tgz',
    trace_name='basic_analysis'
)

# Create and connect to sandbox
sandbox = Sandbox(settings)

try:
    # Connect to container
    if not sandbox.connect():
        raise RuntimeError("Failed to connect to sandbox")
    
    # Basic command execution
    exit_code, output = sandbox.run('whoami')
    print(f"Running as: {output}")
    
    # File system analysis
    exit_code, output = sandbox.run('find /usr/bin -name "*ssh*"')
    print(f"SSH binaries: {output}")
    
    # Create analysis script
    script = """#!/bin/bash
    echo "=== System Information ==="
    uname -a
    echo "=== Network Interfaces ==="
    ip addr show
    """
    
    if sandbox.write_file('/tmp/sysinfo.sh', script):
        sandbox.run('chmod +x /tmp/sysinfo.sh')
        exit_code, output = sandbox.run('/tmp/sysinfo.sh')
        print(f"System info:\n{output}")

finally:
    sandbox.close()
```

### Interactive Analysis Session

```python
"""Interactive GDB analysis example."""

from ivexes.sandbox import Sandbox
from ivexes.config import PartialSettings

settings = PartialSettings(
    sandbox_image='kali-ssh:latest',
    setup_archive='/path/to/vulnerable_binary.tgz'
)

with Sandbox(settings) as sandbox:
    # Start GDB session
    gdb = sandbox.interactive(
        command='gdb /usr/bin/vulnerable_program',
        session='analysis',
        timeout=120
    )
    
    # Set up analysis
    gdb.send('set disassembly-flavor intel')
    gdb.send('break main')
    
    # Run with test input
    gdb.send('run AAAABBBBCCCCDDDD')
    status, output = gdb.read()
    print(f"Execution stopped: {output}")
    
    # Examine registers
    gdb.send('info registers')
    status, output = gdb.read()
    print(f"Registers: {output}")
    
    # Check stack
    gdb.send('x/20x $rsp')
    status, output = gdb.read()
    print(f"Stack contents: {output}")
    
    # Backtrace
    gdb.send('bt')
    status, output = gdb.read()
    print(f"Backtrace: {output}")
    
    gdb.close()
```

### Multi-Tool Analysis

```python
"""Comprehensive binary analysis using multiple tools."""

from ivexes.sandbox import Sandbox
from ivexes.config import PartialSettings

settings = PartialSettings(
    sandbox_image='kali-ssh:latest',
    setup_archive='/path/to/analysis_suite.tgz'
)

with Sandbox(settings) as sandbox:
    binary_path = '/usr/bin/target'
    
    # File type analysis
    exit_code, output = sandbox.run(f'file {binary_path}')
    print(f"File type: {output}")
    
    # String analysis
    exit_code, output = sandbox.run(f'strings {binary_path} | head -20')
    print(f"Interesting strings: {output}")
    
    # Security features check
    exit_code, output = sandbox.run(f'checksec --file={binary_path}')
    print(f"Security features: {output}")
    
    # Library dependencies
    exit_code, output = sandbox.run(f'ldd {binary_path}')
    print(f"Dependencies: {output}")
    
    # Disassembly sample
    exit_code, output = sandbox.run(f'objdump -d {binary_path} | head -50')
    print(f"Disassembly sample: {output}")
    
    # Dynamic analysis with ltrace
    exit_code, output = sandbox.run(
        f'timeout 10 ltrace -c {binary_path} 2>&1 || true',
        timeout=15
    )
    print(f"Library calls: {output}")
```

### Error Handling and Recovery

```python
"""Robust sandbox usage with error handling."""

from ivexes.sandbox import Sandbox
from ivexes.config import PartialSettings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = PartialSettings(
    sandbox_image='kali-ssh:latest',
    setup_archive='/path/to/tools.tgz'
)

sandbox = Sandbox(settings)

try:
    # Attempt connection with retry
    for attempt in range(3):
        if sandbox.connect(reset=attempt > 0):
            logger.info(f"Connected on attempt {attempt + 1}")
            break
        logger.warning(f"Connection attempt {attempt + 1} failed")
    else:
        raise RuntimeError("Failed to connect after 3 attempts")
    
    # Check container health
    if not sandbox.is_running():
        raise RuntimeError("Container is not running")
    
    # Execute commands with timeout handling
    commands = [
        'echo "Starting analysis"',
        'find /usr -name "*.so" | wc -l',  # Potentially long command
        'ps aux | head -10'
    ]
    
    for cmd in commands:
        try:
            exit_code, output = sandbox.run(cmd, timeout=30)
            
            if exit_code == 0:
                logger.info(f"Command succeeded: {cmd}")
                print(output)
            elif exit_code == 2:
                logger.warning(f"Command timed out: {cmd}")
                print(f"Partial output: {output}")
            else:
                logger.error(f"Command failed: {cmd}")
                print(f"Error: {output}")
                
        except Exception as e:
            logger.error(f"Exception running command '{cmd}': {e}")
            continue

except Exception as e:
    logger.error(f"Sandbox error: {e}")
    
finally:
    # Ensure cleanup
    try:
        sandbox.close()
        logger.info("Sandbox closed successfully")
    except Exception as e:
        logger.error(f"Error closing sandbox: {e}")
```

## Security Considerations

### Container Isolation

- Containers run with limited privileges by default
- File system isolation prevents access to host files
- Network isolation can be configured per container
- Resource limits prevent resource exhaustion attacks

### User Management

- Default 'user' account with limited privileges
- 'root' access available for setup operations only
- Password authentication configured for container access
- SSH access through secure container networking

### Resource Management

- Command timeouts prevent hanging processes
- Memory and CPU limits configurable
- Automatic cleanup of containers and sessions
- Proper handling of file descriptors and streams

### Best Practices

1. **Always use timeouts** for command execution
2. **Clean up resources** with context managers or explicit close()
3. **Validate input** before passing to sandbox commands
4. **Monitor container health** during long operations
5. **Use minimal privileges** - avoid root unless necessary
6. **Isolate sensitive data** - don't mount host directories unnecessarily

## See Also

- [Configuration API](config.md) - Settings and configuration management
- [Container Utilities](tools.md) - Docker utilities and helpers
- [Examples Guide](../documentation/examples.md) - Practical usage examples
- [Development Guide](../documentation/development.md) - Custom sandbox development