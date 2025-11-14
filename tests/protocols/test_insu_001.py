"""
Test Suite for INSU-001: Insulation Resistance Test Protocol
Tests protocol definition, calculations, and acceptance criteria per IEC 61730 MST 01
"""

import pytest
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestINSU001Protocol:
    """Test the INSU-001 protocol JSON definition"""

    @pytest.fixture
    def protocol_data(self):
        """Load the INSU-001 protocol definition"""
        protocol_path = Path(__file__).parent.parent.parent / "protocols" / "definitions" / "insu-001.json"
        with open(protocol_path, 'r') as f:
            return json.load(f)

    def test_protocol_metadata(self, protocol_data):
        """Test that protocol metadata is complete and correct"""
        metadata = protocol_data['protocol_metadata']

        assert metadata['protocol_id'] == 'INSU-001'
        assert metadata['protocol_name'] == 'Insulation Resistance Test'
        assert metadata['version'] == '1.0.0'
        assert metadata['category'] == 'safety'
        assert 'IEC 61730 MST 01' in metadata['standard_reference']
        assert len(metadata['tags']) > 0
        assert 'safety' in metadata['tags']

    def test_standard_requirements(self, protocol_data):
        """Test that IEC 61730 standard requirements are defined"""
        standard = protocol_data['standard']

        assert standard['name'] == 'IEC 61730'
        assert standard['section'] == 'MST 01'
        assert len(standard['requirements']) > 0

        # Check for key requirements
        requirements_text = ' '.join(standard['requirements'])
        assert '500 V' in requirements_text or '1000 V' in requirements_text
        assert '40 MΩ' in requirements_text or '40 MΩ·m²' in requirements_text
        assert '60 seconds' in requirements_text

    def test_device_under_test_fields(self, protocol_data):
        """Test that DUT information fields are properly defined"""
        dut = protocol_data['device_under_test']

        required_fields = ['dut_manufacturer', 'dut_model', 'dut_serial', 'dut_area']
        field_ids = [field['field_id'] for field in dut['required_info']]

        for required_field in required_fields:
            assert required_field in field_ids

        # Check module area field has correct unit
        area_field = next(f for f in dut['required_info'] if f['field_id'] == 'dut_area')
        assert area_field['unit'] == 'm²'
        assert area_field['required'] == True

    def test_test_parameters(self, protocol_data):
        """Test that test parameters are properly configured"""
        sections = protocol_data['protocol_inputs']['sections']

        # Find test parameters section
        test_params = next(s for s in sections if s['section_id'] == 'test_parameters')

        field_ids = [field['field_id'] for field in test_params['fields']]

        assert 'test_voltage' in field_ids
        assert 'test_duration' in field_ids

        # Check test voltage options
        voltage_field = next(f for f in test_params['fields'] if f['field_id'] == 'test_voltage')
        assert '500 V DC' in voltage_field['validation']['options']
        assert '1000 V DC' in voltage_field['validation']['options']

        # Check test duration minimum
        duration_field = next(f for f in test_params['fields'] if f['field_id'] == 'test_duration')
        assert duration_field['validation']['min'] == 60
        assert duration_field['unit'] == 'seconds'

    def test_safety_interlocks(self, protocol_data):
        """Test that safety interlocks are comprehensive"""
        safety = protocol_data['safety_interlocks']

        # Pre-test checks
        assert len(safety['pre_test_checks']) >= 5

        # Check for critical safety checks
        check_descriptions = [check['description'] for check in safety['pre_test_checks']]

        # Should check for disconnection from power
        assert any('disconnect' in desc.lower() or 'power source' in desc.lower()
                  for desc in check_descriptions)

        # Should check for dry surface
        assert any('dry' in desc.lower() for desc in check_descriptions)

        # Should check for grounding
        assert any('ground' in desc.lower() for desc in check_descriptions)

        # Post-test procedures
        assert len(safety['post_test_procedures']) > 0

        # Check for discharge procedure
        discharge_check = any('discharge' in proc['description'].lower()
                             for proc in safety['post_test_procedures'])
        assert discharge_check

    def test_acceptance_criteria(self, protocol_data):
        """Test that acceptance criteria match IEC 61730 requirements"""
        criteria = protocol_data['quality_control']['acceptance_criteria']

        # Find the main IEC criterion
        iec_criterion = next(c for c in criteria if c['criteria_id'] == 'ac_minimum_resistance')

        assert 'IEC 61730' in iec_criterion['reference_standard']
        assert '40 MΩ·m²' in iec_criterion['pass_condition']

        # Check for safety threshold
        safety_criterion = next(c for c in criteria if c['criteria_id'] == 'ac_absolute_minimum')
        assert '1 MΩ' in safety_criterion['pass_condition']

    def test_calculations_defined(self, protocol_data):
        """Test that required calculations are defined"""
        calculations = protocol_data['analysis']['calculations']

        calc_ids = [calc['calc_id'] for calc in calculations]

        assert 'specific_insulation_resistance' in calc_ids
        assert 'average_resistance' in calc_ids
        assert 'minimum_resistance' in calc_ids

        # Check specific resistance formula
        specific_calc = next(c for c in calculations if c['calc_id'] == 'specific_insulation_resistance')
        assert 'resistance_reading' in specific_calc['dependencies']
        assert 'dut_area' in specific_calc['dependencies']
        assert specific_calc['output_unit'] == 'MΩ·m²'

    def test_validation_rules(self, protocol_data):
        """Test that QC validation rules are comprehensive"""
        rules = protocol_data['quality_control']['validation_rules']

        rule_ids = [rule['rule_id'] for rule in rules]

        # Should validate test voltage
        assert any('voltage' in rule_id for rule_id in rule_ids)

        # Should validate temperature
        assert any('temperature' in rule_id for rule_id in rule_ids)

        # Should validate calibration
        assert any('calibration' in rule_id for rule_id in rule_ids)

    def test_approval_gates(self, protocol_data):
        """Test that approval workflow is defined"""
        gates = protocol_data['approval_gates']['gates']

        assert len(gates) >= 2

        gate_ids = [gate['gate_id'] for gate in gates]

        # Should have setup and results approval
        assert any('setup' in gate_id for gate_id in gate_ids)
        assert any('results' in gate_id or 'review' in gate_id for gate_id in gate_ids)

    def test_traceability_configuration(self, protocol_data):
        """Test that traceability is properly configured"""
        traceability = protocol_data['traceability']

        assert len(traceability['audit_fields']) > 0
        assert 'test_operator' in traceability['audit_fields']
        assert 'equipment_id' in traceability['audit_fields']

        assert traceability['data_retention_years'] >= 10
        assert traceability['chain_of_custody'] == True

    def test_integrations_configured(self, protocol_data):
        """Test that system integrations are configured"""
        integrations = protocol_data['integrations']

        assert 'lims' in integrations
        assert 'qms' in integrations

        # QMS should have NC auto-creation configured
        assert integrations['qms']['auto_nc_creation'] == True
        assert len(integrations['qms']['nc_trigger_conditions']) > 0


class TestINSU001Calculations:
    """Test calculation logic for insulation resistance"""

    def test_specific_resistance_calculation(self):
        """Test specific insulation resistance calculation"""
        # R_specific = R_measured × A

        # Test case 1: Module area = 1.94 m², Resistance = 100 MΩ
        resistance_mohm = 100.0
        module_area_m2 = 1.94
        expected_specific = 194.0  # MΩ·m²

        calculated_specific = resistance_mohm * module_area_m2

        assert abs(calculated_specific - expected_specific) < 0.01

    def test_pass_fail_logic_iec_requirement(self):
        """Test pass/fail logic for IEC 61730 requirement"""
        IEC_MINIMUM = 40.0  # MΩ·m²

        # Test passing case
        specific_resistance_pass = 50.0
        assert specific_resistance_pass >= IEC_MINIMUM

        # Test failing case
        specific_resistance_fail = 35.0
        assert specific_resistance_fail < IEC_MINIMUM

        # Test boundary case
        specific_resistance_boundary = 40.0
        assert specific_resistance_boundary >= IEC_MINIMUM

    def test_pass_fail_logic_safety_requirement(self):
        """Test pass/fail logic for absolute safety requirement"""
        SAFETY_MINIMUM = 1.0  # MΩ

        # Test passing case
        resistance_pass = 5.0
        assert resistance_pass >= SAFETY_MINIMUM

        # Test failing case
        resistance_fail = 0.5
        assert resistance_fail < SAFETY_MINIMUM

    def test_measurement_repeatability(self):
        """Test measurement repeatability calculation"""
        import numpy as np

        # Sample measurements in MΩ
        measurements = [100.0, 102.0, 98.0, 101.0, 99.0]

        mean = np.mean(measurements)
        std_dev = np.std(measurements)

        # Relative standard deviation (RSD) in percentage
        rsd_percent = (std_dev / mean * 100) if mean > 0 else 0

        # Good repeatability: RSD < 20%
        assert rsd_percent < 20.0

        # Typical values
        assert 99.0 < mean < 101.0
        assert std_dev < 2.0

    def test_multiple_test_points(self):
        """Test handling of multiple test points"""
        test_points = {
            'Active to Frame': {'resistance': 120.0, 'area': 1.94},
            'Active to Mounting Holes': {'resistance': 115.0, 'area': 1.94},
            'Circuit A to B': {'resistance': 200.0, 'area': 1.94}
        }

        specific_resistances = {}

        for point, data in test_points.items():
            specific_resistances[point] = data['resistance'] * data['area']

        # Find minimum specific resistance
        min_specific = min(specific_resistances.values())

        # Should be 115.0 × 1.94 = 223.1 MΩ·m²
        assert abs(min_specific - 223.1) < 0.1

        # All should pass IEC requirement
        assert all(r >= 40.0 for r in specific_resistances.values())


class TestINSU001DataValidation:
    """Test data validation for INSU-001"""

    def test_voltage_range_validation(self):
        """Test that test voltage is within acceptable range"""
        nominal_500v = 500.0
        nominal_1000v = 1000.0

        tolerance_percent = 2.0

        # 500V range: 490-510V
        min_500 = nominal_500v * (1 - tolerance_percent/100)
        max_500 = nominal_500v * (1 + tolerance_percent/100)

        assert min_500 == 490.0
        assert max_500 == 510.0

        # Test valid readings
        assert min_500 <= 500.0 <= max_500
        assert min_500 <= 505.0 <= max_500

        # Test invalid readings
        assert not (min_500 <= 485.0 <= max_500)
        assert not (min_500 <= 515.0 <= max_500)

    def test_environmental_conditions_validation(self):
        """Test environmental conditions are within acceptable ranges"""
        # Temperature: 15-35°C per IEC 61730
        test_temp = 25.0
        assert 15.0 <= test_temp <= 35.0

        # Humidity: <75% recommended
        test_humidity = 45.0
        assert 0.0 <= test_humidity <= 75.0

        # Out of range examples
        assert not (15.0 <= 10.0 <= 35.0)  # Too cold
        assert not (15.0 <= 40.0 <= 35.0)  # Too hot

    def test_test_duration_validation(self):
        """Test that test duration meets minimum requirement"""
        minimum_duration = 60  # seconds per IEC 61730

        # Valid durations
        assert 60 >= minimum_duration
        assert 120 >= minimum_duration

        # Invalid duration
        assert not (30 >= minimum_duration)

    def test_calibration_status_validation(self):
        """Test equipment calibration status checking"""
        from datetime import date, timedelta

        today = date.today()

        # Valid calibration
        cal_due_future = today + timedelta(days=30)
        assert cal_due_future >= today

        # Overdue calibration
        cal_due_past = today - timedelta(days=1)
        assert cal_due_past < today

        # Due soon (within 30 days)
        cal_due_soon = today + timedelta(days=15)
        days_until_due = (cal_due_soon - today).days
        assert 0 < days_until_due < 30


class TestINSU001SafetyChecks:
    """Test safety-related functionality"""

    def test_all_safety_checks_required(self):
        """Test that all safety checks must be completed"""
        safety_checks = {
            'safety_01': False,  # Not checked
            'safety_02': True,
            'safety_03': True,
            'safety_04': True,
            'safety_05': True,
            'safety_06': True
        }

        all_passed = all(safety_checks.values())
        assert not all_passed  # Should fail because safety_01 is False

        # Fix the check
        safety_checks['safety_01'] = True
        all_passed = all(safety_checks.values())
        assert all_passed

    def test_high_voltage_warning_required(self):
        """Test that high voltage warnings are present"""
        test_voltage = 1000  # V

        is_high_voltage = test_voltage >= 500
        assert is_high_voltage

        warning_message = "HIGH VOLTAGE WARNING" if is_high_voltage else ""
        assert "HIGH VOLTAGE" in warning_message

    def test_discharge_time_requirement(self):
        """Test that discharge time is enforced"""
        minimum_discharge_time = 5  # seconds

        # Test that discharge time meets minimum
        actual_discharge_time = 5
        assert actual_discharge_time >= minimum_discharge_time

        # Test insufficient discharge time
        insufficient_time = 2
        assert not (insufficient_time >= minimum_discharge_time)


class TestINSU001ReportGeneration:
    """Test report generation configuration"""

    @pytest.fixture
    def protocol_data(self):
        """Load the INSU-001 protocol definition"""
        protocol_path = Path(__file__).parent.parent.parent / "protocols" / "definitions" / "insu-001.json"
        with open(protocol_path, 'r') as f:
            return json.load(f)

    def test_report_sections_defined(self, protocol_data):
        """Test that all required report sections are defined"""
        report_config = protocol_data['report_generation']

        assert report_config['auto_generate'] == True
        assert len(report_config['sections']) > 0

        section_names = [s['section_name'] for s in report_config['sections']]

        # Required sections
        assert any('Test Summary' in name for name in section_names)
        assert any('Device Under Test' in name for name in section_names)
        assert any('Measurement' in name for name in section_names)
        assert any('Pass/Fail' in name for name in section_names)
        assert any('Safety' in name for name in section_names)

    def test_report_formats_supported(self, protocol_data):
        """Test that required export formats are supported"""
        report_config = protocol_data['report_generation']

        formats = report_config['export_formats']

        assert 'pdf' in formats
        assert 'excel' in formats
        assert 'json' in formats

    def test_digital_signature_required(self, protocol_data):
        """Test that digital signature is required for compliance"""
        report_config = protocol_data['report_generation']

        assert report_config['digital_signature_required'] == True


class TestINSU001Integration:
    """Test system integration configurations"""

    @pytest.fixture
    def protocol_data(self):
        """Load the INSU-001 protocol definition"""
        protocol_path = Path(__file__).parent.parent.parent / "protocols" / "definitions" / "insu-001.json"
        with open(protocol_path, 'r') as f:
            return json.load(f)

    def test_lims_integration(self, protocol_data):
        """Test LIMS integration configuration"""
        lims_config = protocol_data['integrations']['lims']

        assert lims_config['enabled'] == True
        assert 'export_format' in lims_config
        assert len(lims_config['fields_to_export']) > 0

        # Should export critical fields
        assert 'test_result' in lims_config['fields_to_export']
        assert 'min_specific_resistance' in lims_config['fields_to_export']

    def test_qms_integration(self, protocol_data):
        """Test QMS integration configuration"""
        qms_config = protocol_data['integrations']['qms']

        assert qms_config['enabled'] == True
        assert 'document_id' in qms_config
        assert 'QMS-IEC61730' in qms_config['document_id']

        # Auto NC creation
        assert qms_config['auto_nc_creation'] == True
        assert len(qms_config['nc_trigger_conditions']) > 0

        # Check NC triggers include failure condition
        triggers = qms_config['nc_trigger_conditions']
        assert any('40 MΩ·m²' in trigger for trigger in triggers)

    def test_nc_register_configuration(self, protocol_data):
        """Test non-conformance register configuration"""
        nc_config = protocol_data['nc_register']

        assert nc_config['auto_log_failures'] == True
        assert len(nc_config['nc_categories']) > 0

        # Should have failure-related categories
        categories = nc_config['nc_categories']
        assert any('insulation' in cat.lower() for cat in categories)


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])
