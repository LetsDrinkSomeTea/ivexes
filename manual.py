#!/usr/bin/env python3
"""Manual command line interface for ivexes modules."""

import logging
import os
from typing import Optional

import click
from agents import Tool
from dotenv import load_dotenv

from ivexes.config import create_settings, setup_default_logging
from ivexes.config.settings import PartialSettings
from ivexes.cve_search.tools import _search_cve_by_id
from ivexes.printer.formatter import sprint_tools_as_json
from ivexes.vector_db import CweCapecAttackDatabase
from ivexes.agents.multi_agent.tools import (
    create_shared_memory_tools,
    MultiAgentContext,
    agent_as_tool,
)

load_dotenv(verbose=True, override=True)
setup_default_logging('DEBUG')

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
    settings = create_settings()
    db = CweCapecAttackDatabase(settings)
    db.clear()
    click.echo('Database cleared successfully')


@vector_db.command('size')
def cmd_size() -> None:
    """Get the size of the vector database."""
    settings = create_settings()
    db = CweCapecAttackDatabase(settings)
    click.echo(f' Size of DB: {db.collection.count()}')


@vector_db.command('init')
@click.argument('type_of_data', type=click.Choice(['cwe', 'capec', 'attack', 'all']))
def init_verctor_db(type_of_data: str):
    """Initialize vector database with specified data type."""
    settings = create_settings()
    db = CweCapecAttackDatabase(settings)
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
    settings = create_settings()
    db = CweCapecAttackDatabase(settings)
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
    settings = create_settings()
    db = CweCapecAttackDatabase(settings)
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
    settings = create_settings()
    db = CweCapecAttackDatabase(settings)
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
        symbol: The symbol name to find the definition for
    """
    from ivexes.code_browser import CodeBrowser

    settings = create_settings()
    cb = CodeBrowser(settings)

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
    from ivexes.code_browser import CodeBrowser

    settings = create_settings()
    cb = CodeBrowser(settings)

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
    from ivexes.code_browser import CodeBrowser

    settings = create_settings()
    cb = CodeBrowser(settings)

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
    from ivexes.code_browser import CodeBrowser

    settings = create_settings()
    cb = CodeBrowser(settings)

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
    from ivexes.code_browser import CodeBrowser

    settings = create_settings()
    cb = CodeBrowser(settings)

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
    from ivexes.code_browser import CodeBrowser

    settings = create_settings()
    cb = CodeBrowser(settings)

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

    settings = create_settings()

    sb = Sandbox(settings)
    if not sb.connect():
        click.echo('Failed to connect to sandbox')
        return
    command = 'pwd'
    while command not in ['exit']:
        result = sb.run(command.encode())
        click.echo(result)
        command = input("\n Next command ('exit' to exit): ")


@sandbox.command('run')
@click.argument('command')
@click.option('-i', '--image')
def cmd_run(command: str, image: Optional[str]) -> None:
    """Run a command in a sandbox environment.

    Args:
        command: The command to run in the sandbox
        image: Optional Docker image to use for the sandbox

    """
    from ivexes.sandbox.sandbox import Sandbox

    settings = create_settings()
    if image:
        # Override sandbox image in settings
        settings = create_settings(PartialSettings(sandbox_image=image))

    sb = Sandbox(settings)
    if not sb.connect():
        click.echo('Failed to connect to sandbox')
        return
    result = sb.run(command.encode())
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

    settings = create_settings()
    if not settings.setup_archive:
        click.echo(
            'No setup archive configured. Please set it in the settings or via the env vars'
        )
        return

    sb = Sandbox(settings)
    if not sb.connect():
        click.echo('Failed to connect to sandbox')
        return
    click.echo(sb.create_file('test', 'multi\nlinie\ntext ```’’’\\\\´´'))
    click.echo(sb.create_file(path, content=content))


@cli.group
def llm() -> None:
    """Commands for the LLM module.

    This group contains commands for interacting with large language models.
    """
    pass


@llm.command('ask')
@click.argument('input')
def cmd_llm_ask(input: str) -> None:
    """Query a LLM using default config.

    Args:
        input: The input text to query the LLM with
    """
    from ivexes.agents import DefaultAgent

    agent = DefaultAgent()
    click.echo(agent.run(user_msg=input).final_output)


@llm.command('tools')
@click.argument(
    'type',
    type=click.Choice(
        ['code_browser', 'cve', 'context', 'date', 'report', 'sandbox', 'vectordb']
    ),
)
def cmd_llm_tools(type: str) -> None:
    """List all tools for the LLM module."""
    from ivexes.tools import (
        create_code_browser_tools,
        cve_tools,
        date_tools,
        create_report_tools,
        create_sandbox_tools,
        create_vectordb_tools,
    )
    from ivexes.code_browser import CodeBrowser
    from ivexes.vector_db import CweCapecAttackDatabase

    settings = create_settings()
    tools: list[Tool] = []
    match type:
        case 'code_browser':
            cb = CodeBrowser(settings)
            tools = create_code_browser_tools(cb)
        case 'cve':
            tools = cve_tools
        case 'date':
            tools = date_tools
        case 'report':
            tools = create_report_tools(settings)
        case 'sandbox':
            tools = create_sandbox_tools(settings)
        case 'vectordb':
            db = CweCapecAttackDatabase(settings)
            tools = create_vectordb_tools(db)
        case 'context':
            tools = create_shared_memory_tools(MultiAgentContext())
        case _:
            click.echo('Unknown tool type')
            return

    click.echo(sprint_tools_as_json(tools))


if __name__ == '__main__':
    cli()
