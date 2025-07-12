"""Base Agent module providing common functionality for all agents."""

from abc import ABC, abstractmethod
from typing import Optional, Callable, Any, Dict
from contextlib import contextmanager

from agents import Agent, MaxTurnsExceeded, Runner, TResponseInputItem, trace
from openai.types.responses import EasyInputMessage, EasyInputMessageParam
from openai.types.responses.response_input_param import Message

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

    # Error message constants
    _AGENT_NOT_SET_ERROR = (
        'Agent is not set up. Make sure to assign self.agent in _setup_agent method.'
    )
    _USER_MSG_NOT_SET_ERROR = 'User message is not set. Make sure to assign self.user_msg in _setup_agent method'

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

    def _check_settings(self):
        """Validate that agent and user message are properly configured.

        Raises:
            ValueError: If agent or user_msg are not set.
        """
        if not self.agent:
            raise ValueError(self._AGENT_NOT_SET_ERROR)
        if not self.user_msg:
            raise ValueError(self._USER_MSG_NOT_SET_ERROR)

    def _get_runner_config(self) -> Dict[str, Any]:
        """Get common Runner configuration parameters.

        Returns:
            Dict containing common Runner parameters.
        """
        return {
            'starting_agent': self.agent,
            'run_config': get_run_config(),
            'max_turns': self.settings.max_turns,
        }

    @contextmanager
    def _prepare_execution(self):
        """Prepare execution context with validation, banner, and tracing.

        Yields:
            None: Context is set up for execution.
        """
        self._check_settings()
        print_banner()
        with trace(self.settings.trace_name):
            yield

    def _execute_with_context(
        self, runner_func: Callable, result_handler: Callable, input_data: Any = None
    ):
        """Execute runner function with common context setup.

        Args:
            runner_func: Runner function to execute (run_sync, run_streamed, etc.)
            result_handler: Function to handle the result (print_result, stream_result)
            input_data: Input data for the runner, defaults to self.user_msg
        """
        with self._prepare_execution():
            runner_config = self._get_runner_config()
            runner_config['input'] = input_data or self.user_msg

            result = runner_func(**runner_config)
            return result_handler(result) if result_handler else result

    def run(self) -> None:
        """Run the agent synchronously and print the result."""
        self._execute_with_context(Runner.run_sync, print_result)

    async def run_streamed(self) -> None:
        """Run the agent with streaming output."""
        await self._execute_with_context(Runner.run_streamed, stream_result)

    async def run_interactive(self) -> None:
        """Run the agent in interactive mode with continuous user input.

        Allows users to have a conversation with the agent. The session continues
        until the user types 'exit', 'quit', or 'q'.
        """
        with self._prepare_execution():
            input_items: list[TResponseInputItem] = []
            user_msg = self.user_msg
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
