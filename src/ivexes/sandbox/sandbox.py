"""Simplified sandbox module for containerized environment management.

This module provides a simplified Sandbox class that manages containerized
environments for secure code execution with interactive session support.
"""

import io
import os
import tarfile
import threading
from enum import Enum
import time
from typing import Optional, Tuple, Union

import docker
from docker.models.containers import Container
import pexpect

import logging
from .sandbox_container import setup_container

logger = logging.getLogger(__name__)

DELAY = 0.2  # Delay for reading output in interactive sessions


class Sandbox:
    """Simplified containerized sandbox for secure code execution.

    Provides basic container management with interactive session support
    for tools like GDB, Python REPL, and shell commands.

    Example:
        >>> sandbox = Sandbox(setup_archive='debug.tar.gz')
        >>> sandbox.connect()
        >>> # Simple command
        >>> exit_code, output = sandbox.run('ls -la')
        >>> # Interactive session
        >>> gdb = sandbox.interactive('gdb ./program')
        >>> gdb.send('break main')
        >>> gdb.expect('(gdb)')
        >>> sandbox.close()
    """

    def __init__(
        self,
        setup_archive: Optional[str] = None,
        username: str = 'root',
        working_dir: str = '/root',
    ):
        """Initialize the sandbox.

        Args:
            setup_archive: Path to setup archive file
            username: Username for container operations
            working_dir: Working directory inside container
            port: Port for container setup
        """
        self.username = username
        self.working_dir = working_dir
        self.setup_archive = setup_archive
        self.sessions: dict[str, InteractiveSession] = {}

        self.container: Optional[Container] = None
        self.docker_client: Optional[docker.DockerClient] = None

    def connect(self) -> bool:
        """Set up and connect to the container.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.docker_client:
                self.docker_client = docker.from_env()
            self.container = setup_container(setup_archive=self.setup_archive)
            logger.debug(f'Container {self.container.name} ready')
            return True
        except Exception as e:
            logger.error(f'Failed to setup container: {e}')
            return False

    def run(
        self, command: Union[str, bytes], user: Optional[str] = None, timeout: int = 60
    ) -> Tuple[int, str]:
        """Execute a command in the container with 10s timeout and partial results.

        Args:
            command: Command to execute
            user: User to run as (defaults to self.username)
            timeout: Timeout in seconds (default 60)

        Returns:
            Tuple of (exit_code, output)
            - exit_code: 0 for success, 2 for timeout with partial results, 1 for error
            - output: Full output or partial output with timeout indicator
        """
        if not self.container:
            raise RuntimeError('Container not connected. Call connect() first.')

        if user is None:
            user = self.username

        if isinstance(command, bytes):
            command = command.decode('utf-8')

        # Shared buffer for collecting results as they come in
        result_buffer = {'data': b'', 'finished': False, 'error': None, 'stream': None}

        def read_stream():
            """Your original logic with shared buffer updates."""
            try:
                _, result_stream = self.container.exec_run(
                    cmd=['sh', '-c', command],
                    workdir=self.working_dir,
                    user=user,
                    stream=True,
                )

                # Store stream reference for cleanup
                result_buffer['stream'] = result_stream

                # Read events and update buffer in real-time
                try:
                    for event in result_stream:
                        result_buffer['data'] += event
                finally:
                    result_stream.close()
                    result_buffer['stream'] = None

                result_buffer['finished'] = True

            except Exception as e:
                result_buffer['error'] = e
            finally:
                # Ensure stream is closed even on exception
                if result_buffer['stream'] is not None:
                    try:
                        result_buffer['stream'].close()
                    except Exception as cleanup_error:
                        logger.debug(
                            f'Error closing stream on exception: {cleanup_error}'
                        )

        try:
            # Start reading in background thread
            thread = threading.Thread(target=read_stream)
            thread.daemon = True
            thread.start()

            # Wait for completion or timeout (10 seconds)
            thread.join(timeout=timeout)

            if thread.is_alive():
                # Timeout occurred - cleanup stream and return partial results
                if result_buffer['stream'] is not None:
                    try:
                        result_buffer['stream'].close()
                    except Exception as e:
                        logger.debug(f'Error closing stream on timeout: {e}')
                    result_buffer['stream'] = None

                partial_output = result_buffer['data'].decode('utf-8', errors='replace')
                timeout_msg = (
                    f'\n[TIMEOUT after {timeout}s - partial results shown above]'
                )
                logger.warning(f'Command timed out after {timeout} seconds: {command}')
                return 2, partial_output + timeout_msg

            # Check for errors
            if result_buffer['error']:
                raise result_buffer['error']

            # Command completed successfully
            output = result_buffer['data'].decode('utf-8', errors='replace')
            return 0, output

        except Exception as e:
            logger.error(f'Failed to execute command: {e}')
            return 1, f'Error: {e}'
        finally:
            # Ensure stream is always closed
            if result_buffer['stream'] is not None:
                try:
                    result_buffer['stream'].close()
                except Exception as e:
                    logger.debug(f'Error closing stream in cleanup: {e}')

    def interactive(
        self,
        command: str = '/bin/sh',
        user: str = 'root',
        session: Optional[str] = None,
        timeout: int = 60,
    ) -> 'InteractiveSession':
        """Start an interactive session.

        Args:
            command: Command to run interactively
            user: User to run the session
            session: Optional session identifier
            timeout: Timeout for session operations

        Returns:
            InteractiveSession object
        """
        if not self.container:
            raise RuntimeError('Container not connected. Call connect() first.')

        if session in self.sessions:
            logger.debug(f'Reusing existing session: {session}')
            return self.sessions[session]

        if not user:
            user = self.username

        s = InteractiveSession(
            container=self.container,
            command=command,
            working_dir=self.working_dir,
            user=user,
            timeout=timeout,
        )

        if session:
            self.sessions[session] = s

        return s

    def write_file(self, filename: str, content: str) -> bool:
        """Create a file in the container.

        Args:
            filename: File path in container
            content: File content

        Returns:
            bool: True if successful
        """
        if not self.container:
            return False

        try:
            # Handle absolute vs relative paths
            if filename.startswith('/'):
                # Absolute path - split into directory and filename
                file_name = os.path.basename(filename)
                target_path = os.path.dirname(filename)
            else:
                # Relative path - use working directory
                file_name = filename
                target_path = self.working_dir

            # Ensure target directory exists
            if target_path != '/':
                self.container.exec_run(f'mkdir -p {target_path}', user=self.username)

            # Create tar archive with just the filename (not full path)
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                tarinfo = tarfile.TarInfo(name=file_name)
                tarinfo.size = len(content.encode('utf-8'))
                tarinfo.mode = 0o644
                tar.addfile(tarinfo, io.BytesIO(content.encode('utf-8')))

            tar_stream.seek(0)

            # Put archive in the target directory
            self.container.put_archive(path=target_path, data=tar_stream.getvalue())

            logger.debug(f'File {filename} written successfully')
            return True

        except Exception as e:
            logger.error(f'Failed to write file {filename}: {e}')
            return False

    def read_file(self, filename: str) -> Optional[str]:
        """Read a file from the container.

        Args:
            filename: File path in container

        Returns:
            File content or None if failed
        """
        if not self.container:
            return None

        try:
            archive_data, _ = self.container.get_archive(filename)
            archive_bytes = b''.join(archive_data)
            with io.BytesIO(archive_bytes) as tar_stream:
                with tarfile.open(fileobj=tar_stream, mode='r') as tar:
                    for member in tar.getmembers():
                        if member.isfile():
                            try:
                                with tar.extractfile(member) as extracted_file:
                                    if extracted_file:
                                        return extracted_file.read().decode('utf-8')
                            except Exception as e:
                                logger.error(f'Error reading file {filename}: {e}')
            return None

        except Exception as e:
            logger.error(f'Failed to read file {filename}: {e}')
            return None

    def is_running(self) -> bool:
        """Check if container is running."""
        if not self.container:
            return False
        try:
            self.container.reload()
            return self.container.status == 'running'
        except Exception:
            return False

    def close(self):
        """Close sandbox and cleanup resources."""
        for s in self.sessions.values():
            s.close()
        self.sessions.clear()

        try:
            if self.container:
                self.container.stop()
                self.container = None
            if self.docker_client:
                self.docker_client.close()
                self.docker_client = None
            logger.info('Sandbox closed')
        except Exception as e:
            logger.error(f'Error closing sandbox: {e}')

    def __enter__(self):
        """Context manager entry."""
        if not self.connect():
            raise RuntimeError('Failed to connect to sandbox')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class InteractiveSession:
    """Simplified interactive session handler.

    Manages interactive programs running in Docker containers using pexpect.
    """

    class STATUS(Enum):
        """Session status enumeration for pexpect session states."""

        ALIVE = 1
        CLOSED = 2
        TIMEOUT = 3
        EMPTY = 4
        EOF = 4
        ERROR = 5

    def __init__(
        self,
        container: Container,
        command: str,
        working_dir: str,
        user: str,
        timeout: int = 30,
    ):
        """Initialize interactive session.

        Args:
            container: Docker container
            command: Command to run
            working_dir: Working directory
            user: User to run as
            timeout: Default timeout for operations
        """
        self.container = container
        self.timeout = timeout

        # Build docker exec command
        docker_cmd = [
            'docker',
            'exec',
            '-it',
            '-w',
            working_dir,
            '-u',
            user,
            container.name,
            'sh',
            '-c',
            command,
        ]

        try:
            self.process = pexpect.spawn(' '.join(docker_cmd), timeout=timeout)
            time.sleep(DELAY)  # Allow some time for the process to start
            self.process.encoding = 'utf-8'
            logger.debug(f'Started interactive session: {command}')
        except Exception as e:
            logger.error(f'Failed to start session: {e}')
            raise

    def send(self, text: Union[str, bytes]):
        """Send text to the session."""
        if isinstance(text, str):
            text = text.encode('utf-8')

        text = text.strip(b'\n')
        self.process.send(text)
        self.read()
        self.process.send(b'\n')

    def read(self) -> tuple[STATUS, str]:
        """Read any available output without blocking."""
        try:
            time.sleep(DELAY)  # Allow some time for output to be available
            val = self.process.read_nonblocking(size=10000, timeout=1)
            val = (
                val.decode('utf-8').replace('\r\n', '\n')
                if isinstance(val, bytes)
                else val
            )
            return self.STATUS.ALIVE, val.strip('\n')
        except pexpect.TIMEOUT:
            return self.STATUS.EMPTY, 'Nothing to read'
        except pexpect.EOF:
            return self.STATUS.EOF, 'End-of-file reached'

    def is_alive(self) -> bool:
        """Check if session is alive."""
        return self.process.isalive()

    def close(self):
        """Close the session."""
        try:
            if self.process.isalive():
                self.process.close()
            logger.debug('Interactive session closed')
        except Exception as e:
            logger.error(f'Error closing session: {e}')

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close session."""
        self.close()
