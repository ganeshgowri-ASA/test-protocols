# Getting Started with PV Testing Protocol Framework

## Overview

The PV Testing Protocol Framework is a modular, JSON-driven system for executing and managing photovoltaic module testing protocols. It provides:

- **JSON-based protocol definitions** - Easy to create and modify test procedures
- **Python backend** - Robust data processing and analysis
- **Streamlit UI** - Interactive web-based test execution interface
- **Database integration** - Comprehensive data storage and retrieval
- **Automated reporting** - Generate test reports in multiple formats
- **LIMS/QMS integration** - Ready for enterprise system integration

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) PostgreSQL for production database

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/test-protocols.git
   cd test-protocols
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python scripts/init_database.py
   ```

4. **Run the application**
   ```bash
   streamlit run src/ui/hail_001_ui.py
   ```

## Project Structure

```
test-protocols/
├── protocols/              # JSON protocol definitions
│   └── HAIL-001.json      # Hail impact test protocol
├── src/                   # Python source code
│   ├── protocols/         # Protocol loading and handling
│   ├── analysis/          # Data analysis and calculations
│   └── ui/                # Streamlit UI components
├── db/                    # Database schemas
│   ├── schemas/           # SQL schema definitions
│   └── migrations/        # Database migrations
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                  # Documentation
│   ├── protocols/        # Protocol-specific docs
│   └── guides/           # User guides
└── config/               # Configuration files
```

## Quick Start: Running a Test

### Using the Streamlit UI

1. **Start the application**
   ```bash
   streamlit run src/ui/hail_001_ui.py
   ```

2. **Navigate through tabs**
   - **Test Setup**: Enter module information
   - **Pre-Test**: Record initial measurements
   - **Impact Test**: Record impact test data
   - **Post-Test**: Record final measurements
   - **Results**: View analysis and pass/fail determination

3. **Export results**
   - Results are automatically saved to the database
   - Generate reports in JSON or Markdown format

### Using Python API

```python
from src.protocols.loader import ProtocolLoader
from src.protocols.hail_001 import HAIL001Protocol
from src.analysis.database import TestDatabase

# Load protocol
loader = ProtocolLoader("protocols")
protocol_data = loader.load_protocol("HAIL-001")
protocol = HAIL001Protocol(protocol_data)

# Create test session
db = TestDatabase("test_protocols.db")
session_id = db.create_session(
    protocol_id="HAIL-001",
    protocol_version="1.0.0",
    test_date="2025-11-14",
    test_operator="John Doe",
    facility="Test Lab A"
)

# Insert module info
module_data = {
    'manufacturer': 'SolarTech',
    'model': 'ST-300W',
    'serial_number': 'ST-2024-0001',
    'nameplate_power': 300.0
}
db.insert_module_info(session_id, module_data)

# ... proceed with test execution ...

# Analyze results
test_data = {
    'pre_test_data': pre_test_data,
    'test_execution_data': test_execution_data,
    'post_test_data': post_test_data
}

analysis_results = protocol.analyze_results(test_data)
pass_fail_results = protocol.evaluate_pass_fail(analysis_results)

print(f"Test Result: {pass_fail_results['overall_result']}")
```

## Creating a New Protocol

### Step 1: Create JSON Definition

Create a new file in `protocols/` directory (e.g., `protocols/CUSTOM-001.json`):

```json
{
  "protocol_id": "CUSTOM-001",
  "version": "1.0.0",
  "title": "Custom Test Protocol",
  "category": "Electrical",
  "standard": {
    "name": "Custom Standard",
    "reference": "CUSTOM-2024"
  },
  "test_parameters": {
    "parameter1": "value1"
  },
  "test_procedure": {
    "pre_test": [],
    "test_execution": [],
    "post_test": []
  },
  "pass_fail_criteria": {}
}
```

### Step 2: Implement Protocol Class

Create a new Python file in `src/protocols/` (e.g., `src/protocols/custom_001.py`):

```python
from .base import BaseProtocol

class CUSTOM001Protocol(BaseProtocol):
    def validate_test_data(self, test_data):
        # Implement validation logic
        pass

    def analyze_results(self, test_data):
        # Implement analysis logic
        pass

    def evaluate_pass_fail(self, analysis_results):
        # Implement pass/fail evaluation
        pass
```

### Step 3: Create UI Component

Create a Streamlit UI in `src/ui/` (e.g., `src/ui/custom_001_ui.py`):

```python
import streamlit as st
from src.protocols.loader import ProtocolLoader
from src.protocols.custom_001 import CUSTOM001Protocol

def main():
    st.title("CUSTOM-001 Test Protocol")
    # Implement UI logic
    pass

if __name__ == "__main__":
    main()
```

### Step 4: Create Database Schema

Create schema in `db/schemas/` (e.g., `db/schemas/custom_001_schema.sql`):

```sql
CREATE TABLE IF NOT EXISTS custom_test_sessions (
    session_id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(50) NOT NULL,
    -- Add protocol-specific fields
);
```

### Step 5: Write Tests

Create tests in `tests/unit/` and `tests/integration/`.

### Step 6: Document

Create documentation in `docs/protocols/CUSTOM-001.md`.

## Running Tests

### Run all tests
```bash
python -m pytest tests/
```

### Run unit tests only
```bash
python -m pytest tests/unit/
```

### Run integration tests only
```bash
python -m pytest tests/integration/
```

### Run specific test file
```bash
python -m pytest tests/unit/test_hail_001_protocol.py
```

### Run with coverage
```bash
python -m pytest --cov=src tests/
```

## Configuration

### Database Configuration

Edit `config/database.yaml`:

```yaml
database:
  type: postgresql  # or sqlite
  host: localhost
  port: 5432
  database: test_protocols
  username: test_user
  password: secure_password
```

### Application Configuration

Edit `config/app.yaml`:

```yaml
application:
  name: PV Testing Protocol Framework
  version: 1.0.0
  log_level: INFO
  data_directory: ./data
  report_directory: ./reports
```

## Troubleshooting

### Issue: Database connection error

**Solution**: Check database configuration in `config/database.yaml` and ensure database server is running.

### Issue: Protocol not found

**Solution**: Ensure protocol JSON file exists in `protocols/` directory and filename matches protocol ID.

### Issue: Import errors

**Solution**: Ensure all dependencies are installed with `pip install -r requirements.txt`.

### Issue: Streamlit won't start

**Solution**:
1. Check Python version (≥3.8 required)
2. Reinstall Streamlit: `pip install --upgrade streamlit`
3. Check port availability (default 8501)

## Best Practices

### Data Management

1. **Regular Backups**: Back up database regularly
2. **Data Validation**: Always validate test data before analysis
3. **Audit Trail**: Maintain complete audit trail of all tests
4. **Data Retention**: Follow organizational data retention policies

### Protocol Development

1. **Version Control**: Use semantic versioning for protocols
2. **Documentation**: Document all protocol changes
3. **Testing**: Write comprehensive tests for new protocols
4. **Peer Review**: Have protocols reviewed before deployment

### Testing Workflow

1. **Calibration**: Verify all equipment is calibrated before testing
2. **Documentation**: Document all test conditions and deviations
3. **Photography**: Take comprehensive photographs
4. **Review**: Review all data before finalizing test session

## Support

- **Documentation**: See `docs/` directory
- **Issues**: Report issues on GitHub
- **Email**: support@example.com

## Contributing

See `CONTRIBUTING.md` for contribution guidelines.

## License

MIT License - See `LICENSE` file for details.
