.PHONY: sync
sync:
	uv sync --all-extras --all-packages --group dev

.PHONY: format
format: 
	uv run ruff format
	uv run ruff check --fix

.PHONY: format-check
format-check:
	uv run ruff format --check

.PHONY: lint
lint: 
	uv run ruff check

.PHONY: tests
tests: 
	uv run python -m unittest discover -s tests

.PHONY: check
check: format-check lint tests

.PHONY: docs-serve
docs-serve:
	uv run mkdocs serve

.PHONY: docs-build
docs-build:
	uv run mkdocs build

.PHONY: docs-deploy
docs-deploy:
	uv run mkdocs gh-deploy
