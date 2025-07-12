"""MVP Agent module for Minimum Viable Product analysis."""

from typing import Optional

from agents import Agent
from ..config import PartialSettings
from ..tools import date_tools

from .base import BaseAgent


class DefaultAgent(BaseAgent):
    """Agent specialized for MVP (Minimum Viable Product) analysis.

    This agent is configured to handle MVP tasks with sandbox tools
    and specific MVP prompts.
    """

    def __init__(
        self,
        system_msg: Optional[str] = None,
        settings: Optional[PartialSettings] = None,
    ):
        """Initialize MVP Agent.

        Args:
            system_msg: Custom system message for the agent
            settings: Optional partial settings to configure the agent
        """
        self.system_msg = system_msg if system_msg else 'You are a helpful assistant!'
        super().__init__(settings or {})

    def _setup_agent(self):
        """Set up the MVP agent with sandbox tools."""
        self.agent = Agent(
            name='Exploiter',
            instructions=self.system_msg,
            model=self.settings.model,
            tools=date_tools,
        )
