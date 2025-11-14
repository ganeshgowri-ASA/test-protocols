"""Unit tests specifically for TWIST-001 protocol."""

import unittest
import json
from pathlib import Path

from src.parsers import ProtocolLoader, ProtocolExecutor
from src.models.base import get_engine, init_db, get_session
from src.models.test_run import TestStatus, TestResult


class TestTwist001Protocol(unittest.TestCase):
    """Test cases for TWIST-001 Module Twist Test protocol."""

    def setUp(self):
        """Set up test fixtures."""
        # Create in-memory database for testing
        self.engine = get_engine("sqlite:///:memory:")
        init_db(self.engine)
        self.session = get_session(self.engine)

        # Load the actual TWIST-001 protocol file
        protocol_path = Path(__file__).parent.parent.parent / "protocols" / "mechanical" / "TWIST-001.json"

        if protocol_path.exists():
            loader = ProtocolLoader()
            self.protocol_data = loader.load_and_validate(protocol_path)
            self.protocol = loader.import_to_database(self.protocol_data, self.session)
        else:
            self.skipTest("TWIST-001.json not found")

    def tearDown(self):
        """Clean up test fixtures."""
        self.session.close()

    def test_protocol_loaded(self):
        """Test that TWIST-001 protocol is loaded correctly."""
        self.assertIsNotNone(self.protocol)
        self.assertEqual(self.protocol.protocol_id, "TWIST-001")
        self.assertEqual(self.protocol.protocol_name, "Module Twist Test")
        self.assertEqual(self.protocol.version, "1.0.0")
        self.assertEqual(self.protocol.category, "Mechanical")

    def test_protocol_structure(self):
        """Test that TWIST-001 has all required fields."""
        self.assertIn("protocol_id", self.protocol_data)
        self.assertIn("protocol_name", self.protocol_data)
        self.assertIn("version", self.protocol_data)
        self.assertIn("category", self.protocol_data)
        self.assertIn("description", self.protocol_data)
        self.assertIn("standard_reference", self.protocol_data)
        self.assertIn("test_parameters", self.protocol_data)
        self.assertIn("test_steps", self.protocol_data)
        self.assertIn("acceptance_criteria", self.protocol_data)
        self.assertIn("data_collection", self.protocol_data)

    def test_standard_references(self):
        """Test that standard references are present."""
        references = self.protocol_data.get("standard_reference", [])
        self.assertGreater(len(references), 0)

        # Check for IEC 61215-2
        iec_refs = [r for r in references if "IEC 61215" in r.get("standard", "")]
        self.assertGreater(len(iec_refs), 0)

    def test_test_steps(self):
        """Test that test steps are defined."""
        steps = self.protocol_data.get("test_steps", [])

        # TWIST-001 should have 14 steps
        self.assertEqual(len(steps), 14)

        # Verify step numbers are sequential
        for i, step in enumerate(steps, start=1):
            self.assertEqual(step["step_number"], i)
            self.assertIn("description", step)
            self.assertIn("action", step)

    def test_test_parameters(self):
        """Test that test parameters are correctly defined."""
        params = self.protocol_data.get("test_parameters", {})

        # Check specimen requirements
        specimen = params.get("specimen_requirements", {})
        self.assertEqual(specimen.get("quantity"), 1)

        # Check environmental conditions
        env = params.get("environmental_conditions", {})
        self.assertIn("temperature_range", env)
        self.assertIn("humidity_range", env)

        # Check test-specific parameters
        test_params = params.get("test_specific_parameters", {})
        self.assertIn("twist_distance", test_params)
        self.assertEqual(test_params["twist_distance"]["value"], 25)
        self.assertEqual(test_params["twist_distance"]["unit"], "mm")

        self.assertIn("cycles", test_params)
        self.assertEqual(test_params["cycles"]["value"], 3)

    def test_acceptance_criteria(self):
        """Test that acceptance criteria are defined."""
        criteria = self.protocol_data.get("acceptance_criteria", [])

        # TWIST-001 should have 5 acceptance criteria
        self.assertEqual(len(criteria), 5)

        # Check power degradation criterion
        power_criterion = next(
            (c for c in criteria if c.get("criterion_id") == "AC-001"),
            None
        )
        self.assertIsNotNone(power_criterion)
        self.assertEqual(power_criterion["threshold"]["parameter"], "power_degradation")
        self.assertEqual(power_criterion["threshold"]["operator"], "<=")
        self.assertEqual(power_criterion["threshold"]["value"], 5.0)

    def test_measurements(self):
        """Test that data collection measurements are defined."""
        measurements = self.protocol_data.get("data_collection", {}).get("measurements", [])

        # Should have 13 measurements defined
        self.assertEqual(len(measurements), 13)

        # Check for initial and final power measurements
        pmax_initial = next(
            (m for m in measurements if "Pmax" in m.get("parameter", "") and "Initial" in m.get("parameter", "")),
            None
        )
        self.assertIsNotNone(pmax_initial)
        self.assertEqual(pmax_initial["unit"], "W")

        pmax_final = next(
            (m for m in measurements if "Pmax" in m.get("parameter", "") and "Final" in m.get("parameter", "")),
            None
        )
        self.assertIsNotNone(pmax_final)

        # Check for power degradation calculation
        degradation = next(
            (m for m in measurements if "Degradation" in m.get("parameter", "")),
            None
        )
        self.assertIsNotNone(degradation)
        self.assertEqual(degradation["unit"], "%")

    def test_equipment_requirements(self):
        """Test that equipment requirements are defined."""
        equipment = self.protocol_data.get("equipment", [])

        # Should have multiple equipment items
        self.assertGreater(len(equipment), 0)

        # Check for twist test fixture
        fixture = next(
            (e for e in equipment if "twist test fixture" in e.get("name", "").lower()),
            None
        )
        self.assertIsNotNone(fixture)

        # Check for solar simulator
        simulator = next(
            (e for e in equipment if "solar simulator" in e.get("name", "").lower()),
            None
        )
        self.assertIsNotNone(simulator)

    def test_safety_requirements(self):
        """Test that safety requirements are defined."""
        safety = self.protocol_data.get("safety_requirements", [])

        # Should have safety requirements
        self.assertGreater(len(safety), 0)

    def test_create_twist_test_run(self):
        """Test creating a test run for TWIST-001."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="MODULE-TWIST-001",
            operator_name="Test Engineer",
            manufacturer="SolarTech Inc.",
            model_number="ST-350-72M",
            serial_number="SN123456789",
            ambient_temperature=25.0,
            ambient_humidity=50.0
        )

        self.assertIsNotNone(test_run)
        self.assertEqual(test_run.specimen_id, "MODULE-TWIST-001")
        self.assertEqual(len(test_run.test_steps), 14)

    def test_twist_test_workflow(self):
        """Test a complete TWIST-001 test workflow."""
        executor = ProtocolExecutor(self.session)

        # Create test run
        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="MODULE-TWIST-002",
            operator_name="Test Engineer"
        )

        # Start test
        executor.start_test_run(test_run)
        self.assertEqual(test_run.status, TestStatus.IN_PROGRESS)

        # Record initial measurements (Step 2)
        executor.record_measurement(
            test_run=test_run,
            measurement_id="M-001",
            parameter="Maximum Power (Pmax) - Initial",
            value=350.5,
            unit="W",
            measurement_type="pre_test"
        )

        executor.record_measurement(
            test_run=test_run,
            measurement_id="M-002",
            parameter="Open Circuit Voltage (Voc) - Initial",
            value=48.2,
            unit="V",
            measurement_type="pre_test"
        )

        # Record final measurements (Step 12)
        executor.record_measurement(
            test_run=test_run,
            measurement_id="M-008",
            parameter="Maximum Power (Pmax) - Final",
            value=346.0,
            unit="W",
            measurement_type="post_test"
        )

        # Calculate degradation
        degradation = ((350.5 - 346.0) / 350.5) * 100
        executor.record_measurement(
            test_run=test_run,
            measurement_id="M-013",
            parameter="Power Degradation",
            value=degradation,
            unit="%",
            measurement_type="post_test"
        )

        # Verify degradation is within acceptance criteria (≤5%)
        self.assertLess(degradation, 5.0)

        # Complete test
        result = executor.evaluate_acceptance_criteria(test_run, self.protocol)

        # Should pass since degradation is < 5%
        self.assertIn(result, [TestResult.PASS, TestResult.CONDITIONAL])


if __name__ == '__main__':
    unittest.main()
