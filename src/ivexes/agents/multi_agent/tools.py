"""Agent wrapper tools for converting agents into reusable tools."""

from agents import Agent, RunConfig, Runner, Tool, function_tool
from typing import Optional

from ivexes.printer import stream_result, print_and_write_to_file
from .shared_context import MultiAgentContext


def agent_as_tool(
    agent: Agent,
    tool_name: str,
    tool_description: str,
    max_turns: int,
    run_config: RunConfig,
    context: Optional[MultiAgentContext] = None,
) -> Tool:
    """Convert an agent into a tool that can be used by other agents.

    Args:
        agent: The agent to wrap as a tool
        tool_name: Name of the created tool
        tool_description: Description of the tool's functionality
        max_turns: Maximum number of turns for the agent
        run_config: Configuration for running the agent
        context: Optional shared context for multi-agent interactions

    Returns:
        A tool that executes the agent with the given configuration
    """

    @function_tool(
        name_override=tool_name,
        description_override=tool_description,
    )
    async def agent_tool_function(input: str):
        # Print start marker for subagent execution
        print_and_write_to_file(f'{"":=^80}')
        print_and_write_to_file(f'Starting {agent.name} execution')
        print_and_write_to_file(f'Input: {input}')
        print_and_write_to_file(f'{"":=^80}\n')

        if context:
            agent_memory = context.get_agent_memory(agent_name=agent.name)
            input_items = agent_memory.append_messages(input)
            result = Runner.run_streamed(
                starting_agent=agent,
                input=input_items,
                run_config=run_config,
                max_turns=max_turns,
            )
            await stream_result(result)
            agent_memory.messages = result.to_input_list()

        else:
            result = Runner.run_streamed(
                starting_agent=agent,
                input=input,
                run_config=run_config,
                max_turns=max_turns,
            )
            await stream_result(result)

        # Print end marker for subagent execution
        print_and_write_to_file(f'\n{"":=^80}')
        print_and_write_to_file(f'{agent.name} execution completed')
        print_and_write_to_file(f'{"":=^80}')

        return result.final_output

    return agent_tool_function


def create_shared_memory_tools(context: MultiAgentContext) -> list[Tool]:
    """Create tools for accessing shared memory in a multi-agent context.

    Args:
        context: The MultiAgentContext containing shared memory

    Returns:
        A list of tools for interacting with shared memory
    """

    @function_tool
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

    @function_tool
    def get_shared_memory(key: str):
        """Get a value from shared memory.

        Args:
            key: The key to retrieve the value for

        Returns:
            The value stored under the given key, or a message if not found
        """
        return context.shared_memory.get(key, 'Key not found')

    @function_tool
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
