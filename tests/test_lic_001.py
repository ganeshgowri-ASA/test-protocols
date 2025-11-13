"""
Comprehensive tests for LIC-001 Low Irradiance Conditions protocol
"""

import pytest
import json
from pathlib import Path
import numpy as np

from protocols.lic_001 import LIC001Protocol, LIC001Analyzer, LIC001Validator
from core.utils import find_max_power_point, calculate_fill_factor, calculate_efficiency


class TestLIC001Protocol:
    """Test LIC-001 Protocol implementation"""

    def test_protocol_initialization(self):
        """Test protocol initialization"""
        protocol = LIC001Protocol()

        assert protocol.PROTOCOL_ID == "LIC-001"
        assert protocol.VERSION == "1.0.0"
        assert protocol.STANDARD == "IEC 61215-1:2021"
        assert protocol.CATEGORY == "PERFORMANCE"
        assert protocol.REQUIRED_IRRADIANCE_LEVELS == [200, 400, 600, 800]
        assert protocol.TARGET_TEMPERATURE == 25.0

    def test_protocol_metadata(self):
        """Test protocol metadata"""
        protocol = LIC001Protocol()
        metadata = protocol.metadata

        assert metadata.protocol_id == "LIC-001"
        assert metadata.name == "Low Irradiance Conditions Test"
        assert metadata.standard == "IEC 61215-1:2021"
        assert metadata.category == "PERFORMANCE"

    def test_schema_loading(self):
        """Test JSON schema loading"""
        protocol = LIC001Protocol()

        assert protocol.schema is not None
        assert "$schema" in protocol.schema
        assert protocol.schema["title"] == "LIC-001 Low Irradiance Conditions Test"

    def test_create_test_run(self, sample_info):
        """Test test run creation"""
        protocol = LIC001Protocol()

        test_run = protocol.create_test_run(
            sample_id="TEST-001",
            sample_info=sample_info,
            operator="Test Operator"
        )

        assert test_run["protocol_info"]["protocol_id"] == "LIC-001"
        assert test_run["sample_info"]["sample_id"] == "TEST-001"
        assert test_run["test_conditions"]["temperature"] == 25.0
        assert test_run["test_conditions"]["operator"] == "Test Operator"

        # Check all irradiance levels have measurement templates
        for irr in [200, 400, 600, 800]:
            assert str(irr) in test_run["measurements"]

    def test_validate_inputs_valid(self, complete_test_data):
        """Test input validation with valid data"""
        protocol = LIC001Protocol()

        is_valid, errors = protocol.validate_inputs(complete_test_data)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_inputs_missing_sample_id(self, complete_test_data):
        """Test validation fails with missing sample ID"""
        protocol = LIC001Protocol()

        # Remove sample_id
        complete_test_data["sample_info"]["sample_id"] = ""

        is_valid, errors = protocol.validate_inputs(complete_test_data)

        assert is_valid is False
        assert any("sample_id" in err.lower() for err in errors)

    def test_validate_inputs_wrong_temperature(self, complete_test_data):
        """Test validation fails with wrong temperature"""
        protocol = LIC001Protocol()

        # Set temperature outside tolerance
        complete_test_data["test_conditions"]["temperature"] = 30.0

        is_valid, errors = protocol.validate_inputs(complete_test_data)

        assert is_valid is False
        assert any("temperature" in err.lower() for err in errors)

    def test_calculate_results(self, complete_test_data):
        """Test results calculation"""
        protocol = LIC001Protocol()

        results = protocol.calculate_results(complete_test_data)

        assert "by_irradiance" in results
        assert "summary" in results

        # Check results for each irradiance level
        for irr in [200, 400, 600, 800]:
            assert str(irr) in results["by_irradiance"]
            level_results = results["by_irradiance"][str(irr)]

            assert "pmax" in level_results
            assert "vmp" in level_results
            assert "imp" in level_results
            assert "voc" in level_results
            assert "isc" in level_results
            assert "fill_factor" in level_results
            assert "efficiency" in level_results
            assert "quality_indicators" in level_results

            # Check reasonable values
            assert level_results["pmax"] > 0
            assert 0 < level_results["fill_factor"] <= 1
            assert 0 < level_results["efficiency"] <= 100

    def test_calculate_results_scaling(self, complete_test_data):
        """Test that power scales with irradiance"""
        protocol = LIC001Protocol()

        results = protocol.calculate_results(complete_test_data)

        # Extract Pmax values
        pmax_200 = results["by_irradiance"]["200"]["pmax"]
        pmax_400 = results["by_irradiance"]["400"]["pmax"]
        pmax_800 = results["by_irradiance"]["800"]["pmax"]

        # Power should scale approximately linearly with irradiance
        # 400 W/m² should give ~2x the power of 200 W/m²
        ratio_400_200 = pmax_400 / pmax_200
        assert 1.8 < ratio_400_200 < 2.2  # Allow 10% tolerance

        # 800 W/m² should give ~4x the power of 200 W/m²
        ratio_800_200 = pmax_800 / pmax_200
        assert 3.6 < ratio_800_200 < 4.4  # Allow 10% tolerance

    def test_finalize_test_run(self, complete_test_data):
        """Test test run finalization"""
        protocol = LIC001Protocol()

        finalized = protocol.finalize_test_run(complete_test_data)

        assert "data_hash" in finalized["metadata"]
        assert len(finalized["metadata"]["data_hash"]) == 64  # SHA256 hash length
        assert "updated_at" in finalized["metadata"]


class TestLIC001Analyzer:
    """Test LIC-001 Analyzer"""

    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        analyzer = LIC001Analyzer()
        assert analyzer is not None

    def test_analyze_iv_curve(self, sample_iv_curve):
        """Test I-V curve analysis"""
        analyzer = LIC001Analyzer()

        voltage = sample_iv_curve["voltage"]
        current = sample_iv_curve["current"]

        results = analyzer.analyze_iv_curve(
            voltage=voltage,
            current=current,
            irradiance=200.0,
            temperature=25.0,
            module_area=0.65
        )

        assert "pmax" in results
        assert "vmp" in results
        assert "imp" in results
        assert "voc" in results
        assert "isc" in results
        assert "fill_factor" in results
        assert "efficiency" in results

        # Check reasonable values
        assert results["pmax"] > 0
        assert results["voc"] > 0
        assert results["isc"] > 0
        assert 0 < results["fill_factor"] <= 1
        assert results["efficiency"] > 0

    def test_find_voc(self, sample_iv_curve):
        """Test Voc finding"""
        analyzer = LIC001Analyzer()

        voltage = sample_iv_curve["voltage"]
        current = sample_iv_curve["current"]

        voc = analyzer._find_voc(voltage, current)

        # Voc should be close to the expected value (0.6V)
        assert 0.55 < voc < 0.65

    def test_find_isc(self, sample_iv_curve):
        """Test Isc finding"""
        analyzer = LIC001Analyzer()

        voltage = sample_iv_curve["voltage"]
        current = sample_iv_curve["current"]

        isc = analyzer._find_isc(voltage, current)

        # Isc should be close to the expected value (8.5A)
        assert 8.0 < isc < 9.0

    def test_assess_curve_quality_good(self, sample_iv_curve):
        """Test quality assessment for good curve"""
        analyzer = LIC001Analyzer()

        voltage = sample_iv_curve["voltage"]
        current = sample_iv_curve["current"]

        quality = analyzer.assess_curve_quality(voltage, current)

        assert "curve_quality" in quality
        assert "data_quality_score" in quality
        assert quality["curve_quality"] in ["excellent", "good"]
        assert quality["data_quality_score"] >= 75

    def test_assess_curve_quality_few_points(self):
        """Test quality assessment with too few points"""
        analyzer = LIC001Analyzer()

        # Only 5 points
        voltage = [0, 0.15, 0.3, 0.45, 0.6]
        current = [8.5, 8.0, 6.0, 3.0, 0]

        quality = analyzer.assess_curve_quality(voltage, current)

        assert quality["data_quality_score"] < 100
        assert any("few points" in issue.lower() for issue in quality["issues"])

    def test_assess_curve_quality_non_monotonic(self):
        """Test quality assessment with non-monotonic voltage"""
        analyzer = LIC001Analyzer()

        # Non-monotonic voltage
        voltage = [0, 0.2, 0.15, 0.3, 0.4, 0.5, 0.6]  # 0.15 breaks monotonicity
        current = [8.5, 8.0, 8.2, 7.0, 5.0, 2.0, 0]

        quality = analyzer.assess_curve_quality(voltage, current)

        assert quality["data_quality_score"] < 100
        assert any("monotonic" in issue.lower() for issue in quality["issues"])

    def test_compare_performance(self, complete_measurements):
        """Test performance comparison across irradiance levels"""
        analyzer = LIC001Analyzer()

        # First analyze each level
        results_by_irradiance = {}
        for irr_key, measurement in complete_measurements.items():
            iv_curve = measurement["iv_curve"]
            results_by_irradiance[irr_key] = analyzer.analyze_iv_curve(
                voltage=iv_curve["voltage"],
                current=iv_curve["current"],
                irradiance=measurement["actual_irradiance"],
                temperature=measurement["actual_temperature"],
                module_area=0.65
            )

        # Compare performance
        comparison = analyzer.compare_performance(results_by_irradiance)

        assert "linearity" in comparison
        assert "efficiency_variation" in comparison
        assert "fill_factor_variation" in comparison

        # Check linearity results
        linearity = comparison["linearity"]
        assert "r_squared" in linearity
        assert "linearity" in linearity
        assert linearity["r_squared"] > 0.95  # Should be highly linear


class TestLIC001Validator:
    """Test LIC-001 Validator"""

    def test_validator_initialization(self):
        """Test validator initialization"""
        validator = LIC001Validator()
        assert validator is not None

    def test_validate_all_valid(self, complete_test_data):
        """Test validation of valid data"""
        validator = LIC001Validator()

        is_valid, errors = validator.validate_all(complete_test_data)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_protocol_info(self):
        """Test protocol info validation"""
        validator = LIC001Validator()

        # Valid protocol info
        protocol_info = {
            "protocol_id": "LIC-001",
            "standard": "IEC 61215-1:2021"
        }

        errors = validator._validate_protocol_info(protocol_info)
        assert len(errors) == 0

        # Invalid protocol ID
        protocol_info["protocol_id"] = "WRONG-001"
        errors = validator._validate_protocol_info(protocol_info)
        assert len(errors) > 0
        assert any("protocol id" in err.lower() for err in errors)

    def test_validate_sample_info(self):
        """Test sample info validation"""
        validator = LIC001Validator()

        # Valid sample info
        sample_info = {
            "sample_id": "TEST-001",
            "module_type": "Test Module",
            "module_area": 0.65
        }

        errors = validator._validate_sample_info(sample_info)
        assert len(errors) == 0

        # Missing sample_id
        sample_info["sample_id"] = ""
        errors = validator._validate_sample_info(sample_info)
        assert len(errors) > 0

    def test_validate_test_conditions(self):
        """Test conditions validation"""
        validator = LIC001Validator()

        # Valid conditions
        conditions = {
            "temperature": 25.0,
            "irradiance_levels": [200, 400, 600, 800],
            "spectrum": "AM1.5G"
        }

        errors = validator._validate_test_conditions(conditions)
        assert len(errors) == 0

        # Invalid temperature
        conditions["temperature"] = 30.0
        errors = validator._validate_test_conditions(conditions)
        assert len(errors) > 0
        assert any("temperature" in err.lower() for err in errors)

    def test_validate_measurements(self, complete_measurements):
        """Test measurements validation"""
        validator = LIC001Validator()

        errors = validator._validate_measurements(complete_measurements)
        assert len(errors) == 0

    def test_validate_measurements_missing_level(self, complete_measurements):
        """Test validation fails with missing irradiance level"""
        validator = LIC001Validator()

        # Remove one level
        del complete_measurements["400"]

        errors = validator._validate_measurements(complete_measurements)
        assert len(errors) > 0
        assert any("400" in err for err in errors)

    def test_validate_iv_curve(self, sample_iv_curve):
        """Test I-V curve validation"""
        validator = LIC001Validator()

        iv_curve = {
            "voltage": sample_iv_curve["voltage"],
            "current": sample_iv_curve["current"]
        }

        errors = validator._validate_iv_curve(iv_curve, 200.0, 25.0)
        assert len(errors) == 0

    def test_validate_iv_curve_too_few_points(self):
        """Test I-V curve validation with too few points"""
        validator = LIC001Validator()

        iv_curve = {
            "voltage": [0, 0.3, 0.6],
            "current": [8.5, 5.0, 0]
        }

        errors = validator._validate_iv_curve(iv_curve, 200.0, 25.0)
        assert len(errors) > 0
        assert any("points" in err.lower() for err in errors)

    def test_validate_iv_curve_length_mismatch(self):
        """Test I-V curve validation with mismatched array lengths"""
        validator = LIC001Validator()

        iv_curve = {
            "voltage": [0, 0.3, 0.6],
            "current": [8.5, 5.0]  # One less point
        }

        errors = validator._validate_iv_curve(iv_curve, 200.0, 25.0)
        assert len(errors) > 0
        assert any("length" in err.lower() for err in errors)


class TestUtilityFunctions:
    """Test utility functions"""

    def test_find_max_power_point(self, sample_iv_curve):
        """Test maximum power point finding"""
        voltage = sample_iv_curve["voltage"]
        current = sample_iv_curve["current"]

        mpp = find_max_power_point(voltage, current)

        assert "vmp" in mpp
        assert "imp" in mpp
        assert "pmax" in mpp

        assert mpp["pmax"] > 0
        assert mpp["vmp"] > 0
        assert mpp["imp"] > 0

        # Pmax should equal Vmp * Imp
        assert abs(mpp["pmax"] - (mpp["vmp"] * mpp["imp"])) < 0.001

    def test_calculate_fill_factor(self):
        """Test fill factor calculation"""
        voc = 0.6
        isc = 8.5
        pmax = 4.0

        ff = calculate_fill_factor(voc, isc, pmax)

        assert 0 < ff <= 1
        expected_ff = pmax / (voc * isc)
        assert abs(ff - expected_ff) < 0.001

    def test_calculate_efficiency(self):
        """Test efficiency calculation"""
        pmax = 100.0  # W
        irradiance = 1000.0  # W/m²
        area = 0.65  # m²

        efficiency = calculate_efficiency(pmax, irradiance, area)

        assert 0 < efficiency <= 1
        expected_eff = pmax / (irradiance * area)
        assert abs(efficiency - expected_eff) < 0.001


class TestVisualization:
    """Test visualization generation"""

    def test_create_all_plots(self, complete_test_data):
        """Test creating all visualizations"""
        protocol = LIC001Protocol()

        # Calculate results first
        results = protocol.calculate_results(complete_test_data)
        complete_test_data["results"] = results

        # Generate visualizations
        plots = protocol.generate_visualizations(complete_test_data)

        assert "iv_curves" in plots
        assert "iv_curves_all" in plots
        assert "power_curves" in plots
        assert "performance_summary" in plots
        assert "irradiance_response" in plots
        assert "fill_factor_comparison" in plots

        # Check that plots are Plotly figures
        for plot_name, plot_obj in plots.items():
            assert hasattr(plot_obj, "data")
            assert hasattr(plot_obj, "layout")


class TestIntegration:
    """Integration tests for complete workflow"""

    def test_complete_workflow(self, sample_info, test_conditions, complete_measurements):
        """Test complete workflow from test creation to results"""
        protocol = LIC001Protocol()

        # 1. Create test run
        test_run = protocol.create_test_run(
            sample_id="TEST-001",
            sample_info=sample_info,
            operator="Test Operator"
        )

        assert test_run is not None

        # 2. Update with actual measurements
        test_run["measurements"] = complete_measurements

        # 3. Validate inputs
        is_valid, errors = protocol.validate_inputs(test_run)
        assert is_valid is True

        # 4. Calculate results
        results = protocol.calculate_results(test_run)
        assert "by_irradiance" in results
        assert "summary" in results

        # 5. Validate results
        is_valid, errors = protocol.validator.validate_results(results)
        assert is_valid is True

        # 6. Finalize
        finalized = protocol.finalize_test_run(test_run)
        assert "data_hash" in finalized["metadata"]

    def test_data_traceability(self, complete_test_data):
        """Test data traceability with hash"""
        protocol = LIC001Protocol()

        # Finalize twice with same data
        finalized1 = protocol.finalize_test_run(complete_test_data.copy())
        finalized2 = protocol.finalize_test_run(complete_test_data.copy())

        # Hashes should be the same for identical data
        assert finalized1["metadata"]["data_hash"] == finalized2["metadata"]["data_hash"]

        # Modify data
        modified = complete_test_data.copy()
        modified["sample_info"]["sample_id"] = "MODIFIED-001"
        finalized3 = protocol.finalize_test_run(modified)

        # Hash should be different
        assert finalized1["metadata"]["data_hash"] != finalized3["metadata"]["data_hash"]
