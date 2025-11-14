# Getting Started with PV Testing Protocol Framework

## Introduction

Welcome to the PV Testing Protocol Framework! This guide will help you get started with installing, configuring, and using the framework for your photovoltaic testing needs.

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher (for database functionality)
- pip (Python package installer)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/test-protocols.git
cd test-protocols
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Database Setup (Optional)

If you want to use database persistence:

```bash
# Create database
createdb pv_testing

# Run migrations
psql -d pv_testing -f database/schema.sql
```

### Step 4: Verify Installation

```bash
python -c "from src.core.protocol_loader import ProtocolLoader; print('Installation successful!')"
```

## Quick Start

### Running Your First Test

#### 1. Using Python API

```python
from src.protocols.jbox001 import JBOX001Protocol

# Initialize protocol
protocol = JBOX001Protocol()

# Create a test run
test_run = protocol.create_test_run(
    sample_id="MODULE-001",
    operator="Your Name"
)

# Start the test
protocol.runner.start_test_run(test_run.test_run_id)

# Run initial characterization
protocol.run_initial_characterization(
    test_run=test_run,
    visual_inspection={'defects_count': 0, 'notes': 'No defects'},
    contact_resistance=5.2,
    diode_voltage=[0.65, 0.64, 0.66],
    insulation_resistance=100.0,
    iv_curve_data={'pmax': 300.0, 'voc': 40.5, 'isc': 9.2}
)

# Save results
filepath = test_run.save()
print(f"Test data saved to: {filepath}")
```

#### 2. Using the UI

```bash
# Start the Streamlit UI
cd src/ui
streamlit run app.py
```

Then navigate to `http://localhost:8501` in your web browser.

For JBOX-001 specific testing:

```bash
streamlit run pages/jbox001_test.py
```

## Core Concepts

### Protocols

Protocols are JSON-based templates that define:
- Test phases and steps
- Required measurements
- QC acceptance criteria
- Analysis configuration

All protocols are stored in `protocols/templates/`.

### Test Runs

A test run represents a single execution of a protocol on a specific sample. It tracks:
- Test progress (phases and steps)
- Measurement data
- Notes and observations
- QC results

### Measurements

Measurements are data points collected during testing. Each measurement has:
- Measurement ID (e.g., M1, M2)
- Value and unit
- Timestamp
- Associated phase/step
- Metadata

### QC Criteria

Quality control criteria define pass/fail conditions for tests. The framework automatically evaluates criteria and generates results.

## Working with JBOX-001

### Protocol Overview

JBOX-001 tests junction box degradation through six phases:

1. **Initial Characterization** - Baseline measurements
2. **Thermal Cycling** - 200 cycles (-40°C to +85°C)
3. **Humidity-Freeze** - 10 cycles (85%RH/85°C to -40°C)
4. **UV Exposure** - 15 kWh/m² UV dose
5. **Electrical Load Stress** - 168 hours at 1.25×Isc
6. **Final Characterization** - Post-stress measurements

### Example Workflow

```python
from src.protocols.jbox001 import JBOX001Protocol

protocol = JBOX001Protocol()
test_run = protocol.create_test_run(
    sample_id="JBOX-MODULE-001",
    operator="Jane Smith"
)

protocol.runner.start_test_run(test_run.test_run_id)

# Phase 1: Initial Characterization
protocol.run_initial_characterization(
    test_run=test_run,
    visual_inspection={
        'defects_count': 0,
        'notes': 'Module in pristine condition'
    },
    contact_resistance=4.8,
    diode_voltage=[0.65, 0.64, 0.66],
    insulation_resistance=120.0,
    iv_curve_data={
        'pmax': 305.0,
        'voc': 41.2,
        'isc': 9.5
    }
)

# Phase 2: Thermal Cycling
# (Update progress as cycles complete)
protocol.run_thermal_cycling(
    test_run=test_run,
    cycles_completed=50,
    interim_measurements=[
        {
            'cycle': 50,
            'contact_resistance': 4.9,
            'diode_voltage': 0.65
        }
    ]
)

# Continue until 200 cycles...
protocol.run_thermal_cycling(
    test_run=test_run,
    cycles_completed=200
)

# Phase 3: Humidity-Freeze
protocol.run_humidity_freeze(
    test_run=test_run,
    cycles_completed=10,
    weight_gain_percentage=0.3
)

# Phase 4: UV Exposure
protocol.run_uv_exposure(
    test_run=test_run,
    uv_dose=15.0,
    degradation_assessment={
        'discoloration': False,
        'cracking': False,
        'embrittlement': False,
        'defects_count': 0
    }
)

# Phase 5: Electrical Load Stress
from datetime import datetime, timedelta

base_time = datetime.now()
temperature_data = [
    {'timestamp': base_time + timedelta(hours=i), 'temperature': 50 + i*0.1}
    for i in range(168)
]
resistance_data = [
    {'timestamp': base_time + timedelta(hours=i), 'resistance': 4.8 + i*0.001}
    for i in range(168)
]

protocol.run_electrical_load_stress(
    test_run=test_run,
    temperature_data=temperature_data,
    resistance_data=resistance_data
)

# Phase 6: Final Characterization
protocol.run_final_characterization(
    test_run=test_run,
    visual_inspection={
        'defects_count': 0,
        'notes': 'Slight discoloration on housing'
    },
    contact_resistance=5.1,
    diode_voltage=[0.66, 0.65, 0.67],
    insulation_resistance=115.0,
    iv_curve_data={
        'pmax': 293.0,  # ~4% degradation
        'voc': 41.0,
        'isc': 9.4
    }
)

# Complete test
protocol.runner.complete_test_run(test_run.test_run_id)

# Generate report
report = protocol.generate_test_report(test_run)

print(f"Test Status: {report['test_run']['status']}")
print(f"QC Result: {'PASS' if test_run.qc_results['overall_pass'] else 'FAIL'}")
print(f"Power Degradation: {report['test_data']['qc_results'].get('power_degradation_percentage', 'N/A')}%")

# Save test data
filepath = test_run.save()
print(f"Test data saved to: {filepath}")
```

## Understanding Test Results

### QC Pass/Fail Criteria

JBOX-001 has 7 acceptance criteria:

| Criterion | Description | Severity | Threshold |
|-----------|-------------|----------|-----------|
| AC1 | Power degradation | Critical | ≤ 5% |
| AC2 | Resistance increase | Major | ≤ 20% |
| AC3 | Insulation resistance | Critical | ≥ 40 MΩ |
| AC4 | Visual damage | Critical | 0 defects |
| AC5 | Diode voltage drift | Major | ≤ 10% |
| AC6 | Moisture ingress | Major | < 1% |
| AC7 | Temperature rise | Critical | ≤ 40K |

A test **PASSES** only if all criteria are met.
A test **FAILS** if any criterion is not met.

### Interpreting Results

```python
# Check QC results
qc_results = test_run.qc_results

if qc_results['overall_pass']:
    print("✅ TEST PASSED")
else:
    print("❌ TEST FAILED")

    if qc_results['critical_failures']:
        print(f"\nCritical Failures ({len(qc_results['critical_failures'])}):")
        for failure in qc_results['critical_failures']:
            print(f"  - {failure['description']}")
            print(f"    Expected: {failure['condition']}")
            print(f"    Actual: {failure['actual_value']}")

    if qc_results['major_failures']:
        print(f"\nMajor Failures ({len(qc_results['major_failures'])}):")
        for failure in qc_results['major_failures']:
            print(f"  - {failure['description']}")
```

## Data Management

### Saving Test Data

Test data is automatically saved in JSON format:

```python
# Save manually
filepath = test_run.save(output_dir="my_test_results")

# Data is saved as: {test_run_id}_{sample_id}.json
```

### Loading Test Data

```python
import json

with open('test_runs/TEST-001_MODULE-001.json', 'r') as f:
    test_data = json.load(f)

print(f"Test Run: {test_data['test_run_id']}")
print(f"Status: {test_data['status']}")
print(f"Measurements: {len(test_data['measurements'])}")
```

### Database Storage

For database persistence, configure your database connection in `config/database.yaml`:

```yaml
database:
  host: localhost
  port: 5432
  database: pv_testing
  user: your_user
  password: your_password
```

## Troubleshooting

### Common Issues

#### "Protocol file not found"
**Solution:** Ensure protocol templates are in `protocols/templates/` directory.

#### "Module not found" errors
**Solution:** Add the `src` directory to your Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
```

#### Tests fail to run
**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Next Steps

- Read the [JBOX-001 Protocol Documentation](../protocols/JBOX-001.md)
- Explore the [API Documentation](../api/README.md)
- Learn about [Creating Custom Protocols](custom_protocols.md)
- See [Advanced Usage Examples](advanced_usage.md)

## Getting Help

- **Issues:** Report bugs on GitHub Issues
- **Documentation:** Check the `docs/` directory
- **Community:** Join our discussion forum

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.
