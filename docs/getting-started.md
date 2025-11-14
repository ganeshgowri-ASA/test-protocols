# Getting Started

This guide will help you set up and start using the PV Test Protocols Framework.

## Prerequisites

- Python 3.9 or higher
- pip or poetry for package management
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For development:

```bash
pip install -r requirements-dev.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` to configure:
- Database connection
- LIMS/QMS integration endpoints
- Application settings

### 5. Initialize Database

```python
from src.database.connection import init_db
init_db()
```

Or run the initialization script:

```bash
python -c "from src.database.connection import init_db; init_db()"
```

## Running the Application

### Start the Streamlit UI

```bash
streamlit run src/ui/streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

### Running Tests

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html  # On macOS/Linux
```

## Quick Start Guide

### 1. Navigate to the Application

Open your browser and go to `http://localhost:8501`

### 2. Start a New Test

1. Click on **"New Test"** in the sidebar
2. Select a protocol (e.g., TERM-001: Terminal Robustness Test)
3. Enter test information:
   - Test ID (auto-generated)
   - Module Serial Number
   - Operator Name
   - Test Conditions (temperature, humidity)
4. Click **"Start Test"**

### 3. Execute Test Steps

For each test step:

1. Read the step description and requirements
2. Enter all required measurements
3. Complete any input fields
4. Click **"Complete Step"** to move to the next step

The system will automatically:
- Validate that all required measurements are recorded
- Check acceptance criteria
- Calculate derived values
- Move to the next step if all criteria are met

### 4. View Results

After completing all steps:

1. Review the test summary and overall result
2. View charts and graphs of test data
3. Export results to PDF or Excel
4. Start a new test or return to home

### 5. Review Historical Results

1. Click on **"View Results"** in the sidebar
2. Filter by status, operator, or date
3. View detailed results for any test
4. Export reports as needed

## Project Structure

```
test-protocols/
├── src/
│   ├── protocols/          # Protocol definitions and implementations
│   │   ├── templates/      # JSON protocol templates
│   │   ├── base.py         # Base protocol classes
│   │   ├── models.py       # Pydantic models
│   │   └── term001.py      # TERM-001 implementation
│   ├── database/           # Database models and connection
│   │   ├── models.py       # SQLAlchemy models
│   │   └── connection.py   # Database connection
│   └── ui/                 # User interface components
│       ├── streamlit_app.py    # Main application
│       └── components/         # UI components
├── tests/                  # Test suite
├── docs/                   # Documentation
├── pyproject.toml         # Project configuration
└── requirements.txt       # Dependencies
```

## Next Steps

- Read the [Architecture Overview](architecture.md) to understand the system design
- Learn about [Protocol Format](protocol-format.md) to create custom protocols
- Check out the [API Reference](api-reference.md) for detailed API documentation
- Review [TERM-001 Protocol](term-001-protocol.md) documentation

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Check your `.env` file has the correct `DATABASE_URL`
2. Ensure the database file has write permissions
3. Try reinitializing the database: `python -c "from src.database.connection import init_db; init_db()"`

### Import Errors

If you see import errors:

1. Ensure you're in the virtual environment: `source venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.9+)

### Streamlit Issues

If Streamlit won't start:

1. Check port 8501 is not in use
2. Try a different port: `streamlit run src/ui/streamlit_app.py --server.port 8502`
3. Clear Streamlit cache: `streamlit cache clear`

## Support

For issues or questions:

1. Check the [documentation](README.md)
2. Review existing [GitHub issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
3. Create a new issue with detailed information
