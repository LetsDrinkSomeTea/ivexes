"""Agent wrapper tools for converting agents into reusable tools."""

import time

from agents import Agent, RunConfig, Runner, SQLiteSession, Tool, function_tool

from ...printer import Printer
from .shared_context import MultiAgentContext
from ...config.settings import Settings

import logging

logger = logging.getLogger(__name__)


def agent_as_tool(
    agent: Agent,
    tool_name: str,
    tool_description: str,
    settings: Settings,
    context: MultiAgentContext,
    run_config: RunConfig,
) -> Tool:
    """Convert an agent into a tool that can be used by other agents.

    Args:
        agent: The agent to wrap as a tool
        tool_name: Name of the created tool
        tool_description: Description of the tool's functionality
        settings: Settings for the agent execution
        context: Optional shared context for multi-agent interactions
        run_config: Run configuration for the agent execution

    Returns:
        A tool that executes the agent with the given configuration
    """
    printer = Printer(settings=settings)
    session = SQLiteSession(
        session_id=f'{tool_name}-{settings.trace_name}-{time.strftime("%H:%M:%S", time.localtime())}',
        db_path=settings.session_db_path,
    )

    @function_tool(
        name_override=tool_name,
        description_override=tool_description,
    )
    async def agent_tool_function(input: str):
        # Print start marker for subagent execution
        printer.print_and_write_to_file(f'{"":=^80}')
        printer.print_and_write_to_file(f'Starting {agent.name} execution')
        printer.print_and_write_to_file(f'Input: {input}')
        printer.print_and_write_to_file(f'{"":=^80}\n')

        input = f'{context.get_shared_memory().summary()}\n\nNew Task:\n{input}'

        result = Runner.run_streamed(
            starting_agent=agent,
            input=input,
            run_config=run_config,
            max_turns=settings.max_turns,
            session=session,
        )
        await printer.stream_result(result)

        context.update_usage(result, tool_name)

        # Print end marker for subagent execution
        printer.print_and_write_to_file(f'\n{"":=^80}')
        printer.print_and_write_to_file(f'{agent.name} execution completed')
        printer.print_and_write_to_file(f'{"":=^80}')

        return result.final_output

    return agent_tool_function


def create_shared_memory_tools(context: MultiAgentContext) -> list[Tool]:
    """Create tools for accessing shared memory in a multi-agent context.

    Args:
        context: The MultiAgentContext containing shared memory

    Returns:
        A list of tools for interacting with shared memory
    """

    @function_tool(strict_mode=True)
    def set_shared_memory(key: str, value: str, override: bool = False):
        """Set a value in shared memory.

        Args:
            key: The key under which to store the value
            value: The value to store
            override: Whether to override existing value if it exists
        """
        if (val := context.shared_memory.get(key)) and not override:
            return f'Key "{key}" already exists. Use override=True to replace it.\nValue:\n{val}'
        context.shared_memory.set(key, value)
        return f'Successfully set value for key "{key}".'

    @function_tool(strict_mode=True)
    def get_shared_memory(key: str):
        """Get a value from shared memory.

        Args:
            key: The key to retrieve the value for

        Returns:
            The value stored under the given key, or a message if not found
        """
        return context.shared_memory.get(key, 'Key not found')

    @function_tool(strict_mode=True)
    def list_shared_memory():
        """List all keys and values in shared memory.

        Returns:
            A summary of all items in shared memory
        """
        return context.get_shared_memory().summary()

    return [
        set_shared_memory,
        get_shared_memory,
        list_shared_memory,
    ]
