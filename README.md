# IVEXES - Intelligent Vulnerability Exploration and Exploitation System

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

**IVEXES** is a comprehensive Python framework for cybersecurity vulnerability analysis and exploitation using multi-agent AI systems. Developed as part of a bachelor thesis, it combines knowledge bases (CWE, CAPEC, MITRE ATT&CK) with dynamic analysis capabilities for automated security assessment.

## ⚠️ Important Notice

This project is developed as part of a **bachelor thesis** for academic research purposes. It is designed to advance the understanding of automated vulnerability analysis and contribute to defensive cybersecurity research.

### Ethical Considerations and Responsible Use

**IVEXES is intended EXCLUSIVELY for:**
- Academic research and education
- Defensive cybersecurity purposes
- Vulnerability assessment of systems you own or have explicit permission to test
- Security research within controlled environments
- Contributing to the development of better security practices

**STRICTLY PROHIBITED uses include:**
- Unauthorized access to systems or networks
- Malicious exploitation of vulnerabilities
- Any illegal cybersecurity activities
- Attacking systems without explicit written permission
- Commercial exploitation without proper licensing

Users are responsible for ensuring compliance with all applicable laws, regulations, and ethical guidelines in their jurisdiction. The developers assume no responsibility for misuse of this software.

## 🎓 Academic Context

This project represents a bachelor thesis research contribution focusing on:
- Automated vulnerability analysis using AI agents
- Integration of cybersecurity knowledge bases
- Multi-agent systems for security assessment
- Academic advancement in defensive cybersecurity

The research aims to improve defensive capabilities and contribute to the academic understanding of automated security analysis.

## 🚀 Features

- **Multi-Agent AI System**: Orchestrated AI agents for complex vulnerability analysis
- **Knowledge Base Integration**: Built-in support for CWE, CAPEC, and MITRE ATT&CK frameworks
- **Code Analysis**: Advanced code browsing with LSP integration and tree-sitter parsing
- **Sandbox Environment**: Docker-based isolated execution for safe analysis
- **Vector Database**: ChromaDB integration for similarity search and knowledge retrieval
- **CVE Search**: Automated vulnerability lookup and analysis
- **Interactive CLI**: Comprehensive command-line interface for all modules

## 📋 Requirements

- Python 3.8+
- Docker (for sandbox environments)
- Git
- LLM API access (OpenAI or compatible)

## 🛠️ Installation

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LetsDrinkSomeTea/ivexes.git
   cd ivexes
   ```

2. **Install in development mode:**
   ```bash
   pip install -e .
   ```

3. **For development with additional tools:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Build container images:**
   ```bash
   docker compose build
   ```

### Environment Configuration

Create a `.env` file for API keys and sensitive configuration:

```bash
# Required API Configuration, this is preferred
LLM_API_KEY=your_openai_api_key_here
# OR this is used only for tracing if LLM_API_KEY is set
OPENAI_API_KEY=your_openai_api_key_here

# LLM Configuration
LLM_BASE_URL=https://api.openai.com/v1
MODEL=openai/gpt-4o-mini
REASONING_MODEL=openai/o4-mini
MODEL_TEMPERATURE=0.3
```

It is also possible to define the general configuration in the `.env` file:

```bash
# Logging
LOG_LEVEL=INFO
TRACE_NAME=ivexes

# Agent Configuration
MAX_TURNS=10

# Vector Database
EMBEDDING_PROVIDER=builtin
CHROMA_PATH=/tmp/ivexes/chromadb

# Codebase Analysis (for vulnerability assessment)
CODEBASE_PATH=/path/to/your/test/codebase
VULNERABLE_CODEBASE_FOLDER=vulnerable-version
PATCHED_CODEBASE_FOLDER=patched-version

# Sandbox
SANDBOX_IMAGE=kali-ssh:latest
SETUP_ARCHIVE=/path/to/setup.tar.gz
```

## 📖 Usage

### Basic Agent Usage

#### Single Agent Analysis
```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

# Configure for vulnerability analysis
settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/path/to/test/codebase',
    vulnerable_folder='vulnerable-v1.0',
    patched_folder='patched-v1.1'
)

agent = SingleAgent(settings=settings)

# Interactive mode
await agent.run_interactive()

# Or streaming mode
await agent.run_streamed():
```

#### Multi-Agent Analysis
```python
from ivexes.agents import MultiAgent

agent = MultiAgent(settings=settings)
agent.run()
```

### Command Line Interface

IVEXES provides a comprehensive CLI through `examples/manual.py`:

```bash
# Get help about the CLI-tool
python examples/manual.py --help
```

### Configuration Options

It is possible to define global standards as environment variables or to pass them into the Agent.
Passed settings gets preferred over the environment variables.

#### Core Settings
- `MODEL`: Primary LLM model (default: `openai/gpt-4o-mini`)
- `REASONING_MODEL`: Model for planning component (default: `openai/o4-mini`)
- `MODEL_TEMPERATURE`: Model temperature 0.0-2.0 (default: 0.3)
- `MAX_TURNS`: Maximum agent conversation turns (default: 10)

#### Embedding & Vector Database
- `EMBEDDING_PROVIDER`: `builtin`, `local` (fetched from SentenceTransformers), or `openai` (default: builtin)
- `CHROMA_PATH`: ChromaDB storage location

#### Analysis Configuration
- `CODEBASE_PATH`: Root directory containing vulnerable/patched code
- `VULNERABLE_CODEBASE_FOLDER`: Subdirectory with vulnerable version
- `PATCHED_CODEBASE_FOLDER`: Subdirectory with patched version

#### Sandbox Configuration
- `SETUP_ARCHIVE`: tgz-archive with necessary data to setup sandbox, gets unpacked at /tmp, afterwards /tmp/setup.sh is run.
- `SANDBOX_IMAGE`: Which docker image to use as the sandbox base.

## 🏗️ Architecture

### Core Components

#### Agents (`src/ivexes/agents/`)
- **BaseAgent**: Foundation class with settings management
- **SingleAgent**: Focused vulnerability analysis
- **MultiAgent**: Orchestrated multi-agent analysis
- **MVPAgent**: Minimal viable implementation
- **HTBChallengeAgent**: Specialized for CTF challenges

#### Code Browser (`src/ivexes/code_browser/`)
- LSP integration for advanced code analysis
- Tree-sitter parsing for code structure
- Container-based isolated analysis environment

#### Sandbox System (`src/ivexes/sandbox/`)
- Docker-based execution environments
- Kali Linux container for security testing
- Secure isolation with automatic setup

#### Vector Database (`src/ivexes/vector_db/`)
- ChromaDB for knowledge storage
- MITRE ATT&CK framework integration
- CWE and vulnerability pattern matching

## 🧪 Development

### Testing
```bash
# Run all tests
python -m unittest discover tests/

# Individual test modules available in tests/cases/
```

### Code Quality
```bash
# Format code
ruff format

# Run linter
ruff check

# Pre-commit hooks are configured in pyproject.toml
```

### Examples

The `examples/` directory contains various usage patterns:
- `10_agents_sandbox_*`: Sandbox-based analysis examples
- `20_mvp_screen`: MVP agent demonstration
- `30_chroma_db_example`: Vector database usage
- `60_single_agent_*`: Single agent examples
- `70_multi_agent_*`: Multi-agent orchestration

## 📄 License

This project is licensed under the GPL-3.0-or-later License - see the LICENSE file for details.

## 🔗 Repository

- **Source Code**: [https://github.com/LetsDrinkSomeTea/ivexes](https://github.com/LetsDrinkSomeTea/ivexes)
- **Issues**: Report bugs and request features via GitHub Issues

## ⚖️ Legal Disclaimer

This software is provided for educational and research purposes only. Users must ensure compliance with all applicable laws and regulations. Unauthorized use for malicious purposes is strictly prohibited. The developers are not responsible for any misuse of this software.

## 🤝 Contributing

As this is a bachelor thesis project, contributions should align with academic research goals. Please ensure any contributions:
- Follow ethical guidelines
- Support defensive cybersecurity research
- Include appropriate documentation
- Pass all tests and quality checks

---

**IVEXES** - Advancing cybersecurity through responsible AI-driven vulnerability analysis.
