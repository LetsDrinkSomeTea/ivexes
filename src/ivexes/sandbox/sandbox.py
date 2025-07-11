"""Sandbox module for containerized environment management.

This module provides a Sandbox class that manages containerized environments
for secure code execution and analysis. It uses SSH connections to interact
with Docker containers and provides file operations and shell access.

The sandbox environment is isolated and can be used for:
- Safe code execution
- Vulnerability analysis
- Dynamic testing
- Reverse engineering tasks

Example:
    Basic sandbox usage:

    >>> sandbox = Sandbox(setup_archive='path/to/archive.tar.gz')
    >>> if sandbox.connect():
    ...     result = sandbox.write_to_shell(b'ls -la')
    ...     sandbox.close()
"""

import time

import paramiko

import logging
from .sandbox_container import setup_container

logger = logging.getLogger(__name__)


class Sandbox:
    """Containerized sandbox environment for secure code execution and analysis.

    This class provides a secure, isolated environment for running potentially
    malicious code, analyzing vulnerabilities, and performing dynamic testing.
    It manages Docker containers and provides SSH-based access to the sandbox.

    The sandbox automatically sets up and tears down containers as needed,
    ensuring proper isolation and resource management.

    Attributes:
        host (str): SSH hostname or IP address.
        port (int): SSH port number.
        username (str): SSH username for container access.
        password (str): SSH password for container access.
        setup_archive (str): Path to archive containing sandbox setup files.
        container: Docker container instance.
        client: Paramiko SSH client instance.
        shell: Interactive shell channel.
        prompt_string (str): Last shell prompt for output formatting.

    Example:
        Basic sandbox operations:

        >>> sandbox = Sandbox(setup_archive='malware.tar.gz')
        >>> if sandbox.connect():
        ...     # Execute commands safely
        ...     output = sandbox.write_to_shell(b'./analyze_binary')
        ...     # Create analysis files
        ...     sandbox.create_file('report.txt', 'Analysis results...')
        ...     sandbox.close()
    """

    def __init__(
        self,
        setup_archive: str,
        username: str = 'user',
        password: str = 'passwd',
        host: str = 'localhost',
        port: int = 2222,
    ):
        """Initialize the sandbox environment.

        Args:
            setup_archive (str): Path to the archive file containing setup data
                for the sandbox environment.
            username (str, optional): SSH username for container access.
                Defaults to 'user'.
            password (str, optional): SSH password for container access.
                Defaults to 'passwd'.
            host (str, optional): SSH hostname or IP address.
                Defaults to 'localhost'.
            port (int, optional): SSH port number. Defaults to 2222.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.prompt_string = ''  # saved last prompt string for better formatting

        self.setup_archive = setup_archive

        self.container = None

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.shell = None  # This will hold our interactive shell channel

    def connect(self) -> bool:
        """Connect to the sandbox SSH server and set up the container.

        This method initializes the Docker container using the provided setup
        archive and establishes an SSH connection to the sandbox environment.

        Returns:
            bool: True if connection succeeded, False otherwise.

        Example:
            >>> sandbox = Sandbox(setup_archive='test.tar.gz')
            >>> if sandbox.connect():
            ...     print('Sandbox ready for use')
            ... else:
            ...     print('Failed to connect to sandbox')
        """
        try:
            self.container = setup_container(self.setup_archive)
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
            )
            logger.debug(f'Connected to {self.host}:{self.port} as {self.username}')
            return True
        except Exception as e:
            logger.error(f'Failed to connect: {e}')
            return False

    def get_shell(self):
        """Get an interactive shell channel for command execution.

        Creates a new shell channel if one does not exist or if the existing
        channel is closed. The shell is configured with xterm-mono terminal
        type for better compatibility.

        Returns:
            paramiko.Channel: The interactive shell channel.

        Note:
            This method automatically handles shell initialization and flushes
            any initial output to ensure clean command execution.
        """
        if self.shell is None or self.shell.closed:
            self.shell = self.client.invoke_shell(
                term='xterm-mono'
            )  # try dumb, linux-m
            logger.info('Interactive shell started.')
            # Optionally, wait for the shell to be ready
            time.sleep(1)
            # Flush any initial output
            if self.shell.recv_ready():
                initial_output = self.shell.recv(4096).decode('utf-8')
                logger.debug(f'Initial shell output: {initial_output}')
                self.prompt_string = initial_output.splitlines()[-1]
        return self.shell

    def write_to_shell(self, command: bytes, wait: float = 1.0) -> str:
        """Send a command to the interactive shell and return the output.

        This method sends a command to the sandbox shell, waits for output,
        and returns the formatted response. It handles shell prompt formatting
        and ensures proper command termination.

        Args:
            command (bytes): The command to send to the shell. Must be bytes.
            wait (float, optional): Seconds to wait for output before reading.
                Defaults to 1.0.

        Returns:
            str: The formatted output received after sending the command,
                including the previous prompt string for better formatting.

        Example:
            >>> sandbox = Sandbox(setup_archive='test.tar.gz')
            >>> sandbox.connect()
            >>> output = sandbox.write_to_shell(b'ls -la')
            >>> print(output)
        """
        shell = self.get_shell()
        if not command.endswith(b'\n'):
            command += b'\n'  # Ensure command ends with newline
        logger.debug(f'Sending command: {command}')
        shell.send(command)
        # Wait a bit for the command to produce output.
        time.sleep(wait)
        output = ''
        while shell.recv_ready():
            output_chunk = shell.recv(4096).decode('utf-8')
            output += output_chunk
            time.sleep(wait)  # Slight delay in reading further chunks
        output = output.strip()
        # Formatting the output to use the latest prompt_string as prefix
        new_prompt = output.splitlines()[-1]
        stripped_output = ''.join(output.splitlines(keepends=True)[:-1])
        ret = self.prompt_string + stripped_output
        self.prompt_string = new_prompt
        return ret

    def create_file(self, filename: str, content: str) -> bool:
        """Create a file in the sandbox with the given content.

        This method uses SFTP to create a file within the sandbox environment.
        It's useful for transferring analysis scripts, configuration files,
        or any other data needed for sandbox operations.

        Args:
            filename (str): The name/path of the file to create within the sandbox.
            content (str): The content to write to the file.

        Returns:
            bool: True if the file was created successfully, False otherwise.

        Example:
            >>> sandbox = Sandbox(setup_archive='test.tar.gz')
            >>> sandbox.connect()
            >>> success = sandbox.create_file('script.py', "print('Hello')")
            >>> if success:
            ...     print('File created successfully')
        """
        sftp_client = self.client.open_sftp()
        success = True
        try:
            with sftp_client.file(filename=filename, mode='w') as f:
                f.write(content)
        except IOError as e:
            logger.error(f'Failed to create file {filename}: {e}')
            success = False
        sftp_client.close()
        return success

    def close(self):
        """Close the SSH connection and clean up resources.

        This method properly terminates the SSH connection, closes any open
        shell channels, and stops the associated Docker container. It ensures
        proper cleanup of all resources used by the sandbox.

        Returns:
            bool: True indicating successful cleanup.

        Example:
            >>> sandbox = Sandbox(setup_archive='test.tar.gz')
            >>> sandbox.connect()
            >>> # ... use sandbox ...
            >>> sandbox.close()  # Always cleanup when done
        """
        if self.shell:
            self.shell.close()
        self.client.close()
        logger.debug('SSH connection closed.')
        if self.container:
            self.container.stop()
        logger.debug('Container stopped.')
        logger.info('Sandbox closed.')
        return True
