# Getting Started with PV Test Protocol System

## Overview

The PV Test Protocol System is a modular framework for executing photovoltaic module test protocols with automated data collection, quality control, analysis, and reporting.

## Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ganeshgowri-ASA/test-protocols.git
   cd test-protocols
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python -c "from src.database import init_database; init_database()"
   ```

### Running the Application

**Start the Streamlit UI:**
```bash
streamlit run src/ui/app.py
```

The application will open in your web browser at `http://localhost:8501`

## System Architecture

### Directory Structure

```
test-protocols/
├── protocols/                  # Protocol definitions
│   ├── templates/             # JSON protocol templates
│   │   └── degradation/       # Degradation test protocols
│   │       └── pid-002.json   # PID-002 protocol
│   └── schemas/               # JSON validation schemas
├── src/                       # Source code
│   ├── core/                  # Core protocol engine
│   │   ├── protocol_loader.py
│   │   ├── protocol_validator.py
│   │   └── protocol_executor.py
│   ├── ui/                    # Streamlit UI components
│   │   ├── app.py            # Main application
│   │   └── components/       # Reusable UI components
│   ├── analysis/             # Data analysis modules
│   ├── integrations/         # External system integrations
│   └── database/             # Database models
│       ├── models.py         # SQLAlchemy models
│       └── database.py       # Database management
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── docs/                    # Documentation
│   ├── protocols/           # Protocol user guides
│   └── api/                 # API documentation
├── data/                    # Database and data files
└── reports/                 # Generated test reports
```

## Core Concepts

### 1. Protocols

Protocols are defined in JSON format and contain:
- **Test parameters** - Configurable test conditions
- **Equipment requirements** - Required instruments and calibration
- **Test sequence** - Steps and substeps with data fields
- **QC rules** - Automated quality control checks
- **Analysis configuration** - Charts, statistics, calculations
- **Report configuration** - Report structure and content

Example protocol structure:
```json
{
  "protocol_id": "PID-002",
  "name": "Potential-Induced Degradation Test",
  "version": "1.0.0",
  "category": "degradation",
  "test_sequence": {
    "steps": [...]
  },
  "qc_rules": [...],
  "analysis_config": {...}
}
```

### 2. Test Execution

Test execution follows these phases:

1. **Protocol Selection** - Choose from available protocols
2. **Protocol Validation** - Verify protocol structure
3. **Test Initialization** - Create test run and metadata
4. **Step Execution** - Execute each step/substep sequentially
5. **Data Collection** - Record measurements and observations
6. **QC Validation** - Real-time quality control checks
7. **Test Completion** - Finalize and save test data
8. **Analysis & Reporting** - Generate charts and reports

### 3. Data Model

The system uses SQLAlchemy ORM with the following key entities:

- **Protocol** - Protocol definitions
- **TestRun** - Individual test executions
- **TestStep** - Step execution records
- **Measurement** - Individual measurements
- **QCFlag** - Quality control flags
- **Equipment** - Equipment registry
- **Sample** - Sample/module registry

## Using the System

### Creating a New Test Run

1. Navigate to **New Test** in the sidebar
2. Select a protocol from the dropdown
3. Review protocol information
4. Click **Start Test Run**
5. Follow the guided workflow:
   - Complete each step in sequence
   - Enter required data in forms
   - Review QC alerts
   - Monitor progress
6. Review results and generate report

### Working with Protocols

#### Loading a Protocol

```python
from src.core import ProtocolLoader

loader = ProtocolLoader()
protocol = loader.load_protocol("PID-002")
```

#### Validating a Protocol

```python
from src.core import ProtocolValidator

validator = ProtocolValidator()
is_valid, errors = validator.validate_protocol_structure(protocol)

if not is_valid:
    print("Validation errors:", errors)
```

#### Executing a Protocol

```python
from src.core import ProtocolExecutor, StepStatus

executor = ProtocolExecutor(protocol, "TEST-RUN-001")
executor.start_test(metadata={"operator": "John Doe"})

# Execute a step
executor.start_step(step_id=1, substep_id=1.1)
executor.record_data(1, 1.1, {"test_value": 42.5})
executor.complete_step(1, 1.1, StepStatus.COMPLETED)

# Complete test
executor.complete_test(StepStatus.COMPLETED)

# Get results
test_data = executor.get_test_data()
```

### Database Operations

#### Initialize Database

```python
from src.database import init_database

db_manager = init_database(database_url="sqlite:///data/test_protocols.db")
```

#### Query Test Runs

```python
from src.database import get_db_manager, TestRun

db_manager = get_db_manager()

with db_manager.session_scope() as session:
    test_runs = session.query(TestRun).filter_by(
        protocol_id="PID-002"
    ).all()

    for run in test_runs:
        print(f"{run.test_run_id}: {run.status}")
```

#### Save Test Run

```python
from src.database import get_db_manager, TestRun, TestRunStatus

db_manager = get_db_manager()

with db_manager.session_scope() as session:
    test_run = TestRun(
        test_run_id="TEST-001",
        protocol_id=1,
        protocol_version="1.0.0",
        status=TestRunStatus.IN_PROGRESS,
        sample_id="MODULE-001",
        operator_id="JOHN_DOE"
    )
    session.add(test_run)
    # Automatically committed when context exits
```

## Running Tests

### Unit Tests

```bash
pytest tests/unit/
```

### Integration Tests

```bash
pytest tests/integration/
```

### All Tests with Coverage

```bash
pytest --cov=src tests/
```

## Configuration

### Database Configuration

The default database is SQLite stored in `data/test_protocols.db`. To use PostgreSQL:

```python
from src.database import init_database

db_manager = init_database(
    database_url="postgresql://user:password@localhost/test_protocols"
)
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=sqlite:///data/test_protocols.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/test_protocols.log

# UI
UI_PORT=8501
UI_HOST=localhost
```

## Available Protocols

### PID-002: Potential-Induced Degradation Test

- **Category:** Degradation
- **Standard:** IEC 62804-1
- **Duration:** ~12 days (192h stress + 96h recovery)
- **Purpose:** Evaluate PV module susceptibility to PID

See [PID-002 User Guide](protocols/PID-002-User-Guide.md) for detailed information.

## API Reference

### Protocol Loader API

```python
class ProtocolLoader:
    def load_protocol(self, protocol_id: str) -> Dict[str, Any]
    def load_protocol_from_file(self, file_path: Path) -> Dict[str, Any]
    def list_protocols(self) -> List[Dict[str, Any]]
    def get_protocol_metadata(self, protocol_id: str) -> Dict[str, Any]
    def get_test_steps(self, protocol_id: str) -> List[Dict[str, Any]]
```

### Protocol Validator API

```python
class ProtocolValidator:
    def validate_protocol_structure(self, protocol: Dict[str, Any]) -> Tuple[bool, List[str]]
    def validate_test_data(self, protocol: Dict[str, Any], step_id: int,
                          substep_id: float, data: Dict[str, Any]) -> Tuple[bool, List[str]]
    def check_qc_rules(self, protocol: Dict[str, Any],
                      test_data: Dict[str, Any]) -> List[Dict[str, Any]]
```

### Protocol Executor API

```python
class ProtocolExecutor:
    def start_test(self, metadata: Optional[Dict[str, Any]] = None)
    def start_step(self, step_id: int, substep_id: float) -> Dict[str, Any]
    def record_data(self, step_id: int, substep_id: float, data: Dict[str, Any])
    def complete_step(self, step_id: int, substep_id: float,
                     status: StepStatus, notes: Optional[str] = None)
    def add_qc_flag(self, rule_id: str, severity: str, message: str)
    def complete_test(self, status: StepStatus)
    def get_test_data(self) -> Dict[str, Any]
    def get_progress(self) -> Dict[str, Any]
```

## Best Practices

### Protocol Development

1. **Use Semantic Versioning** - Version protocols as X.Y.Z
2. **Validate Thoroughly** - Test protocols before deployment
3. **Document Changes** - Maintain revision history
4. **Include QC Rules** - Add automated quality checks
5. **Provide Clear Instructions** - Include step-by-step guidance

### Data Management

1. **Regular Backups** - Back up database regularly
2. **Data Validation** - Validate all input data
3. **Error Handling** - Implement robust error handling
4. **Audit Trail** - Maintain complete audit trail
5. **Data Retention** - Follow data retention policies

### Testing

1. **Test Early** - Test protocols with sample data
2. **Validate Equipment** - Ensure equipment is calibrated
3. **Document Issues** - Record any anomalies or issues
4. **Review Results** - Review all results before finalizing
5. **Generate Reports** - Create comprehensive reports

## Troubleshooting

### Common Issues

**Database Connection Error**
```
Solution: Check DATABASE_URL and ensure database is initialized
```

**Protocol Not Found**
```
Solution: Verify protocol file exists in protocols/templates/
```

**Validation Errors**
```
Solution: Check protocol structure against required fields
Review validation error messages for specific issues
```

**UI Not Loading**
```
Solution: Check that all dependencies are installed
Verify Streamlit is running on correct port
```

## Support

- **Documentation:** See `docs/` directory
- **Issues:** Report issues on GitHub
- **Email:** support@example.com

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

**Next Steps:**
- Review [PID-002 User Guide](protocols/PID-002-User-Guide.md)
- Explore the UI by running `streamlit run src/ui/app.py`
- Try executing a sample test
- Review the API documentation
