"""Tests for ENER-001 Energy Rating Test protocol."""

import pytest
import pandas as pd
import numpy as np

from src.test_protocols.protocols.ener_001 import ENER001Protocol
from src.test_protocols.core.test_runner import TestRunner


class TestENER001Protocol:
    """Test suite for ENER-001 protocol."""

    def test_protocol_initialization(self):
        """Test protocol initialization."""
        protocol = ENER001Protocol()

        assert protocol.PROTOCOL_ID == "ENER-001"
        assert protocol.VERSION == "1.0.0"
        assert protocol.config is not None
        assert protocol.analyzer is not None
        assert protocol.chart_generator is not None
        assert protocol.qc_checker is not None

    def test_validate_inputs_valid_data(self, sample_iv_data):
        """Test input validation with valid data."""
        protocol = ENER001Protocol()

        is_valid, errors = protocol.validate_inputs(sample_iv_data)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_inputs_missing_columns(self):
        """Test input validation with missing required columns."""
        protocol = ENER001Protocol()

        # Data missing current column
        invalid_data = pd.DataFrame(
            {
                "voltage": [1, 2, 3],
                "irradiance": [1000, 1000, 1000],
                "module_temp": [25, 25, 25],
            }
        )

        is_valid, errors = protocol.validate_inputs(invalid_data)

        assert is_valid is False
        assert len(errors) > 0

    def test_validate_inputs_insufficient_data(self):
        """Test input validation with insufficient data points."""
        protocol = ENER001Protocol()

        # Only 5 data points (minimum is 10)
        insufficient_data = pd.DataFrame(
            {
                "voltage": [1, 2, 3, 4, 5],
                "current": [5, 4, 3, 2, 1],
                "irradiance": [1000, 1000, 1000, 1000, 1000],
                "module_temp": [25, 25, 25, 25, 25],
            }
        )

        is_valid, errors = protocol.validate_inputs(insufficient_data)

        assert is_valid is False
        assert any("Insufficient data points" in error for error in errors)

    def test_run_test_single_condition(self, sample_iv_data):
        """Test running protocol with single test condition."""
        protocol = ENER001Protocol()

        results = protocol.run_test(sample_iv_data)

        assert results is not None
        assert "measurements" in results
        assert "iv_curves" in results
        assert "analysis" in results
        assert "qc_results" in results
        assert "charts" in results

        # Check IV curves
        iv_curves = results["iv_curves"]
        assert len(iv_curves) == 1  # One condition

        # Check first curve
        curve_key = list(iv_curves.keys())[0]
        curve = iv_curves[curve_key]

        assert "pmpp" in curve
        assert "voc" in curve
        assert "isc" in curve
        assert "vmpp" in curve
        assert "impp" in curve
        assert "fill_factor" in curve

        # Validate physical constraints
        assert curve["pmpp"] > 0
        assert curve["voc"] > 0
        assert curve["isc"] > 0
        assert 0 < curve["fill_factor"] < 100

    def test_run_test_multiple_conditions(self, sample_multi_condition_data):
        """Test running protocol with multiple test conditions."""
        protocol = ENER001Protocol()

        results = protocol.run_test(sample_multi_condition_data)

        assert results is not None

        # Check IV curves for multiple conditions
        iv_curves = results["iv_curves"]
        assert len(iv_curves) > 1  # Multiple conditions

        # Check that different irradiances give different results
        powers = [curve["pmpp"] for curve in iv_curves.values()]
        assert len(set(powers)) > 1  # Powers should vary

    def test_extract_iv_curves(self, sample_multi_condition_data):
        """Test IV curve extraction."""
        protocol = ENER001Protocol()

        processed_data = protocol._process_measurements(sample_multi_condition_data)
        iv_curves = protocol._extract_iv_curves(processed_data)

        assert len(iv_curves) > 0

        # Check structure of IV curve
        for key, curve in iv_curves.items():
            assert "irradiance" in curve
            assert "temperature" in curve
            assert "voltage" in curve
            assert "current" in curve
            assert "power" in curve
            assert "voc" in curve
            assert "isc" in curve
            assert "pmpp" in curve
            assert "fill_factor" in curve

            # Validate types
            assert isinstance(curve["voltage"], list)
            assert isinstance(curve["current"], list)
            assert len(curve["voltage"]) == len(curve["current"])

    def test_calculate_fill_factor(self):
        """Test fill factor calculation."""
        protocol = ENER001Protocol()

        # Typical values for a good solar cell
        pmpp = 300.0
        voc = 45.0
        isc = 10.0

        ff = protocol._calculate_fill_factor(pmpp, voc, isc)

        # Fill factor should be reasonable (60-85% for good modules)
        assert 60 <= ff <= 85

        # Test edge cases
        ff_zero = protocol._calculate_fill_factor(0, voc, isc)
        assert ff_zero == 0

        ff_invalid = protocol._calculate_fill_factor(pmpp, 0, isc)
        assert ff_invalid == 0

    def test_temperature_coefficients(self, sample_multi_condition_data):
        """Test temperature coefficient calculation."""
        protocol = ENER001Protocol()

        results = protocol.run_test(sample_multi_condition_data)

        if "analysis" in results and "temperature_coefficients" in results["analysis"]:
            tc = results["analysis"]["temperature_coefficients"]

            # Check that coefficients exist
            assert "gamma_pmax" in tc or "beta_voc" in tc or "alpha_isc" in tc

            # Typical ranges for crystalline silicon
            if "gamma_pmax" in tc:
                # Pmax coefficient should be negative (typically -0.3 to -0.5 %/°C)
                assert tc["gamma_pmax"] < 0

            if "beta_voc" in tc:
                # Voc coefficient should be negative
                assert tc["beta_voc"] < 0

            if "alpha_isc" in tc:
                # Isc coefficient should be slightly positive
                assert tc["alpha_isc"] > 0

    def test_energy_rating_calculation(self, sample_multi_condition_data):
        """Test energy rating calculation."""
        protocol = ENER001Protocol()

        results = protocol.run_test(sample_multi_condition_data)

        assert "analysis" in results
        assert "energy_rating" in results["analysis"]

        energy_rating = results["analysis"]["energy_rating"]

        assert "energy_rating_kWh_per_kWp" in energy_rating
        assert "climate_zone" in energy_rating
        assert "performance_ratio" in energy_rating

        # Energy rating should be positive and reasonable
        er = energy_rating["energy_rating_kWh_per_kWp"]
        assert er > 0
        assert er < 3000  # Should not exceed theoretical maximum

    def test_quality_checks(self, sample_multi_condition_data):
        """Test quality checks."""
        protocol = ENER001Protocol()

        results = protocol.run_test(sample_multi_condition_data)

        assert "qc_results" in results

        qc_results = results["qc_results"]
        assert len(qc_results) > 0

        # Check QC result structure
        for qc in qc_results:
            assert "id" in qc
            assert "name" in qc
            assert "type" in qc
            assert "passed" in qc
            assert "severity" in qc
            assert "message" in qc

    def test_charts_generation(self, sample_multi_condition_data):
        """Test chart generation."""
        protocol = ENER001Protocol()

        results = protocol.run_test(sample_multi_condition_data)

        assert "charts" in results

        charts = results["charts"]

        # Check that expected charts are generated
        expected_charts = [
            "iv_curves",
            "pv_curves",
            "power_vs_irradiance",
            "power_vs_temperature",
            "efficiency_map",
        ]

        for chart_name in expected_charts:
            assert chart_name in charts

    def test_interpolate_performance(self, sample_multi_condition_data):
        """Test performance interpolation."""
        protocol = ENER001Protocol()

        processed_data = protocol._process_measurements(sample_multi_condition_data)
        iv_curves = protocol._extract_iv_curves(processed_data)

        # Interpolate at intermediate point
        target_irr = 700  # Between 600 and 800
        target_temp = 35  # Between 25 and 50

        try:
            interpolated = protocol.interpolate_performance(iv_curves, target_irr, target_temp)

            assert interpolated is not None
            assert "pmpp" in interpolated
            assert "voc" in interpolated
            assert "isc" in interpolated

            # Values should be reasonable
            assert interpolated["pmpp"] > 0
            assert interpolated["voc"] > 0
            assert interpolated["isc"] > 0

        except ValueError:
            # Interpolation may fail with insufficient data
            pass


class TestTestRunner:
    """Test suite for TestRunner with ENER-001."""

    def test_test_runner_initialization(self):
        """Test test runner initialization."""
        protocol = ENER001Protocol()
        runner = TestRunner(protocol)

        assert runner.protocol == protocol
        assert runner.status == "initialized"

    def test_run_test_with_runner(self, sample_iv_data):
        """Test running test through TestRunner."""
        protocol = ENER001Protocol()
        runner = TestRunner(protocol)

        results = runner.run(sample_iv_data)

        assert results is not None
        assert "session_id" in results
        assert "status" in results
        assert results["status"] in ["completed", "completed_with_errors"]

    def test_runner_session_metadata(self, sample_iv_data):
        """Test that runner adds session metadata."""
        protocol = ENER001Protocol()
        runner = TestRunner(protocol)

        results = runner.run(sample_iv_data)

        assert "session_id" in results
        assert "protocol_id" in results
        assert "protocol_version" in results
        assert "start_time" in results
        assert "end_time" in results
        assert "duration_seconds" in results

        assert results["protocol_id"] == "ENER-001"
        assert results["protocol_version"] == "1.0.0"
        assert results["duration_seconds"] >= 0

    def test_runner_handles_invalid_data(self):
        """Test that runner handles invalid data gracefully."""
        protocol = ENER001Protocol()
        runner = TestRunner(protocol)

        # Invalid data (missing required columns)
        invalid_data = pd.DataFrame({"random_column": [1, 2, 3]})

        results = runner.run(invalid_data, validate_inputs=True)

        assert results["status"] == "failed"
        assert "error" in results or "validation_errors" in results
