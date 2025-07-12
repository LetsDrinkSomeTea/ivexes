"""Multi-agent example for screen vulnerability analysis."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging()

settings = PartialSettings(
    log_level='INFO',
    trace_name='Multi-Agent Screen',
    model='openai/gpt-4.1-mini',
    reasoning_model='openai/o4-mini',
    model_temperature=0.1,
    max_turns=25,
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct',
    setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/screen/upload.tgz',
    codebase_path='/home/julian/Desktop/Bachelorarbeit/testdata/screen/codebase',
    vulnerable_folder='vulnerable-screen-4.5.0',
    patched_folder='patched-screen-4.5.1',
)

agent = MultiAgent(bin_path='/usr/bin/screen', settings=settings)


if __name__ == '__main__':
    asyncio.run(agent.run_interactive())
