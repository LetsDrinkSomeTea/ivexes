"""Main script to run all tests for HTB Challenges and Multi-Agent vulnerabilities.

This script executes tests for HTB challenges and Multi-Agent vulnerabilities using various models.
It handles exceptions, cleans up resources, and prints the results of each test run.
"""

import asyncio
import argparse

from dotenv import load_dotenv

from agents.exceptions import MaxTurnsExceeded

from ivexes.agents import HTBChallengeAgent, MultiAgent
from ivexes.config import PartialSettings, setup_default_logging

from testdata import HTB_CHALLENGES, VULNERABILITIES, MODELS

load_dotenv(verbose=True)
setup_default_logging()


GENERAL_SETTINGS = PartialSettings(
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct',
    model_temperature=0,
)


async def run_htb_tests(
    dry_run: bool = False, total_runs: int = 1, max_tests: int = 0
) -> int:
    """Run all HTB Challenge tests.

    Args:
        dry_run: Whether to run in dry mode without executing tests
        total_runs: Current test run counter
        max_tests: Maximum number of tests

    Returns:
        Updated total_runs counter
    """
    for htb_settings, challenge_name, description in HTB_CHALLENGES:
        for model in MODELS:
            print(
                f'[{total_runs:>4}|{max_tests:>4}]Running HTB Challenge: {challenge_name} with model {model}'
            )
            total_runs += 1

            sets = GENERAL_SETTINGS.copy()
            sets.update(
                PartialSettings(
                    model=model,
                    reasoning_model=model,
                    max_turns=25,
                    trace_name=htb_settings.get('trace_name', challenge_name),
                    setup_archive=htb_settings.get('setup_archive', None),
                )
            )

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
                pass  # Each agent cleans up its own containers

    return total_runs


async def run_multi_agent_tests(
    dry_run: bool = False, total_runs: int = 1, max_tests: int = 0
) -> int:
    """Run all Multi-Agent tests.

    Args:
        dry_run: Whether to run in dry mode without executing tests
        total_runs: Current test run counter
        max_tests: Maximum number of tests

    Returns:
        Updated total_runs counter
    """
    didnt_finish: list[PartialSettings] = []
    for vulnerability in VULNERABILITIES:
        for model in MODELS:
            trace_name = vulnerability.get('trace_name', 'Unknown Trace')
            print(
                f'[{total_runs:>4}|{max_tests:>4}]Running Multi-Agent test: {trace_name} with model {model}'
            )
            total_runs += 1

            sets = GENERAL_SETTINGS.copy()
            sets = vulnerability.copy()
            sets.update(**vulnerability)
            sets.update(
                model=model,
                reasoning_model=model,
                max_turns=50,
            )

            agent = MultiAgent(settings=sets)
            try:
                if not dry_run:
                    await agent.run_ensured_report()
            except MaxTurnsExceeded as e:
                print(
                    f'Error: {e} - Max turns exceeded for {trace_name} with model {model}'
                )
                didnt_finish.append((sets))
                max_tests += 1
            except Exception as e:
                print(f"Error during '{trace_name} with model {model}': {e}")

    print("The following tests didn't finish (MaxTurnsExceeded):")
    for a in didnt_finish:
        print(a.get('trace_name', 'Unknown Trace'), a.get('model', 'Unknown Model'))
    return total_runs


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

    dry_run = args.dry_run
    if dry_run:
        print('Dry run mode enabled. No tests will be executed.')

    total_runs = 1
    max_tests = len(MODELS) * (len(HTB_CHALLENGES) + len(VULNERABILITIES))

    if not args.no_htb_challenges:
        print('Running HTB Challenge tests...')
        total_runs = await run_htb_tests(dry_run, total_runs, max_tests)

    if not args.no_multi_agent:
        print('Running Multi-Agent tests...')
        total_runs = await run_multi_agent_tests(dry_run, total_runs, max_tests)

    print('All tests completed.')


if __name__ == '__main__':
    asyncio.run(main())
