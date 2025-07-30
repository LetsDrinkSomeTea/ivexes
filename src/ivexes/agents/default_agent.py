"""MVP Agent module for Minimum Viable Product analysis."""

from typing import Optional

from agents import Agent
from ..config import PartialSettings
from ..tools import date_tools

from .base import BaseAgent


class DefaultAgent(BaseAgent):
    """Default agent implementation with minimal setup."""

    def __init__(
        self,
        system_msg: Optional[str] = None,
        settings: Optional[PartialSettings] = None,
    ):
        """Initialize DefaultAgent with system message and settings."""
        self.system_msg = system_msg if system_msg else 'You are a helpful assistant!'
        super().__init__(settings or {})

    def _setup_agent(self):
        self.agent = Agent(
            name='Exploiter',
            instructions=self.system_msg,
            model=self.settings.model,
            tools=date_tools,
        )
