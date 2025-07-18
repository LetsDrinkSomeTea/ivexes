"""Multi-Agent module for coordinating specialized security analysis agents."""

from typing import Optional, override

from agents import Agent, RunConfig

from ivexes.printer.printer import print_and_write_to_file


from .shared_context import MultiAgentContext
from .tools import agent_as_tool, create_shared_memory_tools
from ...tools import (
    code_browser_tools,
    date_tools,
    sandbox_tools,
    vectordb_tools,
    cve_tools,
    report_tools,
)
from ...prompts.multi_agent import (
    security_specialist_system_msg,
    code_analyst_system_msg,
    red_team_operator_system_msg,
    report_journalist_system_msg,
    planning_system_msg,
    user_msg,
)
from ...config import PartialSettings, get_run_config
from ...code_browser import get_code_browser

from ..base import BaseAgent


class MultiAgent(BaseAgent):
    """Agent specialized for multi-agent coordination tasks.

    This agent creates a planning agent that coordinates multiple
    specialized agents including security specialist, code analyst,
    red team operator, and report journalist.
    """

    def __init__(
        self,
        bin_path: str,
        settings: Optional[PartialSettings] = None,
        subagent_run_config: Optional[RunConfig] = None,
        shared_context: bool = True,
    ):
        """Initialize Multi Agent.

        Args:
            bin_path: Path to the binary to analyze inside the sandbox
            settings: Optional partial settings to configure the agent
            subagent_run_config: Optional run configuration for subagents
            shared_context: Whether to use a shared context for agents
        """
        self.bin_path = bin_path
        self.subagent_run_config = subagent_run_config
        self.context = None
        self.context_tools = []

        if shared_context:
            self.context = MultiAgentContext()
            self.context_tools = create_shared_memory_tools(self.context)
        super().__init__(settings or {})

    def _setup_agent(self):
        """Set up the multi-agent system with specialized agents."""
        # Create specialized agent tools
        if self.subagent_run_config is None:
            self.subagent_run_config = get_run_config()

        security_specialist_tool = agent_as_tool(
            agent=Agent(
                name='Security Specialist',
                handoff_description='Specialist agent for up-to-date information on CWE, CAPEC and ATT&CK data',
                instructions=security_specialist_system_msg,
                tools=vectordb_tools + cve_tools + self.context_tools,
            ),
            tool_name='security-specialist',
            tool_description='Expert in CVE, CWE, CAPEC, and ATT&CK frameworks. Provides security vulnerability analysis, attack pattern identification, and mitigation strategies based on industry standards.',
            run_config=self.subagent_run_config,
            max_turns=self.settings.max_turns,
            context=self.context,
        )

        code_analyst_tool = agent_as_tool(
            Agent(
                name='Code Analyst',
                handoff_description='Specialist agent for information about the codebase, including code structure, functions, diffs and classes',
                instructions=code_analyst_system_msg,
                tools=code_browser_tools + self.context_tools,
            ),
            tool_name='code-analyst',
            tool_description='Specialist for codebase analysis and vulnerability identification. Analyzes code structure, functions, classes, and diffs to identify potential security weaknesses.',
            run_config=self.subagent_run_config,
            max_turns=self.settings.max_turns,
            context=self.context,
        )

        red_team_operator_tool = agent_as_tool(
            Agent(
                name='Red Team Operator',
                handoff_description='Specialist agent for generating Proof-of-Concepts (PoC) and Exploits',
                instructions=red_team_operator_system_msg,
                tools=sandbox_tools + self.context_tools,
            ),
            tool_name='red-team-operator',
            tool_description='Specialist for creating and testing Proof-of-Concept exploits. Develops bash/Python scripts, tests exploits in sandbox, and validates exploitation techniques.',
            run_config=self.subagent_run_config,
            max_turns=self.settings.max_turns,
            context=self.context,
        )

        report_journalist_agent = agent_as_tool(
            Agent(
                name='Report Journalist',
                handoff_description='Specialist agent for generating reports and summaries',
                instructions=report_journalist_system_msg,
                tools=date_tools + report_tools + self.context_tools,
            ),
            tool_name='report_journalist',
            tool_description='Specialist for generating comprehensive reports and summaries. Compiles findings from security analysis, code review, and exploitation into structured reports.',
            run_config=self.subagent_run_config,
            max_turns=self.settings.max_turns,
            context=self.context,
        )

        # Create planning agent
        self.agent = Agent(
            name='Planning Agent',
            handoff_description='Specialist agent for planning and coordinating the actions of other agents',
            instructions=planning_system_msg,
            model=self.settings.reasoning_model,
            tools=[
                security_specialist_tool,
                code_analyst_tool,
                red_team_operator_tool,
                report_journalist_agent,
            ]
            + self.context_tools,
        )

        # Set up user message
        code_browser = get_code_browser()
        self.user_msg = user_msg.format(
            codebase_structure=code_browser.get_codebase_structure(),
            diff='\n'.join(code_browser.get_diff()),
            bin_path=self.bin_path,
        )

    @override
    def run_p(self, user_msg: Optional[str] = None) -> None:
        super().run_p(user_msg)
        print_and_write_to_file(f'\n\n{"Shared Context":=^80}\n{str(self.context)}')

    @override
    async def run_streamed_p(self, user_msg: Optional[str] = None) -> None:
        await super().run_streamed_p(user_msg)
        print_and_write_to_file(f'\n\n{"Shared Context":=^80}\n{str(self.context)}')

    @override
    async def run_interactive(self, user_msg: Optional[str] = None) -> None:
        await super().run_interactive(user_msg)
        print_and_write_to_file(f'\n\n{"Shared Context":=^80}\n{str(self.context)}')
