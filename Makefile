.PHONY: help setup clean build release test lint format check install dev

help:
	@echo "Available commands:"
	@echo "  make setup     - Install dependencies with uv"
	@echo "  make dev       - Install development dependencies with uv"
	@echo "  make clean     - Remove build artifacts"
	@echo "  make build     - Build distribution packages"
	@echo "  make release   - Upload to PyPI"
	@echo "  make test      - Run tests with pytest"
	@echo "  make lint      - Run ruff linting"
	@echo "  make format    - Format code with ruff"
	@echo "  make check     - Run lint and format check"
	@echo "  make install   - Install package in editable mode"

setup:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"

clean:
	rm -rf dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache .ruff_cache .venv

build: clean
	uv build

release: build
	uv publish

test:
	.venv/bin/pytest -v

lint:
	.venv/bin/ruff check .

format:
	.venv/bin/ruff format .

check:
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .

install:
	uv pip install -e .
