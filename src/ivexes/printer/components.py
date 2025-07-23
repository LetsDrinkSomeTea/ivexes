"""UI components module for text formatting and display.

This module provides ASCII art, text formatting utilities, and banner
generation functions for the ivexes application interface.
"""

from agents.usage import Usage


ART = [
    r'o-O-o o   o o--o     o--o  o-o ',
    r'  |   |   | |        |    |    ',
    r'  |   o   o O-o  \ / O-o   o-o ',
    r'  |    \ /  |     o  |        |',
    r'o-O-o   o   o--o / \ o--o o--o ',
    r'',
    r'Intelligent Vulnerability Extraction',
    r'& Exploit Synthesis',
]


def _create_box(
    lines: list[str], horizontal: str = '-', vertical: str = '|', corner: str = '+'
) -> list[str]:
    """Wrap a list of text lines in a box border.

    Args:
        lines: List of text lines to wrap in a box
        horizontal: Character for top/bottom borders
        vertical: Character for side borders
        corner: Character for corners

    Returns:
        List of strings representing the boxed content
    """
    # Determine content width
    width = max(len(line) for line in lines)
    # Top and bottom border include padding of one space on each side
    border_line = corner + horizontal * (width + 2) + corner
    # Side borders with padding to align content
    boxed = [border_line]
    for line in lines:
        boxed.append(f'{vertical} {line.ljust(width)} {vertical}')
    boxed.append(border_line)
    return boxed


def banner(
    model: str,
    reasoning_model: str,
    temperature: float,
    max_turns: int,
    trace_name: str,
) -> str:
    """Generate a banner with ASCII art and model information.

    Args:
        model: Primary model name to display
        reasoning_model: Reasoning model name to display
        temperature: Temperature parameter for model
        max_turns: Maximum number of turns
        trace_name: Name of the trace

    Returns:
        Formatted banner string with ASCII art and model info
    """
    # Sanitize inputs
    trace_name = trace_name.strip()
    model = model.strip()
    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        raise ValueError(f'Invalid temperature: {temperature}')
    try:
        max_turns = int(max_turns)
    except (TypeError, ValueError):
        raise ValueError(f'Invalid max_turns: {max_turns}')

    # Prepare key-value pairs for config
    items = [
        ('trace name', trace_name),
        ('model', model),
        ('reasoning model', reasoning_model),
        ('temperature', str(temperature)),
        ('max turns', str(max_turns)),
    ]
    # Compute widths for padding
    key_width = max(len(k) for k, _ in items)
    val_width = max(len(v) for _, v in items)
    # Create config lines with right-padded values
    cfg = [f'{k:.<{key_width}}....{v:.>{val_width}}' for k, v in items]

    # Combine art and config
    content = ART + [''] + cfg
    content = [line.center(80) for line in content]

    # Large border around whole content
    final_block = _create_box(content, horizontal='=', vertical='|', corner='+')

    # Assemble and return
    return '\n'.join(final_block)


def format_usage_display(usage: Usage, show_details: bool = True) -> str:
    """Format usage information into a human-readable string.

    Args:
        usage: Usage object containing token counts and request information
        show_details: Whether to include detailed breakdown of token types

    Returns:
        Formatted string describing token usage
    """
    # Calculate total tokens if not provided (fallback)
    total_tokens = (
        usage.total_tokens
        if usage.total_tokens > 0
        else (usage.input_tokens + usage.output_tokens)
    )

    # Basic usage format
    base_format = f'{usage.input_tokens:,} input + {usage.output_tokens:,} output = {total_tokens:,} total tokens ({usage.requests} requests)'

    if not show_details:
        return f'Token usage: {base_format}'

    details = []

    # Add reasoning tokens if available
    if hasattr(usage, 'output_tokens_details') and usage.output_tokens_details:
        reasoning_tokens = getattr(
            usage.output_tokens_details, 'reasoning_tokens', None
        )
        if reasoning_tokens and reasoning_tokens > 0:
            details.append(f'reasoning: {reasoning_tokens:,}')

    # Add cached tokens if available
    if hasattr(usage, 'input_tokens_details') and usage.input_tokens_details:
        cached_tokens = getattr(usage.input_tokens_details, 'cached_tokens', None)
        if cached_tokens and cached_tokens > 0:
            details.append(f'cached: {cached_tokens:,}')

    if details:
        details_str = f' ({", ".join(details)})'
    else:
        details_str = ''

    return f'Token usage: {base_format}{details_str}'
