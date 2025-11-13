# Usage Guide

## Getting Started with PV Testing Protocol Framework

This guide will walk you through using the framework for photovoltaic module testing.

## Table of Contents

1. [Installation](#installation)
2. [Running Your First Test](#running-your-first-test)
3. [Understanding Test Results](#understanding-test-results)
4. [Leakage Tracking](#leakage-tracking)
5. [QC Validation](#qc-validation)
6. [Advanced Features](#advanced-features)

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python scripts/init_db.py

# 5. Verify installation
pytest tests/unit/test_schema_validator.py
```

## Running Your First Test

### Using the Streamlit UI

1. **Start the application**:
   ```bash
   streamlit run src/ui/streamlit_app.py
   ```

2. **Navigate to the Run Test page**:
   - Select "▶️ Run Test" from the sidebar
   - Choose "pid-001 - PID Shunting Test Protocol"

3. **Configure test parameters**:
   - Test Name: `PID-TEST-001`
   - Module ID: `PV-MODULE-12345`
   - Test Voltage: `-1000` V
   - Test Duration: `96` hours
   - Temperature: `85` °C
   - Relative Humidity: `85` %

4. **Start the test**:
   - Click "Start Test"
   - Monitor progress in real-time

### Using Python API

```python
from src.core.protocol_engine import ProtocolEngine
from src.models.database import init_db

# Initialize
init_db()
engine = ProtocolEngine()

# Define parameters
params = {
    "test_name": "PID-TEST-001",
    "module_id": "PV-MODULE-12345",
    "test_voltage": -1000,
    "test_duration": 96,
    "temperature": 85,
    "relative_humidity": 85,
    "sampling_interval": 60,
    "leakage_current_threshold": 10,
    "operator": "Test Engineer"
}

# Create test execution
test = engine.create_test_execution("pid-001", params)
print(f"Test ID: {test.id}")
```

## Understanding Test Results

### Result Components

1. **Test Execution Summary**:
   - Test ID and status
   - Start/end times
   - Duration
   - QC status (Pass/Warning/Fail)

2. **Measurements**:
   - Leakage current over time
   - Power degradation
   - Environmental conditions

3. **QC Checks**:
   - Average leakage current
   - Maximum leakage current
   - Power degradation
   - Environmental tolerance

4. **Compliance**:
   - IEC 62804 compliance status
   - Compliance notes

### Viewing Results

#### In Streamlit UI

1. Navigate to "📊 View Results"
2. Select a test from the dropdown
3. Review:
   - Summary metrics
   - Interactive charts
   - Measurement data table
   - QC check details

#### Via Python API

```python
from src.models.database import get_db
from src.models.protocol import TestExecution, Measurement

with get_db() as db:
    test = db.query(TestExecution).filter_by(id=test_id).first()

    print(f"Status: {test.status}")
    print(f"QC Status: {test.qc_status}")
    print(f"Measurements: {len(test.measurements)}")

    # Access summary
    summary = test.results_summary
    print(f"Average Leakage: {summary['average_leakage_current']:.2f} mA")
    print(f"Compliant: {summary['compliance']['iec_62804_compliant']}")
```

## Leakage Tracking

### Understanding Leakage Current

Leakage current is a critical indicator of potential-induced degradation in PV modules. The framework provides:

- **Real-time monitoring**: Track leakage current throughout test
- **Anomaly detection**: Automatic detection of unusual patterns
- **Threshold alerts**: Warning and critical threshold violations

### Leakage Event Types

1. **Warning Threshold**: Leakage exceeds warning level (default: 5 mA)
2. **Critical Threshold**: Leakage exceeds critical level (default: 10 mA)
3. **Rapid Increase**: Sudden jump in leakage current (>100% increase)
4. **Sustained High**: Prolonged elevated leakage

### Working with Leakage Tracker

```python
from protocols.pid_001.implementation import LeakageTracker
from datetime import datetime

# Initialize tracker
tracker = LeakageTracker(
    threshold_warning=5.0,    # mA
    threshold_critical=10.0   # mA
)

# Add measurements
for i in range(100):
    current = measure_leakage()  # Your measurement function
    event = tracker.add_measurement(
        leakage_current=current,
        timestamp=datetime.utcnow(),
        elapsed_time=i * 0.5  # hours
    )

    if event:
        print(f"Alert: {event['description']}")
        print(f"Severity: {event['severity']}")

# Get statistics
stats = tracker.get_statistics()
print(f"Average: {stats['average']:.2f} mA")
print(f"Maximum: {stats['max']:.2f} mA")
```

## QC Validation

### Built-in QC Checks

The framework performs automatic quality control checks:

#### 1. Leakage Current Checks

- **Average Leakage Current**: Mean of all measurements
- **Maximum Leakage Current**: Peak value during test
- **Thresholds**: Warning (5 mA) and Critical (10 mA)

#### 2. Power Degradation Checks

- **Final Power Degradation**: Degradation at test completion
- **Thresholds**: Warning (3%) and Critical (5%)

#### 3. Environmental Checks

- **Temperature Tolerance**: ±2°C from setpoint
- **Humidity Tolerance**: ±5% from setpoint

### Custom QC Rules

You can customize validation rules in the protocol schema:

```json
{
  "validation_rules": {
    "leakage_current_limits": {
      "warning_threshold": 5,
      "critical_threshold": 10,
      "unit": "mA"
    },
    "power_degradation_limits": {
      "warning_threshold": 3,
      "critical_threshold": 5,
      "unit": "percent"
    }
  }
}
```

### QC Status Interpretation

- **✅ Pass**: All checks passed, meets requirements
- **⚠️ Warning**: Some checks exceeded warning thresholds
- **❌ Fail**: One or more checks exceeded critical thresholds

## Advanced Features

### 1. Batch Testing

Process multiple modules in sequence:

```python
modules = ["MOD-001", "MOD-002", "MOD-003"]

for module_id in modules:
    params = {...}
    params["module_id"] = module_id
    test = engine.create_test_execution("pid-001", params)
    # Run test...
```

### 2. Custom Measurement Processing

Implement custom measurement handlers:

```python
class CustomPIDProtocol(PID001Protocol):
    def process_measurement(self, test_exec, measurement_data, tracker):
        # Add custom processing
        measurement, event = super().process_measurement(
            test_exec, measurement_data, tracker
        )

        # Custom logic
        if measurement.leakage_current > 8.0:
            send_alert(measurement)

        return measurement, event
```

### 3. Data Export

Export results for external analysis:

```python
import pandas as pd

# Load measurements
with get_db() as db:
    measurements = db.query(Measurement).filter_by(
        test_execution_id=test_id
    ).all()

# Convert to DataFrame
df = pd.DataFrame([
    {
        "time": m.elapsed_time,
        "leakage": m.leakage_current,
        "degradation": m.power_degradation
    }
    for m in measurements
])

# Export
df.to_csv("test_results.csv", index=False)
df.to_excel("test_results.xlsx", index=False)
```

### 4. Integration with LIMS

Configure LIMS integration:

```python
# In .env file
LIMS_API_URL=https://lims.example.com/api
LIMS_API_KEY=your-api-key

# In code
from src.integrations.lims_integration import LIMSClient

client = LIMSClient()
client.upload_test_results(test_id)
```

## Best Practices

1. **Naming Conventions**:
   - Use descriptive test names: `PID-{DATE}-{MODULE}-{SEQUENCE}`
   - Include operator information
   - Add detailed notes

2. **Parameter Selection**:
   - Follow IEC 62804 guidelines
   - Use standard conditions (85°C, 85% RH)
   - Choose appropriate test duration (96h typical)

3. **Data Review**:
   - Monitor tests regularly
   - Review QC checks immediately
   - Investigate anomalies promptly

4. **Backup and Storage**:
   - Regularly backup database
   - Export critical results
   - Archive completed tests

## Troubleshooting

### Common Issues

**Issue**: Test fails to start
- Check database connection
- Verify parameters are valid
- Review logs for errors

**Issue**: No measurements recorded
- Check sampling interval
- Verify measurement source
- Review database write permissions

**Issue**: QC checks always fail
- Adjust threshold values
- Review measurement quality
- Check environmental conditions

## Next Steps

- Explore additional protocols
- Customize validation rules
- Integrate with your systems
- Develop custom analysis tools

For more information, see:
- [API Documentation](API.md)
- [Protocol Development Guide](PROTOCOL_DEVELOPMENT.md)
- [Architecture Overview](ARCHITECTURE.md)
