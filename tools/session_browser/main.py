"""Main entry point for the session browser application.

This module provides command-line interface functionality for the session browser,
making it easy to launch the browser with different database files.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .browser import SessionBrowser


def main(db_path: Optional[str] = None) -> None:
    """Run the session browser with command-line argument support.

    Args:
        db_path: Optional database path. If None, uses command-line args.
    """
    if db_path is None:
        parser = argparse.ArgumentParser(
            description='IVEXES Session Browser - Interactive TUI for browsing session databases',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s sessions.sqlite              # Browse sessions.sqlite
  %(prog)s /path/to/other.db           # Browse database at custom path
  
Navigation:
  j/↓ - Next session/message           k/↑ - Previous session/message
  h/← - Previous page/first message    l/→ - Next page/last message
  s - Search sessions                  m - Toggle metadata view
  Enter - Select session               q - Quit, b - Back
  d/PgDn - Scroll down                 u/PgUp - Scroll up
            """,
        )

        parser.add_argument(
            'database',
            nargs='?',
            default='sessions.sqlite',
            help='Path to the SQLite session database (default: sessions.sqlite)',
        )

        parser.add_argument('--version', action='version', version='%(prog)s 2.0.0')

        args = parser.parse_args()
        db_path = args.database

    # Validate database file exists
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"Error: Database file '{db_path}' not found.", file=sys.stderr)
        print(
            f'Please ensure the file exists or specify a different path.',
            file=sys.stderr,
        )
        sys.exit(1)

    if not db_file.is_file():
        print(f"Error: '{db_path}' is not a file.", file=sys.stderr)
        sys.exit(1)

    try:
        # Create and run the browser
        browser = SessionBrowser(str(db_file))
        browser.run()
    except KeyboardInterrupt:
        print('\nGoodbye!')
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        # Ensure terminal is restored to normal state
        try:
            import termios
            import sys

            termios.tcsetattr(
                sys.stdin.fileno(),
                termios.TCSADRAIN,
                termios.tcgetattr(sys.stdin.fileno()),
            )
        except:
            pass


def launch_browser(db_path: str) -> None:
    """Simple launcher function for programmatic use.

    Args:
        db_path: Path to the database file

    Example:
        >>> from tools.session_browser.main import launch_browser
        >>> launch_browser('my_sessions.sqlite')
    """
    main(db_path)


if __name__ == '__main__':
    main()
