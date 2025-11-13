"""Tests for PID-001 schema validation."""

import pytest
import json
from pathlib import Path


class TestPID001Schema:
    """Test PID-001 schema structure and validation."""

    def test_schema_exists(self):
        """Test that schema file exists."""
        schema_path = Path(__file__).parent.parent / "schema.json"
        assert schema_path.exists(), "Schema file should exist"

    def test_schema_valid_json(self, pid001_schema):
        """Test that schema is valid JSON."""
        assert isinstance(pid001_schema, dict)
        assert "metadata" in pid001_schema
        assert "test_parameters" in pid001_schema

    def test_metadata_fields(self, pid001_schema):
        """Test schema metadata fields."""
        metadata = pid001_schema["metadata"]

        assert metadata["pid"] == "pid-001"
        assert metadata["name"] == "PID Shunting Test Protocol"
        assert metadata["standard"] == "IEC 62804"
        assert "version" in metadata
        assert metadata["status"] == "active"

    def test_test_parameters_structure(self, pid001_schema):
        """Test test parameters structure."""
        params = pid001_schema["test_parameters"]

        assert params["type"] == "object"
        assert "properties" in params
        assert "required" in params

        # Check required fields
        required = params["required"]
        assert "test_name" in required
        assert "module_id" in required
        assert "test_voltage" in required
        assert "test_duration" in required

    def test_parameter_definitions(self, pid001_schema):
        """Test individual parameter definitions."""
        properties = pid001_schema["test_parameters"]["properties"]

        # Test voltage
        assert properties["test_voltage"]["type"] == "number"
        assert properties["test_voltage"]["minimum"] == -1500
        assert properties["test_voltage"]["maximum"] == 1500

        # Test duration
        assert properties["test_duration"]["type"] == "number"
        assert properties["test_duration"]["minimum"] == 0
        assert properties["test_duration"]["maximum"] == 500

        # Test temperature
        assert properties["temperature"]["type"] == "number"
        assert properties["temperature"]["default"] == 85

        # Test humidity
        assert properties["relative_humidity"]["type"] == "number"
        assert properties["relative_humidity"]["default"] == 85

    def test_measurements_structure(self, pid001_schema):
        """Test measurements structure."""
        measurements = pid001_schema["measurements"]

        assert measurements["type"] == "object"
        properties = measurements["properties"]

        assert "timestamp" in properties
        assert "elapsed_time" in properties
        assert "leakage_current" in properties
        assert "voltage" in properties

    def test_validation_rules(self, pid001_schema):
        """Test validation rules structure."""
        rules = pid001_schema["validation_rules"]

        # Leakage current limits
        assert "leakage_current_limits" in rules
        leakage = rules["leakage_current_limits"]
        assert "warning_threshold" in leakage
        assert "critical_threshold" in leakage
        assert leakage["warning_threshold"] < leakage["critical_threshold"]

        # Power degradation limits
        assert "power_degradation_limits" in rules
        power = rules["power_degradation_limits"]
        assert "warning_threshold" in power
        assert "critical_threshold" in power

    def test_results_structure(self, pid001_schema):
        """Test results structure."""
        results = pid001_schema["results"]

        assert results["type"] == "object"
        properties = results["properties"]

        assert "test_id" in properties
        assert "start_time" in properties
        assert "status" in properties
        assert "measurements" in properties
        assert "summary" in properties

        # Check status enum
        status_enum = properties["status"]["enum"]
        assert "completed" in status_enum
        assert "failed" in status_enum
        assert "in_progress" in status_enum

    def test_chart_configurations(self, pid001_schema):
        """Test chart configurations."""
        charts = pid001_schema["chart_configurations"]

        assert "leakage_current_vs_time" in charts
        assert "power_degradation_vs_time" in charts
        assert "environmental_conditions" in charts

        # Check leakage current chart config
        leakage_chart = charts["leakage_current_vs_time"]
        assert leakage_chart["type"] == "line"
        assert leakage_chart["x_axis"] == "elapsed_time"
        assert leakage_chart["y_axis"] == "leakage_current"

    def test_template_exists(self):
        """Test that template file exists."""
        template_path = Path(__file__).parent.parent / "template.json"
        assert template_path.exists(), "Template file should exist"

    def test_template_valid(self, pid001_template):
        """Test that template contains valid data."""
        assert isinstance(pid001_template, dict)
        assert "test_name" in pid001_template
        assert "module_id" in pid001_template
        assert "test_voltage" in pid001_template
        assert "test_duration" in pid001_template
