"""
JBOX-001 Junction Box Degradation Test Implementation

Protocol-specific implementation for JBOX-001 testing.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.protocol_loader import ProtocolLoader
from core.test_runner import TestRunner, TestRun, PhaseStatus
from core.data_validator import DataValidator


class JBOX001Protocol:
    """JBOX-001 specific protocol implementation."""

    PROTOCOL_ID = "JBOX-001"

    def __init__(self):
        """Initialize JBOX-001 protocol."""
        self.loader = ProtocolLoader()
        self.protocol = self.loader.load_protocol(self.PROTOCOL_ID)
        self.validator = DataValidator(self.protocol)
        self.runner = TestRunner()

    def create_test_run(self, sample_id: str, operator: str,
                       test_run_id: Optional[str] = None) -> TestRun:
        """
        Create a new JBOX-001 test run.

        Args:
            sample_id: Module/junction box identifier
            operator: Test operator name
            test_run_id: Optional custom test run ID

        Returns:
            TestRun instance
        """
        if not test_run_id:
            test_run_id = f"JBOX001-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        test_run = self.runner.create_test_run(
            protocol=self.protocol,
            test_run_id=test_run_id,
            operator=operator,
            sample_id=sample_id
        )

        return test_run

    def run_initial_characterization(self, test_run: TestRun,
                                    visual_inspection: Dict[str, Any],
                                    contact_resistance: float,
                                    diode_voltage: List[float],
                                    insulation_resistance: float,
                                    iv_curve_data: Dict[str, Any]) -> None:
        """
        Execute Phase 1: Initial Characterization.

        Args:
            test_run: TestRun instance
            visual_inspection: Visual inspection results
            contact_resistance: Contact resistance in mΩ
            diode_voltage: List of diode forward voltages
            insulation_resistance: Insulation resistance in MΩ
            iv_curve_data: I-V curve measurement data
        """
        phase_id = "P1"
        test_run.set_phase(phase_id, PhaseStatus.IN_PROGRESS)

        # Step 1: Visual inspection
        test_run.set_step(phase_id, "P1-S1", "completed", visual_inspection)
        test_run.add_note(
            f"Visual inspection completed. Defects found: {visual_inspection.get('defects_count', 0)}"
        )

        # Step 2: Contact resistance
        test_run.set_step(phase_id, "P1-S2", "completed", {"resistance": contact_resistance})
        test_run.add_measurement("M1", contact_resistance, "mΩ",
                               metadata={"phase": "initial"})

        # Validate measurement
        is_valid, error = self.validator.validate_measurement("M1", contact_resistance)
        if not is_valid:
            test_run.add_note(f"Warning: {error}", "warning")

        # Step 3: Diode forward voltage
        avg_diode_voltage = sum(diode_voltage) / len(diode_voltage) if diode_voltage else 0
        test_run.set_step(phase_id, "P1-S3", "completed", {
            "diode_voltages": diode_voltage,
            "average": avg_diode_voltage
        })
        test_run.add_measurement("M2", avg_diode_voltage, "V",
                               metadata={"phase": "initial", "readings": diode_voltage})

        # Step 4: Insulation resistance
        test_run.set_step(phase_id, "P1-S4", "completed", {
            "insulation_resistance": insulation_resistance
        })
        test_run.add_measurement("M3", insulation_resistance, "MΩ",
                               metadata={"phase": "initial"})

        # Step 5: I-V curve
        test_run.set_step(phase_id, "P1-S5", "completed", iv_curve_data)

        # Extract and store I-V parameters
        test_run.add_measurement("M5", iv_curve_data.get('pmax', 0), "W",
                               metadata={"phase": "initial"})
        test_run.add_measurement("M6", iv_curve_data.get('voc', 0), "V",
                               metadata={"phase": "initial"})
        test_run.add_measurement("M7", iv_curve_data.get('isc', 0), "A",
                               metadata={"phase": "initial"})

        test_run.set_phase(phase_id, PhaseStatus.COMPLETED)
        test_run.add_note("Initial characterization completed successfully", "info")

    def run_thermal_cycling(self, test_run: TestRun, cycles_completed: int,
                          interim_measurements: Optional[List[Dict]] = None) -> None:
        """
        Execute Phase 2: Thermal Cycling Stress.

        Args:
            test_run: TestRun instance
            cycles_completed: Number of thermal cycles completed
            interim_measurements: Optional list of interim measurement data
        """
        phase_id = "P2"
        test_run.set_phase(phase_id, PhaseStatus.IN_PROGRESS)

        # Step 1: Thermal cycling
        test_run.set_step(phase_id, "P2-S1", "in_progress", {
            "cycles_completed": cycles_completed,
            "target_cycles": 200
        })
        test_run.add_note(f"Thermal cycling: {cycles_completed}/200 cycles completed")

        # Step 2: Interim measurements
        if interim_measurements:
            for measurement in interim_measurements:
                cycle_num = measurement.get('cycle')
                test_run.add_note(f"Interim measurement at cycle {cycle_num}", "info")

                if 'contact_resistance' in measurement:
                    test_run.add_measurement(
                        "M1",
                        measurement['contact_resistance'],
                        "mΩ",
                        metadata={"phase": "thermal_cycling", "cycle": cycle_num}
                    )

                if 'diode_voltage' in measurement:
                    test_run.add_measurement(
                        "M2",
                        measurement['diode_voltage'],
                        "V",
                        metadata={"phase": "thermal_cycling", "cycle": cycle_num}
                    )

        if cycles_completed >= 200:
            test_run.set_step(phase_id, "P2-S1", "completed", {
                "cycles_completed": cycles_completed
            })
            test_run.set_phase(phase_id, PhaseStatus.COMPLETED)
            test_run.add_note("Thermal cycling phase completed", "info")
        else:
            test_run.add_note(
                f"Thermal cycling in progress: {cycles_completed}/200 cycles",
                "info"
            )

    def run_humidity_freeze(self, test_run: TestRun, cycles_completed: int,
                          weight_gain_percentage: Optional[float] = None) -> None:
        """
        Execute Phase 3: Humidity-Freeze Stress.

        Args:
            test_run: TestRun instance
            cycles_completed: Number of HF cycles completed
            weight_gain_percentage: Optional weight gain percentage
        """
        phase_id = "P3"
        test_run.set_phase(phase_id, PhaseStatus.IN_PROGRESS)

        # Step 1: Humidity-freeze cycling
        test_run.set_step(phase_id, "P3-S1", "completed" if cycles_completed >= 10 else "in_progress", {
            "cycles_completed": cycles_completed,
            "target_cycles": 10
        })

        # Step 2: Moisture ingress inspection
        if weight_gain_percentage is not None:
            test_run.set_step(phase_id, "P3-S2", "completed", {
                "weight_gain_percentage": weight_gain_percentage
            })
            test_run.add_note(
                f"Weight gain: {weight_gain_percentage}% "
                f"({'PASS' if weight_gain_percentage < 1 else 'FAIL'})"
            )

        if cycles_completed >= 10:
            test_run.set_phase(phase_id, PhaseStatus.COMPLETED)
            test_run.add_note("Humidity-freeze phase completed", "info")

    def run_uv_exposure(self, test_run: TestRun, uv_dose: float,
                       degradation_assessment: Dict[str, Any]) -> None:
        """
        Execute Phase 4: UV Exposure Stress.

        Args:
            test_run: TestRun instance
            uv_dose: UV dose in kWh/m²
            degradation_assessment: Material degradation results
        """
        phase_id = "P4"
        test_run.set_phase(phase_id, PhaseStatus.IN_PROGRESS)

        # Step 1: UV preconditioning
        test_run.set_step(phase_id, "P4-S1", "completed", {
            "uv_dose": uv_dose,
            "target_dose": 15
        })

        # Step 2: Material degradation assessment
        test_run.set_step(phase_id, "P4-S2", "completed", degradation_assessment)

        test_run.add_measurement("M8", degradation_assessment.get('defects_count', 0),
                               "count", metadata={"phase": "uv_exposure"})

        test_run.set_phase(phase_id, PhaseStatus.COMPLETED)
        test_run.add_note("UV exposure phase completed", "info")

    def run_electrical_load_stress(self, test_run: TestRun,
                                  temperature_data: List[Dict],
                                  resistance_data: List[Dict]) -> None:
        """
        Execute Phase 5: Electrical Load Stress.

        Args:
            test_run: TestRun instance
            temperature_data: List of temperature measurements
            resistance_data: List of resistance measurements
        """
        phase_id = "P5"
        test_run.set_phase(phase_id, PhaseStatus.IN_PROGRESS)

        # Step 1: Continuous current load
        test_run.set_step(phase_id, "P5-S1", "in_progress", {
            "duration_hours": len(temperature_data)
        })

        # Step 2: Temperature monitoring
        max_temp = 0
        for temp_reading in temperature_data:
            timestamp = temp_reading.get('timestamp')
            temp_value = temp_reading.get('temperature')

            test_run.add_measurement("M4", temp_value, "°C",
                                   timestamp=timestamp,
                                   metadata={"phase": "electrical_stress"})

            if temp_value > max_temp:
                max_temp = temp_value

        test_run.set_step(phase_id, "P5-S2", "completed", {
            "max_temperature": max_temp,
            "measurements_count": len(temperature_data)
        })

        # Step 3: Resistance monitoring
        for res_reading in resistance_data:
            test_run.add_measurement(
                "M1",
                res_reading.get('resistance'),
                "mΩ",
                timestamp=res_reading.get('timestamp'),
                metadata={"phase": "electrical_stress"}
            )

        test_run.set_step(phase_id, "P5-S3", "completed", {
            "measurements_count": len(resistance_data)
        })

        if len(temperature_data) >= 168:  # 168 hours = 7 days
            test_run.set_phase(phase_id, PhaseStatus.COMPLETED)
            test_run.add_note("Electrical load stress phase completed", "info")

    def run_final_characterization(self, test_run: TestRun,
                                  visual_inspection: Dict[str, Any],
                                  contact_resistance: float,
                                  diode_voltage: List[float],
                                  insulation_resistance: float,
                                  iv_curve_data: Dict[str, Any],
                                  destructive_analysis: Optional[Dict] = None) -> None:
        """
        Execute Phase 6: Final Characterization.

        Args:
            test_run: TestRun instance
            visual_inspection: Final visual inspection results
            contact_resistance: Final contact resistance in mΩ
            diode_voltage: List of final diode forward voltages
            insulation_resistance: Final insulation resistance in MΩ
            iv_curve_data: Final I-V curve measurement data
            destructive_analysis: Optional destructive analysis results
        """
        phase_id = "P6"
        test_run.set_phase(phase_id, PhaseStatus.IN_PROGRESS)

        # Step 1: Repeat all initial measurements
        test_run.set_step(phase_id, "P6-S1", "completed", {
            "visual_inspection": visual_inspection,
            "contact_resistance": contact_resistance,
            "diode_voltage": diode_voltage,
            "insulation_resistance": insulation_resistance,
            "iv_curve": iv_curve_data
        })

        # Store final measurements
        test_run.add_measurement("M1", contact_resistance, "mΩ",
                               metadata={"phase": "final"})

        avg_diode_voltage = sum(diode_voltage) / len(diode_voltage) if diode_voltage else 0
        test_run.add_measurement("M2", avg_diode_voltage, "V",
                               metadata={"phase": "final", "readings": diode_voltage})

        test_run.add_measurement("M3", insulation_resistance, "MΩ",
                               metadata={"phase": "final"})

        test_run.add_measurement("M5", iv_curve_data.get('pmax', 0), "W",
                               metadata={"phase": "final"})
        test_run.add_measurement("M6", iv_curve_data.get('voc', 0), "V",
                               metadata={"phase": "final"})
        test_run.add_measurement("M7", iv_curve_data.get('isc', 0), "A",
                               metadata={"phase": "final"})

        test_run.add_measurement("M8", visual_inspection.get('defects_count', 0),
                               "count", metadata={"phase": "final"})

        # Step 2: Destructive analysis (optional)
        if destructive_analysis:
            test_run.set_step(phase_id, "P6-S2", "completed", destructive_analysis)

        # Step 3: Calculate degradation metrics
        initial_measurements = self._extract_initial_measurements(test_run)
        final_measurements = {
            'M1': contact_resistance,
            'M2': avg_diode_voltage,
            'M3': insulation_resistance,
            'M5': iv_curve_data.get('pmax', 0),
            'M6': iv_curve_data.get('voc', 0),
            'M7': iv_curve_data.get('isc', 0)
        }

        degradation_metrics = self.validator.calculate_degradation_metrics(
            initial_measurements,
            final_measurements
        )

        test_run.set_step(phase_id, "P6-S3", "completed", degradation_metrics)
        test_run.add_note(
            f"Power degradation: {degradation_metrics.get('power_degradation_percentage', 0):.2f}%"
        )

        # Evaluate QC criteria
        qc_results = self.validator.evaluate_acceptance_criteria(degradation_metrics)
        test_run.qc_results = qc_results

        test_run.set_phase(phase_id, PhaseStatus.COMPLETED)

        # Add final summary note
        if qc_results['overall_pass']:
            test_run.add_note("Final characterization completed - TEST PASSED", "info")
        else:
            test_run.add_note(
                f"Final characterization completed - TEST FAILED "
                f"({len(qc_results['critical_failures'])} critical failures)",
                "error"
            )

    def _extract_initial_measurements(self, test_run: TestRun) -> Dict[str, float]:
        """Extract initial measurements from test run."""
        initial = {}

        for measurement in test_run.measurements:
            if measurement.get('metadata', {}).get('phase') == 'initial':
                measurement_id = measurement['measurement_id']
                if measurement_id not in initial:  # Take first occurrence
                    initial[measurement_id] = measurement['value']

        return initial

    def generate_test_report(self, test_run: TestRun) -> Dict[str, Any]:
        """
        Generate comprehensive test report.

        Args:
            test_run: TestRun instance

        Returns:
            Complete test report dictionary
        """
        report = {
            'protocol': {
                'id': self.PROTOCOL_ID,
                'name': self.protocol['name'],
                'version': self.protocol['version']
            },
            'test_run': test_run.get_summary(),
            'test_data': test_run.to_dict(),
            'validation': self.validator.generate_validation_report({
                'test_run_id': test_run.test_run_id,
                'measurements': test_run.measurements,
                'metrics': test_run.qc_results.get('criteria_results', [])
                           if hasattr(test_run, 'qc_results') and test_run.qc_results
                           else {}
            }),
            'generated_at': datetime.now().isoformat()
        }

        return report


if __name__ == "__main__":
    # Example usage
    protocol = JBOX001Protocol()

    # Create test run
    test_run = protocol.create_test_run(
        sample_id="MODULE-JBOX-001",
        operator="Jane Smith"
    )

    # Start test
    protocol.runner.start_test_run(test_run.test_run_id)

    # Run initial characterization
    protocol.run_initial_characterization(
        test_run=test_run,
        visual_inspection={'defects_count': 0, 'notes': 'No visible defects'},
        contact_resistance=5.2,
        diode_voltage=[0.65, 0.64, 0.66],
        insulation_resistance=100.0,
        iv_curve_data={'pmax': 300.0, 'voc': 40.5, 'isc': 9.2}
    )

    # Simulate thermal cycling
    protocol.run_thermal_cycling(test_run, cycles_completed=200)

    # Run final characterization
    protocol.run_final_characterization(
        test_run=test_run,
        visual_inspection={'defects_count': 1, 'notes': 'Minor discoloration'},
        contact_resistance=5.8,
        diode_voltage=[0.66, 0.65, 0.67],
        insulation_resistance=95.0,
        iv_curve_data={'pmax': 288.0, 'voc': 40.3, 'isc': 9.1}
    )

    # Complete test
    protocol.runner.complete_test_run(test_run.test_run_id)

    # Generate report
    report = protocol.generate_test_report(test_run)
    print(f"Test completed: {report['test_run']['status']}")
    print(f"QC Pass: {test_run.qc_results.get('overall_pass', False)}")

    # Save test run
    filepath = test_run.save()
    print(f"Test run saved to: {filepath}")
