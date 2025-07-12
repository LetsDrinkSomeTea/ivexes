"""Single agent example for enlightenment vulnerability analysis."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, dotenv_path='../.secrets.env', override=True)
setup_default_logging()

settings = PartialSettings(
    log_level='WARNING',
    trace_name='enlightenment',
    model='anthropic/claude-sonnet-4-20250514',
    model_temperature=0.1,
    max_turns=50,
    embedding_model='text-embedding-3-large',
    embedding_provider='openai',
    setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/screen/upload.tgz',
    codebase_path='/home/julian/Desktop/Bachelorarbeit/testdata/screen/codebase',
)

agent = SingleAgent(bin_path='/usr/bin/screen', settings=settings)


if __name__ == '__main__':
    asyncio.run(agent.run_interactive())
