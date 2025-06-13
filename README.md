# IVEXES

IVEXES (Intelligent Vulnerability Extraction & Exploit Synthesis) is a Python framework that
combines a language model with several containerised tools to analyse source code
changes, search known vulnerability data and experiment with proof of concept
exploits.

## Features

- **Code browser** – A Neovim LSP container to inspect a code base and retrieve
  definitions, references, file contents and diffs.
- **Vector database** – Loads CWE and CAPEC data into a ChromaDB collection and
  provides semantic search for vulnerability descriptions.
- **Sandbox** – Launches a Kali Linux container via SSH for running exploit
  commands in isolation.
- **Agent** – `main.py` orchestrates these tools with an LLM to investigate a
  patch diff and iteratively generate an exploit.
- **CLI utilities** – `manual.py` exposes commands for the vector DB, code
  browser and sandbox without running the full agent.

## Installation

1. Build the Docker images required for the code browser and sandbox:

   ```bash
   docker compose build
   ```

2. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with at least the following variables (see
   `config/settings.py` for all options):

   ```bash
   OPENAI_API_KEY=your-openai-key
   CODEBASE_PATH=/absolute/path/to/codebase
   VULNERABLE_CODEBASE_FOLDER=vulnerable
   PATCHED_CODEBASE_FOLDER=patched
   SETUP_ARCHIVE=/path/to/setup.tar
   ```

## Usage

Run the interactive agent:

```bash
python main.py
```

For manual access to individual modules, use the CLI:

```bash
python manual.py --help
```

## Tests

The project contains unit tests for the vector database utilities. Execute them
with:

```bash
python tests/run_tests.py
```

## Ethical Considerations

IVEXES is a tool for security research and education. Use it responsibly and in
accordance with the law. Always obtain permission before scanning or exploiting
systems, and follow responsible disclosure practices when reporting
vulnerabilities.

## Total Cost:

- OpenAI: 5,65€ + 53,93€ = 59,58€
- Anthropic: 5,44€ + 52,99€ = 58,43€
