import re

import config.log

logger = config.log.get(__name__)
# Compile once at module load
_SYMBOL_PATTERN = re.compile(
    r'''
    ^            # start of string
    [^|]+        # filename (ignored)
    \|           # literal '|'
    (?P<line>\d+)        # capture line number
    \s+col\s+            # literal ' col '
    (?P<col_start>\d+)   # capture column start
    -                    # literal '-'
    (?P<col_end>\d+)     # capture column end
    \|                   # literal '|'
    \s*\[                # optional space + '['
    (?P<type>[^\]]+)     # capture type (up to ']')
    \]\s+                # ']' + space(s)
    (?P<name>\w+)        # capture name (alphanumeric + underscore)
    $            # end of string
    ''',
    re.VERBOSE
)


def parse_symbols(lines: list[str]) -> list[tuple[str, str, int, tuple[int, int]]]:
    """
    Parse symbol information from LSP output lines.

    Args:
        lines: List of strings containing symbol information in LSP format

    Returns:
        A list of tuples, each containing (name, type, line_no, (col_start, col_end))
    """
    parsed = []
    for line in lines:
        try:
            m = _SYMBOL_PATTERN.match(line)
            if not m:
                raise ValueError(f"Line not in expected format: {line!r}")
            name = m.group('name')
            sym_type = m.group('type')
            line_no = int(m.group('line'))
            col_start = int(m.group('col_start'))
            col_end = int(m.group('col_end'))
            parsed.append((name, sym_type, line_no, (col_start, col_end)))
        except ValueError as e:
            logger.warning(f"error parsing line {line}: {e}")
    parsed.sort(key=lambda x: x[1])
    return parsed


_REFERENCE_PATTERN = re.compile(
    r'''
    ^                           # start of string
    (?P<filename>[^|]+)         # filename (everything up to the first '|')
    \|                          # literal '|'
    (?P<line>\d+)               # line number
    \s+col\s+                   # literal ' col '
    (?P<col_start>\d+)          # column start
    -                           # literal '-'
    (?P<col_end>\d+)            # column end
    \|                          # literal '|'
    \s*                         # optional whitespace
    (?P<code>.+)                # the rest is the code snippet
    $                           # end of string
    ''',
    re.VERBOSE
)


def parse_references(lines: list[str]) -> list[tuple[str, str, int, tuple[int, int]]]:
    """
    Parse reference information from LSP output lines.

    Args:
        lines: List of strings containing reference information in LSP format

    Returns:
        A list of tuples, each containing (filename, code, line_no, (col_start, col_end))
    """
    parsed = []
    for line in lines:
        try:
            m = _REFERENCE_PATTERN.match(line)
            if not m:
                raise ValueError(f"Line not in expected format: {line!r}")
            filename = m.group('filename')
            line_no = int(m.group('line'))
            col_start = int(m.group('col_start'))
            col_end = int(m.group('col_end'))
            code = m.group('code')
            parsed.append((filename, code, line_no, (col_start, col_end)))
        except ValueError as e:
            logger.warning(f"error parsing line {line}: {e}")
    parsed.sort(key=lambda x: x[0])
    return parsed
