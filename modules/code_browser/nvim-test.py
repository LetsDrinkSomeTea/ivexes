
#!/usr/bin/env python3
import sys
import subprocess
import pynvim
import os
import logging
from time import sleep


# Logging-Konfiguration
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def search_symbol(symbol, workspace):
    """Suche mit ripgrep (vimgrep-Format) im Workspace."""
    cmd = [
        "rg", "--vimgrep",
        fr"\b{symbol}\b",  # exakter Wortbeginn/-ende
        workspace
    ]
    logger.info(f"Running: {" ".join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    logger.debug(f"{proc=}")
    if proc.returncode != 0:
        return []
    # Format: file:line:col:match
    hits = []
    for line in proc.stdout.splitlines():
        parts = line.split(":", 3)
        file_path, lineno, col = parts[0], int(parts[1]), int(parts[2])
        hits.append((file_path.split('/', 1)[1], lineno, col))
    return hits


def find_definition(nvim: pynvim.Nvim, file, line, col) -> tuple[str, int, int]:
    """Open file at position, call LSP-Definition, return sync result."""
    logger.debug(f"open {file=} at {line=} {col=}")
    nvim.command(f"edit {file}")
    sleep(1)
    nvim.current.window.cursor = (line, col - 1)

    nvim.command('lua vim.lsp.buf.definition()')
    sleep(1)
    (b_line, b_col) = nvim.current.window.cursor
    logger.debug(f"Jumped to definition ({b_line=} {b_col=})")

    # nvim.input(b'vaB<Esc>')
    nvim.input(b']M')
    sleep(1)
    (e_line, e_col) = nvim.current.window.cursor
    logger.debug(f"']m' -> ({e_line=} {e_col=})")
    if nvim.current.line[e_col] == '{':
        nvim.input('%')
        sleep(1)
        (e_line, e_col) = nvim.current.window.cursor
        logger.debug(f"'%' -> ({e_line=} {e_col=})")

    
    res = "\n".join(nvim.current.buffer[b_line-1:e_line])
    logger.debug(f"{res=}")

    return (res, b_line, e_line)

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: get-def <FunctionName>")
        sys.exit(1)

    symbol = sys.argv[1]

    hits = search_symbol(symbol, "workspace")
    if not hits:
        logger.warning(f"Kein Vorkommen von '{symbol}' im Workspace gefunden.")
        sys.exit(1)

    file_path, line, col = hits[0]
    logger.info(f"Found at: %s:%d:%d", file_path, line, col)

    sock = os.path.join("workspace", "nvim.sock")
    try:
        nvim = pynvim.attach("socket", path=sock)
        logger.info("Attached to socket")
    except Exception as e:
        logger.error("Connection to '%s' failed: %s", sock, e)
        sys.exit(1)

    definition = find_definition(nvim, file_path, line, col)
    if not definition:
        logger.warning(f"No definition for '{symbol}' found.")
        sys.exit(1)

    text, from_line, to_line = definition
    print(f"{text}\n")
    logger.info(f"{from_line=} {to_line=}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.exception("Unerwarteter Fehler: %s", exc)
        sys.exit(1)

