.PHONY: help install install-dev test lint format clean docs run-ui setup-db

help:
	@echo "Available commands:"
	@echo "  make install      - Install package dependencies"
	@echo "  make install-dev  - Install package with development dependencies"
	@echo "  make test         - Run tests with pytest"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code with black and isort"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make docs         - Build documentation"
	@echo "  make run-ui       - Start Streamlit UI"
	@echo "  make setup-db     - Initialize database"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs,integrations]"

test:
	pytest tests/ -v --cov=test_protocols --cov-report=html --cov-report=term

lint:
	flake8 src/test_protocols tests/
	mypy src/test_protocols

format:
	black src/test_protocols tests/
	isort src/test_protocols tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	cd docs && sphinx-build -b html . _build/html

run-ui:
	streamlit run src/test_protocols/ui/streamlit_app.py

setup-db:
	python scripts/setup_database.py

.DEFAULT_GOAL := help
