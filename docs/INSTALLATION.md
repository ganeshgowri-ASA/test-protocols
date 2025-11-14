# Installation Guide

## System Requirements

- Python 3.8 or higher
- 2GB RAM minimum (4GB recommended)
- 500MB disk space
- Web browser (for Streamlit UI)

## Installation Methods

### Method 1: Using pip (Recommended)

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install package and dependencies
pip install -e .
```

### Method 2: Using requirements.txt

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Method 3: Development Installation

For development with additional tools:

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or install all extras
pip install -e ".[dev,docs]"
```

## Database Setup

### Initialize Database

```bash
# Initialize SQLite database
python -m src.db.database
```

This creates `test_protocols.db` in the project root.

### Using PostgreSQL (Optional)

```bash
# Set database URL environment variable
export DATABASE_URL="postgresql://user:password@localhost/test_protocols"

# Initialize database
python -m src.db.database
```

## Verify Installation

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_wind_001.py
```

### Run Example Protocol

```bash
python -m src.protocols.wind_001
```

Expected output:
```
========================================
WIND-001 Wind Load Test Summary Report
========================================
...
Status: PASS
...
```

## Launch Streamlit UI

```bash
streamlit run src/ui/wind_001_ui.py
```

The UI will open in your default web browser at `http://localhost:8501`

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=sqlite:///test_protocols.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=test_protocols.log

# UI
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# Integration endpoints (optional)
LIMS_API_URL=https://lims.example.com/api
QMS_API_URL=https://qms.example.com/api
```

### Protocol Configuration

Protocol configurations are stored in:
```
protocols/mechanical/wind-001/
├── config.json
└── schema.json
```

Modify these files to customize test parameters and acceptance criteria.

## Troubleshooting

### Issue: Module not found errors

**Solution:**
```bash
# Ensure you're in the project root
pwd

# Reinstall in editable mode
pip install -e .
```

### Issue: Database connection errors

**Solution:**
```bash
# Check database file exists
ls -la test_protocols.db

# Reinitialize database
python -m src.db.database
```

### Issue: Streamlit won't start

**Solution:**
```bash
# Check Streamlit installation
streamlit --version

# Reinstall Streamlit
pip install --upgrade streamlit

# Try running with full path
python -m streamlit run src/ui/wind_001_ui.py
```

### Issue: Import errors in tests

**Solution:**
```bash
# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Or use pytest with src path
python -m pytest tests/
```

## Updating

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -e . --upgrade

# Run database migrations (if any)
# alembic upgrade head
```

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv/

# Remove database (optional)
rm test_protocols.db

# Remove project directory
cd ..
rm -rf test-protocols/
```

## Docker Installation (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

EXPOSE 8501

CMD ["streamlit", "run", "src/ui/wind_001_ui.py"]
```

Build and run:

```bash
docker build -t test-protocols .
docker run -p 8501:8501 test-protocols
```

## Next Steps

- Read the [WIND-001 Documentation](WIND-001.md)
- Check the [API Documentation](API.md)
- Try running a test through the Streamlit UI
- Explore the example data in `protocols/mechanical/wind-001/`

## Support

For installation issues:
- Check the [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- Contact: test-protocols@example.com
