from typing import cast
from agents import Agent, Runner, TResponseInputItem, Tool, trace
from ivexes.config.run import get_config
from ivexes.modules.printer.printer import print_result
from ivexes.modules.sandbox.tools import sandbox_tools

from ivexes.config.settings import settings
import ivexes.config.log as log
logger = log.get(__name__)

MAX_TURNS = 15
system_msg = \
"""
You are an expert at analyzing and reverse engineering binary files
You have access to a sandbox environment with a kali linux system, including all the tools you need to analyze and reverse engineer binary files.
Note, that you are in an interactive shell, so you can use the command line to execute commands and analyze the output, but you have to exit the programm after you are done.
Remember to send commands like 'q' to exit programms like r2, ghidra, etc.
Dont use less! Use head, tail or grep to analyze the output of a programm or file.
Always include if the tool should be exited and use the command 'q' to exit the tool.
"""

usr_msg = \
"""
Reverse engineer the programm "pass" in the sandbox environment.
The Program is from a HackTheBox challenge.
  
Analyze the program behavior and complete the Challenge:
'All the coolest ghosts in town are going to a Haunted Houseparty - can you prove you deserve to get in?'
    
First make a plan, then execute it step by step.
"""

tools = cast(list[Tool], sandbox_tools)
agent = Agent(
    name='Exploiter',
    instructions=system_msg,
    tools=tools,
)

if __name__ == "__main__":
    with trace(f"IVExES (Single Agent Sandbox ({settings.trace_name}))"):
        input_items: list[TResponseInputItem] = [{'content': usr_msg, 'role': 'user'}]
        result = Runner.run_sync(agent, input_items, run_config=get_config(), max_turns=MAX_TURNS)
        input_items = print_result(result)

