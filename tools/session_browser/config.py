"""Configuration module for session browser hotkeys and settings.

This module centralizes all keyboard configuration to make the browser
easily customizable and maintainable.
"""

from enum import Enum
from typing import Dict, List, Literal, Union


class HotkeyConfig:
    r"""Centralized hotkey configuration for easy customization.

    This class contains all keyboard shortcuts used throughout the session browser.
    To modify hotkeys, simply change the values here and they will be applied
    consistently across the entire application.

    Key Format:
    - Single characters: 'q', 'j', 'k', etc.
    - Special sequences: escape sequences for arrow keys, function keys
    - Lists: Multiple keys that perform the same action ['j', '\x1b[B']

    Example:
        # To change the quit key from 'q' to 'x':
        QUIT = ['x']

        # To add alternative keys:
        NEXT_SESSION = ['j', 'n', '\x1b[B']  # j, n, or down arrow
    """

    # Special key sequences (terminal escape codes)
    ARROW_UP = '\x1b[A'
    ARROW_DOWN = '\x1b[B'
    ARROW_LEFT = '\x1b[D'
    ARROW_RIGHT = '\x1b[C'
    PAGE_UP = '\x1b[5~'
    PAGE_DOWN = '\x1b[6~'
    ENTER = ['\r', '\n']
    BACKSPACE = ['\x7f', '\b']
    ESCAPE = '\x1b'

    # Session list navigation hotkeys
    NEXT_SESSION = ['j', ARROW_DOWN]
    PREV_SESSION = ['k', ARROW_UP]
    NEXT_PAGE = ['l', ARROW_RIGHT]
    PREV_PAGE = ['h', ARROW_LEFT]

    # Message navigation hotkeys
    NEXT_MESSAGE = ['j', ARROW_DOWN]
    PREV_MESSAGE = ['k', ARROW_UP]
    FIRST_MESSAGE = ['h', ARROW_LEFT]
    LAST_MESSAGE = ['l', ARROW_RIGHT]

    # Message scrolling hotkeys
    SCROLL_DOWN = ['d', PAGE_DOWN]
    SCROLL_UP = ['u', PAGE_UP]

    # Action hotkeys
    TOGGLE_METADATA = ['m']
    TOGGLE_WORKFLOW_MODE = ['w']
    TOGGLE_ONLY_FILE_CREATION = ['f']
    SAVE_TO_FILE = ['s']
    COPY_TO_CLIPBOARD = ['c']

    SEARCH = ['s']
    QUIT = ['q']
    BACK = ['b']
    SELECT_SESSION = ENTER

    @classmethod
    def matches(cls, key: str, action: str) -> bool:
        r"""Check if a pressed key matches the given action.

        Args:
            key: The key that was pressed
            action: The action name (attribute of HotkeyConfig)

        Returns:
            True if the key matches the action, False otherwise

        Example:
            >>> HotkeyConfig.matches('j', 'NEXT_SESSION')
            True
            >>> HotkeyConfig.matches('\\x1b[B', 'NEXT_SESSION')  # down arrow
            True
            >>> HotkeyConfig.matches('x', 'NEXT_SESSION')
            False
        """
        if not hasattr(cls, action):
            return False

        action_keys = getattr(cls, action)
        if isinstance(action_keys, list):
            return key in action_keys
        return key == action_keys

    @classmethod
    def get_help_text(cls, action: str) -> str:
        """Get formatted help text for an action.

        Generates user-friendly help text showing all key combinations
        for a given action. Converts escape sequences to readable symbols.

        Args:
            action: The action name (attribute of HotkeyConfig)

        Returns:
            Formatted help text showing key combinations

        Example:
            >>> HotkeyConfig.get_help_text('NEXT_SESSION')
            'j/↓'
            >>> HotkeyConfig.get_help_text('SCROLL_DOWN')
            'd/PgDn'
        """
        if not hasattr(cls, action):
            return ''

        action_keys = getattr(cls, action)
        if isinstance(action_keys, list):
            # Show primary key and alternatives
            primary = action_keys[0]
            alternatives = []

            for key in action_keys[1:]:
                # Convert escape sequences to readable symbols
                if key == cls.ARROW_UP:
                    alternatives.append('↑')
                elif key == cls.ARROW_DOWN:
                    alternatives.append('↓')
                elif key == cls.ARROW_LEFT:
                    alternatives.append('←')
                elif key == cls.ARROW_RIGHT:
                    alternatives.append('→')
                elif key == cls.PAGE_UP:
                    alternatives.append('PgUp')
                elif key == cls.PAGE_DOWN:
                    alternatives.append('PgDn')
                else:
                    alternatives.append(key)

            if alternatives:
                return f'{primary}/{"/".join(alternatives)}'
            return primary
        return str(action_keys)

    @classmethod
    def get_all_actions(cls) -> List[str]:
        """Get list of all available actions.

        Returns:
            List of action names that can be used with matches() and get_help_text()
        """
        excluded_attrs = {'matches', 'get_help_text', 'get_all_actions'}
        return [
            attr
            for attr in dir(cls)
            if not attr.startswith('_')
            and attr not in excluded_attrs
            and not callable(getattr(cls, attr))
        ]


# Type definitions for better type safety
MessageType = Literal[
    'function_call',
    'create_file',
    'function_call_output',
    'output_text',
    'regular',
    'user',
    'assistant',
    'unknown',
]

RichStyle = Literal['blue', 'yellow', 'red', 'green']


class MessageTypeIcon(Enum):
    """Emoji indicators for different message types."""

    FUNCTION_CALL = '🔧'
    CREATE_FILE = '📜'
    FUNCTION_CALL_OUTPUT = '📤'
    OUTPUT_TEXT = '🤖'
    REGULAR = '💬'
    USER = '👤'
    ASSISTANT = '🤖'
    UNKNOWN = '❓'


class RichStyleColor(Enum):
    """Rich color styles used in the UI."""

    PANEL_BORDER = 'blue'
    SEARCH_HIGHLIGHT = 'yellow'
    ERROR = 'red'
    SUCCESS = 'green'


class BrowserSettings:
    """Configuration settings for the session browser.

    Centralizes non-hotkey settings like display options, paging, etc.
    """

    # Display settings
    SESSIONS_PER_PAGE: int = 20
    DEFAULT_TERMINAL_HEIGHT: int = 30
    CONTENT_TRUNCATION_LENGTH: int = 2000
    ARGUMENT_TRUNCATION_LENGTH: int = 50

    # UI settings
    PANEL_BORDER_STYLE: RichStyle = RichStyleColor.PANEL_BORDER.value
    SEARCH_HIGHLIGHT_STYLE: RichStyle = RichStyleColor.SEARCH_HIGHLIGHT.value
    ERROR_STYLE: RichStyle = RichStyleColor.ERROR.value
    SUCCESS_STYLE: RichStyle = RichStyleColor.SUCCESS.value

    # Message type indicators (emojis)
    TYPE_INDICATORS: Dict[MessageType, str] = {
        'function_call': MessageTypeIcon.FUNCTION_CALL.value,
        'create_file': MessageTypeIcon.CREATE_FILE.value,
        'function_call_output': MessageTypeIcon.FUNCTION_CALL_OUTPUT.value,
        'output_text': MessageTypeIcon.OUTPUT_TEXT.value,
        'regular': MessageTypeIcon.REGULAR.value,
        'user': MessageTypeIcon.USER.value,
        'assistant': MessageTypeIcon.ASSISTANT.value,
        'unknown': MessageTypeIcon.UNKNOWN.value,
    }

    # Scrolling settings
    MIN_PAGE_SIZE: int = 10
    UI_RESERVED_LINES: int = 15  # Lines reserved for navigation, headers, etc.
