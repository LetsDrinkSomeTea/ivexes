"""Single agent vulnerability analysis example."""

import asyncio
from agents import Agent, Runner

from ivexes.config import create_settings, get_run_config
from ivexes.code_browser import CodeBrowser
from ivexes.date import current_date
from ivexes.printer import stream_result

from ivexes.tools import (
    create_sandbox_tools,
    create_vectordb_tools,
    create_code_browser_tools,
    cve_tools,
)
from ivexes.prompts.single_agent import system_msg, user_msg

settings = create_settings(
    {
        'codebase_path': 'testdata/screen',
        'vulnerable_folder': 'vuln-screen',
        'patched_folder': 'patched-screen',
        'setup_archive': 'testdata/screen/upload.tgz',
        'embedding_model': 'text-embedding-3-large',
        'embedding_provider': 'openai',
    }
)

code_browser = CodeBrowser(settings)

tools = (
    create_sandbox_tools(settings)
    + create_vectordb_tools()
    + create_code_browser_tools(code_browser)
    + cve_tools
)

user_msg = user_msg.format(
    codebase_structure=code_browser.get_codebase_structure(),
    diff=code_browser.get_diff(),
    bin_path='/usr/bin/screen',
    datetime=current_date(),
)

agent = Agent(
    name='Exploiter',
    instructions=system_msg,
    tools=tools,
)


async def main(user_msg, agent):
    """Run the single agent with streaming output."""
    result = Runner.run_streamed(
        agent,
        user_msg,
        run_config=get_run_config(),
        max_turns=settings.max_turns,
    )
    await stream_result(result)


if __name__ == '__main__':
    asyncio.run(main(user_msg, agent))
