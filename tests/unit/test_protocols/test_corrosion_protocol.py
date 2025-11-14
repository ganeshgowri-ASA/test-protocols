"""
Unit Tests for CORR-001 Corrosion Protocol

Tests for the corrosion testing protocol implementation.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from protocols.implementations.corrosion.corrosion_protocol import CorrosionProtocol


def test_load_corr_001_protocol(corr_001_definition_path):
    """Test loading CORR-001 protocol"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)

    assert protocol.definition.protocol_id == "CORR-001"
    assert protocol.definition.name == "Corrosion Testing - Salt Spray and Humidity"
    assert protocol.definition.category == "degradation"
    assert len(protocol.definition.steps) == 13
    assert protocol.current_cycle == 0


def test_step_1_initial_documentation(corr_001_definition_path):
    """Test step 1: Initial documentation"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    result = protocol.execute_step(
        1,
        sample_id="SAMPLE-001",
        serial_number="SN-12345",
        operator="Test Operator",
        photos=["photo1.jpg", "photo2.jpg"]
    )

    assert result["success"] == True
    assert result["result"]["sample_id"] == "SAMPLE-001"
    assert protocol.test_run.data["sample_id"] == "SAMPLE-001"


def test_step_1_missing_parameters(corr_001_definition_path):
    """Test step 1 with missing required parameters"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    result = protocol.execute_step(1, sample_id="SAMPLE-001")
    # Missing serial_number and operator

    assert result["success"] == False
    assert "error" in result


def test_step_2_baseline_electrical(corr_001_definition_path):
    """Test step 2: Baseline electrical characterization"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    result = protocol.execute_step(
        2,
        baseline_voc=45.5,
        baseline_isc=9.2,
        baseline_pmax=350.0,
        baseline_ff=78.5,
        baseline_rs=0.5,
        baseline_rsh=1000.0
    )

    assert result["success"] == True
    assert protocol.test_run.data["baseline_pmax"] == 350.0
    assert len(protocol.electrical_history) == 1


def test_step_3_prepare_solution(corr_001_definition_path):
    """Test step 3: Prepare salt solution"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    result = protocol.execute_step(
        3,
        salt_solution_concentration=5.0,
        salt_solution_ph=6.8
    )

    assert result["success"] == True
    assert result["result"]["status"] == "ready"


def test_step_3_invalid_concentration(corr_001_definition_path):
    """Test step 3 with invalid salt concentration"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    result = protocol.execute_step(
        3,
        salt_solution_concentration=3.0,  # Too low (must be 4-6%)
        salt_solution_ph=6.8
    )

    assert result["success"] == False
    assert "concentration" in result["error"].lower()


def test_step_3_invalid_ph(corr_001_definition_path):
    """Test step 3 with invalid pH"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    result = protocol.execute_step(
        3,
        salt_solution_concentration=5.0,
        salt_solution_ph=8.0  # Too high (must be 6.5-7.2)
    )

    assert result["success"] == False
    assert "ph" in result["error"].lower()


def test_step_4_salt_spray_exposure(corr_001_definition_path):
    """Test step 4: Salt spray exposure"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    result = protocol.execute_step(
        4,
        spray_temp=35.0,
        duration_hours=48
    )

    assert result["success"] == True
    assert protocol.current_cycle == 1
    assert len(protocol.salt_spray_logs) == 1


def test_step_4_invalid_temperature(corr_001_definition_path):
    """Test step 4 with invalid temperature"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    result = protocol.execute_step(
        4,
        spray_temp=40.0,  # Too high (must be 33-37°C)
        duration_hours=48
    )

    assert result["success"] == False
    assert "temperature" in result["error"].lower()


def test_step_6_humidity_exposure(corr_001_definition_path):
    """Test step 6: Humidity exposure"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    # First execute step 4 to set current_cycle
    protocol.execute_step(4, spray_temp=35.0, duration_hours=48)

    result = protocol.execute_step(
        6,
        humidity_temp=85.0,
        humidity_rh=85.0,
        duration_hours=96
    )

    assert result["success"] == True
    assert len(protocol.humidity_logs) == 1


def test_step_8_interim_visual(corr_001_definition_path):
    """Test step 8: Interim visual inspection"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    # Set cycle number
    protocol.current_cycle = 1

    result = protocol.execute_step(
        8,
        visual_corrosion="Minor",
        corrosion_location=["Frame"],
        delamination=False,
        discoloration=False,
        photos=["inspection1.jpg"]
    )

    assert result["success"] == True
    assert len(protocol.inspection_history) == 1
    assert protocol.inspection_history[0]["visual_corrosion"] == "Minor"


def test_step_9_interim_electrical(corr_001_definition_path):
    """Test step 9: Interim electrical testing"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    # Set baseline and cycle
    protocol.test_run.data["baseline_pmax"] = 350.0
    protocol.current_cycle = 1

    result = protocol.execute_step(
        9,
        interim_voc=45.3,
        interim_isc=9.1,
        interim_pmax=348.0,
        insulation_resistance=50.0
    )

    assert result["success"] == True
    assert "power_degradation" in protocol.electrical_history[-1]
    degradation = protocol.electrical_history[-1]["power_degradation"]
    assert degradation < 1.0  # Less than 1% degradation


def test_step_12_final_electrical(corr_001_definition_path):
    """Test step 12: Final electrical characterization"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    # Set baseline
    protocol.test_run.data["baseline_pmax"] = 350.0

    result = protocol.execute_step(
        12,
        final_voc=44.8,
        final_isc=9.0,
        final_pmax=342.0,
        final_ff=77.8,
        wet_leakage_current=0.5,
        ground_continuity=True
    )

    assert result["success"] == True
    assert protocol.test_run.data["final_pmax"] == 342.0
    assert "total_power_degradation" in protocol.test_run.data


def test_qc_checks_with_passing_data(corr_001_definition_path, sample_test_data):
    """Test QC checks with data that should pass"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    qc_results = protocol.run_qc_checks(sample_test_data)

    # Check that critical QC criteria pass
    critical_checks = [r for r in qc_results if r["severity"] == "critical"]
    critical_failures = [r for r in critical_checks if not r["passed"]]

    assert len(critical_failures) == 0, f"Critical QC checks failed: {critical_failures}"


def test_qc_checks_with_failing_data(corr_001_definition_path, sample_test_data_with_failures):
    """Test QC checks with data that should fail"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    qc_results = protocol.run_qc_checks(sample_test_data_with_failures)

    # Should have critical failures
    critical_failures = [
        r for r in qc_results
        if r["severity"] == "critical" and not r["passed"]
    ]

    assert len(critical_failures) > 0, "Expected critical QC failures"

    # Check specific failures
    failure_ids = [f["criterion_id"] for f in critical_failures]

    # Power degradation should fail (>5%)
    assert "qc_power_degradation" in failure_ids

    # Insulation resistance should fail (<40 MΩ)
    assert "qc_insulation_resistance" in failure_ids


def test_generate_report(corr_001_definition_path, sample_test_data):
    """Test report generation"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-RUN-001", "Test Operator")
    protocol.test_run.data.update(sample_test_data)
    protocol.test_run.qc_results = protocol.run_qc_checks(sample_test_data)

    report = protocol.generate_report()

    assert "CORR-001" in report
    assert "TEST-RUN-001" in report
    assert "TEST-SAMPLE-001" in report
    assert "Test Operator" in report


def test_get_degradation_curve(corr_001_definition_path):
    """Test degradation curve generation"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)
    protocol.create_test_run("TEST-001", "Test Operator")

    # Add baseline and measurements
    protocol.test_run.data["baseline_pmax"] = 350.0
    protocol.electrical_history.append({
        "cycle_number": 1,
        "interim_pmax": 348.0
    })
    protocol.electrical_history.append({
        "cycle_number": 2,
        "interim_pmax": 345.0
    })
    protocol.test_run.data["final_pmax"] = 342.0
    protocol.current_cycle = 3

    df = protocol.get_degradation_curve()

    assert not df.empty
    assert len(df) >= 3  # Baseline + interim measurements + final
    assert "cycle" in df.columns
    assert "pmax" in df.columns


def test_complete_workflow(corr_001_definition_path):
    """Test complete protocol workflow"""
    protocol = CorrosionProtocol(definition_path=corr_001_definition_path)

    # Create test run
    protocol.create_test_run("COMPLETE-TEST-001", "Test Operator")

    # Step 1: Initial documentation
    result = protocol.execute_step(
        1,
        sample_id="SAMPLE-COMPLETE",
        serial_number="SN-99999",
        operator="Test Operator"
    )
    assert result["success"]

    # Step 2: Baseline electrical
    result = protocol.execute_step(
        2,
        baseline_voc=45.5,
        baseline_isc=9.2,
        baseline_pmax=350.0,
        baseline_ff=78.5
    )
    assert result["success"]

    # Step 3: Prepare solution
    result = protocol.execute_step(
        3,
        salt_solution_concentration=5.0,
        salt_solution_ph=6.8
    )
    assert result["success"]

    # Verify test run has accumulated data
    assert "sample_id" in protocol.test_run.data
    assert "baseline_pmax" in protocol.test_run.data
    assert "salt_solution_concentration" in protocol.test_run.data

    # Check completed steps
    assert 1 in protocol.test_run.data.get("completed_steps", [])
    assert 2 in protocol.test_run.data.get("completed_steps", [])
    assert 3 in protocol.test_run.data.get("completed_steps", [])
