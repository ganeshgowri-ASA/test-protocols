"""Tests for HOT-001 Protocol

Unit and integration tests for Hot Spot Endurance Test.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
import json

from protocols.environmental.hot_001 import (
    HotSpotEnduranceProtocol,
    IVCurveData,
    HotSpotTestData,
    VisualInspection
)


class TestHotSpotProtocolInitialization:
    """Test protocol initialization"""

    def test_protocol_initialization(self, hot_spot_protocol):
        """Test protocol initializes correctly"""
        assert hot_spot_protocol.metadata.protocol_id == "HOT-001"
        assert hot_spot_protocol.metadata.standard == "IEC 61215 MQT 09"
        assert hot_spot_protocol.metadata.category == "Safety Testing"

    def test_protocol_parameters_loaded(self, hot_spot_protocol):
        """Test protocol parameters are loaded from JSON"""
        assert 'max_power_degradation' in hot_spot_protocol.parameters
        assert hot_spot_protocol.get_parameter_value('max_power_degradation') == 5

    def test_protocol_equipment_loaded(self, hot_spot_protocol):
        """Test equipment requirements are loaded"""
        assert 'solar_simulator' in hot_spot_protocol.equipment
        assert 'thermal_imaging_camera' in hot_spot_protocol.equipment


class TestVisualInspection:
    """Test visual inspection functionality"""

    def test_initial_visual_inspection(self, hot_spot_protocol, sample_defects_minor):
        """Test initial visual inspection recording"""
        inspection = hot_spot_protocol.perform_initial_visual_inspection(
            inspector="Test Inspector",
            defects=sample_defects_minor,
            notes="Test inspection"
        )

        assert inspection.inspector == "Test Inspector"
        assert len(inspection.defects) == 1
        assert inspection.severity == "minor"

    def test_visual_inspection_no_defects(self, hot_spot_protocol):
        """Test visual inspection with no defects"""
        inspection = hot_spot_protocol.perform_initial_visual_inspection(
            inspector="Test Inspector",
            defects=[],
            notes="No defects found"
        )

        assert inspection.severity == "none"
        assert len(inspection.defects) == 0

    def test_visual_inspection_major_defects(self, hot_spot_protocol, sample_defects_major):
        """Test visual inspection with major defects"""
        inspection = hot_spot_protocol.perform_initial_visual_inspection(
            inspector="Test Inspector",
            defects=sample_defects_major,
            notes="Major defects found"
        )

        assert inspection.severity == "major"
        assert len(inspection.defects) == 2


class TestIVCurveMeasurement:
    """Test I-V curve measurement functionality"""

    def test_initial_iv_measurement(self, hot_spot_protocol, sample_iv_data):
        """Test initial I-V curve measurement"""
        iv_curve = hot_spot_protocol.measure_initial_iv_curve(
            voltage=sample_iv_data['voltage'],
            current=sample_iv_data['current'],
            irradiance=sample_iv_data['irradiance'],
            temperature=sample_iv_data['temperature']
        )

        assert isinstance(iv_curve, IVCurveData)
        assert iv_curve.voc > 0
        assert iv_curve.isc > 0
        assert iv_curve.pmax > 0
        assert 0 < iv_curve.fill_factor < 1

    def test_final_iv_measurement(self, hot_spot_protocol, sample_iv_data_degraded):
        """Test final I-V curve measurement"""
        iv_curve = hot_spot_protocol.measure_final_iv_curve(
            voltage=sample_iv_data_degraded['voltage'],
            current=sample_iv_data_degraded['current'],
            irradiance=sample_iv_data_degraded['irradiance'],
            temperature=sample_iv_data_degraded['temperature']
        )

        assert isinstance(iv_curve, IVCurveData)
        assert iv_curve.pmax > 0

    def test_iv_curve_parameters_calculated(self, hot_spot_protocol, sample_iv_data):
        """Test I-V curve parameters are calculated correctly"""
        iv_curve = hot_spot_protocol.measure_initial_iv_curve(
            voltage=sample_iv_data['voltage'],
            current=sample_iv_data['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        # Verify Voc is close to expected
        assert abs(iv_curve.voc - 40.0) < 1.0

        # Verify Isc is close to expected
        assert abs(iv_curve.isc - 9.0) < 0.5

        # Verify Pmax is reasonable
        assert 250 < iv_curve.pmax < 350

        # Verify fill factor is reasonable
        assert 0.7 < iv_curve.fill_factor < 0.85


class TestHotSpotTests:
    """Test hot spot test execution"""

    def test_cell_selection(self, hot_spot_protocol):
        """Test cell selection"""
        cell_ids = hot_spot_protocol.select_test_cells(['A1', 'B5', 'C9'])
        assert len(cell_ids) == 3
        assert 'A1' in cell_ids

    def test_cell_selection_insufficient_cells(self, hot_spot_protocol):
        """Test cell selection with insufficient cells raises error"""
        with pytest.raises(ValueError, match="Must select at least 3 cells"):
            hot_spot_protocol.select_test_cells(['A1', 'B5'])

    def test_bypass_diode_verification(self, hot_spot_protocol):
        """Test bypass diode verification"""
        is_functional = hot_spot_protocol.verify_bypass_diode(
            cell_id='A1',
            bypass_voltage_drop=0.6,
            activation_current=8.5
        )
        assert is_functional is True

    def test_bypass_diode_verification_failed(self, hot_spot_protocol):
        """Test bypass diode verification failure"""
        is_functional = hot_spot_protocol.verify_bypass_diode(
            cell_id='A1',
            bypass_voltage_drop=2.0,  # Too high
            activation_current=8.5
        )
        assert is_functional is False

    def test_hot_spot_test_execution(
        self,
        hot_spot_protocol,
        sample_temperature_profile
    ):
        """Test hot spot test execution"""
        test_data = hot_spot_protocol.execute_hot_spot_test(
            cell_id='A1',
            reverse_bias_voltage=50.0,
            current_limit=9.0,
            target_temperature=85.0,
            duration_hours=1.0,
            temperature_readings=sample_temperature_profile
        )

        assert isinstance(test_data, HotSpotTestData)
        assert test_data.cell_id == 'A1'
        assert test_data.completed is True
        assert test_data.max_temperature_reached > 0

    def test_hot_spot_test_safety_limit(
        self,
        hot_spot_protocol
    ):
        """Test hot spot test aborts on safety limit"""
        # Create temperature profile that exceeds safety limit
        start_time = datetime.now()
        unsafe_profile = [
            (start_time, 25.0),
            (start_time + timedelta(minutes=30), 125.0)  # Exceeds 120°C limit
        ]

        with pytest.raises(ValueError, match="Temperature exceeded safety limit"):
            hot_spot_protocol.execute_hot_spot_test(
                cell_id='A1',
                reverse_bias_voltage=50.0,
                current_limit=9.0,
                target_temperature=85.0,
                duration_hours=1.0,
                temperature_readings=unsafe_profile
            )

    def test_multiple_hot_spot_tests(
        self,
        hot_spot_protocol,
        sample_temperature_profile
    ):
        """Test executing multiple hot spot tests"""
        for cell_id in ['A1', 'B5', 'C9']:
            hot_spot_protocol.execute_hot_spot_test(
                cell_id=cell_id,
                reverse_bias_voltage=50.0,
                current_limit=9.0,
                target_temperature=85.0,
                duration_hours=1.0,
                temperature_readings=sample_temperature_profile
            )

        assert len(hot_spot_protocol.hot_spot_tests) == 3


class TestInsulationAndLeakage:
    """Test insulation resistance and leakage current measurements"""

    def test_insulation_resistance_measurement(self, hot_spot_protocol):
        """Test insulation resistance measurement"""
        resistance = hot_spot_protocol.measure_insulation_resistance(
            resistance=500.0,
            test_voltage=500.0,
            is_initial=True
        )

        assert resistance == 500.0
        assert hot_spot_protocol.initial_insulation_resistance == 500.0

    def test_wet_leakage_current_measurement(self, hot_spot_protocol):
        """Test wet leakage current measurement"""
        leakage = hot_spot_protocol.measure_wet_leakage_current(
            leakage_current=25.0,
            test_voltage=500.0
        )

        assert leakage == 25.0
        assert hot_spot_protocol.wet_leakage_current == 25.0


class TestPowerDegradation:
    """Test power degradation calculation"""

    def test_power_degradation_calculation(
        self,
        hot_spot_protocol,
        sample_iv_data,
        sample_iv_data_degraded
    ):
        """Test power degradation calculation"""
        # Measure initial and final curves
        hot_spot_protocol.measure_initial_iv_curve(
            voltage=sample_iv_data['voltage'],
            current=sample_iv_data['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        hot_spot_protocol.measure_final_iv_curve(
            voltage=sample_iv_data_degraded['voltage'],
            current=sample_iv_data_degraded['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        degradation = hot_spot_protocol.calculate_power_degradation()

        # Should be approximately 3-5% degradation
        assert 2.0 < degradation < 6.0

    def test_power_degradation_no_curves(self, hot_spot_protocol):
        """Test power degradation calculation without curves raises error"""
        with pytest.raises(ValueError, match="Both initial and final I-V curves required"):
            hot_spot_protocol.calculate_power_degradation()


class TestPassFailDetermination:
    """Test pass/fail determination"""

    def test_pass_determination(
        self,
        hot_spot_protocol,
        sample_iv_data,
        sample_iv_data_degraded,
        sample_temperature_profile
    ):
        """Test pass determination with acceptable degradation"""
        # Setup complete test
        hot_spot_protocol.measure_initial_iv_curve(
            voltage=sample_iv_data['voltage'],
            current=sample_iv_data['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        hot_spot_protocol.measure_final_iv_curve(
            voltage=sample_iv_data_degraded['voltage'],
            current=sample_iv_data_degraded['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        hot_spot_protocol.measure_insulation_resistance(500.0, 500.0, is_initial=False)
        hot_spot_protocol.measure_wet_leakage_current(25.0, 500.0)

        for cell_id in ['A1', 'B5', 'C9']:
            hot_spot_protocol.execute_hot_spot_test(
                cell_id=cell_id,
                reverse_bias_voltage=50.0,
                current_limit=9.0,
                temperature_readings=sample_temperature_profile
            )

        hot_spot_protocol.perform_final_visual_inspection(
            inspector="Test Inspector",
            defects=[]
        )

        pass_status, failures = hot_spot_protocol.determine_pass_fail()

        assert pass_status is True
        assert len(failures) == 0

    def test_fail_excessive_degradation(
        self,
        hot_spot_protocol,
        sample_iv_data
    ):
        """Test fail determination with excessive degradation"""
        # Create heavily degraded data (>5% degradation)
        voc = 40.0 * 0.90  # 10% Voc drop
        isc = 9.0 * 0.90   # 10% Isc drop
        voltage = np.linspace(0, voc, 100)
        current = isc * (1 - voltage / voc) ** 1.5

        hot_spot_protocol.measure_initial_iv_curve(
            voltage=sample_iv_data['voltage'],
            current=sample_iv_data['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        hot_spot_protocol.measure_final_iv_curve(
            voltage=voltage,
            current=current,
            irradiance=1000.0,
            temperature=25.0
        )

        pass_status, failures = hot_spot_protocol.determine_pass_fail()

        assert pass_status is False
        assert any('Power degradation' in f for f in failures)

    def test_fail_insufficient_hot_spot_tests(
        self,
        hot_spot_protocol,
        sample_iv_data,
        sample_temperature_profile
    ):
        """Test fail determination with insufficient hot spot tests"""
        hot_spot_protocol.measure_initial_iv_curve(
            voltage=sample_iv_data['voltage'],
            current=sample_iv_data['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        hot_spot_protocol.measure_final_iv_curve(
            voltage=sample_iv_data['voltage'],
            current=sample_iv_data['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        # Only 1 hot spot test instead of 3
        hot_spot_protocol.execute_hot_spot_test(
            cell_id='A1',
            reverse_bias_voltage=50.0,
            current_limit=9.0,
            temperature_readings=sample_temperature_profile
        )

        pass_status, failures = hot_spot_protocol.determine_pass_fail()

        assert pass_status is False
        assert any('cells tested' in f for f in failures)


class TestReportGeneration:
    """Test report generation"""

    def test_generate_test_report(
        self,
        hot_spot_protocol,
        sample_iv_data,
        sample_iv_data_degraded,
        sample_temperature_profile,
        module_info
    ):
        """Test complete report generation"""
        # Setup test
        hot_spot_protocol.start_test("TEST-001")
        hot_spot_protocol.module_info = module_info

        hot_spot_protocol.measure_initial_iv_curve(
            voltage=sample_iv_data['voltage'],
            current=sample_iv_data['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        for cell_id in ['A1', 'B5', 'C9']:
            hot_spot_protocol.execute_hot_spot_test(
                cell_id=cell_id,
                reverse_bias_voltage=50.0,
                current_limit=9.0,
                temperature_readings=sample_temperature_profile
            )

        hot_spot_protocol.measure_final_iv_curve(
            voltage=sample_iv_data_degraded['voltage'],
            current=sample_iv_data_degraded['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        hot_spot_protocol.measure_insulation_resistance(500.0, 500.0, is_initial=False)
        hot_spot_protocol.measure_wet_leakage_current(25.0, 500.0)

        report = hot_spot_protocol.generate_test_report()

        assert report['test_info']['test_id'] == "TEST-001"
        assert report['module_info']['serial_number'] == module_info['module_serial_number']
        assert len(report['hot_spot_tests']) == 3
        assert 'analysis' in report
        assert 'pass_fail' in report['analysis']

    def test_export_report_to_json(
        self,
        hot_spot_protocol,
        sample_iv_data,
        module_info,
        temp_directory
    ):
        """Test JSON report export"""
        hot_spot_protocol.start_test("TEST-002")
        hot_spot_protocol.module_info = module_info

        hot_spot_protocol.measure_initial_iv_curve(
            voltage=sample_iv_data['voltage'],
            current=sample_iv_data['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        hot_spot_protocol.measure_final_iv_curve(
            voltage=sample_iv_data['voltage'],
            current=sample_iv_data['current'],
            irradiance=1000.0,
            temperature=25.0
        )

        filepath = temp_directory / "test_report.json"
        hot_spot_protocol.export_report_to_json(str(filepath))

        assert filepath.exists()

        # Verify JSON content
        with open(filepath, 'r') as f:
            data = json.load(f)
            assert data['test_info']['test_id'] == "TEST-002"


class TestValidation:
    """Test input validation"""

    def test_validate_inputs_success(self, hot_spot_protocol, module_info):
        """Test successful input validation"""
        is_valid = hot_spot_protocol.validate_inputs(**module_info)
        assert is_valid is True

    def test_validate_inputs_missing_field(self, hot_spot_protocol):
        """Test validation fails with missing required field"""
        with pytest.raises(ValueError, match="Missing required field"):
            hot_spot_protocol.validate_inputs(
                module_serial_number='TEST-001'
                # Missing other required fields
            )
