"""Sandbox Tools for Secure Code Execution.

This module provides tool functions for managing and interacting with
sandbox environments. The sandbox provides a secure, isolated environment
for executing potentially malicious code and analyzing vulnerabilities.

All sandbox operations are performed within Docker containers to ensure
proper isolation and security.
"""

from typing import Literal, Optional, cast

from agents import function_tool, Tool
from .sandbox import Sandbox
from ..config.settings import Settings
import logging

logger = logging.getLogger(__name__)


def create_sandbox_tools(
    settings: Settings, sandbox: Optional[Sandbox] = None
) -> list[Tool]:
    """Create sandbox tools with dependency injection.

    Args:
        settings: Settings instance from the creating agent.
        sandbox: Optional sandbox instance. If not provided, creates new one from settings.

    Returns:
        List of sandbox tools configured with the provided sandbox instance.
    """
    if sandbox is None:
        sandbox = Sandbox(settings)

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
        if not sandbox.connect(reset=True):
            return 'Failed to setup sandbox'
        r = (
            'Sandbox setup successfully\n'
            'Username: "user" Password: "passwd"\n'
            'Rootuser: "root Password: "passwd" (Only use for setup purposes)\n'
        )
        r += sandbox.run('whoami')[1]
        r += sandbox.run('pwd')[1]
        r += sandbox.run('ls -la')[1]
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
        success = False
        success = sandbox.close()
        return (
            'Sandbox teardown successfully' if success else 'Failed to teardown sandbox'
        )

    @function_tool(strict_mode=True)
    def sandbox_run(
        input: str,
        user: Literal['root', 'user'] = 'user',
        session: Optional[str] = None,
        timeout: int = 60,
    ) -> str:
        r"""Interactively writes the input to the shell in the Kali Linux sandbox environment.

        Executes commands in the sandbox shell and returns the output. Useful for
        running analysis tools, scripts, and system commands within the secure environment.

        Args:
            input (str): The input to write to the shell.
            user (Literal['root', 'user']): The user context to run the command as.
            session (Optional[str]): Optional session identifier for interactive commands.
            timeout (int): Timeout for the command execution in seconds. Defaults to 60.

        Returns:
            str: The output of the shell command execution.

        Example:
            >>> sandbox_run('ls -la')
            'total 0
            drwxr-xr-x 1 user user 0 Oct 10 12:00 .
            drwxr-xr-x 1 user user 0 Oct 10 12:00 ..'

            >>> sandbox_run('python3', session='python')
            'Python 3.13.5 (main, Jun 21 2025, 09:35:00) [GCC 15.1.1 20250425] on linux
            Type "help", "copyright", "credits" or "license" for more information.'

            >>> sandbox_run('print("Hello, World!")', session='python')
            'Hello, World!'

        """
        logger.info(f'running run({input=}, {session=})')
        if session:
            s = sandbox.interactive(session=session, timeout=timeout)
            s.send(input)
            return s.read()[1]
        return sandbox.run(input.encode(), user=user, timeout=timeout)[1]

    @function_tool(strict_mode=True)
    def sandbox_write_file(file_path: str, content: str) -> str:
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
        success = sandbox.write_file(file_path, content)
        return (
            f'File {file_path} created successfully.'
            if success
            else f'Failed to create file {file_path}.'
        )

    return cast(
        list[Tool],
        [setup_sandbox, teardown_sandbox, sandbox_run, sandbox_write_file],
    )
