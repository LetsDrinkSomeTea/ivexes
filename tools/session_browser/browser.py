"""Main browser UI logic for the session browser.

This module contains the core SessionBrowser class that orchestrates
the user interface, navigation, and interaction logic.
"""

import sys
import termios
import tty
from pathlib import Path
from typing import Optional, List

from rich.console import Console
from rich.panel import Panel

from ..database import SessionDatabase, Session, Message as DBMessage
from .config import HotkeyConfig, BrowserSettings
from .formatter import MessageFormatter
from .scroller import MessageScroller


def get_single_key():
    """Get a single keypress from the user without requiring Enter.

    Returns:
        The pressed key as a string, including escape sequences for special keys
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        # Handle special keys (escape sequences)
        if ch == '\x1b':  # ESC sequence
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class SessionBrowser:
    """Console-based browser for session databases.

    Provides an interactive interface for browsing session data with
    enhanced formatting, navigation, and scrolling capabilities.

    Attributes:
        db_path: Path to the SQLite database file
        db: SessionDatabase instance for data access
        sessions: List of available sessions
        console: Rich Console for output
        formatter: MessageFormatter for message display
        current_session_index: Index of currently selected session
        current_message_index: Index of currently displayed message
        current_page: Current page in session list
        message_scroller: Scroller for long message content

    Example:
        >>> browser = SessionBrowser('sessions.sqlite')
        >>> browser.run()  # Start interactive browsing
    """

    def __init__(self, db_path: str):
        """Initialize the browser with a database path.

        Args:
            db_path: Path to the SQLite database file

        Raises:
            FileNotFoundError: If database file doesn't exist
        """
        self.db_path = db_path
        self.db = SessionDatabase(db_path)
        self.sessions: List[Session] = []
        self.current_messages: List[DBMessage] = []
        self.console = Console()
        self.formatter = MessageFormatter()

        # Navigation state
        self.current_session_index = 0
        self.current_message_index = 0

        # Paging configuration
        self.sessions_per_page = BrowserSettings.SESSIONS_PER_PAGE
        self.current_page = 0

        # Message viewing state
        self.message_scroller: Optional[MessageScroller] = None

    def run(self) -> None:
        """Run the interactive browser.

        Starts the main browser loop, loading sessions and showing
        the main menu for user interaction.
        """
        self.load_sessions()
        self.show_main_menu()

    def load_sessions(self) -> None:
        """Load sessions from the database.

        Populates the sessions list with data from the database,
        handling any errors gracefully.
        """
        try:
            self.sessions = self.db.get_sessions()
        except Exception as e:
            self.console.print(f'[red]Error loading sessions: {e}[/red]')

    def show_main_menu(self) -> None:
        """Show the main interactive menu.

        Displays the session list and handles user navigation until
        the user chooses to quit.
        """
        while True:
            self.console.clear()
            self.console.print(
                f'[bold]IVEXES Session Browser - {Path(self.db_path).name}[/bold]\n'
            )

            if not self.sessions:
                self.console.print('[red]No sessions found in database[/red]')
                break

            self.display_sessions_table()
            self.show_navigation_help()

            try:
                key = get_single_key()
            except KeyboardInterrupt:
                break

            if HotkeyConfig.matches(key, 'QUIT'):
                break
            elif HotkeyConfig.matches(key, 'NEXT_SESSION'):
                self.next_session()
            elif HotkeyConfig.matches(key, 'PREV_SESSION'):
                self.previous_session()
            elif HotkeyConfig.matches(key, 'PREV_PAGE'):
                self.previous_page()
            elif HotkeyConfig.matches(key, 'NEXT_PAGE'):
                self.next_page()
            elif HotkeyConfig.matches(key, 'SEARCH'):
                self.search_sessions()
            elif HotkeyConfig.matches(key, 'SELECT_SESSION'):
                if self.sessions:
                    self.view_session(self.sessions[self.current_session_index])
            elif key.isdigit():
                self.select_session_by_number(key)

    def display_sessions_table(self) -> None:
        """Display sessions in a table format with paging.

        Shows a paginated table of sessions with session IDs, creation dates,
        message counts, and current selection indicator.
        """
        from rich.table import Table

        # Calculate page boundaries
        start_idx = self.current_page * self.sessions_per_page
        end_idx = min(start_idx + self.sessions_per_page, len(self.sessions))
        page_sessions = self.sessions[start_idx:end_idx]

        table = Table(title=f'Sessions (Page {self.current_page + 1})')
        table.add_column('Status', style='yellow', width=2, justify='right')
        table.add_column('#', style='cyan', width=6)
        table.add_column('Session ID', style='blue', max_width=50)
        table.add_column('Created', style='green')
        table.add_column('Messages', style='magenta', justify='right')

        for i, session in enumerate(page_sessions):
            global_idx = start_idx + i
            created = session.created_at.strftime('%Y-%m-%d %H:%M')
            session_id = session.session_id
            if len(session_id) > 47:
                session_id = session_id[:44] + '...'

            status = '→' if global_idx == self.current_session_index else ''

            table.add_row(
                status,
                str(global_idx + 1),
                session_id,
                created,
                str(session.message_count),
            )

        self.console.print(table)

    def show_navigation_help(self) -> None:
        """Show navigation help at the bottom of the screen.

        Displays current page/session information and available navigation commands.
        """
        total_pages = (
            len(self.sessions) + self.sessions_per_page - 1
        ) // self.sessions_per_page

        self.console.print(
            f'\n[dim]Page {self.current_page + 1}/{total_pages} | Session {self.current_session_index + 1}/{len(self.sessions)}[/dim]'
        )
        self.console.print('\n[bold]Navigation:[/bold]')
        self.console.print(
            f'• [cyan]{HotkeyConfig.get_help_text("NEXT_SESSION")} {HotkeyConfig.get_help_text("PREV_SESSION")}[/cyan] - Next/Previous session'
        )
        self.console.print(
            f'• [cyan]{HotkeyConfig.get_help_text("NEXT_PAGE")} {HotkeyConfig.get_help_text("PREV_PAGE")}[/cyan] - Previous/Next page'
        )
        self.console.print(
            f'• [cyan]Enter[/cyan] - View session | [cyan]{HotkeyConfig.get_help_text("SEARCH")}[/cyan] - Search | [cyan]{HotkeyConfig.get_help_text("QUIT")}[/cyan] - Quit'
        )

    def next_session(self) -> None:
        """Move to next session."""
        if self.current_session_index < len(self.sessions) - 1:
            self.current_session_index += 1
            # Update page if necessary
            new_page = self.current_session_index // self.sessions_per_page
            if new_page != self.current_page:
                self.current_page = new_page

    def previous_session(self) -> None:
        """Move to previous session."""
        if self.current_session_index > 0:
            self.current_session_index -= 1
            # Update page if necessary
            new_page = self.current_session_index // self.sessions_per_page
            if new_page != self.current_page:
                self.current_page = new_page

    def next_page(self) -> None:
        """Move to next page."""
        total_pages = (
            len(self.sessions) + self.sessions_per_page - 1
        ) // self.sessions_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            # Update session index to first session of new page
            self.current_session_index = self.current_page * self.sessions_per_page

    def previous_page(self) -> None:
        """Move to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            # Update session index to first session of new page
            self.current_session_index = self.current_page * self.sessions_per_page

    def search_sessions(self) -> None:
        """Search sessions interactively.

        Prompts for search term and displays matching sessions,
        allowing the user to select from results.
        """
        search_term = self.console.input('\n[bold]Search term:[/bold] ')
        if search_term:
            matching_sessions = self.db.search_sessions(search_term)
            if matching_sessions:
                self.console.clear()
                self.console.print(f"[bold]Search Results for '{search_term}'[/bold]\n")

                from rich.table import Table

                table = Table()
                table.add_column('#', style='cyan', width=4)
                table.add_column('Session ID', style='blue', max_width=50)
                table.add_column('Created', style='green')
                table.add_column('Messages', style='magenta', justify='right')

                for i, session in enumerate(matching_sessions):
                    created = session.created_at.strftime('%Y-%m-%d %H:%M')
                    session_id = session.session_id
                    if len(session_id) > 47:
                        session_id = session_id[:44] + '...'

                    table.add_row(
                        str(i + 1), session_id, created, str(session.message_count)
                    )

                self.console.print(table)

                self.console.print(
                    '\n[dim]Press session number or any other key to go back...[/dim]'
                )
                try:
                    key = get_single_key()
                    if key.isdigit():
                        session_num = int(key) - 1
                        if 0 <= session_num < len(matching_sessions):
                            self.view_session(matching_sessions[session_num])
                except KeyboardInterrupt:
                    pass
            else:
                self.console.print(
                    f"[yellow]No sessions found matching '{search_term}'[/yellow]"
                )
                self.console.print('\n[dim]Press any key to continue...[/dim]')
                try:
                    get_single_key()
                except KeyboardInterrupt:
                    pass

    def select_session_by_number(self, digit: str) -> None:
        """Handle digit input for session selection.

        Args:
            digit: First digit entered by user
        """
        # Allow multi-digit input
        number_str = digit
        self.console.print(f'\n[bold]Session number: {number_str}[/bold]', end='')

        while True:
            try:
                key = get_single_key()
                if HotkeyConfig.matches(key, 'SELECT_SESSION'):
                    break
                elif key.isdigit():
                    number_str += key
                    self.console.print(key, end='')
                elif HotkeyConfig.matches(key, 'BACKSPACE'):
                    if len(number_str) > 0:
                        number_str = number_str[:-1]
                        self.console.print('\b \b', end='')
                elif key == HotkeyConfig.ESCAPE:
                    return
            except KeyboardInterrupt:
                return

        try:
            session_num = int(number_str) - 1
            if 0 <= session_num < len(self.sessions):
                self.current_session_index = session_num
                # Update page to show selected session
                self.current_page = session_num // self.sessions_per_page
                self.view_session(self.sessions[session_num])
        except ValueError:
            pass

    def view_session(self, session: Session) -> None:
        """View messages in a specific session.

        Args:
            session: The session to view
        """
        try:
            self.current_messages = self.db.get_session_messages(session.session_id)
            self.current_message_index = 0

            while True:
                self.console.clear()
                self.console.print(f'[bold]Session: {session.session_id}[/bold]')
                self.console.print(
                    f'[dim]Created: {session.created_at.strftime("%Y-%m-%d %H:%M:%S")}[/dim]'
                )
                self.console.print(
                    f'[dim]Messages: {len(self.current_messages)}[/dim]\n'
                )

                if not self.current_messages:
                    self.console.print('[yellow]No messages in this session[/yellow]')
                    self.console.print('\n[dim]Press any key to go back...[/dim]')
                    try:
                        get_single_key()
                    except KeyboardInterrupt:
                        pass
                    break

                # Display current message
                message = self.current_messages[self.current_message_index]
                content, metadata = self.formatter.format_message(message)

                # Initialize or update scroller if content changed
                if (
                    self.message_scroller is None
                    or self.message_scroller.lines != content.split('\n')
                ):
                    terminal_height = self.console.size.height
                    self.message_scroller = MessageScroller(content, terminal_height)

                # Get visible content
                if self.message_scroller.is_scrollable():
                    visible_content = self.message_scroller.get_visible_content()
                else:
                    visible_content = content

                # Create message title with type indicator and scroll info
                title = self._create_message_title(message, self.message_scroller)

                panel = Panel(
                    visible_content,
                    title=title,
                    border_style=BrowserSettings.PANEL_BORDER_STYLE,
                )
                self.console.print(panel)

                # Show additional scroll help if applicable
                if self.message_scroller and self.message_scroller.is_scrollable():
                    scroll_help = f'[dim]📄 Scrollable content - Use {HotkeyConfig.get_help_text("SCROLL_DOWN")} to scroll[/dim]'
                    self.console.print(scroll_help)

                # Show navigation commands
                self._show_message_navigation_help()

                # Handle user input
                try:
                    key = get_single_key()
                except KeyboardInterrupt:
                    break

                if HotkeyConfig.matches(key, 'BACK') or HotkeyConfig.matches(
                    key, 'QUIT'
                ):
                    break
                elif HotkeyConfig.matches(key, 'NEXT_MESSAGE'):
                    if self.current_message_index < len(self.current_messages) - 1:
                        self.current_message_index += 1
                        self.message_scroller = None  # Reset scroller for new message
                elif HotkeyConfig.matches(key, 'PREV_MESSAGE'):
                    if self.current_message_index > 0:
                        self.current_message_index -= 1
                        self.message_scroller = None  # Reset scroller for new message
                elif HotkeyConfig.matches(key, 'FIRST_MESSAGE'):
                    self.current_message_index = 0
                    self.message_scroller = None  # Reset scroller for new message
                elif HotkeyConfig.matches(key, 'LAST_MESSAGE'):
                    self.current_message_index = len(self.current_messages) - 1
                    self.message_scroller = None  # Reset scroller for new message
                elif HotkeyConfig.matches(key, 'SCROLL_DOWN'):
                    if self.message_scroller:
                        self.message_scroller.page_down()
                elif HotkeyConfig.matches(key, 'SCROLL_UP'):
                    if self.message_scroller:
                        self.message_scroller.page_up()
                elif HotkeyConfig.matches(key, 'TOGGLE_METADATA'):
                    self.formatter.toggle_metadata_view()
                    self.message_scroller = None  # Reset scroller for new format

        except Exception as e:
            self.console.print(f'[red]Error viewing session: {e}[/red]')
            self.console.print('\n[dim]Press any key to continue...[/dim]')
            try:
                get_single_key()
            except KeyboardInterrupt:
                pass

    def _create_message_title(
        self, message: DBMessage, scroller: Optional[MessageScroller]
    ) -> str:
        """Create title for message panel with type indicator and scroll info.

        Args:
            message: The database message
            scroller: The message scroller (if any)

        Returns:
            Formatted title string
        """
        # Determine message type for title
        msg_type = message.message_data.get('type', 'message')
        type_indicator = BrowserSettings.TYPE_INDICATORS.get(msg_type, '💬')

        title = f'{type_indicator} Message {self.current_message_index + 1}/{len(self.current_messages)}'

        if self.formatter.show_metadata:
            title += ' (Metadata View)'

        # Add scroll position to title if content is scrollable
        if scroller and scroller.is_scrollable():
            scroll_info = scroller.get_scroll_position_info()
            title += f' | Lines {scroll_info["visible_start"]}-{scroll_info["visible_end"]}/{scroll_info["total_lines"]}'

        return title

    def _show_message_navigation_help(self) -> None:
        """Show navigation commands for message viewing."""
        self.console.print('\n[bold]Navigation:[/bold]')
        nav_help = []
        nav_help.append(
            f'• [cyan]{HotkeyConfig.get_help_text("NEXT_MESSAGE")} {HotkeyConfig.get_help_text("PREV_MESSAGE")}[/cyan] - Next/Previous message'
        )

        if self.message_scroller and self.message_scroller.is_scrollable():
            nav_help.append(
                f'• [cyan]{HotkeyConfig.get_help_text("SCROLL_DOWN")} {HotkeyConfig.get_help_text("SCROLL_UP")}[/cyan] - Scroll message'
            )

        nav_help.append(
            f'• [cyan]{HotkeyConfig.get_help_text("FIRST_MESSAGE")} {HotkeyConfig.get_help_text("LAST_MESSAGE")}[/cyan] - First/Last message'
        )
        nav_help.append(
            f'• [cyan]{HotkeyConfig.get_help_text("TOGGLE_METADATA")}[/cyan] - Toggle metadata | [cyan]{HotkeyConfig.get_help_text("BACK")}[/cyan] - Back'
        )

        for help_line in nav_help:
            self.console.print(help_line)

    def close(self) -> None:
        """Clean up resources."""
        if self.db:
            self.db.close()
