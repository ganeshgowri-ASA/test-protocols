# Test Protocols Framework - Installation Guide

## Prerequisites

- Python 3.9 or higher
- PostgreSQL 12 or higher (for database backend)
- pip (Python package manager)
- Git

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

### 4. Database Setup (Optional)

If using PostgreSQL backend:

```bash
# Create database
createdb test_protocols

# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost/test_protocols"

# Initialize database schema
python scripts/init_database.py
```

Alternatively, use the SQL script directly:

```bash
psql -U username -d test_protocols -f database/schemas/create_tables.sql
```

### 5. Verify Installation

```bash
# Run tests to verify installation
pytest tests/

# Expected output: All tests should pass
```

### 6. Run the Application

```bash
# Start Streamlit UI
streamlit run ui/app.py

# The application will open in your default browser at http://localhost:8501
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database configuration
DATABASE_URL=postgresql://username:password@localhost/test_protocols

# Application settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# UI settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
address = "localhost"
```

## Development Setup

### Install Development Tools

```bash
pip install black flake8 mypy pytest pytest-cov
```

### Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

### Code Formatting

```bash
# Format code with Black
black protocols/ ui/ tests/

# Run linter
flake8 protocols/ ui/ tests/

# Type checking
mypy protocols/ ui/
```

## Docker Setup (Alternative)

```dockerfile
# Dockerfile (example)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "ui/app.py"]
```

```bash
# Build and run
docker build -t test-protocols .
docker run -p 8501:8501 test-protocols
```

## Database Migrations

Using Alembic for database migrations:

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Troubleshooting

### Issue: Module not found errors

**Solution**: Ensure virtual environment is activated and dependencies are installed:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Database connection errors

**Solution**: Verify PostgreSQL is running and DATABASE_URL is correct:

```bash
psql -U username -d test_protocols -c "SELECT 1"
```

### Issue: Streamlit not starting

**Solution**: Check port availability and Streamlit installation:

```bash
pip install --upgrade streamlit
streamlit run ui/app.py --server.port 8502  # Try different port
```

### Issue: Import errors in tests

**Solution**: Ensure PYTHONPATH includes project root:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

## Updating

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run database migrations
alembic upgrade head

# Verify with tests
pytest tests/
```

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv/

# Drop database (if created)
dropdb test_protocols
```

## Next Steps

After installation:

1. Read the [User Guide](CHALK-001_User_Guide.md) for CHALK-001 protocol
2. Review [API Documentation](API_Documentation.md) for development
3. Explore sample data in `tests/fixtures/`
4. Try running a test through the UI

## Support

For issues or questions:
- Check existing issues on GitHub
- Review documentation in `docs/`
- Contact the development team

## License

This project is licensed under the MIT License - see LICENSE file for details.
