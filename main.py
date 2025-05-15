#!/usr/bin/env python3
import click

from modules.code_browser.code_browser import CodeBrowser
from modules.vector_db.embed import CweCapecDatabase

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

@vector_db.command('query-capec')
@click.argument('query_text')
@click.option('--count', '-n', default=3, help="Number of results to return")
def cmd_query_capec(query_text, count):
    """Query CAPEC entries in the vector database."""
    click.echo("not implementet")

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
