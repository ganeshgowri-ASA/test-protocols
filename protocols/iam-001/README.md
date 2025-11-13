# IAM-001 Protocol - Incidence Angle Modifier

## Overview

The IAM-001 protocol implements testing for the Incidence Angle Modifier (IAM) of photovoltaic modules according to IEC 61853 standards.

## Purpose

The IAM characterizes how a PV module's electrical performance varies with the angle of incidence (AOI) of sunlight. This is critical for:

- Accurate energy yield predictions
- Performance modeling under real-world conditions
- Module comparison and selection
- Quality assurance

## Test Specifications

### Angle Range

- **Minimum**: 0° (normal incidence)
- **Maximum**: 90° (grazing incidence)
- **Recommended angles**: 0°, 10°, 20°, 30°, 40°, 50°, 60°, 70°, 80°, 90°
- **Minimum data points**: 5

### Test Conditions

- **Irradiance**: 1000 W/m² (±50 W/m² tolerance)
- **Temperature**: 25°C (±5°C tolerance)
- **Spectrum**: AM1.5G (standard)
- **Stability requirement**: CV < 2%

### Required Measurements

For each angle, measure:

1. **Isc** - Short-circuit current (A)
2. **Voc** - Open-circuit voltage (V)
3. **Pmax** - Maximum power (W)
4. **Imp** - Current at maximum power point (A)
5. **Vmp** - Voltage at maximum power point (V)
6. **FF** - Fill factor

Optional:
- Full I-V curve
- Actual irradiance
- Actual temperature

## Protocol Files

### schema.json

Defines the JSON schema for protocol validation. All protocol instances must conform to this schema.

Key sections:
- `protocol_info`: Test metadata
- `sample_info`: Module specifications
- `test_configuration`: Test parameters
- `measurements`: Array of angle measurements
- `analysis_results`: Calculated IAM curve and fitting
- `metadata`: Equipment and environmental data

### template.json

Template for creating new protocol instances. Contains default values and structure.

### config.json

Configuration parameters for:
- Default test settings
- Validation rules
- Analysis settings
- QC check thresholds
- Output formatting

## Analysis Models

### ASHRAE Model (default)

Single-parameter model:
```
IAM(θ) = 1 - b₀ * (1/cos(θ) - 1)
```

**Parameters**: b₀ (typically 0.02-0.08)

**Characteristics**:
- Simple and widely used
- Good for most flat-plate modules
- Fast computation

### Physical Model

Based on Fresnel reflections:
```
IAM(θ) = (1 - exp(-cos(θ)/aᵣ)) / (1 - exp(-1/aᵣ))
```

**Parameters**: aᵣ (angular losses coefficient)

**Characteristics**:
- Physically-based
- Accounts for reflection losses
- Better for modules with AR coatings

### Polynomial Model

4th-order polynomial:
```
IAM(θ) = 1 + a₁(θ/90) + a₂(θ/90)² + a₃(θ/90)³ + a₄(θ/90)⁴
```

**Parameters**: a₁, a₂, a₃, a₄

**Characteristics**:
- Most flexible
- Can capture complex behaviors
- May overfit with sparse data

## Quality Metrics

### Fit Quality

Based on R² value:
- **Excellent**: R² ≥ 0.99
- **Good**: R² ≥ 0.95
- **Acceptable**: R² ≥ 0.90
- **Poor**: R² < 0.90

### Data Completeness

Percentage of recommended angles measured.

### Measurement Stability

- Irradiance CV < 2%
- Temperature variation < 5°C
- No significant measurement drift

## Validation Checks

The protocol performs automatic validation:

1. **Schema validation**: JSON structure and types
2. **Measurement validation**:
   - Sufficient data points (≥5)
   - Valid angle range (0-90°)
   - No negative values
   - No duplicate angles
3. **Stability validation**:
   - Irradiance within tolerance
   - Temperature within tolerance
4. **Physical validation**:
   - IAM decreases with angle
   - Reasonable values at high angles

## Usage Example

```python
from protocol_engine import ProtocolExecutor
from analysis import create_analyzer

# Initialize
executor = ProtocolExecutor("iam-001")

# Create protocol
executor.create_protocol(
    **{
        "sample_info.sample_id": "PV-MODULE-001",
        "sample_info.module_type": "400W Monocrystalline",
        "sample_info.technology": "mono-Si"
    }
)

# Add measurements (0-90° in 10° steps)
test_data = [
    (0, 10.0, 48.0, 400.0),
    (10, 9.8, 47.9, 392.0),
    (20, 9.4, 47.7, 375.0),
    (30, 8.7, 47.4, 345.0),
    (40, 7.7, 47.0, 303.0),
    (50, 6.4, 46.5, 250.0),
    (60, 5.0, 45.8, 192.0),
    (70, 3.4, 44.9, 128.0),
    (80, 1.7, 43.7, 63.0),
    (90, 0.2, 42.0, 7.0),
]

for angle, isc, voc, pmax in test_data:
    executor.add_measurement(
        angle=angle,
        isc=isc,
        voc=voc,
        pmax=pmax,
        irradiance_actual=1000.0,
        temperature_actual=25.0
    )

# Validate
results = executor.validate_protocol()
print(f"Status: {results['overall_status']}")

# Analyze
executor.execute_analysis(create_analyzer)
analysis = executor.get_analysis_results()

print(f"Best model: {analysis['fitting_parameters']['model']}")
print(f"R²: {analysis['fitting_parameters']['r_squared']:.4f}")
print(f"Fit quality: {analysis['quality_metrics']['fit_quality']}")

# Save
executor.save_protocol("iam-001-results.json")
```

## Expected Results

Typical IAM curve characteristics:

- **IAM(0°)** = 1.0 (by definition)
- **IAM(30°)** ≈ 0.96-0.99
- **IAM(50°)** ≈ 0.92-0.96
- **IAM(60°)** ≈ 0.88-0.94
- **IAM(70°)** ≈ 0.80-0.90
- **IAM(80°)** ≈ 0.60-0.80
- **IAM(90°)** ≈ 0.0-0.3

## Troubleshooting

### Low fit quality (R² < 0.90)

- Check for measurement errors
- Ensure stable test conditions
- Verify angle positioning accuracy
- Try different fitting model

### High irradiance variation

- Allow simulator to stabilize
- Check for shadowing or reflections
- Verify pyranometer calibration

### Non-monotonic IAM curve

- Check measurement sequence
- Verify angle positioning
- Look for temperature effects
- Review test conditions stability

## References

- IEC 61853-2: Performance testing at different irradiance and temperature
- ASHRAE Standard 93: Methods of Testing to Determine the Thermal Performance of Solar Collectors
- King et al. (2004): Photovoltaic Array Performance Model (Sandia Report)

## Version History

- **1.0.0** (2025-11-13): Initial release
  - Complete 0-90° angle range
  - Three fitting models (ASHRAE, Physical, Polynomial)
  - Comprehensive validation and QC
  - Streamlit UI integration

---

Protocol ID: **IAM-001**
Version: **1.0.0**
Standard: **IEC 61853**
Updated: **2025-11-13**
