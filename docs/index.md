# IVExES Documentation

**Intelligent Vulnerability Exploration and Exploitation System**

IVExES is a comprehensive Python framework for cybersecurity vulnerability analysis and exploitation using multi-agent AI systems.

## Quick Start

### Installation

```bash
git clone https://github.com/LetsDrinkSomeTea/ivexes.git
cd ivexes
pip install -e .
```

### Basic Usage

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/path/to/test/codebase'
)

agent = SingleAgent(settings=settings)
asyncio.run(agent.run_interactive())
```

## Architecture

- **[Agents](agents.md)** - Multi-agent AI system for vulnerability analysis
- **[Code Browser](code_browser.md)** - LSP integration and tree-sitter parsing
- **[Configuration](config.md)** - Settings and environment management
- **[CVE Search](cve_search.md)** - Vulnerability lookup and analysis
- **[Sandbox](sandbox.md)** - Docker-based isolated execution
- **[Tools](tools.md)** - Utility functions and helpers
- **[Vector Database](vector_db.md)** - ChromaDB integration for knowledge retrieval
