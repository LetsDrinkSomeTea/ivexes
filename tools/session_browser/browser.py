"""Main browser UI logic for the session browser.

This module contains the core SessionBrowser class that orchestrates
the user interface, navigation, and interaction logic.
"""

import sys
import termios
import tty
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel

from .database import SessionDatabase, Session, Message as DBMessage, WorkflowGroup
from .config import HotkeyConfig, BrowserSettings
from .formatter import MessageFormatter
from .scroller import MessageScroller


def get_single_key() -> str:
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

    def __init__(self, db_path: str) -> None:
        """Initialize the browser with a database path.

        Args:
            db_path: Path to the SQLite database file

        Raises:
            FileNotFoundError: If database file doesn't exist
        """
        self.db_path = db_path
        self.db = SessionDatabase(db_path)
        self.sessions: List[Session] = []
        self.workflow_groups: List[WorkflowGroup] = []
        self.current_messages: List[DBMessage] = []
        self.current_messages_only_files: List[DBMessage] = []
        self.console = Console()
        self.formatter = MessageFormatter()

        # View mode state
        self.workflow_mode: bool = (
            True  # False = individual sessions, True = workflow groups
        )

        # Navigation state
        self.current_session_index: int = 0
        self.current_message_index: int = 0

        # Paging configuration
        self.sessions_per_page: int = BrowserSettings.SESSIONS_PER_PAGE
        self.current_page: int = 0

        # Message viewing state
        self.message_scroller: Optional[MessageScroller] = None

        self.show_only_files: bool = False  # Show only file creation messages

    def run(self) -> None:
        """Run the interactive browser.

        Starts the main browser loop, loading sessions and showing
        the main menu for user interaction.
        """
        self.load_sessions()
        self.show_main_menu()

    def load_sessions(self) -> None:
        """Load sessions and workflow groups from the database.

        Populates both sessions and workflow groups lists with data from the database,
        handling any errors gracefully.
        """
        try:
            self.sessions = self.db.get_sessions()
            self.workflow_groups = self.db.get_workflow_groups()
        except Exception as e:
            self.console.print(f'[red]Error loading sessions: {e}[/red]')

    def show_main_menu(self) -> None:
        """Show the main interactive menu.

        Displays the session list and handles user navigation until
        the user chooses to quit.
        """
        while True:
            self.console.clear()
            mode_text = (
                'Workflow Groups' if self.workflow_mode else 'Individual Sessions'
            )
            self.console.print(
                f'[bold]IVEXES Session Browser - {Path(self.db_path).name} ({mode_text})[/bold]\n'
            )

            current_list = self.workflow_groups if self.workflow_mode else self.sessions
            if not current_list:
                list_type = 'workflow groups' if self.workflow_mode else 'sessions'
                self.console.print(f'[red]No {list_type} found in database[/red]')
                break

            self.display_sessions_table()
            self.show_navigation_help()

            try:
                key = get_single_key()
            except KeyboardInterrupt:
                break

            if HotkeyConfig.matches(key, 'QUIT'):
                break
            elif HotkeyConfig.matches(key, 'TOGGLE_WORKFLOW_MODE'):
                self.toggle_workflow_mode()
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
                if current_list:
                    if self.workflow_mode:
                        self.view_workflow(
                            self.workflow_groups[self.current_session_index]
                        )
                    else:
                        self.view_session(self.sessions[self.current_session_index])
            elif key.isdigit():
                self.select_session_by_number(key)

    def display_sessions_table(self) -> None:
        """Display sessions or workflow groups in a table format with paging.

        Shows a paginated table with appropriate columns based on current mode.
        """
        from rich.table import Table

        current_list = self.workflow_groups if self.workflow_mode else self.sessions

        # Calculate page boundaries
        start_idx = self.current_page * self.sessions_per_page
        end_idx = min(start_idx + self.sessions_per_page, len(current_list))
        page_items = current_list[start_idx:end_idx]

        if self.workflow_mode:
            table = Table(title=f'Workflow Groups (Page {self.current_page + 1})')
            table.add_column('', style='yellow', width=2, justify='right')
            table.add_column('#', style='cyan', width=6)
            table.add_column('Workflow Name', style='blue')
            table.add_column('Created', style='green')
            table.add_column('Agents', style='magenta', justify='right')
            table.add_column('Messages', style='magenta', justify='right')

            for i, workflow_group in enumerate(page_items):
                global_idx = start_idx + i
                created = workflow_group.created_at.strftime('%Y-%m-%d %H:%M')
                workflow_name = workflow_group.display_name

                status = '→' if global_idx == self.current_session_index else ''
                agent_count = len(workflow_group.agent_names)

                table.add_row(
                    status,
                    str(global_idx + 1),
                    workflow_name,
                    created,
                    str(agent_count),
                    str(workflow_group.total_messages),
                )
        else:
            table = Table(title=f'Sessions (Page {self.current_page + 1})')
            table.add_column('Status', style='yellow', width=2, justify='right')
            table.add_column('#', style='cyan', width=6)
            table.add_column('Session ID', style='blue', max_width=50)
            table.add_column('Created', style='green')
            table.add_column('Messages', style='magenta', justify='right')

            for i, session in enumerate(page_items):
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
        current_list = self.workflow_groups if self.workflow_mode else self.sessions
        total_pages = (
            len(current_list) + self.sessions_per_page - 1
        ) // self.sessions_per_page

        item_type = 'workflow' if self.workflow_mode else 'session'
        self.console.print(
            f'\n[dim]Page {self.current_page + 1}/{total_pages} | {item_type.title()} {self.current_session_index + 1}/{len(current_list)}[/dim]'
        )
        self.console.print('\n[bold]Navigation:[/bold]')
        self.console.print(
            f'• [cyan]{HotkeyConfig.get_help_text("NEXT_SESSION")} {HotkeyConfig.get_help_text("PREV_SESSION")}[/cyan] - Next/Previous {item_type}'
        )
        self.console.print(
            f'• [cyan]{HotkeyConfig.get_help_text("NEXT_PAGE")} {HotkeyConfig.get_help_text("PREV_PAGE")}[/cyan] - Previous/Next page'
        )
        self.console.print(
            f'• [cyan]Enter[/cyan] - View {item_type} | [cyan]{HotkeyConfig.get_help_text("SEARCH")}[/cyan] - Search | [cyan]{HotkeyConfig.get_help_text("TOGGLE_WORKFLOW_MODE")}[/cyan] - Toggle mode | [cyan]{HotkeyConfig.get_help_text("QUIT")}[/cyan] - Quit'
        )

    def next_session(self) -> None:
        """Move to next session/workflow."""
        current_list = self.workflow_groups if self.workflow_mode else self.sessions
        if self.current_session_index < len(current_list) - 1:
            self.current_session_index += 1
            # Update page if necessary
            new_page = self.current_session_index // self.sessions_per_page
            if new_page != self.current_page:
                self.current_page = new_page

    def previous_session(self) -> None:
        """Move to previous session/workflow."""
        if self.current_session_index > 0:
            self.current_session_index -= 1
            # Update page if necessary
            new_page = self.current_session_index // self.sessions_per_page
            if new_page != self.current_page:
                self.current_page = new_page

    def next_page(self) -> None:
        """Move to next page."""
        current_list = self.workflow_groups if self.workflow_mode else self.sessions
        total_pages = (
            len(current_list) + self.sessions_per_page - 1
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

    def toggle_workflow_mode(self) -> None:
        """Toggle between individual sessions and workflow groups view."""
        self.workflow_mode = not self.workflow_mode
        # Reset navigation state when switching modes
        self.current_session_index = 0
        self.current_page = 0

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
            current_list = self.workflow_groups if self.workflow_mode else self.sessions
            if 0 <= session_num < len(current_list):
                self.current_session_index = session_num
                # Update page to show selected session
                self.current_page = session_num // self.sessions_per_page
                if self.workflow_mode:
                    self.view_workflow(self.workflow_groups[session_num])
                else:
                    self.view_session(self.sessions[session_num])
        except ValueError:
            pass

    def view_session(self, session: Session) -> None:
        """View messages in a specific session.

        Args:
            session: The session to view
        """
        try:
            # Only load messages if not already set (for workflow groups)
            if not hasattr(session, 'workflow_group'):
                self.current_messages = self.db.get_session_messages(session.session_id)
            self.current_message_index = 0
            self.show_only_files = False

            self.current_messages_only_files = [
                x
                for x in self.current_messages
                if x.message_data.get('name', None) == 'sandbox_write_file'
            ]

            while True:
                self.console.clear()

                if self.show_only_files:
                    messages = self.current_messages_only_files
                else:
                    messages = self.current_messages

                # Check if this is a workflow session
                is_workflow = hasattr(session, 'workflow_group')
                if is_workflow:
                    workflow_group = session.workflow_group
                    self.console.print(f'[bold]Workflow: {session.session_id}[/bold]')
                    self.console.print(
                        f'[dim]Created: {session.created_at.strftime("%Y-%m-%d %H:%M:%S")}[/dim]'
                    )
                    self.console.print(
                        f'[dim]Agents: {", ".join(workflow_group.agent_names)}[/dim]'
                    )
                    self.console.print(f'[dim]Total Messages: {len(messages)}[/dim]\n')
                else:
                    self.console.print(f'[bold]Session: {session.session_id}[/bold]')
                    self.console.print(
                        f'[dim]Created: {session.created_at.strftime("%Y-%m-%d %H:%M:%S")}[/dim]'
                    )
                    self.console.print(f'[dim]Messages: {len(messages)}[/dim]\n')

                if not messages:
                    if self.show_only_files:
                        self.console.print(
                            '[yellow]No file creation messages in this session[/yellow]'
                        )
                        self.console.print('\n[dim]Press any key to go back...[/dim]')
                    else:
                        self.console.print(
                            '[yellow]No messages in this session[/yellow]'
                        )
                        self.console.print('\n[dim]Press any key to go back...[/dim]')
                    try:
                        get_single_key()
                    except KeyboardInterrupt:
                        pass
                    if self.show_only_files:
                        self.show_only_files = False
                        continue
                    else:
                        break

                # Display current message
                message = messages[self.current_message_index]
                content, metadata = self.formatter.format_message(message)

                # Add agent context for workflow sessions
                is_workflow = hasattr(session, 'workflow_group')
                if is_workflow:
                    agent_name = message.agent_name
                    if agent_name:
                        content = (
                            f'[bold cyan]Agent: {agent_name}[/bold cyan]\n{content}'
                        )

                # Always recreate scroller when content changes (including format changes)
                terminal_height = self.console.size.height
                current_content_lines = content.split('\n')

                # Check if we need to create/update scroller
                if (
                    self.message_scroller is None
                    or self.message_scroller.lines != current_content_lines
                ):
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
                    scroll_help = f'[dim]📄 Scrollable content - Use {HotkeyConfig.get_help_text("SCROLL_DOWN")} {HotkeyConfig.get_help_text("SCROLL_UP")} to scroll[/dim]'
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
                    if self.current_message_index < len(messages) - 1:
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
                    self.current_message_index = len(messages) - 1
                    self.message_scroller = None  # Reset scroller for new message
                elif HotkeyConfig.matches(key, 'SCROLL_DOWN'):
                    if self.message_scroller:
                        self.message_scroller.page_down()
                elif HotkeyConfig.matches(key, 'SCROLL_UP'):
                    if self.message_scroller:
                        self.message_scroller.page_up()
                elif HotkeyConfig.matches(key, 'TOGGLE_METADATA'):
                    self.formatter.toggle_metadata_view()
                elif HotkeyConfig.matches(key, 'TOGGLE_ONLY_FILE_CREATION'):
                    self.show_only_files = not self.show_only_files
                    self.current_message_index = 0
                elif HotkeyConfig.matches(key, 'SAVE_TO_FILE'):
                    self._save_content_to_file(content)
                elif HotkeyConfig.matches(key, 'COPY_TO_CLIPBOARD'):
                    self._copy_to_clipboard(content)

        except Exception as e:
            self.console.print(f'[red]Error viewing session: {e}[/red]')
            self.console.print('\n[dim]Press any key to continue...[/dim]')
            try:
                get_single_key()
            except KeyboardInterrupt:
                pass

    def _copy_to_clipboard(self, content: str) -> None:
        """Copy the current message content to the clipboard.

        Uses the rich console's clipboard functionality to copy content.

        Args:
            content: The message content to copy
        """
        try:
            import pyperclip

            lines = content.splitlines(True)
            content = ''.join(lines[3:])

            pyperclip.copy(content)
            self.console.print('[green]Content copied to clipboard![/green]')
            get_single_key()
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                f'[red]pyperclip module not found. Please install it to use clipboard functionality.[/red]'
            )

    def _save_content_to_file(self, content: str) -> None:
        """Save the current message content to a file.

        Prompts the user for a filename and saves the content to that file.

        Args:
            content: The message content to save
        """
        filename = self.console.input('\n[bold]Enter filename to save content: [/bold]')
        if not filename:
            self.console.print('[red]No filename provided. Aborting.[/red]')
            return

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.console.print(f'[green]Content saved to {filename}[/green]')
        except Exception as e:
            self.console.print(f'[red]Error saving content: {e}[/red]')

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

        if self.show_only_files:
            title = f'{type_indicator} File Creation Message {self.current_message_index + 1}/{len(self.current_messages_only_files)}'
        else:
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
        nav_help.append(
            f'• [cyan]{HotkeyConfig.get_help_text("TOGGLE_ONLY_FILE_CREATION")}[/cyan] - Toggle file creation only'
        )

        for help_line in nav_help:
            self.console.print(help_line)

    def view_workflow(self, workflow_group: WorkflowGroup) -> None:
        """View messages in a workflow group by reusing session viewing logic."""

        # Create a temporary session-like object for compatibility
        class WorkflowSession:
            def __init__(self, workflow_group: WorkflowGroup) -> None:
                self.session_id = workflow_group.display_name
                self.created_at = workflow_group.created_at
                self.workflow_group = workflow_group

        temp_session = WorkflowSession(workflow_group)

        # Override current_messages with workflow messages
        self.current_messages = self.db.get_workflow_messages(workflow_group)

        # Call existing view_session method with our temp session
        self.view_session(temp_session)

    def close(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'db') and self.db:
            self.db.close()
