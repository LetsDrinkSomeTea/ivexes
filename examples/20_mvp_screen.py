"""MVP Agent example for screen vulnerability analysis."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import MVPAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging()

settings = PartialSettings(
    trace_name='screen',
    model='anthropic/claude-sonnet-4-20250514',
    model_temperature=0.1,
    max_turns=50,
    embedding_model='text-embedding-3-large',
    embedding_provider='openai',
    setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/screen_mvp/upload.tgz',
)

agent = MVPAgent(
    vulnerable_version='vulnerable-screen-4.5.0',
    patched_version='patched-screen-4.5.1',
    settings=settings,
)


if __name__ == '__main__':
    asyncio.run(agent.run_interactive())
