#!/usr/bin/env python3
import sys
import subprocess
import pynvim
import os
from time import sleep

import config.log

from modules.code_browser.nvim import setup_container
from modules.code_browser.parser import parse_symbols, parse_references

logger = config.log.get(__name__)
NVIM_DELAY = 0.8

class CodeBrowser:
    """Code Browser for Neovim LSP."""

    def __init__(self, codebase: os.path, port: int = 8080):
        self.path = os.path.abspath(codebase)
        logger.info(f"Codebase: {self.path} starting container ...")
        self.container = setup_container(self.path)
        try:
            self.nvim = pynvim.attach("tcp", address="127.0.0.1", port=port)
            logger.info(f"Connected to Neovim with {self.path}")
        except Exception as e:
            logger.error(f"Error connecting to Neovim (127.0.0.1:{port}): {e}")
            sys.exit(1)


    def _search_symbol(self, symbol):
        """Suche mit ripgrep (vimgrep-Format) im Workspace."""
        cmd = [
            "rg", "--vimgrep",
            fr"\b{symbol}\b",  # exakter Wortbeginn/-ende
            '/codebase',  # Arbeitsverzeichnis
        ]
        logger.info(f"Running: {" ".join(cmd)}")
        res = self.container.exec_run(cmd)

        if res.exit_code != 0 :
            logger.error(f"Error running command: {res.output}")
            return []
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

    def get_file_content(self, file):
        """Get the content of the file."""
        cmd = [
            "cat",
            file,
        ]
        logger.info(f"Running: {" ".join(cmd)}")
        res = self.container.exec_run(cmd)
        if res.exit_code != 0:
            logger.error(f"Error running command: {res.output}")
            return []
        logger.info(f"Got {len(res.output.splitlines())} lines from {file}")
        return res.output.decode()

    def get_codebase_structure(self, n: int=3):
        """Get the structure of the codebase."""
        cmd = [
            "tree",
            "-L", str(n),
            "/codebase",  # Arbeitsverzeichnis
        ]
        logger.info(f"Running: {" ".join(cmd)}")
        res = self.container.exec_run(cmd)
        if res.exit_code != 0:
            logger.error(f"Error running command: {res.output}")
            return []
        logger.info(f"Tree got {len(res.output.splitlines())} entries in {self.path}")
        return res.output.decode()
    
    def get_symbols(self, file):
        """Get all symbols in the file."""
        self.nvim.command(f"edit {file}")
        sleep(NVIM_DELAY)

        # Get the symbols from the buffer
        self.nvim.command_output('lua vim.lsp.buf.document_symbol()')
        sleep(NVIM_DELAY)
        symbols = parse_symbols(self.nvim.current.buffer)


        logger.info(f"Found {len(symbols)} symbols in {file}")

        return symbols

    def get_references(self, symbol):
        """Get all references to the symbol at the given line and column."""
        file, line, col = self._search_symbol(symbol)
        self.nvim.command(f"edit {file}")
        sleep(NVIM_DELAY)
        self.nvim.current.window.cursor = (line, col - 1)

        # Get the references from the buffer
        self.nvim.command_output('lua vim.lsp.buf.references()')
        sleep(NVIM_DELAY)
        references = parse_references(self.nvim.current.buffer)

        logger.info(f"Found {len(references)} references in {file}")

        return references


    def get_definition(self, symbol) -> tuple[str, int, int]:
        """Open file at position, call LSP-Definition, return sync result."""
        file, line, col = self._search_symbol(symbol)
        logger.info(f"open {file=} at {line=} {col=}")
        self.nvim.command(f"edit {file}")
        sleep(NVIM_DELAY)
        self.nvim.current.window.cursor = (line, col - 1)

        self.nvim.command('lua vim.lsp.buf.definition()')
        sleep(NVIM_DELAY)
        (b_line, b_col) = self.nvim.current.window.cursor
        logger.debug(f"Jumped to definition ({b_line=} {b_col=})")

        # self.nvim.input(b'vaB<Esc>')
        self.nvim.input(b']M')
        sleep(NVIM_DELAY)
        (e_line, e_col) = self.nvim.current.window.cursor
        logger.debug(f"']m' -> ({e_line=} {e_col=})")
        if self.nvim.current.line[e_col] == '{':
            self.nvim.input('%')
            sleep(NVIM_DELAY)
            (e_line, e_col) = self.nvim.current.window.cursor
            logger.debug(f"'%' -> ({e_line=} {e_col=})")


        res = "\n".join(self.nvim.current.buffer[b_line-1:e_line])
        logger.debug(f"{res=}")

        return res, b_line, e_line
