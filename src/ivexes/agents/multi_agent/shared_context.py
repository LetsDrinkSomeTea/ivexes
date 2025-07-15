"""Simple shared context for multi-agent memory management."""

from dataclasses import dataclass, field
from datetime import datetime
from agents import TResponseInputItem
from openai.types.responses import EasyInputMessageParam


@dataclass
class AgentMemory:
    """Stores complete conversation history for an agent."""

    agent_name: str
    messages: list[TResponseInputItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def clear_messages(self):
        """Clear conversation history."""
        self.messages.clear()

    def append_messages(
        self, messages: list[TResponseInputItem] | TResponseInputItem | str
    ) -> list[TResponseInputItem]:
        """Append messages to the agent's memory.

        Args:
            messages: A single message or a list of messages to append.

        Returns:
            The updated list of messages in the agent's memory.
        """
        if isinstance(messages, list):
            self.messages.extend(messages)
        else:
            self.messages.append(
                EasyInputMessageParam(content=messages, role='user')
                if isinstance(messages, str)
                else messages
            )
        return self.messages


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

    agent_memories: dict[str, AgentMemory] = field(default_factory=dict)
    shared_memory: SharedMemory = field(default_factory=SharedMemory)
    start_time: datetime = field(default_factory=datetime.now)

    def get_agent_memory(self, agent_name: str) -> AgentMemory:
        """Get or create agent memory."""
        if agent_name not in self.agent_memories:
            self.agent_memories[agent_name] = AgentMemory(agent_name=agent_name)
        return self.agent_memories[agent_name]

    def get_shared_memory(self) -> SharedMemory:
        """Get shared memory object."""
        return self.shared_memory

    def __str__(self) -> str:
        """String representation of the multi-agent context.

        Returns:
            Formatted string with agent memories and shared memory summary.
        """
        agent_summaries = [
            f'Agent: {name}, Messages: {len(memory.messages)}'
            for name, memory in self.agent_memories.items()
        ]

        return (
            'Multi-Agent Context:\n'
            + f'Total running time: {(datetime.now() - self.start_time).total_seconds()} seconds\n'
            + '\n'.join(agent_summaries)
            + '\n\nShared Memory:\n'
            + str(self.shared_memory)
        )
