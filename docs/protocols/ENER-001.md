# ENER-001: Energy Rating Test Protocol

## Overview

The Energy Rating Test Protocol (ENER-001) implements comprehensive energy rating measurements for photovoltaic modules according to IEC 61853 standards. This protocol determines the energy output characteristics of PV modules under various operating conditions to provide a comprehensive energy rating.

**Version**: 1.0.0
**Category**: Performance
**Standards**: IEC 61853-1, IEC 61853-2, IEC 61853-3, IEC 61215

## Purpose

The energy rating test provides a more realistic assessment of PV module performance compared to standard test conditions (STC) by measuring performance across a matrix of irradiance and temperature conditions that modules experience in real-world operation.

## Test Methodology

### Test Conditions Matrix

The protocol requires measurements at the following conditions:

**Irradiance Levels** (W/m²):
- 100
- 200
- 400
- 600
- 800
- 1000
- 1100 (optional)

**Module Temperatures** (°C):
- 15
- 25
- 50
- 75

**Total Test Points**: 28 conditions (7 irradiance × 4 temperatures)

### Environmental Conditions

- **Spectrum**: AM1.5G (Standard terrestrial solar spectrum)
- **Air Mass**: 1.5
- **Wind Speed**: < 1.0 m/s (for indoor testing)

### Stabilization Requirements

Before each measurement, the following stability criteria must be met:

| Parameter | Stability Threshold | Duration |
|-----------|-------------------|----------|
| Voltage | < 0.5% variation | 60 seconds |
| Current | < 0.5% variation | 60 seconds |
| Module Temperature | < 1.0°C variation | 120 seconds |

## Required Measurements

### Input Parameters

For each test condition, measure:

| Parameter | Unit | Description | Uncertainty |
|-----------|------|-------------|------------|
| Irradiance | W/m² | Incident irradiance on module plane | ±2% |
| Module Temperature | °C | Average module temperature (4 points minimum) | ±1°C |
| Ambient Temperature | °C | Ambient air temperature | ±1°C |
| Voltage | V | Module terminal voltage | ±0.5% |
| Current | A | Module output current | ±0.5% |

### Module Specifications

Required module specifications:

- **Module Area** (m²): Total module area
- **Rated Power (STC)** (W): Module rated power at standard test conditions

## Output Parameters

The protocol calculates the following performance parameters:

### Per Test Condition

- **Maximum Power Point (Pmpp)**: Maximum power output
- **Open Circuit Voltage (Voc)**: Voltage at zero current
- **Short Circuit Current (Isc)**: Current at zero voltage
- **Voltage at MPP (Vmpp)**: Voltage at maximum power point
- **Current at MPP (Impp)**: Current at maximum power point
- **Fill Factor (FF)**: Ratio of Pmpp to (Voc × Isc)
- **Efficiency (η)**: Conversion efficiency

### Overall Analysis

1. **Temperature Coefficients**
   - α (Isc): Temperature coefficient of short circuit current (%/°C)
   - β (Voc): Temperature coefficient of open circuit voltage (%/°C)
   - γ (Pmax): Temperature coefficient of maximum power (%/°C)

2. **Energy Rating** (kWh/kWp)
   - Calculated for specified climate zones (hot, moderate, cold)
   - Based on IEC 61853-3 methodology
   - Normalized to rated power

3. **Performance Ratio** (%)
   - Ratio of actual to theoretical energy output

## Quality Control Checks

The protocol includes automatic quality checks:

### Mandatory Checks (Errors)

| QC ID | Check | Threshold | Description |
|-------|-------|-----------|-------------|
| qc_001 | Irradiance Stability | < 2% variation | Irradiance must be stable during measurement |
| qc_002 | Temperature Range | 10-80°C | Module temperature must be within safe limits |
| qc_006 | Efficiency Range | 5-25% | Efficiency must be physically reasonable |
| qc_007 | Data Completeness | 100% | All test points must be measured |

### Warnings

| QC ID | Check | Threshold | Description |
|-------|-------|-----------|-------------|
| qc_003 | Temperature Stability | < 1°C variation | Module temperature should be stable |
| qc_004 | IV Curve Smoothness | Monotonic decrease | Current should decrease with voltage |
| qc_005 | Fill Factor Range | 60-85% | Fill factor should be typical for Si modules |
| qc_008 | Measurement Uncertainty | < 5% | Combined uncertainty should be acceptable |

## Charts and Visualizations

The protocol generates the following charts:

1. **I-V Characteristics**: Current-voltage curves at all test conditions
2. **P-V Characteristics**: Power-voltage curves with MPP markers
3. **Power vs Irradiance**: MPP power as function of irradiance at different temperatures
4. **Power vs Temperature**: MPP power as function of temperature at different irradiances
5. **Efficiency Map**: Heatmap of efficiency across irradiance-temperature matrix
6. **Energy Rating Contribution**: Bar chart showing energy contribution by operating condition

## Usage Example

### Python API

```python
from test_protocols.protocols.ener_001 import ENER001Protocol
from test_protocols.core.test_runner import TestRunner
import pandas as pd

# Load test data (CSV with columns: irradiance, module_temp, voltage, current)
data = pd.read_csv("energy_rating_test_data.csv")

# Add module specifications
data["module_area"] = 1.65  # m²
data["rated_power"] = 300   # W

# Initialize protocol
protocol = ENER001Protocol()

# Validate inputs
is_valid, errors = protocol.validate_inputs(data)
if not is_valid:
    print(f"Validation errors: {errors}")
    exit(1)

# Create test runner
runner = TestRunner(protocol)

# Execute test
results = runner.run(data, validate_inputs=True, run_qc=True)

# Access results
print(f"Test Status: {results['status']}")
print(f"Session ID: {results['session_id']}")

# Analysis results
analysis = results['analysis']
print(f"\nEnergy Rating: {analysis['energy_rating']['energy_rating_kWh_per_kWp']:.0f} kWh/kWp")

# Temperature coefficients
tc = analysis['temperature_coefficients']
print(f"\nTemperature Coefficients:")
print(f"  α (Isc): {tc['alpha_isc']:.3f} %/°C")
print(f"  β (Voc): {tc['beta_voc']:.3f} %/°C")
print(f"  γ (Pmax): {tc['gamma_pmax']:.3f} %/°C")

# STC Performance
stc = analysis['stc_performance']
print(f"\nPerformance at STC:")
print(f"  Pmax: {stc['pmpp']:.2f} W")
print(f"  Voc: {stc['voc']:.2f} V")
print(f"  Isc: {stc['isc']:.2f} A")
print(f"  FF: {stc['fill_factor']:.1f}%")

# Quality checks
qc_results = results['qc_results']
passed = sum(1 for qc in qc_results if qc['passed'])
print(f"\nQuality Checks: {passed}/{len(qc_results)} passed")

# Export results
protocol.export_results("ener001_results.json", format="json")

# Generate charts (saved as HTML)
for chart_name, fig in results['charts'].items():
    fig.write_html(f"chart_{chart_name}.html")
```

### UI Workflow

1. **Navigate to Protocol Selection**
   - Select ENER-001 from available protocols
   - Review test conditions and requirements

2. **Prepare Test Data**
   - Format data as CSV with required columns
   - Ensure all test conditions are measured

3. **Execute Test**
   - Go to Test Execution page
   - Enter test metadata (operator, device ID, etc.)
   - Upload test data CSV or use sample data
   - Select climate zone for energy rating
   - Click "Run Test"

4. **Review Results**
   - View test summary and status
   - Check performance analysis
   - Review quality control results
   - Examine interactive charts

5. **Export Results**
   - Download results as JSON
   - Download measurements as CSV
   - Generate PDF report (coming soon)

## Data Format

### Input CSV Format

```csv
irradiance,module_temp,ambient_temp,voltage,current
1000,25,20,45.2,0.0
1000,25,20,44.8,1.2
1000,25,20,44.0,2.5
...
1000,25,20,0.5,10.8
1000,25,20,0.0,10.9
1000,50,45,44.0,0.0
1000,50,45,43.5,1.3
...
```

**Requirements**:
- Minimum 10 voltage points per IV curve
- All irradiance-temperature combinations must be tested
- Voltage range: 0 to Voc
- Current range: 0 to Isc

### Output JSON Structure

```json
{
  "session_id": "ENER-001_20250114_143022",
  "status": "completed",
  "protocol_id": "ENER-001",
  "protocol_version": "1.0.0",
  "duration_seconds": 12.5,

  "iv_curves": {
    "G1000_T25": {
      "irradiance": 1000,
      "temperature": 25,
      "pmpp": 300.5,
      "voc": 45.2,
      "isc": 10.8,
      "fill_factor": 77.5,
      "efficiency": 18.2
    },
    ...
  },

  "analysis": {
    "energy_rating": {
      "energy_rating_kWh_per_kWp": 1520,
      "climate_zone": "moderate",
      "performance_ratio": 89.4
    },
    "temperature_coefficients": {
      "alpha_isc": 0.045,
      "beta_voc": -0.320,
      "gamma_pmax": -0.425
    },
    "stc_performance": {
      "pmpp": 300.5,
      "voc": 45.2,
      "isc": 10.8,
      "fill_factor": 77.5,
      "efficiency": 18.2
    }
  },

  "qc_results": [...]
}
```

## Calculation Methods

### Fill Factor

```
FF = (Vmpp × Impp) / (Voc × Isc) × 100%
```

### Efficiency

```
η = Pmpp / (G × A) × 100%
```

Where:
- G = irradiance (W/m²)
- A = module area (m²)

### Temperature Coefficients

Temperature coefficients are calculated using linear regression on normalized parameters versus temperature:

```
γ = ΔPmpp/Pmpp(25°C) / ΔT × 100%  (%/°C)
β = ΔVoc/Voc(25°C) / ΔT × 100%    (%/°C)
α = ΔIsc/Isc(25°C) / ΔT × 100%    (%/°C)
```

### Energy Rating

Energy rating is calculated according to IEC 61853-3 using weighted contributions from different operating conditions:

```
ER = Σ(Pi/Prated × Wi) × Annual_Irradiation
```

Where:
- Pi = power at operating condition i
- Prated = rated power at STC
- Wi = climate-specific weight for condition i
- Weights sum to 1.0

## Equipment Requirements

### Minimum Requirements

1. **Solar Simulator**: Class AAA (IEC 60904-9)
   - Spectral match: Class A (0.75-1.25 × reference)
   - Non-uniformity: Class A (< 2%)
   - Temporal instability: Class A (< 2%)

2. **IV Curve Tracer**
   - Voltage accuracy: ±0.5%
   - Current accuracy: ±0.5%
   - Minimum 50 points per curve

3. **Irradiance Sensor**
   - Calibrated reference cell or pyranometer
   - Accuracy: ±2%

4. **Temperature Sensors**
   - Type: K-type thermocouples or PT100
   - Minimum 4 measurement points on module
   - Accuracy: ±1°C

5. **Temperature Control**
   - Environmental chamber or temperature-controlled fixture
   - Range: 10-80°C
   - Stability: ±1°C

## Typical Values

For crystalline silicon modules:

| Parameter | Typical Range |
|-----------|--------------|
| Fill Factor | 75-82% |
| Efficiency (STC) | 15-22% |
| α (Isc) | +0.03 to +0.06 %/°C |
| β (Voc) | -0.25 to -0.35 %/°C |
| γ (Pmax) | -0.35 to -0.50 %/°C |
| Energy Rating (moderate climate) | 1400-1700 kWh/kWp |

## Troubleshooting

### Common Issues

**Issue**: QC check "Irradiance Stability" fails
**Solution**: Allow more stabilization time, check simulator warm-up

**Issue**: QC check "IV Curve Smoothness" fails
**Solution**: Check connections, reduce sweep rate, improve shielding

**Issue**: Energy rating unreasonably low
**Solution**: Verify module specifications, check temperature sensor placement

**Issue**: Temperature coefficients out of range
**Solution**: Ensure adequate temperature range tested, check temperature sensor accuracy

## References

1. **IEC 61853-1:2011**: Photovoltaic (PV) module performance testing and energy rating - Part 1: Irradiance and temperature performance measurements and power rating

2. **IEC 61853-2:2016**: Photovoltaic (PV) module performance testing and energy rating - Part 2: Spectral responsivity, incidence angle and module operating temperature measurements

3. **IEC 61853-3:2018**: Photovoltaic (PV) module performance testing and energy rating - Part 3: Energy rating of PV modules

4. **IEC 61215**: Terrestrial photovoltaic (PV) modules - Design qualification and type approval

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-14 | Initial release |
