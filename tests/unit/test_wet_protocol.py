"""Unit tests for WET-001 protocol."""

import pytest
from datetime import datetime

from protocols.wet_leakage_current.protocol import WETLeakageCurrentProtocol
from protocols.wet_leakage_current.analysis import WETAnalyzer
from protocols.base import MeasurementPoint


class TestWETProtocol:
    """Test suite for WET-001 protocol."""

    def test_protocol_initialization(self):
        """Test protocol initialization."""
        protocol = WETLeakageCurrentProtocol()

        assert protocol.protocol_id == "WET-001"
        assert protocol.name == "Wet Leakage Current Test"
        assert protocol.standard == "IEC 61730 MST 02"
        assert protocol.version == "1.0.0"
        assert protocol.schema is not None

    def test_parameter_validation_valid(self, sample_wet001_params):
        """Test validation with valid parameters."""
        protocol = WETLeakageCurrentProtocol()
        result = protocol.validate_parameters(sample_wet001_params)
        assert result is True

    def test_parameter_validation_missing_section(self):
        """Test validation with missing required section."""
        protocol = WETLeakageCurrentProtocol()

        invalid_params = {
            "sample_information": {
                "sample_id": "TEST-001",
                "module_type": "Test Module"
            }
            # Missing test_conditions and environmental_conditions
        }

        with pytest.raises(ValueError, match="Missing required section"):
            protocol.validate_parameters(invalid_params)

    def test_parameter_validation_missing_sample_id(self, sample_wet001_params):
        """Test validation with missing sample_id."""
        protocol = WETLeakageCurrentProtocol()

        params = sample_wet001_params.copy()
        params['sample_information']['sample_id'] = ""

        with pytest.raises(ValueError, match="sample_id is required"):
            protocol.validate_parameters(params)

    def test_parameter_validation_invalid_voltage(self, sample_wet001_params):
        """Test validation with invalid voltage."""
        protocol = WETLeakageCurrentProtocol()

        params = sample_wet001_params.copy()
        params['test_conditions']['test_voltage'] = 6000.0  # Exceeds max

        with pytest.raises(ValueError, match="test_voltage must be"):
            protocol.validate_parameters(params)

    def test_parameter_validation_invalid_electrode_config(self, sample_wet001_params):
        """Test validation with invalid electrode configuration."""
        protocol = WETLeakageCurrentProtocol()

        params = sample_wet001_params.copy()
        params['test_conditions']['electrode_configuration'] = "C"  # Invalid

        with pytest.raises(ValueError, match="electrode_configuration must be"):
            protocol.validate_parameters(params)

    def test_add_measurement(self):
        """Test adding measurements."""
        protocol = WETLeakageCurrentProtocol()

        protocol.add_measurement(
            leakage_current=0.15,
            voltage=1500.0,
            temperature=25.0,
            humidity=90.0
        )

        assert len(protocol.measurements) == 1
        assert protocol.measurements[0].values['leakage_current'] == 0.15

    def test_add_multiple_measurements(self):
        """Test adding multiple measurements."""
        protocol = WETLeakageCurrentProtocol()

        for i in range(5):
            protocol.add_measurement(
                leakage_current=0.1 + (i * 0.01),
                voltage=1500.0,
                temperature=25.0,
                humidity=90.0
            )

        assert len(protocol.measurements) == 5

    def test_insulation_resistance_calculation(self):
        """Test automatic insulation resistance calculation."""
        protocol = WETLeakageCurrentProtocol()

        protocol.add_measurement(
            leakage_current=0.25,  # mA
            voltage=1500.0,  # V
            temperature=25.0,
            humidity=90.0
        )

        measurement = protocol.measurements[0]
        insulation = measurement.values['insulation_resistance']

        # R = V / I = 1500V / 0.00025A = 6,000,000 Ω = 6 MΩ
        expected = 6.0
        assert abs(insulation - expected) < 0.1

    def test_clear_measurements(self):
        """Test clearing measurements."""
        protocol = WETLeakageCurrentProtocol()

        protocol.add_measurement(0.15, 1500.0, 25.0, 90.0)
        protocol.add_measurement(0.16, 1500.0, 25.0, 90.0)

        assert len(protocol.measurements) == 2

        protocol.clear_measurements()
        assert len(protocol.measurements) == 0


class TestWETAnalyzer:
    """Test suite for WET analyzer."""

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        criteria = {
            'max_leakage_current': 0.25,
            'min_insulation_resistance': 400.0,
            'max_voltage_variation': 5.0,
        }

        analyzer = WETAnalyzer(criteria)

        assert analyzer.max_leakage_current == 0.25
        assert analyzer.min_insulation_resistance == 400.0

    def test_analyze_measurements_pass(self, sample_measurements):
        """Test analysis with passing measurements."""
        criteria = {
            'max_leakage_current': 0.30,  # Above all measurements
            'min_insulation_resistance': 400.0,
            'max_voltage_variation': 5.0,
        }

        analyzer = WETAnalyzer(criteria)
        result = analyzer.analyze_measurements(sample_measurements, 1500.0)

        assert result['passed'] is True
        assert 'PASS' in result['summary']
        assert len(result['failure_reasons']) == 0

    def test_analyze_measurements_fail_leakage(self, sample_measurements):
        """Test analysis failing due to high leakage current."""
        criteria = {
            'max_leakage_current': 0.10,  # Below some measurements
            'min_insulation_resistance': 400.0,
            'max_voltage_variation': 5.0,
        }

        analyzer = WETAnalyzer(criteria)
        result = analyzer.analyze_measurements(sample_measurements, 1500.0)

        assert result['passed'] is False
        assert 'FAIL' in result['summary']
        assert any('leakage current' in reason.lower() for reason in result['failure_reasons'])

    def test_analyze_no_measurements(self):
        """Test analysis with no measurements."""
        criteria = {'max_leakage_current': 0.25, 'min_insulation_resistance': 400.0}
        analyzer = WETAnalyzer(criteria)

        result = analyzer.analyze_measurements([], 1500.0)

        assert result['passed'] is False
        assert 'No measurements' in result['summary']

    def test_calculate_statistics(self, sample_measurements):
        """Test statistical calculations."""
        criteria = {'max_leakage_current': 0.30, 'min_insulation_resistance': 400.0}
        analyzer = WETAnalyzer(criteria)

        result = analyzer.analyze_measurements(sample_measurements, 1500.0)

        assert result['max_leakage_current_measured'] > 0
        assert result['min_leakage_current_measured'] > 0
        assert result['average_leakage_current'] > 0
        assert result['std_dev_leakage_current'] >= 0

    def test_detect_anomalies(self, sample_measurements):
        """Test anomaly detection."""
        criteria = {'max_leakage_current': 0.30}
        analyzer = WETAnalyzer(criteria)

        # Add an anomalous measurement
        anomaly = MeasurementPoint(
            timestamp=datetime.now(),
            values={
                'leakage_current': 5.0,  # Very high
                'voltage': 1500.0,
                'temperature': 25.0,
                'humidity': 90.0,
                'insulation_resistance': 100.0,
            }
        )
        measurements = sample_measurements + [anomaly]

        anomalies = analyzer.detect_anomalies(measurements, threshold_std=3.0)

        assert len(anomalies) > 0

    def test_calculate_trending_increasing(self):
        """Test trending detection for increasing values."""
        from datetime import timedelta

        criteria = {'max_leakage_current': 0.30}
        analyzer = WETAnalyzer(criteria)

        # Create measurements with increasing trend
        start = datetime.now()
        measurements = []
        for i in range(10):
            m = MeasurementPoint(
                timestamp=start + timedelta(hours=i),
                values={
                    'leakage_current': 0.1 + (i * 0.02),  # Increasing
                    'voltage': 1500.0,
                    'temperature': 25.0,
                    'humidity': 90.0,
                    'insulation_resistance': 500.0,
                }
            )
            measurements.append(m)

        trending = analyzer.calculate_trending(measurements)

        assert trending['trend'] in ['increasing', 'stable', 'decreasing']

    def test_test_duration_calculation(self, sample_measurements):
        """Test duration calculation."""
        criteria = {'max_leakage_current': 0.30}
        analyzer = WETAnalyzer(criteria)

        result = analyzer.analyze_measurements(sample_measurements, 1500.0)

        assert result['test_duration_hours'] >= 0


class TestProtocolIntegration:
    """Integration tests for the full protocol workflow."""

    def test_full_test_workflow(self, sample_wet001_params):
        """Test complete test workflow."""
        protocol = WETLeakageCurrentProtocol()

        # Validate parameters
        protocol.validate_parameters(sample_wet001_params)

        # Add measurements
        for i in range(10):
            protocol.add_measurement(
                leakage_current=0.15 + (i * 0.01),
                voltage=1500.0,
                temperature=25.0,
                humidity=90.0
            )

        # Analyze
        protocol.parameters = sample_wet001_params
        protocol.analyzer = WETAnalyzer(sample_wet001_params['acceptance_criteria'])

        result = protocol.analyze_results()

        assert 'passed' in result
        assert 'summary' in result
        assert result['measurement_count'] == 10

    def test_report_generation_json(self, sample_wet001_params):
        """Test JSON report generation."""
        protocol = WETLeakageCurrentProtocol()
        protocol.parameters = sample_wet001_params
        protocol.start_time = datetime.now()

        # Add some measurements
        for i in range(5):
            protocol.add_measurement(0.15, 1500.0, 25.0, 90.0)

        # Create test result
        test_result = protocol._create_test_result("TEST-001", "Test Operator")

        # Generate JSON report
        report = protocol.generate_report(test_result, format='json')

        assert isinstance(report, str)
        assert 'TEST-001' in report

        # Validate it's valid JSON
        import json
        data = json.loads(report)
        assert 'test_result' in data
        assert 'measurements' in data
        assert 'parameters' in data
