# Protocol Catalog

## Complete List of 54 PV Testing Protocols

This catalog provides a comprehensive overview of all 54 testing protocols included in the PV Testing Protocol Framework, organized by category and mapped to relevant IEC/ISO standards.

---

## 1. Module Performance Testing (9 Protocols)

### PVTP-001: STC Power Measurement
- **Standard**: IEC 61215-1:2021, IEC 61215-2
- **Description**: Standard Test Conditions (1000 W/m², 25°C, AM1.5G spectrum) power measurement
- **Duration**: 1-2 hours per module
- **Key Parameters**: Pmax, Voc, Isc, Vmp, Imp, Fill Factor, Efficiency
- **Equipment**: Solar simulator, I-V tracer, temperature sensors
- **Module File**: `protocols/performance/pvtp_001_stc_power.py`
- **JSON Template**: `templates/protocols/PVTP-001.json`
- **UI Page**: `pages/protocol_execution/PVTP-001.py`

### PVTP-002: NOCT Measurement
- **Standard**: IEC 61215-1:2021 (MST 04)
- **Description**: Nominal Operating Cell Temperature measurement
- **Duration**: 4-6 hours
- **Key Parameters**: NOCT, Pmax at NOCT, Temperature coefficient validation
- **Equipment**: Outdoor test rack, pyranometer, temperature sensors, wind speed meter
- **Module File**: `protocols/performance/pvtp_002_noct.py`
- **JSON Template**: `templates/protocols/PVTP-002.json`
- **UI Page**: `pages/protocol_execution/PVTP-002.py`

### PVTP-003: Low Irradiance Performance
- **Standard**: IEC 61215-1:2021 (MST 05)
- **Description**: Performance at 200 W/m² and 500 W/m²
- **Duration**: 2-3 hours
- **Key Parameters**: Pmax, efficiency at low light, linearity
- **Equipment**: Solar simulator with variable irradiance, I-V tracer
- **Module File**: `protocols/performance/pvtp_003_low_irradiance.py`
- **JSON Template**: `templates/protocols/PVTP-003.json`
- **UI Page**: `pages/protocol_execution/PVTP-003.py`

### PVTP-004: Temperature Coefficients
- **Standard**: IEC 61215-1:2021 (MST 06)
- **Description**: Measurement of temperature coefficients for Pmax, Voc, and Isc
- **Duration**: 3-4 hours
- **Key Parameters**: αIsc, βVoc, γPmax (%/°C)
- **Equipment**: Temperature-controlled chamber, solar simulator
- **Module File**: `protocols/performance/pvtp_004_temp_coefficients.py`
- **JSON Template**: `templates/protocols/PVTP-004.json`
- **UI Page**: `pages/protocol_execution/PVTP-004.py`

### PVTP-005: I-V Curve Analysis
- **Standard**: IEC 60904-1:2020
- **Description**: Detailed I-V characteristic curve analysis
- **Duration**: 1-2 hours
- **Key Parameters**: I-V curve shape, series resistance, shunt resistance, diode ideality factor
- **Equipment**: High-precision I-V tracer, data analysis software
- **Module File**: `protocols/performance/pvtp_005_iv_curve.py`
- **JSON Template**: `templates/protocols/PVTP-005.json`
- **UI Page**: `pages/protocol_execution/PVTP-005.py`

### PVTP-006: Spectral Response
- **Standard**: IEC 60904-8:2014
- **Description**: Quantum efficiency and spectral response measurement
- **Duration**: 2-3 hours
- **Key Parameters**: QE(λ), spectral response, optimal wavelength range
- **Equipment**: Monochromator, light source, current meter
- **Module File**: `protocols/performance/pvtp_006_spectral_response.py`
- **JSON Template**: `templates/protocols/PVTP-006.json`
- **UI Page**: `pages/protocol_execution/PVTP-006.py`

### PVTP-007: Angle of Incidence (AOI)
- **Standard**: IEC 61215-1:2021 (MST 07)
- **Description**: Performance at various angles of incidence
- **Duration**: 3-4 hours
- **Key Parameters**: IAM (Incidence Angle Modifier), performance at 0°, 30°, 45°, 60°, 75°
- **Equipment**: Rotating test platform, solar simulator
- **Module File**: `protocols/performance/pvtp_007_aoi.py`
- **JSON Template**: `templates/protocols/PVTP-007.json`
- **UI Page**: `pages/protocol_execution/PVTP-007.py`

### PVTP-008: Bifacial Performance
- **Standard**: IEC 60904-1-2:2019
- **Description**: Front and rear side performance characterization
- **Duration**: 2-3 hours
- **Key Parameters**: Bifacial factor, rear side efficiency, front/rear power ratio
- **Equipment**: Dual-sided solar simulator or albedo test setup
- **Module File**: `protocols/performance/pvtp_008_bifacial.py`
- **JSON Template**: `templates/protocols/PVTP-008.json`
- **UI Page**: `pages/protocol_execution/PVTP-008.py`

### PVTP-009: Reverse Bias Characteristics
- **Standard**: IEC 61215-1:2021 (MST 19)
- **Description**: Reverse bias I-V characteristics and hot spot evaluation
- **Duration**: 2-3 hours
- **Key Parameters**: Reverse breakdown voltage, hot spot temperature, shading tolerance
- **Equipment**: Reverse bias power supply, IR camera
- **Module File**: `protocols/performance/pvtp_009_reverse_bias.py`
- **JSON Template**: `templates/protocols/PVTP-009.json`
- **UI Page**: `pages/protocol_execution/PVTP-009.py`

---

## 2. Electrical Safety Testing (8 Protocols)

### PVTP-010: Insulation Resistance (Dry)
- **Standard**: IEC 61215-1:2021 (MST 01), IEC 61730-2:2016
- **Description**: Insulation resistance measurement in dry conditions
- **Duration**: 1 hour
- **Key Parameters**: Insulation resistance (≥400 MΩ·m²)
- **Equipment**: Insulation resistance tester (1000 VDC)
- **Module File**: `protocols/safety/pvtp_010_insulation_dry.py`
- **JSON Template**: `templates/protocols/PVTP-010.json`
- **UI Page**: `pages/protocol_execution/PVTP-010.py`

### PVTP-011: Insulation Resistance (Wet)
- **Standard**: IEC 61215-1:2021 (MST 02), IEC 61730-2:2016
- **Description**: Wet leakage current test
- **Duration**: 2-3 hours
- **Key Parameters**: Leakage current (≤1 μA per kW rated power)
- **Equipment**: Water spray apparatus, leakage current meter
- **Module File**: `protocols/safety/pvtp_011_wet_leakage.py`
- **JSON Template**: `templates/protocols/PVTP-011.json`
- **UI Page**: `pages/protocol_execution/PVTP-011.py`

### PVTP-012: Diode Thermal Test
- **Standard**: IEC 61215-1:2021 (MST 18)
- **Description**: Bypass diode thermal test
- **Duration**: 2 hours
- **Key Parameters**: Diode temperature, forward voltage drop, reverse leakage
- **Equipment**: IR camera, multimeter, shading device
- **Module File**: `protocols/safety/pvtp_012_diode_thermal.py`
- **JSON Template**: `templates/protocols/PVTP-012.json`
- **UI Page**: `pages/protocol_execution/PVTP-012.py`

### PVTP-013: Ground Continuity
- **Standard**: IEC 61215-1:2021, IEC 61730-2:2016
- **Description**: Frame ground continuity verification
- **Duration**: 30 minutes
- **Key Parameters**: Resistance between frame and ground points (≤0.1 Ω)
- **Equipment**: Low resistance ohmmeter
- **Module File**: `protocols/safety/pvtp_013_ground_continuity.py`
- **JSON Template**: `templates/protocols/PVTP-013.json`
- **UI Page**: `pages/protocol_execution/PVTP-013.py`

### PVTP-014: High Voltage Stress Test
- **Standard**: IEC 61730-2:2016 (MST 50)
- **Description**: Dielectric withstand test
- **Duration**: 1 hour
- **Key Parameters**: Test voltage (system voltage + 1000V), leakage current
- **Equipment**: High voltage tester, current monitor
- **Module File**: `protocols/safety/pvtp_014_high_voltage.py`
- **JSON Template**: `templates/protocols/PVTP-014.json`
- **UI Page**: `pages/protocol_execution/PVTP-014.py`

### PVTP-015: Hot Spot Endurance
- **Standard**: IEC 61215-1:2021 (MST 09)
- **Description**: Hot spot heating test
- **Duration**: 2-3 hours
- **Key Parameters**: Maximum hot spot temperature, duration at elevated temperature
- **Equipment**: IR camera, shading device, solar simulator
- **Module File**: `protocols/safety/pvtp_015_hot_spot.py`
- **JSON Template**: `templates/protocols/PVTP-015.json`
- **UI Page**: `pages/protocol_execution/PVTP-015.py`

### PVTP-016: Fire Resistance (Class A/B/C)
- **Standard**: IEC 61730-2:2016, UL 1703
- **Description**: Fire resistance classification test
- **Duration**: 1 day
- **Key Parameters**: Flame spread rating, burning brand test
- **Equipment**: Fire test apparatus, burning brand
- **Module File**: `protocols/safety/pvtp_016_fire_resistance.py`
- **JSON Template**: `templates/protocols/PVTP-016.json`
- **UI Page**: `pages/protocol_execution/PVTP-016.py`

### PVTP-017: Overvoltage Protection
- **Standard**: IEC 61730-2:2016
- **Description**: Overvoltage category verification
- **Duration**: 2 hours
- **Key Parameters**: Voltage withstand, protection device response
- **Equipment**: Impulse generator, voltage monitor
- **Module File**: `protocols/safety/pvtp_017_overvoltage.py`
- **JSON Template**: `templates/protocols/PVTP-017.json`
- **UI Page**: `pages/protocol_execution/PVTP-017.py`

---

## 3. Environmental Testing (12 Protocols)

### PVTP-018: Thermal Cycling
- **Standard**: IEC 61215-1:2021 (MQT 12)
- **Description**: 200 cycles (-40°C to +85°C)
- **Duration**: 30-35 days
- **Key Parameters**: Power degradation (≤5%), visual inspection, insulation resistance
- **Equipment**: Thermal cycling chamber
- **Module File**: `protocols/environmental/pvtp_018_thermal_cycling.py`
- **JSON Template**: `templates/protocols/PVTP-018.json`
- **UI Page**: `pages/protocol_execution/PVTP-018.py`

### PVTP-019: Humidity Freeze
- **Standard**: IEC 61215-1:2021 (MQT 13)
- **Description**: 10 cycles (+85°C/85%RH → -40°C)
- **Duration**: 12-15 days
- **Key Parameters**: Power degradation (≤5%), visual defects, insulation
- **Equipment**: Climate chamber with humidity control
- **Module File**: `protocols/environmental/pvtp_019_humidity_freeze.py`
- **JSON Template**: `templates/protocols/PVTP-019.json`
- **UI Page**: `pages/protocol_execution/PVTP-019.py`

### PVTP-020: Damp Heat
- **Standard**: IEC 61215-1:2021 (MQT 14)
- **Description**: 1000 hours at 85°C/85%RH
- **Duration**: 42 days
- **Key Parameters**: Power degradation (≤5%), corrosion, delamination
- **Equipment**: Damp heat chamber
- **Module File**: `protocols/environmental/pvtp_020_damp_heat.py`
- **JSON Template**: `templates/protocols/PVTP-020.json`
- **UI Page**: `pages/protocol_execution/PVTP-020.py`

### PVTP-021: UV Preconditioning
- **Standard**: IEC 61215-1:2021 (MQT 10)
- **Description**: UV exposure 15 kWh/m² at 280-385 nm
- **Duration**: 5-7 days
- **Key Parameters**: Discoloration, power degradation
- **Equipment**: UV chamber with filtered lamps
- **Module File**: `protocols/environmental/pvtp_021_uv_preconditioning.py`
- **JSON Template**: `templates/protocols/PVTP-021.json`
- **UI Page**: `pages/protocol_execution/PVTP-021.py`

### PVTP-022: UV Extended Exposure
- **Standard**: IEC 61215-1:2021, IEC 61345
- **Description**: Extended UV exposure up to 60 kWh/m²
- **Duration**: 20-30 days
- **Key Parameters**: Yellowing index, transmittance change, power loss
- **Equipment**: UV chamber with spectral monitoring
- **Module File**: `protocols/environmental/pvtp_022_uv_extended.py`
- **JSON Template**: `templates/protocols/PVTP-022.json`
- **UI Page**: `pages/protocol_execution/PVTP-022.py`

### PVTP-023: Salt Mist Corrosion
- **Standard**: IEC 61215-1:2021, IEC 60068-2-52
- **Description**: Salt mist exposure for marine environments
- **Duration**: 14 days
- **Key Parameters**: Corrosion rating, electrical performance
- **Equipment**: Salt spray chamber
- **Module File**: `protocols/environmental/pvtp_023_salt_mist.py`
- **JSON Template**: `templates/protocols/PVTP-023.json`
- **UI Page**: `pages/protocol_execution/PVTP-023.py`

### PVTP-024: Ammonia Corrosion
- **Standard**: IEC 62716:2013
- **Description**: Ammonia exposure test for agricultural applications
- **Duration**: 8-10 days
- **Key Parameters**: Corrosion, power degradation, visual defects
- **Equipment**: Ammonia chamber
- **Module File**: `protocols/environmental/pvtp_024_ammonia.py`
- **JSON Template**: `templates/protocols/PVTP-024.json`
- **UI Page**: `pages/protocol_execution/PVTP-024.py`

### PVTP-025: High Temperature/High Humidity (HTHH)
- **Standard**: IEC 62938:2020
- **Description**: Extended exposure at 85°C/85%RH (2000+ hours)
- **Duration**: 84+ days
- **Key Parameters**: Power degradation, reliability assessment
- **Equipment**: Climate chamber
- **Module File**: `protocols/environmental/pvtp_025_hthh.py`
- **JSON Template**: `templates/protocols/PVTP-025.json`
- **UI Page**: `pages/protocol_execution/PVTP-025.py`

### PVTP-026: Temperature/Humidity Cycling
- **Standard**: IEC TS 63126:2020
- **Description**: Combined thermal and humidity stress cycles
- **Duration**: 25-30 days
- **Key Parameters**: Degradation rate, failure modes
- **Equipment**: Advanced climate chamber
- **Module File**: `protocols/environmental/pvtp_026_th_cycling.py`
- **JSON Template**: `templates/protocols/PVTP-026.json`
- **UI Page**: `pages/protocol_execution/PVTP-026.py`

### PVTP-027: Dry Heat
- **Standard**: IEC 61215-1:2021
- **Description**: 200 hours at 85°C dry heat
- **Duration**: 9 days
- **Key Parameters**: Power stability, material degradation
- **Equipment**: Dry heat oven
- **Module File**: `protocols/environmental/pvtp_027_dry_heat.py`
- **JSON Template**: `templates/protocols/PVTP-027.json`
- **UI Page**: `pages/protocol_execution/PVTP-027.py`

### PVTP-028: Cold Temperature Test
- **Standard**: IEC 61215-1:2021
- **Description**: Low temperature operation and storage
- **Duration**: 2-3 days
- **Key Parameters**: Cold temperature performance, flex cable integrity
- **Equipment**: Cold chamber
- **Module File**: `protocols/environmental/pvtp_028_cold_temp.py`
- **JSON Template**: `templates/protocols/PVTP-028.json`
- **UI Page**: `pages/protocol_execution/PVTP-028.py`

### PVTP-029: Outdoor Exposure
- **Standard**: IEC 61215-1:2021 (MQT 20)
- **Description**: Natural outdoor weathering
- **Duration**: 60+ kWh/m² (6-12 months depending on location)
- **Key Parameters**: Real-world degradation, long-term stability
- **Equipment**: Outdoor test rack, monitoring equipment
- **Module File**: `protocols/environmental/pvtp_029_outdoor_exposure.py`
- **JSON Template**: `templates/protocols/PVTP-029.json`
- **UI Page**: `pages/protocol_execution/PVTP-029.py`

---

## 4. Mechanical Testing (8 Protocols)

### PVTP-030: Mechanical Load Test (Static)
- **Standard**: IEC 61215-1:2021 (MQT 16)
- **Description**: Front and rear static load (2400 Pa / -2400 Pa)
- **Duration**: 2-3 hours
- **Key Parameters**: Deflection, power degradation, cracks
- **Equipment**: Pressure chamber or mechanical load frame
- **Module File**: `protocols/mechanical/pvtp_030_static_load.py`
- **JSON Template**: `templates/protocols/PVTP-030.json`
- **UI Page**: `pages/protocol_execution/PVTP-030.py`

### PVTP-031: Mechanical Load Test (Dynamic)
- **Standard**: IEC 61215-1:2021 (MQT 17)
- **Description**: 1000 cycles of front/rear loading
- **Duration**: 2-3 days
- **Key Parameters**: Cumulative power degradation (≤5%), structural integrity
- **Equipment**: Dynamic load test machine
- **Module File**: `protocols/mechanical/pvtp_031_dynamic_load.py`
- **JSON Template**: `templates/protocols/PVTP-031.json`
- **UI Page**: `pages/protocol_execution/PVTP-031.py`

### PVTP-032: Hail Impact Test
- **Standard**: IEC 61215-1:2021 (MQT 15)
- **Description**: Ice ball impact at 23 m/s (25mm diameter)
- **Duration**: 1-2 hours
- **Key Parameters**: Glass breakage, cell cracks, power loss
- **Equipment**: Hail gun or pneumatic launcher
- **Module File**: `protocols/mechanical/pvtp_032_hail_impact.py`
- **JSON Template**: `templates/protocols/PVTP-032.json`
- **UI Page**: `pages/protocol_execution/PVTP-032.py`

### PVTP-033: Twist Test
- **Standard**: IEC 61215-1:2021 (MQT 08)
- **Description**: Module twist deformation
- **Duration**: 1 hour
- **Key Parameters**: Electrical performance during/after twist
- **Equipment**: Twist test fixture
- **Module File**: `protocols/mechanical/pvtp_033_twist.py`
- **JSON Template**: `templates/protocols/PVTP-033.json`
- **UI Page**: `pages/protocol_execution/PVTP-033.py`

### PVTP-034: Robustness of Terminations
- **Standard**: IEC 61215-1:2021 (MQT 07)
- **Description**: Cable and connector pull/twist test
- **Duration**: 1-2 hours
- **Key Parameters**: Cable retention, connector integrity, electrical continuity
- **Equipment**: Pull tester, torque tester
- **Module File**: `protocols/mechanical/pvtp_034_terminations.py`
- **JSON Template**: `templates/protocols/PVTP-034.json`
- **UI Page**: `pages/protocol_execution/PVTP-034.py`

### PVTP-035: Bypass Diode Function
- **Standard**: IEC 61215-1:2021 (MQT 09)
- **Description**: Bypass diode operational verification
- **Duration**: 1 hour
- **Key Parameters**: Forward voltage, reverse leakage, I-V bypass characteristics
- **Equipment**: Multimeter, I-V curve tracer with shading
- **Module File**: `protocols/mechanical/pvtp_035_diode_function.py`
- **JSON Template**: `templates/protocols/PVTP-035.json`
- **UI Page**: `pages/protocol_execution/PVTP-035.py`

### PVTP-036: Mounting System Stress
- **Standard**: IEC 61215-1:2021
- **Description**: Clamp and mounting point stress test
- **Duration**: 2 hours
- **Key Parameters**: Structural damage, stress cracks, electrical performance
- **Equipment**: Mounting clamps, load application device
- **Module File**: `protocols/mechanical/pvtp_036_mounting_stress.py`
- **JSON Template**: `templates/protocols/PVTP-036.json`
- **UI Page**: `pages/protocol_execution/PVTP-036.py`

### PVTP-037: Edge Seal Durability
- **Standard**: IEC 61215-1:2021
- **Description**: Edge seal integrity and peel strength
- **Duration**: 1-2 hours
- **Key Parameters**: Peel strength, edge seal width, adhesion
- **Equipment**: Peel tester, microscope
- **Module File**: `protocols/mechanical/pvtp_037_edge_seal.py`
- **JSON Template**: `templates/protocols/PVTP-037.json`
- **UI Page**: `pages/protocol_execution/PVTP-037.py`

---

## 5. Degradation Analysis (6 Protocols)

### PVTP-038: PID Testing (Potential Induced Degradation)
- **Standard**: IEC 62804-1:2015
- **Description**: High voltage stress test (-1000V or +1000V, 85°C/85%RH)
- **Duration**: 96-192 hours
- **Key Parameters**: Power degradation, recovery potential
- **Equipment**: PID chamber, high voltage supply
- **Module File**: `protocols/degradation/pvtp_038_pid.py`
- **JSON Template**: `templates/protocols/PVTP-038.json`
- **UI Page**: `pages/protocol_execution/PVTP-038.py`

### PVTP-039: LID Testing (Light Induced Degradation)
- **Standard**: IEC 61215-1:2021
- **Description**: Initial light soaking (5-10 kWh/m²)
- **Duration**: 2-3 days
- **Key Parameters**: Initial degradation, stabilization power
- **Equipment**: Light soaking chamber or solar simulator
- **Module File**: `protocols/degradation/pvtp_039_lid.py`
- **JSON Template**: `templates/protocols/PVTP-039.json`
- **UI Page**: `pages/protocol_execution/PVTP-039.py`

### PVTP-040: LeTID Testing (Light and elevated Temperature Induced Degradation)
- **Standard**: IEC TS 60904-13:2018
- **Description**: Extended light soaking at 50-75°C
- **Duration**: 7-14 days
- **Key Parameters**: Degradation curve, recovery, final stabilized power
- **Equipment**: LeTID chamber with temperature control
- **Module File**: `protocols/degradation/pvtp_040_letid.py`
- **JSON Template**: `templates/protocols/PVTP-040.json`
- **UI Page**: `pages/protocol_execution/PVTP-040.py`

### PVTP-041: UV Degradation (Long-term)
- **Standard**: IEC 61345:1998
- **Description**: Extended UV exposure beyond preconditioning
- **Duration**: 30-60 days
- **Key Parameters**: Transmittance loss, yellowing, power degradation
- **Equipment**: UV chamber with spectral control
- **Module File**: `protocols/degradation/pvtp_041_uv_degradation.py`
- **JSON Template**: `templates/protocols/PVTP-041.json`
- **UI Page**: `pages/protocol_execution/PVTP-041.py`

### PVTP-042: Thermal Stress Screening
- **Standard**: Custom / Industry practice
- **Description**: Accelerated thermal stress to identify weak modules
- **Duration**: 5-7 days
- **Key Parameters**: Infant mortality detection, early failure identification
- **Equipment**: Thermal cycling chamber with rapid ramp rates
- **Module File**: `protocols/degradation/pvtp_042_thermal_stress_screening.py`
- **JSON Template**: `templates/protocols/PVTP-042.json`
- **UI Page**: `pages/protocol_execution/PVTP-042.py`

### PVTP-043: Reverse Current Overstress
- **Standard**: IEC 61215-1:2021
- **Description**: Reverse current stress on module
- **Duration**: 1-2 hours
- **Key Parameters**: Hot spot formation, cell damage threshold
- **Equipment**: Reverse current source, IR camera
- **Module File**: `protocols/degradation/pvtp_043_reverse_current.py`
- **JSON Template**: `templates/protocols/PVTP-043.json`
- **UI Page**: `pages/protocol_execution/PVTP-043.py`

---

## 6. Quality Control & Inspection (5 Protocols)

### PVTP-044: Visual Inspection
- **Standard**: IEC 61215-1:2021 (MQT 01), IEC 61730-2:2016
- **Description**: Comprehensive visual inspection checklist
- **Duration**: 30-60 minutes per module
- **Key Parameters**: Cracks, delamination, discoloration, bubbles, corrosion
- **Equipment**: Visual inspection aids, microscope, lighting
- **Module File**: `protocols/qc/pvtp_044_visual_inspection.py`
- **JSON Template**: `templates/protocols/PVTP-044.json`
- **UI Page**: `pages/protocol_execution/PVTP-044.py`

### PVTP-045: Electroluminescence (EL) Imaging
- **Standard**: IEC TS 60904-13:2018
- **Description**: EL imaging for cell defects and cracks
- **Duration**: 15-30 minutes per module
- **Key Parameters**: Crack detection, cell uniformity, inactive areas, finger interruptions
- **Equipment**: EL camera, dark room, forward bias supply
- **Module File**: `protocols/qc/pvtp_045_el_imaging.py`
- **JSON Template**: `templates/protocols/PVTP-045.json`
- **UI Page**: `pages/protocol_execution/PVTP-045.py`

### PVTP-046: Infrared (IR) Thermography
- **Standard**: IEC 62446-3:2017
- **Description**: Thermal imaging under load
- **Duration**: 30-60 minutes
- **Key Parameters**: Hot spots, cell temperature uniformity, defect detection
- **Equipment**: IR camera, solar simulator or outdoor setup
- **Module File**: `protocols/qc/pvtp_046_ir_thermography.py`
- **JSON Template**: `templates/protocols/PVTP-046.json`
- **UI Page**: `pages/protocol_execution/PVTP-046.py`

### PVTP-047: Flash Test
- **Standard**: IEC 60904-1:2020
- **Description**: Production-line flash testing
- **Duration**: 5-10 seconds per module
- **Key Parameters**: Quick power measurement, binning classification
- **Equipment**: Flash tester (pulsed solar simulator)
- **Module File**: `protocols/qc/pvtp_047_flash_test.py`
- **JSON Template**: `templates/protocols/PVTP-047.json`
- **UI Page**: `pages/protocol_execution/PVTP-047.py`

### PVTP-048: Cell Crack Detection
- **Standard**: IEC TS 60904-13:2018
- **Description**: Advanced crack detection and classification
- **Duration**: 20-40 minutes
- **Key Parameters**: Crack length, type (vertical/horizontal), severity, impact on power
- **Equipment**: EL imaging system, image analysis software
- **Module File**: `protocols/qc/pvtp_048_crack_detection.py`
- **JSON Template**: `templates/protocols/PVTP-048.json`
- **UI Page**: `pages/protocol_execution/PVTP-048.py`

---

## 7. Specialty Testing (4 Protocols)

### PVTP-049: Backsheet Adhesion Test
- **Standard**: IEC 62788-1-6:2017
- **Description**: Peel test for backsheet adhesion
- **Duration**: 1-2 hours
- **Key Parameters**: Peel strength (N/cm), failure mode
- **Equipment**: Universal testing machine with peel fixtures
- **Module File**: `protocols/specialty/pvtp_049_backsheet_adhesion.py`
- **JSON Template**: `templates/protocols/PVTP-049.json`
- **UI Page**: `pages/protocol_execution/PVTP-049.py`

### PVTP-050: Glass Adhesion Test
- **Standard**: IEC 62788-1-2:2016
- **Description**: Encapsulant to glass adhesion
- **Duration**: 1-2 hours
- **Key Parameters**: Peel strength, cohesive vs. adhesive failure
- **Equipment**: Peel tester, sample preparation tools
- **Module File**: `protocols/specialty/pvtp_050_glass_adhesion.py`
- **JSON Template**: `templates/protocols/PVTP-050.json`
- **UI Page**: `pages/protocol_execution/PVTP-050.py`

### PVTP-051: Water Vapor Transmission Rate (WVTR)
- **Standard**: ASTM E96, ISO 15106-3
- **Description**: Backsheet and edge seal WVTR measurement
- **Duration**: 7-14 days
- **Key Parameters**: WVTR (g/m²/day), barrier performance
- **Equipment**: WVTR test chamber, analytical balance
- **Module File**: `protocols/specialty/pvtp_051_wvtr.py`
- **JSON Template**: `templates/protocols/PVTP-051.json`
- **UI Page**: `pages/protocol_execution/PVTP-051.py`

### PVTP-052: Partial Shading Analysis
- **Standard**: IEC 61853-2:2016
- **Description**: Performance under various shading patterns
- **Duration**: 2-3 hours
- **Key Parameters**: Power loss patterns, bypass diode effectiveness, shading tolerance
- **Equipment**: Solar simulator, programmable shading device
- **Module File**: `protocols/specialty/pvtp_052_partial_shading.py`
- **JSON Template**: `templates/protocols/PVTP-052.json`
- **UI Page**: `pages/protocol_execution/PVTP-052.py`

---

## 8. Advanced Diagnostics (2 Protocols)

### PVTP-053: Comprehensive Module Analysis
- **Standard**: Multiple (IEC 61215, IEC 61730, etc.)
- **Description**: Full suite of electrical, thermal, and optical characterization
- **Duration**: 1-2 weeks
- **Key Parameters**: Complete module characterization for R&D or failure analysis
- **Equipment**: Full laboratory setup
- **Module File**: `protocols/advanced/pvtp_053_comprehensive.py`
- **JSON Template**: `templates/protocols/PVTP-053.json`
- **UI Page**: `pages/protocol_execution/PVTP-053.py`

### PVTP-054: IEC 61215 Complete Type Approval
- **Standard**: IEC 61215-1:2021 + IEC 61215-2
- **Description**: Full type approval testing for module certification
- **Duration**: 3-4 months
- **Key Parameters**: All design qualification tests per IEC 61215
- **Equipment**: Full accredited testing laboratory
- **Module File**: `protocols/advanced/pvtp_054_type_approval.py`
- **JSON Template**: `templates/protocols/PVTP-054.json`
- **UI Page**: `pages/protocol_execution/PVTP-054.py`

---

## Protocol Selection Guidelines

### By Standard Requirements

| Standard | Required Protocols |
|----------|-------------------|
| **IEC 61215** (Module Design Qualification) | PVTP-001, 010, 011, 015, 018, 019, 020, 021, 030, 031, 032, 033, 034, 035, 044 |
| **IEC 61730** (Module Safety) | PVTP-010, 011, 012, 013, 014, 016, 017, 044 |
| **IEC 62804** (PID Testing) | PVTP-038 |
| **IEC 61853** (Module Performance) | PVTP-001, 002, 003, 004, 052 |
| **IEC 62716** (Ammonia Corrosion) | PVTP-024 |

### By Test Duration

| Duration | Protocols |
|----------|-----------|
| **< 1 day** | PVTP-001 through 017, 028, 030, 032-037, 043-048 |
| **1-7 days** | PVTP-021, 023, 024, 027, 039, 042 |
| **1-4 weeks** | PVTP-022, 040, 041, 053 |
| **1-2 months** | PVTP-020, 025 |
| **2-4 months** | PVTP-018, 019, 054 |

### By Equipment Requirements

| Equipment Category | Protocols |
|-------------------|-----------|
| **Solar Simulator** | PVTP-001, 003, 004, 005, 007, 008, 015, 047, 052 |
| **Climate Chamber** | PVTP-018, 019, 020, 025, 026, 027, 028 |
| **UV Chamber** | PVTP-021, 022, 041 |
| **Mechanical Testing** | PVTP-030, 031, 032, 033, 034, 036, 037, 049, 050 |
| **Electrical Testing** | PVTP-010, 011, 012, 013, 014, 017 |
| **Imaging Equipment** | PVTP-045, 046, 048 |
| **Specialized** | PVTP-006, 023, 024, 038, 039, 040, 051, 053, 054 |

---

## Protocol Dependencies

Some protocols have prerequisites or recommended sequences:

1. **Initial characterization** should include:
   - PVTP-044 (Visual Inspection)
   - PVTP-001 (STC Power)
   - PVTP-045 (EL Imaging)

2. **Before environmental testing**:
   - Complete initial characterization
   - PVTP-010 (Dry Insulation)

3. **After environmental testing**:
   - Repeat PVTP-001, 010, 044, 045
   - Calculate degradation

4. **LID before other performance tests**:
   - PVTP-039 (LID) or PVTP-040 (LeTID)
   - Then performance characterization

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-12
**Total Protocols**: 54
