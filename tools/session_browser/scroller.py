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
        """Get the currently visible portion of content with Rich markup preservation.

        Returns:
            String containing the lines currently visible on screen with
            Rich markup state preserved across scroll boundaries
        """
        end_line = min(self.total_lines, self.current_line + self.page_size)
        visible_lines = self.lines[self.current_line : end_line]

        # If we're not at the top, check if we need to preserve Rich markup state
        if self.current_line > 0:
            opening_tags = self._get_active_markup_state(self.current_line)
            if opening_tags:
                # Prepend the opening tags to maintain formatting
                if visible_lines:
                    visible_lines[0] = opening_tags + visible_lines[0]

        return '\n'.join(visible_lines)

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

    def _get_active_markup_state(self, line_index: int) -> str:
        """Get the Rich markup state that should be active at the given line.

        Analyzes content before the given line to determine which Rich
        markup tags are currently open and should be preserved. Only preserves
        content-level formatting, not header formatting.

        Args:
            line_index: The line index to check markup state for

        Returns:
            String containing opening tags that should be active
        """
        import re

        # Only preserve markup that starts after the first line (skip headers)
        # Headers are typically on the first line with patterns like "[bold]📤 Output[/bold]"
        if line_index <= 1:
            return ''

        # Look at content starting from line 1 (after the header)
        content_lines = self.lines[1:line_index]
        content_before = '\n'.join(content_lines)

        # Track opening and closing tags
        tag_stack = []

        # Find all Rich markup tags in the content before current position
        # Rich tags have the format [tag] or [/tag] or [tag param]
        tag_pattern = r'\[([^]]+)\]'

        for match in re.finditer(tag_pattern, content_before):
            tag_content = match.group(1)

            if tag_content.startswith('/'):
                # Closing tag - remove the corresponding opening tag from stack
                closing_tag = tag_content[1:]  # Remove the '/'
                # Remove the last occurrence of this tag from the stack
                for i in range(len(tag_stack) - 1, -1, -1):
                    if tag_stack[i].split(' ')[0] == closing_tag:
                        tag_stack.pop(i)
                        break
            else:
                # Opening tag - add to stack, but only preserve content-level tags
                if self._is_content_formatting_tag(tag_content):
                    tag_stack.append(tag_content)

        # Return the opening tags that are still active
        if tag_stack:
            return ''.join(f'[{tag}]' for tag in tag_stack)
        return ''

    def _is_content_formatting_tag(self, tag: str) -> bool:
        """Check if a Rich markup tag is meant for content formatting.

        Args:
            tag: The tag content (without brackets)

        Returns:
            True if this tag should be preserved across scroll boundaries
        """
        # Only preserve tags that are typically used for content formatting
        # Skip header/title formatting tags
        tag_name = tag.split(' ')[0].lower()

        content_tags = {
            'dim',  # Dimmed text (commonly used for tool output)
            'italic',  # Italic text
            'underline',  # Underlined text
            'strike',  # Strikethrough text
        }

        # Don't preserve header/title formatting
        header_tags = {
            'bold',  # Bold text (used in headers)
            'cyan',  # Color formatting (used in headers)
            'blue',  # Color formatting
            'red',  # Color formatting
            'green',  # Color formatting
            'yellow',  # Color formatting
            'magenta',  # Color formatting
        }

        return tag_name in content_tags

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f'MessageScroller(lines={self.total_lines}, '
            f'current={self.current_line}, '
            f'page_size={self.page_size}, '
            f'scrollable={self.is_scrollable()})'
        )
