#!/usr/bin/env python3
import os
import chardet
import sys
from time import sleep

import pynvim

import ivexes.config.log as log
from ivexes.modules.code_browser.nvim import setup_container
from ivexes.modules.code_browser.parser import parse_symbols, parse_references

logger = log.get(__name__)
NVIM_DELAY = 0.5


class CodeBrowser:
    """Code Browser for Neovim LSP."""

    def __init__(self, codebase: str, vulnerable_folder: str, patched_folder: str, port: int = 8080) -> None:
        """
        Initialize the CodeBrowser with a codebase path and port.

        Args:
            codebase: Path to the codebase directory
            port: Port number for Neovim connection
        """
        self.path = os.path.abspath(codebase)
        self.vulnerable_folder = os.path.basename(vulnerable_folder)
        self.patched_folder = os.path.basename(patched_folder)
        logger.info(f"Codebase: {self.path} starting container ...")
        logger.debug(f'{self.vulnerable_folder=}')
        logger.debug(f'{self.patched_folder=}')
        self.container = setup_container(self.path)
        try:
            self.nvim = pynvim.attach("tcp", address="127.0.0.1", port=port)
            logger.info(f"Connected to Neovim with {self.path}")
        except Exception as e:
            logger.error(f"Error connecting to Neovim (127.0.0.1:{port}): {e}")
            sys.exit(1)

    def _search_symbol(self, symbol: str) -> tuple[str, int, int] | None:
        """
        Search for a symbol in the workspace using ripgrep in vimgrep format.

        Args:
            symbol: The symbol name to search for

        Returns:
            A tuple containing (file_path, line_number, column_number) of the first occurrence
        """
        cmd = ["rg", "--vimgrep", fr"\b{symbol}\b",  # exakter Wortbeginn/-ende
               '/codebase',  # Arbeitsverzeichnis
               ]
        logger.debug(f"Running: {' '.join(cmd)}")
        res = self.container.exec_run(cmd)

        if res.exit_code != 0:
            logger.error(f"Error running command: {res.output}")
            return None
        # Format: file:line:col:match
        hits = []
        for line in res.output.splitlines():
            parts = line.split(b":", 3)
            file_path, lineno, col = parts[0], int(parts[1]), int(parts[2])
            hits.append((file_path.decode(), lineno, col))
        logger.debug(f"Found {len(hits)} hits")

        # Using any of the hits
        file_path, line, col = hits[0]
        logger.info(f"Found at: {file_path=} {line=} {col=}")
        return file_path, line, col

    def get_file_content(self, file: str, from_line: int = 0, to_line: int = -1) -> str | None:
        """
        Get the content of a file from the container.

        Args:
            file: Path to the file within the container
            from_line: Start line number (0-indexed, default: 0)
            to_line: End line number (0-indexed, -1 for all lines, default: -1)

        Returns:
            The content of the file as a string
        """
        cmd = ["cat", file]
        logger.info(f"Running: {' '.join(cmd)}")
        res = self.container.exec_run(cmd)

        if res.exit_code != 0:
            logger.error(f"Error running command: {res.output}")
            return None

        raw_bytes = res.output
        detected = chardet.detect(raw_bytes)
        encoding = detected.get("encoding", "utf-8")
        confidence = detected.get("confidence", 0)

        logger.debug(f"Detected encoding '{encoding}' with confidence {confidence:.2f} for file {file}")

        try:
            content_lines = raw_bytes.decode(encoding).splitlines()[:]
            if to_line != -1 and to_line < len(content_lines):
                content_lines = content_lines[:to_line]
            content = "\n".join(content_lines[from_line:])
            return content
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode with detected encoding {encoding}: {e}")
            return None

    def get_codebase_structure(self, n: int = 3) -> str | None:
        """
        Get the structure of the codebase using the tree command.

        Args:
            n: Maximum depth level of the tree (default: 3)

        Returns:
            A string representation of the codebase directory structure
        """
        cmd = [
            "tree",
            "-L", str(n),
            "/codebase",  # Arbeitsverzeichnis
        ]
        logger.info(f"Running: {' '.join(cmd)}")
        res = self.container.exec_run(cmd)
        if res.exit_code != 0:
            logger.error(f"Error running command: {res.output}")
            return None
        logger.info(f"Tree got {len(res.output.splitlines())} entries")
        return res.output.decode()

    def get_symbols(self, file: str) -> list[tuple[str, str, int, tuple[int, int]]]:
        """
        Get all symbols (variables, functions, classes, etc.) in the specified file using LSP.

        Args:
            file: Path to the file to analyze

        Returns:
            A list of tuples containing symbol information:
            - symbol_name (str): Name of the symbol
            - symbol_type (str): Type of symbol (function, class, variable, etc.)
            - line_number (int): Line number where symbol is defined
            - range (tuple): Symbol range as (start_col, end_col)
            
            
        """
        self.nvim.command(f"edit {file}")
        sleep(NVIM_DELAY)
        # Get the symbols from the buffer
        self.nvim.command_output('lua vim.lsp.buf.document_symbol()')
        sleep(NVIM_DELAY)
        symbols = parse_symbols(self.nvim.current.buffer)

        logger.info(f"Found {len(symbols)} symbols in {file}")

        return symbols

    def get_references(self, symbol: str) -> list[tuple[str, str, int, tuple[int, int]]]:
        """
        Get all references to the specified symbol in the codebase using LSP.

        Args:
            symbol: The symbol name to find references for

        Returns:
            A list of tuples containing reference information:
            - file_path (str): Path to the file containing the reference
            - code_context (str): The line of code containing the reference
            - line_number (int): Line number where reference appears
            - range (tuple): Reference range as (start_col, end_col)
        """
        file, line, col = self._search_symbol(symbol)
        try: 
            self.nvim.command(f"edit {file}")
            sleep(NVIM_DELAY)
            self.nvim.current.window.cursor = (line, col - 1)

            # Get the references from the buffer
            self.nvim.command_output('lua vim.lsp.buf.references()')
            sleep(NVIM_DELAY)
            references = parse_references(self.nvim.current.buffer)

            logger.info(f"Found {len(references)} references in {file}")
            logger.debug(f"{references=}")
        except Exception as e:
            logger.error(f"{type(e)=}\n{e}")

        return references

    def get_definition(self, symbol: str) -> tuple[str, str, int, int]:
        """
        Find the definition of a symbol using LSP and return its content and location.

        Args:
            symbol: The symbol name to find the definition for

        Returns:
            A tuple containing (definition_content, begin_line, end_line)
        """
        file, line, col = self._search_symbol(symbol)
        logger.info(f"open {file=} at {line=} {col=}")
        self.nvim.command(f"edit {file}")
        sleep(NVIM_DELAY)
        self.nvim.current.window.cursor = (line, col - 1)

        self.nvim.command('lua vim.lsp.buf.definition()')
        sleep(NVIM_DELAY)
        (b_line, b_col) = self.nvim.current.window.cursor
        logger.debug(f"Jumped to definition ({b_line=} {b_col=})")

        self.nvim.input(b']M')
        sleep(NVIM_DELAY)
        (e_line, e_col) = self.nvim.current.window.cursor
        logger.debug(f"']m' -> ({e_line=} {e_col=})")
        if self.nvim.current.line[e_col] == '{':
            self.nvim.input('%')
            sleep(NVIM_DELAY)
            (e_line, e_col) = self.nvim.current.window.cursor
            logger.debug(f"'%' -> ({e_line=} {e_col=})")

        res = "\n".join(self.nvim.current.buffer[b_line - 1:e_line])
        logger.debug(f"{res=}")

        return res, file, b_line, e_line

    def get_diff(self):
        cmd = [
            "git", "diff",
            "-W",  # function context
            "-w",  # ignore whitespaces
            "--no-index",
            "--exit-code",
            "--no-prefix",
            self.vulnerable_folder,
            self.patched_folder
        ]
        logger.info(f"Running: {' '.join(cmd)}")
        res = self.container.exec_run(cmd)
        if res.exit_code not in [0, 1]:
            logger.error(f"Error running command: {res.output}")
            return None
        file_diffs = res.output.decode().split("diff --git ")[1:]
        logger.info(f'{len(file_diffs)} files altered')
        return file_diffs
