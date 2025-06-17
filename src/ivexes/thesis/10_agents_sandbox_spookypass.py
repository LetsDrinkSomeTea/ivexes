from typing import cast
from agents import Agent, Runner, TResponseInputItem, Tool, trace
import dotenv
dotenv.load_dotenv('thesis/10_agents_sandbox_spookypass.env', override=True)
from ivexes.config.run import get_config
from ivexes.modules.printer.printer import print_result
from ivexes.modules.sandbox.tools import sandbox_tools
from ivexes.prompts.htb_reversing import system_msg, user_msg
from ivexes.config.settings import settings

user_msg = user_msg.format(
    program="pass",
    challenge='All the coolest ghosts in town are going to a Haunted Houseparty - can you prove you deserve to get in?'
)

tools = cast(list[Tool], sandbox_tools)
agent = Agent(
    name='Exploiter',
    instructions=system_msg,
    tools=tools,
)

if __name__ == "__main__":
    with trace(f"IVExES (Single Agent Sandbox ({settings.trace_name}))"):
        input_items: list[TResponseInputItem] = [{'content': user_msg, 'role': 'user'}]
        result = Runner.run_sync(agent, input_items, run_config=get_config(), max_turns=settings.max_turns)
        input_items = print_result(result)

