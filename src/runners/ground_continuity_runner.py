"""
Ground Continuity Test Runner (GROUND-001)

Implements IEC 61730-2 MST 13 - Continuity of equipotential bonding test
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import time

from sqlalchemy.orm import Session

from .base_runner import BaseTestRunner
from ..models import TestExecution, TestOutcome

logger = logging.getLogger(__name__)


class GroundContinuityRunner(BaseTestRunner):
    """
    Test runner for Ground Continuity Test (GROUND-001)

    This runner implements the IEC 61730-2 MST 13 test procedure for
    verifying the continuity of equipotential bonding in PV modules.
    """

    def __init__(
        self,
        db_session: Session,
        protocol_json_path: Optional[str] = None
    ):
        """
        Initialize Ground Continuity Test Runner

        Args:
            db_session: SQLAlchemy database session
            protocol_json_path: Optional path to protocol JSON file
        """
        super().__init__(
            protocol_id="GROUND-001",
            db_session=db_session,
            protocol_json_path=protocol_json_path
        )

    def calculate_parameters(self, input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate test parameters from inputs

        Args:
            input_params: Must contain 'max_overcurrent_protection' in Amps

        Returns:
            Dictionary containing all calculated parameters
        """
        max_overcurrent = input_params.get('max_overcurrent_protection')
        if max_overcurrent is None:
            raise ValueError("max_overcurrent_protection is required")

        # Get parameters from protocol definition
        params = self.protocol_json['parameters']

        # Calculate test current (2.5 × max overcurrent protection)
        test_current = 2.5 * max_overcurrent

        # Compile all parameters
        calculated_params = {
            'max_overcurrent_protection': max_overcurrent,
            'test_current': test_current,
            'test_duration': params['test_duration']['value'],
            'voltage_limit': params['voltage_limit']['value'],
            'max_resistance': params['max_resistance']['value'],
            'ambient_temperature': input_params.get('ambient_temperature'),
            'relative_humidity': input_params.get('relative_humidity')
        }

        logger.info(f"Calculated test parameters: {calculated_params}")
        return calculated_params

    def run_test(
        self,
        test_execution: TestExecution,
        measurement_points: Optional[list] = None,
        auto_mode: bool = False,
        instrument_interface=None
    ) -> TestOutcome:
        """
        Execute the ground continuity test

        Args:
            test_execution: TestExecution object
            measurement_points: List of measurement point identifiers
                               (e.g., ["Frame to J-Box", "Frame to Connector"])
            auto_mode: If True, attempt to interface with test equipment
            instrument_interface: Optional instrument control interface

        Returns:
            TestOutcome (PASS/FAIL)
        """
        try:
            self.start_test(test_execution)

            # Get test parameters
            params = test_execution.parameters
            test_current = params['test_current']
            test_duration = params['test_duration']
            max_resistance = params['max_resistance']
            voltage_limit = params['voltage_limit']

            # Default measurement points if not provided
            if measurement_points is None:
                measurement_points = ["Point 1"]

            all_measurements_passed = True

            # Test each measurement point
            for idx, point in enumerate(measurement_points, 1):
                logger.info(f"Testing measurement point: {point}")

                # Record environmental conditions (if available)
                if idx == 1:  # Only record once at start
                    if params.get('ambient_temperature'):
                        self.add_measurement(
                            test_execution=test_execution,
                            measurement_name="ambient_temperature",
                            value=params['ambient_temperature'],
                            unit="°C"
                        )

                    if params.get('relative_humidity'):
                        self.add_measurement(
                            test_execution=test_execution,
                            measurement_name="relative_humidity",
                            value=params['relative_humidity'],
                            unit="%"
                        )

                # Execute measurement
                if auto_mode and instrument_interface:
                    # Automated measurement using instrument
                    measurement_data = self._automated_measurement(
                        instrument_interface,
                        test_current,
                        test_duration,
                        point
                    )
                else:
                    # Manual measurement (simulated for this example)
                    measurement_data = self._manual_measurement(
                        test_current,
                        test_duration,
                        point
                    )

                # Record measurements
                voltage_drop = measurement_data['voltage_drop']
                actual_current = measurement_data['actual_current']
                actual_duration = measurement_data['duration']

                # Calculate resistance (Ohm's law: R = V / I)
                measured_resistance = voltage_drop / actual_current if actual_current > 0 else float('inf')

                # Save measurements to database
                self.add_measurement(
                    test_execution=test_execution,
                    measurement_name="voltage_drop",
                    value=voltage_drop,
                    unit="V",
                    measurement_point=point,
                    within_limits=voltage_drop <= voltage_limit
                )

                self.add_measurement(
                    test_execution=test_execution,
                    measurement_name="test_current_actual",
                    value=actual_current,
                    unit="A",
                    measurement_point=point
                )

                self.add_measurement(
                    test_execution=test_execution,
                    measurement_name="measured_resistance",
                    value=measured_resistance,
                    unit="Ω",
                    measurement_point=point,
                    within_limits=measured_resistance <= max_resistance
                )

                self.add_measurement(
                    test_execution=test_execution,
                    measurement_name="test_duration_actual",
                    value=actual_duration,
                    unit="s",
                    measurement_point=point
                )

                # Check if this measurement point passed
                point_passed = (
                    measured_resistance <= max_resistance and
                    voltage_drop <= voltage_limit and
                    actual_duration >= test_duration
                )

                if not point_passed:
                    all_measurements_passed = False
                    logger.warning(
                        f"Measurement point '{point}' FAILED: "
                        f"R={measured_resistance:.4f}Ω (limit: {max_resistance}Ω), "
                        f"V={voltage_drop:.2f}V (limit: {voltage_limit}V)"
                    )
                else:
                    logger.info(
                        f"Measurement point '{point}' PASSED: "
                        f"R={measured_resistance:.4f}Ω, V={voltage_drop:.2f}V"
                    )

                # Check safety limits
                safety_action = self.check_safety_limits({
                    'voltage': voltage_drop,
                    'current': actual_current
                })

                if safety_action == 'stop':
                    self.abort_test(
                        test_execution,
                        "Safety limit exceeded - test stopped"
                    )
                    return TestOutcome.FAIL

            # Evaluate all pass/fail criteria
            all_measurements = {
                'measured_resistance': measured_resistance,  # Last measurement
                'voltage_drop': voltage_drop,
                'test_duration_actual': actual_duration,
                'test_current_actual': actual_current,
                'test_current': test_current,
                'max_resistance': max_resistance,
                'voltage_limit': voltage_limit,
                'test_duration': test_duration
            }

            results = self.evaluate_criteria(test_execution, all_measurements)

            # Determine overall outcome
            critical_failures = [r for r in results if not r.passed and r.severity == 'critical']

            if critical_failures or not all_measurements_passed:
                outcome = TestOutcome.FAIL
            else:
                outcome = TestOutcome.PASS

            self.complete_test(test_execution, outcome)
            return outcome

        except Exception as e:
            logger.error(f"Test execution failed: {e}", exc_info=True)
            self.abort_test(test_execution, f"Exception: {str(e)}")
            return TestOutcome.FAIL

    def _automated_measurement(
        self,
        instrument_interface,
        test_current: float,
        duration: float,
        measurement_point: str
    ) -> Dict[str, float]:
        """
        Perform automated measurement using instrument interface

        Args:
            instrument_interface: Instrument control interface
            test_current: Test current in Amps
            duration: Test duration in seconds
            measurement_point: Measurement point identifier

        Returns:
            Dictionary with voltage_drop, actual_current, and duration
        """
        logger.info(f"Starting automated measurement at {measurement_point}")

        try:
            # Configure instrument
            instrument_interface.set_current(test_current)
            instrument_interface.set_duration(duration)

            # Start test
            start_time = time.time()
            instrument_interface.start_test()

            # Wait for completion
            time.sleep(duration)

            # Read results
            voltage = instrument_interface.read_voltage()
            current = instrument_interface.read_current()
            end_time = time.time()

            actual_duration = end_time - start_time

            return {
                'voltage_drop': voltage,
                'actual_current': current,
                'duration': actual_duration
            }

        except Exception as e:
            logger.error(f"Automated measurement failed: {e}")
            raise

    def _manual_measurement(
        self,
        test_current: float,
        duration: float,
        measurement_point: str
    ) -> Dict[str, float]:
        """
        Placeholder for manual measurement entry

        In a real implementation, this would prompt the operator
        to enter measurements from the test equipment.

        Args:
            test_current: Test current in Amps
            duration: Test duration in seconds
            measurement_point: Measurement point identifier

        Returns:
            Dictionary with voltage_drop, actual_current, and duration
            (simulated values for demonstration)
        """
        logger.info(
            f"Manual measurement mode for {measurement_point}\n"
            f"Set test current to {test_current:.2f} A\n"
            f"Apply for {duration} seconds\n"
            f"Record voltage drop and actual current"
        )

        # In a real implementation, this would be entered by operator
        # For now, return simulated values
        # Simulate a good measurement (well within limits)
        simulated_voltage = min(test_current * 0.05, 1.0)  # ~0.05 Ω typical

        return {
            'voltage_drop': simulated_voltage,
            'actual_current': test_current * 0.99,  # Within 1% of target
            'duration': duration
        }

    def validate_sample(self, sample) -> tuple[bool, Optional[str]]:
        """
        Validate that the sample has required information for this test

        Args:
            sample: Sample object

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not sample.max_overcurrent_protection:
            return False, "Sample must have max_overcurrent_protection specified"

        if sample.max_overcurrent_protection <= 0:
            return False, "max_overcurrent_protection must be greater than 0"

        return True, None

    def get_required_equipment(self) -> list:
        """
        Get list of required equipment for this test

        Returns:
            List of equipment specifications from protocol JSON
        """
        return self.protocol_json.get('equipment', [])

    def get_procedure_steps(self) -> list:
        """
        Get test procedure steps

        Returns:
            List of procedure steps from protocol JSON
        """
        return self.protocol_json.get('procedure', [])
