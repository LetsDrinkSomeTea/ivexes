import dotenv

import asyncio
from agents import Agent, Runner, TResponseInputItem, trace, MaxTurnsExceeded

from ivexes import stream_result, get_run_config, get_settings, setup_default_logging
from ivexes.tools import code_browser_tools, date_tools, sandbox_tools, vectordb_tools
from ivexes.prompts.multi_agent import (
    security_specialist_system_msg,
    code_analyst_system_msg,
    red_team_operator_system_msg,
    report_journalist_system_msg,
    planning_system_msg,
    user_msg,
)
from ivexes.code_browser import get_code_browser

dotenv.load_dotenv(verbose=True, override=True)
dotenv.load_dotenv(verbose=True, dotenv_path='../.secrets.env', override=True)

settings = get_settings()
setup_default_logging(settings.log_level)

security_specialist_tool = Agent(
    name='Security Specialist',
    handoff_description='Specialist agent for up-to-date information on CWE, CAPEC and ATT&CK data',
    instructions=security_specialist_system_msg,
    tools=vectordb_tools,
).as_tool(
    tool_name='security-specialist',
    tool_description='Expert in CWE, CAPEC, and ATT&CK frameworks. Provides security vulnerability analysis, attack pattern identification, and mitigation strategies based on industry standards.',
)

code_analyst_tool = Agent(
    name='Code Analyst',
    handoff_description='Specialist agent for information about the codebase, including code structure, functions, diffs and classes',
    instructions=code_analyst_system_msg,
    tools=code_browser_tools,
).as_tool(
    tool_name='code-analyst',
    tool_description='Specialist for codebase analysis and vulnerability identification. Analyzes code structure, functions, classes, and diffs to identify potential security weaknesses.',
)

red_team_operator_tool = Agent(
    name='Red Team Operator',
    handoff_description='Specialist agent for generating Proof-of-Concepts (PoC) and Exploits',
    instructions=red_team_operator_system_msg,
    tools=sandbox_tools,
).as_tool(
    tool_name='red-team-operator',
    tool_description='Specialist for creating and testing Proof-of-Concept exploits. Develops bash/Python scripts, tests exploits in sandbox, and validates exploitation techniques.',
)

report_journalist_agent = Agent(
    name='Report Journalist',
    handoff_description='Specialist agent for generating reports and summaries',
    instructions=report_journalist_system_msg,
    tools=date_tools,
)

planning_agent = Agent(
    name='Planning Agent',
    handoff_description='Specialist agent for planning and coordinating the actions of other agents',
    instructions=planning_system_msg,
    model=settings.reasoning_model,
    tools=[security_specialist_tool, code_analyst_tool, red_team_operator_tool],
    handoffs=[report_journalist_agent],
)

code_browser = get_code_browser()
user_msg = user_msg.format(
    codebase_structure=code_browser.get_codebase_structure(),
    diff='\n'.join(code_browser.get_diff()),
    bin_path='/usr/bin/screen',
)


async def main(user_msg, agent):
    with trace(f'IVExES (Multi Agent ({settings.trace_name}))'):
        input_items: list[TResponseInputItem] = []
        while user_msg not in ['exit', 'quit', 'q']:
            input_items.append({'content': user_msg, 'role': 'user'})
            try:
                result = Runner.run_streamed(
                    starting_agent=agent,
                    input=input_items,
                    run_config=get_run_config(),
                    max_turns=settings.max_turns,
                )
                input_items = await stream_result(result)
            except MaxTurnsExceeded as e:
                print(f'MaxTurnsExceeded: {e}')
            user_msg = input('User: ')


if __name__ == '__main__':
    asyncio.run(main(user_msg, planning_agent))
