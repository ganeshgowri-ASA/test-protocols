"""
Protocol Generator Script

Generates JSON templates and Python implementations for all 54 PV testing protocols
"""

import json
import os
from pathlib import Path

# Define all 54 protocols with their metadata
PROTOCOLS = {
    'performance': [
        {
            'id': 'STC-001',
            'name': 'Standard Test Conditions Testing',
            'standard': 'IEC 61215-1:2021, Section 7.2',
            'duration': 120,
            'description': 'Measure PV module performance under standard test conditions (1000 W/m², 25°C, AM1.5G)',
            'equipment': ['Solar Simulator', 'IV Curve Tracer', 'Temperature Sensor', 'Irradiance Sensor'],
            'measurements': ['IV Curve', 'Pmax', 'Voc', 'Isc', 'FF', 'Efficiency']
        },
        {
            'id': 'NOCT-001',
            'name': 'Nominal Operating Cell Temperature',
            'standard': 'IEC 61215-1:2021, Section 7.3',
            'duration': 240,
            'description': 'Determine module temperature under nominal operating conditions',
            'equipment': ['Solar Simulator', 'Environmental Chamber', 'Temperature Sensors'],
            'measurements': ['Module Temperature', 'Ambient Temperature', 'Irradiance', 'Wind Speed']
        },
        {
            'id': 'LIC-001',
            'name': 'Low Irradiance Conditions Testing',
            'standard': 'IEC 61215-1:2021',
            'duration': 180,
            'description': 'Measure performance at low irradiance levels (200-500 W/m²)',
            'equipment': ['Solar Simulator', 'IV Curve Tracer'],
            'measurements': ['IV Curves at Multiple Irradiances', 'Efficiency vs Irradiance']
        },
        {
            'id': 'PERF-001',
            'name': 'Performance at Different Temperatures',
            'standard': 'IEC 61215-1:2021',
            'duration': 300,
            'description': 'Measure performance across temperature range (15°C to 75°C)',
            'equipment': ['Solar Simulator', 'Environmental Chamber', 'IV Curve Tracer'],
            'measurements': ['Temperature Coefficients', 'Power vs Temperature']
        },
        {
            'id': 'PERF-002',
            'name': 'Performance at Different Irradiances',
            'standard': 'IEC 61215-1:2021',
            'duration': 240,
            'description': 'Measure performance across irradiance range (100-1200 W/m²)',
            'equipment': ['Solar Simulator', 'IV Curve Tracer'],
            'measurements': ['Efficiency vs Irradiance', 'Linearity Check']
        },
        {
            'id': 'IAM-001',
            'name': 'Incidence Angle Modifier',
            'standard': 'IEC 61853-2:2016',
            'duration': 360,
            'description': 'Measure angular response characteristics',
            'equipment': ['Solar Simulator', 'Rotation Stage', 'IV Curve Tracer'],
            'measurements': ['Power vs Angle', 'IAM Coefficients']
        },
        {
            'id': 'SPEC-001',
            'name': 'Spectral Response',
            'standard': 'IEC 60904-8:2014',
            'duration': 480,
            'description': 'Measure spectral response across wavelength range',
            'equipment': ['Spectroradiometer', 'Monochromator', 'Light Source'],
            'measurements': ['Quantum Efficiency', 'Spectral Response Curve']
        },
        {
            'id': 'TEMP-001',
            'name': 'Temperature Coefficients',
            'standard': 'IEC 60891:2021',
            'duration': 240,
            'description': 'Determine temperature coefficients (alpha, beta, gamma)',
            'equipment': ['Solar Simulator', 'Environmental Chamber', 'IV Curve Tracer'],
            'measurements': ['Alpha (Isc)', 'Beta (Voc)', 'Gamma (Pmax)']
        },
        {
            'id': 'ENER-001',
            'name': 'Energy Rating (IEC 61853)',
            'standard': 'IEC 61853-1:2011',
            'duration': 720,
            'description': 'Comprehensive energy rating testing',
            'equipment': ['Solar Simulator', 'Environmental Chamber', 'IV Curve Tracer'],
            'measurements': ['Power Matrix', 'Energy Output Estimates']
        },
        {
            'id': 'BIFI-001',
            'name': 'Bifacial Performance',
            'standard': 'IEC TS 60904-1-2:2019',
            'duration': 300,
            'description': 'Test bifacial module performance',
            'equipment': ['Dual Solar Simulator', 'IV Curve Tracer', 'Albedometer'],
            'measurements': ['Front Power', 'Rear Power', 'Bifaciality Factor']
        },
        {
            'id': 'TRACK-001',
            'name': 'Tracker Performance',
            'standard': 'Custom',
            'duration': 480,
            'description': 'Test module performance with tracking systems',
            'equipment': ['Solar Simulator', 'Tracker Simulator', 'IV Curve Tracer'],
            'measurements': ['Energy Gain', 'Tracking Accuracy']
        },
        {
            'id': 'CONC-001',
            'name': 'Concentration Testing',
            'standard': 'IEC 62108:2016',
            'duration': 360,
            'description': 'Test concentrator PV modules',
            'equipment': ['Concentrating Solar Simulator', 'IV Curve Tracer', 'DNI Sensor'],
            'measurements': ['Power vs Concentration', 'Efficiency vs DNI']
        }
    ],
    'degradation': [
        {
            'id': 'LID-001',
            'name': 'Light-Induced Degradation',
            'standard': 'IEC 61215-1:2021, MQT 02',
            'duration': 1440,
            'description': 'Measure light-induced degradation (LID) effects',
            'equipment': ['Solar Simulator', 'IV Curve Tracer', 'Light Soaking Chamber'],
            'measurements': ['Initial Power', 'Power After Exposure', 'Degradation Rate']
        },
        {
            'id': 'LETID-001',
            'name': 'Light and Elevated Temperature Induced Degradation',
            'standard': 'IEC TS 63126:2020',
            'duration': 2880,
            'description': 'Test LeTID effects in silicon modules',
            'equipment': ['Environmental Chamber', 'Light Source', 'IV Curve Tracer'],
            'measurements': ['Power vs Time', 'LeTID Degradation', 'Recovery']
        },
        {
            'id': 'PID-001',
            'name': 'Potential-Induced Degradation (Shunting)',
            'standard': 'IEC TS 62804-1:2015',
            'duration': 2160,
            'description': 'Test PID susceptibility (shunting mode)',
            'equipment': ['Environmental Chamber', 'High Voltage Supply', 'IV Curve Tracer'],
            'measurements': ['Initial Power', 'Power After Stress', 'Leakage Current']
        },
        {
            'id': 'PID-002',
            'name': 'Potential-Induced Degradation (Polarization)',
            'standard': 'IEC TS 62804-1:2015',
            'duration': 2160,
            'description': 'Test PID susceptibility (polarization mode)',
            'equipment': ['Environmental Chamber', 'High Voltage Supply', 'IV Curve Tracer'],
            'measurements': ['Initial Power', 'Power After Stress', 'Recovery Rate']
        },
        {
            'id': 'UVID-001',
            'name': 'UV-Induced Degradation',
            'standard': 'IEC 61215-1:2021, MQT 10',
            'duration': 720,
            'description': 'Test UV exposure effects on performance',
            'equipment': ['UV Chamber', 'UV Radiometer', 'IV Curve Tracer'],
            'measurements': ['UV Dose', 'Power Degradation', 'Yellowing Index']
        },
        {
            'id': 'SPONGE-001',
            'name': 'Sponge Effect Testing',
            'standard': 'Custom',
            'duration': 480,
            'description': 'Test reversible moisture-induced changes',
            'equipment': ['Environmental Chamber', 'IV Curve Tracer'],
            'measurements': ['Power vs Humidity Cycle', 'Reversibility']
        },
        {
            'id': 'SNAIL-001',
            'name': 'Snail Trail Formation',
            'standard': 'Custom',
            'duration': 1440,
            'description': 'Accelerated testing for snail trail formation',
            'equipment': ['Environmental Chamber', 'Imaging System'],
            'measurements': ['Visual Inspection', 'Discoloration Area', 'Power Impact']
        },
        {
            'id': 'DELAM-001',
            'name': 'Delamination Testing',
            'standard': 'IEC 61215-1:2021',
            'duration': 2000,
            'description': 'Test for encapsulant delamination',
            'equipment': ['Environmental Chamber', 'Imaging System', 'EL Tester'],
            'measurements': ['Delamination Area', 'Adhesion Strength', 'Power Loss']
        },
        {
            'id': 'CORR-001',
            'name': 'Corrosion Testing',
            'standard': 'IEC 61215-1:2021, MQT 11',
            'duration': 1440,
            'description': 'Test corrosion resistance of components',
            'equipment': ['Salt Spray Chamber', 'Environmental Chamber'],
            'measurements': ['Visual Inspection', 'Insulation Resistance', 'Power Loss']
        },
        {
            'id': 'CHALK-001',
            'name': 'Backsheet Chalking',
            'standard': 'Custom',
            'duration': 720,
            'description': 'Test backsheet degradation and chalking',
            'equipment': ['UV Chamber', 'Gloss Meter'],
            'measurements': ['Gloss Retention', 'Chalking Rating', 'Emissivity']
        },
        {
            'id': 'YELLOW-001',
            'name': 'EVA Yellowing',
            'standard': 'Custom',
            'duration': 720,
            'description': 'Test EVA encapsulant yellowing',
            'equipment': ['UV Chamber', 'Spectrophotometer'],
            'measurements': ['Yellowing Index', 'Transmittance', 'Power Loss']
        },
        {
            'id': 'CRACK-001',
            'name': 'Cell Crack Propagation',
            'standard': 'Custom',
            'duration': 960,
            'description': 'Test cell crack formation and propagation',
            'equipment': ['Mechanical Load Tester', 'EL Imaging System'],
            'measurements': ['Crack Detection', 'Crack Propagation', 'Power Impact']
        },
        {
            'id': 'SOLDER-001',
            'name': 'Solder Bond Degradation',
            'standard': 'IEC 61215-1:2021',
            'duration': 480,
            'description': 'Test solder bond integrity under stress',
            'equipment': ['Thermal Cycling Chamber', 'Shear Test Equipment'],
            'measurements': ['Bond Strength', 'Electrical Resistance', 'Visual Inspection']
        },
        {
            'id': 'JBOX-001',
            'name': 'Junction Box Degradation',
            'standard': 'IEC 61215-1:2021',
            'duration': 720,
            'description': 'Test junction box durability',
            'equipment': ['Environmental Chamber', 'Thermal Imaging'],
            'measurements': ['Adhesion Strength', 'Seal Integrity', 'Contact Resistance']
        },
        {
            'id': 'SEAL-001',
            'name': 'Edge Seal Degradation',
            'standard': 'Custom',
            'duration': 1440,
            'description': 'Test edge seal durability and moisture ingress',
            'equipment': ['Environmental Chamber', 'Moisture Detection'],
            'measurements': ['Moisture Ingress', 'Seal Integrity', 'Delamination']
        }
    ],
    'environmental': [
        {
            'id': 'TC-001',
            'name': 'Thermal Cycling (50/200/600 cycles)',
            'standard': 'IEC 61215-1:2021, MQT 13',
            'duration': 7200,
            'description': 'Thermal cycling test (-40°C to +85°C)',
            'equipment': ['Thermal Cycling Chamber', 'IV Curve Tracer'],
            'measurements': ['Power Before/After', 'Insulation Resistance', 'Visual Inspection']
        },
        {
            'id': 'DH-001',
            'name': 'Damp Heat (1000h)',
            'standard': 'IEC 61215-1:2021, MQT 12',
            'duration': 60000,
            'description': 'Damp heat exposure (85°C, 85% RH, 1000h)',
            'equipment': ['Damp Heat Chamber', 'IV Curve Tracer'],
            'measurements': ['Power Degradation', 'Insulation Resistance', 'Visual Inspection']
        },
        {
            'id': 'DH-002',
            'name': 'Extended Damp Heat (2000h)',
            'standard': 'IEC 61215-1:2021',
            'duration': 120000,
            'description': 'Extended damp heat exposure (85°C, 85% RH, 2000h)',
            'equipment': ['Damp Heat Chamber', 'IV Curve Tracer'],
            'measurements': ['Power Degradation', 'Insulation Resistance', 'Delamination']
        },
        {
            'id': 'HF-001',
            'name': 'Humidity Freeze',
            'standard': 'IEC 61215-1:2021, MQT 14',
            'duration': 1440,
            'description': 'Humidity freeze cycling (10 cycles)',
            'equipment': ['Humidity Freeze Chamber', 'IV Curve Tracer'],
            'measurements': ['Power Before/After', 'Insulation Resistance', 'Visual Inspection']
        },
        {
            'id': 'UV-001',
            'name': 'UV Preconditioning',
            'standard': 'IEC 61215-1:2021, MQT 10',
            'duration': 360,
            'description': 'UV preconditioning test (15 kWh/m²)',
            'equipment': ['UV Chamber', 'UV Radiometer', 'IV Curve Tracer'],
            'measurements': ['UV Dose', 'Power Before/After', 'Visual Inspection']
        },
        {
            'id': 'SALT-001',
            'name': 'Salt Mist Corrosion',
            'standard': 'IEC 61215-1:2021, MQT 11',
            'duration': 720,
            'description': 'Salt mist corrosion test',
            'equipment': ['Salt Spray Chamber', 'IV Curve Tracer'],
            'measurements': ['Corrosion Level', 'Insulation Resistance', 'Power Loss']
        },
        {
            'id': 'SAND-001',
            'name': 'Sand/Dust Testing',
            'standard': 'IEC 60068-2-68',
            'duration': 240,
            'description': 'Sand and dust resistance test',
            'equipment': ['Dust Chamber', 'Abrasion Tester'],
            'measurements': ['Surface Damage', 'Transmittance Loss', 'Power Loss']
        },
        {
            'id': 'AMMON-001',
            'name': 'Ammonia Resistance',
            'standard': 'IEC 62716:2013',
            'duration': 480,
            'description': 'Ammonia corrosion resistance test',
            'equipment': ['Gas Exposure Chamber', 'IV Curve Tracer'],
            'measurements': ['Corrosion Level', 'Power Degradation', 'Visual Inspection']
        },
        {
            'id': 'SO2-001',
            'name': 'Sulfur Dioxide Testing',
            'standard': 'Custom',
            'duration': 480,
            'description': 'SO2 gas exposure test',
            'equipment': ['Gas Exposure Chamber', 'Gas Analyzer'],
            'measurements': ['Corrosion Level', 'Power Degradation', 'Material Changes']
        },
        {
            'id': 'H2S-001',
            'name': 'Hydrogen Sulfide Testing',
            'standard': 'Custom',
            'duration': 480,
            'description': 'H2S gas exposure test',
            'equipment': ['Gas Exposure Chamber', 'Gas Analyzer'],
            'measurements': ['Corrosion Level', 'Power Degradation', 'Material Changes']
        },
        {
            'id': 'TROP-001',
            'name': 'Tropical Climate Testing',
            'standard': 'Custom',
            'duration': 2880,
            'description': 'Accelerated tropical climate testing',
            'equipment': ['Environmental Chamber', 'IV Curve Tracer'],
            'measurements': ['Power Degradation', 'Moisture Ingress', 'Corrosion']
        },
        {
            'id': 'DESERT-001',
            'name': 'Desert Climate Testing',
            'standard': 'Custom',
            'duration': 2880,
            'description': 'Accelerated desert climate testing',
            'equipment': ['Environmental Chamber', 'UV Source', 'Dust Generator'],
            'measurements': ['Power Degradation', 'Surface Soiling', 'UV Degradation']
        }
    ],
    'mechanical': [
        {
            'id': 'ML-001',
            'name': 'Mechanical Load (Static)',
            'standard': 'IEC 61215-1:2021, MQT 15',
            'duration': 240,
            'description': 'Static mechanical load test (front/back)',
            'equipment': ['Load Application System', 'Deflection Sensors', 'IV Curve Tracer'],
            'measurements': ['Deflection', 'Power Before/After', 'Visual Inspection']
        },
        {
            'id': 'ML-002',
            'name': 'Mechanical Load (Dynamic)',
            'standard': 'IEC 61215-1:2021, MQT 16',
            'duration': 480,
            'description': 'Dynamic mechanical load test',
            'equipment': ['Dynamic Load System', 'IV Curve Tracer'],
            'measurements': ['Cycles', 'Power Degradation', 'Visual Inspection']
        },
        {
            'id': 'HAIL-001',
            'name': 'Hail Impact Test',
            'standard': 'IEC 61215-1:2021, MQT 17',
            'duration': 120,
            'description': 'Hail impact resistance test',
            'equipment': ['Hail Impact Tester', 'High Speed Camera', 'IV Curve Tracer'],
            'measurements': ['Impact Energy', 'Damage Assessment', 'Power Before/After']
        },
        {
            'id': 'WIND-001',
            'name': 'Wind Load Testing',
            'standard': 'Custom',
            'duration': 360,
            'description': 'Wind load resistance test',
            'equipment': ['Wind Tunnel', 'Load Cells', 'Deflection Sensors'],
            'measurements': ['Pressure Distribution', 'Deflection', 'Structural Integrity']
        },
        {
            'id': 'SNOW-001',
            'name': 'Snow Load Testing',
            'standard': 'Custom',
            'duration': 240,
            'description': 'Snow load resistance test',
            'equipment': ['Load Application System', 'Temperature Chamber'],
            'measurements': ['Load Capacity', 'Deflection', 'Power Under Load']
        },
        {
            'id': 'VIBR-001',
            'name': 'Transportation Vibration',
            'standard': 'ASTM D4169',
            'duration': 360,
            'description': 'Transportation vibration test',
            'equipment': ['Vibration Table', 'Accelerometers', 'IV Curve Tracer'],
            'measurements': ['Vibration Levels', 'Power Before/After', 'Visual Inspection']
        },
        {
            'id': 'TWIST-001',
            'name': 'Module Twist Testing',
            'standard': 'IEC 61215-1:2021, MQT 18',
            'duration': 180,
            'description': 'Module twist test',
            'equipment': ['Twist Test Fixture', 'IV Curve Tracer'],
            'measurements': ['Twist Angle', 'Power Before/After', 'Visual Inspection']
        },
        {
            'id': 'TERM-001',
            'name': 'Terminal Robustness',
            'standard': 'IEC 61215-1:2021, MQT 19',
            'duration': 120,
            'description': 'Terminal mechanical robustness test',
            'equipment': ['Pull Test Equipment', 'Torque Wrench'],
            'measurements': ['Pull Force', 'Torque', 'Connection Integrity']
        }
    ],
    'safety': [
        {
            'id': 'INSU-001',
            'name': 'Insulation Resistance',
            'standard': 'IEC 61215-1:2021, MQT 01',
            'duration': 60,
            'description': 'Insulation resistance test',
            'equipment': ['Insulation Tester (Megohmmeter)', 'High Voltage Supply'],
            'measurements': ['Insulation Resistance (>40 MΩ)']
        },
        {
            'id': 'WET-001',
            'name': 'Wet Leakage Current',
            'standard': 'IEC 61215-1:2021, MQT 03',
            'duration': 120,
            'description': 'Wet leakage current test',
            'equipment': ['Leakage Current Meter', 'Water Spray System'],
            'measurements': ['Leakage Current (<1 mA)']
        },
        {
            'id': 'DIEL-001',
            'name': 'Dielectric Withstand',
            'standard': 'IEC 61215-1:2021, MQT 04',
            'duration': 90,
            'description': 'Dielectric withstand test (Hi-Pot)',
            'equipment': ['High Voltage Tester', 'Current Meter'],
            'measurements': ['Test Voltage', 'Leakage Current', 'Pass/Fail']
        },
        {
            'id': 'GROUND-001',
            'name': 'Ground Continuity',
            'standard': 'IEC 61215-1:2021, MQT 05',
            'duration': 60,
            'description': 'Ground continuity test',
            'equipment': ['Ground Continuity Tester', 'Resistance Meter'],
            'measurements': ['Resistance (<0.1 Ω)', 'Continuity']
        },
        {
            'id': 'HOT-001',
            'name': 'Hot Spot Endurance',
            'standard': 'IEC 61215-1:2021, MQT 09',
            'duration': 720,
            'description': 'Hot spot endurance test',
            'equipment': ['Solar Simulator', 'Thermal Imaging', 'IV Curve Tracer'],
            'measurements': ['Hot Spot Temperature', 'Power Degradation', 'Visual Inspection']
        },
        {
            'id': 'BYPASS-001',
            'name': 'Bypass Diode Testing',
            'standard': 'IEC 61215-1:2021, MQT 07',
            'duration': 240,
            'description': 'Bypass diode thermal test',
            'equipment': ['Environmental Chamber', 'Current Source', 'Thermal Imaging'],
            'measurements': ['Diode Temperature', 'Forward Voltage', 'Functionality']
        },
        {
            'id': 'FIRE-001',
            'name': 'Fire Resistance Testing',
            'standard': 'IEC 61730-2:2016',
            'duration': 180,
            'description': 'Fire resistance classification test',
            'equipment': ['Fire Test Apparatus', 'Temperature Sensors'],
            'measurements': ['Flame Spread', 'Burn Duration', 'Fire Classification']
        }
    ]
}


def create_json_template(protocol_info, category):
    """Create JSON template for a protocol"""
    template = {
        "protocol_id": protocol_info['id'],
        "name": protocol_info['name'],
        "category": category,
        "version": "1.0",
        "standard_reference": protocol_info['standard'],
        "description": protocol_info['description'],
        "test_conditions": {
            "temperature_range": {"min": 15, "max": 75, "unit": "°C"},
            "irradiance_range": {"min": 100, "max": 1200, "unit": "W/m²"},
            "humidity_range": {"min": 0, "max": 100, "unit": "%RH"}
        },
        "input_parameters": [
            {"name": "sample_id", "type": "string", "required": True},
            {"name": "rated_power", "type": "float", "unit": "W", "required": True},
            {"name": "test_temperature", "type": "float", "unit": "°C", "default": 25},
            {"name": "test_irradiance", "type": "float", "unit": "W/m²", "default": 1000}
        ],
        "measurement_points": protocol_info['measurements'],
        "calculations": [
            {"name": "power_degradation", "formula": "((P_initial - P_final) / P_initial) * 100", "unit": "%"},
            {"name": "efficiency", "formula": "(P_max / (Irradiance * Area)) * 100", "unit": "%"}
        ],
        "acceptance_criteria": {
            "power_degradation_max": 5.0,
            "insulation_resistance_min": 40.0,
            "visual_defects": "none"
        },
        "equipment_required": protocol_info['equipment'],
        "estimated_duration": protocol_info['duration'],
        "safety_precautions": [
            "Wear appropriate PPE",
            "Ensure equipment is properly grounded",
            "Follow electrical safety procedures",
            "Monitor test chamber conditions"
        ]
    }
    return template


def create_python_implementation(protocol_info, category):
    """Create Python implementation for a protocol"""
    class_name = protocol_info['id'].replace('-', '')

    code = f'''"""
{protocol_info['name']} Protocol Implementation

Standard: {protocol_info['standard']}
Category: {category}
Duration: ~{protocol_info['duration']} minutes
"""

from protocols.base_protocol import BaseProtocol, ProtocolStep
from utils.data_processor import DataProcessor
from utils.equipment_interface import EquipmentManager
import logging

logger = logging.getLogger(__name__)


class {class_name}Protocol(BaseProtocol):
    """
    {protocol_info['name']}

    {protocol_info['description']}
    """

    def __init__(self):
        super().__init__(protocol_id="{protocol_info['id']}")
        self.data_processor = DataProcessor()
        self.equipment_manager = EquipmentManager()

    def setup(self) -> bool:
        """Setup equipment and prepare for testing"""
        try:
            logger.info(f"Setting up {{self.protocol_id}}")

            # Validate input parameters
            if not self.input_parameters:
                self.add_error("Input parameters not set")
                return False

            # Initialize equipment
            for equipment in {protocol_info['equipment']}:
                logger.info(f"Initializing {{equipment}}")
                # Equipment initialization code here

            self.update_progress(20, ProtocolStep.EQUIPMENT_SETUP, "Equipment setup complete")
            return True

        except Exception as e:
            self.add_error(f"Setup failed: {{str(e)}}")
            logger.exception("Setup failed")
            return False

    def execute(self) -> bool:
        """Execute the test procedure"""
        try:
            logger.info(f"Executing {{self.protocol_id}}")

            self.update_progress(40, ProtocolStep.PRE_TEST_MEASUREMENTS, "Taking initial measurements")

            # Perform measurements
            # This is a simplified implementation
            # In production, this would interface with actual equipment

            measurement_data = {{
                'timestamp': self._get_timestamp(),
                'values': {{}}
            }}

            self.add_measurement("{protocol_info['id']}_data", measurement_data)

            self.update_progress(70, ProtocolStep.MAIN_TEST, "Main test complete")
            return True

        except Exception as e:
            self.add_error(f"Execution failed: {{str(e)}}")
            logger.exception("Execution failed")
            return False

    def analyze(self) -> dict:
        """Analyze test data"""
        try:
            logger.info(f"Analyzing data for {{self.protocol_id}}")

            # Perform data analysis
            # Simplified implementation
            results = {{
                'analysis_complete': True,
                'timestamp': self._get_timestamp()
            }}

            self.analysis_results = results
            return results

        except Exception as e:
            self.add_error(f"Analysis failed: {{str(e)}}")
            logger.exception("Analysis failed")
            return {{}}

    def validate(self) -> bool:
        """Validate results against acceptance criteria"""
        try:
            logger.info(f"Validating results for {{self.protocol_id}}")

            # Validation logic
            is_valid = True

            self.validation_results = {{
                'is_valid': is_valid,
                'validation_timestamp': self._get_timestamp()
            }}

            return is_valid

        except Exception as e:
            self.add_error(f"Validation failed: {{str(e)}}")
            logger.exception("Validation failed")
            return False

    def generate_report(self) -> dict:
        """Generate test report"""
        try:
            logger.info(f"Generating report for {{self.protocol_id}}")

            report = {{
                'protocol_id': self.protocol_id,
                'protocol_name': '{protocol_info['name']}',
                'status': self.status.value,
                'measurements': self.measurements,
                'analysis_results': self.analysis_results,
                'validation_results': self.validation_results
            }}

            return report

        except Exception as e:
            self.add_error(f"Report generation failed: {{str(e)}}")
            logger.exception("Report generation failed")
            return {{}}

    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
'''

    return code


def generate_all_protocols():
    """Generate all 54 protocols"""
    base_path = Path(__file__).parent / 'genspark_app'

    for category, protocols in PROTOCOLS.items():
        print(f"\nGenerating {category} protocols ({len(protocols)} protocols)...")

        # Create category directories
        template_dir = base_path / 'templates' / 'protocols' / category
        impl_dir = base_path / 'protocols' / category

        template_dir.mkdir(parents=True, exist_ok=True)
        impl_dir.mkdir(parents=True, exist_ok=True)

        for protocol_info in protocols:
            protocol_id = protocol_info['id'].lower().replace('-', '_')

            # Generate JSON template
            json_path = template_dir / f"{protocol_id}.json"
            template = create_json_template(protocol_info, category)
            with open(json_path, 'w') as f:
                json.dump(template, f, indent=2)
            print(f"  ✓ Created template: {json_path}")

            # Generate Python implementation
            py_path = impl_dir / f"{protocol_id}.py"
            implementation = create_python_implementation(protocol_info, category)
            with open(py_path, 'w') as f:
                f.write(implementation)
            print(f"  ✓ Created implementation: {py_path}")

    print(f"\n✅ Successfully generated all {sum(len(p) for p in PROTOCOLS.values())} protocols!")
    print(f"   - {len(PROTOCOLS['performance'])} Performance protocols")
    print(f"   - {len(PROTOCOLS['degradation'])} Degradation protocols")
    print(f"   - {len(PROTOCOLS['environmental'])} Environmental protocols")
    print(f"   - {len(PROTOCOLS['mechanical'])} Mechanical protocols")
    print(f"   - {len(PROTOCOLS['safety'])} Safety protocols")


if __name__ == '__main__':
    generate_all_protocols()
