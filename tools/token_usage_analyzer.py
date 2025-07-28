#!/usr/bin/env python3
"""Token Usage Analyzer for IVEXES Output Files.

This script analyzes token usage data from IVEXES multi-agent system output files
and calculates median usage statistics per agent type and subfolder.

Usage: python tools/token_usage_analyzer.py output/
"""

import re
import sys
from collections import defaultdict
import statistics
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import track
except ImportError:
    print('Error: Rich library is required. Install with: pip install rich')
    sys.exit(1)

console = Console()


def parse_token_data(file_path):
    """Parse token usage data from a single file.

    Returns dict with either:
    - For multi-agent: {'agents': {agent_name -> total_tokens}, 'total': sum}
    - For single-agent: {'total': total_tokens}
    - None if no valid data found
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        console.print(f'[red]Error reading {file_path}: {e}[/red]')
        return None

    # First try to find agent breakdown (multi-agent format)
    # ├─ code-analyst: 38,715 input + 660 output = 39,375 total tokens (4 requests)
    # └─ planning-agent: 34,819 input + 1,202 output = 36,021 total tokens (15 requests)
    agent_pattern = r'[├└]─\s+([a-z-]+):\s+[\d,]+\s+input\s+\+\s+[\d,]+\s+output\s+=\s+([\d,]+)\s+total\s+tokens'
    agent_matches = re.findall(agent_pattern, content)

    if agent_matches:
        # Multi-agent format
        agents_data = {}
        total_tokens = 0
        for agent_name, total_tokens_str in agent_matches:
            tokens = int(total_tokens_str.replace(',', ''))
            if tokens > 0:  # Skip zero token entries
                agents_data[agent_name] = tokens
                total_tokens += tokens

        if agents_data:
            return {'agents': agents_data, 'total': total_tokens}

    # If no agent breakdown found, look for single total
    # Total tokens used: 201,581 input + 6,403 output = 207,984 total tokens (60 requests)
    # Token usage: 0 input + 0 output = 0 total tokens (0 requests)
    total_patterns = [
        r'Total tokens used:\s+[\d,]+\s+input\s+\+\s+[\d,]+\s+output\s+=\s+([\d,]+)\s+total\s+tokens',
        r'Token usage:\s+[\d,]+\s+input\s+\+\s+[\d,]+\s+output\s+=\s+([\d,]+)\s+total\s+tokens',
    ]

    total_matches = []
    for pattern in total_patterns:
        matches = re.findall(pattern, content)
        total_matches.extend(matches)

    if total_matches:
        # Take the last (most recent) total in the file
        total_tokens = int(total_matches[-1].replace(',', ''))
        if total_tokens > 0:
            return {'total': total_tokens}

    return None


def analyze_folder(output_folder):
    """Analyze all .txt files in output folder subfolders.

    Returns nested dict: subfolder -> {'multi_agent': {agent_type -> [token_counts]}, 'single_agent': [totals], 'all_totals': [totals]}
    """
    output_path = Path(output_folder)
    if not output_path.exists():
        console.print(f'[red]Error: Folder {output_folder} does not exist[/red]')
        return None

    # Data structure: subfolder -> analysis data
    subfolder_data = defaultdict(
        lambda: {
            'multi_agent': defaultdict(list),  # agent_type -> [token_counts]
            'single_agent': [],  # [total_tokens] for single-agent runs
            'all_totals': [],  # [total_tokens] for all runs
        }
    )

    # Find all .txt files, excluding reports folder
    txt_files = []
    for subfolder in output_path.iterdir():
        if subfolder.is_dir() and subfolder.name != 'reports':
            for txt_file in subfolder.rglob('*.txt'):
                txt_files.append((subfolder.name, txt_file))

    console.print(f'Found {len(txt_files)} files to analyze...')

    # Process files with progress bar
    for subfolder_name, file_path in track(txt_files, description='Parsing files...'):
        token_data = parse_token_data(file_path)
        if token_data:
            if 'agents' in token_data:
                # Multi-agent format
                for agent_name, token_count in token_data['agents'].items():
                    subfolder_data[subfolder_name]['multi_agent'][agent_name].append(
                        token_count
                    )
                subfolder_data[subfolder_name]['all_totals'].append(token_data['total'])
            else:
                # Single-agent format
                subfolder_data[subfolder_name]['single_agent'].append(
                    token_data['total']
                )
                subfolder_data[subfolder_name]['all_totals'].append(token_data['total'])

    return dict(subfolder_data)


def calculate_medians(subfolder_data):
    """Calculate overall medians across all subfolders for each agent type."""
    overall_data = defaultdict(list)

    for subfolder, data in subfolder_data.items():
        for agent_name, token_counts in data['multi_agent'].items():
            overall_data[agent_name].extend(token_counts)

    medians = {}
    for agent_name, token_counts in overall_data.items():
        if token_counts:
            medians[agent_name] = statistics.median(token_counts)

    return medians


def display_results(subfolder_data, overall_medians):
    """Display results using Rich formatting."""
    # Per-subfolder analysis
    console.print('\n[bold cyan]Per Subfolder Analysis[/bold cyan]')
    console.print('=' * 50)

    for subfolder_name in sorted(subfolder_data.keys()):
        data = subfolder_data[subfolder_name]
        multi_agent = data['multi_agent']
        single_agent = data['single_agent']
        all_totals = data['all_totals']

        table = Table(
            title=f'[bold]{subfolder_name}[/bold]',
            show_header=True,
            header_style='bold magenta',
        )
        table.add_column('Agent Type', style='cyan')
        table.add_column('Median Tokens', justify='right', style='green')
        table.add_column('File Count', justify='center', style='yellow')

        # Add multi-agent data
        for agent_name in sorted(multi_agent.keys()):
            token_counts = multi_agent[agent_name]
            median_tokens = statistics.median(token_counts)
            file_count = len(token_counts)

            table.add_row(agent_name, f'{median_tokens:,}', str(file_count))

        # Add single-agent data if present
        if single_agent:
            median_single = statistics.median(single_agent)
            table.add_row(
                '[italic]Single Agent Total[/italic]',
                f'{median_single:,}',
                str(len(single_agent)),
            )

        # Add total row
        if all_totals:
            median_total = statistics.median(all_totals)
            total_files = len(all_totals)
            table.add_row(
                '[bold]TOTAL[/bold]',
                f'[bold]{median_total:,}[/bold]',
                f'[bold]{total_files}[/bold]',
            )

        console.print(table)
        console.print()

    # Overall medians (only for multi-agent data)
    if overall_medians:
        table = Table(
            title='[bold]Overall Agent Medians[/bold]',
            show_header=True,
            header_style='bold blue',
        )
        table.add_column('Agent Type', style='cyan')
        table.add_column('Median Tokens', justify='right', style='green')

        # Sort by median tokens (descending)
        sorted_agents = sorted(
            overall_medians.items(), key=lambda x: x[1], reverse=True
        )

        for agent_name, median_tokens in sorted_agents:
            table.add_row(agent_name, f'{median_tokens:,.0f}')

        console.print(table)


def main(output_folder: Optional[str] = None):
    """Main function to run the token usage analyzer."""
    if not output_folder and len(sys.argv) != 2:
        console.print(
            '[red]Usage: python token_usage_analyzer.py <output_folder>[/red]'
        )
        console.print('Example: python token_usage_analyzer.py output/')
        sys.exit(1)

    if not output_folder:
        output_folder = sys.argv[1]

    console.print('[bold]Token Usage Analysis Tool[/bold]')
    console.print(f'Analyzing folder: {output_folder}')

    # Analyze folder
    subfolder_data = analyze_folder(output_folder)
    if not subfolder_data:
        console.print('[red]No valid token data found[/red]')
        return

    # Calculate overall medians
    overall_medians = calculate_medians(subfolder_data)

    # Display results
    display_results(subfolder_data, overall_medians)

    # Calculate total files processed
    total_files = sum(len(data['all_totals']) for data in subfolder_data.values())
    multi_agent_files = sum(
        len(data['multi_agent']) for data in subfolder_data.values()
    )
    single_agent_files = sum(
        len(data['single_agent']) for data in subfolder_data.values()
    )

    console.print(f'\n[green]Analysis complete![/green]')
    console.print(f'Total files processed: {total_files}')
    console.print(f'Multi-agent files: {multi_agent_files}')
    console.print(f'Single-agent files: {single_agent_files}')


if __name__ == '__main__':
    main()
