import asyncio
from typing import cast

from ivexes.config.settings import settings, get_run_config
from ivexes.modules.printer.printer import stream_result

from ivexes.modules.sandbox.tools import sandbox_tools
from ivexes.modules.vector_db.tools import vectordb_tools
from ivexes.modules.code_browser.tools import code_browser_tools

from agents import Agent, Runner, TResponseInputItem, Tool, trace, MaxTurnsExceeded

import ivexes.config.log

logger = ivexes.config.log.get(__name__)

tools: list[Tool] = cast(
    list[Tool], sandbox_tools + vectordb_tools + code_browser_tools
)

system_msg = """
You are an expert at analyzing codebases and finding vulnerabilities.
You are also an expert at generating proof of concept (PoC) exploits for the vulnerabilities you find.

You are given a diff of a codebase. The diff shows the changes made to the codebase.
Your task is to analyze the diff and find the vulnerability and create a PoC exploit for it.

Do not halucinate or make up any information.
Query the tools you need to find the information you need.

You have access to the following tools:
- `sandbox`: A Kali Linux sandbox environment where you can run commands and test your exploits. The vulnerable version is installed in the sandbox.
- `code_browser`: A tool to browse the codebase and find the relevant files and functions.
- `cwe_capec`: A tool to query the CWE and CAPEC databases for vulnerabilities and exploits.
The tools are different containerized environments.

Dont stop until you a working PoC exploit and verified it in the sandbox.
Always create a file in the sandbox with the PoC exploit, preferably in bash or python.
The vulnerable version is installed in the sandbox.
"""

agent = Agent(
    name='Exploiter', instructions=system_msg, model=settings.model, tools=tools
)


async def main(user_msg, agent):
    with trace(f'IVExES (Single Agent Sandbox ({settings.trace_name}))'):
        input_items: list[TResponseInputItem] = []
        while user_msg not in ['exit', 'quit', 'q']:
            input_items.append({'content': user_msg, 'role': 'user'})
            try:
                result = Runner.run_streamed(
                    agent,
                    input_items,
                    run_config=get_run_config(),
                    max_turns=settings.max_turns,
                )
                input_items = await stream_result(result)
            except MaxTurnsExceeded as e:
                print(f'MaxTurnsExceeded: {e}')
            user_msg = input('User: ')


if __name__ == '__main__':
    from ivexes.modules.code_browser.tools import code_browser

    user_msg = f"""
{code_browser.get_diff()}
"""
    asyncio.run(main(user_msg, agent))
