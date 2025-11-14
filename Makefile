.PHONY: help install test run clean db-init db-migrate lint format

help:
	@echo "PV Test Protocol Framework - Available Commands"
	@echo ""
	@echo "  make install      Install dependencies"
	@echo "  make test         Run all tests"
	@echo "  make test-unit    Run unit tests only"
	@echo "  make test-int     Run integration tests only"
	@echo "  make coverage     Run tests with coverage report"
	@echo "  make run          Start Streamlit application"
	@echo "  make db-init      Initialize database"
	@echo "  make lint         Run code linting"
	@echo "  make format       Format code with black"
	@echo "  make clean        Clean temporary files"

install:
	pip install -r requirements.txt

test:
	pytest

test-unit:
	pytest tests/unit/ -v

test-int:
	pytest tests/integration/ -v

coverage:
	pytest --cov=src --cov-report=html --cov-report=term

run:
	streamlit run src/ui/app.py

db-init:
	python -c "from src.models import init_db; init_db(); print('Database initialized successfully')"

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache htmlcov .mypy_cache
	@echo "Cleaned temporary files"
