.PHONY: help install install-dev test test-cov lint format type-check clean docs docs-serve build publish pre-commit

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv pip install -e .

install-dev: ## Install development dependencies
	uv pip install -e ".[dev]"
	uv pip install -e ".[docs]"
	pre-commit install

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov=subtitleflow --cov-report=term-missing --cov-report=html --cov-report=xml

test-cov-fail: ## Run tests with coverage, fail if below 80%
	uv run pytest --cov=subtitleflow --cov-report=term-missing --cov-fail-under=80

lint: ## Run linters (ruff)
	uv run ruff check .

lint-fix: ## Run linters and auto-fix issues
	uv run ruff check --fix .

format: ## Format code with ruff
	uv run ruff format .

format-check: ## Check code formatting without making changes
	uv run ruff format --check .

type-check: ## Run type checkers (mypy + pyright)
	uv run mypy subtitleflow
	uv run pyright subtitleflow

type-check-mypy: ## Run mypy only
	uv run mypy subtitleflow

type-check-pyright: ## Run pyright only
	uv run pyright subtitleflow

clean: ## Remove build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

docs: ## Build documentation
	uv run mkdocs build

docs-serve: ## Serve documentation locally
	uv run mkdocs serve

docs-deploy: ## Deploy documentation to GitHub Pages
	uv run mkdocs gh-deploy --force

build: clean ## Build distribution packages
	uv build

publish: build ## Publish to PyPI
	uv publish

pre-commit: ## Run all pre-commit hooks
	pre-commit run --all-files

check-all: lint format-check type-check test-cov ## Run all checks (lint, format, type-check, test with coverage)

ci: check-all ## Run CI pipeline locally
