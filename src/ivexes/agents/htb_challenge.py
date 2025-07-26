"""HTB Challenge Agent module for Hack The Box challenge exploitation."""

from typing import cast, Optional

from agents import Agent, Tool


from ..tools import sandbox_tools
from ..prompts.htb_reversing import system_msg, user_msg
from ..config import PartialSettings

from .base import BaseAgent


class HTBChallengeAgent(BaseAgent):
    """Agent specialized for Hack The Box challenge exploitation.

    This agent is configured to handle HTB challenges with sandbox tools
    and specific reversing prompts.
    """

    def __init__(
        self, program: str, challenge: str, settings: Optional[PartialSettings] = None
    ):
        """Initialize HTB Challenge Agent.

        Args:
            program: Program name for the challenge
            challenge: Challenge description
            settings: Optional partial settings to configure the agent
        """
        self.program = program
        self.challenge = challenge
        super().__init__(settings or {})

    def _setup_agent(self):
        """Set up the HTB challenge agent with sandbox tools."""
        from ..tools import create_report_tools

        self.user_msg = user_msg.format(
            program=self.program,
            challenge=self.challenge,
        )

        tools = cast(list[Tool], sandbox_tools + create_report_tools())
        self.agent = Agent(
            name='Exploiter',
            instructions=system_msg,
            model=self.settings.model,
            tools=tools,
        )
