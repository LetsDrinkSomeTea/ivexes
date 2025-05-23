import time

import paramiko

import config.log
from modules.sandbox.kali import setup_container

logger = config.log.get(__name__)


class Sandbox:
    def __init__(self, executable_archive: str, username: str = "root", password: str = "passwd",
                 host: str = "localhost", port: int = 2222):
        """
        Initialize the SSH client.

        Args:
            host (str): Hostname or IP address.
            port (int): Port number.
            username (str): SSH username.
            password (str): SSH password.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.prompt_string = ""  # saved last prompt string for better formatting

        self.executable_archive = executable_archive

        self.container = None

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.shell = None  # This will hold our interactive shell channel

    def __del__(self):
        """
        Destructor to ensure the SSH connection is closed.
        """
        self.close()

    def connect(self) -> bool:
        """
        Connect to the SSH server.
        """
        try:
            self.container = setup_container(self.executable_archive)
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            logger.debug(f"Connected to {self.host}:{self.port} as {self.username}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def get_shell(self):
        """
        Get an interactive shell channel. Creates one if it does not exist.
        """
        if self.shell is None or self.shell.closed:
            self.shell = self.client.invoke_shell(term="dumb")
            logger.info("Interactive shell started.")
            # Optionally, wait for the shell to be ready
            time.sleep(1)
            # Flush any initial output
            if self.shell.recv_ready():
                initial_output = self.shell.recv(4096).decode('utf-8')
                logger.debug(f"Initial shell output: {initial_output}")
                self.prompt_string = initial_output.splitlines()[-1]
        return self.shell

    def write_to_shell(self, command: bytes, wait: float = 1.0) -> str:
        """
        Send a command to the interactive shell and return the output.

        Args:
            command (str): The command to send.
            wait (float): Seconds to wait for output before reading.

        Returns:
            str: The output received after sending the command.
        """
        shell = self.get_shell()
        logger.debug(f"Sending command: {command}")
        shell.send(command + b"\n")
        # Wait a bit for the command to produce output.
        time.sleep(wait)
        output = ""
        while shell.recv_ready():
            output_chunk = shell.recv(4096).decode('utf-8')
            output += output_chunk
            time.sleep(0.1)  # Slight delay in reading further chunks
        output = self.prompt_string + output
        self.prompt_string = output.splitlines()[-1]
        return "\n".join(output.splitlines()[:-1]).strip()

    def close(self):
        """
        Close the SSH connection.
        """
        if self.shell:
            self.shell.close()
        self.client.close()
        logger.info("SSH connection closed.")
        self.container.stop()
        logger.info("Container stopped and removed.")
        return True
