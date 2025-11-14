"""Unit tests for HF-001 Humidity Freeze Protocol"""

import pytest
from pathlib import Path
from datetime import datetime

from protocols.environmental.hf_001 import (
    HumidityFreezeProtocol,
    IVCurveData,
    CycleData,
    HumidityFreezeTestData
)


class TestHF001Protocol:
    """Test suite for HF-001 protocol implementation"""

    def test_protocol_initialization(self, protocol_instance):
        """Test protocol initializes correctly"""
        assert protocol_instance is not None
        assert protocol_instance.metadata.protocol_id == "HF-001"
        assert protocol_instance.metadata.name == "Humidity Freeze Test Protocol"
        assert protocol_instance.metadata.version == "1.0.0"
        assert protocol_instance.metadata.standard == "IEC 61215 MQT 12"

    def test_template_loading(self, protocol_instance):
        """Test JSON template loads correctly"""
        assert protocol_instance.template is not None
        assert 'metadata' in protocol_instance.template
        assert 'parameters' in protocol_instance.template
        assert 'equipment' in protocol_instance.template
        assert 'test_steps' in protocol_instance.template
        assert 'qc_criteria' in protocol_instance.template

    def test_get_parameters(self, protocol_instance):
        """Test parameter retrieval from template"""
        total_cycles = protocol_instance.get_parameter('total_cycles')
        assert total_cycles is not None
        assert total_cycles['value'] == 10
        assert total_cycles['unit'] == 'cycles'

        temp_low = protocol_instance.get_parameter('temperature_low')
        assert temp_low['value'] == -40
        assert temp_low['unit'] == '°C'

        temp_high = protocol_instance.get_parameter('temperature_high')
        assert temp_high['value'] == 85

    def test_validate_equipment(self, protocol_instance):
        """Test equipment validation"""
        # Basic validation should pass
        result = protocol_instance.validate_equipment()
        assert result is True

    def test_validate_sample(self, protocol_instance, sample_data):
        """Test sample validation"""
        # Valid sample data
        result = protocol_instance.validate_sample(sample_data)
        assert result is True

        # Invalid sample data (missing required field)
        invalid_data = {'module_serial': 'TEST-001'}
        result = protocol_instance.validate_sample(invalid_data)
        assert result is False

    def test_measure_iv_curve(self, protocol_instance):
        """Test I-V curve measurement"""
        iv_data = protocol_instance.measure_iv_curve(
            module_temp=25.0,
            irradiance=1000.0
        )

        assert isinstance(iv_data, IVCurveData)
        assert iv_data.Voc > 0
        assert iv_data.Isc > 0
        assert iv_data.Pmax > 0
        assert 0 < iv_data.FF < 1
        assert iv_data.Vmp < iv_data.Voc
        assert iv_data.Imp < iv_data.Isc

        # Verify power relationship
        calculated_pmax = iv_data.Vmp * iv_data.Imp
        assert abs(calculated_pmax - iv_data.Pmax) < 0.1

    def test_measure_insulation_resistance(self, protocol_instance):
        """Test insulation resistance measurement"""
        resistance = protocol_instance.measure_insulation_resistance(
            test_voltage=1000.0
        )

        assert isinstance(resistance, float)
        assert resistance > 0
        # Should meet minimum requirement of 40 MΩ
        assert resistance > 40.0

    def test_execute_cycle(self, protocol_instance):
        """Test single cycle execution"""
        cycle_data = protocol_instance.execute_cycle(
            cycle_number=1,
            duration_minutes=360  # 6 hours
        )

        assert isinstance(cycle_data, CycleData)
        assert cycle_data.cycle_number == 1
        assert cycle_data.status == "completed"
        assert len(cycle_data.temperature_log) > 0
        assert len(cycle_data.humidity_log) > 0
        assert cycle_data.end_time > cycle_data.start_time

        # Check temperature range
        temps = [t[1] for t in cycle_data.temperature_log]
        assert min(temps) < -30  # Should reach low temp
        assert max(temps) > 80   # Should reach high temp

    def test_run_test(self, protocol_instance, sample_data):
        """Test full test execution"""
        result = protocol_instance.run_test(
            sample_id=sample_data['module_serial'],
            operator_id="TEST-OPERATOR"
        )

        assert result is not None
        assert result.test_id is not None
        assert result.protocol_id == "HF-001"
        assert result.status == "completed"
        assert result.pass_fail is not None

        # Verify test data was created
        assert protocol_instance.test_data is not None
        assert isinstance(protocol_instance.test_data, HumidityFreezeTestData)
        assert protocol_instance.test_data.module_serial == sample_data['module_serial']

        # Verify measurements
        assert protocol_instance.test_data.initial_iv_curve is not None
        assert protocol_instance.test_data.final_iv_curve is not None
        assert protocol_instance.test_data.initial_insulation_resistance is not None
        assert protocol_instance.test_data.final_insulation_resistance is not None

        # Verify cycles
        assert len(protocol_instance.test_data.cycles) == 10
        for cycle in protocol_instance.test_data.cycles:
            assert cycle.status == "completed"

    def test_analyze_results(self, protocol_instance, sample_data):
        """Test results analysis"""
        # Run test first
        result = protocol_instance.run_test(
            sample_id=sample_data['module_serial'],
            operator_id="TEST-OPERATOR"
        )

        # Analyze results
        analysis = protocol_instance.analyze_results(result)

        assert 'power_degradation' in analysis
        assert 'pass_fail' in analysis
        assert 'failure_modes' in analysis
        assert 'initial_performance' in analysis
        assert 'final_performance' in analysis
        assert 'cycles_completed' in analysis

        # Check degradation calculation
        assert isinstance(analysis['power_degradation'], (int, float))
        assert 0 <= analysis['power_degradation'] <= 100

        # Should pass with ~3% degradation
        assert analysis['pass_fail'] is True
        assert analysis['power_degradation'] < 5.0

    def test_qc_criteria_power_degradation(self, protocol_instance):
        """Test power degradation QC criteria"""
        qc = protocol_instance.get_qc_criteria()

        assert 'power_degradation' in qc
        assert qc['power_degradation']['limit'] == 5.0
        assert qc['power_degradation']['unit'] == '%'
        assert qc['power_degradation']['criticality'] == 'FAIL'

    def test_qc_criteria_insulation(self, protocol_instance):
        """Test insulation resistance QC criteria"""
        qc = protocol_instance.get_qc_criteria()

        assert 'insulation_resistance' in qc
        assert qc['insulation_resistance']['final_min'] == 40
        assert qc['insulation_resistance']['unit'] == 'MΩ'

    def test_qc_criteria_visual_defects(self, protocol_instance):
        """Test visual defect QC criteria"""
        qc = protocol_instance.get_qc_criteria()

        assert 'visual_defects' in qc
        assert 'major_defects' in qc['visual_defects']
        assert 'minor_defects' in qc['visual_defects']

        # Major defects should cause failure
        major = qc['visual_defects']['major_defects']
        assert 'broken_cells' in major
        assert major['broken_cells']['criticality'] == 'FAIL'

    def test_export_cycle_data(self, protocol_instance, sample_data, test_data_dir):
        """Test cycle data export to CSV"""
        # Run test first
        protocol_instance.run_test(
            sample_id=sample_data['module_serial'],
            operator_id="TEST-OPERATOR"
        )

        # Export data
        csv_path = protocol_instance.export_cycle_data(test_data_dir)

        assert csv_path.exists()
        assert csv_path.suffix == '.csv'

        # Verify CSV content
        import pandas as pd
        df = pd.read_csv(csv_path)

        assert 'cycle' in df.columns
        assert 'timestamp' in df.columns
        assert 'parameter' in df.columns
        assert 'value' in df.columns
        assert 'unit' in df.columns

        # Should have both temperature and humidity data
        assert 'temperature' in df['parameter'].values
        assert 'humidity' in df['parameter'].values

    def test_generate_qr_code(self, protocol_instance, sample_data):
        """Test QR code generation"""
        # Run test first
        protocol_instance.run_test(
            sample_id=sample_data['module_serial'],
            operator_id="TEST-OPERATOR"
        )

        # Generate QR code
        qr_content = protocol_instance.generate_qr_code()

        assert qr_content is not None
        assert isinstance(qr_content, str)
        assert 'HF-001' in qr_content
        assert sample_data['module_serial'] in qr_content

    def test_test_steps_count(self, protocol_instance):
        """Test that all required steps are defined"""
        steps = protocol_instance.get_test_steps()

        assert len(steps) == 12  # Should have 12 steps per template
        assert steps[0]['step'] == 1
        assert steps[-1]['step'] == 12

    def test_equipment_requirements(self, protocol_instance):
        """Test equipment requirements are properly defined"""
        equipment = protocol_instance.template['equipment']

        # Required equipment
        assert 'environmental_chamber' in equipment
        assert equipment['environmental_chamber']['required'] is True
        assert equipment['iv_curve_tracer']['required'] is True
        assert equipment['insulation_tester']['required'] is True
        assert equipment['solar_simulator']['required'] is True

    def test_temperature_tolerance(self, protocol_instance):
        """Test temperature parameters have proper tolerances"""
        temp_high = protocol_instance.get_parameter('temperature_high')
        temp_low = protocol_instance.get_parameter('temperature_low')

        assert 'tolerance' in temp_high
        assert temp_high['tolerance'] == '±2'
        assert 'tolerance' in temp_low
        assert temp_low['tolerance'] == '±2'

    def test_cycle_profile_phases(self, protocol_instance):
        """Test cycle profile has all required phases"""
        steps = protocol_instance.get_test_steps()

        # Find cycling step (step 6)
        cycling_step = next(s for s in steps if s['step'] == 6)

        assert 'cycle_profile' in cycling_step
        profile = cycling_step['cycle_profile']

        # Verify all 4 phases exist
        assert 'phase_1' in profile
        assert 'phase_2' in profile
        assert 'phase_3' in profile
        assert 'phase_4' in profile

        # Verify phase 1 (high temp with humidity)
        assert profile['phase_1']['temperature'] == '85°C ±2°C'
        assert profile['phase_1']['humidity'] == '85% RH ±5%'
        assert profile['phase_1']['duration'] == '4 hours'

        # Verify phase 3 (low temp)
        assert profile['phase_3']['temperature'] == '-40°C ±2°C'
        assert profile['phase_3']['duration'] == '1 hour'


class TestIVCurveData:
    """Test IVCurveData model"""

    def test_iv_curve_creation(self, mock_iv_curve_data):
        """Test IVCurveData model creation"""
        iv_data = IVCurveData(**mock_iv_curve_data)

        assert iv_data.Voc > 0
        assert iv_data.Isc > 0
        assert iv_data.Pmax > 0
        assert iv_data.FF > 0

    def test_iv_curve_validation(self):
        """Test IVCurveData validation"""
        with pytest.raises(Exception):
            # Missing required fields
            IVCurveData(
                timestamp=datetime.now(),
                voltage=[1, 2, 3],
                current=[1, 2, 3]
            )


class TestCycleData:
    """Test CycleData model"""

    def test_cycle_data_creation(self, mock_cycle_data):
        """Test CycleData model creation"""
        cycle = CycleData(**mock_cycle_data)

        assert cycle.cycle_number == 1
        assert cycle.status == 'completed'
        assert len(cycle.temperature_log) > 0
        assert len(cycle.humidity_log) > 0


class TestDataTraceability:
    """Test data traceability features"""

    def test_qr_code_configuration(self, protocol_instance):
        """Test QR code configuration in template"""
        traceability = protocol_instance.template['data_traceability']

        assert 'qr_code' in traceability
        assert traceability['qr_code']['enabled'] is True
        assert 'content' in traceability['qr_code']

    def test_required_traceability_fields(self, protocol_instance):
        """Test required fields for traceability"""
        traceability = protocol_instance.template['data_traceability']

        required_fields = traceability['required_fields']

        assert 'test_id' in required_fields
        assert 'module_serial_number' in required_fields
        assert 'test_start_datetime' in required_fields
        assert 'operator_id' in required_fields
        assert 'equipment_ids' in required_fields

    def test_data_retention(self, protocol_instance):
        """Test data retention policy"""
        traceability = protocol_instance.template['data_traceability']

        assert 'data_retention' in traceability
        assert traceability['data_retention']['duration'] == '25 years'


class TestReporting:
    """Test reporting functionality"""

    def test_report_configuration(self, protocol_instance):
        """Test report configuration in template"""
        reporting = protocol_instance.template['reporting']

        assert reporting['auto_generation'] is True
        assert 'PDF' in reporting['formats']
        assert 'JSON' in reporting['formats']
        assert 'CSV' in reporting['formats']

    def test_report_includes(self, protocol_instance):
        """Test report content requirements"""
        reporting = protocol_instance.template['reporting']

        includes = reporting['includes']

        assert 'Executive summary with pass/fail' in includes
        assert 'Test conditions and parameters' in includes
        assert 'QC criteria evaluation' in includes
        assert 'QR code for traceability' in includes
