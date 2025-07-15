#!/usr/bin/env python3
"""github_scraper.py: Search for Linux tools on GitHub with CVEs in recent versions.

This script uses the GitHub API to find repositories tagged with "linux", clones each locally,
then scans commit messages and text files (.md, .txt) for CVE identifiers and keywords such as
"Vulnerability". It stores results in SQLite database and only rescans repositories when new
commits are detected.

Features:
 - SQLite database for persistent storage
 - Incremental scanning (only rescans when new commits detected)
 - Configurable number of repositories to scan
 - JSON output to file or stdout
 - Progress tracking with rich console output

Usage:
    export GITHUB_TOKEN=<your_token>
    python3 github_scraper.py [-n NUM_REPOS] [-o OUTPUT_FILE] [-d DATABASE] [--force-rescan]

Options:
    -n, --num-repos NUM     Number of repositories to scan (default: 50)
    -o, --output FILE       Output JSON results to file
    -d, --database FILE     SQLite database file (default: github_scan.db)
    --force-rescan          Force rescan all repos even without new commits

Dependencies:
    pip install PyGithub GitPython rich
"""

import os
import re
import json
import tempfile
import shutil
import sqlite3
import argparse
from datetime import datetime, timedelta
from github import Github
from git import Repo
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.table import Table
from rich.panel import Panel

console = Console()


def init_database(db_path):
    """Initialize SQLite database with repositories and scan_results tables.

    Args:
        db_path (str): Path to SQLite database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create repositories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT UNIQUE,
            url TEXT,
            language TEXT,
            last_scanned TIMESTAMP,
            last_commit_sha TEXT
        )
    """)

    # Create scan_results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository_id INTEGER,
            location TEXT,
            matches TEXT,
            scan_date TIMESTAMP,
            FOREIGN KEY (repository_id) REFERENCES repositories (id)
        )
    """)

    conn.commit()
    conn.close()


def get_repository_info(db_path, repo_full_name):
    """Get repository information from database.

    Args:
        db_path (str): Path to SQLite database file
        repo_full_name (str): Full name of repository (owner/repo)

    Returns:
        tuple: (repository_id, last_commit_sha) or None if not found
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, last_commit_sha FROM repositories WHERE full_name = ?',
        (repo_full_name,),
    )
    result = cursor.fetchone()
    conn.close()
    return result


def update_repository_info(
    db_path, repo_full_name, repo_url, language, last_commit_sha
):
    """Update or insert repository information in database.

    Args:
        db_path (str): Path to SQLite database file
        repo_full_name (str): Full name of repository (owner/repo)
        repo_url (str): Repository URL
        language (str): Primary programming language
        last_commit_sha (str): SHA of latest commit

    Returns:
        int: Repository ID
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO repositories (full_name, url, language, last_scanned, last_commit_sha)
        VALUES (?, ?, ?, ?, ?)
    """,
        (
            repo_full_name,
            repo_url,
            language,
            datetime.now().isoformat(),
            last_commit_sha,
        ),
    )
    repo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return repo_id


def store_scan_results(db_path, repository_id, matches):
    """Store scan results in database.

    Args:
        db_path (str): Path to SQLite database file
        repository_id (int): Repository ID
        matches (list): List of match dictionaries with location and matches
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear previous results for this repository
    cursor.execute('DELETE FROM scan_results WHERE repository_id = ?', (repository_id,))

    # Insert new results
    for match in matches:
        cursor.execute(
            """
            INSERT INTO scan_results (repository_id, location, matches, scan_date)
            VALUES (?, ?, ?, ?)
        """,
            (
                repository_id,
                match['location'],
                json.dumps(match['matches']),
                datetime.now().isoformat(),
            ),
        )

    conn.commit()
    conn.close()


def get_stored_results(db_path):
    """Get all stored scan results from database.

    Args:
        db_path (str): Path to SQLite database file

    Returns:
        list: List of repository results with matches
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.full_name, r.url, r.language, sr.location, sr.matches
        FROM repositories r
        JOIN scan_results sr ON r.id = sr.repository_id
        ORDER BY r.full_name, sr.location
    """)
    results = cursor.fetchall()
    conn.close()

    # Group results by repository
    repo_results = {}
    for full_name, url, language, location, matches_json in results:
        if full_name not in repo_results:
            repo_results[full_name] = {
                'repository': full_name,
                'url': url,
                'type': language,
                'matches': [],
            }
        repo_results[full_name]['matches'].append(
            {'location': location, 'matches': json.loads(matches_json)}
        )

    return list(repo_results.values())


def query_cve_commit_matches(db_path):
    """Query database for entries where matches contain CVE and location is a commit message."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.full_name, r.url, r.language, sr.location, sr.matches, sr.scan_date
        FROM repositories r
        JOIN scan_results sr ON r.id = sr.repository_id
        WHERE sr.location LIKE 'commit:%'
        AND sr.matches LIKE '%CVE-%'
        ORDER BY r.full_name, sr.scan_date DESC
    """)
    results = cursor.fetchall()
    conn.close()

    # Format results
    formatted_results = []
    for full_name, url, language, location, matches_json, scan_date in results:
        matches = json.loads(matches_json)
        # Filter matches to only include CVE entries
        cve_matches = [match for match in matches if 'CVE-' in match]
        if cve_matches:
            formatted_results.append(
                {
                    'repository': full_name,
                    'url': url,
                    'language': language,
                    'commit_sha': location.replace('commit:', ''),
                    'cve_matches': cve_matches,
                    'scan_date': scan_date,
                }
            )

    return formatted_results


def has_new_commits(repo, last_commit_sha, since_date):
    """Check if repository has new commits since last scan.

    Args:
        repo: GitHub repository object
        last_commit_sha (str): SHA of last known commit
        since_date (datetime): Date to check commits since

    Returns:
        bool: True if repository has new commits
    """
    try:
        commits = list(
            repo.get_commits(since=since_date).get_page(0)
        )  # Get first page only
        if not commits:
            return False
        latest_commit_sha = commits[0].sha
        return latest_commit_sha != last_commit_sha
    except Exception:
        return True  # If we can't check, assume we need to scan


def find_cve_matches_in_text(text):
    """Find CVE identifiers and vulnerability keywords in text.

    Args:
        text (str): Text to search

    Returns:
        list: List of unique CVE identifiers and keywords found
    """
    pattern = re.compile(r'CVE-\d{4}-\d{4,7}', re.IGNORECASE)
    keyword_pattern = re.compile(r'Vulnerability', re.IGNORECASE)
    matches = []
    for m in pattern.findall(text):
        matches.append(m)
    if keyword_pattern.search(text):
        matches.append('Vulnerability')
    return list(set(matches))


def scan_commit_messages(repo, since_date):
    """Scan repository commit messages for CVE matches.

    Args:
        repo: GitHub repository object
        since_date (datetime): Date to scan commits since

    Returns:
        list: List of matches with location and found CVEs
    """
    matches = []
    commit_count = 0
    max_commits = 200  # Limit commits scanned to prevent API timeouts

    try:
        for commit in repo.get_commits(since=since_date):
            if commit_count >= max_commits:
                break

            msg = commit.commit.message
            found = find_cve_matches_in_text(msg)
            if found:
                matches.append({'location': f'commit:{commit.sha}', 'matches': found})
            commit_count += 1
    except Exception as e:
        # If API fails, continue with empty results
        pass

    return matches


def scan_local_files(path):
    """Scan local repository files for CVE matches.

    Args:
        path (str): Path to local repository

    Returns:
        list: List of matches with file location and found CVEs
    """
    matches = []
    file_count = 0
    max_files = 100  # Limit files scanned per repo to prevent timeouts

    for root, _, files in os.walk(path):
        for fname in files:
            # Only scan .md and .txt files
            if not (fname.lower().endswith('.md') or fname.lower().endswith('.txt')):
                continue

            if file_count >= max_files:
                break

            fpath = os.path.join(root, fname)
            try:
                # Limit file size to prevent memory issues
                file_size = os.path.getsize(fpath)
                if file_size > 1024 * 1024:  # Skip files larger than 1MB
                    continue

                with open(fpath, 'r', errors='ignore') as f:
                    text = f.read(100000)  # Read max 100KB per file
            except Exception:
                continue

            found = find_cve_matches_in_text(text)
            if found:
                matches.append({'location': fpath, 'matches': found})
            file_count += 1

        if file_count >= max_files:
            break

    return matches


def parse_arguments():
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Search GitHub repositories for CVE mentions and vulnerabilities'
    )
    parser.add_argument(
        '-n',
        '--num-repos',
        type=int,
        default=50,
        help='Number of repositories to scan (default: 50)',
    )
    parser.add_argument(
        '-o', '--output', type=str, help='Output file path for JSON results'
    )
    parser.add_argument(
        '-d',
        '--database',
        type=str,
        default='github_scan.db',
        help='SQLite database file path (default: github_scan.db)',
    )
    parser.add_argument(
        '--force-rescan',
        action='store_true',
        help='Force rescan all repositories even if no new commits',
    )
    parser.add_argument(
        '--query-cve-commits',
        action='store_true',
        help='Query database for CVE matches in commit messages and exit',
    )
    return parser.parse_args()


def main():
    """Main function that orchestrates the GitHub scraping process."""
    args = parse_arguments()

    # Initialize database
    init_database(args.database)

    # Handle query mode
    if args.query_cve_commits:
        results = query_cve_commit_matches(args.database)

        if results:
            console.print(
                f'[bold green]Found {len(results)} CVE matches in commit messages:[/bold green]\n'
            )

            table = Table(show_header=True, header_style='bold magenta')
            table.add_column('Repository', style='cyan', no_wrap=True)
            table.add_column('Language', style='green')
            table.add_column('Commit SHA', style='yellow', no_wrap=True)
            table.add_column('CVE Matches', style='red')
            table.add_column('Scan Date', style='dim')

            for result in results:
                table.add_row(
                    result['repository'],
                    result['language'] or 'Unknown',
                    result['commit_sha'][:8],  # Short SHA
                    ', '.join(result['cve_matches']),
                    result['scan_date'][:10],  # Date only
                )

            console.print(table)

            # Output to file if specified
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                console.print(f'\n[green]Results saved to {args.output}[/green]')
        else:
            console.print('[yellow]No CVE matches found in commit messages.[/yellow]')

        return

    token = os.getenv('GITHUB_TOKEN')
    if not token:
        console.print(
            '[bold red]ERROR:[/bold red] Please set GITHUB_TOKEN environment variable.'
        )
        return

    gh = Github(token)
    six_months_ago = datetime.now() - timedelta(days=180)

    query = 'topic:linux stars:>=100'
    repos = gh.search_repositories(query=query, sort='updated', order='desc')

    results = []
    temp_root = tempfile.mkdtemp(prefix='ghscrape_')

    console.print(
        Panel.fit('[bold blue]GitHub CVE Scraper[/bold blue]', border_style='blue')
    )
    console.print(f"[dim]Searching for repositories with topic 'linux'...[/dim]")

    repo_list = list(repos[: args.num_repos])
    console.print(f'[green]Found {len(repo_list)} repositories to process[/green]')

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn('[progress.description]{task.description}'),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task('Processing repositories...', total=len(repo_list))

            for i, repo in enumerate(repo_list):
                progress.update(task, description=f'Processing {repo.full_name}')

                # Check if we need to rescan this repository
                repo_info = get_repository_info(args.database, repo.full_name)
                if repo_info and not args.force_rescan:
                    repo_id, last_commit_sha = repo_info
                    if not has_new_commits(repo, last_commit_sha, six_months_ago):
                        console.print(
                            f'[dim][yellow]Skipping[/yellow] {repo.full_name} (no new commits)[/dim]'
                        )
                        progress.advance(task)
                        continue

                # Check if repo has recent activity (commit within last month OR release within last 6 months)
                one_month_ago = datetime.now() - timedelta(days=30)
                has_recent_activity = False

                # Check for recent commits
                try:
                    recent_commits = list(
                        repo.get_commits(since=one_month_ago).get_page(0)
                    )
                    if recent_commits:
                        has_recent_activity = True
                except Exception:
                    pass

                # If no recent commits, check for recent releases
                if not has_recent_activity:
                    try:
                        recent_releases = [
                            r
                            for r in repo.get_releases()
                            if r.created_at >= six_months_ago.astimezone()
                        ]
                        if recent_releases:
                            has_recent_activity = True
                    except Exception:
                        pass

                if not has_recent_activity:
                    console.print(
                        f'[dim][yellow]Skipping[/yellow] {repo.full_name}: no recent activity)[/dim]'
                    )
                    progress.advance(task)
                    continue

                repo_path = os.path.join(temp_root, repo.full_name.replace('/', '_'))
                try:
                    # Clone with timeout and shallow clone for performance
                    repo_obj = Repo.clone_from(
                        repo.clone_url,
                        repo_path,
                        depth=1,  # Shallow clone for faster downloads
                    )
                except Exception as e:
                    console.print(
                        f'[yellow]Skipping[/yellow] {repo.full_name}: clone failed ({str(e)})'
                    )
                    progress.advance(task)
                    continue

                cmeshes = scan_commit_messages(repo, six_months_ago)
                fmeshes = scan_local_files(repo_path)

                all_matches = cmeshes + fmeshes

                # Get latest commit SHA for tracking
                latest_commit_sha = None
                try:
                    commits = list(repo.get_commits(since=six_months_ago).get_page(0))
                    if commits:
                        latest_commit_sha = commits[0].sha
                except Exception:
                    pass

                # Update repository info in database
                repo_id = update_repository_info(
                    args.database,
                    repo.full_name,
                    repo.html_url,
                    repo.language or 'Unknown',
                    latest_commit_sha,
                )

                if all_matches:
                    console.print(
                        f'[green]✓[/green] Found CVE matches in {repo.full_name}'
                    )

                    # Store results in database
                    store_scan_results(args.database, repo_id, all_matches)

                    results.append(
                        {
                            'repository': repo.full_name,
                            'url': repo.html_url,
                            'type': repo.language or 'Unknown',
                            'matches': all_matches,
                        }
                    )

                shutil.rmtree(repo_path)
                progress.advance(task)

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    # Get all stored results from database
    all_results = get_stored_results(args.database)

    console.print(
        f'\n[bold green]Scan completed![/bold green] Found {len(results)} new repositories with CVE matches.\n'
    )
    console.print(
        f'[bold blue]Total stored results:[/bold blue] {len(all_results)} repositories with CVE matches.\n'
    )

    if all_results:
        table = Table(show_header=True, header_style='bold magenta')
        table.add_column('Repository', style='cyan', no_wrap=True)
        table.add_column('Language', style='green')
        table.add_column('Matches', style='yellow')
        table.add_column('URL', style='blue')

        for result in all_results:
            matches_summary = []
            for match in result['matches']:
                if isinstance(match['matches'], list):
                    matches_summary.extend(match['matches'])
                else:
                    matches_summary.append(match['matches'])

            matches_text = ', '.join(set(matches_summary))
            table.add_row(
                result['repository'], result['type'], matches_text, result['url']
            )

        console.print(table)
    else:
        console.print('[yellow]No repositories found with CVE matches.[/yellow]')

    # Output to file if specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(all_results, f, indent=2)
        console.print(f'\n[green]Results saved to {args.output}[/green]')
    else:
        console.print(f'\n[dim]JSON output:[/dim]')
        print(json.dumps(all_results, indent=2))


if __name__ == '__main__':
    main()
