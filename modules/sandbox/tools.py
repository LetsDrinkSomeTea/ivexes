from langchain_core.tools import tool

import sandbox.ssh_client

ssh_client = sandbox.ssh_client.SSHClientWrapper("root", "passwd")

@tool(parse_docstring=True)
def setup_sandbox() -> str:
    """
    Sets up a kali sandbox environment.

    Returns:
        str: A message indicating the result of the setup operation. And basic information about the environment.
    """

    success = ssh_client.connect()
    if not success:
        return "Failed to setup sandbox"
    r = "Sandbox setup successfully\n"
    r += ssh_client.write_to_shell(b"pwd").splitlines()[-1]
    r += ssh_client.write_to_shell(b"whoami")
    r += ssh_client.write_to_shell(b"pwd")
    r += ssh_client.write_to_shell(b"ls -la")
    return r


@tool(parse_docstring=True)
def teardown_sandbox() -> str:
    """
    Teardown the kali sandbox environment.

    Returns:
        str: A message indicating the result of the teardown operation.
    """
    #dc.containers.get("kali-ssh").stop()
    return "Sandbox teardown succesfully" if ssh_client.close() else "Failed to teardown sandbox"


@tool(parse_docstring=True)
def write_to_shell(input: str) -> str:
    """
    Interactively writes the input to the shell in the kali sandbox environment.

    Args:
        input: The input to write to the shell.

    Returns:
        The output of the shell.
    """
    return ssh_client.write_to_shell(input.encode())

sandbox_tools = [
    setup_sandbox,
    teardown_sandbox,
    write_to_shell
]