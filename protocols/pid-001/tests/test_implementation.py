"""Tests for PID-001 protocol implementation."""

import pytest
from datetime import datetime
from protocols.pid_001.implementation import PID001Protocol, LeakageTracker
from src.models.protocol import TestExecution, Measurement


class TestLeakageTracker:
    """Test LeakageTracker class."""

    def test_initialization(self):
        """Test tracker initialization."""
        tracker = LeakageTracker(threshold_warning=5.0, threshold_critical=10.0)
        assert tracker.threshold_warning == 5.0
        assert tracker.threshold_critical == 10.0
        assert len(tracker.measurements) == 0

    def test_add_measurement_normal(self):
        """Test adding normal measurement."""
        tracker = LeakageTracker(threshold_warning=5.0, threshold_critical=10.0)
        event = tracker.add_measurement(2.5, datetime.utcnow(), 1.0)
        assert event is None  # No anomaly
        assert len(tracker.measurements) == 1

    def test_add_measurement_warning(self):
        """Test measurement exceeding warning threshold."""
        tracker = LeakageTracker(threshold_warning=5.0, threshold_critical=10.0)
        event = tracker.add_measurement(6.0, datetime.utcnow(), 1.0)
        assert event is not None
        assert event["severity"] == "warning"
        assert event["event_type"] == "warning_threshold"

    def test_add_measurement_critical(self):
        """Test measurement exceeding critical threshold."""
        tracker = LeakageTracker(threshold_warning=5.0, threshold_critical=10.0)
        event = tracker.add_measurement(12.0, datetime.utcnow(), 1.0)
        assert event is not None
        assert event["severity"] == "critical"
        assert event["event_type"] == "critical_threshold"

    def test_rapid_increase_detection(self):
        """Test rapid increase detection."""
        tracker = LeakageTracker(threshold_warning=10.0, threshold_critical=20.0)

        # Add normal measurements
        for i in range(5):
            tracker.add_measurement(1.0, datetime.utcnow(), float(i))

        # Add rapid increase
        event = tracker.add_measurement(3.0, datetime.utcnow(), 5.0)
        assert event is not None
        assert event["event_type"] == "rapid_increase"

    def test_get_statistics(self):
        """Test statistics calculation."""
        tracker = LeakageTracker()
        tracker.add_measurement(1.0, datetime.utcnow(), 1.0)
        tracker.add_measurement(2.0, datetime.utcnow(), 2.0)
        tracker.add_measurement(3.0, datetime.utcnow(), 3.0)

        stats = tracker.get_statistics()
        assert stats["average"] == 2.0
        assert stats["max"] == 3.0
        assert stats["min"] == 1.0
        assert stats["latest"] == 3.0
        assert stats["total_measurements"] == 3


class TestPID001Protocol:
    """Test PID001Protocol class."""

    def test_initialization(self, pid001_schema):
        """Test protocol initialization."""
        protocol = PID001Protocol()
        assert protocol.schema is not None
        assert protocol.metadata["pid"] == "pid-001"
        assert "validation_rules" in protocol.schema

    def test_validate_parameters_valid(self, sample_test_parameters):
        """Test parameter validation with valid data."""
        protocol = PID001Protocol()
        is_valid, errors = protocol.validate_parameters(sample_test_parameters)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_parameters_missing_required(self):
        """Test parameter validation with missing required fields."""
        protocol = PID001Protocol()
        params = {"test_name": "TEST-001"}  # Missing required fields
        is_valid, errors = protocol.validate_parameters(params)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_parameters_out_of_range(self):
        """Test parameter validation with out of range values."""
        protocol = PID001Protocol()
        params = {
            "test_name": "TEST-001",
            "module_id": "MOD-001",
            "test_voltage": -2000,  # Out of range
            "test_duration": 96
        }
        is_valid, errors = protocol.validate_parameters(params)
        assert is_valid is False
        assert any("voltage" in err.lower() for err in errors)

    def test_create_test_execution(self, sample_test_parameters):
        """Test test execution creation."""
        protocol = PID001Protocol()
        test_exec = protocol.create_test_execution("protocol-id-123", sample_test_parameters)

        assert isinstance(test_exec, TestExecution)
        assert test_exec.test_name == sample_test_parameters["test_name"]
        assert test_exec.module_id == sample_test_parameters["module_id"]
        assert test_exec.protocol_id == "protocol-id-123"

    def test_simulate_measurement(self):
        """Test measurement simulation."""
        protocol = PID001Protocol()
        measurement = protocol.simulate_measurement(10.0, -1000, base_leakage=1.0)

        assert "timestamp" in measurement
        assert "elapsed_time" in measurement
        assert "leakage_current" in measurement
        assert "voltage" in measurement
        assert measurement["elapsed_time"] == 10.0
        assert measurement["voltage"] == -1000
        assert measurement["leakage_current"] >= 0

    def test_process_measurement(self, sample_test_parameters):
        """Test measurement processing."""
        protocol = PID001Protocol()
        test_exec = protocol.create_test_execution("protocol-id-123", sample_test_parameters)
        test_exec.id = "test-exec-123"

        tracker = LeakageTracker()
        measurement_data = {
            "timestamp": datetime.utcnow(),
            "elapsed_time": 5.0,
            "leakage_current": 2.5,
            "voltage": -1000,
            "temperature": 85.0,
            "humidity": 85.0,
            "power_degradation": 0.5
        }

        measurement, event = protocol.process_measurement(test_exec, measurement_data, tracker)

        assert isinstance(measurement, Measurement)
        assert measurement.elapsed_time == 5.0
        assert measurement.leakage_current == 2.5
        assert event is None  # No anomaly

    def test_perform_qc_checks_pass(self):
        """Test QC checks with passing measurements."""
        protocol = PID001Protocol()

        # Create sample measurements
        measurements = []
        for i in range(10):
            m = Measurement(
                test_execution_id="test-123",
                timestamp=datetime.utcnow(),
                elapsed_time=float(i),
                leakage_current=2.0 + i * 0.1,  # Low leakage
                voltage=-1000,
                power_degradation=0.5 + i * 0.05
            )
            measurements.append(m)

        qc_status, qc_checks = protocol.perform_qc_checks(measurements, {})

        from src.models.protocol import QCStatus
        assert qc_status == QCStatus.PASS
        assert len(qc_checks) > 0

    def test_perform_qc_checks_fail(self):
        """Test QC checks with failing measurements."""
        protocol = PID001Protocol()

        # Create sample measurements with high leakage
        measurements = []
        for i in range(10):
            m = Measurement(
                test_execution_id="test-123",
                timestamp=datetime.utcnow(),
                elapsed_time=float(i),
                leakage_current=15.0,  # High leakage (exceeds critical)
                voltage=-1000,
                power_degradation=1.0
            )
            measurements.append(m)

        qc_status, qc_checks = protocol.perform_qc_checks(measurements, {})

        from src.models.protocol import QCStatus
        assert qc_status == QCStatus.FAIL

    def test_generate_results_summary(self):
        """Test results summary generation."""
        protocol = PID001Protocol()

        measurements = []
        for i in range(10):
            m = Measurement(
                test_execution_id="test-123",
                timestamp=datetime.utcnow(),
                elapsed_time=float(i),
                leakage_current=2.0 + i * 0.1,
                voltage=-1000,
                power_degradation=0.5 + i * 0.05
            )
            measurements.append(m)

        from src.models.protocol import QCStatus, QCCheck
        qc_checks = [
            QCCheck(
                check_name="Test Check",
                check_type="leakage_current",
                status=QCStatus.PASS,
                measured_value=2.5,
                threshold_value=10.0,
                message="Test passed"
            )
        ]

        summary = protocol.generate_results_summary(measurements, qc_checks, QCStatus.PASS)

        assert "total_measurements" in summary
        assert summary["total_measurements"] == 10
        assert "average_leakage_current" in summary
        assert "max_leakage_current" in summary
        assert "qc_status" in summary
        assert "compliance" in summary
        assert summary["compliance"]["iec_62804_compliant"] is True

    def test_get_chart_data(self):
        """Test chart data preparation."""
        protocol = PID001Protocol()

        measurements = []
        for i in range(5):
            m = Measurement(
                test_execution_id="test-123",
                timestamp=datetime.utcnow(),
                elapsed_time=float(i),
                leakage_current=2.0 + i * 0.1,
                voltage=-1000,
                temperature=85.0,
                humidity=85.0,
                power_degradation=0.5
            )
            measurements.append(m)

        chart_data = protocol.get_chart_data(measurements)

        assert "elapsed_time" in chart_data
        assert "leakage_current" in chart_data
        assert "power_degradation" in chart_data
        assert len(chart_data["elapsed_time"]) == 5
        assert len(chart_data["leakage_current"]) == 5
