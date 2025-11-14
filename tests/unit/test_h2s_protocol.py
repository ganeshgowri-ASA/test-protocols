"""
Unit Tests for H2S-001 Protocol
Tests specific to the hydrogen sulfide exposure protocol
"""

import pytest
import numpy as np
from datetime import datetime, timedelta

from protocols.environmental.h2s_001 import H2S001Protocol
from protocols.base import Criticality


class TestH2S001Protocol:
    """Tests for H2S-001 Protocol Implementation"""

    def test_protocol_initialization(self, h2s_protocol):
        """Test H2S protocol initialization"""
        assert isinstance(h2s_protocol, H2S001Protocol)
        assert h2s_protocol.baseline_measurements == {}
        assert h2s_protocol.post_test_measurements == {}
        assert h2s_protocol.environmental_log == []

    def test_record_baseline_electrical(self, h2s_protocol):
        """Test recording baseline electrical measurements"""
        h2s_protocol.record_baseline_electrical(
            voc=47.5, isc=10.8, vmp=39.2,
            imp=10.2, pmax=400.0, ff=0.78
        )

        assert h2s_protocol.baseline_measurements["Voc"] == 47.5
        assert h2s_protocol.baseline_measurements["Pmax"] == 400.0
        assert "baseline_electrical" in h2s_protocol.test_data

    def test_record_post_test_electrical(self, h2s_protocol):
        """Test recording post-test electrical measurements"""
        h2s_protocol.record_post_test_electrical(
            voc=47.2, isc=10.6, vmp=38.8,
            imp=10.0, pmax=388.0, ff=0.77
        )

        assert h2s_protocol.post_test_measurements["Voc"] == 47.2
        assert h2s_protocol.post_test_measurements["Pmax"] == 388.0
        assert "post_test_electrical" in h2s_protocol.test_data

    def test_record_environmental_data(self, h2s_protocol):
        """Test recording environmental chamber data"""
        timestamp = datetime.now()
        h2s_protocol.record_environmental_data(
            timestamp=timestamp,
            h2s_ppm=10.2,
            temperature_c=40.5,
            humidity_rh=85.2
        )

        assert len(h2s_protocol.environmental_log) == 1
        assert h2s_protocol.environmental_log[0]["h2s_ppm"] == 10.2

    def test_record_insulation_resistance(self, h2s_protocol):
        """Test recording insulation resistance"""
        h2s_protocol.record_insulation_resistance(
            baseline_mohm=500.0,
            post_test_mohm=480.0
        )

        assert "insulation_resistance" in h2s_protocol.test_data
        assert h2s_protocol.test_data["insulation_resistance"]["baseline_MOhm"]["value"] == 500.0

    def test_record_weight_measurements(self, h2s_protocol):
        """Test recording weight measurements"""
        h2s_protocol.record_weight_measurements(
            baseline_kg=22.5,
            post_test_kg=22.6
        )

        weight_change = h2s_protocol.test_data["physical_measurements"]["weight_change_pct"]["value"]
        expected_change = ((22.6 - 22.5) / 22.5) * 100
        assert abs(weight_change - expected_change) < 0.01

    def test_calculate_degradation(self, h2s_protocol, sample_electrical_data):
        """Test degradation calculation"""
        baseline = sample_electrical_data["baseline"]
        post = sample_electrical_data["post_test"]

        h2s_protocol.record_baseline_electrical(**baseline)
        h2s_protocol.record_post_test_electrical(**post)

        degradation = h2s_protocol.calculate_degradation()

        assert "ΔPmax" in degradation
        assert "ΔVoc" in degradation
        assert "ΔIsc" in degradation

        # Check Pmax degradation calculation
        expected_pmax_deg = ((post["pmax"] - baseline["pmax"]) / baseline["pmax"]) * 100
        assert abs(degradation["ΔPmax"] - expected_pmax_deg) < 0.01

    def test_calculate_degradation_missing_data(self, h2s_protocol):
        """Test degradation calculation with missing data"""
        with pytest.raises(ValueError, match="Both baseline and post-test measurements required"):
            h2s_protocol.calculate_degradation()

    def test_analyze_environmental_stability(self, h2s_protocol, sample_environmental_data):
        """Test environmental stability analysis"""
        for entry in sample_environmental_data:
            h2s_protocol.record_environmental_data(**entry)

        analysis = h2s_protocol.analyze_environmental_stability()

        assert "h2s_concentration" in analysis
        assert "temperature" in analysis
        assert "relative_humidity" in analysis
        assert "total_measurements" in analysis

        assert analysis["total_measurements"] == len(sample_environmental_data)

        # Check statistics structure
        h2s_stats = analysis["h2s_concentration"]
        assert "mean" in h2s_stats
        assert "std" in h2s_stats
        assert "percent_within_tolerance" in h2s_stats

    def test_analyze_environmental_stability_empty(self, h2s_protocol):
        """Test environmental stability with no data"""
        analysis = h2s_protocol.analyze_environmental_stability()
        assert "error" in analysis

    def test_analyze_environmental_stability_tolerance(self, h2s_protocol):
        """Test environmental stability tolerance checking"""
        # Create data all within tolerance
        base_time = datetime.now()
        for i in range(10):
            h2s_protocol.record_environmental_data(
                timestamp=base_time + timedelta(minutes=i * 15),
                h2s_ppm=10.0,  # Target is 10 ± 2
                temperature_c=40.0,  # Target is 40 ± 3
                humidity_rh=85.0  # Target is 85 ± 5
            )

        analysis = h2s_protocol.analyze_environmental_stability()

        # All measurements should be within tolerance
        assert analysis["h2s_concentration"]["percent_within_tolerance"] == 100.0
        assert analysis["h2s_concentration"]["meets_requirement"] is True

    def test_evaluate_criteria_power_degradation(self, populated_protocol):
        """Test evaluation of power degradation criterion"""
        populated_protocol.calculate_degradation()
        populated_protocol._evaluate_criteria()

        # Find power degradation criterion
        pmax_criterion = None
        for criterion in populated_protocol.acceptance_criteria:
            if criterion.parameter == "Maximum Power Degradation":
                pmax_criterion = criterion
                break

        assert pmax_criterion is not None
        assert pmax_criterion.actual_value is not None
        assert pmax_criterion.passed is not None

    def test_evaluate_criteria_insulation(self, populated_protocol):
        """Test evaluation of insulation resistance criterion"""
        populated_protocol._evaluate_criteria()

        # Find insulation criterion
        insulation_criterion = None
        for criterion in populated_protocol.acceptance_criteria:
            if criterion.parameter == "Insulation Resistance":
                insulation_criterion = criterion
                break

        assert insulation_criterion is not None
        assert insulation_criterion.actual_value is not None

    def test_analyze_results_complete(self, populated_protocol):
        """Test complete results analysis"""
        # Add environmental data
        base_time = datetime.now()
        for i in range(5):
            populated_protocol.record_environmental_data(
                timestamp=base_time + timedelta(minutes=i * 15),
                h2s_ppm=10.0,
                temperature_c=40.0,
                humidity_rh=85.0
            )

        analysis = populated_protocol.analyze_results()

        assert "degradation" in analysis
        assert "environmental_stability" in analysis
        assert "acceptance_evaluation" in analysis
        assert "recommendations" in analysis

        # Check degradation results
        assert "ΔPmax" in analysis["degradation"]
        assert "ΔVoc" in analysis["degradation"]

    def test_analyze_results_missing_data(self, h2s_protocol):
        """Test analysis with missing measurement data"""
        analysis = h2s_protocol.analyze_results()
        assert "error" in analysis

    def test_generate_recommendations_pass(self, populated_protocol):
        """Test recommendation generation for passing test"""
        # Add environmental data (all within spec)
        base_time = datetime.now()
        for i in range(20):
            populated_protocol.record_environmental_data(
                timestamp=base_time + timedelta(minutes=i * 15),
                h2s_ppm=10.0,
                temperature_c=40.0,
                humidity_rh=85.0
            )

        populated_protocol.calculate_degradation()
        populated_protocol._evaluate_criteria()

        recommendations = populated_protocol._generate_recommendations()

        assert len(recommendations) > 0
        # Should have positive recommendation since module passed
        assert any("passed" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_critical_failure(self, h2s_protocol, sample_module_info):
        """Test recommendations for critical failure"""
        h2s_protocol.set_module_info(sample_module_info)

        # Create failing measurements (>5% Pmax degradation)
        h2s_protocol.record_baseline_electrical(
            voc=47.5, isc=10.8, vmp=39.2,
            imp=10.2, pmax=400.0, ff=0.78
        )
        h2s_protocol.record_post_test_electrical(
            voc=46.0, isc=10.0, vmp=37.0,
            imp=9.5, pmax=350.0, ff=0.76  # 12.5% degradation!
        )

        h2s_protocol.calculate_degradation()
        h2s_protocol._evaluate_criteria()

        recommendations = h2s_protocol._generate_recommendations()

        # Should have critical failure warning
        assert any("CRITICAL" in rec for rec in recommendations)

    def test_validate_test_execution_complete(self, populated_protocol):
        """Test validation of complete test execution"""
        # Mark all phases as completed
        for phase in populated_protocol.phases:
            phase.status = StepStatus.COMPLETED

        # Add environmental data
        base_time = datetime.now()
        for i in range(20):
            populated_protocol.record_environmental_data(
                timestamp=base_time + timedelta(minutes=i * 15),
                h2s_ppm=10.0,
                temperature_c=40.0,
                humidity_rh=85.0
            )

        is_valid, issues = populated_protocol.validate_test_execution()

        assert is_valid
        assert len(issues) == 0

    def test_validate_test_execution_incomplete(self, populated_protocol):
        """Test validation of incomplete test execution"""
        # Don't complete phases
        is_valid, issues = populated_protocol.validate_test_execution()

        assert not is_valid
        assert len(issues) > 0
        assert any("not completed" in issue for issue in issues)

    def test_validate_test_execution_missing_data(self, h2s_protocol):
        """Test validation with missing data"""
        is_valid, issues = h2s_protocol.validate_test_execution()

        assert not is_valid
        assert any("Baseline" in issue for issue in issues)
        assert any("environmental" in issue.lower() for issue in issues)

    def test_get_unit(self):
        """Test unit helper method"""
        assert H2S001Protocol._get_unit("Voc") == "V"
        assert H2S001Protocol._get_unit("Isc") == "A"
        assert H2S001Protocol._get_unit("Pmax") == "W"
        assert H2S001Protocol._get_unit("FF") == "dimensionless"
        assert H2S001Protocol._get_unit("Unknown") == ""

    def test_protocol_registration(self):
        """Test that H2S-001 protocol is registered"""
        from protocols.loader import ProtocolLoader

        registered = ProtocolLoader.list_registered_protocols()
        assert "H2S-001" in registered
        assert registered["H2S-001"] == H2S001Protocol


# Import StepStatus for test
from protocols.base import StepStatus
