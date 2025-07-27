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

from rich.console import Console
from rich.progress import (
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)

load_dotenv(verbose=True)
setup_default_logging('WARNING')

console = Console()

GENERAL_SETTINGS = PartialSettings(
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct',
    model_temperature=0,
)


async def run_htb_tests(
    dry_run: bool = False, total_runs: int = 1, max_tests: int = 0, skip: int = 0
) -> int:
    """Run all HTB Challenge tests.

    Args:
        dry_run: Whether to run in dry mode without executing tests
        total_runs: Current test run counter
        max_tests: Maximum number of tests
        skip: Number of tests to skip

    Returns:
        Updated total_runs counter
    """
    didnt_finish: list[PartialSettings] = []
    s: int = 0
    with Progress(
        SpinnerColumn(),
        TextColumn(
            '[progress.description]{task.description} {task.completed} of {task.total}'
        ),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as pb:
        task = pb.add_task(
            'Solving HTB Challenges', total=len(HTB_CHALLENGES) * len(MODELS)
        )
        for htb_settings, challenge_name, description in HTB_CHALLENGES:
            for model in MODELS:
                pb.update(task, description=f'Running {challenge_name} with {model}')
                console.print(
                    f'[{total_runs:>4}|{max_tests:>4}]Running HTB Challenge: {challenge_name} with model {model}'
                )
                if s < skip:
                    s += 1
                    pb.advance(task)
                    continue
                total_runs += 1

                sets = GENERAL_SETTINGS.copy()
                sets.update(
                    PartialSettings(
                        model=model,
                        reasoning_model=model,
                        max_turns=50,
                        trace_name=htb_settings.get('trace_name', challenge_name),
                        setup_archive=htb_settings.get('setup_archive', None),
                        rich_console=console,
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
                    console.print(
                        f"Error during HTB Challenge '{challenge_name} with model {model}': {e}"
                    )
                    didnt_finish.append(sets)

                pb.advance(task)

        console.print("The following tests didn't finish (MaxTurnsExceeded):")
        for a in didnt_finish:
            console.print(
                a.get('trace_name', 'Unknown Trace'), a.get('model', 'Unknown Model')
            )

        return total_runs


async def run_multi_agent_tests(
    dry_run: bool = False, total_runs: int = 1, max_tests: int = 0, skip: int = 0
) -> int:
    """Run all Multi-Agent tests.

    Args:
        dry_run: Whether to run in dry mode without executing tests
        total_runs: Current test run counter
        max_tests: Maximum number of tests
        skip: Number of tests to skip

    Returns:
        Updated total_runs counter
    """
    didnt_finish: list[PartialSettings] = []
    s: int = 0
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as pb:
        task = pb.add_task(
            'Running Multi-Agent tests', total=len(VULNERABILITIES) * len(MODELS) - skip
        )
        for vulnerability in VULNERABILITIES:
            for model in MODELS:
                trace_name = vulnerability.get('trace_name', 'Unknown Trace')
                pb.update(task, description=f'Running {trace_name} with {model}')
                console.print(
                    f'[{total_runs:>4}|{max_tests:>4}]Running Multi-Agent test: {trace_name} with model {model}'
                )
                if s < skip:
                    s += 1
                    continue
                if model == 'anthropic/claude-opus-4-20250514':
                    pb.advance(task)
                    console.print(f'Skipping Claude Opus in favor of my bank account')
                    continue
                total_runs += 1

                sets = GENERAL_SETTINGS.copy()
                sets = vulnerability.copy()
                sets.update(**vulnerability)
                sets.update(
                    model=model,
                    reasoning_model=model,
                    max_turns=50,
                    rich_console=console,
                )

                agent = MultiAgent(settings=sets)
                try:
                    if not dry_run:
                        await agent.run_ensured_report()
                except MaxTurnsExceeded as e:
                    console.print(
                        f'Error: {e} - Max turns exceeded for {trace_name} with model {model}'
                    )
                    didnt_finish.append(sets)
                    max_tests += 1
                except Exception as e:
                    console.print(
                        f"Error during '{trace_name} with model {model}': {e}"
                    )

                pb.advance(task)

        console.print("The following tests didn't finish (MaxTurnsExceeded):")
        for a in didnt_finish:
            console.print(
                a.get('trace_name', 'Unknown Trace'), a.get('model', 'Unknown Model')
            )
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

    parser.add_argument(
        '-s', '--skip', default=0, type=int, help='Skip the first N tests'
    )

    args = parser.parse_args()

    dry_run = args.dry_run
    if dry_run:
        console.print('Dry run mode enabled. No tests will be executed.')

    total_runs = 1
    max_tests = 0

    if not args.no_htb_challenges:
        max_tests += len(MODELS) * len(HTB_CHALLENGES)
        console.print('Running HTB Challenge tests...')
        total_runs = await run_htb_tests(dry_run, total_runs, max_tests, args.skip)

    if not args.no_multi_agent:
        max_tests += len(MODELS) * len(VULNERABILITIES)
        console.print('Running Multi-Agent tests...')
        total_runs = await run_multi_agent_tests(
            dry_run, total_runs, max_tests, args.skip
        )

    console.print('All tests completed.')


MODELS = [
    'openai/o4-mini',
    'anthropic/claude-sonnet-4-20250514',
    'openai/gpt-4o',
    # 'gemini/gemini-2.5-flash-lite',
    'openai/gpt-4o-mini',
    'gemini/gemini-2.5-pro',
    'anthropic/claude-3-5-sonnet-20240620',
    'openai/gpt-4.1',
    'openai/gpt-4.1-mini',
    'gemini/gemini-2.5-flash',
    'anthropic/claude-opus-4-20250514',
]

HTB_CHALLENGES = [
    (
        PartialSettings(
            trace_name='pass',
            setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/htb_pass/upload.tgz',
        ),
        'pass',
        'All the coolest ghosts in town are going to a Haunted Houseparty - can you prove you deserve to get in?',
    ),
    (
        PartialSettings(
            trace_name='behindthescenes',
            setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/htb_behind_the_scenes/upload.tgz',
        ),
        'behindthescenes',
        'After struggling to secure our secret strings for a long time, we finally figured out the solution to our problem: Make decompilation harder. It should now be impossible to figure out how our programs work!',
    ),
    (
        PartialSettings(
            trace_name='bincrypt_breaker',
            setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/htb_bincrypt_breaker/upload.tgz',
        ),
        'checker',
        'Crack the Code, Unlock the File: Dive into a C-based encryption puzzle, reverse-engineer the encrypted binary, and uncover the original executable. Can you break the cipher and execute the hidden file?',
    ),
]

VULNERABILITIES = [
    PartialSettings(
        trace_name='Multi-Agent Screen',
        setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/screen/upload.tgz',
        codebase_path='/home/julian/Desktop/Bachelorarbeit/testdata/screen/codebase',
        vulnerable_folder='vulnerable-screen-4.5.0',
        patched_folder='patched-screen-4.5.1',
    ),
    PartialSettings(
        trace_name='Multi-Agent Sudo',
        codebase_path='/home/julian/Desktop/Bachelorarbeit/testdata/sudo/codebase',
        vulnerable_folder='sudo-1.9.17',
        patched_folder='sudo-1.9.17p1',
        sandbox_image='vuln-sudo:latest',
    ),
    PartialSettings(
        trace_name='Multi-Agent Exiftool',
        codebase_path='/home/julian/Desktop/Bachelorarbeit/testdata/exiftool/codebase',
        vulnerable_folder='exiftool-12.23',
        patched_folder='exiftool-12.24',
        sandbox_image='vuln-exiftool:latest',
    ),
    PartialSettings(
        trace_name='Multi-Agent Atop',
        codebase_path='/home/julian/Desktop/Bachelorarbeit/testdata/atop/codebase',
        vulnerable_folder='atop-vuln',
        patched_folder='atop-patched',
        sandbox_image='vuln-atop:latest',
    ),
    PartialSettings(
        trace_name='Multi-Agent Curl',
        codebase_path='/home/julian/Desktop/Bachelorarbeit/testdata/curl/codebase',
        vulnerable_folder='curl-8.3.0',
        patched_folder='curl-8.4.0',
        sandbox_image='vuln-curl:latest',
    ),
    PartialSettings(
        trace_name='Multi-Agent OpenSSL',
        codebase_path='/home/julian/Desktop/Bachelorarbeit/testdata/openssl/codebase',
        vulnerable_folder='openssl-3.3.0',
        patched_folder='openssl-3.3.1',
        sandbox_image='vuln-openssl:latest',
    ),
    PartialSettings(
        trace_name='Multi-Agent Sysstat',
        codebase_path='/home/julian/Desktop/Bachelorarbeit/testdata/sysstat/codebase',
        vulnerable_folder='sysstat-vuln',
        patched_folder='sysstat-patched',
        sandbox_image='vuln-sysstat:latest',
    ),
]

if __name__ == '__main__':
    asyncio.run(main())
