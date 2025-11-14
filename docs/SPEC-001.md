# SPEC-001: Spectral Response Test

## Overview

The SPEC-001 protocol implements spectral response testing according to IEC 60904-8 standard. This test measures the wavelength-dependent photocurrent response of photovoltaic devices, providing critical information about device performance and quantum efficiency.

## Standard Reference

**IEC 60904-8**: Photovoltaic devices - Part 8: Measurement of spectral responsivity of a photovoltaic (PV) device

## Physical Principle

### Spectral Response

The spectral response SR(λ) is defined as the ratio of photocurrent to incident optical power at each wavelength:

```
SR(λ) = I_photo(λ) / P_incident(λ)  [A/W]
```

### External Quantum Efficiency

The external quantum efficiency (EQE) represents the fraction of incident photons that produce collected electron-hole pairs:

```
EQE(λ) = SR(λ) × (hc/qλ) × 100%
```

Where:
- h = Planck constant (6.626×10⁻³⁴ J·s)
- c = Speed of light (2.998×10⁸ m/s)
- q = Elementary charge (1.602×10⁻¹⁹ C)
- λ = Wavelength (m)

### Integrated Short-Circuit Current

The integrated short-circuit current density under a reference spectrum (e.g., AM1.5G) is calculated by:

```
Jsc = (1/A) ∫ SR(λ) × Φ(λ) dλ
```

Where:
- A = Device active area
- Φ(λ) = Reference spectrum photon flux

## Equipment Requirements

### Required Equipment

1. **Monochromator System**
   - Wavelength range: 300-1200 nm minimum
   - Wavelength accuracy: ±1 nm
   - Spectral bandwidth: ≤10 nm

2. **Broadband Light Source**
   - Type: Xenon or Quartz-Halogen
   - Power: ≥150 W
   - Stability: ±0.5%

3. **Calibrated Reference Detector**
   - NIST or equivalent traceable calibration
   - Wavelength range: 300-1200 nm
   - Uncertainty: ≤2%

4. **Device Under Test Holder**
   - Temperature control: 25±2°C
   - Alignment: perpendicular to beam

5. **Source Measure Unit**
   - Current range: pA to A
   - Voltage range: ±20V
   - Accuracy: 0.1%

### Optional Equipment

6. **Bias Light Source**
   - Spectrum: AM1.5G or equivalent
   - Adjustable intensity: 0-1000 W/m²

7. **Mechanical Chopper & Lock-in Amplifier**
   - For improved signal-to-noise ratio
   - Frequency: 1-1000 Hz

## Test Parameters

### Wavelength Configuration

| Parameter | Default | Range | Unit | Description |
|-----------|---------|-------|------|-------------|
| Start | 300 | 300-1200 | nm | Starting wavelength |
| End | 1200 | 300-1200 | nm | Ending wavelength |
| Step Size | 10 | 1-50 | nm | Wavelength increment |

**Technology-Specific Recommendations:**
- Silicon (c-Si, mc-Si): 300-1200 nm
- CdTe: 300-900 nm
- CIGS: 300-1300 nm
- Perovskite: 300-850 nm
- GaAs: 300-900 nm

### Environmental Parameters

| Parameter | Default | Range | Tolerance | Unit |
|-----------|---------|-------|-----------|------|
| Temperature | 25 | -40 to 85 | ±2 | °C |

### Measurement Parameters

| Parameter | Default | Range | Unit | Description |
|-----------|---------|-------|------|-------------|
| Integration Time | 100 | 10-10000 | ms | Signal integration time |
| Averaging | 3 | 1-100 | - | Number of averages per point |
| Bias Voltage | 0 | -10 to 10 | V | DC bias voltage (optional) |
| Bias Light | 0 | 0-1000 | W/m² | Background illumination (optional) |

## Test Procedure

### 1. Pre-Test Preparation

**Equipment Warm-Up (30 minutes minimum)**
- Turn on light source and allow to stabilize
- Initialize monochromator and home gratings
- Warm up source measure unit
- Stabilize temperature control system

**Reference Calibration**
- Mount reference detector in sample position
- Sweep wavelength range and record reference signal
- Verify reference detector calibration is current

### 2. Sample Preparation

**Mounting**
- Mount DUT in sample holder
- Ensure electrical contacts are secure
- Verify alignment perpendicular to beam (±2°)

**Temperature Stabilization**
- Set target temperature (typically 25°C)
- Allow 10 minutes for thermal equilibrium
- Monitor temperature throughout test

### 3. Measurement

**For each wavelength point:**
1. Set monochromator to wavelength λ
2. Measure reference detector current I_ref(λ)
3. Switch to DUT position
4. Apply bias conditions (if specified)
5. Measure DUT photocurrent I_sample(λ)
6. Repeat for averaging
7. Record temperature and timestamp

**Typical scan times:**
- Full range (300-1200 nm, 10 nm steps): ~15-20 minutes
- Quick scan (400-1000 nm, 50 nm steps): ~3-5 minutes

### 4. Data Analysis

**Calculate Spectral Response**
```python
SR(λ) = I_sample(λ) / [I_ref(λ) × SR_ref(λ)]
```

**Calculate EQE**
```python
EQE(λ) = SR(λ) × (h×c)/(q×λ) × 100%
```

**Integrate Jsc**
```python
Jsc = ∫ SR(λ) × AM15G(λ) dλ / Area
```

### 5. Quality Control

Automated QC checks are performed:

| Check | Threshold | Action |
|-------|-----------|--------|
| Noise Level | < 0.02 A/W | Warning |
| Reference Stability | < 1.0 % | Error |
| Temperature Stability | < 2.0 °C | Warning |
| Minimum EQE | > 5.0 % | Warning |
| Data Completeness | > 95.0 % | Error |

## Data Outputs

### Raw Data

- Wavelength array (nm)
- Sample photocurrent (A)
- Reference photocurrent (A)
- Temperature readings (°C)
- Timestamps (s)

### Calculated Data

- Spectral Response (A/W)
- External Quantum Efficiency (%)
- Integrated Jsc (mA/cm²)
- Peak wavelength (nm)
- Peak EQE (%)

### Visualizations

- SR vs Wavelength plot
- EQE vs Wavelength plot
- Raw photocurrent plot (log scale)
- Temperature monitoring plot

## Interpretation of Results

### Silicon Solar Cells

**Typical Characteristics:**
- Peak EQE: 80-95% at 800-900 nm
- UV response: Limited by surface recombination
- IR cutoff: ~1100 nm (bandgap)
- Integrated Jsc: 35-43 mA/cm² (for high-efficiency cells)

**Indicators:**
- Low EQE in blue (< 500 nm): Poor surface passivation or heavy doping
- Low EQE in red (> 900 nm): Poor bulk quality or thin cell
- Overall low EQE: High series resistance or poor collection

### CdTe Solar Cells

**Typical Characteristics:**
- Peak EQE: 75-90% at 500-700 nm
- Sharp cutoff: ~850 nm
- Integrated Jsc: 25-28 mA/cm²

### CIGS Solar Cells

**Typical Characteristics:**
- Peak EQE: 80-95% at 600-900 nm
- Extended IR response to ~1200 nm
- Integrated Jsc: 35-40 mA/cm²

## Python API Usage

### Basic Usage

```python
from src.protocols import Protocol, SpectralResponseTest

# Load protocol
protocol = Protocol("protocols/SPEC-001.json")

# Initialize test
test = SpectralResponseTest(protocol=protocol)

# Configure parameters
test_params = {
    "wavelength": {
        "start": 300,
        "end": 1200,
        "step_size": 10
    },
    "temperature": 25,
    "integration_time": 100,
    "averaging": 3
}

sample_info = {
    "sample_id": "SI-CELL-001",
    "sample_type": "Solar Cell",
    "technology": "c-Si",
    "area": 2.0
}

# Run complete workflow
test_id = test.initialize(test_params, sample_info)
test.run()
test.load_reference_calibration("reference_cal.csv")
test.analyze()
qc_results = test.run_qc()
exported_files = test.export_results()
test.complete()

# Access results
print(f"Peak EQE: {test.results['peak_eqe']:.1f}%")
print(f"Peak Wavelength: {test.results['peak_wavelength']:.0f} nm")
print(f"Integrated Jsc: {test.results['integrated_jsc']:.2f} mA/cm²")
```

### Custom Reference Calibration

```python
import pandas as pd

# Load custom reference calibration
ref_cal = pd.read_csv("my_reference.csv")
# Format: columns must be 'wavelength' and 'spectral_response'

test.reference_sr = ref_cal
test.analyze()
```

### Accessing Detailed Data

```python
# Get raw data
raw_data = test.raw_data
wavelengths = raw_data['wavelength']
photocurrents = raw_data['photocurrent_sample']

# Get calculated data
calc_data = test.calculated_data
sr = calc_data['spectral_response']
eqe = calc_data['external_quantum_efficiency']

# Get specific results
peak_eqe = test.results['peak_eqe']
peak_wavelength = test.results['peak_wavelength']
integrated_jsc = test.results['integrated_jsc']
```

## Troubleshooting

### Common Issues

**Low Signal/Noise**
- Increase integration time
- Increase averaging
- Check light source power
- Verify electrical connections

**Reference Instability**
- Allow longer warm-up time
- Check lamp alignment
- Verify reference detector calibration

**Temperature Drift**
- Allow longer stabilization time
- Check temperature controller
- Reduce ambient temperature variations

**Unexpected EQE Shape**
- Verify wavelength calibration
- Check for stray light
- Verify reference detector calibration
- Check for bias light interference

## References

1. IEC 60904-8:2014 - Photovoltaic devices - Part 8: Measurement of spectral responsivity of a photovoltaic (PV) device
2. ASTM E1021 - Standard Test Methods for Measuring Spectral Response of Photovoltaic Cells
3. ASTM G173 - Standard Tables for Reference Solar Spectral Irradiances

## Version History

- **v1.0.0** (2025-01-14): Initial release
  - IEC 60904-8 compliant implementation
  - Full automation and analysis
  - Integrated QC checks
