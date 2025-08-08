"""Token Estimation Tool for IVEXES Output Files.

This module provides token estimation functionality for analyzing output files in the output/ directory.
It excludes reports/ and */openai/ folders and uses a progressive formula per agent:
    estimated_tokens = Σ(first_part * total_parts + second_part * (total_parts - 1) + ... + last_part * 1)

Where content is split by agent boundaries and each agent's sections are weighted progressively,
reflecting cumulative context buildup in multi-agent conversations.
"""

import os
import re
import csv
from pathlib import Path
from typing import Tuple, List, Dict, Optional
from ivexes.token import get_text_statistics


def parse_agent_sections(file_path: str) -> Dict[str, List[int]]:
    """Parse agent sections from file and return token counts per agent.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Dictionary mapping agent names to lists of their section token counts
        Format: {'agent_name': [section1_tokens, section2_tokens, ...]}
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Split content by agent boundaries
        # Pattern matches: [N]===============================Agent (AgentName)================================
        agent_pattern = r'\[\d+\]===============================Agent \(([^)]+)\)================================'

        # Find all agent boundaries with their names and positions
        agent_matches = list(re.finditer(agent_pattern, content))

        if not agent_matches:
            # No agent sections found, treat entire content as single section
            token_count, _, _ = get_text_statistics(content)
            return {'unknown': [token_count]}

        agent_sections = {}

        for i, match in enumerate(agent_matches):
            agent_name = match.group(1)  # Extract agent name from parentheses
            start_pos = match.end()  # Start after the agent header

            # Find end position (start of next agent or end of file)
            if i + 1 < len(agent_matches):
                end_pos = agent_matches[i + 1].start()
            else:
                end_pos = len(content)

            # Extract section content
            section_content = content[start_pos:end_pos]

            # Count tokens in this section
            section_tokens, _, _ = get_text_statistics(section_content)

            # Add to agent sections
            if agent_name not in agent_sections:
                agent_sections[agent_name] = []
            agent_sections[agent_name].append(section_tokens)

        return agent_sections

    except Exception as e:
        print(f'Error reading {file_path}: {e}')
        return {}


def calculate_progressive_tokens(
    agent_sections: Dict[str, List[int]],
) -> Tuple[float, Dict[str, float]]:
    """Calculate progressive token estimation using the new formula.

    For each agent, applies: first_part * total_parts + second_part * (total_parts - 1) + ... + last_part * 1

    Args:
        agent_sections: Dictionary mapping agent names to lists of section token counts

    Returns:
        Tuple of (total_estimated_tokens, per_agent_breakdown)
    """
    total_estimated = 0.0
    agent_breakdown = {}

    for agent_name, section_tokens in agent_sections.items():
        if not section_tokens:
            agent_breakdown[agent_name] = 0.0
            continue

        agent_total = 0.0
        total_parts = len(section_tokens)

        # Apply progressive formula: section_tokens[i] * (total_parts - i)
        for i, tokens in enumerate(section_tokens):
            multiplier = total_parts - i  # total_parts, total_parts-1, ..., 1
            agent_total += tokens * multiplier

        agent_breakdown[agent_name] = agent_total
        total_estimated += agent_total

    return total_estimated, agent_breakdown


def find_output_files(output_dir: str) -> List[str]:
    """Find all .txt files in output directory excluding reports/ and */openai/ folders.

    Args:
        output_dir: Path to the output directory

    Returns:
        List of file paths to analyze
    """
    output_path = Path(output_dir)

    if not output_path.exists():
        print(f'Output directory {output_dir} does not exist')
        return []

    files = []

    # Find all .txt files in output directory
    for txt_file in output_path.glob('**/*.txt'):
        # Skip files in reports/ directory
        if 'reports' in txt_file.parts:
            continue

        # Skip files in */openai/ directories
        if any('openai' in part for part in txt_file.parts):
            continue

        files.append(str(txt_file))

    return sorted(files)


def estimate_output_tokens(output_dir: Optional[str] = None) -> Dict:
    """Main function to estimate tokens for all valid output files.

    Args:
        output_dir: Path to output directory. If None, uses project_root/output

    Returns:
        Dictionary with estimation results and statistics
    """
    if output_dir is None:
        # Get the project root directory (assuming this is called from tools/)
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        output_dir = project_root / 'output'

    output_dir = str(output_dir)

    # Find all files to process
    files = find_output_files(output_dir)

    if not files:
        return {
            'error': 'No files found to process',
            'files_processed': 0,
            'total_tokens': 0,
            'results': [],
        }

    total_estimated_tokens = 0
    results = []

    # Process each file
    for file_path in files:
        rel_path = Path(file_path).relative_to(output_dir)
        agent_sections = parse_agent_sections(file_path)
        estimated_tokens, agent_breakdown = calculate_progressive_tokens(agent_sections)

        total_estimated_tokens += estimated_tokens

        # Calculate total base tokens for display
        total_base_tokens = sum(sum(sections) for sections in agent_sections.values())
        total_agent_sections = sum(
            len(sections) for sections in agent_sections.values()
        )

        result = {
            'file': str(rel_path),
            'tokens_base': total_base_tokens,
            'agents': total_agent_sections,
            'tokens': estimated_tokens,
            'agent_breakdown': agent_breakdown,
            'agent_sections': agent_sections,
        }
        results.append(result)

    # Group by provider
    providers = {}
    for result in results:
        parts = result['file'].split('/')
        if len(parts) >= 2:
            provider = parts[1]  # anthropic, gemini, openai (but openai is excluded)
            if provider not in providers:
                providers[provider] = {'files': 0, 'tokens': 0}
            providers[provider]['files'] += 1
            providers[provider]['tokens'] += result['tokens']

    # Group by challenge/test
    challenges = {}
    for result in results:
        challenge = result['file'].split('/')[0]
        if challenge not in challenges:
            challenges[challenge] = {'files': 0, 'tokens': 0}
        challenges[challenge]['files'] += 1
        challenges[challenge]['tokens'] += result['tokens']

    return {
        'files_processed': len(files),
        'total_tokens': total_estimated_tokens,
        'results': results,
        'by_provider': providers,
        'by_challenge': challenges,
        'output_dir': output_dir,
    }


def print_estimation_results(estimation_data: Dict) -> None:
    """Print token estimation results in a formatted way.

    Args:
        estimation_data: Results from estimate_output_tokens()
    """
    if 'error' in estimation_data:
        print(f'Error: {estimation_data["error"]}')
        return

    print('IVEXES Token Estimation Tool')
    print('=' * 50)
    print(f'Analyzing files in: {estimation_data["output_dir"]}')
    print(f'Progressive Formula: Σ(part1 * n + part2 * (n-1) + ... + partN * 1)')
    print(f'Where parts are agent sections and n=total_sections_per_agent')
    print('=' * 50)
    print(f'Found {estimation_data["files_processed"]} files to analyze\n')

    # Print individual results
    for result in estimation_data['results']:
        print(
            f'{result["file"]:60} | Tokens: {result["tokens_base"]:8,} | Agents: {result["agents"]:3} | Estimated: {result["tokens"]:10,.1f}'
        )

    # Print summary
    print('\n' + '=' * 50)
    print('SUMMARY')
    print('=' * 50)
    print(f'Total files processed: {estimation_data["files_processed"]}')
    print(f'Total estimated tokens: {estimation_data["total_tokens"]:,.1f}')

    # Print provider breakdown
    print(f'\nBy Provider:')
    for provider, stats in sorted(estimation_data['by_provider'].items()):
        print(
            f'  {provider:10}: {stats["files"]:3} files, {stats["tokens"]:10,.1f} tokens'
        )

    # Print challenge breakdown
    print(f'\nBy Challenge/Test:')
    for challenge, stats in sorted(estimation_data['by_challenge'].items()):
        print(
            f'  {challenge:20}: {stats["files"]:3} files, {stats["tokens"]:10,.1f} tokens'
        )


def export_to_csv(estimation_data: Dict, csv_path: str) -> None:
    """Export token estimation results to CSV format with provider/model, challenge, and tokens.

    Args:
        estimation_data: Results from estimate_output_tokens()
        csv_path: Path where to save the CSV file
    """
    if 'error' in estimation_data:
        print(f'Error: Cannot export - {estimation_data["error"]}')
        return

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['provider_model', 'challenge', 'tokens']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for result in estimation_data['results']:
            # Parse provider/model and challenge from file path
            # Format: challenge/provider/model-timestamp.txt
            file_parts = result['file'].split('/')
            challenge = file_parts[0] if len(file_parts) >= 1 else 'unknown'

            if len(file_parts) >= 3:
                provider = file_parts[1]  # anthropic, gemini, etc.
                model_file: str = file_parts[2]  # model-timestamp.txt
                model = model_file.rsplit('-', maxsplit=1)[0].split('/', maxsplit=1)[
                    -1
                ]  # remove -time.txt extension
                provider_model = f'{provider}/{model}'
            else:
                provider_model = 'unknown'

            writer.writerow(
                {
                    'provider_model': provider_model,
                    'challenge': challenge,
                    'tokens': f'{result["tokens"]:.0f}',
                }
            )

    print(f'Results exported to {csv_path}')


if __name__ == '__main__':
    """Allow running as standalone script for backwards compatibility."""
    import sys

    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = None

    results = estimate_output_tokens(output_dir)
    print_estimation_results(results)
