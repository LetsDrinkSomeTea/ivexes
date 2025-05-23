from agents import function_tool
from config.settings import settings
from modules.code_browser.code_browser import CodeBrowser

code_browser = CodeBrowser(settings.codebase_path, settings.vulnerable_folder, settings.patched_folder)

@function_tool
def get_definition(symbol: str) -> str:
    """
    Find the definition of a symbol in the codebase.

    Args:
        symbol: The symbol name to find the definition for
        vulnerable_version: If True, search in the vulnerable codebase; otherwise, search in the patched codebase (default: True)
    """
    result = code_browser.get_definition(symbol)
    if result:
        definition, file, from_line, to_line = result
        return (f"Definition of {symbol} found in file {file} from line {from_line} to {to_line}:\n"
                f"<definition>"
                f"{definition}"
                f"</definition>")
    else:
        return "No definition found"


@function_tool
def get_references(symbol: str) -> str:
    """
    Find all references to a symbol in the codebase.

    Args:
        symbol: The symbol name to find references for
        vulnerable_version: If True, search in the vulnerable codebase; otherwise, search in the patched codebase (default: True)
    """
    results = code_browser.get_references(symbol)
    if results:
        references = []
        for result in results:
            file, code, line, (col_s, col_e) = result
            references.append(f"{file}:{line}:{col_s}-{col_e}\t{code}")
        return (f'Found {len(results)} references:\n'
                f'{"\n".join(references)}')
    else:
        return "No References found"


@function_tool
def get_symbols(file: str) -> str:
    """
    Get all symbols (variables, functions, classes) in a file.

    Args:
        file: Path to the file within the codebase to analyze
        vulnerable_version: If True, search in the vulnerable codebase; otherwise, search in the patched codebase (default: True)
    """
    results = code_browser.get_symbols(file)
    if results:
        symbols = []
        for result in results:
            symbol_name, symbol_type, line_number, (col_s, col_e) = result
            symbols.append(f"{symbol_name} ({symbol_type}) at {line_number}:{col_s}-{col_e}")
        return f'{"\n".join(symbols)}'
    else:
        return f"No symbols found in file {file}"


@function_tool
def get_file_content(file: str) -> str:
    """
    Get the content of a file in the codebase.

    Args:
        file: Path to the file within the codebase to analyze
        vulnerable_version: If True, search in the vulnerable codebase; otherwise, search in the patched codebase (default: True)
    """
    result = code_browser.get_file_content(file)
    if result:
        return f"Content of {file}:\n<code>{result}</code>"
    else:
        return f"file {file} not found, is the path correct?"


@function_tool
def get_file_structure(depth: int = 3) -> str:
    """
    Get the tree of files in the codebase.

    Args:
        depth: Maximum depth level of the tree (default: 3)
        vulnerable_version: If True, search in the vulnerable codebase; otherwise, search in the patched codebase (default: True)
    """
    result = code_browser.get_codebase_structure(depth)
    if result:
        return f"Tree of the codebase:\n<tree>{result}</tree>"
    else:
        return "No files found in the codebase."

@function_tool
def get_diff():
    """
    Get the diff of the codebase.
    """
    result = code_browser.get_diff()
    if result:
        return f"Diff of the codebase:\n<diff>{result}</diff>"
    else:
        return "No diff found in the codebase."

code_browser_tools = [
    get_definition,
    get_references,
    get_symbols,
    get_file_content,
    get_file_structure,
    get_diff,
]
