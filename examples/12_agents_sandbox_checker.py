"""HTB Challenge Agent example for checker."""

import asyncio
from dotenv import load_dotenv

from ivexes.agents import HTBChallengeAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging()

settings = PartialSettings(
    log_level='INFO',
    trace_name='bincrypt_breaker',
    model='openai/gpt-4.1-mini',
    model_temperature=0.2,
    max_turns=25,
    setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/bincrypt_breaker/upload.tgz',
)

agent = HTBChallengeAgent(
    program='checker',
    challenge='Crack the Code, Unlock the File: Dive into a C-based encryption puzzle, reverse-engineer the encrypted binary, and uncover the original executable. Can you break the cipher and execute the hidden file?',
    settings=settings,
)


if __name__ == '__main__':
    asyncio.run(agent.run_interactive())
