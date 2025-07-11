import asyncio
from dotenv import load_dotenv
from typing import cast
from agents import Agent, MaxTurnsExceeded, Runner, TResponseInputItem, Tool, trace

from ivexes.config import get_run_config, get_settings
from ivexes.printer import stream_result, print_banner
from ivexes.tools import sandbox_tools
from ivexes.prompts.htb_reversing import system_msg, user_msg

load_dotenv(verbose=True, override=True)
load_dotenv(verbose=True, dotenv_path='../.secrets.env', override=True)

settings = get_settings()
print(settings)
print_banner()

user_msg = user_msg.format(
    program='pass',
    challenge='All the coolest ghosts in town are going to a Haunted Houseparty - can you prove you deserve to get in?',
)

tools = cast(list[Tool], sandbox_tools)
agent = Agent(name='Exploiter', instructions=system_msg, tools=tools)


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
