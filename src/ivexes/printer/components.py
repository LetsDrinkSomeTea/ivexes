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
    """
    Wrap a list of text lines in a box border.
    horizontal: character for top/bottom borders
    vertical: character for side borders
    corner: character for corners
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
