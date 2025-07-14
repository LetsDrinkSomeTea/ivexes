"""HTB Challenge Agent example for behindthescenes."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import HTBChallengeAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging()

settings = PartialSettings(
    trace_name='behindthescenes',
    model='openai/gpt-4.1-mini',
    model_temperature=0.1,
    max_turns=25,
    setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/behind_the_scenes/upload.tgz',
)

agent = HTBChallengeAgent(
    program='behindthescenes',
    challenge='After struggling to secure our secret strings for a long time, we finally figured out the solution to our problem: Make decompilation harder. It should now be impossible to figure out how our programs work!',
    settings=settings,
)


if __name__ == '__main__':
    asyncio.run(agent.run_interactive())
