# Development Setup

Guidelines for setting up a development environment for IVEXES.

## Prerequisites

- Python 3.9+
- Docker
- Git
- uv (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/LetsDrinkSomeTea/ivexes.git
cd ivexes
```

2. Install dependencies:
```bash
uv sync
```

3. Set up pre-commit hooks:
```bash
uv run pre-commit install
```

## Development Workflow

1. Create a feature branch
2. Make changes and test locally
3. Run tests and linting
4. Submit a pull request

## Running Tests

```bash
uv run pytest
```

## Code Quality

```bash
# Linting
uv run ruff check

# Type checking
uv run mypy

# Formatting
uv run ruff format
```

## Documentation

```bash
# Build documentation
uv run mkdocs build

# Serve documentation locally
uv run mkdocs serve
```

## See Also

- [Testing Guide](testing.md)
- [Code Style](style.md)