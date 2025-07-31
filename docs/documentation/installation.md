# Installation Guide

## Overview

This guide provides comprehensive instructions for installing and setting up IVEXES (Intelligent Vulnerability Extraction & Exploit Synthesis). The installation process involves setting up the Python environment, configuring Docker containers, and initializing the LiteLLM proxy for API access.

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: Version 3.12 or higher
- **Docker**: Version 20.10 or higher with Docker Compose V2
- **Memory**: Minimum 8GB RAM (16GB recommended for large analyses)
- **Storage**: At least 10GB free space for containers and databases
- **Network**: Internet access for downloading models and vulnerability data

### Required Software

1. **Python 3.12+**
   ```bash
   # Check Python version
   python --version
   # or
   python3 --version
   ```

2. **Docker & Docker Compose**
   ```bash
   # Check Docker version
   docker --version
   docker compose version
   ```

3. **Git** (for development installation)
   ```bash
   git --version
   ```

## Installation Methods

### Method 1: Quick Setup (Recommended)

The quickest way to get IVEXES running is using the provided Makefile:

```bash
# Clone the repository
git clone https://github.com/LetsDrinkSomeTea/ivexes.git
cd ivexes

# Run complete setup (builds images, syncs dependencies, starts LiteLLM)
make setup
```

This command will:
1. Build Docker images for Nvim LSP and Kali sandbox
2. Install Python dependencies using uv
3. Start the LiteLLM proxy server

### Method 2: Step-by-Step Installation

For more control over the installation process:

#### Step 1: Environment Setup

First, set up the Python environment:

```bash
# Option A: Using uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --all-extras --all-packages --group dev

# Option B: Using pip (legacy)
pip install -e ".[dev]"
```

#### Step 2: Build Container Images

Build the required Docker images:

```bash
# Build all images
make build-images

# Or manually:
docker compose --profile images build
```

This builds:
- **nvim-lsp:latest** - Neovim with LSP support for code analysis
- **kali-ssh:latest** - Kali Linux environment for security testing

#### Step 3: Start LiteLLM Proxy

Start the LiteLLM proxy service:

```bash
# Start LiteLLM and database
make run-litellm

# Or manually:
docker compose up -d
```

#### Step 4: Environment Configuration

Create environment configuration files:

```bash
# Create .env file for general settings
cat > .env << EOF
MODEL=openai/gpt-4o-mini
REASONING_MODEL=openai/o4-mini
TEMPERATURE=0.3
MAX_TURNS=10
LOG_LEVEL=INFO
EOF

# Create .secrets.env for API keys (never commit this file)
cat > .secrets.env << EOF
OPENAI_API_KEY=your_openai_api_key_here
LLM_API_KEY=your_llm_api_key_here
LLM_BASE_URL=http://localhost:4000/v1
EOF
```

## Configuration

### API Keys

IVEXES requires API keys for LLM services:

#### OpenAI Configuration
```bash
export OPENAI_API_KEY="sk-your-openai-key"
export LLM_BASE_URL="https://api.openai.com/v1"
```

#### LiteLLM Proxy Configuration
```bash
export LLM_API_KEY="sk-1234"  # Default LiteLLM key
export LLM_BASE_URL="http://localhost:4000/v1"
```

#### Alternative Providers
```bash
# Anthropic Claude
export LLM_API_KEY="your-anthropic-key"
export LLM_BASE_URL="your-litellm-proxy-url"

# Google Gemini
export LLM_API_KEY="your-google-key"
export LLM_BASE_URL="your-litellm-proxy-url"
```

### Environment Variables

Key configuration options:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL` | `openai/gpt-4o-mini` | Primary LLM model |
| `REASONING_MODEL` | `openai/o4-mini` | Model for reasoning tasks |
| `TEMPERATURE` | `0.3` | Model temperature (0.0-2.0) |
| `MAX_TURNS` | `10` | Maximum agent conversation turns |
| `LOG_LEVEL` | `INFO` | Logging level |
| `TRACE_NAME` | `ivexes` | OpenAI tracing identifier |
| `SESSION_DB_PATH` | `./sessions.sqlite` | Session database path |
| `CHROMA_PATH` | `/tmp/ivexes/chromadb` | Vector database path |

### Directory Structure

After installation, your directory should look like:

```
ivexes/
├── src/ivexes/              # Main package source
├── container/               # Docker configurations
│   ├── nvim_lsp/           # Neovim LSP container
│   ├── kali_sandbox/       # Kali sandbox container
│   └── litellm/            # LiteLLM configuration
├── docs/                   # Documentation
├── examples/               # Usage examples
├── tests/                  # Test suite
├── .env                    # Environment settings
├── .secrets.env            # API keys (create this)
└── docker-compose.yaml     # Container orchestration
```

## Verification

### 1. Check Installation Status

Verify that all components are properly installed:

```bash
# Check Python dependencies
uv run python -c "import ivexes; print('IVEXES imported successfully')"

# Check Docker images
docker images | grep -E "(nvim-lsp|kali-ssh)"

# Check running containers
docker compose ps
```

### 2. Test LiteLLM Proxy

Verify the LiteLLM proxy is working:

```bash
# Check health endpoint
curl http://localhost:4000/health/liveliness

# Test API endpoint
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### 3. Run Test Suite

Execute the test suite to verify functionality:

```bash
# Run all tests
make tests

# Or manually:
uv run python -m unittest discover -s tests -v
```

### 4. Basic Functionality Test

Test basic IVEXES functionality:

```bash
# Run a simple example
uv run python examples/20_mvp_screen.py

# Or test interactively
uv run python -c "
from ivexes.agents import MVPAgent
from ivexes.config import PartialSettings

settings = PartialSettings()
agent = MVPAgent(settings=settings)
print('Agent initialized successfully')
"
```

## Docker Services

### LiteLLM Proxy

The LiteLLM proxy provides unified API access to multiple LLM providers:

- **Service**: `litellm`
- **Port**: `4000`
- **Health Check**: `http://localhost:4000/health/liveliness`
- **API Endpoint**: `http://localhost:4000/v1`
- **Master Key**: `sk-1234` (configurable)

### PostgreSQL Database

Database for LiteLLM configuration and logging:

- **Service**: `db`
- **Internal Port**: `5432`
- **Database**: `litellm`
- **User**: `llmproxy`
- **Data Volume**: `./container/litellm/data/postgres_data`

### Container Images

Two specialized images are built for analysis:

1. **nvim-lsp:latest**
   - Neovim with LSP support
   - Language servers for multiple languages
   - Code analysis and navigation tools

2. **kali-ssh:latest**
   - Kali Linux security distribution
   - Pre-installed security testing tools
   - SSH server for remote access

## Troubleshooting

### Common Issues

#### 1. Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

#### 2. Port Conflicts
```bash
# Check if port 4000 is in use
lsof -i :4000
# Stop conflicting services or change port in docker-compose.yaml
```

#### 3. Python Version Issues
```bash
# Install Python 3.12 on Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-pip

# Or use pyenv
curl https://pyenv.run | bash
pyenv install 3.12.0
pyenv global 3.12.0
```

#### 4. Memory Issues
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory > 8GB+
# Or add swap space on Linux systems
```

#### 5. Container Build Failures
```bash
# Clean Docker cache and rebuild
docker system prune -a
make build-images
```

#### 6. LiteLLM Startup Issues
```bash
# Check logs
docker compose logs litellm

# Restart services
docker compose down
docker compose up -d
```

### Dependency Issues

#### uv Installation Problems
```bash
# Alternative uv installation methods
pip install uv
# or
pipx install uv
```

#### ChromaDB Issues
```bash
# Clear ChromaDB cache
rm -rf /tmp/ivexes/chromadb
# Or set custom path
export CHROMA_PATH="/path/to/your/chromadb"
```

### Performance Optimization

#### For Low-Memory Systems
```bash
# Use smaller models
export MODEL="openai/gpt-4o-mini"
export REASONING_MODEL="openai/gpt-4o-mini"

# Reduce max turns
export MAX_TURNS="5"
```

#### For Better Performance
```bash
# Use local embedding models
export EMBEDDING_PROVIDER="local"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Enable parallel processing
export PARALLEL_PROCESSING="true"
```

## Development Installation

For development work:

```bash
# Install with development dependencies
uv sync --all-extras --all-packages --group dev

# Install pre-commit hooks
uv run pre-commit install

# Run development tools
make format      # Format code
make lint        # Run linter
make tests       # Run tests
make build-docs  # Build documentation
make serve-docs  # Serve docs locally
```

## Next Steps

After successful installation:

1. **Configuration**: Review the [Configuration Guide](configuration.md) for detailed settings
2. **Usage**: Read the [Usage Guide](usage.md) to learn basic workflows
3. **Examples**: Explore the [Examples Guide](examples.md) for practical use cases
4. **Development**: See the [Development Guide](development.md) for contributing

## Getting Help

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting) above
2. Review the [Configuration Guide](configuration.md) for settings issues
3. Examine log files and error messages
4. Search existing GitHub issues
5. Create a new issue with detailed error information

## Related Topics

- [Architecture Guide](architecture.md) - System design and components
- [Configuration Guide](configuration.md) - Detailed configuration options
- [Usage Guide](usage.md) - Basic usage patterns
- [Development Guide](development.md) - Development setup and contribution