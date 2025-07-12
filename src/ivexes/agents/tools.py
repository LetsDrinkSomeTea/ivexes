"""Agent wrapper tools for converting agents into reusable tools."""

from agents import Agent, RunConfig, Runner, Tool, function_tool

from ivexes.printer import stream_result


def agent_as_tool(
    agent: Agent,
    tool_name: str,
    tool_description: str,
    max_turns: int,
    run_config: RunConfig,
) -> Tool:
    """Convert an agent into a tool that can be used by other agents.

    Args:
        agent: The agent to wrap as a tool
        tool_name: Name of the created tool
        tool_description: Description of the tool's functionality
        max_turns: Maximum number of turns for the agent
        run_config: Configuration for running the agent

    Returns:
        A tool that executes the agent with the given configuration
    """

    @function_tool(
        name_override=tool_name,
        description_override=tool_description,
    )
    async def agent_tool_function(input: str):
        result = Runner.run_streamed(
            starting_agent=agent,
            input=input,
            run_config=run_config,
            max_turns=max_turns,
        )
        await stream_result(result)
        return result.final_output

    return agent_tool_function
