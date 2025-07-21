"""Base Agent module providing common functionality for all agents."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Any, Dict

from agents import (
    Agent,
    MaxTurnsExceeded,
    RunResult,
    RunResultStreaming,
    Runner,
    TResponseInputItem,
    trace,
    SQLiteSession,
)
from openai.types.responses import EasyInputMessageParam

from ivexes import print_result, print_banner, stream_result

from ..config import (
    PartialSettings,
    get_settings,
    set_settings,
    reset_settings,
    get_run_config,
)


class BaseAgent(ABC):
    """Base class for all agents providing common functionality and interface.

    This abstract base class defines the common interface and functionality
    for all agents in the system. It handles settings management, agent
    initialization, and provides different execution modes.
    """

    def __init__(self, settings: PartialSettings):
        """Initialize the base agent with settings.

        Args:
            settings: Partial settings to configure the agent. Settings not provided
                will be loaded from environment variables.
        """
        set_settings(settings)
        self.settings = get_settings()
        self.agent: Optional[Agent] = None
        self.user_msg: Optional[str] = None
        self.session = SQLiteSession(
            session_id=f'{self.__class__.__name__}-{self.settings.trace_name}-{datetime.isoformat}',
            db_path=self.settings.session_db_path,
        )
        self._setup_agent()

    def __del__(self):
        """Clean up by resetting settings when object is destroyed."""
        reset_settings()

    @abstractmethod
    def _setup_agent(self):
        """Set up the agent instance.

        This method must be implemented by subclasses to initialize the agent
        and user message. Should set self.agent and self.user_msg.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError('Subclasses must implement this method.')

    def _check_settings(self, user_msg: Optional[str]):
        """Validate that agent and user message are properly configured.

        Raises:
            ValueError: If agent or user_msg are not set.
        """
        if not self.agent:
            raise ValueError(
                'Agent is not set up. Make sure to assign self.agent in _setup_agent method.'
            )
        if not self.user_msg and not user_msg:
            raise ValueError(
                'User message is not set. Make sure to assign self.user_msg in _setup_agent method or provide one in the run command'
            )

    def _get_runner_config(self) -> Dict[str, Any]:
        """Get common Runner configuration parameters.

        Returns:
            Dict containing common Runner parameters.
        """
        return {
            'starting_agent': self.agent,
            'run_config': get_run_config(),
            'max_turns': self.settings.max_turns,
            'session': self.session,
        }

    def run_p(self, user_msg: Optional[str] = None) -> None:
        """Run the agent synchronously and print the result.

        Args:
            user_msg: Optional user message to override the default. If not provided, uses the user_msg set during agent initialization.
        """
        print_result(self.run(user_msg))

    def run(self, user_msg: Optional[str] = None) -> RunResult:
        """Run the agent synchronously.

        Args:
            user_msg: Optional user message to override the default. If not provided, uses the user_msg set during agent initialization.

        Returns:
            RunResult: The result of the agent execution.
        """
        self._check_settings(user_msg)
        print_banner()
        with trace(self.settings.trace_name):
            runner_config = self._get_runner_config()
            runner_config['input'] = user_msg if user_msg else self.user_msg
            result = Runner.run_sync(**runner_config)
            return result

    async def run_streamed_p(self, user_msg: Optional[str] = None) -> None:
        """Run the agent with streaming output.

        Args:
            user_msg: Optional user message to override the default. If not provided, uses the user_msg set during agent initialization.
        """
        await stream_result(self.run_streamed(user_msg))

    def run_streamed(self, user_msg: Optional[str] = None) -> RunResultStreaming:
        """Run the agent with streaming results.

        Args:
            user_msg: Optional user message to override the default. If not provided, uses the user_msg set during agent initialization.

        Returns:
            RunResultStreaming: The streaming result of the agent execution.
        """
        self._check_settings(user_msg)
        print_banner()
        with trace(self.settings.trace_name):
            runner_config = self._get_runner_config()
            runner_config['input'] = user_msg if user_msg else self.user_msg
            result = Runner.run_streamed(**runner_config)
            return result

    async def run_interactive(self, user_msg: Optional[str] = None) -> None:
        """Run the agent in interactive mode with continuous user input.

        Allows users to have a conversation with the agent. The session continues
        until the user types 'exit', 'quit', or 'q'.

        Args:
            user_msg: Optional user message to override the default. If not provided, uses the user_msg set during agent initialization.
        """
        self._check_settings(user_msg)
        print_banner()
        with trace(self.settings.trace_name):
            input_items: list[TResponseInputItem] = []
            user_msg = user_msg if user_msg else self.user_msg
            runner_config = self._get_runner_config()

            while user_msg not in ['exit', 'quit', 'q']:
                user_input_item = EasyInputMessageParam(content=user_msg, role='user')
                input_items.append(user_input_item)
                try:
                    result = Runner.run_streamed(input=input_items, **runner_config)
                    input_items = await stream_result(result)
                except MaxTurnsExceeded as e:
                    print(f'MaxTurnsExceeded: {e}')
                user_msg = input('User: ')
