"""Unit tests for IAM calculator."""

import pytest
import numpy as np

from analysis import IAMCalculator


def test_iam_calculator_initialization(sample_measurements):
    """Test IAM calculator initialization."""
    calculator = IAMCalculator(sample_measurements)

    assert len(calculator.measurements) == len(sample_measurements)
    assert len(calculator.angles) == len(sample_measurements)
    assert len(calculator.powers) == len(sample_measurements)


def test_calculate_iam(sample_measurements):
    """Test IAM calculation."""
    calculator = IAMCalculator(sample_measurements)

    iam_curve = calculator.calculate_iam(metric="pmax", normalization_angle=0.0)

    assert len(iam_curve) == len(sample_measurements)

    # IAM at 0° should be 1.0
    iam_at_0 = next(point for point in iam_curve if point["angle"] == 0)
    assert abs(iam_at_0["iam"] - 1.0) < 0.001

    # IAM should decrease with angle
    iam_values = [point["iam"] for point in iam_curve]
    for i in range(len(iam_values) - 1):
        # Allow some tolerance for the last few points
        if iam_curve[i]["angle"] < 80:
            assert iam_values[i] >= iam_values[i + 1] - 0.1


def test_calculate_iam_different_metrics(sample_measurements):
    """Test IAM calculation with different metrics."""
    calculator = IAMCalculator(sample_measurements)

    iam_pmax = calculator.calculate_iam(metric="pmax")
    iam_isc = calculator.calculate_iam(metric="isc")
    iam_voc = calculator.calculate_iam(metric="voc")

    assert len(iam_pmax) == len(sample_measurements)
    assert len(iam_isc) == len(sample_measurements)
    assert len(iam_voc) == len(sample_measurements)


def test_interpolate_iam(sample_measurements):
    """Test IAM interpolation."""
    calculator = IAMCalculator(sample_measurements)
    iam_curve = calculator.calculate_iam()

    # Interpolate at intermediate angles
    target_angles = [5, 15, 25, 35, 45]
    interpolated = calculator.interpolate_iam(iam_curve, target_angles)

    assert len(interpolated) == len(target_angles)

    for point in interpolated:
        assert "angle" in point
        assert "iam" in point
        assert point["interpolated"] is True


def test_get_statistics(sample_measurements):
    """Test IAM statistics calculation."""
    calculator = IAMCalculator(sample_measurements)
    iam_curve = calculator.calculate_iam()

    stats = calculator.get_statistics(iam_curve)

    assert "mean_iam" in stats
    assert "std_iam" in stats
    assert "min_iam" in stats
    assert "max_iam" in stats
    assert "iam_at_50deg" in stats
    assert "iam_at_60deg" in stats
    assert "iam_at_70deg" in stats
    assert "num_points" in stats

    assert stats["num_points"] == len(iam_curve)
    assert 0 <= stats["mean_iam"] <= 1
    assert 0 <= stats["min_iam"] <= 1
    assert 0 <= stats["max_iam"] <= 1


def test_validate_iam_curve(sample_measurements):
    """Test IAM curve validation."""
    calculator = IAMCalculator(sample_measurements)
    iam_curve = calculator.calculate_iam()

    is_valid, warnings = calculator.validate_iam_curve(iam_curve)

    # Should be valid for sample data
    assert is_valid or len(warnings) < 3  # Allow some minor warnings


def test_calculate_effective_irradiance(sample_measurements):
    """Test effective irradiance calculation."""
    calculator = IAMCalculator(sample_measurements)

    # At 0°, effective should equal GHI * IAM
    eff_irr_0 = calculator.calculate_effective_irradiance(0, 1000, 1.0)
    assert abs(eff_irr_0 - 1000) < 0.1

    # At 60°, effective should be less
    eff_irr_60 = calculator.calculate_effective_irradiance(60, 1000, 0.95)
    assert eff_irr_60 < 1000
    assert eff_irr_60 > 0


def test_iam_calculation_with_correction(sample_measurements):
    """Test IAM calculation with irradiance correction."""
    calculator = IAMCalculator(sample_measurements)

    iam_curve = calculator.calculate_iam_with_correction(
        metric="pmax",
        normalization_angle=0,
        correct_irradiance=True
    )

    assert len(iam_curve) == len(sample_measurements)

    # Check that correction flags are present
    for point in iam_curve:
        assert "irradiance_corrected" in point


def test_iam_full_range_0_to_90(sample_measurements):
    """Test IAM calculation over full 0-90° range."""
    calculator = IAMCalculator(sample_measurements)
    iam_curve = calculator.calculate_iam()

    # Verify full range is covered
    angles = [point["angle"] for point in iam_curve]
    assert min(angles) == 0
    assert max(angles) == 90

    # Verify 10 points (0, 10, 20, ..., 90)
    assert len(iam_curve) == 10

    # IAM at 0° should be 1.0
    assert abs(iam_curve[0]["iam"] - 1.0) < 0.01

    # IAM at 90° should be very low
    assert iam_curve[-1]["iam"] < 0.3


def test_iam_invalid_metric(sample_measurements):
    """Test IAM calculation with invalid metric."""
    calculator = IAMCalculator(sample_measurements)

    with pytest.raises(ValueError):
        calculator.calculate_iam(metric="invalid_metric")
