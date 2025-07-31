# IVExES - Intelligent Vulnerability Extraction & Exploit Synthesis

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

IVExES is an advanced Python framework for cybersecurity vulnerability analysis
and exploitation using multi-agent AI systems. It combines knowledge bases (CWE,
CAPEC, MITRE ATT&CK) with dynamic analysis capabilities for automated security
assessment.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- uv package manager (recommended)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/LetsDrinkSomeTea/ivexes.git
   cd ivexes
   ```

2. **Full setup (recommended):**

   ```bash
   make setup
   ```

   This will build Docker images, sync dependencies, and start the LiteLLM
   proxy.

3. **Configure environment variables:** Create a `.secrets.env` file with your
   API keys:
   ```bash
   LLM_API_KEY=your_openai_api_key_here
   # or
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Quick Example

```python
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/path/to/vulnerable/code',
    vulnerable_folder='vulnerable-version',
    patched_folder='patched-version'
)

agent = SingleAgent(settings=settings)
await agent.run_interactive()
```

## 📖 Overview

IVExES provides a comprehensive framework for automated vulnerability analysis
through:

- **Multi-Agent Architecture**: Specialized AI agents for different aspects of
  security analysis
- **Knowledge Base Integration**: MITRE ATT&CK, CWE, CAPEC, and CVE databases
- **Dynamic Code Analysis**: Container-based sandbox environment with Neovim LSP
  integration
- **Automated Reporting**: Structured vulnerability reports with exploitation
  details
- **Extensible Design**: Modular architecture supporting custom agents and tools

## 🏗️ Architecture

### Core Components

#### Agents (`src/ivexes/agents/`)

- **BaseAgent**: Abstract foundation with settings management and execution
  modes
- **SingleAgent**: Individual agent for focused vulnerability assessment
- **MultiAgent**: Orchestrates multiple specialized agents for complex analysis
- **MVPAgent**: Minimal viable product implementation for quick analysis
- **HTBChallengeAgent**: Specialized for Hack The Box challenge analysis

#### Code Browser (`src/ivexes/code_browser/`)

- Neovim LSP integration for intelligent code analysis
- Tree-sitter parsing for code structure understanding
- Container-based isolation for safe code examination

#### Sandbox System (`src/ivexes/sandbox/`)

- Docker-based execution environments
- Kali Linux container for security testing
- Automatic setup from archives with secure isolation

#### Vector Database (`src/ivexes/vector_db/`)

- ChromaDB for knowledge storage and retrieval
- MITRE ATT&CK framework integration
- CVE and vulnerability pattern matching
- Embedding-based similarity search

## 🛠️ Development

### Development Commands

```bash
# Setup and dependency management
make setup              # Complete setup (images, deps, services)
make sync               # Install/update dependencies
make build-images       # Build Docker images
make run-litellm        # Start LiteLLM proxy

# Code quality
make format             # Format and fix code
make format-check       # Check formatting
make lint               # Run linter
make check              # Run all quality checks

# Testing
make tests              # Run test suite

# Documentation
make build-docs         # Build documentation
make serve-docs         # Serve docs locally
make deploy-docs        # Deploy to GitHub Pages
```

### Project Structure

```
ivexes/
├── src/ivexes/           # Main package source
│   ├── agents/           # AI agent implementations
│   ├── code_browser/     # Code analysis tools
│   ├── config/           # Configuration management
│   ├── sandbox/          # Execution environments
│   ├── vector_db/        # Knowledge base integration
│   └── tools.py          # Shared utilities
├── container/            # Docker configurations
│   ├── kali_sandbox/     # Security testing environment
│   ├── nvim_lsp/         # Code analysis container
│   └── litellm/          # LLM proxy service
├── examples/             # Usage examples
├── tests/                # Test suite
└── docs/                 # Documentation
```

## ⚙️ Configuration

IVExES uses environment variables for configuration with sensible defaults.
Create `.env` and `.secrets.env` files as needed:

### Essential Settings

```bash
# API Configuration
LLM_API_KEY=your_api_key                    # Required: LLM provider API key
LLM_BASE_URL=https://api.openai.com/v1     # LLM endpoint

# Model Configuration
MODEL=openai/gpt-4o-mini                    # Primary model
REASONING_MODEL=openai/o4-mini              # Reasoning model
TEMPERATURE=0.3                             # Model temperature (0.0-2.0)

# Analysis Configuration
CODEBASE_PATH=/path/to/code                 # Analysis target
VULNERABLE_CODEBASE_FOLDER=vulnerable       # Vulnerable version folder
PATCHED_CODEBASE_FOLDER=patched            # Patched version folder

# System Configuration
LOG_LEVEL=INFO                              # Logging level
MAX_TURNS=10                               # Agent conversation limit
```

### Advanced Configuration

```bash
# Embedding Configuration
EMBEDDING_PROVIDER=builtin                  # builtin, local, or openai
EMBEDDING_MODEL=builtin                     # Embedding model
CHROMA_PATH=/tmp/ivexes/chromadb           # Vector database path

# Sandbox Configuration
SANDBOX_IMAGE=kali-ssh:latest              # Container image
SETUP_ARCHIVE=/path/to/setup.tgz          # Analysis setup archive
```

## 🎯 Usage Examples

### Single Agent Analysis

```python
import asyncio
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/path/to/vulnerable/code',
    vulnerable_folder='vulnerable-v1.0',
    patched_folder='patched-v1.1'
)

agent = SingleAgent(settings=settings)

# Interactive mode
await agent.run_interactive()

# Streaming mode
async for chunk in agent.run_streamed():
    print(chunk, end='')

# Synchronous mode
result = agent.run()
print(result)
```

### Multi-Agent Orchestration

```python
from ivexes.agents import MultiAgent

agent = MultiAgent(settings=settings)
await agent.run_interactive()
```

### HTB Challenge Analysis

```python
from ivexes.agents import HTBChallengeAgent

agent = HTBChallengeAgent(
    challenge_name="buffer_overflow_example",
    settings=settings
)
await agent.run_interactive()
```

## 🐳 Container Services

IVExES uses Docker containers for isolation and specialized environments:

### LiteLLM Proxy

- Unified API for multiple LLM providers
- Request routing and load balancing
- Usage tracking and rate limiting

### Kali Sandbox

- Security testing environment
- Pre-installed penetration testing tools
- Isolated execution for exploit development

### Neovim LSP

- Intelligent code analysis
- Language server protocol integration
- Syntax highlighting and error detection

## 📊 Features

### Vulnerability Analysis

- **Static Analysis**: Code structure and pattern recognition
- **Dynamic Analysis**: Runtime behavior in controlled environments
- **Differential Analysis**: Comparison between vulnerable and patched versions
- **Knowledge Integration**: CVE, CWE, CAPEC, and MITRE ATT&CK correlation

### AI Agent Capabilities

- **Specialized Roles**: Different agents for reconnaissance, analysis, and
  exploitation
- **Collaborative Analysis**: Multi-agent coordination for complex
  vulnerabilities
- **Adaptive Learning**: Continuous improvement through feedback loops
- **Context Awareness**: Maintains conversation history and analysis state

### Reporting and Documentation

- **Structured Reports**: Markdown-formatted vulnerability assessments
- **Exploitation Details**: Step-by-step exploitation procedures
- **Risk Assessment**: CVSS scoring and impact analysis
- **Remediation Guidance**: Specific mitigation recommendations

## 🔧 Troubleshooting

### Common Issues

**Dependencies not installing:**

```bash
# Use UV for dependency management
uv sync --all-extras --all-packages --group dev

# Or fallback to pip
pip install -e ".[dev]"
```

**Docker issues:**

```bash
# Rebuild images
make build-images

# Check service status
docker compose ps

# View logs
docker compose logs
```

**LiteLLM proxy not starting:**

```bash
# Check configuration
cat container/litellm/config/config.yaml

# Restart service
docker compose restart
```

### Getting Help

- Check the [documentation](https://pages.faigle.dev/ivexes)
- Review [example scripts](examples/)
- Open an issue on GitHub for bugs or feature requests

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the
[LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines and submit
pull requests to the main repository.

## 📚 Citation

If you use IVExES in your research, please cite:

```bibtex
@software{ivexes2024,
  title={IVExES: Intelligent Vulnerability Extraction \& Exploit Synthesis},
  author={Julian Faigle},
  year={2025},
  url={https://github.com/LetsDrinkSomeTea/ivexes}
}
```

---

**Note**: IVExES is designed for educational and authorized security testing
purposes only. Users are responsible for ensuring compliance with applicable
laws and regulations.

