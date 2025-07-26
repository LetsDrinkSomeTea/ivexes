"""HTB Challenge Agent example for spookypass."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import HTBChallengeAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging('DEBUG')

settings = PartialSettings(
    trace_name='pass',
    model='openai/gpt-4.1-mini',
    model_temperature=0.1,
    max_turns=25,
    setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/htb_pass/upload.tgz',
)

agent = HTBChallengeAgent(
    program='pass',
    challenge='All the coolest ghosts in town are going to a Haunted Houseparty - can you prove you deserve to get in?',
    settings=settings,
)


agent.run()
