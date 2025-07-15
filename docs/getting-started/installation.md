# Installation Guide

This guide provides detailed instructions for installing IVEXES in various environments and configurations.

## System Requirements

### Minimum Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| Python | 3.8+ | 3.9+ recommended for optimal performance |
| RAM | 2GB | 4GB+ recommended for multi-agent analysis |
| Disk Space | 3GB | 5GB+ for full container setup |
| Docker | Latest | Required for sandbox functionality |
| Git | Any recent version | For source code management |

### Recommended Setup

- **Python 3.11** - Best performance and compatibility
- **Docker Desktop** - Easier container management
- **8GB+ RAM** - For complex vulnerability analysis
- **SSD Storage** - Faster container and database operations

## Installation Steps

### 1. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/LetsDrinkSomeTea/ivexes.git
cd ivexes

# Verify the repository structure
ls -la
```

### 2. Set Up Python Environment

It's highly recommended to use a virtual environment:

=== "venv (Built-in)"
    ```bash
    # Create virtual environment
    python -m venv venv
    
    # Activate (Linux/macOS)
    source venv/bin/activate
    
    # Activate (Windows)
    venv\Scripts\activate
    
    # Verify activation
    which python
    ```

=== "conda"
    ```bash
    # Create conda environment
    conda create -n ivexes python=3.11
    conda activate ivexes
    
    # Verify environment
    conda info --envs
    ```

=== "pyenv + virtualenv"
    ```bash
    # Install specific Python version
    pyenv install 3.11.0
    pyenv virtualenv 3.11.0 ivexes
    pyenv activate ivexes
    ```

### 3. Install IVEXES

Choose your installation method based on your use case:

=== "Standard Installation"
    ```bash
    # Install core dependencies
    pip install -e .
    
    # Verify installation
    python -c "import ivexes; print('Installation successful!')"
    ```

=== "Development Installation"
    ```bash
    # Install with development tools
    pip install -e ".[dev]"
    
    # Set up pre-commit hooks
    pre-commit install
    
    # Run code quality checks
    ruff check
    ruff format --check
    ```

=== "Full Installation"
    ```bash
    # Install everything including documentation tools
    pip install -e ".[dev,docs]"
    
    # Verify all components
    mkdocs --version
    ruff --version
    ```

### 4. Container Setup

IVEXES uses Docker containers for sandbox environments:

```bash
# Build container images
docker compose --profile images build

# Start supporting services
docker compose up -d

# Verify containers are running
docker ps
```

### 5. Verify Installation

Run the verification script to ensure everything is working:

```bash
# Check core functionality
python -c "
from ivexes.config import Settings
from ivexes.agents import SingleAgent
print('✓ Core imports successful')
print('✓ IVEXES installation verified')
"
```

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv docker.io git

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Continue with standard installation
```

### Linux (CentOS/RHEL/Fedora)

```bash
# Install system dependencies
sudo dnf install -y python3-pip python3-venv docker git

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Continue with standard installation
```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 docker git

# Start Docker Desktop
open /Applications/Docker.app

# Continue with standard installation
```

### Windows

!!! note "Windows Installation"
    Windows installation requires additional setup for Docker and WSL2.

1. **Install WSL2**:
   ```powershell
   wsl --install
   ```

2. **Install Docker Desktop** with WSL2 backend

3. **Install Python 3.11** from [python.org](https://python.org)

4. **Use PowerShell or WSL2** for installation commands

## Troubleshooting Installation

### Common Issues

!!! failure "pip install fails"
    ```bash
    # Update pip first
    python -m pip install --upgrade pip
    
    # Clear pip cache
    pip cache purge
    
    # Try installation again
    pip install -e .
    ```

!!! failure "Docker permission denied"
    ```bash
    # Add user to docker group (Linux)
    sudo usermod -aG docker $USER
    newgrp docker
    
    # Or use sudo for docker commands
    sudo docker ps
    ```

!!! failure "Import errors after installation"
    ```bash
    # Check if you're in the right environment
    which python
    pip list | grep ivexes
    
    # Reinstall if necessary
    pip uninstall ivexes
    pip install -e .
    ```

### Dependency Conflicts

If you encounter dependency conflicts:

```bash
# Check for conflicts
pip check

# Create fresh environment
python -m venv fresh_env
source fresh_env/bin/activate
pip install -e .
```

### Docker Issues

!!! tip "Docker Troubleshooting"
    ```bash
    # Check Docker installation
    docker --version
    docker run hello-world
    
    # Free up space if needed
    docker system prune
    
    # Restart Docker service (Linux)
    sudo systemctl restart docker
    ```

## Verification Checklist

After installation, verify these components work:

- [ ] Python imports: `python -c "import ivexes"`
- [ ] Docker access: `docker ps`
- [ ] Configuration: `python -c "from ivexes.config import Settings; print(Settings())"`
- [ ] Container build: `docker compose --profile images build`

## Next Steps

Once installation is complete:

1. [Configure your environment](configuration.md)
2. [Run the quickstart tutorial](quickstart.md)
3. [Explore the examples](../examples/index.md)

## Getting Help

If you're still having issues:

- Check the [FAQ](../contributing/index.md#faq)
- Search existing [GitHub issues](https://github.com/LetsDrinkSomeTea/ivexes/issues)
- Create a new issue with your installation details