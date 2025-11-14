# Quick Start Guide

## Installation & Setup

### 1. System Requirements

- **Python**: 3.10 or higher
- **OS**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM
- **Storage**: 500MB free space

### 2. Install Dependencies

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. Configure System

```bash
# (Optional) Edit configuration
nano config/config.yaml

# Initialize database
python -c "from database.session import init_database; init_database()"
```

### 4. Launch Application

```bash
# Start Streamlit UI
streamlit run ui/streamlit_app.py

# Or run directly
python -m streamlit run ui/streamlit_app.py
```

Access the application at: http://localhost:8501

## Running Your First Test (WET-001)

### Step 1: Navigate to "Run Test"

Click **"Run Test"** in the sidebar navigation.

### Step 2: Enter Sample Information

```
Sample ID: PV-2025-001
Module Type: Monocrystalline 400W
Manufacturer: Solar Corp
Serial Number: SN123456
Rated Power: 400 W
```

### Step 3: Configure Test Conditions

```
Test Voltage: 1500 V
Electrode Configuration: A
Test Duration: 168 hours
Measurement Interval: 60 minutes
Temperature: 25°C
Relative Humidity: 90%
```

### Step 4: Set Acceptance Criteria

Use defaults or customize:
```
Max Leakage Current: 0.25 mA
Min Insulation Resistance: 400 MΩ
Max Voltage Variation: 5%
```

### Step 5: Start Test

Click **"✅ Start Test"** button.

### Step 6: Add Measurements

```python
# Manual entry via UI
# Or programmatically:

from protocols.wet_leakage_current import WETLeakageCurrentProtocol

protocol = WETLeakageCurrentProtocol()

# Add measurement
protocol.add_measurement(
    leakage_current=0.15,  # mA
    voltage=1500.0,        # V
    temperature=25.0,      # °C
    humidity=90.0          # %
)
```

### Step 7: Analyze Results

Navigate to **"View Results"** page:
- Click **"🔬 Analyze Results"**
- Review pass/fail status
- View charts and statistics

### Step 8: Generate Report

Click **"📄 Generate Report"** to create HTML report with:
- Test summary
- Measurement data
- Charts and graphs
- Pass/fail determination

## Programmatic Usage

### Example: Complete Test Workflow

```python
from datetime import datetime
from protocols.wet_leakage_current import WETLeakageCurrentProtocol

# Initialize protocol
protocol = WETLeakageCurrentProtocol()

# Define parameters
params = {
    "sample_information": {
        "sample_id": "PV-2025-001",
        "module_type": "Monocrystalline 400W",
        "manufacturer": "Solar Corp",
    },
    "test_conditions": {
        "test_voltage": 1500.0,
        "electrode_configuration": "A",
        "test_duration": 168.0,
        "measurement_interval": 60.0,
    },
    "environmental_conditions": {
        "temperature": 25.0,
        "relative_humidity": 90.0,
        "barometric_pressure": 101.3,
    },
    "acceptance_criteria": {
        "max_leakage_current": 0.25,
        "min_insulation_resistance": 400.0,
    }
}

# Validate parameters
protocol.validate_parameters(params)

# Simulate test with measurements
for hour in range(168):  # 1 week
    protocol.add_measurement(
        leakage_current=0.15 + (hour * 0.0001),
        voltage=1500.0,
        temperature=25.0,
        humidity=90.0
    )

# Analyze
protocol.parameters = params
from protocols.wet_leakage_current.analysis import WETAnalyzer
protocol.analyzer = WETAnalyzer(params['acceptance_criteria'])

results = protocol.analyze_results()

# Generate report
test_result = protocol._create_test_result("PV-2025-001", "John Doe")
report_path = protocol.generate_report(test_result, format='html')

print(f"Test {'PASSED' if results['passed'] else 'FAILED'}")
print(f"Report: {report_path}")
```

### Example: Database Integration

```python
from database.session import get_session
from database.models import TestRun, SampleInformation

# Get database session
session = get_session()

# Create sample
sample = SampleInformation(
    sample_id="PV-2025-001",
    module_type="Monocrystalline 400W",
    manufacturer="Solar Corp"
)
session.add(sample)

# Create test run
test_run = TestRun(
    protocol_id="WET-001",
    sample_id=sample.id,
    test_parameters=params,
    operator="John Doe"
)
session.add(test_run)
session.commit()

print(f"Test run created: {test_run.id}")
```

## Common Tasks

### View Test History

```python
from database.session import get_session
from database.models import TestRun

session = get_session()
runs = session.query(TestRun).filter_by(protocol_id="WET-001").all()

for run in runs:
    print(f"{run.sample_id}: {run.status}")
```

### Export Measurement Data

```python
# Export to JSON
protocol.export_measurements("data.json", format="json")

# Export to CSV
protocol.export_measurements("data.csv", format="csv")
```

### Custom Analysis

```python
from protocols.wet_leakage_current.analysis import WETAnalyzer

analyzer = WETAnalyzer({
    'max_leakage_current': 0.25,
    'min_insulation_resistance': 400.0
})

# Detect anomalies
anomalies = analyzer.detect_anomalies(measurements, threshold_std=3.0)

# Calculate trending
trending = analyzer.calculate_trending(measurements)

print(f"Trend: {trending['trend']}")
print(f"Anomalies found: {len(anomalies)}")
```

## Troubleshooting

### Issue: Database Connection Error

```bash
# Reset database
rm test_protocols.db
python -c "from database.session import init_database; init_database()"
```

### Issue: Module Import Error

```bash
# Ensure you're in the project root
pwd
# Should show: /path/to/test-protocols

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: UI Not Loading

```bash
# Check Streamlit installation
streamlit --version

# Clear cache
streamlit cache clear

# Restart with clean state
streamlit run ui/streamlit_app.py --server.headless true
```

## Next Steps

1. **Read Documentation**:
   - [WET-001 Protocol Guide](WET-001.md)
   - [Architecture Overview](ARCHITECTURE.md)

2. **Explore Examples**:
   - Check `tests/` for usage examples
   - Review sample configurations in `config/`

3. **Customize**:
   - Modify acceptance criteria
   - Add custom analysis methods
   - Create new protocols

4. **Integrate**:
   - Connect to test equipment
   - Set up LIMS integration
   - Configure automated reporting

## Getting Help

- **Documentation**: Check the `docs/` directory
- **Examples**: Review test files in `tests/`
- **Issues**: [Report bugs](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- **Discussions**: [Ask questions](https://github.com/ganeshgowri-ASA/test-protocols/discussions)

## Best Practices

1. **Always validate parameters** before starting tests
2. **Use version control** for protocol schemas
3. **Regular equipment calibration** verification
4. **Backup database** regularly
5. **Document custom modifications**
6. **Review QC checks** before finalizing reports
7. **Archive raw measurement data**

---

Happy testing! 🔬
