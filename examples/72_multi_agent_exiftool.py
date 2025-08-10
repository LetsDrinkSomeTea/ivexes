"""Multi-agent example for screen vulnerability analysis."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging('WARNING')

settings = PartialSettings(
    trace_name='Multi-Agent Exiftool',
    # model='anthropic/claude-sonnet-4-20250514',
    model='openai/gpt-4.1',
    reasoning_model='openai/o4-mini',
    model_temperature=0.1,
    max_turns=50,
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct',
    codebase_path='testdata/exiftool/codebase',
    vulnerable_folder='exiftool-12.23',
    patched_folder='exiftool-12.24',
    sandbox_image='vuln-exiftool:latest',
)

agent = MultiAgent(settings=settings)

if __name__ == '__main__':
    asyncio.run(agent.run_interactive())
