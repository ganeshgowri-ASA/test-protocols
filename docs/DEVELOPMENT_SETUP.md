# Development Setup Guide

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Git
- Code editor (VS Code recommended)

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt
```

### 4. Setup Database

```bash
# Create database
createdb pv_testing_dev

# Run migrations
python manage.py db upgrade

# Load test data
python manage.py load_fixtures
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 6. Install Pre-commit Hooks

```bash
pre-commit install
```

## Development Workflow

### Running the Application

```bash
# Terminal 1: API server
uvicorn pv_testing.api.main:app --reload --port 8000

# Terminal 2: Streamlit dashboard
streamlit run streamlit_app.py --server.port 8501

# Terminal 3: Celery worker (optional)
celery -A pv_testing.tasks worker --loglevel=info
```

### Code Quality

```bash
# Format code
black pv_testing/ tests/

# Sort imports
isort pv_testing/ tests/

# Lint
pylint pv_testing/

# Type checking
mypy pv_testing/
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=pv_testing

# Watch mode
pytest-watch
```

## Project Structure

```
pv_testing/
├── api/              # FastAPI application
├── protocols/        # Protocol implementations
├── models/           # Database models
├── services/         # Business logic
├── integrations/     # External system integrations
├── analysis/         # Data analysis modules
├── reports/          # Report generation
└── utils/            # Utility functions

streamlit_app.py      # Streamlit dashboard entry point
templates/            # Protocol JSON templates
tests/                # Test suite
docs/                 # Documentation
deploy/               # Deployment scripts
```

## IDE Setup (VS Code)

### Recommended Extensions

- Python
- Pylance
- Black Formatter
- GitLens
- Docker
- PostgreSQL

### Settings

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

## Database Migrations

### Creating Migrations

```bash
# Auto-generate migration
alembic revision --autogenerate -m "description"

# Review generated migration
# Edit migrations/versions/xxxx_description.py if needed

# Apply migration
alembic upgrade head
```

### Managing Migrations

```bash
# Show current version
alembic current

# Show history
alembic history

# Downgrade
alembic downgrade -1
```

## Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Ensure tests pass
5. Submit pull request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-12
