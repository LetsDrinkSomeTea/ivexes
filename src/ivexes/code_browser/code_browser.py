#!/usr/bin/env python3
"""Code Browser module for LSP-based code analysis.

This module provides a CodeBrowser class that leverages Neovim's Language Server
Protocol (LSP) capabilities to analyze codebases. It runs in a containerized
environment to provide consistent analysis capabilities across different systems.

The CodeBrowser can:
- Navigate code structures using LSP
- Find symbol definitions and references
- Analyze file contents and directory structures
- Generate code diffs between versions
- Parse programming language symbols

Example:
    Basic code browser usage:

    >>> browser = CodeBrowser(
    ...     codebase='/path/to/code', vulnerable_folder='vuln', patched_folder='patched'
    ... )
    >>> symbols = browser.get_symbols('main.c')
    >>> structure = browser.get_codebase_structure()
"""

import os
import re
from typing import Literal, Optional
import chardet
import sys
from time import sleep
import asyncio
import concurrent.futures

from docker.models.containers import Container
import pynvim

import logging
from .nvim import setup_container
from .parser import parse_symbols, parse_references
from ..config.settings import Settings

logger = logging.getLogger(__name__)
NVIM_DELAY = 0.5


class CodeBrowser:
    """LSP-based code browser for comprehensive code analysis.

    This class provides a high-level interface for analyzing codebases using
    Neovim's Language Server Protocol capabilities in a containerized environment.
    It supports various programming languages and provides symbol navigation,
    reference finding, and code structure analysis.

    The browser operates in a Docker container to ensure consistent analysis
    environments and proper LSP server availability for different languages.

    Attributes:
        path (str): Absolute path to the codebase directory.
        vulnerable_folder (str): Name of the vulnerable code folder.
        patched_folder (str): Name of the patched code folder.
        container: Docker container instance for the analysis environment.
        nvim: PyNvim client instance for LSP communication.

    Example:
        Comprehensive code analysis workflow:

        >>> browser = CodeBrowser(
        ...     codebase='/project/src',
        ...     vulnerable_folder='before_fix',
        ...     patched_folder='after_fix',
        ...     port=8080,
        ... )
        >>> # Get codebase structure
        >>> structure = browser.get_codebase_structure(n=3)
        >>> print(structure)
        >>> # Analyze symbols in a file
        >>> symbols = browser.get_symbols('main.c')
        >>> for name, type, line, range in symbols:
        ...     print(f'{name} ({type}) at line {line}')
        >>> # Find references to a symbol
        >>> refs = browser.get_references('vulnerable_function')
        >>> # Get differences between versions
        >>> diffs = browser.get_diff()
    """

    def __init__(
        self,
        settings: Settings,
        port: int = 8080,
        load: Literal['lazy', 'eager'] = 'lazy',
    ) -> None:
        """Initialize the CodeBrowser with codebase and connection parameters.

        Args:
            settings (Settings): Settings instance containing codebase paths and other configurations.
            port (int, optional): Port number for Neovim TCP connection.
                Defaults to 8080.
            load (Literal['lazy', 'eager'], optional): Load mode for the browser.

        Raises:
            SystemExit: If connection to Neovim fails.

        Example:
            >>> browser = CodeBrowser(
            ...     settings=settings,
            ...     port=8080,
            ... )
        """
        if (
            not settings.codebase_path
            or not settings.vulnerable_folder
            or not settings.patched_folder
        ):
            raise ValueError(
                'Codebase path, vulnerable folder, and patched folder must be set in settings to instance a CodeBrowser.'
            )
        self.settings = settings
        self.path = os.path.abspath(settings.codebase_path)
        self.vulnerable_folder = os.path.basename(settings.vulnerable_folder)
        self.patched_folder = os.path.basename(settings.patched_folder)
        self.port = port
        self.container: Container = None  # type: ignore[assignment] This won't be None, because it will be set in `initialize()` and checked in `_check_init()`
        self.nvim: pynvim.Nvim = None  # type: ignore[assignment] This won't be None, because it will be set in `initialize()` and checked in `_check_init()`
        if load == 'eager':
            self.initialize()

    def _check_init(self) -> None:
        if not self.container or not self.nvim:
            self.initialize()

    def initialize(self) -> None:
        """Initialize the CodeBrowser by setting up the Docker container and connecting to Neovim.

        This method sets up the Docker container for the codebase, ensuring that
        the necessary environment is ready for code analysis. It also establishes
        a connection to Neovim using PyNvim for LSP capabilities.

        Raises:
            SystemExit: If connection to Neovim fails.
        """
        logger.info(f'Codebase: {self.path} starting container ...')
        logger.debug(f'{self.vulnerable_folder=}')
        logger.debug(f'{self.patched_folder=}')
        self.container = setup_container(self.path, self.settings)
        try:
            # Run the pynvim connection in a thread pool to avoid event loop conflicts
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            if loop is not None:
                # We're in an async context, use thread pool
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        pynvim.attach, 'tcp', address='127.0.0.1', port=self.port
                    )
                    self.nvim = future.result(timeout=30)
            else:
                # We're not in an async context, use direct connection
                self.nvim = pynvim.attach('tcp', address='127.0.0.1', port=self.port)

            logger.info(f'Connected to Neovim with {self.path}')
        except Exception as e:
            logger.critical(f'Error connecting to Neovim (127.0.0.1:{self.port}): {e}')
            sys.exit(1)

    def _search_symbol(self, symbol: str) -> tuple[str, int, int]:
        """Search for a symbol in the workspace using ripgrep in vimgrep format.

        Args:
            symbol: The symbol name to search for

        Returns:
            A tuple containing (file_path, line_number, column_number) of the first occurrence
        """
        self._check_init()
        cmd = [
            'rg',
            '--vimgrep',
            rf'\b{symbol}\b',  # exakter Wortbeginn/-ende
            '/codebase',  # Arbeitsverzeichnis
        ]
        logger.debug(f'Running: {" ".join(cmd)}')
        res = self.container.exec_run(cmd)

        if res.exit_code != 0:
            logger.error(f'Error running command: {res.output}')
            return (f'error running {" ".join(cmd)}', 0, 0)
        # Format: file:line:col:match
        hits = []
        for line in res.output.splitlines():
            parts = line.split(b':', 3)
            file_path, lineno, col = parts[0], int(parts[1]), int(parts[2])
            hits.append((file_path.decode(), lineno, col))
        logger.debug(f'Found {len(hits)} hits')

        # Using any of the hits
        file_path, line, col = hits[0]
        logger.info(f'Found at: {file_path=} {line=} {col=}')
        return file_path, line, col

    def get_file_content(
        self,
        file: str,
        offset: int = 0,
        limit: int = 50,
        encode: Literal['auto', 'raw'] = 'auto',
    ) -> str | None:
        """Get the content of a file from the container.

        Args:
            file: Path to the file within the container
            offset: Start line number (0-indexed, default: 0)
            limit: Maximum number of lines to return (default: 50)
            encode: Encoding type to use for decoding the file content (default: auto).
                Default 'auto' uses chardet to detect encoding, 'raw' returns bytes without decoding.

        Returns:
            The content of the file as a string
        """
        self._check_init()
        cmd = ['cat', file]
        logger.info(f'Running: {" ".join(cmd)}')
        res = self.container.exec_run(cmd)

        if res.exit_code != 0:
            logger.error(f'Error running command: {res.output}')
            return None

        raw_bytes = res.output
        if encode == 'raw':
            logger.debug(f'Returning raw bytes for file {file}')
            return raw_bytes
        detected = chardet.detect(raw_bytes)
        encoding = detected.get('encoding', 'utf-8')
        confidence = detected.get('confidence', 0)

        logger.debug(
            f"Detected encoding '{encoding}' with confidence {confidence:.2f} for file {file}"
        )

        try:
            content_lines = raw_bytes.decode(encoding).splitlines()[:]
            if offset + limit < len(content_lines):
                content_lines = content_lines[: offset + limit]
            content = '\n'.join(content_lines[offset:])
            return content
        except UnicodeDecodeError as e:
            logger.error(f'Failed to decode with detected encoding {encoding}: {e}')
            return None

    def get_codebase_structure(self, n: int = 3) -> str:
        """Get the structure of the codebase using the tree command.

        Args:
            n: Maximum depth level of the tree (default: 3)

        Returns:
            A string representation of the codebase directory structure
        """
        self._check_init()
        cmd = [
            'tree',
            '-L',
            str(n),
            '/codebase',  # Arbeitsverzeichnis
        ]
        logger.info(f'Running: {" ".join(cmd)}')
        res = self.container.exec_run(cmd)
        if res.exit_code != 0:
            logger.error(f'Error running command: {res.output}')
            return f'Error running command: {res.output}'
        logger.info(f'Tree got {len(res.output.splitlines())} entries')
        return res.output.decode()

    def get_symbols(self, file: str) -> list[tuple[str, str, int, tuple[int, int]]]:
        """Get all symbols (variables, functions, classes, etc.) in the specified file using LSP.

        Args:
            file: Path to the file to analyze

        Returns:
            A list of tuples containing symbol information:
            - symbol_name (str): Name of the symbol
            - symbol_type (str): Type of symbol (function, class, variable, etc.)
            - line_number (int): Line number where symbol is defined
            - range (tuple): Symbol range as (start_col, end_col)


        """
        self._check_init()
        self.nvim.command(f'edit {file}')
        sleep(NVIM_DELAY)
        # Get the symbols from the buffer
        self.nvim.command_output('lua vim.lsp.buf.document_symbol()')
        sleep(NVIM_DELAY)
        symbols = parse_symbols(self.nvim.current.buffer)

        logger.info(f'Found {len(symbols)} symbols in {file}')

        return symbols

    def get_references(
        self, symbol: str
    ) -> list[tuple[str, str, int, tuple[int, int]]]:
        """Get all references to the specified symbol in the codebase using LSP.

        Args:
            symbol: The symbol name to find references for

        Returns:
            A list of tuples containing reference information:
            - file_path (str): Path to the file containing the reference
            - code_context (str): The line of code containing the reference
            - line_number (int): Line number where reference appears
            - range (tuple): Reference range as (start_col, end_col)
        """
        self._check_init()
        file, line, col = self._search_symbol(symbol)
        references = []
        try:
            self.nvim.command(f'edit {file}')
            sleep(NVIM_DELAY)
            self.nvim.current.window.cursor = (line, col - 1)

            # Get the references from the buffer
            self.nvim.command_output('lua vim.lsp.buf.references()')
            sleep(NVIM_DELAY)
            references = parse_references(self.nvim.current.buffer)

            logger.info(f'Found {len(references)} references in {file}')
            logger.debug(f'{references=}')
        except Exception as e:
            logger.error(f'{type(e)=}\n{e}')

        return references

    def get_definition(self, symbol: str) -> tuple[str, str, int, int]:
        """Find the definition of a symbol using LSP and return its content and location.

        Args:
            symbol: The symbol name to find the definition for

        Returns:
            A tuple containing (definition_content, begin_line, end_line)
        """
        self._check_init()
        file, line, col = self._search_symbol(symbol)
        logger.info(f'open {file=} at {line=} {col=}')
        self.nvim.command(f'edit {file}')
        sleep(NVIM_DELAY)
        self.nvim.current.window.cursor = (line, col - 1)

        self.nvim.command('lua vim.lsp.buf.definition()')
        sleep(NVIM_DELAY)
        (b_line, b_col) = self.nvim.current.window.cursor
        logger.debug(f'Jumped to definition ({b_line=} {b_col=})')

        self.nvim.input(b']M')
        sleep(NVIM_DELAY)
        (e_line, e_col) = self.nvim.current.window.cursor
        logger.debug(f"']m' -> ({e_line=} {e_col=})")
        if self.nvim.current.line[e_col] == '{':
            self.nvim.input('%')
            sleep(NVIM_DELAY)
            (e_line, e_col) = self.nvim.current.window.cursor
            logger.debug(f"'%' -> ({e_line=} {e_col=})")

        res = '\n'.join(self.nvim.current.buffer[b_line - 1 : e_line])
        logger.debug(f'{res=}')

        return res, file, b_line, e_line

    def get_diff(
        self,
        options: Optional[list[str]] = None,
        file1: Optional[str] = None,
        file2: Optional[str] = None,
    ) -> list[str]:
        """Get diff output and split it into individual file diffs using regex.

        Returns:
            List of strings, each containing the diff for one file, or None if error
        """
        self._check_init()
        if not options:
            options = ['-u', '-w']
        if not file1:
            file1 = f'/codebase/{self.vulnerable_folder}'
        if not file2:
            file2 = f'/codebase/{self.patched_folder}'

        cmd = ['diff'] + options + [file1, file2]
        logger.info(f'Running: {" ".join(cmd)}')
        res = self.container.exec_run(cmd)

        if res.exit_code not in [0, 1]:
            logger.error(f'Error running command: {res.output}')
            return [f'Error running {" ".join(cmd)}:\n{res.output}']

        # Get the full diff output as string
        diff_output = res.output.decode()

        # Split using regex to find "diff " at the beginning of lines
        file_diffs = re.split(
            r'^(?=diff |Common subdirectories)', diff_output, flags=re.MULTILINE
        )

        # Remove empty strings and common subdirectories message
        file_diffs = [diff.strip() for diff in file_diffs if diff.strip()]

        logger.info(f'{len(file_diffs)} files altered')
        return file_diffs
