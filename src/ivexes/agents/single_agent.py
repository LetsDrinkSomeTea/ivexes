"""Single Agent module for comprehensive security analysis."""

from typing import cast, Optional

from agents import Agent, Tool

from ..tools import sandbox_tools, code_browser_tools, vectordb_tools
from ..prompts.single_agent import system_msg, user_msg
from ..config import PartialSettings
from ..code_browser import get_code_browser

from .base import BaseAgent


class SingleAgent(BaseAgent):
    """Agent specialized for single agent analysis tasks.

    This agent is configured with sandbox tools, code browser tools,
    and vector database tools for comprehensive analysis.
    """

    def __init__(self, bin_path: str, settings: Optional[PartialSettings] = None):
        """Initialize Single Agent.

        Args:
            bin_path: Path to the binary to analyze inside the sandbox
            settings: Optional partial settings to configure the agent
        """
        self.bin_path = bin_path
        super().__init__(settings or {})

    def _setup_agent(self):
        """Set up the single agent with comprehensive tools."""
        code_browser = get_code_browser()
        self.user_msg = user_msg.format(
            codebase_structure=code_browser.get_codebase_structure(),
            diff=code_browser.get_diff(),
            bin_path=self.bin_path,
        )

        tools = cast(list[Tool], sandbox_tools + code_browser_tools + vectordb_tools)
        self.agent = Agent(
            name='Exploiter',
            instructions=system_msg,
            model=self.settings.model,
            tools=tools,
        )
