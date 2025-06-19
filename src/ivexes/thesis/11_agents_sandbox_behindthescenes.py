import asyncio
from typing import cast
from agents import Agent, MaxTurnsExceeded, Runner, TResponseInputItem, Tool, trace
import dotenv
dotenv.load_dotenv('thesis/11_agents_sandbox_behindthescenes.env', override=True)
from ivexes.config.run import get_config
from ivexes.modules.printer.printer import stream_result
from ivexes.modules.sandbox.tools import sandbox_tools
from ivexes.prompts.htb_reversing import system_msg, user_msg
from ivexes.config.settings import settings

user_msg = user_msg.format(
    program='behindthescenes',
    challenge='After struggling to secure our secret strings for a long time, we finally figured out the solution to our problem: Make decompilation harder. It should now be impossible to figure out how our programs work!'
)

tools = cast(list[Tool], sandbox_tools)
agent = Agent(
    name='Exploiter',
    instructions=system_msg,
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
