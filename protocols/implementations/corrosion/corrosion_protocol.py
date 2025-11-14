"""
CORR-001 Corrosion Testing Protocol Implementation

Implements salt spray and humidity testing for photovoltaic modules
according to IEC 61701 and ASTM B117 standards.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from ..base_protocol import BaseProtocol, ProtocolStep


class CorrosionProtocol(BaseProtocol):
    """
    CORR-001 Corrosion Testing Protocol

    Implements accelerated corrosion testing using salt spray and humidity
    exposure cycles. Tracks electrical performance degradation and visual
    corrosion indicators.
    """

    def __init__(self, definition_path: Optional[Path] = None):
        """
        Initialize CORR-001 protocol.

        Args:
            definition_path: Path to protocol definition JSON file
        """
        if definition_path is None:
            # Default to protocol definition in standard location
            definition_path = Path(__file__).parent.parent.parent / \
                            "definitions" / "corrosion" / "corr-001.json"

        super().__init__(definition_path=definition_path)

        # Protocol-specific state
        self.current_cycle = 0
        self.salt_spray_logs: List[Dict[str, Any]] = []
        self.humidity_logs: List[Dict[str, Any]] = []
        self.inspection_history: List[Dict[str, Any]] = []
        self.electrical_history: List[Dict[str, Any]] = []

    def execute_step(self, step_number: int, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute a specific protocol step.

        Args:
            step_number: Step number to execute (1-13)
            **kwargs: Step-specific parameters

        Returns:
            Step execution results
        """
        step_handlers = {
            1: self._step_initial_documentation,
            2: self._step_baseline_electrical,
            3: self._step_prepare_solution,
            4: self._step_salt_spray_exposure,
            5: self._step_post_spray_recovery,
            6: self._step_humidity_exposure,
            7: self._step_post_humidity_recovery,
            8: self._step_interim_visual,
            9: self._step_interim_electrical,
            10: self._step_repeat_cycles,
            11: self._step_final_visual,
            12: self._step_final_electrical,
            13: self._step_analysis_report
        }

        handler = step_handlers.get(step_number)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown step number: {step_number}"
            }

        try:
            result = handler(**kwargs)
            self.mark_step_complete(step_number)
            return {
                "success": True,
                "step_number": step_number,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "step_number": step_number,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _step_initial_documentation(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 1: Initial documentation and inspection"""
        sample_id = kwargs.get("sample_id")
        serial_number = kwargs.get("serial_number")
        operator = kwargs.get("operator")
        photos = kwargs.get("photos", [])

        if not all([sample_id, serial_number, operator]):
            raise ValueError("Missing required parameters: sample_id, serial_number, operator")

        # Record initial state
        initial_data = {
            "sample_id": sample_id,
            "serial_number": serial_number,
            "operator": operator,
            "test_date": datetime.now().isoformat(),
            "initial_photos": photos,
            "initial_inspection_notes": kwargs.get("notes", "")
        }

        if self.test_run:
            self.test_run.data.update(initial_data)

        return {
            "message": "Initial documentation completed",
            "sample_id": sample_id,
            "photos_count": len(photos)
        }

    def _step_baseline_electrical(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 2: Baseline electrical characterization"""
        required_params = ["baseline_voc", "baseline_isc", "baseline_pmax", "baseline_ff"]

        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")

        baseline_data = {
            "baseline_voc": kwargs["baseline_voc"],
            "baseline_isc": kwargs["baseline_isc"],
            "baseline_pmax": kwargs["baseline_pmax"],
            "baseline_ff": kwargs["baseline_ff"],
            "baseline_rs": kwargs.get("baseline_rs"),
            "baseline_rsh": kwargs.get("baseline_rsh"),
            "baseline_el_images": kwargs.get("el_images", []),
            "baseline_timestamp": datetime.now().isoformat()
        }

        if self.test_run:
            self.test_run.data.update(baseline_data)

        self.electrical_history.append({
            "cycle": 0,
            "type": "baseline",
            **baseline_data
        })

        return {
            "message": "Baseline electrical characterization completed",
            "voc": baseline_data["baseline_voc"],
            "isc": baseline_data["baseline_isc"],
            "pmax": baseline_data["baseline_pmax"],
            "ff": baseline_data["baseline_ff"]
        }

    def _step_prepare_solution(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 3: Prepare salt spray solution"""
        concentration = kwargs.get("salt_solution_concentration")
        ph = kwargs.get("salt_solution_ph")

        if not concentration or not ph:
            raise ValueError("Missing salt_solution_concentration or salt_solution_ph")

        # Validate concentration and pH
        if not (4.0 <= concentration <= 6.0):
            raise ValueError(f"Salt concentration {concentration}% outside valid range (4-6%)")

        if not (6.5 <= ph <= 7.2):
            raise ValueError(f"pH {ph} outside valid range (6.5-7.2)")

        solution_data = {
            "salt_solution_concentration": concentration,
            "salt_solution_ph": ph,
            "solution_prep_timestamp": datetime.now().isoformat()
        }

        if self.test_run:
            self.test_run.data.update(solution_data)

        return {
            "message": "Salt solution prepared and validated",
            "concentration": concentration,
            "ph": ph,
            "status": "ready"
        }

    def _step_salt_spray_exposure(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 4: Salt spray exposure cycle"""
        target_duration = kwargs.get("duration_hours", 48)
        temperature = kwargs.get("spray_temp")

        if not temperature:
            raise ValueError("Missing spray_temp parameter")

        if not (33 <= temperature <= 37):
            raise ValueError(f"Spray temperature {temperature}°C outside valid range (33-37°C)")

        self.current_cycle += 1

        exposure_data = {
            "spray_temp": temperature,
            "spray_duration": target_duration,
            "spray_start": datetime.now().isoformat(),
            "spray_end": (datetime.now() + timedelta(hours=target_duration)).isoformat()
        }

        self.salt_spray_logs.append({
            "cycle": self.current_cycle,
            **exposure_data
        })

        if self.test_run:
            self.test_run.data[f"cycle_{self.current_cycle}_spray"] = exposure_data

        return {
            "message": f"Salt spray exposure cycle {self.current_cycle} started",
            "cycle": self.current_cycle,
            "duration_hours": target_duration,
            "temperature": temperature,
            "expected_completion": exposure_data["spray_end"]
        }

    def _step_post_spray_recovery(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 5: Post-spray recovery and drying"""
        recovery_start = datetime.now()
        recovery_duration = kwargs.get("recovery_hours", 24)

        recovery_data = {
            "recovery_start": recovery_start.isoformat(),
            "recovery_end": (recovery_start + timedelta(hours=recovery_duration)).isoformat(),
            "rinse_completed": kwargs.get("rinse_completed", True),
            "drying_completed": kwargs.get("drying_completed", True)
        }

        if self.test_run:
            self.test_run.data[f"cycle_{self.current_cycle}_spray_recovery"] = recovery_data

        return {
            "message": "Post-spray recovery completed",
            "cycle": self.current_cycle,
            "duration_hours": recovery_duration
        }

    def _step_humidity_exposure(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 6: Humidity exposure cycle"""
        target_duration = kwargs.get("duration_hours", 96)
        temperature = kwargs.get("humidity_temp")
        rh = kwargs.get("humidity_rh")

        if not temperature or not rh:
            raise ValueError("Missing humidity_temp or humidity_rh parameter")

        if not (83 <= temperature <= 87):
            raise ValueError(f"Humidity temperature {temperature}°C outside valid range (83-87°C)")

        if not (80 <= rh <= 90):
            raise ValueError(f"Relative humidity {rh}% outside valid range (80-90%)")

        exposure_data = {
            "humidity_temp": temperature,
            "humidity_rh": rh,
            "humidity_duration": target_duration,
            "humidity_start": datetime.now().isoformat(),
            "humidity_end": (datetime.now() + timedelta(hours=target_duration)).isoformat()
        }

        self.humidity_logs.append({
            "cycle": self.current_cycle,
            **exposure_data
        })

        if self.test_run:
            self.test_run.data[f"cycle_{self.current_cycle}_humidity"] = exposure_data

        return {
            "message": f"Humidity exposure cycle {self.current_cycle} started",
            "cycle": self.current_cycle,
            "duration_hours": target_duration,
            "temperature": temperature,
            "rh": rh,
            "expected_completion": exposure_data["humidity_end"]
        }

    def _step_post_humidity_recovery(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 7: Post-humidity recovery"""
        recovery_duration = kwargs.get("recovery_hours", 4)

        recovery_data = {
            "recovery_start": datetime.now().isoformat(),
            "recovery_end": (datetime.now() + timedelta(hours=recovery_duration)).isoformat(),
            "equilibration_completed": kwargs.get("equilibration_completed", True)
        }

        if self.test_run:
            self.test_run.data[f"cycle_{self.current_cycle}_humidity_recovery"] = recovery_data

        return {
            "message": "Post-humidity recovery completed",
            "cycle": self.current_cycle,
            "duration_hours": recovery_duration
        }

    def _step_interim_visual(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 8: Interim visual inspection"""
        inspection_data = {
            "cycle_number": self.current_cycle,
            "visual_corrosion": kwargs.get("visual_corrosion", "None"),
            "corrosion_location": kwargs.get("corrosion_location", []),
            "delamination": kwargs.get("delamination", False),
            "discoloration": kwargs.get("discoloration", False),
            "photos": kwargs.get("photos", []),
            "notes": kwargs.get("notes", ""),
            "timestamp": datetime.now().isoformat()
        }

        self.inspection_history.append(inspection_data)

        if self.test_run:
            self.test_run.data[f"cycle_{self.current_cycle}_visual"] = inspection_data

        return {
            "message": f"Interim visual inspection cycle {self.current_cycle} completed",
            "cycle": self.current_cycle,
            "corrosion": inspection_data["visual_corrosion"],
            "delamination": inspection_data["delamination"]
        }

    def _step_interim_electrical(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 9: Interim electrical testing"""
        electrical_data = {
            "cycle_number": self.current_cycle,
            "interim_voc": kwargs.get("interim_voc"),
            "interim_isc": kwargs.get("interim_isc"),
            "interim_pmax": kwargs.get("interim_pmax"),
            "insulation_resistance": kwargs.get("insulation_resistance"),
            "timestamp": datetime.now().isoformat()
        }

        # Calculate degradation
        if self.test_run and "baseline_pmax" in self.test_run.data:
            baseline_pmax = self.test_run.data["baseline_pmax"]
            interim_pmax = electrical_data["interim_pmax"]
            if baseline_pmax and interim_pmax:
                degradation = ((baseline_pmax - interim_pmax) / baseline_pmax) * 100
                electrical_data["power_degradation"] = degradation

        self.electrical_history.append(electrical_data)

        if self.test_run:
            self.test_run.data[f"cycle_{self.current_cycle}_electrical"] = electrical_data

        return {
            "message": f"Interim electrical testing cycle {self.current_cycle} completed",
            "cycle": self.current_cycle,
            "pmax": electrical_data["interim_pmax"],
            "degradation": electrical_data.get("power_degradation")
        }

    def _step_repeat_cycles(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 10: Repeat exposure cycles"""
        target_cycles = kwargs.get("total_cycles", 3)

        return {
            "message": f"Repeating cycles - {self.current_cycle} of {target_cycles} completed",
            "current_cycle": self.current_cycle,
            "target_cycles": target_cycles,
            "remaining": target_cycles - self.current_cycle
        }

    def _step_final_visual(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 11: Final visual inspection"""
        final_inspection = {
            "final_visual_corrosion": kwargs.get("visual_corrosion", "None"),
            "final_corrosion_location": kwargs.get("corrosion_location", []),
            "final_delamination": kwargs.get("delamination", False),
            "final_discoloration": kwargs.get("discoloration", False),
            "final_photos": kwargs.get("photos", []),
            "final_inspection_notes": kwargs.get("notes", ""),
            "final_inspection_timestamp": datetime.now().isoformat()
        }

        if self.test_run:
            self.test_run.data.update(final_inspection)

        return {
            "message": "Final visual inspection completed",
            "corrosion": final_inspection["final_visual_corrosion"],
            "delamination": final_inspection["final_delamination"],
            "photos_count": len(final_inspection["final_photos"])
        }

    def _step_final_electrical(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 12: Final electrical characterization"""
        final_electrical = {
            "final_voc": kwargs.get("final_voc"),
            "final_isc": kwargs.get("final_isc"),
            "final_pmax": kwargs.get("final_pmax"),
            "final_ff": kwargs.get("final_ff"),
            "wet_leakage_current": kwargs.get("wet_leakage_current"),
            "ground_continuity": kwargs.get("ground_continuity"),
            "final_el_images": kwargs.get("el_images", []),
            "final_electrical_timestamp": datetime.now().isoformat()
        }

        # Calculate total degradation
        if self.test_run and "baseline_pmax" in self.test_run.data:
            baseline_pmax = self.test_run.data["baseline_pmax"]
            final_pmax = final_electrical["final_pmax"]
            if baseline_pmax and final_pmax:
                degradation = ((baseline_pmax - final_pmax) / baseline_pmax) * 100
                final_electrical["total_power_degradation"] = degradation

        if self.test_run:
            self.test_run.data.update(final_electrical)

        return {
            "message": "Final electrical characterization completed",
            "voc": final_electrical["final_voc"],
            "isc": final_electrical["final_isc"],
            "pmax": final_electrical["final_pmax"],
            "ff": final_electrical["final_ff"],
            "total_degradation": final_electrical.get("total_power_degradation")
        }

    def _step_analysis_report(self, **kwargs: Any) -> Dict[str, Any]:
        """Step 13: Data analysis and report generation"""
        if not self.test_run:
            raise ValueError("No test run data available")

        # Run QC checks
        qc_results = self.run_qc_checks(self.test_run.data)

        # Calculate results
        calculated_results = self.calculate_results(self.test_run.data)

        # Determine pass/fail
        critical_failures = [r for r in qc_results if not r["passed"] and r["severity"] == "critical"]
        test_result = "Fail" if critical_failures else "Pass"

        analysis_data = {
            "test_result": test_result,
            "qc_results": qc_results,
            "calculated_results": calculated_results,
            "analysis_timestamp": datetime.now().isoformat()
        }

        if self.test_run:
            self.test_run.data.update(analysis_data)
            self.test_run.qc_results = qc_results
            self.test_run.status = "completed"
            self.test_run.end_date = datetime.now()

        return {
            "message": "Analysis and report generation completed",
            "test_result": test_result,
            "critical_failures": len(critical_failures),
            "total_qc_checks": len(qc_results)
        }

    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """
        Generate comprehensive test report.

        Args:
            output_path: Optional path to save report

        Returns:
            Report content as markdown string
        """
        if not self.test_run:
            return "Error: No test run data available"

        report_sections = []

        # Header
        report_sections.append(f"# {self.definition.name}")
        report_sections.append(f"**Protocol ID:** {self.definition.protocol_id}")
        report_sections.append(f"**Version:** {self.definition.version}")
        report_sections.append(f"**Test Run ID:** {self.test_run.run_id}")
        report_sections.append(f"**Date:** {self.test_run.start_date.strftime('%Y-%m-%d')}")
        report_sections.append(f"**Operator:** {self.test_run.operator}")
        report_sections.append("\n---\n")

        # Executive Summary
        report_sections.append("## Executive Summary")
        test_result = self.test_run.data.get("test_result", "Unknown")
        report_sections.append(f"**Test Result:** {test_result}")

        if "total_power_degradation" in self.test_run.data:
            degradation = self.test_run.data["total_power_degradation"]
            report_sections.append(f"**Total Power Degradation:** {degradation:.2f}%")

        report_sections.append(f"**Cycles Completed:** {self.current_cycle}")
        report_sections.append("\n")

        # Sample Information
        report_sections.append("## Sample Information")
        report_sections.append(f"- **Sample ID:** {self.test_run.data.get('sample_id', 'N/A')}")
        report_sections.append(f"- **Serial Number:** {self.test_run.data.get('serial_number', 'N/A')}")
        report_sections.append("\n")

        # Baseline Measurements
        report_sections.append("## Baseline Measurements")
        report_sections.append(f"- **Voc:** {self.test_run.data.get('baseline_voc', 'N/A')} V")
        report_sections.append(f"- **Isc:** {self.test_run.data.get('baseline_isc', 'N/A')} A")
        report_sections.append(f"- **Pmax:** {self.test_run.data.get('baseline_pmax', 'N/A')} W")
        report_sections.append(f"- **FF:** {self.test_run.data.get('baseline_ff', 'N/A')} %")
        report_sections.append("\n")

        # Final Measurements
        report_sections.append("## Final Measurements")
        report_sections.append(f"- **Voc:** {self.test_run.data.get('final_voc', 'N/A')} V")
        report_sections.append(f"- **Isc:** {self.test_run.data.get('final_isc', 'N/A')} A")
        report_sections.append(f"- **Pmax:** {self.test_run.data.get('final_pmax', 'N/A')} W")
        report_sections.append(f"- **FF:** {self.test_run.data.get('final_ff', 'N/A')} %")
        report_sections.append("\n")

        # QC Results
        report_sections.append("## Quality Control Results")
        for qc in self.test_run.qc_results:
            status = "✓ PASS" if qc["passed"] else "✗ FAIL"
            report_sections.append(f"- **{qc['name']}:** {status} - {qc['message']}")
        report_sections.append("\n")

        # Visual Inspection Summary
        report_sections.append("## Visual Inspection Summary")
        report_sections.append(f"- **Corrosion:** {self.test_run.data.get('final_visual_corrosion', 'N/A')}")
        report_sections.append(f"- **Delamination:** {self.test_run.data.get('final_delamination', 'N/A')}")
        report_sections.append(f"- **Discoloration:** {self.test_run.data.get('final_discoloration', 'N/A')}")
        report_sections.append("\n")

        # Standards Compliance
        report_sections.append("## Standards Compliance")
        for standard in self.definition.standards:
            report_sections.append(f"- {standard['name']} {standard['number']}: {standard['title']}")
        report_sections.append("\n")

        report_content = "\n".join(report_sections)

        # Save to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(report_content)
            return str(output_path)

        return report_content

    def get_degradation_curve(self) -> pd.DataFrame:
        """
        Get degradation curve data over all cycles.

        Returns:
            DataFrame with cycle number and power measurements
        """
        data = []

        # Add baseline
        if self.test_run and "baseline_pmax" in self.test_run.data:
            data.append({
                "cycle": 0,
                "type": "baseline",
                "pmax": self.test_run.data["baseline_pmax"]
            })

        # Add interim measurements
        for measurement in self.electrical_history:
            if "interim_pmax" in measurement:
                data.append({
                    "cycle": measurement.get("cycle_number", 0),
                    "type": "interim",
                    "pmax": measurement["interim_pmax"]
                })

        # Add final
        if self.test_run and "final_pmax" in self.test_run.data:
            data.append({
                "cycle": self.current_cycle,
                "type": "final",
                "pmax": self.test_run.data["final_pmax"]
            })

        return pd.DataFrame(data)
