"""Sandbox Tools for Secure Code Execution.

This module provides tool functions for managing and interacting with
sandbox environments. The sandbox provides a secure, isolated environment
for executing potentially malicious code and analyzing vulnerabilities.

All sandbox operations are performed within Docker containers to ensure
proper isolation and security.
"""

from typing import cast

from agents import function_tool, Tool
from .sandbox import Sandbox
from ..config import get_settings
import logging

logger = logging.getLogger(__name__)
_sandbox: Sandbox | None = None


def get_sandbox() -> Sandbox:
    """Get the global sandbox instance, creating it if necessary.

    Creates a sandbox instance using the setup archive specified in settings.
    Implements singleton pattern to ensure only one sandbox exists.

    Returns:
        Sandbox: The sandbox instance.

    Raises:
        SystemExit: If setup_archive is not configured in settings.
    """
    global _sandbox
    if _sandbox is None:
        settings = get_settings()
        _sandbox = Sandbox(settings.setup_archive)
    return _sandbox


@function_tool(strict_mode=True)
def setup_sandbox() -> str:
    """Sets up a Kali Linux sandbox environment.

    Initializes a containerized Kali Linux environment for secure code execution
    and vulnerability analysis. Returns basic environment information upon success.

    Returns:
        str: A message indicating the result of the setup operation and basic
            information about the environment including user, working directory,
            and file listing.
    """
    logger.info('running setup_sandbox()')
    sandbox = get_sandbox()
    if not sandbox.connect():
        return 'Failed to setup sandbox'
    r = (
        'Sandbox setup successfully\n'
        'Username: "user" Password: "passwd"\n'
        'Rootuser: "root Password: "passwd" (Only use for setup purposes)\n'
    )
    r += sandbox.write_to_shell(b'whoami')
    r += sandbox.write_to_shell(b'pwd')
    r += sandbox.write_to_shell(b'ls -la')
    return r


@function_tool(strict_mode=True)
def teardown_sandbox() -> str:
    """Teardown the Kali Linux sandbox environment.

    Properly closes the sandbox connection and cleans up associated resources
    including Docker containers.

    Returns:
        str: A message indicating the result of the teardown operation.
    """
    logger.info('running teardown_sandbox()')
    sandbox = get_sandbox()
    success = False
    if sandbox:
        success = sandbox.close()
    if success:
        sandbox = None
    return 'Sandbox teardown successfully' if success else 'Failed to teardown sandbox'


@function_tool(strict_mode=True)
def sandbox_write_to_shell(input: str) -> str:
    """Interactively writes the input to the shell in the Kali Linux sandbox environment.

    Executes commands in the sandbox shell and returns the output. Useful for
    running analysis tools, scripts, and system commands within the secure environment.

    Args:
        input (str): The input to write to the shell.

    Returns:
        str: The output of the shell command execution.
    """
    logger.info(f'running write_to_shell({input=})')
    sandbox = get_sandbox()
    if not sandbox:
        return 'Sandbox is not set up. Please run setup_sandbox() first.'
    return sandbox.write_to_shell(input.encode())


@function_tool(strict_mode=True)
def sandbox_create_file(file_path: str, content: str) -> str:
    """Create a file (overriding) with the specified content in the sandbox environment.

    Creates or overwrites a file at the specified path with the given content.
    Useful for transferring scripts, configuration files, or analysis data into
    the sandbox.

    Args:
        file_path (str): The path where the file should be created.
        content (str): The content to write into the file.

    Returns:
        str: Confirmation message or error description.
    """
    logger.info(f'running create_file({file_path=}, {content=})')
    sandbox = get_sandbox()
    if not sandbox:
        return 'Sandbox is not set up. Please run setup_sandbox() first.'
    success = sandbox.create_file(file_path, content)
    return (
        f'File {file_path} created successfully.'
        if success
        else f'Failed to create file {file_path}.'
    )


sandbox_tools = cast(
    list[Tool],
    [setup_sandbox, teardown_sandbox, sandbox_write_to_shell, sandbox_create_file],
)
