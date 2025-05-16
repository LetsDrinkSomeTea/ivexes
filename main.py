#!/usr/bin/env python3
import click

from modules.code_browser.code_browser import CodeBrowser
from modules.vector_db.embed import CweCapecDatabase

import docker

import config.log
logger = config.log.get(__name__)

@click.group()
def cli():
    """Command line interface for ivexes modules."""
    pass

# Vector DB module commands
@cli.group()
def vector_db():
    """Commands for the vector database module."""
    pass

@vector_db.command('clear')
def cmd_clear():
    """Clear the vector database."""
    db = CweCapecDatabase()
    db.clear()
    click.echo("Database cleared successfully")

@vector_db.command('query')
@click.argument('query_text')
@click.option('--type', '-t', type=click.Choice(['cwe', 'capec']),
              help="Type of entries to query")
@click.option('--count', '-n', default=3, help="Number of results to return")
def cmd_query(query_text, type, count):
    """Query the vector database."""
    db = CweCapecDatabase()
    types = list(type) if type else None
    results = db.query(query_text, types, count)
    for result in results:
        click.echo(result)

@vector_db.command('query-cwe')
@click.argument('query_text')
@click.option('--count', '-n', default=3, help="Number of results to return")
def cmd_query_cwe(query_text, count):
    """Query CWE entries in the vector database."""
    db = CweCapecDatabase()
    results = db.query_cwe(query_text, count)
    for result in results:
        click.echo(result)

@vector_db.command('query-capec')
@click.argument('query_text')
@click.option('--count', '-n', default=3, help="Number of results to return")
def cmd_query_capec(query_text, count):
    """Query CAPEC entries in the vector database."""
    db = CweCapecDatabase()
    results = db.query_capec(query_text, count)
    for result in results:
        click.echo(result)

# Code Browser module commands
@cli.group()
def code_browser():
    """Commands for the code browser module."""
    pass

@code_browser.command('get-definition')
@click.argument('path_to_codebase')
@click.argument('symbol')
def cmd_get_definition(path_to_codebase, symbol):
    """Query CAPEC entries in the vector database."""
    cb = CodeBrowser(path_to_codebase)
    result = cb.get_definition(symbol)
    if result:
        definition, line, col = result
        click.echo(f"Found definition at {line}:{col}\n{definition}")
    else:
        click.echo("No definition found")

@code_browser.command('get-references')
@click.argument('path_to_codebase')
@click.argument('symbol')
def cmd_get_references(path_to_codebase, symbol):
    """Query CAPEC entries in the vector database."""
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
def cmd_get_symbols(path_to_codebase, file):
    """Get all symbols in the file."""
    cb = CodeBrowser(path_to_codebase)
    symbols = cb.get_symbols(file)
    for symbol in symbols:
        click.echo(symbol)

@code_browser.command('get-file')
@click.argument('path_to_codebase')
@click.argument('file')
def cmd_get_file(path_to_codebase, file):
    """Get all symbols in the file."""
    cb = CodeBrowser(path_to_codebase)
    content = cb.get_file_content(file)
    click.echo(content)

@code_browser.command('get-tree')
@click.argument('path_to_codebase')
@click.option('--count', '-n', default=3, help="Number of recursive levels")
def cmd_get_tree(path_to_codebase, count):
    """Get the structure of the codebase."""
    cb = CodeBrowser(path_to_codebase)
    content = cb.get_codebase_structure(n=count)
    click.echo(content)

# Diff module commands
@cli.group()
def diff():
    """Commands for the diff module."""
    click.echo("Diff module not yet implemented")

# Sandbox module commands
@cli.group()
def sandbox():
    """Commands for the sandbox module."""
    click.echo("Sandbox module not yet implemented")

if __name__ == '__main__':
    cli()
