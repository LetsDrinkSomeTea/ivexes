import asyncio
from typing import cast
from agents import Agent, Runner, TResponseInputItem, Tool, trace, MaxTurnsExceeded

import dotenv

dotenv.load_dotenv('thesis/60_single_agent_screen.env', override=True)

settings = get_settings()
from ivexes.printer.printer import stream_result
from ivexes.prompts.single_agent import system_msg, user_msg
from ivexes.config.settings import get_settings, get_run_config
from ivexes.sandbox.tools import sandbox_tools
from ivexes.code_browser import code_browser_tools, code_browser
from ivexes.vector_db.tools import vectordb_tools

user_msg = user_msg.format(
    codebase_structure=code_browser.get_codebase_structure(),
    diff=code_browser.get_diff(),
    bin_path='/usr/bin/screen',
)

tools: list[Tool] = cast(
    list[Tool], sandbox_tools + code_browser_tools + vectordb_tools
)
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
    asyncio.run(main(user_msg, agent))
