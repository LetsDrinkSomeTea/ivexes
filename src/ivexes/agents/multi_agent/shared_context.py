"""Simple shared context for multi-agent memory management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Union
from agents import RunResult, RunResultStreaming
from agents.usage import Usage

import logging

logger = logging.getLogger(__name__)


@dataclass
class SharedMemory:
    """Simple key-value based shared object for cross-agent information."""

    def _time(self):
        return datetime.now().strftime('%H:%M:%S')

    @dataclass
    class Entry:
        """Entry in shared memory."""

        value: str
        timestamp: str

        def __str__(self) -> str:
            """Format the entry for display.

            Returns:
                Formatted string representation of the entry.

                [TIMESTAMP]
                VALUE
            """
            return f'[{self.timestamp}]\n{self.value}'

    data: dict[str, Entry] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def set(self, key: str, value: str):
        """Store a value in shared memory."""
        self.data[key] = self.Entry(value=value, timestamp=self._time())

    def get(self, key: str, default=None):
        """Retrieve a value from shared memory."""
        item = self.data.get(key)
        return f'[{item.timestamp}]\n{item.value}' if item else default

    def keys(self) -> list[str]:
        """Get all available keys."""
        return list(self.data.keys())

    def summary(self) -> str:
        """Get a summary of shared memory contents."""
        if not self.data:
            return 'Shared memory is empty'

        items = []
        for key, item in self.data.items():
            truncated_value = (
                f'{item.value[:80]}... (truncated)'
                if len(item.value) > 80
                else item.value
            )
            items.append(f'  -[{item.timestamp}] {key}:\n{truncated_value}\n{"-" * 80}')

        joined_items = '\n'.join(items)
        return f'Shared memory contents (current time: {self._time()}):\n{joined_items}'

    def __str__(self) -> str:
        """String representation of the shared memory.

        Returns:
            Formatted string with all entries in shared memory.
        """
        return '\n'.join(f'{key}\n{str(entry)}\n\n' for key, entry in self.data.items())


@dataclass
class MultiAgentContext:
    """Combined context with agent memories and shared data."""

    shared_memory: SharedMemory = field(default_factory=SharedMemory)
    start_time: datetime = field(default_factory=datetime.now)
    agents_usage: dict[str, Usage] = field(default_factory=dict)
    report_generated: bool = False
    times_reprompted: int = 0

    def get_shared_memory(self) -> SharedMemory:
        """Get shared memory object."""
        return self.shared_memory

    def get_usage(self) -> str:
        """Get a summary of token usage across all agents.

        Returns:
            Formatted string with total token usage and subagent usage.
        """
        ret = '## Usage Summary:\n'

        def format_usage(u: Usage) -> str:
            return (
                f'{u.input_tokens:,} input + '
                f'{u.output_tokens:,} output = '
                f'{u.total_tokens:,} total tokens ({u.requests} requests)'
            )

        total_usage = Usage()
        for usage in self.agents_usage.values():
            total_usage.add(usage)

        ret += f'Total tokens used: {format_usage(total_usage)}\n'

        if self.agents_usage:
            lines = []
            active_agents = {
                name: usage
                for name, usage in self.agents_usage.items()
                if usage.total_tokens > 0
                or usage.input_tokens > 0
                or usage.output_tokens > 0
            }

            if active_agents:
                agent_names = list(active_agents.keys())
                for i, (agent_name, usage) in enumerate(active_agents.items()):
                    prefix = '├─' if i < len(agent_names) - 1 else '└─'
                    agent_line = f'{prefix} {agent_name}: {format_usage(usage)}'
                    lines.append(agent_line)
            ret += '\nUsage per agent:\n' + '\n'.join(lines)
        return ret or 'No usage information available'

    def update_usage(
        self,
        result: Union[RunResult, RunResultStreaming],
        subagent: str = 'planning-agent',
    ) -> None:
        """Update the total usage for this multi-agent context.

        Args:
            result: The RunResult or RunResultStreaming object
            subagent: Optional name of the subagent that generated this usage
        """
        try:
            usage = result.context_wrapper.usage
        except AttributeError:
            logger.warning('No usage information available in result')
            return None

        if not usage:
            logger.debug(f'usage is none for subagent {subagent}')
            return

        total_tokens = (
            usage.total_tokens
            if usage.total_tokens > 0
            else (usage.input_tokens + usage.output_tokens)
        )
        total_usage = Usage(
            requests=usage.requests,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=total_tokens,
            input_tokens_details=usage.input_tokens_details,
            output_tokens_details=usage.output_tokens_details,
        )
        if subagent not in self.agents_usage:
            self.agents_usage[subagent] = total_usage
        else:
            self.agents_usage[subagent].add(total_usage)

    def __str__(self) -> str:
        """String representation of the multi-agent context.

        Returns:
            Formatted string with agent memories and shared memory summary.
        """
        context_info = (
            'Multi-Agent Context:\n'
            + f'Total running time: {(datetime.now() - self.start_time).total_seconds():.1f} seconds\n'
        )

        context_info += self.get_usage() + '\n'

        context_info += '\n\nShared Memory:\n' + str(self.shared_memory)
        return context_info
