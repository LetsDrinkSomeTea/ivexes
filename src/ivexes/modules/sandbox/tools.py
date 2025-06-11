from agents import function_tool
from ivexes.modules.sandbox.sandbox import Sandbox
from ivexes.config.settings import settings
import ivexes.config.log as log
logger = log.get(__name__)
sandbox = Sandbox(settings.setup_archive)

@function_tool
def setup_sandbox() -> str:
    """
    Sets up a kali sandbox environment.

    Returns:
        str: A message indicating the result of the setup operation. And basic information about the environment.
    """
    logger.info(f'running setup_sandbox()')
    success = sandbox.connect()
    if not success:
        return "Failed to setup sandbox"
    r = "Sandbox setup successfully\n"
    r += sandbox.write_to_shell(b"whoami")
    r += sandbox.write_to_shell(b"pwd")
    r += sandbox.write_to_shell(b"ls -la")
    return r


@function_tool
def teardown_sandbox() -> str:
    """
    Teardown the kali sandbox environment.

    Returns:
        str: A message indicating the result of the teardown operation.
    """
    logger.info(f'running teardown_sandbox()')
    return "Sandbox teardown succesfully" if sandbox.close() else "Failed to teardown sandbox"


@function_tool
def sandbox_write_to_shell(input: str) -> str:
    """
    Interactively writes the input to the shell in the kali sandbox environment.

    Args:
        input: The input to write to the shell.

    Returns:
        The output of the shell.
    """
    logger.info(f'running write_to_shell({input=})')
    return sandbox.write_to_shell(input.encode())

@function_tool
def sandbox_create_file(file_path: str, content: str) -> str:
    """
    Create a file (overriding) with the specified content in the sandbox environment.

    Args:
        file_path: The path where the file should be created.
        content: The content to write into the file.

    Returns:
        str: Confirmation message or error.
    """
    logger.info(f'running create_file({file_path=}, {content=})')
    command = f'cat > {file_path} << EOL\n{content}\nEOL\n'
    return sandbox.write_to_shell(command.encode())

sandbox_tools = [
    setup_sandbox,
    teardown_sandbox,
    sandbox_write_to_shell,
    sandbox_create_file
]
