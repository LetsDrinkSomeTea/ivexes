# Getting Started

Welcome to IVEXES! This section will guide you through the installation process, initial configuration, and your first vulnerability analysis.

## Overview

IVEXES is designed to be easy to set up while providing powerful capabilities for cybersecurity research and vulnerability analysis. The framework consists of several key components that work together:

- **Agent System**: AI-driven analysis coordination
- **Code Browser**: Advanced code analysis with LSP support
- **Sandbox Environment**: Isolated execution for safe testing
- **Vector Database**: Knowledge base integration
- **Container Support**: Docker-based isolation

## Prerequisites

Before installing IVEXES, ensure you have the following requirements:

### System Requirements

- **Python 3.8+** - IVEXES requires modern Python features
- **Docker** - For sandbox environments and containerized analysis
- **Git** - For version control and source management
- **4GB+ RAM** - Recommended for optimal performance
- **5GB+ Disk Space** - For containers and knowledge bases

### API Access

IVEXES requires access to a Large Language Model (LLM) service:

- **OpenAI API** - Recommended for best performance
- **Compatible APIs** - Any OpenAI-compatible service
- **Local Models** - Via LiteLLM proxy setup

## Installation Methods

Choose the installation method that best fits your use case:

=== "Standard Installation"
    
    Perfect for most users who want to use IVEXES for vulnerability analysis:
    
    ```bash
    # Clone the repository
    git clone https://github.com/LetsDrinkSomeTea/ivexes.git
    cd ivexes
    
    # Install the package
    pip install -e .
    ```

=== "Development Installation"
    
    For contributors and advanced users who want all development tools:
    
    ```bash
    # Clone the repository  
    git clone https://github.com/LetsDrinkSomeTea/ivexes.git
    cd ivexes
    
    # Install with development dependencies
    pip install -e ".[dev]"
    
    # Install pre-commit hooks
    pre-commit install
    ```

=== "Documentation Build"
    
    For building and viewing documentation locally:
    
    ```bash
    # Install with documentation dependencies
    pip install -e ".[docs]"
    
    # Build and serve documentation
    mkdocs serve
    ```

## Next Steps

Once you have IVEXES installed, continue with:

1. [**Installation Guide**](installation.md) - Detailed installation instructions
2. [**Configuration**](configuration.md) - Set up your environment and API keys
3. [**Quick Start**](quickstart.md) - Run your first vulnerability analysis

## Getting Help

If you encounter any issues during installation:

- Check the [Troubleshooting](#troubleshooting) section below
- Review the [Examples](../examples/index.md) directory
- Open an issue on [GitHub](https://github.com/LetsDrinkSomeTea/ivexes/issues)

## Troubleshooting

### Common Installation Issues

!!! failure "Permission Denied"
    If you encounter permission errors during installation:
    ```bash
    # Use user installation
    pip install --user -e .
    
    # Or use virtual environment (recommended)
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # or
    venv\Scripts\activate     # Windows
    pip install -e .
    ```

!!! failure "Docker Not Found"
    Ensure Docker is installed and running:
    ```bash
    # Check Docker installation
    docker --version
    docker run hello-world
    
    # Start Docker service (Linux)
    sudo systemctl start docker
    ```

!!! failure "Python Version"
    IVEXES requires Python 3.8+:
    ```bash
    # Check Python version
    python --version
    
    # Install Python 3.8+ if needed
    # Use pyenv, conda, or your system package manager
    ```

### Environment Issues

!!! warning "Import Errors"
    If you see import errors after installation:
    ```bash
    # Ensure you're in the right environment
    which python
    pip list | grep ivexes
    
    # Reinstall if necessary
    pip uninstall ivexes
    pip install -e .
    ```