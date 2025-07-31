"""Printer module for formatting and displaying agent interactions.

This module provides functionality to format and display various types of
agent interactions including messages, tool calls, handoffs, and reasoning
steps. It handles output formatting for both console and file display.
"""

import os
from typing import Iterable, Optional, Union
from agents import RunItem, TResponseInputItem, Tool
from agents.result import RunResult, RunResultStreaming
import time

import logging

from .components import banner, format_usage_display
from .formatter import (
    ItemFormatter,
    create_header,
    get_agent_name,
    sprint_tools_as_json,
)
from ..config.settings import Settings

logger = logging.getLogger(__name__)

TIME_STRING: str = time.strftime('%H:%M:%S', time.localtime())


class Printer:
    """Printer service for agent output formatting and logging.

    This class handles all printing and file logging for agents,
    encapsulating settings-dependent behavior like trace names and model info.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize printer with settings.

        Args:
            settings: Settings instance containing trace_name, model, etc.
        """
        self.settings = settings
        self.time_string = time.strftime('%H:%M:%S', time.localtime())

    def print_and_write_to_file(
        self, text: str, truncate: bool = True, end: str = '\n'
    ) -> None:
        """Print text to console and write to file with optional truncation.

        Args:
            text: Text to print and write
            truncate: Whether to truncate long output
            end: Line ending character
        """
        lines: list[str] = text.splitlines()
        if truncate and len(lines) > 10:
            lines = lines[:10] + [f'... truncated {len(lines) - 10} lines']
        out_str = '\n'.join(lines)
        if self.settings and self.settings.rich_console:
            self.settings.rich_console.print(out_str, end=end)
        else:
            print(out_str, end=end)
        if self.settings:
            path = os.path.join(
                'output',
                f'{self.settings.trace_name}',
                f'{self.settings.model}-{self.time_string}.txt',
            )
            os.makedirs(name=os.path.dirname(path), exist_ok=True)
            with open(path, 'a') as f:
                f.write(text + end)

    def print_banner(self) -> None:
        """Print a banner with configuration details."""
        if not self.settings:
            logger.warning(f'No settings provided for printer, skipping banner.')
            return

        self.print_and_write_to_file(
            banner(
                model=self.settings.model,
                reasoning_model=self.settings.reasoning_model,
                temperature=self.settings.model_temperature,
                max_turns=self.settings.max_turns,
                trace_name=self.settings.trace_name,
            ),
            truncate=False,
        )

    async def stream_result(
        self, result: RunResultStreaming
    ) -> list[TResponseInputItem]:
        """Stream and print results as they come in."""
        async for event in result.stream_events():
            if event.type == 'raw_response_event':
                continue
            elif event.type == 'agent_updated_stream_event':
                continue
            elif event.type == 'run_item_stream_event':
                self.print_item(event.item, result.current_turn)
            else:
                # Handle any other event types
                self.print_and_write_to_file(
                    f'[{result.current_turn}]{f"Unknown Event {event.type}":=^80}\n{event}\n'
                )
        return result.to_input_list()

    def print_tools_as_json(self, tools: Tool | Iterable[Tool]) -> None:
        """Print tools as JSON formatted string."""
        self.print_and_write_to_file(
            sprint_tools_as_json(tools), truncate=False, end='\n\n'
        )

    def print_usage_summary(self, result: Union[RunResult, RunResultStreaming]) -> None:
        """Print token usage summary for a completed run.

        Displays total token usage for the run. This is automatically called at the end of
        agent runs to provide visibility into resource consumption.

        Args:
            result: The completed run result containing usage information
        """
        usage = result.context_wrapper.usage
        if not usage:
            return

        usage_display = format_usage_display(usage, show_details=True)

        self.print_and_write_to_file(f'\n{usage_display}\n')

    def print_item(self, item: RunItem, turn: Optional[int] = None) -> None:
        """Print a single item with proper formatting."""
        item_type: str
        content: str
        item_type, content = ItemFormatter.format_item(item)
        agent_name: Optional[str] = get_agent_name(item)
        header: str = create_header(item_type, turn, agent_name)
        self.print_and_write_to_file(f'{header}\n{content}\n')

    def print_result(self, result: RunResult) -> list[TResponseInputItem]:
        """Prints the result of a run and returns the input list for the next run."""
        self.print_items(result.new_items)
        return result.to_input_list()

    def print_items(self, items: list[RunItem]) -> None:
        """Print a list of items."""
        for item in items:
            self.print_item(item)


async def stream_result(result: RunResultStreaming) -> list[TResponseInputItem]:
    """Stream and print results using the provided printer."""
    return await Printer().stream_result(result)


def print_result(result: RunResult) -> list[TResponseInputItem]:
    """Print the result of a run and return the input list for the next run."""
    return Printer().print_result(result)
