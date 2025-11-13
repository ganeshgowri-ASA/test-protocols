# NOCT-001 Protocol User Guide

## Overview

The NOCT-001 protocol implements the Nominal Operating Cell Temperature test per IEC 61215-1:2021, Section 7.3.

**Purpose:** Determine the temperature that a PV module reaches under nominal operating conditions:
- Irradiance: 800 W/m²
- Ambient temperature: 20°C
- Wind speed: 1 m/s
- Open circuit conditions

## Features

### Interactive UI
- **Conditional Fields**: Parameters appear/hide based on selections
- **Smart Dropdowns**: Auto-complete with historical data
- **Auto-Validation**: Real-time parameter validation
- **User-Friendly Forms**: Minimal effort with intelligent defaults

### Real-Time Monitoring
- **Live Graphs**: Temperature vs Time, Power vs Temperature
- **Environmental Monitoring**: Irradiance and wind speed tracking
- **Progress Indicators**: Real-time test progress updates

### Data Traceability
- **Full Audit Trail**: Every action logged with timestamps
- **Data Integrity**: SHA-256 checksums and digital signatures
- **Version Control**: Complete change history

### QA Testing Built-In
- **Pre-Test Checks**: Equipment calibration verification
- **During-Test Monitoring**: Continuous data quality checks
- **Post-Test Validation**: Results validation against criteria

## Test Parameters

### Required Parameters

| Parameter | Description | Unit | Typical Range |
|-----------|-------------|------|---------------|
| Sample ID | Unique sample identifier | - | e.g., MOD-2025-001 |
| Manufacturer | Module manufacturer | - | - |
| Model | Module model number | - | - |
| Technology | Cell technology type | - | mono-Si, poly-Si, etc. |
| Rated Power | Nameplate power at STC | W | 100-600 |
| Module Area | Total module area | m² | 1.0-2.5 |

### Test Conditions

| Parameter | Default | Range | Tolerance |
|-----------|---------|-------|-----------|
| Test Irradiance | 800 W/m² | 700-900 W/m² | ±50 W/m² |
| Ambient Temperature | 20°C | 15-25°C | ±2°C |
| Wind Speed | 1 m/s | 0.5-2.0 m/s | ±0.25 m/s |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| Calculate Temp Coefficients | Measure temperature coefficients | Yes |
| Temp Coefficient Points | Number of temperature points | 5 |
| Stabilization Duration | Time to wait for stabilization | 30 min |
| Measurement Interval | Time between measurements | 60 sec |

## Test Procedure

### Step 1: Equipment Setup (15 min)
1. Verify all equipment calibration is current
2. Connect sensors (thermocouples, pyranometer, anemometer)
3. Configure data acquisition system
4. Verify electrical safety

### Step 2: Module Installation (10 min)
1. Mount module on open rack structure
2. Ensure proper clearance for airflow
3. Set appropriate tilt angle
4. Secure all connections

### Step 3: Sensor Attachment (10 min)
1. Attach thermocouples to module back surface
   - Center back
   - Edge back
   - Corner back
2. Position pyranometer in module plane
3. Position anemometer at module level

### Step 4: Environmental Conditioning (20 min)
1. Adjust solar simulator to 800 W/m²
2. Set chamber temperature to 20°C
3. Set wind speed to 1 m/s
4. Wait for conditions to stabilize

### Step 5: Thermal Stabilization (30+ min)
1. Monitor cell temperature continuously
2. Check for temperature stability:
   - Variation < 1°C in last 10 minutes
   - Minimum duration: 15 minutes
3. Record when stabilization achieved

### Step 6: Data Collection (15 min)
1. Collect measurements at regular intervals
2. Record:
   - Cell temperature (3 locations)
   - Ambient temperature
   - Irradiance
   - Wind speed
3. Minimum 30 data points required

### Step 7: Temperature Coefficients (60 min, optional)
1. Vary cell temperature from 25°C to 65°C
2. Measure IV characteristics at each temperature
3. Record Pmax, Voc, Isc
4. Calculate temperature coefficients

### Step 8: Data Analysis (10 min, automated)
1. Calculate NOCT
2. Calculate Pmax at NOCT
3. Calculate efficiency at NOCT
4. Calculate temperature coefficients (if enabled)
5. Generate statistical analysis

### Step 9: Report Generation (10 min, automated)
1. Generate comprehensive PDF report
2. Include all graphs and analysis
3. Add QC check results
4. Export data in multiple formats

## Calculated Results

### Primary Results

**NOCT (Nominal Operating Cell Temperature)**
- Formula: `NOCT = T_ambient + (T_cell - T_ambient) × (800 / G_actual)`
- Unit: °C
- Typical Range: 40-50°C
- Uncertainty: ±2°C

**Power at NOCT**
- Formula: `Pmax_NOCT = Pmax_STC × [1 + α_P × (NOCT - 25)] × (800 / 1000)`
- Unit: W
- Expected: 20-30% lower than STC rating

**Efficiency at NOCT**
- Formula: `η_NOCT = (Pmax_NOCT / (800 × A_module)) × 100`
- Unit: %
- Typical Range: 15-20%

### Temperature Coefficients (Optional)

**Power Coefficient (α_P)**
- Unit: %/°C
- Typical for Si: -0.35 to -0.50 %/°C
- Calculated from linear regression of P vs T

**Voc Coefficient (β_Voc)**
- Unit: %/°C
- Typical for Si: -0.25 to -0.35 %/°C
- Voc decreases with temperature

**Isc Coefficient (α_Isc)**
- Unit: %/°C
- Typical for Si: +0.03 to +0.06 %/°C
- Isc increases slightly with temperature

## Acceptance Criteria

### NOCT Range
- Typical: 40-50°C
- Values outside this range trigger warnings

### Environmental Compliance
- Irradiance: 750-850 W/m² (average during test)
- Ambient Temp: 18-22°C (average during test)
- Wind Speed: 0.75-1.25 m/s (average during test)

### Measurement Stability
- Temperature variation: < 2°C in last 10 minutes
- Irradiance variation: < 50 W/m² in last 10 minutes

### Data Quality
- Minimum data points: 30
- Maximum outliers: < 5%
- Minimum stabilization time: 15 minutes

## Using the UI

### Starting a Test

1. **Navigate to NOCT-001 protocol**
2. **Fill in test parameters**:
   - Required fields marked with *
   - Validation feedback shown in real-time
   - Smart dropdowns show previous entries
3. **Review test conditions**
4. **Click "Start Test"**

### During Test Execution

- **Monitor Progress**: Progress bar shows current step
- **Live Graphs**: Real-time temperature monitoring
- **Environmental Conditions**: Track irradiance and wind speed
- **Pause/Resume**: Ability to pause test if needed
- **Auto-Save**: Progress saved every 30 seconds

### After Test Completion

- **View Results**: Key metrics displayed prominently
- **Interactive Graphs**: Explore data with Plotly charts
- **Download Report**: Export as PDF, Excel, or JSON
- **Audit Trail**: Review complete test history

## Troubleshooting

### Temperature Not Stabilizing
- **Check**: Wind speed consistency
- **Check**: Solar simulator stability
- **Action**: Increase stabilization duration
- **Action**: Check thermal contact of sensors

### Data Quality Warnings
- **High Outliers**: Check sensor connections
- **Missing Data**: Check data acquisition system
- **High Variation**: Extend measurement period

### Environmental Condition Violations
- **Irradiance**: Recalibrate solar simulator
- **Temperature**: Adjust chamber setpoint
- **Wind Speed**: Check anemometer calibration

### Equipment Calibration Expired
- **Action**: Schedule calibration before testing
- **Workaround**: Document in test report
- **Impact**: May affect result uncertainty

## Best Practices

### Before Testing
1. Verify equipment calibration dates
2. Clean module surface
3. Check all cable connections
4. Perform electrical safety checks

### During Testing
1. Monitor environmental conditions continuously
2. Don't disturb the test setup
3. Record any anomalies or observations
4. Keep personnel traffic minimal

### After Testing
1. Allow module to cool before handling
2. Verify data completeness
3. Review and approve results
4. Archive all raw data files

## Data Export Formats

### JSON
- Complete protocol state
- All measurements and calculations
- Full audit trail
- Machine-readable

### CSV
- Time-series measurement data
- Easy import to Excel/MATLAB
- Human-readable

### PDF Report
- Professional test report
- All graphs and tables
- Executive summary
- QC check results

### Excel
- Multi-sheet workbook
- Summary sheet
- Raw data sheet
- Graphs sheet

## API Usage

```python
from protocols.performance.noct_001 import NOCT001Protocol

# Create protocol instance
protocol = NOCT001Protocol()

# Set parameters
parameters = {
    'sample_id': 'MOD-2025-001',
    'manufacturer': 'SolarCorp',
    'model': 'SC-300W',
    'technology': 'mono-Si',
    'rated_power': 300.0,
    'module_area': 1.6,
    'test_irradiance': 800,
    'ambient_temp_target': 20,
    'wind_speed_target': 1.0,
    'calculate_temp_coefficients': True
}
protocol.set_input_parameters(parameters)

# Run protocol
success = protocol.run()

# Get results
if success:
    print(f"NOCT: {protocol.noct_value:.2f}°C")
    print(f"Power at NOCT: {protocol.pmax_at_noct:.2f}W")

    # Generate report
    report = protocol.generate_report()

    # Export data
    json_data = protocol.export_data('json')
```

## References

- IEC 61215-1:2021 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 1: Test requirements
- Section 7.3 - Nominal Operating Cell Temperature (NOCT)
- ASTM E1036 - Standard Test Methods for Electrical Performance of Nonconcentrator Terrestrial Photovoltaic Modules and Arrays Using Reference Cells

## Support

For questions or issues:
- Email: support@genspark.io
- Documentation: https://docs.genspark.io
- Issue Tracker: https://github.com/genspark/protocols/issues
