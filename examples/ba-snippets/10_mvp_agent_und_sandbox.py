"""MVP Agent with Sandbox."""

from agents import Agent, Runner
from ivexes.config import get_run_config
from ivexes.prompts.htb_reversing import system_msg, user_msg
from ivexes.tools import create_sandbox_tools

user_msg = user_msg.format(
    program='pass',
    challenge='All the coolest ghosts in town are going to a Haunted Houseparty - can you prove you deserve to get in?',
)

agent = Agent(
    name='Agent',
    instructions=system_msg,
    tools=create_sandbox_tools(),
)

result = Runner.run_sync(
    agent,
    user_msg,
    run_config=get_run_config(),
)

print(result)
