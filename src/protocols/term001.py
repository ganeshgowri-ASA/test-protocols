"""TERM-001: Terminal Robustness Test implementation."""

from pathlib import Path
from typing import Any, Dict

from .base import BaseProtocol, ProtocolStep


class TERM001Protocol(BaseProtocol):
    """Terminal Robustness Test protocol implementation."""

    def __init__(self, protocol_file: Path = None):
        """Initialize TERM-001 protocol."""
        if protocol_file is None:
            # Default to the template file
            protocol_file = Path(__file__).parent / "templates" / "term-001.json"
        super().__init__(protocol_file)

    def calculate_derived_values(self, step: ProtocolStep):
        """
        Calculate derived values for TERM-001 protocol.

        For step 5 (Post-Stress Electrical Continuity Test):
        - Calculate resistance_change_positive
        - Calculate resistance_change_negative
        """
        if step.step_number == 5:
            # Get initial resistance values from step 2
            step_2 = self.steps[1]  # Index 1 is step 2
            if "resistance_positive" in step_2.results:
                initial_positive = step_2.results["resistance_positive"]
                post_positive = step.results.get("resistance_positive_post", 0)

                if initial_positive > 0:
                    change_positive = (
                        (post_positive - initial_positive) / initial_positive * 100
                    )
                    step.results["resistance_change_positive"] = round(change_positive, 2)

            if "resistance_negative" in step_2.results:
                initial_negative = step_2.results["resistance_negative"]
                post_negative = step.results.get("resistance_negative_post", 0)

                if initial_negative > 0:
                    change_negative = (
                        (post_negative - initial_negative) / initial_negative * 100
                    )
                    step.results["resistance_change_negative"] = round(change_negative, 2)

    def get_resistance_data(self) -> Dict[str, Any]:
        """
        Get resistance measurement data for reporting and charting.

        Returns:
            Dictionary with resistance measurements and changes
        """
        data = {}

        # Get step 2 (initial) results
        if len(self.steps) > 1 and self.steps[1].completed:
            step_2 = self.steps[1]
            data["initial_positive"] = step_2.results.get("resistance_positive")
            data["initial_negative"] = step_2.results.get("resistance_negative")

        # Get step 5 (post-stress) results
        if len(self.steps) > 4 and self.steps[4].completed:
            step_5 = self.steps[4]
            data["post_positive"] = step_5.results.get("resistance_positive_post")
            data["post_negative"] = step_5.results.get("resistance_negative_post")
            data["change_positive"] = step_5.results.get("resistance_change_positive")
            data["change_negative"] = step_5.results.get("resistance_change_negative")

        return data

    def get_mechanical_data(self) -> Dict[str, Any]:
        """
        Get mechanical test data (pull force and torque).

        Returns:
            Dictionary with mechanical test results
        """
        data = {}

        # Get step 3 (pull force) results
        if len(self.steps) > 2 and self.steps[2].completed:
            step_3 = self.steps[2]
            data["pull_force"] = step_3.results.get("pull_force_applied")
            data["displacement"] = step_3.results.get("terminal_displacement")
            data["cable_pulled_out"] = step_3.results.get("cable_pulled_out")

        # Get step 4 (torque) results
        if len(self.steps) > 3 and self.steps[3].completed:
            step_4 = self.steps[3]
            data["torque_applied"] = step_4.results.get("torque_applied")
            data["terminal_integrity"] = step_4.results.get("terminal_integrity")

        return data

    def get_dielectric_data(self) -> Dict[str, Any]:
        """
        Get dielectric strength test data.

        Returns:
            Dictionary with dielectric test results
        """
        data = {}

        # Get step 6 (dielectric test) results
        if len(self.steps) > 5 and self.steps[5].completed:
            step_6 = self.steps[5]
            data["test_voltage"] = step_6.results.get("test_voltage")
            data["leakage_current"] = step_6.results.get("leakage_current")
            data["breakdown_occurred"] = step_6.results.get("breakdown_occurred")

        return data

    def validate_equipment_calibration(self, equipment_list: list) -> tuple[bool, list]:
        """
        Validate that all required equipment is calibrated and within calibration period.

        Args:
            equipment_list: List of equipment with calibration dates

        Returns:
            Tuple of (all_valid, list_of_issues)
        """
        from datetime import datetime

        issues = []
        required_equipment = self.get_test_equipment()

        for req_equip in required_equipment:
            if not req_equip.get("calibration_required", False):
                continue

            equipment_name = req_equip["name"]
            found = False

            for equip in equipment_list:
                if equip.get("name") == equipment_name:
                    found = True
                    cal_due = equip.get("calibration_due_date")

                    if cal_due is None:
                        issues.append(f"{equipment_name}: No calibration due date provided")
                    elif isinstance(cal_due, str):
                        cal_due = datetime.fromisoformat(cal_due)

                    if cal_due and cal_due < datetime.now():
                        issues.append(f"{equipment_name}: Calibration expired on {cal_due}")
                    break

            if not found:
                issues.append(f"{equipment_name}: Equipment not found in provided list")

        return len(issues) == 0, issues
