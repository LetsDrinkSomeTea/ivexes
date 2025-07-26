"""Base Agent module providing common functionality for all agents."""

from abc import ABC, abstractmethod
import time
from typing import Callable, Optional, Any, Dict

from agents import (
    Agent,
    MaxTurnsExceeded,
    MessageOutputItem,
    RunResult,
    RunResultStreaming,
    Runner,
    trace,
    SQLiteSession,
)

from ..printer import Printer

from ..config import (
    PartialSettings,
    create_settings,
    get_run_config,
)
from ..code_browser import CodeBrowser
from ..vector_db import CweCapecAttackDatabase


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
        self.settings = create_settings(settings)
        self.turns_left: int = self.settings.max_turns
        self.agent: Optional[Agent] = None
        self.user_msg: Optional[str] = None
        self.session = SQLiteSession(
            session_id=f'{self.__class__.__name__}-{self.settings.trace_name}-{time.strftime("%H:%M:%S", time.localtime())}',
            db_path=self.settings.session_db_path,
        )

        # Initialize CodeBrowser service if settings are available
        self.code_browser: Optional[CodeBrowser] = None
        if (
            self.settings.codebase_path
            and self.settings.vulnerable_folder
            and self.settings.patched_folder
        ):
            self.code_browser = CodeBrowser(
                self.settings,
            )

        self.printer = Printer(self.settings)

        # Initialize VectorDB service
        self.vector_db = CweCapecAttackDatabase(self.settings)

        self._setup_agent()

    def __del__(self):
        """Clean up when object is destroyed."""
        pass

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
            'run_config': get_run_config(self.settings),
            'max_turns': self.turns_left,
            'session': self.session,
        }

    def run_p(self, user_msg: Optional[str] = None) -> None:
        """Run the agent synchronously and print the result.

        Args:
            user_msg: Optional user message to override the default. If not provided, uses the user_msg set during agent initialization.
        """
        self.printer.print_banner()
        result = self.run(user_msg)
        self.printer.print_result(result)
        self.printer.print_usage_summary(result)
        turns = sum([1 for r in result.new_items if isinstance(r, MessageOutputItem)])
        self.turns_left -= turns

    def run(self, user_msg: Optional[str] = None) -> RunResult:
        """Run the agent synchronously.

        Args:
            user_msg: Optional user message to override the default. If not provided, uses the user_msg set during agent initialization.

        Returns:
            RunResult: The result of the agent execution.
        """
        self._check_settings(user_msg)
        with trace(self.settings.trace_name):
            runner_config = self._get_runner_config()
            runner_config['input'] = user_msg if user_msg else self.user_msg
            result = Runner.run_sync(**runner_config)
            self.printer.print_usage_summary(result)
            return result

    async def run_streamed_p(self, user_msg: Optional[str] = None) -> None:
        """Run the agent with streaming output.

        Args:
            user_msg: Optional user message to override the default. If not provided, uses the user_msg set during agent initialization.
        """
        self.printer.print_banner()
        result = self.run_streamed(user_msg)
        await self.printer.stream_result(result)
        self.printer.print_usage_summary(result)
        self.turns_left -= result.current_turn

    def run_streamed(self, user_msg: Optional[str] = None) -> RunResultStreaming:
        """Run the agent with streaming results.

        Args:
            user_msg: Optional user message to override the default. If not provided, uses the user_msg set during agent initialization.

        Returns:
            RunResultStreaming: The streaming result of the agent execution.
        """
        self._check_settings(user_msg)
        with trace(self.settings.trace_name):
            runner_config = self._get_runner_config()
            runner_config['input'] = user_msg if user_msg else self.user_msg
            result = Runner.run_streamed(**runner_config)
            return result

    async def run_interactive(
        self,
        user_msg: Optional[str] = None,
        result_hook: Callable[[RunResultStreaming], None] | None = None,
    ) -> None:
        """Run the agent in interactive mode with continuous user input.

        Allows users to have a conversation with the agent. The session continues
        until the user types 'exit', 'quit', or 'q'.

        Args:
            user_msg: Optional user message to override the default. If not provided, uses the user_msg set during agent initialization.
            result_hook: Optional callback function to process the result after each interaction.
        """
        self.printer.print_banner()
        self._check_settings(user_msg)
        with trace(self.settings.trace_name):
            user_msg = user_msg if user_msg else self.user_msg
            if not user_msg:
                raise ValueError(
                    f'User message is not set. Please provide a message in _setup_agent or run command.'
                )
            runner_config = self._get_runner_config()

            while user_msg not in ['exit', 'quit', 'q']:
                try:
                    result = Runner.run_streamed(input=user_msg, **runner_config)
                    await self.printer.stream_result(result)
                    self.printer.print_usage_summary(result)
                    self.turns_left -= result.current_turn
                    if result_hook:
                        result_hook(result)
                except MaxTurnsExceeded as e:
                    print(f'MaxTurnsExceeded: {e}')
                user_msg = input(f'User ({self.turns_left} turns left): ')
