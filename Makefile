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
	uv run python -m unittest discover -s tests -v

.PHONY: build-docs
build-docs:
	uv run mkdocs build

.PHONY: serve-docs
serve-docs:
	uv run mkdocs serve

.PHONY: deploy-docs
deploy-docs:
	uv run mkdocs gh-deploy --force --verbose

.PHONY: build-images
build-images:
	docker compose --profile images build

.PHONY: run-litellm
run-litellm:
	docker compose up -d

.PHONY: setup
setup: build-images sync run-litellm

.PHONY: check
check: format-check lint tests
