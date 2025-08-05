# IVExES Demo

## llm (prompt)

> one shot llm prompt

```bash
uv run manual.py llm ask "$prompt"
uv run manual.py llm ask -m 'anthropic/claude-3-5-sonnet-20240620' "$prompt"

```

## code-browser

> Usage examples of the codebrowser

### get-tree

```bash
uv run manual.py code-browser get-tree
```

### get-diff

```bash
uv run manual.py code-browser get-diff
```

### get-file

```bash
uv run manual.py code-browser get-file vulnerable-screen-4.5.0/logfile.c
```

### get-definition

```bash
uv run manual.py code-browser get-definition changed_logfile
```

## vectordb

> example for semantic search.

```bash
uv run manual.py vector-db query -t cwe "Privilege Escalation"
```

## cve

> query cve by id

```bash
uv run manual.py cve by-id "CVE-2025-32463"
```

## sandbox

> example of sandbox usage

```bash
uv run manual.py sandbox start -i vuln-exiftool
```

## htb-challenge

> Runs the HTBChallengeAgent with the "pass"-Challenge.

```python
import asyncio
from dotenv import load_dotenv

from ivexes.agents import HTBChallengeAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging()

settings = PartialSettings(
    trace_name='pass',
    model='openai/gpt-4.1-mini',
    model_temperature=0.1,
    max_turns=25,
    setup_archive='/home/julian/Desktop/Bachelorarbeit/testdata/htb_pass/upload.tgz',
)

agent = HTBChallengeAgent(
    program='pass',
    challenge='All the coolest ghosts in town are going to a' \
    ' Haunted Houseparty- can you prove you deserve to get in?',
    settings=settings,
)

if __name__ == '__main__':
    asyncio.run(agent.run_interactive())
```

## multi-agent

> Multiple specialised agents working together

```python
import asyncio
from dotenv import load_dotenv

from ivexes.agents import MultiAgent
from ivexes.config import PartialSettings, setup_default_logging

load_dotenv(verbose=True, override=True)
setup_default_logging('WARNING')

settings = PartialSettings(
    trace_name='Multi-Agent Sudo',
    # model='anthropic/claude-sonnet-4-20250514',
    model='openai/gpt-4.1',
    reasoning_model='openai/o4-mini',
    model_temperature=0.1,
    max_turns=50,
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct',
    codebase_path='/home/julian/Desktop/Bachelorarbeit/testdata/sudo/codebase',
    vulnerable_folder='sudo-1.9.17',
    patched_folder='sudo-1.9.17p1',
    sandbox_image='vuln-sudo:latest',
)

agent = MultiAgent(settings=settings)

if __name__ == '__main__':
    asyncio.run(agent.run_interactive())

```

## browse-sessions

> Browse the executed session for easy follow of the taken actions.

```python
from tools import browse_sessions

browse_sessions('sessions.sqlite')
```

## fragen

> Offen gebliebene Fragen vor der Abgabe

```python

fragen = """
- Müssen die Exemplare alle mit Farbe ausgedruckt werden oder reicht eins?
    -> Ich hätte eins in voll Farbe und alle anderen schwarz-weiß
    -> alternativ nur die Quellenangaben in sw
- Gibt es schon einen Termin fürs Kolloqium?
- Wie genau wird das Projekt angeschaut? Soll ich einen API-Key beilegen?
"""

print(fragen)
```
