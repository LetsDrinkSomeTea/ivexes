# Quick Start Guide

Get up and running with IVExES in under 10 minutes. This guide walks you through the essential steps to install, configure, and run your first vulnerability analysis.

## 🚀 1-Minute Setup

The fastest way to get IVExES running:

```bash
# Clone and setup everything
git clone https://github.com/LetsDrinkSomeTea/ivexes.git
cd ivexes
make setup

# Add your API key
echo "LLM_API_KEY=your_openai_api_key_here" > .secrets.env

# Start analyzing!
python examples/20_mvp_screen.py
```

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.12+** - Check with `python --version`
- **Docker** - Check with `docker --version` 
- **Git** - Check with `git --version`
- **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)

!!! tip "Quick Check"
    Run this command to verify all prerequisites:
    ```bash
    python --version && docker --version && git --version
    ```

## 🛠️ Installation

### Option 1: Automated Setup (Recommended)

The `make setup` command handles everything:

```bash
git clone https://github.com/LetsDrinkSomeTea/ivexes.git
cd ivexes
make setup
```

This will:
- ✅ Build Docker images (nvim-lsp, kali-ssh)
- ✅ Install Python dependencies with uv
- ✅ Start LiteLLM proxy server
- ✅ Initialize vector databases

### Option 2: Manual Setup

For more control over the process:

```bash
# 1. Clone repository
git clone https://github.com/LetsDrinkSomeTea/ivexes.git
cd ivexes

# 2. Install dependencies
make sync  # or: uv sync --all-extras --all-packages --group dev

# 3. Build containers
make build-images  # or: docker compose --profile images build

# 4. Start services
make run-litellm  # or: docker compose up -d
```

## 🔑 Configuration

### Essential Configuration

Create your API key configuration:

```bash
# Create secrets file (never commit this!)
cat > .secrets.env << EOF
LLM_API_KEY=your_openai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
LLM_BASE_URL=http://localhost:4000/v1
EOF
```

### Basic Settings (Optional)

Create a `.env` file for additional settings:

```bash
cat > .env << EOF
MODEL=openai/gpt-4o-mini
REASONING_MODEL=openai/o4-mini
TEMPERATURE=0.3
MAX_TURNS=10
LOG_LEVEL=INFO
EOF
```

## ✅ Verification

Verify your installation is working:

### 1. Check Services
```bash
# Verify LiteLLM proxy is running
curl http://localhost:4000/health/liveliness

# Check Docker containers
docker compose ps
```

### 2. Test Import
```bash
python -c "import ivexes; print('✅ IVExES imported successfully')"
```

### 3. Run Test Suite
```bash
make tests
```

## 🎯 Your First Analysis

### Example 1: MVP Agent (Quickest Start)

The MVP Agent provides a minimal viable analysis:

```python
import asyncio
from ivexes.agents import MVPAgent
from ivexes.config import PartialSettings

# Basic configuration
settings = PartialSettings(
    model='openai/gpt-4o-mini',
    max_turns=10
)

# Create and run agent
agent = MVPAgent(settings=settings)
asyncio.run(agent.run_interactive())
```

Save this as `my_first_analysis.py` and run:
```bash
python my_first_analysis.py
```

### Example 2: Single Agent with Codebase

For analyzing actual code vulnerabilities:

```python
import asyncio
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

settings = PartialSettings(
    model='openai/gpt-4o-mini',
    codebase_path='/path/to/your/project',
    vulnerable_folder='vulnerable-version',
    patched_folder='patched-version',
    max_turns=15
)

agent = SingleAgent(settings=settings)
asyncio.run(agent.run_interactive())
```

### Example 3: Using Pre-built Examples

Run one of the included examples:

```bash
# MVP analysis example
python examples/20_mvp_screen.py

# Single agent analysis
python examples/60_single_agent_screen.py

# Multi-agent orchestration
python examples/70_multi_agent_screen.py
```

## 🗨️ Interaction Modes

IVExES supports three execution modes:

### Interactive Mode
```python
await agent.run_interactive()
```
- ✅ Best for exploration and learning
- ✅ Real-time conversation with the agent
- ✅ Type `exit`, `quit`, or `q` to end

### Streaming Mode
```python
async for chunk in agent.run_streamed():
    print(chunk, end='')
```
- ✅ Real-time output as analysis progresses
- ✅ Good for monitoring long-running analyses
- ✅ Integrates well with web interfaces

### Synchronous Mode
```python
result = agent.run()
print(result)
```
- ✅ Simple one-shot analysis
- ✅ Best for scripting and automation
- ✅ Returns complete analysis result

## 🎨 Customization

### Model Selection

Choose different models for different tasks:

```python
settings = PartialSettings(
    model='openai/gpt-4o',           # More capable but slower
    reasoning_model='openai/o4-mini', # For complex reasoning
    temperature=0.1,                  # More deterministic
)
```

### Analysis Scope

Configure what gets analyzed:

```python
settings = PartialSettings(
    codebase_path='/path/to/project',
    vulnerable_folder='v1.0-vulnerable',
    patched_folder='v1.1-patched',
    setup_archive='/path/to/setup.tgz',  # Optional setup files
)
```

### Vector Database

Enable enhanced knowledge base searching:

```python
settings = PartialSettings(
    embedding_provider='openai',        # or 'builtin', 'local'
    embedding_model='text-embedding-3-large',
    chroma_path='/custom/db/path',      # Optional custom path
)
```

## 🔧 Common Workflows

### 1. CVE Analysis
```python
from ivexes.agents import SingleAgent

# Analyze a specific CVE
agent = SingleAgent()
# In interactive mode, ask:
# "Analyze CVE-2024-12345 and explain the vulnerability"
```

### 2. Code Diff Analysis
```python
settings = PartialSettings(
    codebase_path='/path/to/project',
    vulnerable_folder='before-patch',
    patched_folder='after-patch'
)
agent = SingleAgent(settings=settings)
# Ask: "What vulnerability was fixed in the patch?"
```

### 3. CTF Challenge
```python
from ivexes.agents import HTBChallengeAgent

agent = HTBChallengeAgent(
    challenge_name="buffer_overflow_basic",
    settings=settings
)
```

## 🐛 Troubleshooting

### Common Issues

**❌ "ModuleNotFoundError: No module named 'ivexes'"**
```bash
# Reinstall dependencies
make sync
# or
uv sync --all-extras --all-packages --group dev
```

**❌ "Connection refused" when contacting LiteLLM**
```bash
# Restart LiteLLM service
docker compose restart litellm
# Check if port 4000 is available
lsof -i :4000
```

**❌ "Docker permission denied"**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

**❌ "API key not found"**
```bash
# Verify .secrets.env exists and contains your key
cat .secrets.env
# Ensure the file is in the project root directory
```

### Getting Help

1. **Check logs**: `docker compose logs litellm`
2. **Run diagnostics**: `make tests`
3. **Review configuration**: See [Configuration Guide](documentation/configuration.md)
4. **Search issues**: Check [GitHub Issues](https://github.com/LetsDrinkSomeTea/ivexes/issues)

## 🎓 Learning Path

Now that you're up and running, here's your learning path:

### Beginner (First Hour)
1. ✅ Complete this quickstart guide
2. 📖 Read [Usage Guide](documentation/usage.md) for basic workflows
3. 🔍 Explore [Examples](documentation/examples.md) for practical use cases

### Intermediate (First Day)
1. 🏗️ Understand [Architecture](documentation/architecture.md) 
2. ⚙️ Master [Configuration](documentation/configuration.md) options
3. 🤖 Learn about different [Agent Types](api/agents.md)

### Advanced (First Week)
1. 🛠️ Study [Development Guide](documentation/development.md)
2. 🔌 Explore [API Reference](api/agents.md) for all components
3. 🚀 Build custom agents and tools

## 💡 Pro Tips

!!! success "Performance Tip"
    Start with `gpt-4o-mini` for faster responses, then upgrade to `gpt-4o` for complex analyses.

!!! info "Cost Optimization"
    Set `MAX_TURNS=5` for initial testing to limit API usage.

!!! warning "Security Note"
    Never commit `.secrets.env` to version control. Add it to `.gitignore`.

!!! tip "Debugging"
    Set `LOG_LEVEL=DEBUG` in your `.env` file for detailed troubleshooting information.

## 🚀 Next Steps

Choose your path:

- **🔍 Explore Examples**: Try different [analysis examples](documentation/examples.md)
- **⚙️ Advanced Setup**: Customize your [configuration](documentation/configuration.md)
- **🏗️ Learn Architecture**: Understand the [system design](documentation/architecture.md)
- **🛠️ Start Developing**: Read the [development guide](documentation/development.md)
- **📚 API Deep Dive**: Browse the [API reference](api/agents.md)

**Ready for your first real analysis?** Head to the [Usage Guide](documentation/usage.md) to learn core workflows and best practices.