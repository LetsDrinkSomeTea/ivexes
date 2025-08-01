"""Code browser tools module for agent integration.

This module provides agent-compatible tools that wrap CodeBrowser functionality
for use within multi-agent systems. It includes tools for code analysis,
symbol searching, and structural exploration.
"""

from typing import Literal, cast, Optional

from agents import function_tool, Tool
from .code_browser import CodeBrowser
from ..config import Settings, create_settings

import logging

logger = logging.getLogger(__name__)


def create_code_browser_tools(
    code_browser: Optional[CodeBrowser] = None, settings: Optional[Settings] = None
) -> list[Tool]:
    """Create code browser tools with dependency injection.

    Args:
        code_browser: CodeBrowser instance from the creating agent.
        settings: Settings instance for creating a new CodeBrowser instance, if needed. Gets ignored if `code_browser` is provided and created from environment variables if not present.

    Returns:
        List of code browser tools configured with the provided browser instance.
    """
    if not settings:
        settings = create_settings()
    if not code_browser:
        code_browser = CodeBrowser(settings)

    @function_tool(strict_mode=True)
    def codebrowser_get_definition(symbol: str) -> str:
        """Find the definition of a symbol in the codebase.

        Args:
            symbol: The symbol name to find the definition for
        """
        logger.info(f'running codebrowser_get_definition({symbol=})')
        result = code_browser.get_definition(symbol)
        if result:
            definition, file, from_line, to_line = result
            return (
                f'Definition of {symbol} found in file {file} from line {from_line} to {to_line}:\n\n'
                f'<definition>\n{definition}\n</definition>'
            )
        else:
            return 'No definition found for symbol'

    @function_tool(strict_mode=True)
    def codebrowser_get_references(symbol: str) -> str:
        """Find all references to a symbol in the codebase.

        Args:
            symbol: The symbol name to find references for
        """
        logger.info(f'running codebrowser_get_references({symbol=})')
        results = code_browser.get_references(symbol)
        if results:
            references = []
            for result in results:
                file, code, line, (col_s, col_e) = result
                references.append(
                    f'<reference>\n{file}:{line}:{col_s}-{col_e}\t{code}\n</reference>'
                )
            return f'Found {len(results)} references for {symbol}:\n\n<references>\n{"\n".join(references)}\n</references>'
        else:
            return 'No references found for symbol'

    @function_tool(strict_mode=True)
    def codebrowser_get_symbols(file: str) -> str:
        """Get all symbols (variables, functions, classes) in a file.

        Args:
            file: Path to the file within the codebase to analyze
        """
        logger.info(f'running codebrowser_get_symbols({file=})')
        results = code_browser.get_symbols(file)
        if results:
            symbols = []
            for result in results:
                symbol_name, symbol_type, line_number, (col_s, col_e) = result
                symbols.append(
                    f'{symbol_name} ({symbol_type}) at {line_number}:{col_s}-{col_e}'
                )
            return f'Found {len(results)} symbols in file {file}:\n\n<symbols>\n{"\n".join(symbols)}\n</symbols>'
        else:
            return f'No symbols found in file {file}'

    @function_tool(strict_mode=True)
    def codebrowser_get_file_content(
        file: str,
        offset: int = 0,
        limit: int = 50,
        encode: Literal['auto', 'raw'] = 'auto',
    ) -> str:
        """Get the content of a file in the codebase.

        Args:
            file: Path to the file within the codebase to analyze
            offset: Optional: For text files, the 0-based line number to start reading from. Requires 'limit' to be set. Use for paginating through large files.
            limit: Optional: For text files, maximum number of lines to read. Use with 'offset' to paginate through large files. If omitted, reads the entire file (if feasible, up to a default limit).
            encode: Optional: Encoding type for the file content. Defaults to 'auto' which detects encoding, or 'raw' to return raw bytes.
        """
        logger.info(f'running codebrowser_get_file_content({file=})')
        result = code_browser.get_file_content(file, offset, limit, encode)
        if result:
            return f'Content of {file}:\n\n<content>\n{result}\n</content>'
        else:
            return f'File {file} not found, is the path correct?'

    @function_tool(strict_mode=True)
    def codebrowser_get_file_structure(depth: int = 3) -> str:
        """Get the tree of files in the codebase.

        Args:
            depth: Maximum depth level of the tree (default: 3)
        """
        logger.info(f'running codebrowser_get_file_structure({depth=})')
        result = code_browser.get_codebase_structure(depth)
        if result:
            return (
                f'Codebase file structure (depth {depth}):\n\n<tree>\n{result}\n</tree>'
            )
        else:
            return 'No files found in the codebase'

    @function_tool(strict_mode=True)
    def codebrowser_get_diff(
        file1: str = 'vulnerable_folder',
        file2: str = 'patched_folder',
        options: Optional[list[str]] = None,
    ) -> str:
        """Get the diff of the codebase using diff.

        Args:
            options: List of options for the diff command (default: ['-u', '-w'])
            file1: Path to the first file to compare (default: vulnerable_folder)
            file2: Path to the second file to compare (default: patched_folder)
        """
        if not options:
            options = ['-u', '-w']
        logger.info(f'running codebrowser_get_diff({options})')
        result = code_browser.get_diff(options, file1, file2)
        if result:
            return f'Diff between {file1} and {file2}:\n\n<diff>\n{"\n\n".join(result)}\n</diff>'
        else:
            return 'No differences found between codebases'

    return cast(
        list[Tool],
        [
            codebrowser_get_definition,
            codebrowser_get_references,
            codebrowser_get_symbols,
            codebrowser_get_file_content,
            codebrowser_get_file_structure,
            codebrowser_get_diff,
        ],
    )
