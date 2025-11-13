"""Integration tests for full IAM-001 workflow."""

import pytest
from pathlib import Path

from protocol_engine import ProtocolLoader, ProtocolValidator, ProtocolExecutor
from analysis import create_analyzer


def test_create_protocol_from_template():
    """Test creating a protocol from template."""
    executor = ProtocolExecutor("iam-001")

    executor.create_protocol(
        **{
            "sample_info.sample_id": "INT-TEST-001",
            "sample_info.module_type": "Test Module",
            "sample_info.technology": "mono-Si"
        }
    )

    protocol_data = executor.get_protocol_data()

    assert protocol_data["protocol_info"]["protocol_id"] == "IAM-001"
    assert protocol_data["sample_info"]["sample_id"] == "INT-TEST-001"


def test_add_measurements_workflow():
    """Test adding measurements workflow."""
    executor = ProtocolExecutor("iam-001")
    executor.create_protocol()

    # Add measurements at different angles (0-90° in 10° steps)
    for angle in range(0, 91, 10):
        # Realistic values that decrease with angle
        isc = 10.0 * (1 - angle / 100)
        voc = 48.0 * (1 - angle / 200)
        pmax = isc * voc * 0.75

        executor.add_measurement(
            angle=float(angle),
            isc=isc,
            voc=voc,
            pmax=pmax,
            irradiance_actual=1000.0,
            temperature_actual=25.0
        )

    measurements = executor.get_measurements()

    assert len(measurements) == 10
    assert measurements[0]["angle"] == 0
    assert measurements[-1]["angle"] == 90


def test_validation_workflow():
    """Test validation workflow."""
    executor = ProtocolExecutor("iam-001")
    executor.create_protocol()

    # Add sufficient measurements
    for angle in [0, 20, 40, 60, 80, 90]:
        executor.add_measurement(
            angle=float(angle),
            isc=10.0 - angle * 0.05,
            voc=48.0,
            pmax=400.0 - angle * 3,
            irradiance_actual=1000.0,
            temperature_actual=25.0
        )

    validation_results = executor.validate_protocol()

    assert validation_results["schema_valid"]
    assert validation_results["measurements_valid"]
    assert validation_results["overall_status"] in ["pass", "pass_with_warnings"]


def test_analysis_workflow():
    """Test analysis workflow."""
    executor = ProtocolExecutor("iam-001")
    executor.create_protocol()

    # Add measurements
    for angle in range(0, 91, 10):
        isc = 10.0 * (1 - angle / 100)
        voc = 48.0
        pmax = 400.0 * (1 - angle / 120)

        executor.add_measurement(
            angle=float(angle),
            isc=isc,
            voc=voc,
            pmax=pmax,
            irradiance_actual=1000.0,
            temperature_actual=25.0
        )

    # Execute analysis
    executor.execute_analysis(create_analyzer)

    analysis_results = executor.get_analysis_results()

    assert "iam_curve" in analysis_results
    assert "fitting_parameters" in analysis_results
    assert "quality_metrics" in analysis_results

    # Check IAM curve
    iam_curve = analysis_results["iam_curve"]
    assert len(iam_curve) == 10

    # Check fitting
    fitting_params = analysis_results["fitting_parameters"]
    assert "model" in fitting_params
    assert "r_squared" in fitting_params
    assert fitting_params["r_squared"] > 0.7  # Should fit reasonably


def test_save_and_load_workflow(temp_dir):
    """Test save and load workflow."""
    executor = ProtocolExecutor("iam-001")
    executor.create_protocol()

    # Add measurements
    for angle in [0, 30, 60, 90]:
        executor.add_measurement(
            angle=float(angle),
            isc=10.0,
            voc=48.0,
            pmax=400.0,
        )

    # Execute analysis
    executor.execute_analysis(create_analyzer)

    # Save
    save_path = temp_dir / "test_protocol.json"
    executor.save_protocol(save_path)

    assert save_path.exists()

    # Load with new executor
    executor2 = ProtocolExecutor("iam-001")
    executor2.load_protocol(save_path)

    loaded_data = executor2.get_protocol_data()
    measurements = executor2.get_measurements()

    assert len(measurements) == 4
    assert "analysis_results" in loaded_data


def test_full_0_to_90_degree_workflow(temp_dir):
    """Test complete workflow with 0-90° angle coverage."""
    executor = ProtocolExecutor("iam-001")

    # Create protocol with sample information
    executor.create_protocol(
        **{
            "sample_info.sample_id": "FULL-TEST-001",
            "sample_info.module_type": "400W Mono-Si",
            "sample_info.manufacturer": "TestCo",
            "sample_info.technology": "mono-Si",
            "sample_info.rated_power": 400.0
        }
    )

    # Add measurements for complete 0-90° range in 10° steps
    import numpy as np

    for angle in range(0, 91, 10):
        angle_rad = np.radians(angle)

        # Simulate realistic behavior
        if angle < 90:
            iam_effect = 1.0 - 0.05 * (1.0 / np.cos(angle_rad) - 1.0)
            iam_effect = max(0.0, iam_effect)
        else:
            iam_effect = 0.1

        isc = 10.0 * iam_effect * np.cos(angle_rad)
        voc = 48.0 * (1.0 - 0.002 * angle)
        pmax = 400.0 * iam_effect * np.cos(angle_rad)

        executor.add_measurement(
            angle=float(angle),
            isc=float(isc),
            voc=float(voc),
            pmax=float(pmax),
            irradiance_actual=1000.0,
            temperature_actual=25.0
        )

    # Validate
    validation_results = executor.validate_protocol()
    assert validation_results["overall_status"] in ["pass", "pass_with_warnings"]

    # Analyze
    executor.execute_analysis(create_analyzer)

    # Get results
    analysis_results = executor.get_analysis_results()

    # Verify IAM curve covers full range
    iam_curve = analysis_results["iam_curve"]
    angles = [point["angle"] for point in iam_curve]

    assert min(angles) == 0
    assert max(angles) == 90
    assert len(iam_curve) == 10

    # Verify IAM values are reasonable
    iam_at_0 = next(p for p in iam_curve if p["angle"] == 0)
    assert abs(iam_at_0["iam"] - 1.0) < 0.05  # Should be ~1.0 at 0°

    iam_at_90 = next(p for p in iam_curve if p["angle"] == 90)
    assert iam_at_90["iam"] < 0.5  # Should be low at 90°

    # Verify fit quality
    assert analysis_results["fitting_parameters"]["r_squared"] > 0.85
    assert analysis_results["quality_metrics"]["data_completeness"] == 100.0

    # Save protocol
    save_path = temp_dir / "full_range_protocol.json"
    executor.save_protocol(save_path)

    assert save_path.exists()

    # Verify file size is reasonable (should contain all data)
    assert save_path.stat().st_size > 1000  # At least 1KB


def test_execution_log():
    """Test execution log tracking."""
    executor = ProtocolExecutor("iam-001")

    executor.create_protocol()
    executor.add_measurement(0, 10, 48, 400)

    execution_log = executor.get_execution_log()

    assert len(execution_log) > 0
    assert any(log["event_type"] == "protocol_created" for log in execution_log)
    assert any(log["event_type"] == "measurement_added" for log in execution_log)


def test_recommended_angles():
    """Test getting recommended test angles."""
    executor = ProtocolExecutor("iam-001")

    recommended = executor.get_recommended_angles()

    assert len(recommended) > 0
    assert 0 in recommended
    assert 90 in recommended
    assert all(0 <= angle <= 90 for angle in recommended)
