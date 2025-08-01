"""Date and Time Tools.

This module provides utility functions for retrieving current date and time
information. These tools are useful for timestamping analysis results,
logging events, and general temporal operations.
"""

from datetime import datetime
from typing import cast

from agents.tool import function_tool, Tool


def current_date():
    """Get the current date and time in a formatted string.

    Returns:
        str: Current date and time in 'YYYY-MM-DD HH:MM:SS' format.
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@function_tool(strict_mode=True)
def get_current_date():
    """Get the current date and time.

    Returns the current date and time in a formatted string.

    Returns:
        str: Current date and time in 'YYYY-MM-DD HH:MM:SS' format.

    Example:
        >>> get_current_date()
        '2024-01-15 14:30:45'
    """
    return current_date()


date_tools = cast(list[Tool], [get_current_date])
