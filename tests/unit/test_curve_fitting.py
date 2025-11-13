"""Unit tests for curve fitting models."""

import pytest
import numpy as np

from analysis import CurveFitter, ASHRAEModel, PhysicalModel, PolynomialModel


def test_ashrae_model():
    """Test ASHRAE model."""
    model = ASHRAEModel()

    angles = np.array([0, 30, 60])
    iam_values = model.function(angles, 0.05)

    # IAM at 0° should be 1.0
    assert abs(iam_values[0] - 1.0) < 0.001

    # IAM should decrease with angle
    assert iam_values[0] > iam_values[1] > iam_values[2]


def test_physical_model():
    """Test physical model."""
    model = PhysicalModel()

    angles = np.array([0, 30, 60])
    iam_values = model.function(angles, 0.16)

    # IAM at 0° should be 1.0
    assert abs(iam_values[0] - 1.0) < 0.001

    # IAM should decrease with angle
    assert iam_values[0] > iam_values[1] > iam_values[2]


def test_polynomial_model():
    """Test polynomial model."""
    model = PolynomialModel(degree=4)

    angles = np.array([0, 30, 60])
    params = [-0.1, -0.05, -0.02, -0.01]  # 4 parameters
    iam_values = model.function(angles, *params)

    # Values should be reasonable
    assert all(0 <= iam <= 1.2 for iam in iam_values)


def test_curve_fitter_initialization(sample_iam_curve):
    """Test curve fitter initialization."""
    fitter = CurveFitter(sample_iam_curve)

    assert len(fitter.angles) == len(sample_iam_curve)
    assert len(fitter.iam_values) == len(sample_iam_curve)


def test_fit_ashrae_model(sample_iam_curve):
    """Test fitting ASHRAE model."""
    fitter = CurveFitter(sample_iam_curve)
    model = ASHRAEModel()

    result = fitter.fit_model(model)

    assert result["success"]
    assert "b0" in result["parameters"]
    assert result["r_squared"] > 0.8  # Should fit reasonably well
    assert result["rmse"] < 0.1


def test_fit_all_models(sample_iam_curve):
    """Test fitting all models."""
    fitter = CurveFitter(sample_iam_curve)

    results = fitter.fit_all_models()

    assert "ashrae" in results
    assert "physical" in results
    assert "polynomial" in results

    # All should succeed
    assert results["ashrae"]["success"]
    assert results["physical"]["success"]
    assert results["polynomial"]["success"]


def test_select_best_model(sample_iam_curve):
    """Test selecting best model."""
    fitter = CurveFitter(sample_iam_curve)
    results = fitter.fit_all_models()

    best_name, best_result = fitter.select_best_model(results, criterion="r_squared")

    assert best_name in ["ashrae", "physical", "polynomial"]
    assert best_result["success"]
    assert best_result["r_squared"] > 0


def test_predict_with_model(sample_iam_curve):
    """Test prediction with fitted model."""
    fitter = CurveFitter(sample_iam_curve)
    model = ASHRAEModel()

    result = fitter.fit_model(model)
    parameters = result["parameters"]

    # Predict at new angles
    new_angles = np.array([5, 15, 25])
    predicted = fitter.predict(model, parameters, new_angles)

    assert len(predicted) == len(new_angles)
    assert all(0 <= iam <= 1.0 for iam in predicted)


def test_generate_smooth_curve(sample_iam_curve):
    """Test generating smooth curve."""
    fitter = CurveFitter(sample_iam_curve)
    model = ASHRAEModel()

    result = fitter.fit_model(model)
    parameters = result["parameters"]

    smooth_curve = fitter.generate_smooth_curve(model, parameters, num_points=100)

    assert len(smooth_curve) == 100
    assert smooth_curve[0]["angle"] == 0
    assert smooth_curve[-1]["angle"] == 90
    assert all(point["fitted"] for point in smooth_curve)


def test_fit_quality_metrics(sample_iam_curve):
    """Test fit quality metrics."""
    fitter = CurveFitter(sample_iam_curve)
    model = ASHRAEModel()

    result = fitter.fit_model(model)

    assert "r_squared" in result
    assert "rmse" in result
    assert "mae" in result
    assert "fitted_values" in result
    assert "residuals" in result

    # Metrics should be reasonable
    assert 0 <= result["r_squared"] <= 1
    assert result["rmse"] >= 0
    assert result["mae"] >= 0


def test_polynomial_different_degrees():
    """Test polynomial model with different degrees."""
    angles = np.array([0, 30, 60, 90])
    iam_values = np.array([1.0, 0.95, 0.85, 0.1])

    iam_curve = [
        {"angle": angle, "iam": iam}
        for angle, iam in zip(angles, iam_values)
    ]

    fitter = CurveFitter(iam_curve)

    # Test degree 2
    model2 = PolynomialModel(degree=2)
    result2 = fitter.fit_model(model2)
    assert result2["success"]

    # Test degree 3
    model3 = PolynomialModel(degree=3)
    result3 = fitter.fit_model(model3)
    assert result3["success"]

    # Test degree 4
    model4 = PolynomialModel(degree=4)
    result4 = fitter.fit_model(model4)
    assert result4["success"]
