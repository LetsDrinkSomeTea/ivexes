#!/usr/bin/env python3
import click

from modules.code_browser.code_browser import CodeBrowser
from modules.sandbox.sandbox import Sandbox
from modules.vector_db.embed import CweCapecDatabase

import docker

import config.log
logger = config.log.get(__name__)

@click.group()
def cli() -> None:
    """
    Command line interface for ivexes modules.

    This is the main entry point for the CLI application.
    """
    pass

# Vector DB module commands
@cli.group()
def vector_db() -> None:
    """
    Commands for the vector database module.

    This group contains commands for managing and querying the vector database.
    """
    pass

@vector_db.command('clear')
def cmd_clear() -> None:
    """
    Clear the vector database.

    This command removes all entries from the vector database.
    """
    db = CweCapecDatabase()
    db.clear()
    click.echo("Database cleared successfully")

@vector_db.command('query')
@click.argument('query_text')
@click.option('--type', '-t', type=click.Choice(['cwe', 'capec']),
              help="Type of entries to query")
@click.option('--count', '-n', default=3, help="Number of results to return")
def cmd_query(query_text: str, type: str, count: int) -> None:
    """
    Query the vector database for matching entries.

    Args:
        query_text: The text to search for in the database
        type: Filter results by entry type (cwe or capec)
        count: Maximum number of results to return
    """
    db = CweCapecDatabase()
    types = [type] if type else None
    results = db.query(query_text, types, count)
    for result in results:
        click.echo(result)

@vector_db.command('query-cwe')
@click.argument('query_text')
@click.option('--count', '-n', default=3, help="Number of results to return")
def cmd_query_cwe(query_text: str, count: int) -> None:
    """
    Query only CWE entries in the vector database.

    Args:
        query_text: The text to search for in CWE entries
        count: Maximum number of results to return
    """
    db = CweCapecDatabase()
    results = db.query_cwe(query_text, count)
    for result in results:
        click.echo(result)

@vector_db.command('query-capec')
@click.argument('query_text')
@click.option('--count', '-n', default=3, help="Number of results to return")
def cmd_query_capec(query_text: str, count: int) -> None:
    """
    Query only CAPEC entries in the vector database.

    Args:
        query_text: The text to search for in CAPEC entries
        count: Maximum number of results to return
    """
    db = CweCapecDatabase()
    results = db.query_capec(query_text, count)
    for result in results:
        click.echo(result)

# Code Browser module commands
@cli.group()
def code_browser() -> None:
    """
    Commands for the code browser module.

    This group contains commands for browsing and analyzing code using LSP.
    """
    pass

@code_browser.command('get-definition')
@click.argument('path_to_codebase')
@click.argument('symbol')
def cmd_get_definition(path_to_codebase: str, symbol: str) -> None:
    """
    Find the definition of a symbol in the codebase.

    Args:
        path_to_codebase: Path to the codebase directory
        symbol: The symbol name to find the definition for
    """
    cb = CodeBrowser(path_to_codebase)
    result = cb.get_definition(symbol)
    if result:
        definition, file, from_line, to_line = result
        click.echo(f"Found definition in file {file} from line {from_line} to {to_line} \n{definition}")
    else:
        click.echo("No definition found")

@code_browser.command('get-references')
@click.argument('path_to_codebase')
@click.argument('symbol')
def cmd_get_references(path_to_codebase: str, symbol: str) -> None:
    """
    Find all references to a symbol in the codebase.

    Args:
        path_to_codebase: Path to the codebase directory
        symbol: The symbol name to find references for
    """
    cb = CodeBrowser(path_to_codebase)
    results = cb.get_references(symbol)
    if results:
        click.echo(f"Found {len(results)} references:")
        for result in results:
            file, code, line, (col_s, col_e) = result
            click.echo(f"{file}:{line}:{col_s}-{col_e}\t{code}")
    else:
        click.echo("No References found")

@code_browser.command('get-symbols')
@click.argument('path_to_codebase')
@click.argument('file')
def cmd_get_symbols(path_to_codebase: str, file: str) -> None:
    """
    Get all symbols (variables, functions, classes) in a file.

    Args:
        path_to_codebase: Path to the codebase directory
        file: Path to the file within the codebase to analyze
    """
    cb = CodeBrowser(path_to_codebase)
    symbols = cb.get_symbols(file)
    for symbol in symbols:
        click.echo(symbol)

@code_browser.command('get-file')
@click.argument('path_to_codebase')
@click.argument('file')
def cmd_get_file(path_to_codebase: str, file: str) -> None:
    """
    Get the content of a file in the codebase.

    Args:
        path_to_codebase: Path to the codebase directory
        file: Path to the file within the codebase to retrieve
    """
    cb = CodeBrowser(path_to_codebase)
    content = cb.get_file_content(file)
    click.echo(content)

@code_browser.command('get-tree')
@click.argument('path_to_codebase')
@click.option('--count', '-n', default=3, help="Number of recursive levels")
def cmd_get_tree(path_to_codebase: str, count: int) -> None:
    """
    Get the directory structure of the codebase.

    Args:
        path_to_codebase: Path to the codebase directory
        count: Maximum depth level for the directory tree
    """
    cb = CodeBrowser(path_to_codebase)
    content = cb.get_codebase_structure(n=count)
    click.echo(content)

# Diff module commands
@cli.group()
def diff() -> None:
    """
    Commands for the diff module.

    This group contains commands for comparing code versions and analyzing differences.
    """
    click.echo("Diff module not yet implemented")

# Sandbox module commands
@cli.group()
def sandbox() -> None:
    """
    Commands for the sandbox module.

    This group contains commands for running code in an isolated sandbox environment.
    """
    pass

@sandbox.command('run')
@click.argument('path_to_executable_archive')
@click.argument('command')
def cmd_run(path_to_executable_archive: str, command: str) -> None:
    """
    Run a command in a sandbox environment.
    Args:
        path_to_executable_archive: Path to the executable archive
        command: The command to run in the sandbox

    """
    sb = Sandbox(path_to_executable_archive)
    if not sb.connect():
        click.echo("Failed to connect to sandbox")
        return
    result = sb.write_to_shell(command.encode())
    click.echo(result)


if __name__ == '__main__':
    cli()
