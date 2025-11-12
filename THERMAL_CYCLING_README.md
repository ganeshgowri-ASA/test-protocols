# Thermal Cycling Protocol (PVTP-002-TC)

## Overview

Comprehensive thermal cycling test protocol implementation for photovoltaic (PV) modules according to **IEC 61215-2:2016 MQT 12** standard. This protocol evaluates module resistance to thermal fatigue, temperature extremes, and stress on materials and interconnects.

## Protocol Details

- **Protocol ID:** PVTP-002-TC
- **Category:** Environmental & Durability Testing
- **Standards:**
  - IEC 61215-2:2016 MQT 12
  - IEC 61730
  - UL 1703
- **Test Types:** TC50, TC200

## Temperature Profile

- **Temperature Range:** -40°C to +85°C
- **Dwell Time:** 30 minutes at each extreme
- **Transition Rate:** ≤100°C/hour
- **Humidity Level:** <75% RH

## Components

### 1. Protocol Template (`templates/thermal_cycling.json`)

Complete JSON-based protocol definition including:

- **Protocol Metadata:** ID, name, version, standards, test types
- **General Data:** Test facility, project, client, technician, chamber ID
- **Sample Information:** Module specifications, serial numbers, pre-test measurements
- **Protocol Inputs:** Cycle count, temperature range, dwell times, measurement intervals
- **Cycle Monitoring:** Real-time temperature, humidity, phase tracking
- **Intermediate Measurements:** Electrical parameters (Pmax, Voc, Isc, FF, Rs, Rsh)
- **Analysis:** Power degradation, performance retention, defect tracking
- **Charts:** Temperature profiles, degradation trends, parameter evolution
- **Quality Control:** Calibration records, sensor accuracy, data validation
- **Maintenance:** Chamber maintenance logs, sensor replacement schedules
- **Project Management:** Test phases, milestones, deliverables
- **NC Register:** Non-conformance tracking and corrective actions
- **Export Settings:** Excel and PDF report configurations

### 2. Backend Handler (`backend/protocols/thermal_cycling_handler.py`)

Python handler with comprehensive functionality:

#### Key Features:

**Cycle Tracking:**
- Add and retrieve cycle monitoring data
- Track current cycle number
- Access complete cycle history

**Temperature Profile Validation:**
- Validate compliance with IEC 61215-2 requirements
- Check temperature range accuracy
- Verify dwell time stability
- Monitor transition rates
- Generate validation reports with errors and warnings

**Measurement Analysis:**
- Record electrical measurements at specified intervals
- Track measurement trends over time
- Compare measurements between cycles
- Support for all key parameters (Pmax, Voc, Isc, FF, Rs, Rsh)

**Degradation Calculation:**
- Calculate power degradation for individual modules
- Batch analysis for multiple modules
- Statistical analysis (mean, std dev, outliers)
- Degradation rate calculation (% per cycle)

**Pass/Fail Determination:**
- Automated pass/fail based on IEC 61215-2 criteria
- Maximum 5% power loss threshold
- Visual and EL defect evaluation
- Detailed justification generation

**Data Management:**
- Export to JSON format
- Save/load project data
- Chart data preparation utilities

#### Data Structures:

```python
@dataclass
class CycleData:
    cycle_number: int
    timestamp: datetime
    chamber_temp: float
    humidity: float
    module_temps: Dict[str, float]
    cycle_phase: str
    alarms: List[str]

@dataclass
class MeasurementData:
    serial_number: str
    cycle_number: int
    pmax: float
    voc: float
    isc: float
    vmp: float
    imp: float
    ff: float
    rs: Optional[float]
    rsh: Optional[float]

@dataclass
class DegradationAnalysis:
    serial_number: str
    initial_power: float
    final_power: float
    absolute_loss: float
    percentage_loss: float
    degradation_rate: float
    performance_retention: float
```

### 3. Streamlit UI (`streamlit_app/pages/thermal_cycling_protocol.py`)

Interactive web interface with five main sections:

#### Test Setup
- General test data entry (facility, project, client, technician)
- Sample information (module specs, serial numbers)
- Pre-test power measurements
- Protocol parameter configuration (TC50/TC200, temperature range, dwell times)
- Measurement interval selection

#### Cycle Monitoring
- **Cycle Counter Widget:**
  - Current cycle display
  - Progress percentage
  - Estimated time remaining
  - Visual progress bar

- **Real-Time Temperature Monitoring:**
  - Data entry form (chamber temp, humidity, module temp, phase)
  - Current readings display
  - Live temperature profile chart
  - Phase tracking (heating, hot_dwell, cooling, cold_dwell)

- **Cycle Validation:**
  - On-demand validation of temperature profiles
  - Compliance checking against IEC 61215-2
  - Error and warning reporting
  - Statistical summary

#### Measurements
- Electrical parameter entry form
- Measurement data table display
- CSV export functionality
- Historical measurement tracking

#### Analysis & Results
- **Degradation Analysis:**
  - Module selection and cycle range specification
  - Power loss calculation and display
  - Performance retention metrics
  - Degradation rate computation

- **Automated Pass/Fail Determination:**
  - IEC 61215-2 compliance checking
  - Visual pass/fail indication
  - Detailed justification

- **Interactive Charts:**
  - Power degradation trend (all modules)
  - Parameter evolution (Pmax, Voc, Isc, FF)
  - Initial vs current comparison (bar charts)
  - Acceptance criteria visualization

#### Data Management
- Project save/load functionality
- Report export (JSON, Excel, PDF)
- Configurable export options
- Quick CSV exports for cycle data and measurements

## Installation

```bash
# Clone repository
git clone <repository-url>
cd test-protocols

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Streamlit App

```bash
streamlit run streamlit_app/pages/thermal_cycling_protocol.py
```

### Using the Backend Handler

```python
from backend.protocols.thermal_cycling_handler import (
    ThermalCyclingHandler,
    CycleData,
    MeasurementData
)
from datetime import datetime

# Initialize handler
handler = ThermalCyclingHandler()

# Add cycle data
cycle_data = CycleData(
    cycle_number=1,
    timestamp=datetime.now(),
    chamber_temp=-40.0,
    humidity=50.0,
    module_temps={"SN001": -39.5},
    cycle_phase="cold_dwell",
    alarms=[]
)
handler.add_cycle_data(cycle_data)

# Add measurement
measurement = MeasurementData(
    serial_number="SN001",
    cycle_number=0,
    pmax=450.0,
    voc=48.5,
    isc=11.2,
    vmp=40.3,
    imp=11.1,
    ff=82.5
)
handler.add_measurement(measurement)

# Calculate degradation
analysis = handler.calculate_degradation("SN001", initial_cycle=0, final_cycle=200)
print(f"Power loss: {analysis.percentage_loss:.2f}%")

# Validate temperature profile
validation = handler.validate_temperature_profile(cycle_number=1)
print(f"Valid: {validation['valid']}")

# Determine pass/fail
result = handler.determine_pass_fail(analysis)
print(f"Result: {result['result']}")
```

## Test Procedure

### 1. Setup Phase
1. Configure test parameters (TC50/TC200)
2. Enter module specifications and serial numbers
3. Record pre-test power measurements
4. Set measurement intervals

### 2. Testing Phase
1. Monitor real-time temperature and humidity
2. Record cycle data at regular intervals
3. Validate temperature profiles
4. Perform intermediate measurements at specified cycles
5. Track any alarms or deviations

### 3. Analysis Phase
1. Calculate power degradation for all modules
2. Review parameter evolution trends
3. Compare initial vs final measurements
4. Identify outliers and anomalies
5. Determine pass/fail status

### 4. Reporting Phase
1. Generate comprehensive reports
2. Export data in multiple formats
3. Document non-conformances
4. Archive project data

## Pass/Fail Criteria (IEC 61215-2)

A module **PASSES** if:
- Power degradation ≤ 5%
- No major visual defects
- No major EL defects
- Temperature profile compliance

A module **FAILS** if:
- Power degradation > 5%
- Major visual defects present (delamination, cell cracks, etc.)
- Major EL defects present (inactive cells, busbar discontinuity, etc.)
- Temperature profile non-compliance

## Quality Control Features

- Chamber calibration tracking
- Sensor accuracy validation
- Data completeness monitoring
- Reference module verification
- Maintenance logging
- Test interruption documentation

## Project Management Integration

- Test phase tracking
- Completion percentage calculation
- Milestone management
- Stakeholder tracking
- Deliverable status monitoring

## Non-Conformance Management

Comprehensive NC register with:
- Unique NC identification
- Issue categorization
- Root cause analysis
- Corrective and preventive actions
- Status tracking
- Verification of effectiveness

## Chart Types

1. **Temperature Profile:** Time vs temperature for representative cycle
2. **Power Degradation Trend:** Cycle number vs power/retention
3. **Parameter Evolution:** Multi-line chart for Pmax, Voc, Isc, FF
4. **Degradation Distribution:** Box plot for batch analysis
5. **Initial vs Current Comparison:** Bar chart comparison

## Export Formats

- **JSON:** Complete project data with all measurements and analysis
- **Excel:** Multi-sheet workbook with summary, test parameters, cycle data, measurements, analysis, charts, QC records, NC register
- **PDF:** Comprehensive report with cover page, executive summary, test setup, results, analysis, conclusions, appendices
- **CSV:** Quick exports for cycle data and measurements

## Dependencies

- Python 3.8+
- numpy: Numerical computations and statistical analysis
- pandas: Data manipulation and export
- plotly: Interactive visualizations
- streamlit: Web interface
- openpyxl/xlsxwriter: Excel export
- reportlab: PDF generation

## Future Enhancements

- Real-time chamber integration via APIs
- Automated EL image analysis
- Advanced statistical modeling
- Multi-chamber coordination
- Cloud data synchronization
- Mobile app for technicians
- AI-powered anomaly detection

## Standards Compliance

This implementation follows:
- IEC 61215-2:2016 MQT 12 (Thermal Cycling Test)
- IEC 61730 (PV Module Safety Qualification)
- UL 1703 (Flat-Plate Photovoltaic Modules)

## License

See LICENSE file in repository root.

## Contact

For questions or issues, please refer to the main repository documentation.
