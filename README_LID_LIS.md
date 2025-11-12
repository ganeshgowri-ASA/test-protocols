# LID/LIS Stabilization Protocol

## Overview

This protocol implements comprehensive testing for **Light Induced Degradation (LID)** and **Light & Elevated Temperature Induced Stabilization (LIS)** of photovoltaic modules.

**Protocol ID:** PVTP-001-LID-LIS
**Category:** Performance & Reliability Testing
**Standards:** IEC 61215, IEC 61730

## Components

### 1. JSON Template (`templates/lid_lis_stabilization.json`)

Comprehensive protocol template including:

- **Protocol Metadata**: ID, version, category, applicable standards
- **General Data**: Test lab, project, client, dates, operators, equipment
- **Sample Information**: Module specifications, serial numbers, nameplate ratings
- **Pre-Test Inspection**: Visual defects, EL imaging, initial flash test results
- **Protocol Inputs**:
  - Irradiance level (800-1200 W/m²)
  - Module temperature (50-75°C)
  - Test duration (100-500 hours)
  - Measurement intervals
  - Stabilization criteria
- **Live Readings**: Time-series data (irradiance, temperature, power, Voc, Isc, FF)
- **Analysis**: Degradation metrics, stabilization status, pass/fail criteria
- **Charts**: Power trends, degradation curves, temperature profiles
- **Quality Control**: Calibration status, measurement uncertainty, deviations
- **Maintenance**: Equipment logs, calibration schedules
- **Project Management**: Milestones, deadlines, status tracking
- **NC Register**: Non-conformance tracking and resolution

### 2. Backend Handler (`backend/protocols/lid_lis_handler.py`)

Python handler providing:

#### Key Features:

**Data Validation**
- Template-based validation of protocol data
- Input range checking (irradiance, temperature, duration)
- Required field verification
- Live reading validation

**Degradation Analysis**
```python
handler = LIDLISProtocolHandler()

# Calculate degradation metrics
results = handler.calculate_degradation_metrics(live_readings)
# Returns: initial_power, final_power, degradation_percentage,
#          recovery_percentage, stabilization_achieved, etc.
```

**Key Metrics Calculated:**
- Power degradation percentage from initial measurement
- Minimum power point and maximum degradation
- Power recovery from minimum to final
- Stabilization achievement and timing
- Power trend analysis (degrading/recovering/stable)

**Pass/Fail Determination**
```python
# Determine pass/fail based on criteria
results = handler.determine_pass_fail(
    module_results,
    criteria={
        'degradation_limit': 2.0,        # Max 2% degradation
        'stabilization_required': True,   # Must stabilize
        'min_stabilization_power': 98.0   # Min 98% of initial
    }
)
```

**Stabilization Detection**
- Monitors power variation within sliding time window
- Default: ≤0.5% variation over 48-hour window
- Returns stabilization time when achieved

**Chart Data Generation**
- Power vs time
- Degradation trends
- Temperature and irradiance profiles
- Fill factor evolution
- Multi-parameter correlations

### 3. Streamlit Interface (`streamlit_app/pages/lid_lis_protocol.py`)

Interactive web interface with 7 sections:

#### 📋 Protocol Setup
- General information entry
- Sample/module specification
- Protocol parameters (irradiance, temperature, duration)
- Measurement interval scheduling
- Pass/fail criteria definition

#### 🔍 Pre-Test Inspection
- Initial flash test measurements (Pmax, Voc, Isc, Vmp, Imp, FF)
- Visual inspection documentation
- Defect severity classification
- Baseline data establishment

#### 📊 Live Data Entry
- Real-time measurement recording
- Per-module data entry
- Automated timestamp tracking
- Live degradation calculations
- Quick statistics display
- **Real-time analysis** showing current degradation and recovery

#### 📈 Analysis & Results
- Comprehensive analysis report generation
- Module-by-module results
- Pass/fail determination
- Statistical summaries (average, std dev, pass rate)
- Detailed performance metrics

#### 📊 Charts & Visualization
- Interactive Plotly charts:
  - Power output vs time
  - Degradation percentage trends
  - Temperature profiles
  - Irradiance consistency
  - Fill factor evolution
- Multi-parameter comparison views
- Module-by-module visualization

#### ✅ Quality Control
- Equipment calibration tracking
- Calibration expiry monitoring
- Measurement uncertainty documentation
- Deviation logging

#### 📤 Export & Reports
- JSON export of complete protocol data
- Analysis report download
- Protocol summary display
- Timestamped file naming

## Usage

### Running the Streamlit App

```bash
cd streamlit_app
streamlit run pages/lid_lis_protocol.py
```

### Using the Backend Handler

```python
from backend.protocols.lid_lis_handler import LIDLISProtocolHandler

# Initialize handler
handler = LIDLISProtocolHandler()

# Validate protocol data
is_valid, errors = handler.validate_protocol_data(protocol_data)

# Calculate degradation metrics
results = handler.calculate_degradation_metrics(live_readings)

# Generate complete analysis report
report = handler.generate_analysis_report(protocol_data)

# Export to JSON
handler.export_to_json(report, 'analysis_report.json')
```

### Example Workflow

1. **Setup Protocol** (Protocol Setup page)
   - Enter test lab, project, client details
   - Define module specifications and serial numbers
   - Set irradiance (1000 W/m²), temperature (60°C), duration (200 hrs)
   - Define measurement intervals: 0, 24, 48, 96, 144, 200 hours
   - Set pass/fail criteria (e.g., <2% degradation)

2. **Pre-Test Inspection** (Pre-Test Inspection page)
   - Record initial flash test results for each module
   - Document any visual defects
   - Establish baseline performance

3. **Test Execution** (Live Data Entry page)
   - Record measurements at scheduled intervals
   - Monitor real-time degradation
   - Track temperature and irradiance stability
   - Add notes for any observations

4. **Analysis** (Analysis & Results page)
   - Generate comprehensive analysis
   - Review pass/fail status for each module
   - Examine degradation statistics
   - Verify stabilization achievement

5. **Visualization** (Charts & Visualization page)
   - Review power degradation curves
   - Analyze temperature and irradiance profiles
   - Compare module performance

6. **Export** (Export & Reports page)
   - Download complete protocol data (JSON)
   - Export analysis report
   - Archive for documentation

## Test Specifications

### Standard Conditions

- **Irradiance**: 1000 W/m² ±5%
- **Module Temperature**: 60°C ±2°C
- **Duration**: 200 hours (typical)
- **Measurement Intervals**: 0, 24, 48, 96, 144, 200 hours

### Acceptance Criteria (IEC 61215)

- Maximum power degradation: ≤2% from initial measurement
- Power stabilization required within test duration
- Final stabilized power: ≥98% of initial power

### Key Performance Indicators

1. **Power Degradation %**: (P_initial - P_final) / P_initial × 100
2. **Maximum Degradation**: Lowest power point during test
3. **Recovery %**: Power regained from minimum to final
4. **Stabilization Time**: Hours until power stabilizes
5. **Power Trend**: Degrading, recovering, or stable

## Data Structure

### Live Reading Format
```json
{
  "timestamp": "2025-11-12T10:30:00",
  "elapsed_hours": 48.5,
  "irradiance": 1000.0,
  "module_temp": 60.2,
  "module_id": "SN12345",
  "pmax": 395.8,
  "voc": 49.2,
  "isc": 10.15,
  "ff": 79.5,
  "notes": "Stable conditions"
}
```

### Analysis Result Format
```json
{
  "module_id": "SN12345",
  "initial_power": 400.0,
  "final_power": 396.5,
  "minimum_power": 394.2,
  "degradation_percentage": 0.875,
  "recovery_percentage": 0.575,
  "stabilization_achieved": true,
  "stabilization_time": 144.0,
  "power_trend": "stable",
  "pass_fail": "PASS",
  "pass_fail_reasons": ["All criteria met"]
}
```

## Features

### ✅ Self-Contained
- Complete JSON template definition
- Standalone backend processing
- Independent Streamlit interface

### 🔗 Framework Integration
- Compatible with core test protocol framework
- Follows standardized data structures
- Interoperable with other protocol modules

### 📊 Real-Time Analysis
- Live degradation calculation during data entry
- Instant feedback on module performance
- Progressive trend analysis

### 📈 Interactive Visualization
- Plotly-based interactive charts
- Multi-module comparison
- Zoom, pan, and hover capabilities

### 🔍 Comprehensive Validation
- Template-based data validation
- Range checking for all inputs
- Required field enforcement

### 💾 Export Capabilities
- JSON format for data interchange
- Timestamped file naming
- Complete protocol data preservation

## Standards Compliance

- **IEC 61215**: Terrestrial PV modules - Design qualification and type approval
  - Section 10.20: Light-induced degradation test
- **IEC 61730**: PV module safety qualification
  - Module construction and materials assessment

## Dependencies

```python
# Core
streamlit
pandas
numpy

# Visualization
plotly

# Standard library
json
datetime
pathlib
```

## File Structure

```
test-protocols/
├── templates/
│   └── lid_lis_stabilization.json      # Protocol template
├── backend/
│   └── protocols/
│       └── lid_lis_handler.py          # Backend handler
└── streamlit_app/
    └── pages/
        └── lid_lis_protocol.py         # Streamlit interface
```

## Future Enhancements

- [ ] Automated report generation (PDF)
- [ ] Email notifications for test completion
- [ ] Database integration for historical data
- [ ] Comparative analysis across test batches
- [ ] Advanced statistical analysis (regression, confidence intervals)
- [ ] Integration with equipment data loggers
- [ ] Real-time alerts for out-of-spec conditions
- [ ] Multi-user collaboration features

## Support

For issues or questions:
- Review the JSON template structure
- Check backend handler documentation
- Consult IEC 61215 and IEC 61730 standards
- Verify measurement equipment calibration

## Version History

- **v1.0** (2025-11-12): Initial implementation
  - Complete JSON template
  - Backend analysis handler
  - Streamlit interface with 7 sections
  - Real-time degradation monitoring
  - Interactive visualization
  - Pass/fail determination
