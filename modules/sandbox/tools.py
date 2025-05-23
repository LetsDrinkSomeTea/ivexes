from agents import function_tool
from modules.sandbox.sandbox import Sandbox
from config.settings import settings

sandbox = Sandbox(settings.executable_archive)

@function_tool
def setup_sandbox() -> str:
    """
    Sets up a kali sandbox environment.

    Returns:
        str: A message indicating the result of the setup operation. And basic information about the environment.
    """

    success = sandbox.connect()
    if not success:
        return "Failed to setup sandbox"
    r = "Sandbox setup successfully\n"
    r += sandbox.write_to_shell(b"pwd").splitlines()[-1]
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
    #dc.containers.get("kali-ssh").stop()
    return "Sandbox teardown succesfully" if sandbox.close() else "Failed to teardown sandbox"


@function_tool
def write_to_shell(input: str) -> str:
    """
    Interactively writes the input to the shell in the kali sandbox environment.

    Args:
        input: The input to write to the shell.

    Returns:
        The output of the shell.
    """
    return sandbox.write_to_shell(input.encode())

sandbox_tools = [
    setup_sandbox,
    teardown_sandbox,
    write_to_shell
]