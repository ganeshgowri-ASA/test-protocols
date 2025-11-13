# Example I-V Curve Data Files

This directory contains sample I-V curve data files for testing the STC-001 protocol implementation.

## Files

### 1. sample_iv_curve_mono_400w.csv
- **Module Type:** Monocrystalline Silicon (Mono c-Si)
- **Rated Power:** 400W
- **Technology:** Standard Mono c-Si
- **Data Points:** 200
- **Format:** CSV with headers "Voltage (V)" and "Current (A)"

**Typical Parameters:**
- Voc: ~48.2V
- Isc: ~10.45A
- Vmp: ~40.2V
- Imp: ~9.95A
- Pmax: ~400W
- Fill Factor: ~0.79

### 2. sample_iv_curve_perc_450w.csv
- **Module Type:** PERC (Passivated Emitter and Rear Cell)
- **Rated Power:** 450W
- **Technology:** PERC
- **Data Points:** 200
- **Format:** CSV with headers "Voltage" and "Current"

**Typical Parameters:**
- Voc: ~50.0V
- Isc: ~11.52A
- Vmp: ~41.5V
- Imp: ~10.8A
- Pmax: ~450W
- Fill Factor: ~0.78

## Usage

### Python
```python
from genspark_app.protocols.performance.stc_001 import STC001Protocol

# Create protocol instance
protocol = STC001Protocol()

# Load I-V data
iv_data = protocol._load_iv_data_from_file(
    'examples/data/sample_iv_curve_mono_400w.csv',
    voltage_col='Voltage (V)',
    current_col='Current (A)'
)

# Execute test
test_params = {
    'data_source': 'file',
    'file_path': 'examples/data/sample_iv_curve_mono_400w.csv'
}
result = protocol.execute_test(test_params)
```

### API
```bash
# Upload data file via API
curl -X POST http://localhost:5000/api/v1/protocols/stc-001/tests/TEST-001/upload-data \
  -F "file=@examples/data/sample_iv_curve_mono_400w.csv"
```

## Data Format Requirements

I-V curve data files must meet the following requirements:

1. **File Format:** CSV, TXT, XLSX, or XLS
2. **Minimum Points:** 100 data points
3. **Required Columns:** Voltage and Current
4. **Column Headers:** Must contain identifiable headers (voltage/v/volt and current/i/amp)
5. **Data Quality:**
   - No missing values (NaN)
   - Monotonically increasing voltage values
   - No negative voltages (except small noise)
   - Current decreases as voltage increases

## Generating Custom Test Data

You can generate custom I-V curves using the following Python script:

```python
import numpy as np
import pandas as pd

def generate_iv_curve(voc=48, isc=10, rs=0.3, rsh=500, points=200):
    """Generate realistic I-V curve data."""
    voltage = np.linspace(0, voc, points)
    current = []

    for v in voltage:
        # Simplified single diode model
        i = isc * (1 - (v / voc) ** 2) - v / rsh - (v * rs) / (voc * isc)
        i = max(0, i)  # No negative current
        current.append(i)

    df = pd.DataFrame({
        'Voltage (V)': voltage,
        'Current (A)': current
    })

    df.to_csv('custom_iv_curve.csv', index=False)
    return df

# Generate data
generate_iv_curve(voc=48.5, isc=10.8, rs=0.25, rsh=600)
```

## Notes

- These files contain simulated data for testing purposes
- Real I-V curve data will come from solar simulators and I-V tracers
- Data includes realistic non-idealities (series/shunt resistance)
- Suitable for validation, testing, and demonstration purposes
