.PHONY: help install dev-install test lint format clean run db-init db-migrate docs

help:  ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

dev-install:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev,docs]"

test:  ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-quick:  ## Run tests without coverage
	pytest tests/ -v

lint:  ## Run linter and type checking
	ruff check src/ tests/
	mypy src/

format:  ## Format code with ruff
	ruff format src/ tests/
	ruff check --fix src/ tests/

clean:  ## Clean up temporary files
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:  ## Run Streamlit UI
	streamlit run src/ui/app.py

db-init:  ## Initialize database
	python -c "from src.models.base import get_engine, init_db; engine = get_engine(); init_db(engine); print('Database initialized!')"

db-reset:  ## Reset database (WARNING: deletes all data)
	rm -f test_protocols.db
	$(MAKE) db-init

load-protocols:  ## Load all protocols from protocols/ directory
	python -c "from src.parsers import ProtocolLoader; from src.models.base import get_engine, get_session; from pathlib import Path; loader = ProtocolLoader(); engine = get_engine(); session = get_session(engine); protocols = loader.load_protocol_directory(Path('protocols')); [loader.import_to_database(p, session) for p in protocols]; print(f'Loaded {len(protocols)} protocols')"

docs-serve:  ## Serve documentation locally
	mkdocs serve

docs-build:  ## Build documentation
	mkdocs build

setup-dev:  ## Complete development setup
	$(MAKE) dev-install
	$(MAKE) db-init
	$(MAKE) load-protocols
	@echo "Development environment ready!"

.DEFAULT_GOAL := help
