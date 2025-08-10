"""Multi-agent example for screen vulnerability analysis."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging('WARNING')

settings = PartialSettings(
    trace_name='Multi-Agent Screen',
    model='openai/gpt-4.1-mini',
    reasoning_model='openai/o4-mini',
    model_temperature=0.1,
    max_turns=50,
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct',
    setup_archive='testdata/screen/upload.tgz',
    codebase_path='testdata/screen/codebase',
    vulnerable_folder='vulnerable-screen-4.5.0',
    patched_folder='patched-screen-4.5.1',
)

agent = MultiAgent(settings=settings)


async def main():
    """Run the multi-agent screen vulnerability analysis."""
    _, _ = await agent.run_ensured_report()


if __name__ == '__main__':
    asyncio.run(main())
