import asyncio
from typing import cast
from agents import Agent, Runner, TResponseInputItem, Tool, trace, MaxTurnsExceeded

import dotenv
dotenv.load_dotenv('thesis/20_mvp_screen.env', override=True)
from ivexes.config.run import get_config
from ivexes.modules.printer.printer import stream_result
from ivexes.prompts.mvp import system_msg, user_msg
from ivexes.config.settings import settings
from ivexes.modules.sandbox.tools import sandbox_tools

user_msg = user_msg.format(
    vulnerable_version=settings.vulnerable_folder,
    patched_version=settings.patched_folder
)

tools: list[Tool] = cast(list[Tool], sandbox_tools)
agent = Agent(
    name="Exploiter",
    instructions=system_msg,
    model=settings.model,
    tools=tools,

)

async def main(user_msg, agent):
    with trace(f"IVExES (Single Agent Sandbox ({settings.trace_name}))"):
        input_items: list[TResponseInputItem] = []
        while user_msg not in ['exit', 'quit', 'q']:
            input_items.append({'content': user_msg, 'role': 'user'})
            try:
                result = Runner.run_streamed(agent, input_items, run_config=get_config(), max_turns=settings.max_turns)
                input_items = await stream_result(result)
            except MaxTurnsExceeded as e:
                print(f"MaxTurnsExceeded: {e}")
            user_msg = input("User: ")

if __name__ == "__main__":
    asyncio.run(main(user_msg, agent))
