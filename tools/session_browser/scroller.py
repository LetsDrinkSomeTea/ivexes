"""Message scrolling functionality for the session browser.

This module provides scrolling capabilities for long message content,
allowing users to navigate through content that exceeds the terminal height.
"""

from typing import Optional
from .config import BrowserSettings


class MessageScroller:
    r"""Handles scrolling for long message content.

    Provides page-based and line-based scrolling functionality with
    automatic adaptation to terminal dimensions.

    Attributes:
        lines: List of content lines
        current_line: Current top line being displayed (0-based)
        page_size: Number of lines displayed per page
        total_lines: Total number of lines in content

    Example:
        >>> content = 'Line 1\\nLine 2\\nLine 3\\n...Line 100'
        >>> scroller = MessageScroller(content, terminal_height=25)
        >>> scroller.is_scrollable()
        True
        >>> scroller.page_down()
        True
        >>> scroller.get_scroll_indicator()
        '[dim]Lines 16-30 of 100[/dim]'
    """

    def __init__(self, content: str, terminal_height: Optional[int] = None):
        """Initialize the scroller with content and terminal dimensions.

        Args:
            content: The message content to scroll through
            terminal_height: Height of the terminal window. If None, uses default.
        """
        self.lines = content.split('\n')
        self.current_line = 0
        self.total_lines = len(self.lines)

        # Calculate page size based on terminal height
        if terminal_height is None:
            terminal_height = BrowserSettings.DEFAULT_TERMINAL_HEIGHT

        self.page_size = max(
            BrowserSettings.MIN_PAGE_SIZE,
            terminal_height - BrowserSettings.UI_RESERVED_LINES,
        )

    def scroll_down(self, lines: int = 1) -> bool:
        """Scroll down by specified number of lines.

        Args:
            lines: Number of lines to scroll down

        Returns:
            True if scrolling occurred, False if already at bottom
        """
        max_start = max(0, self.total_lines - self.page_size)
        old_line = self.current_line
        self.current_line = min(max_start, self.current_line + lines)
        return self.current_line != old_line

    def scroll_up(self, lines: int = 1) -> bool:
        """Scroll up by specified number of lines.

        Args:
            lines: Number of lines to scroll up

        Returns:
            True if scrolling occurred, False if already at top
        """
        old_line = self.current_line
        self.current_line = max(0, self.current_line - lines)
        return self.current_line != old_line

    def page_down(self) -> bool:
        """Scroll down by one page.

        Returns:
            True if scrolling occurred, False if already at bottom
        """
        return self.scroll_down(self.page_size)

    def page_up(self) -> bool:
        """Scroll up by one page.

        Returns:
            True if scrolling occurred, False if already at top
        """
        return self.scroll_up(self.page_size)

    def scroll_to_top(self) -> bool:
        """Scroll to the very top of the content.

        Returns:
            True if scrolling occurred, False if already at top
        """
        old_line = self.current_line
        self.current_line = 0
        return self.current_line != old_line

    def scroll_to_bottom(self) -> bool:
        """Scroll to the very bottom of the content.

        Returns:
            True if scrolling occurred, False if already at bottom
        """
        old_line = self.current_line
        self.current_line = max(0, self.total_lines - self.page_size)
        return self.current_line != old_line

    def get_visible_content(self) -> str:
        """Get the currently visible portion of content.

        Returns:
            String containing the lines currently visible on screen
        """
        end_line = min(self.total_lines, self.current_line + self.page_size)
        return '\n'.join(self.lines[self.current_line : end_line])

    def get_scroll_indicator(self) -> str:
        """Get scroll position indicator text.

        Returns:
            Formatted string showing current position (e.g., "Lines 1-15 of 100").
            Returns empty string if content is not scrollable.
        """
        if not self.is_scrollable():
            return ''

        start = self.current_line + 1
        end = min(self.total_lines, self.current_line + self.page_size)
        return f'[dim]Lines {start}-{end} of {self.total_lines}[/dim]'

    def get_scroll_position_info(self) -> dict:
        """Get detailed scroll position information.

        Returns:
            Dictionary with detailed scroll position data:
            - current_line: Current top line (0-based)
            - visible_start: First visible line (1-based)
            - visible_end: Last visible line (1-based)
            - total_lines: Total number of lines
            - page_size: Lines per page
            - can_scroll_up: Whether scrolling up is possible
            - can_scroll_down: Whether scrolling down is possible
            - scroll_percentage: Scroll position as percentage (0-100)
        """
        visible_start = self.current_line + 1
        visible_end = min(self.total_lines, self.current_line + self.page_size)

        # Calculate scroll percentage
        if self.total_lines <= self.page_size:
            scroll_percentage = 0  # Content fits on one page
        else:
            max_scroll = self.total_lines - self.page_size
            scroll_percentage = (
                (self.current_line / max_scroll) * 100 if max_scroll > 0 else 0
            )

        return {
            'current_line': self.current_line,
            'visible_start': visible_start,
            'visible_end': visible_end,
            'total_lines': self.total_lines,
            'page_size': self.page_size,
            'can_scroll_up': self.current_line > 0,
            'can_scroll_down': self.current_line < (self.total_lines - self.page_size),
            'scroll_percentage': round(scroll_percentage, 1),
        }

    def is_scrollable(self) -> bool:
        """Check if content requires scrolling.

        Returns:
            True if content is longer than one page, False otherwise
        """
        return self.total_lines > self.page_size

    def get_line_count(self) -> int:
        """Get total number of lines in content.

        Returns:
            Total line count
        """
        return self.total_lines

    def update_terminal_height(self, new_height: int) -> None:
        """Update scroller for new terminal dimensions.

        Adjusts page size and ensures current position remains valid
        when terminal is resized.

        Args:
            new_height: New terminal height
        """
        old_page_size = self.page_size
        self.page_size = max(
            BrowserSettings.MIN_PAGE_SIZE,
            new_height - BrowserSettings.UI_RESERVED_LINES,
        )

        # Adjust current position if necessary
        if self.page_size != old_page_size:
            max_start = max(0, self.total_lines - self.page_size)
            self.current_line = min(self.current_line, max_start)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f'MessageScroller(lines={self.total_lines}, '
            f'current={self.current_line}, '
            f'page_size={self.page_size}, '
            f'scrollable={self.is_scrollable()})'
        )
