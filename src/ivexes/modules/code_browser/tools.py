from agents import function_tool
from ivexes.config.settings import settings
from ivexes.modules.code_browser.code_browser import CodeBrowser

import ivexes.config.log as log

logger = log.get(__name__)

if settings.codebase_path and settings.vulnerable_folder and settings.patched_folder:
    code_browser = CodeBrowser(
        settings.codebase_path, settings.vulnerable_folder, settings.patched_folder
    )
else:
    logger.warning(
        'Skipping code_browser tools because codebase_path, vulnerable_folder or patched_folder is not set in settings.'
    )


@function_tool
def codebrowser_get_definition(symbol: str) -> str:
    """
    Find the definition of a symbol in the codebase.

    Args:
        symbol: The symbol name to find the definition for
    """
    logger.info(f'running codebrowser_get_definition({symbol=})')
    result = code_browser.get_definition(symbol)
    if result:
        definition, file, from_line, to_line = result
        return (
            f'Definition of {symbol} found in file {file} from line {from_line} to {to_line}:\n'
            f'<definition>'
            f'{definition}'
            f'</definition>'
        )
    else:
        return 'No definition found'


@function_tool
def codebrowser_get_references(symbol: str) -> str:
    """
    Find all references to a symbol in the codebase.

    Args:
        symbol: The symbol name to find references for
    """
    logger.info(f'running codebrowser_get_references({symbol=})')
    results = code_browser.get_references(symbol)
    if results:
        references = []
        for result in results:
            file, code, line, (col_s, col_e) = result
            references.append(f'{file}:{line}:{col_s}-{col_e}\t{code}')
        return f'Found {len(results)} references:\n{"\n".join(references)}'
    else:
        return 'No References found'


@function_tool
def codebrowser_get_symbols(file: str) -> str:
    """
    Get all symbols (variables, functions, classes) in a file.

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
        return f'{"\n".join(symbols)}'
    else:
        return f'No symbols found in file {file}'


@function_tool
def codebrowser_get_file_content(
    file: str, from_line: int = 0, to_line: int = -1
) -> str:
    """
    Get the content of a file in the codebase.

    Args:
        file: Path to the file within the codebase to analyze
        from_line: Start line number (0-indexed, default: 0)
        to_line: End line number (0-indexed, -1 for all lines, default: -1)
    """
    logger.info(f'running codebrowser_get_file_content({file=})')
    result = code_browser.get_file_content(file, from_line, to_line)
    if result:
        return f'Content of {file}:\n<code>{result}</code>'
    else:
        return f'file {file} not found, is the path correct?'


@function_tool
def codebrowser_get_file_structure(depth: int = 3) -> str:
    """
    Get the tree of files in the codebase.

    Args:
        depth: Maximum depth level of the tree (default: 3)
    """
    logger.info(f'running codebrowser_get_file_structure({depth=})')
    result = code_browser.get_codebase_structure(depth)
    if result:
        return f'Tree of the codebase:\n<tree>{result}</tree>'
    else:
        return 'No files found in the codebase.'


@function_tool
def codebrowser_get_diff(
    file1: str = 'vulnerable_folder',
    file2: str = 'patched_folder',
    options: list[str] | None = None,
) -> str:
    """
    Get the diff of the codebase using diff.

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
        return f'Diff of the codebase:\n<diff>{result}</diff>'
    else:
        return 'No diff found in the codebase.'


code_browser_tools = (
    [
        codebrowser_get_definition,
        codebrowser_get_references,
        codebrowser_get_symbols,
        codebrowser_get_file_content,
        codebrowser_get_file_structure,
        codebrowser_get_diff,
    ]
    if settings.codebase_path and settings.vulnerable_folder and settings.patched_folder
    else []
)
