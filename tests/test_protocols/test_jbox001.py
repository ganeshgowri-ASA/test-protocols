"""
Unit tests specific to JBOX-001 protocol implementation.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from protocols.jbox001 import JBOX001Protocol
from core.test_runner import PhaseStatus, TestStatus


class TestJBOX001Protocol(unittest.TestCase):
    """Test cases for JBOX-001 protocol implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.protocol = JBOX001Protocol()

    def test_protocol_initialization(self):
        """Test protocol initialization."""
        self.assertIsNotNone(self.protocol.loader)
        self.assertIsNotNone(self.protocol.protocol)
        self.assertIsNotNone(self.protocol.validator)
        self.assertIsNotNone(self.protocol.runner)
        self.assertEqual(self.protocol.PROTOCOL_ID, "JBOX-001")

    def test_create_test_run_with_auto_id(self):
        """Test creating test run with auto-generated ID."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-001",
            operator="John Doe"
        )

        self.assertIsNotNone(test_run.test_run_id)
        self.assertTrue(test_run.test_run_id.startswith("JBOX001-"))

    def test_create_test_run_with_custom_id(self):
        """Test creating test run with custom ID."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-002",
            operator="Jane Smith",
            test_run_id="CUSTOM-001"
        )

        self.assertEqual(test_run.test_run_id, "CUSTOM-001")

    def test_initial_characterization_phase(self):
        """Test Phase 1: Initial Characterization."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-003",
            operator="Test User"
        )

        self.protocol.run_initial_characterization(
            test_run=test_run,
            visual_inspection={
                'defects_count': 0,
                'notes': 'No defects found',
                'junction_box_housing': 'good',
                'cable_entry': 'good',
                'potting_compound': 'good'
            },
            contact_resistance=4.8,
            diode_voltage=[0.65, 0.64, 0.66],
            insulation_resistance=120.0,
            iv_curve_data={
                'pmax': 305.0,
                'voc': 41.2,
                'isc': 9.5
            }
        )

        # Verify phase completion
        self.assertIn('P1', test_run.phase_results)
        self.assertEqual(
            test_run.phase_results['P1']['status'],
            PhaseStatus.COMPLETED.value
        )

        # Verify measurements were recorded
        measurement_ids = {m['measurement_id'] for m in test_run.measurements}
        self.assertIn('M1', measurement_ids)  # Contact resistance
        self.assertIn('M2', measurement_ids)  # Diode voltage
        self.assertIn('M3', measurement_ids)  # Insulation resistance
        self.assertIn('M5', measurement_ids)  # Power
        self.assertIn('M6', measurement_ids)  # Voc
        self.assertIn('M7', measurement_ids)  # Isc

        # Verify specific values
        contact_res_measurements = [
            m for m in test_run.measurements
            if m['measurement_id'] == 'M1'
        ]
        self.assertEqual(len(contact_res_measurements), 1)
        self.assertEqual(contact_res_measurements[0]['value'], 4.8)

    def test_thermal_cycling_phase(self):
        """Test Phase 2: Thermal Cycling."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-004",
            operator="Test User"
        )

        # Run partial thermal cycling
        self.protocol.run_thermal_cycling(
            test_run=test_run,
            cycles_completed=100
        )

        self.assertIn('P2', test_run.phase_results)
        # Should not be completed yet (need 200 cycles)
        self.assertNotEqual(
            test_run.phase_results['P2']['status'],
            PhaseStatus.COMPLETED.value
        )

        # Complete thermal cycling
        self.protocol.run_thermal_cycling(
            test_run=test_run,
            cycles_completed=200
        )

        self.assertEqual(
            test_run.phase_results['P2']['status'],
            PhaseStatus.COMPLETED.value
        )

    def test_thermal_cycling_with_interim_measurements(self):
        """Test thermal cycling with interim measurements."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-005",
            operator="Test User"
        )

        interim_measurements = [
            {
                'cycle': 50,
                'contact_resistance': 5.0,
                'diode_voltage': 0.65
            },
            {
                'cycle': 100,
                'contact_resistance': 5.2,
                'diode_voltage': 0.66
            }
        ]

        self.protocol.run_thermal_cycling(
            test_run=test_run,
            cycles_completed=100,
            interim_measurements=interim_measurements
        )

        # Check that interim measurements were recorded
        thermal_measurements = [
            m for m in test_run.measurements
            if m.get('metadata', {}).get('phase') == 'thermal_cycling'
        ]

        self.assertGreater(len(thermal_measurements), 0)

    def test_humidity_freeze_phase(self):
        """Test Phase 3: Humidity-Freeze."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-006",
            operator="Test User"
        )

        self.protocol.run_humidity_freeze(
            test_run=test_run,
            cycles_completed=10,
            weight_gain_percentage=0.3
        )

        self.assertIn('P3', test_run.phase_results)
        self.assertEqual(
            test_run.phase_results['P3']['status'],
            PhaseStatus.COMPLETED.value
        )

        # Check for weight gain note
        weight_notes = [
            n for n in test_run.notes
            if 'Weight gain' in n['note']
        ]
        self.assertGreater(len(weight_notes), 0)

    def test_uv_exposure_phase(self):
        """Test Phase 4: UV Exposure."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-007",
            operator="Test User"
        )

        self.protocol.run_uv_exposure(
            test_run=test_run,
            uv_dose=15.0,
            degradation_assessment={
                'discoloration': True,
                'cracking': False,
                'embrittlement': False,
                'defects_count': 2
            }
        )

        self.assertIn('P4', test_run.phase_results)
        self.assertEqual(
            test_run.phase_results['P4']['status'],
            PhaseStatus.COMPLETED.value
        )

    def test_electrical_load_stress_phase(self):
        """Test Phase 5: Electrical Load Stress."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-008",
            operator="Test User"
        )

        from datetime import datetime, timedelta

        # Generate temperature data (every hour for 24 hours)
        base_time = datetime.now()
        temperature_data = [
            {
                'timestamp': base_time + timedelta(hours=i),
                'temperature': 50 + i * 0.5
            }
            for i in range(24)
        ]

        # Generate resistance data
        resistance_data = [
            {
                'timestamp': base_time + timedelta(hours=i),
                'resistance': 5.0 + i * 0.01
            }
            for i in range(24)
        ]

        self.protocol.run_electrical_load_stress(
            test_run=test_run,
            temperature_data=temperature_data,
            resistance_data=resistance_data
        )

        self.assertIn('P5', test_run.phase_results)

        # Verify temperature measurements
        temp_measurements = [
            m for m in test_run.measurements
            if m['measurement_id'] == 'M4'
        ]
        self.assertEqual(len(temp_measurements), 24)

    def test_final_characterization_and_qc(self):
        """Test Phase 6: Final Characterization and QC evaluation."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-009",
            operator="Test User"
        )

        self.protocol.runner.start_test_run(test_run.test_run_id)

        # Run initial characterization
        self.protocol.run_initial_characterization(
            test_run=test_run,
            visual_inspection={'defects_count': 0, 'notes': 'Clean'},
            contact_resistance=5.0,
            diode_voltage=[0.65, 0.64, 0.66],
            insulation_resistance=100.0,
            iv_curve_data={'pmax': 300.0, 'voc': 40.5, 'isc': 9.2}
        )

        # Run final characterization with acceptable degradation
        self.protocol.run_final_characterization(
            test_run=test_run,
            visual_inspection={'defects_count': 0, 'notes': 'Slight discoloration'},
            contact_resistance=5.4,  # 8% increase (within 20% limit)
            diode_voltage=[0.66, 0.65, 0.67],
            insulation_resistance=95.0,  # Above 40 MΩ limit
            iv_curve_data={
                'pmax': 288.0,  # 4% degradation (within 5% limit)
                'voc': 40.3,
                'isc': 9.1
            }
        )

        # Verify QC results
        self.assertIsNotNone(test_run.qc_results)
        self.assertTrue(test_run.qc_results['overall_pass'])
        self.assertEqual(len(test_run.qc_results['critical_failures']), 0)

    def test_final_characterization_qc_failure(self):
        """Test QC failure scenarios."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-010",
            operator="Test User"
        )

        self.protocol.runner.start_test_run(test_run.test_run_id)

        # Run initial characterization
        self.protocol.run_initial_characterization(
            test_run=test_run,
            visual_inspection={'defects_count': 0, 'notes': 'Clean'},
            contact_resistance=5.0,
            diode_voltage=[0.65, 0.64, 0.66],
            insulation_resistance=100.0,
            iv_curve_data={'pmax': 300.0, 'voc': 40.5, 'isc': 9.2}
        )

        # Run final characterization with excessive degradation
        self.protocol.run_final_characterization(
            test_run=test_run,
            visual_inspection={'defects_count': 1, 'notes': 'Damage observed'},
            contact_resistance=6.5,  # 30% increase (exceeds 20% limit)
            diode_voltage=[0.70, 0.69, 0.71],
            insulation_resistance=35.0,  # Below 40 MΩ limit (FAIL)
            iv_curve_data={
                'pmax': 270.0,  # 10% degradation (exceeds 5% limit - FAIL)
                'voc': 39.8,
                'isc': 8.9
            }
        )

        # Verify QC failure
        self.assertIsNotNone(test_run.qc_results)
        self.assertFalse(test_run.qc_results['overall_pass'])
        self.assertGreater(len(test_run.qc_results['critical_failures']), 0)

    def test_generate_test_report(self):
        """Test test report generation."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-011",
            operator="Test User"
        )

        self.protocol.runner.start_test_run(test_run.test_run_id)

        # Add some basic data
        test_run.add_measurement("M1", 5.0, "mΩ")
        test_run.set_phase("P1", PhaseStatus.COMPLETED)

        # Generate report
        report = self.protocol.generate_test_report(test_run)

        # Verify report structure
        self.assertIn('protocol', report)
        self.assertIn('test_run', report)
        self.assertIn('test_data', report)
        self.assertIn('validation', report)
        self.assertIn('generated_at', report)

        # Verify protocol info
        self.assertEqual(report['protocol']['id'], 'JBOX-001')
        self.assertEqual(
            report['protocol']['name'],
            'Junction Box Degradation Test'
        )

    def test_extract_initial_measurements(self):
        """Test extraction of initial measurements."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-012",
            operator="Test User"
        )

        # Add initial measurements
        test_run.add_measurement(
            "M1", 5.0, "mΩ",
            metadata={"phase": "initial"}
        )
        test_run.add_measurement(
            "M5", 300.0, "W",
            metadata={"phase": "initial"}
        )

        # Add some other measurements
        test_run.add_measurement(
            "M1", 5.2, "mΩ",
            metadata={"phase": "thermal_cycling"}
        )

        initial = self.protocol._extract_initial_measurements(test_run)

        self.assertEqual(initial['M1'], 5.0)
        self.assertEqual(initial['M5'], 300.0)
        self.assertNotIn('M2', initial)


if __name__ == '__main__':
    unittest.main()
