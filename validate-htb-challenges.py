"""Validate HTB Challenges.

This script checks the output reports for HTB challenges to see if the expected flags are found.
It reads the report files, extracts the model and flag information, and displays the results in a
formatted table.
"""

import os
import re
from rich.console import Console
from rich.table import Table

c = Console()

challenges = [
    'pass',
    'behindthescenes',
    'bincrypt_breaker',
]

model_re = re.compile(r'\*\*Model:\*\* (.+)')
flag_re = re.compile(r'HTB\{......*?\}')

table = Table(title='HTB Challenge Validation Results')
table.add_column('Challenge', style='bold')
table.add_column('Status', justify='center')
table.add_column('Model', style='yellow')
table.add_column('Flag Found', style='dim')
table.add_column('Report File', style='dim')

for challenge in challenges:
    for file in os.listdir('output/reports'):
        if file.endswith('.md') and challenge in file:
            with open(f'./output/reports/{file}', 'r') as f:
                content = f.read()
                matches = model_re.findall(content)
                model = matches[0] if matches else 'Unknown'
                flag_matches = flag_re.findall(content)
                if flag_matches:
                    table.add_row(
                        challenge,
                        '[green]✓ Found[/green]',
                        model,
                        flag_matches[0],
                        os.path.basename(file),
                    )
                else:
                    table.add_row(
                        challenge,
                        '[red]✗ Not Found[/red]',
                        model,
                        '-',
                        os.path.basename(file),
                    )

c.print(table)
