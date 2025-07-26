"""Main script to run all tests for HTB Challenges and Multi-Agent vulnerabilities.

This script executes tests for HTB challenges and Multi-Agent vulnerabilities using various models.
It handles exceptions, cleans up resources, and prints the results of each test run.
"""

import asyncio
import argparse

from dotenv import load_dotenv

from agents.exceptions import MaxTurnsExceeded

from ivexes.agents import HTBChallengeAgent, MultiAgent
from ivexes.config import PartialSettings, setup_default_logging, reset_settings
from ivexes.container import cleanup

from testdata import HTB_CHALLENGES, VULNERABILITIES, MODELS

load_dotenv(verbose=True)
setup_default_logging()

total_runs: int = 1
dry_run = False

GENERAL_SETTINGS = PartialSettings(
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct',
    model_temperature=0,
)

# FIXME: During testing, we limit the number of challenges and vulnerabilities to speed up the process.
HTB_CHALLENGES = HTB_CHALLENGES[:1]  # Limit to one challenge for testing
VULNERABILITIES = VULNERABILITIES[:1]  # Limit to one vulnerability for testing
MODELS = [  # Limit to two models for testing
    'openai/gpt-4.1-mini',
    'openai/gpt-4o-mini',
]
# FIXME: Remove the above limits for full testing

max_tests = len(MODELS) * (len(HTB_CHALLENGES) + len(VULNERABILITIES))


async def run_htb_tests():
    """Run all HTB Challenge tests."""
    global total_runs
    global try_run
    global max_tests
    for model in MODELS:
        for htb_settings, challenge_name, description in HTB_CHALLENGES:
            print(
                f'[{total_runs:>4}|{max_tests:>4}]Running HTB Challenge: {challenge_name} with model {model}'
            )
            total_runs += 1

            sets = PartialSettings(
                model=model,
                max_turns=25,
                embedding_provider='local',
                embedding_model='intfloat/multilingual-e5-large-instruct',
                model_temperature=0,
                trace_name=htb_settings.get('trace_name', challenge_name),
                setup_archive=htb_settings.get('setup_archive', None),
            )

            print(sets)

            agent = HTBChallengeAgent(
                program=challenge_name,
                challenge=description,
                settings=sets,
            )

            try:
                if not dry_run:
                    await agent.run_streamed_p()
            except Exception as e:
                print(
                    f"Error during HTB Challenge '{challenge_name} with model {model}': {e}"
                )
            finally:
                cleanup()


async def run_multi_agent_tests():
    """Run all Multi-Agent tests."""
    global total_runs
    global dry_run
    global max_tests
    need_more_turns: list[tuple[PartialSettings, str]] = []
    for vulnerability, bin_path in VULNERABILITIES:
        for model in MODELS:
            trace_name = vulnerability.get('trace_name', 'Unknown Trace')
            print(
                f'[{total_runs:>4}|{max_tests:>4}]Running Multi-Agent test: {trace_name} with model {model}'
            )
            total_runs += 1

            sets = vulnerability.copy()
            sets.update(
                model=model,
                max_turns=20,
            )
            if not dry_run:
                agent = MultiAgent(bin_path=bin_path, settings=sets)
                try:
                    await agent.run_ensured_report()
                except MaxTurnsExceeded as e:
                    print(
                        f'Error: {e} - Max turns exceeded for {trace_name} with model {model}'
                    )
                    need_more_turns.append((sets, bin_path))
                    max_tests += 1
                except Exception as e:
                    print(f"Error during '{trace_name} with model {model}': {e}")
                finally:
                    cleanup()

    for sets, bin_path in need_more_turns:
        trace_name = sets.get('trace_name', 'Unknown Trace')
        model = sets.get('model', 'Unknown Model')

        print(
            f'[{total_runs:>4}|{max_tests:>4}]Running Multi-Agent test: {trace_name} with model {model}'
        )
        total_runs += 1
        sets.update(max_turns=50)
        if not dry_run:
            agent = MultiAgent(bin_path=bin_path, settings=sets)
            try:
                await agent.run_ensured_report()
            except Exception as e:
                print(f"Error during '{trace_name} with model {model}': {e}")
            finally:
                cleanup()


async def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(
        'Run all tests for HTB Challenges and Multi-Agent vulnerabilities.'
    )
    # flag for htb Challenge tests
    parser.add_argument(
        '-c', '--no-htb-challenges', action='store_true', help='Run HTB Challenge tests'
    )
    # flag for Multi-Agent tests
    parser.add_argument(
        '-m', '--no-multi-agent', action='store_true', help='Run Multi-Agent tests'
    )
    # dry run flag
    parser.add_argument(
        '-d', '--dry-run', action='store_true', help='Dry run without executing tests'
    )

    args = parser.parse_args()

    if args.dry_run:
        print('Dry run mode enabled. No tests will be executed.')
        global dry_run
        dry_run = True

    if not args.no_htb_challenges:
        print('Running HTB Challenge tests...')
        await run_htb_tests()

    if not args.no_multi_agent:
        print('Running Multi-Agent tests...')
        await run_multi_agent_tests()

    print('All tests completed.')


if __name__ == '__main__':
    asyncio.run(main())
