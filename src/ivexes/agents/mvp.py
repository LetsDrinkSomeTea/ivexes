"""MVP Agent module for Minimum Viable Product analysis."""

from typing import cast, Optional

from agents import Agent, Tool

from ..tools import sandbox_tools
from ..prompts.mvp import system_msg, user_msg
from ..config import PartialSettings

from .base import BaseAgent


class MVPAgent(BaseAgent):
    """Agent specialized for MVP (Minimum Viable Product) analysis.

    This agent is configured to handle MVP tasks with sandbox tools
    and specific MVP prompts.
    """

    def __init__(
        self,
        vulnerable_version: str,
        patched_version: str,
        settings: Optional[PartialSettings] = None,
    ):
        """Initialize MVP Agent.

        Args:
            vulnerable_version: Path to vulnerable version
            patched_version: Path to patched version
            settings: Optional partial settings to configure the agent
        """
        self.vulnerable_version = vulnerable_version
        self.patched_version = patched_version
        super().__init__(settings or {})

    def _setup_agent(self):
        """Set up the MVP agent with sandbox tools."""
        self.user_msg = user_msg.format(
            vulnerable_version=self.vulnerable_version,
            patched_version=self.patched_version,
        )

        tools = cast(list[Tool], sandbox_tools)
        self.agent = Agent(
            name='Exploiter',
            instructions=system_msg,
            model=self.settings.model,
            tools=tools,
        )
