"""Printer module for formatting and displaying agent interactions.

This module provides functionality to format and display various types of
agent interactions including messages, tool calls, handoffs, and reasoning
steps. It handles output formatting for both console and file display.
"""

from typing import Iterable, Optional, Union, Any, Callable
from agents import RunItem, TResponseInputItem, Tool
from agents.items import (
    HandoffCallItem,
    HandoffOutputItem,
    ItemHelpers,
    MCPApprovalRequestItem,
    MCPListToolsItem,
    MessageOutputItem,
    ReasoningItem,
    ToolCallItem,
    ToolCallOutputItem,
)
from agents.models.chatcmpl_converter import Converter
from agents.result import RunResult, RunResultStreaming
from openai.types.responses import ResponseFunctionToolCall
import json
import time

from .components import banner
from ..config import get_settings

TIME_STRING: str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def print_and_write_to_file(text: str, truncate: bool = True, end: str = '\n') -> None:
    """Print text to console and write to file with optional truncation.

    Args:
        text: Text to print and write
        truncate: Whether to truncate long output
        end: Line ending character
    """
    lines: list[str] = text.splitlines()
    if truncate and len(lines) > 10:
        lines = lines[:10] + [f'... truncated {len(lines) - 10} lines']
    print('\n'.join(lines), end=end)
    with open(f'output-{TIME_STRING}.txt', 'a') as f:
        f.write(text + end)


def format_tool_call(tool_call: Union[ResponseFunctionToolCall, Any]) -> str:
    """Format a tool call with its arguments."""
    if isinstance(tool_call, ResponseFunctionToolCall):
        formatted_args: str = ', '.join(
            f'{k}={repr(v)}' for k, v in json.loads(tool_call.arguments).items()
        )
        return f'{tool_call.name}({formatted_args})'
    return str(tool_call)


def create_header(
    item_type: str, turn: Optional[int] = None, agent_name: Optional[str] = None
) -> str:
    """Create a formatted header for an item."""
    prefix: str = f'[{turn}]' if turn is not None else ''
    agent_suffix: str = f' ({agent_name})' if agent_name else ''
    header_text: str = f'{item_type}{agent_suffix}'
    return f'{prefix}{header_text:=^80}'


class ItemFormatter:
    """Handles formatting of different RunItem types."""

    @staticmethod
    def format_message_output(item: MessageOutputItem) -> tuple[str, str]:
        """Format a message output item for display.

        Args:
            item: Message output item to format

        Returns:
            Tuple of (label, formatted_content)
        """
        return 'Agent', ItemHelpers.text_message_output(item)

    @staticmethod
    def format_tool_call(item: ToolCallItem) -> tuple[str, str]:
        """Format a tool call item for display.

        Args:
            item: Tool call item to format

        Returns:
            Tuple of (label, formatted_content)
        """
        return 'Tool Call', format_tool_call(item.raw_item)

    @staticmethod
    def format_tool_call_output(item: ToolCallOutputItem) -> tuple[str, str]:
        """Format a tool call output item for display.

        Args:
            item: Tool call output item to format

        Returns:
            Tuple of (label, formatted_content)
        """
        return 'Tool Output', item.output

    @staticmethod
    def format_handoff_call(item: HandoffCallItem) -> tuple[str, str]:
        """Format a handoff call item for display.

        Args:
            item: Handoff call item to format

        Returns:
            Tuple of (label, formatted_content)
        """
        raw_call: Any = item.raw_item
        if isinstance(raw_call, ResponseFunctionToolCall):
            formatted_call: str = format_tool_call(raw_call)
            content: str = f'Handoff call: {formatted_call}'
        else:
            content = f'Handoff call: {raw_call}'
        return 'Handoff Requested', content

    @staticmethod
    def format_handoff_output(item: HandoffOutputItem) -> tuple[str, str]:
        """Format a handoff output item for display.

        Args:
            item: Handoff output item to format

        Returns:
            Tuple of (label, formatted_content)
        """
        content: str = f'Handoff completed from {item.source_agent.name} to {item.target_agent.name}'
        return 'Handoff Completed', content

    @staticmethod
    def format_reasoning(item: ReasoningItem) -> tuple[str, str]:
        """Format a reasoning item for display.

        Args:
            item: Reasoning item to format

        Returns:
            Tuple of (label, formatted_content)
        """
        reasoning_text: str = ''
        for summary_item in item.raw_item.summary:
            reasoning_text += summary_item.text + '\n'
        return 'Reasoning', reasoning_text.rstrip()

    @staticmethod
    def format_mcp_approval_request(item: MCPApprovalRequestItem) -> tuple[str, str]:
        """Format an MCP approval request item for display.

        Args:
            item: MCP approval request item to format

        Returns:
            Tuple of (label, formatted_content)
        """
        raw_item: Any = item.raw_item
        content: str = f'MCP Server: {raw_item.server_label}\n'
        content += f'Tool: {raw_item.name}\n'
        content += f'Arguments: {raw_item.arguments}'
        return 'MCP Approval Request', content

    @staticmethod
    def format_mcp_list_tools(item: MCPListToolsItem) -> tuple[str, str]:
        """Format an MCP list tools item for display.

        Args:
            item: MCP list tools item to format

        Returns:
            Tuple of (label, formatted_content)
        """
        raw_item: Any = item.raw_item
        content: str = f'MCP Server: {raw_item.server_label}\n'
        if raw_item.tools:
            content += 'Available tools:\n'
            for tool in raw_item.tools:
                tool_desc: str = (
                    tool.description if tool.description else 'No description'
                )
                content += f'  - {tool.name}: {tool_desc}\n'
        return 'MCP Tools List', content.rstrip()

    @classmethod
    def format_item(cls, item: RunItem) -> tuple[str, str]:
        """Format any RunItem and return (item_type, content)."""
        formatters = {
            MessageOutputItem: cls.format_message_output,
            ToolCallItem: cls.format_tool_call,
            ToolCallOutputItem: cls.format_tool_call_output,
            HandoffCallItem: cls.format_handoff_call,
            HandoffOutputItem: cls.format_handoff_output,
            ReasoningItem: cls.format_reasoning,
            MCPApprovalRequestItem: cls.format_mcp_approval_request,
            MCPListToolsItem: cls.format_mcp_list_tools,
        }

        formatter: Optional[Callable[[RunItem], tuple[str, str]]] = formatters.get(
            type(item)
        )
        if formatter:
            return formatter(item)
        else:
            return f'Unknown Item {type(item).__name__}', str(item)


def get_agent_name(item: RunItem) -> Optional[str]:
    """Extract agent name from a RunItem."""
    agent: Any = getattr(item, 'agent', None)
    return agent.name if agent and hasattr(agent, 'name') else None


def print_item(item: RunItem, turn: Optional[int] = None) -> None:
    """Print a single item with proper formatting."""
    item_type: str
    content: str
    item_type, content = ItemFormatter.format_item(item)
    agent_name: Optional[str] = get_agent_name(item)
    header: str = create_header(item_type, turn, agent_name)
    print_and_write_to_file(f'{header}\n{content}\n')


def print_result(result: RunResult) -> list[TResponseInputItem]:
    """Prints the result of a run and returns the input list for the next run."""
    print_items(result.new_items)
    return result.to_input_list()


def print_items(items: list[RunItem]) -> None:
    """Print a list of items."""
    for item in items:
        print_item(item)


async def stream_result(result: RunResultStreaming) -> list[TResponseInputItem]:
    """Stream and print results as they come in."""
    async for event in result.stream_events():
        if event.type == 'raw_response_event':
            continue
        elif event.type == 'agent_updated_stream_event':
            continue
        elif event.type == 'run_item_stream_event':
            print_item(event.item, result.current_turn)
        else:
            # Handle any other event types
            print_and_write_to_file(
                f'[{result.current_turn}]{f"Unknown Event {event.type}":=^80}\n{event}\n'
            )
    return result.to_input_list()


def print_banner() -> None:
    """Print a banner with configuration details."""
    settings = get_settings()
    print_and_write_to_file(
        banner(
            model=settings.model,
            reasoning_model=settings.reasoning_model,
            temperature=settings.model_temperature,
            max_turns=settings.max_turns,
            trace_name=settings.trace_name,
        ),
        truncate=False,
    )


def sprint_tools_as_json(tools: Tool | Iterable[Tool]) -> str:
    """Convert tools to JSON formatted string for OpenAI API."""
    p = lambda x: json.dumps(Converter.tool_to_openai(x).get('function', {}), indent=2)
    return p(tools) if isinstance(tools, Tool) else '\n'.join(p(tool) for tool in tools)


def print_tools_as_json(tools: Tool | Iterable[Tool]) -> None:
    """Print tools as JSON formatted string."""
    print_and_write_to_file(sprint_tools_as_json(tools), truncate=False, end='\n\n')
