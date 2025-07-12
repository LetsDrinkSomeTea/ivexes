#!/usr/bin/env python3
"""Manual command line interface for ivexes modules."""

import click
import os
import logging
from dotenv import load_dotenv

from ivexes.config import get_settings, setup_default_logging
from ivexes.vector_db import CweCapecAttackDatabase
from ivexes.cve_search.tools import _search_cve_by_id

load_dotenv(dotenv_path='.secrets.env', override=True)
setup_default_logging()

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """Command line interface for ivexes modules.

    This is the main entry point for the CLI application.
    """
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
def tokenize(path: str) -> None:
    """Tokenize a file and print the number of tokens, characters, and words."""
    import ivexes.token as count

    res = (0, 0, 0)  # Default result in case of error
    if os.path.isdir(path):
        res = count.get_directory_statistics(path)
    elif os.path.isfile(path):
        res = count.get_file_statistics(path)

    click.echo(
        f'===== Result of counting =====\nTokens: {res[0]}\nCharacters: {res[1]}\nWords: {res[2]}'
    )


# CVE module commands
@cli.group()
def cve() -> None:
    """Commands for the CVE module.

    This group contains commands for fetching CVEs.
    """
    pass


@cve.command('by-id')
@click.argument('id')
def cmd_cve_by_id(id: str) -> None:
    """Search for a CVE by its ID."""
    click.echo(_search_cve_by_id(id))


# Vector DB module commands
@cli.group()
def vector_db() -> None:
    """Commands for the vector database module.

    This group contains commands for managing and querying the vector database.
    """
    pass


@vector_db.command('clear')
def cmd_clear() -> None:
    """Clear the vector database.

    This command removes all entries from the vector database.
    """
    db = CweCapecAttackDatabase()
    db.clear()
    click.echo('Database cleared successfully')


@vector_db.command('size')
def cmd_size() -> None:
    """Get the size of the vector database."""
    db = CweCapecAttackDatabase()
    click.echo(f' Size of DB: {db.collection.count()}')


@vector_db.command('init')
@click.argument('type_of_data', type=click.Choice(['cwe', 'capec', 'attack', 'all']))
def init_verctor_db(type_of_data: str):
    """Initialize vector database with specified data type."""
    db = CweCapecAttackDatabase()
    if type_of_data == 'cwe':
        db.initialize_cwe()
    elif type_of_data == 'capec':
        db.initialize_capec()
    elif type_of_data == 'attack':
        db.initialize_attack()
    elif type_of_data == 'all':
        db.initialize()


@vector_db.command('query')
@click.argument('query_text')
@click.option(
    '--type', '-t', type=click.Choice(['cwe', 'capec']), help='Type of entries to query'
)
@click.option('--count', '-n', default=3, help='Number of results to return')
def cmd_query(query_text: str, type: str, count: int) -> None:
    """Query the vector database for matching entries.

    Args:
        query_text: The text to search for in the database
        type: Filter results by entry type (cwe or capec)
        count: Maximum number of results to return
    """
    db = CweCapecAttackDatabase()
    types = [type] if type else None
    results = db.query(query_text, types, count)
    for result in results:
        click.echo(result)


@vector_db.command('query-cwe')
@click.argument('query_text')
@click.option('--count', '-n', default=3, help='Number of results to return')
def cmd_query_cwe(query_text: str, count: int) -> None:
    """Query only CWE entries in the vector database.

    Args:
        query_text: The text to search for in CWE entries
        count: Maximum number of results to return
    """
    db = CweCapecAttackDatabase()
    results = db.query_cwe(query_text, count)
    for result in results:
        click.echo(result)


@vector_db.command('query-capec')
@click.argument('query_text')
@click.option('--count', '-n', default=3, help='Number of results to return')
def cmd_query_capec(query_text: str, count: int) -> None:
    """Query only CAPEC entries in the vector database.

    Args:
        query_text: The text to search for in CAPEC entries
        count: Maximum number of results to return
    """
    db = CweCapecAttackDatabase()
    results = db.query_capec(query_text, count)
    for result in results:
        click.echo(result)


# Code Browser module commands
@cli.group()
def code_browser() -> None:
    """Commands for the code browser module.

    This group contains commands for browsing and analyzing code using LSP.
    """
    pass


@code_browser.command('get-definition')
@click.argument('symbol')
def cmd_get_definition(symbol: str) -> None:
    """Find the definition of a symbol in the codebase.

    Args:
        path_to_codebase: Path to the codebase directory
        symbol: The symbol name to find the definition for
    """
    from ivexes.code_browser import get_code_browser

    cb = get_code_browser()

    result = cb.get_definition(symbol)
    if result:
        definition, file, from_line, to_line = result
        click.echo(
            f'Found definition in file {file} from line {from_line} to {to_line} \n{definition}'
        )
    else:
        click.echo('No definition found')


@code_browser.command('get-references')
@click.argument('symbol')
def cmd_get_references(symbol: str) -> None:
    """Find all references to a symbol in the codebase.

    Args:
        path_to_codebase: Path to the codebase directory
        symbol: The symbol name to find references for
    """
    from ivexes.code_browser import get_code_browser

    cb = get_code_browser()

    results = cb.get_references(symbol)
    if results:
        click.echo(f'Found {len(results)} references:')
        for result in results:
            file, code, line, (col_s, col_e) = result
            click.echo(f'{file}:{line}:{col_s}-{col_e}\t{code}')
    else:
        click.echo('No References found')


@code_browser.command('get-diff')
@click.argument('file1', required=False)
@click.argument('file2', required=False)
def cmd_get_diff(file1: str, file2: str) -> None:
    """Get the differences between two files in the codebase.

    Args:
        file1: Path to the first file
        file2: Path to the second file
    """
    from ivexes.code_browser import get_code_browser

    cb = get_code_browser()

    results = cb.get_diff(file1=file1, file2=file2)
    if results:
        click.echo(f'Found {len(results)} diffs:')
        for result in results:
            click.echo(f'{result}\n{"-" * 80}\n')
    else:
        click.echo('No References found')


@code_browser.command('get-symbols')
@click.argument('file')
def cmd_get_symbols(file: str) -> None:
    """Get all symbols (variables, functions, classes) in a file.

    Args:
        path_to_codebase: Path to the codebase directory
        file: Path to the file within the codebase to analyze
    """
    from ivexes.code_browser import get_code_browser

    cb = get_code_browser()

    symbols = cb.get_symbols(file)
    for symbol in symbols:
        click.echo(symbol)


@code_browser.command('get-file')
@click.argument('file')
def cmd_get_file(file: str) -> None:
    """Get the content of a file in the codebase.

    Args:
        path_to_codebase: Path to the codebase directory
        file: Path to the file within the codebase to retrieve
    """
    from ivexes.code_browser import get_code_browser

    cb = get_code_browser()

    content = cb.get_file_content(file)
    click.echo(content)


@code_browser.command('get-tree')
@click.option('--count', '-n', default=3, help='Number of recursive levels')
def cmd_get_tree(count: int) -> None:
    """Get the directory structure of the codebase.

    Args:
        path_to_codebase: Path to the codebase directory
        count: Maximum depth level for the directory tree
    """
    from ivexes.code_browser import get_code_browser

    cb = get_code_browser()

    content = cb.get_codebase_structure(n=count)
    click.echo(content)


# Diff module commands
@cli.group()
def diff() -> None:
    """Commands for the diff module.

    This group contains commands for comparing code versions and analyzing differences.
    """
    click.echo('Diff module not yet implemented')


# Sandbox module commands
@cli.group()
def sandbox() -> None:
    """Commands for the sandbox module.

    This group contains commands for running code in an isolated sandbox environment.
    """
    pass


@sandbox.command('start')
def cmd_start() -> None:
    """Starts interactive shell in a sandbox environment."""
    from ivexes.sandbox.sandbox import Sandbox

    if not (setup_archive := get_settings().setup_archive):
        click.echo(
            'No setup archive configured. Please set it in the settings or via the env vars'
        )
        return

    sb = Sandbox(setup_archive=setup_archive)
    if not sb.connect():
        click.echo('Failed to connect to sandbox')
        return
    command = 'pwd'
    while command not in ['exit']:
        result = sb.write_to_shell(command.encode())
        click.echo(result)
        command = input("\n Next command ('exit' to exit): ")


@sandbox.command('run')
@click.argument('command')
def cmd_run(command: str) -> None:
    """Run a command in a sandbox environment.

    Args:
        path_to_executable_archive: Path to the executable archive
        command: The command to run in the sandbox

    """
    from ivexes.sandbox.sandbox import Sandbox

    if not (setup_archive := get_settings().setup_archive):
        click.echo(
            'No setup archive configured. Please set it in the settings or via the env vars'
        )
        return

    sb = Sandbox(setup_archive=setup_archive)
    if not sb.connect():
        click.echo('Failed to connect to sandbox')
        return
    result = sb.write_to_shell(command.encode())
    click.echo(result)


@sandbox.command('create-file')
@click.argument('path')
@click.argument('content')
def create_file(path: str, content: str) -> None:
    """Create a file in the sandbox environment.

    Args:
        path: Path where the file should be created
        content: Content to write to the file

    """
    from ivexes.sandbox.sandbox import Sandbox

    if not (setup_archive := get_settings().setup_archive):
        click.echo(
            'No setup archive configured. Please set it in the settings or via the env vars'
        )
        return

    sb = Sandbox(setup_archive=setup_archive)
    if not sb.connect():
        click.echo('Failed to connect to sandbox')
        return
    click.echo(sb.create_file('test', 'multi\nlinie\ntext ```’’’\\\\´´'))
    click.echo(sb.create_file(path, content=content))


if __name__ == '__main__':
    cli()
