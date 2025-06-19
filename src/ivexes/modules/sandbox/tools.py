from agents import function_tool
from ivexes.modules.sandbox.sandbox import Sandbox
from ivexes.config.settings import settings
import ivexes.config.log as log
logger = log.get(__name__)
sandbox: Sandbox | None = None

@function_tool
def setup_sandbox() -> str:
    """
    Sets up a kali sandbox environment.

    Returns:
        str: A message indicating the result of the setup operation. And basic information about the environment.
    """
    global sandbox
    logger.info(f'running setup_sandbox()')
    sandbox = Sandbox(settings.setup_archive)
    if not sandbox.connect():
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
    global sandbox
    logger.info(f'running teardown_sandbox()')
    success = False
    if sandbox: 
        success = sandbox.close()
    if success: 
        sandbox = None
    return "Sandbox teardown succesfully" if success else "Failed to teardown sandbox"


@function_tool
def sandbox_write_to_shell(input: str) -> str:
    """
    Interactively writes the input to the shell in the kali sandbox environment.

    Args:
        input: The input to write to the shell.

    Returns:
        The output of the shell.
    """
    global sandbox
    logger.info(f'running write_to_shell({input=})')
    if not sandbox:
        return "Sandbox is not set up. Please run setup_sandbox() first."
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
    global sandbox
    logger.info(f'running create_file({file_path=}, {content=})')
    if not sandbox:
        return "Sandbox is not set up. Please run setup_sandbox() first."
    success = sandbox.create_file(file_path, content)
    return f'File {file_path} created successfully.' if success else f'Failed to create file {file_path}.'

sandbox_tools = [
    setup_sandbox,
    teardown_sandbox,
    sandbox_write_to_shell,
    sandbox_create_file
]
