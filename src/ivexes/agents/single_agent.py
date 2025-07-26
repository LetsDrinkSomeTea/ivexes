"""Single Agent module for comprehensive security analysis."""

from typing import cast, Optional

from agents import Agent, Tool

from ..vector_db import create_vectordb_tools
from ..sandbox.tools import create_sandbox_tools
from ..code_browser.tools import create_code_browser_tools
from ..prompts.single_agent import system_msg, user_msg
from ..config import PartialSettings

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
        # SingleAgent requires code browser to be configured
        if not self.code_browser:
            raise ValueError(
                'SingleAgent requires codebase_path, vulnerable_folder, and patched_folder '
                'to be set in settings for code browser functionality.'
            )

        self.user_msg = user_msg.format(
            codebase_structure=self.code_browser.get_codebase_structure(),
            diff=self.code_browser.get_diff(),
            bin_path=self.bin_path,
        )

        # Create tools using mixed service/factory pattern
        sandbox_tools = create_sandbox_tools(self.settings)  # Factory pattern
        code_browser_tools = create_code_browser_tools(
            self.code_browser
        )  # Service pattern
        vectordb_tools = create_vectordb_tools(self.vector_db)  # Service pattern

        tools = cast(list[Tool], sandbox_tools + code_browser_tools + vectordb_tools)
        self.agent = Agent(
            name='Exploiter',
            instructions=system_msg,
            model=self.settings.model,
            tools=tools,
        )
