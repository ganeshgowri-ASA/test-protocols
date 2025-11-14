"""
Unit Tests for Base Protocol

Tests for the base protocol class and common functionality.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from protocols.implementations.base_protocol import (
    BaseProtocol,
    ProtocolDefinition,
    TestRun
)


class ConcreteProtocol(BaseProtocol):
    """Concrete implementation for testing abstract base class"""

    def execute_step(self, step_number, **kwargs):
        return {"success": True, "step": step_number, "data": kwargs}

    def generate_report(self, output_path=None):
        return f"Test Report for {self.definition.protocol_id}"


def test_load_protocol_from_dict(mock_protocol_definition):
    """Test loading protocol from dictionary"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    assert protocol.definition.protocol_id == "TEST-001"
    assert protocol.definition.name == "Test Protocol"
    assert len(protocol.definition.steps) == 2
    assert len(protocol.definition.data_fields) == 2


def test_load_protocol_from_file(corr_001_definition_path):
    """Test loading protocol from JSON file"""
    protocol = ConcreteProtocol(definition_path=corr_001_definition_path)

    assert protocol.definition.protocol_id == "CORR-001"
    assert protocol.definition.category == "degradation"
    assert len(protocol.definition.steps) == 13


def test_create_test_run(mock_protocol_definition):
    """Test creating a test run instance"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    test_run = protocol.create_test_run(
        run_id="TEST-RUN-001",
        operator="Test Operator",
        initial_data={"sample_id": "SAMPLE-001"}
    )

    assert test_run.run_id == "TEST-RUN-001"
    assert test_run.operator == "Test Operator"
    assert test_run.protocol_id == "TEST-001"
    assert test_run.data["sample_id"] == "SAMPLE-001"
    assert test_run.status == "in_progress"


def test_validate_data_success(mock_protocol_definition):
    """Test data validation with valid data"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    test_data = {
        "test_field_1": 50.0,
        "test_field_2": "test value"
    }

    is_valid, errors = protocol.validate_data(test_data)

    assert is_valid
    assert len(errors) == 0


def test_validate_data_missing_required(mock_protocol_definition):
    """Test data validation with missing required field"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    test_data = {
        "test_field_2": "test value"
        # test_field_1 is required but missing
    }

    is_valid, errors = protocol.validate_data(test_data)

    assert not is_valid
    assert len(errors) > 0
    assert any("test_field_1" in error.lower() or "test field 1" in error.lower() for error in errors)


def test_validate_data_out_of_range(mock_protocol_definition):
    """Test data validation with value out of range"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    test_data = {
        "test_field_1": 150.0,  # max is 100
        "test_field_2": "test value"
    }

    is_valid, errors = protocol.validate_data(test_data)

    assert not is_valid
    assert len(errors) > 0
    assert any("100" in error for error in errors)


def test_run_qc_checks_pass(mock_protocol_definition):
    """Test QC checks with passing data"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    test_data = {
        "test_field_1": 50.0  # Within range 10-90
    }

    qc_results = protocol.run_qc_checks(test_data)

    assert len(qc_results) == 1
    assert qc_results[0]["passed"] == True
    assert qc_results[0]["criterion_id"] == "qc_test_1"


def test_run_qc_checks_fail(mock_protocol_definition):
    """Test QC checks with failing data"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    test_data = {
        "test_field_1": 5.0  # Below min of 10
    }

    qc_results = protocol.run_qc_checks(test_data)

    assert len(qc_results) == 1
    assert qc_results[0]["passed"] == False
    assert qc_results[0]["severity"] == "warning"


def test_calculate_results(mock_protocol_definition):
    """Test calculation of derived results"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    test_data = {
        "test_field_1": 25.0
    }

    results = protocol.calculate_results(test_data)

    assert "Test Calculation" in results
    assert results["Test Calculation"]["value"] == 50.0  # 25 * 2
    assert results["Test Calculation"]["unit"] == "V"


def test_mark_step_complete(mock_protocol_definition):
    """Test marking steps as complete"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    protocol.create_test_run("TEST-001", "Operator")

    protocol.mark_step_complete(1)

    assert 1 in protocol.test_run.data.get("completed_steps", [])


def test_get_next_step(mock_protocol_definition):
    """Test getting next step to execute"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    protocol.create_test_run("TEST-001", "Operator")

    # First step
    next_step = protocol.get_next_step()
    assert next_step.step_number == 1

    # Mark first step complete
    protocol.mark_step_complete(1)

    # Should return second step
    next_step = protocol.get_next_step()
    assert next_step.step_number == 2

    # Mark second step complete
    protocol.mark_step_complete(2)

    # No more steps
    next_step = protocol.get_next_step()
    assert next_step is None


def test_get_protocol_info(mock_protocol_definition):
    """Test getting protocol information"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    info = protocol.get_protocol_info()

    assert info["protocol_id"] == "TEST-001"
    assert info["name"] == "Test Protocol"
    assert info["version"] == "1.0.0"
    assert info["category"] == "degradation"
    assert info["num_steps"] == 2
    assert info["num_data_fields"] == 2


def test_get_data_as_dataframe(mock_protocol_definition):
    """Test converting test data to DataFrame"""
    protocol = ConcreteProtocol(definition_dict=mock_protocol_definition)

    protocol.create_test_run("TEST-001", "Operator", {"test_field_1": 50.0})

    df = protocol.get_data_as_dataframe()

    assert not df.empty
    assert "test_field_1" in df.columns
    assert df.iloc[0]["test_field_1"] == 50.0


def test_abstract_methods():
    """Test that base protocol cannot be instantiated directly"""
    with pytest.raises(TypeError):
        # Should fail because BaseProtocol is abstract
        protocol = BaseProtocol(definition_dict={"protocol_id": "TEST"})
