"""
Unit tests for ML-002 implementation

Tests test execution logic, equipment control, and data collection

Author: ganeshgowri-ASA
Date: 2025-11-14
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
import time

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from implementation import (
    ML002MechanicalLoadTest,
    TestSample,
    TestStatus,
    AlertLevel,
    LoadController,
    SensorArray
)


class TestTestSample:
    """Test TestSample dataclass"""

    def test_create_sample(self):
        """Test creating a test sample"""
        sample = TestSample(
            sample_id="TEST-001",
            module_type="Crystalline Silicon",
            serial_number="SN123"
        )

        assert sample.sample_id == "TEST-001"
        assert sample.module_type == "Crystalline Silicon"
        assert sample.serial_number == "SN123"

    def test_sample_to_dict(self):
        """Test converting sample to dictionary"""
        sample = TestSample(
            sample_id="TEST-001",
            module_type="Crystalline Silicon",
            serial_number="SN123",
            manufacturer="Test Inc."
        )

        sample_dict = sample.to_dict()

        assert isinstance(sample_dict, dict)
        assert sample_dict['sample_id'] == "TEST-001"
        assert sample_dict['manufacturer'] == "Test Inc."


class TestLoadController:
    """Test LoadController class"""

    @pytest.fixture
    def controller(self):
        """Create load controller instance"""
        config = {'max_load_pa': 5400}
        return LoadController(config)

    def test_controller_initialization(self, controller):
        """Test controller initializes correctly"""
        assert controller.connected is False
        assert controller.calibrated is False
        assert controller.current_load_pa == 0.0

    def test_controller_connect(self, controller):
        """Test controller connection"""
        assert controller.connect() is True
        assert controller.connected is True

    def test_controller_calibrate(self, controller):
        """Test controller calibration"""
        controller.connect()
        assert controller.calibrate() is True
        assert controller.calibrated is True

    def test_controller_is_ready(self, controller):
        """Test controller ready check"""
        assert controller.is_ready() is False

        controller.connect()
        assert controller.is_ready() is False

        controller.calibrate()
        assert controller.is_ready() is True

    def test_set_load(self, controller):
        """Test setting load"""
        controller.connect()
        controller.calibrate()

        result = controller.set_load(1000.0, rate_pa_per_sec=100.0)
        assert result is True
        assert controller.current_load_pa == 1000.0

    def test_set_load_not_ready(self, controller):
        """Test setting load when not ready"""
        result = controller.set_load(1000.0)
        assert result is False

    def test_emergency_stop(self, controller):
        """Test emergency stop"""
        controller.connect()
        controller.calibrate()
        controller.set_load(1000.0)

        assert controller.emergency_stop() is True
        assert controller.current_load_pa == 0.0


class TestSensorArray:
    """Test SensorArray class"""

    @pytest.fixture
    def sensor_configs(self):
        """Create sensor configurations"""
        return [
            {
                'sensor_id': 'load_cell_1',
                'sensor_type': 'load_cell',
                'parameter': 'applied_load',
                'unit': 'Pa',
                'sample_rate_hz': 10
            },
            {
                'sensor_id': 'displacement_center',
                'sensor_type': 'lvdt',
                'parameter': 'deflection_center',
                'unit': 'mm',
                'sample_rate_hz': 10
            }
        ]

    @pytest.fixture
    def sensor_array(self, sensor_configs):
        """Create sensor array instance"""
        return SensorArray(sensor_configs)

    def test_sensor_array_initialization(self, sensor_array, sensor_configs):
        """Test sensor array initializes correctly"""
        assert len(sensor_array.sensors) == len(sensor_configs)
        assert sensor_array.connected is False

    def test_sensor_array_connect(self, sensor_array):
        """Test sensor array connection"""
        assert sensor_array.connect() is True
        assert sensor_array.connected is True

    def test_read_all_sensors(self, sensor_array):
        """Test reading all sensors"""
        sensor_array.connect()
        readings = sensor_array.read_all()

        assert len(readings) == len(sensor_array.sensors)
        for reading in readings:
            assert reading.sensor_id is not None
            assert reading.value is not None
            assert reading.unit is not None

    def test_read_specific_sensor(self, sensor_array):
        """Test reading specific sensor"""
        sensor_array.connect()
        reading = sensor_array.read_sensor('load_cell_1')

        assert reading is not None
        assert reading.sensor_id == 'load_cell_1'


class TestML002MechanicalLoadTest:
    """Test ML002MechanicalLoadTest class"""

    @pytest.fixture
    def protocol_file(self):
        """Get protocol file path"""
        return str(Path(__file__).parent.parent / "protocol.json")

    @pytest.fixture
    def test_instance(self, protocol_file):
        """Create test instance"""
        return ML002MechanicalLoadTest(protocol_file)

    @pytest.fixture
    def test_sample(self):
        """Create test sample"""
        return TestSample(
            sample_id="TEST-MODULE-001",
            module_type="Crystalline Silicon",
            serial_number="SN123456",
            manufacturer="Test Solar Inc."
        )

    def test_initialization(self, test_instance):
        """Test test instance initializes correctly"""
        assert test_instance.target_load_pa == 1000
        assert test_instance.cycle_count == 1000
        assert test_instance.status == TestStatus.INITIALIZED

    def test_load_protocol(self, protocol_file):
        """Test loading protocol file"""
        test = ML002MechanicalLoadTest(protocol_file)
        protocol = test.protocol

        assert protocol['metadata']['protocol_id'] == 'ML-002'
        assert 'parameters' in protocol

    def test_set_progress_callback(self, test_instance):
        """Test setting progress callback"""
        callback_called = False

        def callback(cycle, total, data):
            nonlocal callback_called
            callback_called = True

        test_instance.set_progress_callback(callback)
        assert test_instance.progress_callback is not None

    def test_set_alert_callback(self, test_instance):
        """Test setting alert callback"""
        alerts = []

        def callback(level, message):
            alerts.append((level, message))

        test_instance.set_alert_callback(callback)
        test_instance._emit_alert(AlertLevel.WARNING, "Test alert")

        assert len(alerts) == 1
        assert alerts[0][0] == AlertLevel.WARNING

    def test_initialize_equipment(self, test_instance):
        """Test equipment initialization"""
        result = test_instance.initialize_equipment()
        assert result is True
        assert test_instance.status == TestStatus.RUNNING or test_instance.status == TestStatus.CALIBRATING

    def test_abort_test(self, test_instance):
        """Test aborting test"""
        test_instance.abort_test()
        assert test_instance.abort_flag is True


class TestTestExecution:
    """Integration tests for test execution"""

    @pytest.fixture
    def protocol_file(self):
        """Get protocol file path"""
        return str(Path(__file__).parent.parent / "protocol.json")

    @pytest.fixture
    def test_sample(self):
        """Create test sample"""
        return TestSample(
            sample_id="INTEGRATION-TEST-001",
            module_type="Crystalline Silicon",
            serial_number="SN999",
            manufacturer="Integration Test Inc.",
            rated_power_w=400.0
        )

    @pytest.mark.slow
    def test_execute_single_cycle(self, protocol_file, test_sample):
        """Test executing a single cycle"""
        # Create test with reduced cycle count for fast testing
        test = ML002MechanicalLoadTest(protocol_file)
        test.cycle_count = 1  # Override for testing

        # Initialize equipment
        assert test.initialize_equipment() is True

        # Execute one cycle
        cycle_data = test._execute_cycle(1)

        assert cycle_data.cycle_number == 1
        assert cycle_data.max_load_pa >= 0
        assert cycle_data.end_time > cycle_data.start_time

    def test_check_failure_conditions_no_failure(self, protocol_file):
        """Test failure condition checking with normal data"""
        from implementation import CycleData

        test = ML002MechanicalLoadTest(protocol_file)

        cycle_data = CycleData(
            cycle_number=1,
            start_time=time.time(),
            end_time=time.time() + 10,
            max_load_pa=1000,
            min_load_pa=0,
            max_deflection_mm=5.0,
            min_deflection_mm=0.1,
            peak_to_peak_deflection_mm=4.9
        )

        failure = test._check_failure_conditions(cycle_data)
        assert failure is False

    def test_check_failure_conditions_excessive_deflection(self, protocol_file):
        """Test failure condition checking with excessive deflection"""
        from implementation import CycleData

        test = ML002MechanicalLoadTest(protocol_file)

        cycle_data = CycleData(
            cycle_number=1,
            start_time=time.time(),
            end_time=time.time() + 10,
            max_load_pa=1000,
            min_load_pa=0,
            max_deflection_mm=60.0,  # Exceeds 50mm threshold
            min_deflection_mm=0.1,
            peak_to_peak_deflection_mm=59.9
        )

        failure = test._check_failure_conditions(cycle_data)
        assert failure is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
