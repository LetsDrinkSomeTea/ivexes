"""Session Browser Package for IVEXES.

A modular, maintainable session database browser with enhanced formatting,
scrolling, and navigation capabilities.

Package Structure:
- config: Hotkey configuration and settings
- scroller: Message content scrolling functionality
- formatter: Message type-specific formatting
- browser: Main browser UI logic
- main: Entry point and command-line interface

Example Usage:
    from tools.session_browser import SessionBrowser

    browser = SessionBrowser('sessions.sqlite')
    browser.run()

    # Or use the command-line interface
    from tools.session_browser.main import main
    main()
"""

from .browser import SessionBrowser
from .config import HotkeyConfig, BrowserSettings
from .formatter import MessageFormatter
from .scroller import MessageScroller
from .main import main, launch_browser
from .database import SessionDatabase, get_database_stats

__all__ = [
    'SessionBrowser',
    'HotkeyConfig',
    'BrowserSettings',
    'MessageFormatter',
    'MessageScroller',
    'main',
    'launch_browser',
    'SessionDatabase',
    'get_database_stats',
]

__version__ = '2.0.0'
