"""Integration tests for TRACK-001 protocol."""

import pytest
from datetime import datetime
import math

from src.tests.track.track_001.protocol import TRACK001Protocol
from src.tests.track.track_001.test_runner import TRACK001TestRunner
from src.tests.track.track_001.analysis import TRACK001Analyzer


def test_track001_initialization(track001_config):
    """Test TRACK-001 protocol initialization."""
    protocol = TRACK001Protocol(track001_config)

    assert protocol.config.protocol_id == "TRACK-001"
    assert protocol.tracking_mode == "dual_axis"
    assert len(protocol.metrics) == 3


def test_track001_sun_position_calculation(track001_config):
    """Test sun position calculation."""
    protocol = TRACK001Protocol(track001_config)

    # Test at known time
    test_time = datetime(2025, 6, 21, 12, 0, 0)  # Summer solstice, noon
    latitude = 40.0
    longitude = -105.0

    sun_pos = protocol.calculate_sun_position(test_time, latitude, longitude)

    assert 'azimuth' in sun_pos
    assert 'elevation' in sun_pos
    assert 0 <= sun_pos['azimuth'] <= 360
    assert -90 <= sun_pos['elevation'] <= 90


def test_track001_tracking_error_calculation(track001_config):
    """Test tracking error calculation."""
    protocol = TRACK001Protocol(track001_config)

    # Perfect tracking - error should be 0
    error = protocol.calculate_tracking_error(180.0, 45.0, 180.0, 45.0)
    assert abs(error) < 0.01

    # Some deviation
    error = protocol.calculate_tracking_error(180.0, 45.0, 182.0, 46.0)
    assert error > 0


def test_track001_measurement_validation(track001_config):
    """Test measurement validation."""
    protocol = TRACK001Protocol(track001_config)

    # Valid angle
    is_valid, quality = protocol.validate_measurement('azimuth_angle', 180.0)
    assert is_valid is True
    assert quality == 'good'

    # Invalid angle (out of range)
    is_valid, quality = protocol.validate_measurement('azimuth_angle', 500.0)
    assert is_valid is False
    assert quality == 'bad'


def test_track001_expected_measurement_count(track001_config):
    """Test expected measurement count calculation."""
    protocol = TRACK001Protocol(track001_config)

    expected_count = protocol.get_expected_measurement_count()

    # 1 hour / 5 minutes = 12 measurements per metric
    # 3 metrics = 36 total measurements
    assert expected_count == 36


def test_track001_performance_thresholds(track001_config):
    """Test performance threshold retrieval."""
    protocol = TRACK001Protocol(track001_config)

    thresholds = protocol.get_performance_thresholds()

    assert 'tracking_accuracy' in thresholds
    assert thresholds['tracking_accuracy'] == 2.0


def test_track001_test_runner_initialization(track001_config):
    """Test TRACK-001 test runner initialization."""
    protocol = TRACK001Protocol(track001_config)
    runner = TRACK001TestRunner(protocol)

    assert runner.protocol == protocol
    assert runner.is_running is False


def test_track001_analyzer_tracking_performance(track001_config):
    """Test TRACK-001 analyzer tracking performance analysis."""
    qc_criteria = track001_config.qc_criteria
    analysis_methods = track001_config.analysis_methods

    analyzer = TRACK001Analyzer(qc_criteria, analysis_methods)

    # Create sample tracking error measurements
    measurements = []
    base_time = datetime.now()

    for i in range(20):
        measurements.append({
            'run_id': 'TEST-RUN',
            'timestamp': base_time,
            'metric_name': 'tracking_error',
            'metric_value': 1.0 + i * 0.05,  # Values 1.0 to 1.95
            'quality_flag': 'good'
        })

    results = analyzer.analyze_tracking_performance(measurements)

    assert 'mean_error' in results
    assert 'max_error' in results
    assert 'percentile_95' in results
    assert 'pass_fail' in results


def test_track001_analyzer_power_consumption(track001_config):
    """Test power consumption analysis."""
    analyzer = TRACK001Analyzer(
        track001_config.qc_criteria,
        track001_config.analysis_methods
    )

    measurements = []
    base_time = datetime.now()

    for i in range(20):
        measurements.append({
            'run_id': 'TEST-RUN',
            'timestamp': base_time,
            'metric_name': 'power_consumption',
            'metric_value': 100.0 + i * 2,
            'quality_flag': 'good'
        })

    results = analyzer.analyze_power_consumption(measurements)

    assert 'mean_power' in results
    assert 'max_power' in results
    assert 'total_energy_wh' in results


def test_track001_analyzer_anomaly_detection(track001_config):
    """Test anomaly detection."""
    analyzer = TRACK001Analyzer(
        track001_config.qc_criteria,
        track001_config.analysis_methods
    )

    measurements = []
    base_time = datetime.now()

    # Normal data with outliers
    for i in range(20):
        value = 1.0 if i != 10 else 100.0  # One outlier
        measurements.append({
            'run_id': 'TEST-RUN',
            'timestamp': base_time,
            'metric_name': 'tracking_error',
            'metric_value': value,
            'quality_flag': 'good'
        })

    anomalies = analyzer.identify_anomalies(measurements)

    assert isinstance(anomalies, list)
    # Should detect the outlier
    outlier_anomalies = [a for a in anomalies if a['type'] == 'outlier']
    assert len(outlier_anomalies) > 0


def test_track001_end_to_end_simulated(track001_config, test_db):
    """Test end-to-end TRACK-001 execution with simulated data."""
    # This is a lightweight version that completes quickly
    # Modify duration for faster testing
    track001_config.test_parameters['duration'] = {'value': 1, 'unit': 'minutes'}
    track001_config.test_parameters['sample_interval'] = {'value': 10, 'unit': 'seconds'}

    protocol = TRACK001Protocol(track001_config, db_manager=test_db)
    runner = TRACK001TestRunner(protocol)

    # Run test (this will complete quickly with modified duration)
    run_id = runner.run_test(
        data_source="simulated",
        operator="Test Suite",
        sample_id="TEST-TRACKER",
        latitude=40.0,
        longitude=-105.0
    )

    assert run_id is not None
    assert run_id.startswith("TRACK-001")

    # Check that measurements were recorded
    measurements = test_db.get_measurements(run_id)
    assert len(measurements) > 0

    # Check summary
    summary = protocol.get_test_summary()
    assert summary is not None
    assert summary['status'] == 'completed'
