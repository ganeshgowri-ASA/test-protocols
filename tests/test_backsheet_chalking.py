"""Tests for CHALK-001 Backsheet Chalking Protocol"""

import pytest
from protocols.implementations.backsheet_chalking import BacksheetChalkingProtocol


class TestBacksheetChalkingProtocol:
    """Test suite for BacksheetChalkingProtocol"""

    def test_protocol_initialization(self, protocol_definition):
        """Test protocol initializes correctly"""
        protocol = BacksheetChalkingProtocol(protocol_definition)

        assert protocol.protocol_id == "CHALK-001"
        assert protocol.version == "1.0.0"
        assert protocol.name == "Backsheet Chalking Protocol"
        assert protocol.definition is not None

    def test_start_test(self, chalking_protocol, sample_info, test_conditions):
        """Test test execution starts correctly"""
        execution_id = chalking_protocol.start_test(sample_info, test_conditions)

        assert execution_id is not None
        assert execution_id.startswith("CHALK-001-")
        assert chalking_protocol.sample_info == sample_info
        assert chalking_protocol.test_conditions == test_conditions
        assert chalking_protocol.start_time is not None

    def test_add_measurement(self, chalking_protocol, sample_info, test_conditions):
        """Test adding measurements"""
        chalking_protocol.start_test(sample_info, test_conditions)

        measurement = {
            "location_id": "LOC-01",
            "chalking_rating": 2.5,
            "location_x": 100.0,
            "location_y": 100.0,
        }

        chalking_protocol.add_measurement(measurement)

        assert len(chalking_protocol.measurements) == 1
        assert chalking_protocol.measurements[0]["location_id"] == "LOC-01"
        assert "measurement_timestamp" in chalking_protocol.measurements[0]

    def test_calculate_results_passing(
        self, chalking_protocol, sample_info, test_conditions, passing_measurements
    ):
        """Test calculation with passing measurements"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in passing_measurements:
            chalking_protocol.add_measurement(measurement)

        results = chalking_protocol.calculate_results()

        assert "average_chalking_rating" in results
        assert "chalking_std_dev" in results
        assert "max_chalking_rating" in results
        assert "min_chalking_rating" in results
        assert results["average_chalking_rating"] < 3.0  # Should pass

    def test_calculate_results_failing(
        self, chalking_protocol, sample_info, test_conditions, failing_measurements
    ):
        """Test calculation with failing measurements"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in failing_measurements:
            chalking_protocol.add_measurement(measurement)

        results = chalking_protocol.calculate_results()

        assert results["average_chalking_rating"] > 5.0  # Should fail

    def test_pass_fail_evaluation_pass(
        self, chalking_protocol, sample_info, test_conditions, passing_measurements
    ):
        """Test pass/fail evaluation for passing data"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in passing_measurements:
            chalking_protocol.add_measurement(measurement)

        chalking_protocol.calculated_results = chalking_protocol.calculate_results()
        assessment = chalking_protocol.evaluate_pass_fail()

        assert assessment["overall_result"] == "PASS"
        assert len(assessment["criteria_evaluations"]) > 0

    def test_pass_fail_evaluation_fail(
        self, chalking_protocol, sample_info, test_conditions, failing_measurements
    ):
        """Test pass/fail evaluation for failing data"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in failing_measurements:
            chalking_protocol.add_measurement(measurement)

        chalking_protocol.calculated_results = chalking_protocol.calculate_results()
        assessment = chalking_protocol.evaluate_pass_fail()

        assert assessment["overall_result"] == "FAIL"

    def test_pass_fail_evaluation_warning(
        self, chalking_protocol, sample_info, test_conditions, warning_measurements
    ):
        """Test pass/fail evaluation for warning data"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in warning_measurements:
            chalking_protocol.add_measurement(measurement)

        chalking_protocol.calculated_results = chalking_protocol.calculate_results()
        assessment = chalking_protocol.evaluate_pass_fail()

        assert assessment["overall_result"] in ["WARNING", "FAIL"]

    def test_complete_test(
        self, chalking_protocol, sample_info, test_conditions, sample_measurements
    ):
        """Test complete test execution"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in sample_measurements:
            chalking_protocol.add_measurement(measurement)

        results = chalking_protocol.complete_test()

        assert results["test_execution_id"] is not None
        assert results["protocol_id"] == "CHALK-001"
        assert "calculated_results" in results
        assert "pass_fail_assessment" in results
        assert "metadata" in results
        assert chalking_protocol.end_time is not None

    def test_get_full_results(
        self, chalking_protocol, sample_info, test_conditions, sample_measurements
    ):
        """Test getting full results structure"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in sample_measurements:
            chalking_protocol.add_measurement(measurement)

        chalking_protocol.complete_test()
        results = chalking_protocol.get_full_results()

        # Verify structure
        assert "test_execution_id" in results
        assert "protocol_id" in results
        assert "protocol_version" in results
        assert "sample_info" in results
        assert "test_conditions" in results
        assert "measurements" in results
        assert "calculated_results" in results
        assert "pass_fail_assessment" in results
        assert "metadata" in results

    def test_spatial_analysis(
        self, chalking_protocol, sample_info, test_conditions, sample_measurements
    ):
        """Test spatial analysis generation"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in sample_measurements:
            chalking_protocol.add_measurement(measurement)

        spatial_analysis = chalking_protocol.generate_spatial_analysis()

        assert spatial_analysis["has_spatial_data"] is True
        assert "spatial_points" in spatial_analysis
        assert len(spatial_analysis["spatial_points"]) == len(sample_measurements)

    def test_recommendations_pass(
        self, chalking_protocol, sample_info, test_conditions, passing_measurements
    ):
        """Test recommendations for passing test"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in passing_measurements:
            chalking_protocol.add_measurement(measurement)

        chalking_protocol.complete_test()
        recommendations = chalking_protocol.get_recommendations()

        assert len(recommendations) > 0
        assert any("acceptable" in rec.lower() for rec in recommendations)

    def test_recommendations_fail(
        self, chalking_protocol, sample_info, test_conditions, failing_measurements
    ):
        """Test recommendations for failing test"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in failing_measurements:
            chalking_protocol.add_measurement(measurement)

        chalking_protocol.complete_test()
        recommendations = chalking_protocol.get_recommendations()

        assert len(recommendations) > 0
        assert any("critical" in rec.lower() for rec in recommendations)

    def test_parameter_validation(self, chalking_protocol):
        """Test parameter validation"""
        # Valid temperature
        assert chalking_protocol.validate_parameter(
            "environmental_conditions.temperature", 25.0
        ) is True

        # Invalid temperature (out of range)
        assert chalking_protocol.validate_parameter(
            "environmental_conditions.temperature", 50.0
        ) is False

        # Valid backsheet material
        assert chalking_protocol.validate_parameter(
            "sample_parameters.backsheet_material", "PET"
        ) is True

        # Invalid backsheet material
        assert chalking_protocol.validate_parameter(
            "sample_parameters.backsheet_material", "INVALID"
        ) is False

    def test_export_to_json(
        self, chalking_protocol, sample_info, test_conditions, sample_measurements, tmp_path
    ):
        """Test exporting results to JSON"""
        chalking_protocol.start_test(sample_info, test_conditions)

        for measurement in sample_measurements:
            chalking_protocol.add_measurement(measurement)

        chalking_protocol.complete_test()

        output_file = tmp_path / "test_results.json"
        chalking_protocol.export_to_json(str(output_file))

        assert output_file.exists()

        # Verify content
        import json
        with open(output_file, "r") as f:
            exported_data = json.load(f)

        assert exported_data["protocol_id"] == "CHALK-001"
        assert len(exported_data["measurements"]) == len(sample_measurements)

    def test_empty_measurements(self, chalking_protocol, sample_info, test_conditions):
        """Test behavior with no measurements"""
        chalking_protocol.start_test(sample_info, test_conditions)

        results = chalking_protocol.calculate_results()
        assert results == {}

        assessment = chalking_protocol.evaluate_pass_fail()
        assert assessment["overall_result"] == "FAIL"

    def test_metrics_calculation_accuracy(
        self, chalking_protocol, sample_info, test_conditions
    ):
        """Test accuracy of calculated metrics"""
        chalking_protocol.start_test(sample_info, test_conditions)

        # Add known measurements
        known_ratings = [1.0, 2.0, 3.0, 4.0, 5.0]
        for i, rating in enumerate(known_ratings):
            chalking_protocol.add_measurement({
                "location_id": f"LOC-{i+1:02d}",
                "chalking_rating": rating,
                "location_x": float(i * 100),
                "location_y": 100.0,
            })

        results = chalking_protocol.calculate_results()

        # Verify calculations
        import statistics
        expected_mean = statistics.mean(known_ratings)
        expected_std = statistics.stdev(known_ratings)

        assert abs(results["average_chalking_rating"] - expected_mean) < 0.01
        assert abs(results["chalking_std_dev"] - expected_std) < 0.01
        assert results["max_chalking_rating"] == 5.0
        assert results["min_chalking_rating"] == 1.0
