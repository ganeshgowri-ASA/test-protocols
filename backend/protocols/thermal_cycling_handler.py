"""
Thermal Cycling Protocol Handler (PVTP-002-TC)
Handles cycle tracking, temperature profile validation, measurement analysis, and degradation calculations
for thermal cycling tests according to IEC 61215-2:2016 MQT 12
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CycleData:
    """Data structure for a single thermal cycle"""
    cycle_number: int
    timestamp: datetime
    chamber_temp: float
    humidity: float
    module_temps: Dict[str, float]  # {serial_number: temperature}
    cycle_phase: str  # heating, hot_dwell, cooling, cold_dwell
    alarms: List[str]


@dataclass
class MeasurementData:
    """Data structure for electrical measurements"""
    serial_number: str
    cycle_number: int
    pmax: float
    voc: float
    isc: float
    vmp: float
    imp: float
    ff: float
    rs: Optional[float] = None
    rsh: Optional[float] = None


@dataclass
class DegradationAnalysis:
    """Results of degradation analysis"""
    serial_number: str
    initial_power: float
    final_power: float
    absolute_loss: float
    percentage_loss: float
    degradation_rate: float  # %/cycle
    performance_retention: float


class ThermalCyclingHandler:
    """Handler for thermal cycling protocol operations"""

    def __init__(self, protocol_path: str = "templates/thermal_cycling.json"):
        """Initialize handler with protocol template"""
        self.protocol_path = Path(protocol_path)
        self.protocol_template = self._load_protocol()
        self.cycle_data: List[CycleData] = []
        self.measurements: Dict[int, List[MeasurementData]] = {}  # {cycle_number: [measurements]}

    def _load_protocol(self) -> Dict:
        """Load protocol template from JSON file"""
        with open(self.protocol_path, 'r') as f:
            return json.load(f)

    # ==================== CYCLE TRACKING ====================

    def add_cycle_data(self, cycle_data: CycleData) -> bool:
        """
        Add cycle monitoring data

        Args:
            cycle_data: CycleData object with cycle information

        Returns:
            bool: True if data added successfully
        """
        self.cycle_data.append(cycle_data)
        return True

    def get_current_cycle(self) -> int:
        """Get the current cycle number"""
        if not self.cycle_data:
            return 0
        return max(cd.cycle_number for cd in self.cycle_data)

    def get_cycle_history(self, serial_number: Optional[str] = None) -> List[Dict]:
        """
        Get cycle history for a specific module or all modules

        Args:
            serial_number: Optional serial number to filter by

        Returns:
            List of cycle data dictionaries
        """
        history = []
        for cd in self.cycle_data:
            cycle_dict = asdict(cd)
            cycle_dict['timestamp'] = cd.timestamp.isoformat()

            if serial_number:
                if serial_number in cd.module_temps:
                    cycle_dict['module_temp'] = cd.module_temps[serial_number]
                else:
                    continue

            history.append(cycle_dict)

        return history

    # ==================== TEMPERATURE PROFILE VALIDATION ====================

    def validate_temperature_profile(self,
                                     cycle_number: int,
                                     temp_range: Tuple[float, float] = (-40, 85),
                                     tolerance: float = 3.0) -> Dict[str, any]:
        """
        Validate that temperature profile meets IEC 61215-2 requirements

        Args:
            cycle_number: Cycle number to validate
            temp_range: (min_temp, max_temp) in °C
            tolerance: Acceptable temperature tolerance in °C

        Returns:
            Dict with validation results
        """
        cycle_temps = [
            cd for cd in self.cycle_data
            if cd.cycle_number == cycle_number
        ]

        if not cycle_temps:
            return {
                "valid": False,
                "errors": [f"No data found for cycle {cycle_number}"]
            }

        errors = []
        warnings = []

        # Extract chamber temperatures
        chamber_temps = [cd.chamber_temp for cd in cycle_temps]
        min_temp_achieved = min(chamber_temps)
        max_temp_achieved = max(chamber_temps)

        # Check temperature range compliance
        min_target, max_target = temp_range
        if min_temp_achieved > (min_target + tolerance):
            errors.append(
                f"Minimum temperature {min_temp_achieved}°C exceeds target "
                f"{min_target}°C + tolerance {tolerance}°C"
            )

        if max_temp_achieved < (max_target - tolerance):
            errors.append(
                f"Maximum temperature {max_temp_achieved}°C below target "
                f"{max_target}°C - tolerance {tolerance}°C"
            )

        # Check dwell time compliance (should have stable temps for 30 min)
        hot_dwell_temps = [
            cd.chamber_temp for cd in cycle_temps
            if cd.cycle_phase == 'hot_dwell'
        ]
        cold_dwell_temps = [
            cd.chamber_temp for cd in cycle_temps
            if cd.cycle_phase == 'cold_dwell'
        ]

        if hot_dwell_temps:
            hot_dwell_std = np.std(hot_dwell_temps)
            if hot_dwell_std > 2.0:
                warnings.append(
                    f"Hot dwell temperature variation {hot_dwell_std:.2f}°C "
                    f"exceeds recommended 2°C"
                )

        if cold_dwell_temps:
            cold_dwell_std = np.std(cold_dwell_temps)
            if cold_dwell_std > 2.0:
                warnings.append(
                    f"Cold dwell temperature variation {cold_dwell_std:.2f}°C "
                    f"exceeds recommended 2°C"
                )

        # Check transition rate (≤100°C/hour per IEC 61215-2)
        transition_rates = self._calculate_transition_rates(cycle_temps)
        max_transition_rate = max(transition_rates) if transition_rates else 0

        if max_transition_rate > 100:
            errors.append(
                f"Transition rate {max_transition_rate:.1f}°C/hour exceeds "
                f"maximum 100°C/hour per IEC 61215-2"
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "statistics": {
                "min_temp_achieved": min_temp_achieved,
                "max_temp_achieved": max_temp_achieved,
                "hot_dwell_std": np.std(hot_dwell_temps) if hot_dwell_temps else None,
                "cold_dwell_std": np.std(cold_dwell_temps) if cold_dwell_temps else None,
                "max_transition_rate": max_transition_rate
            }
        }

    def _calculate_transition_rates(self, cycle_temps: List[CycleData]) -> List[float]:
        """Calculate temperature transition rates in °C/hour"""
        rates = []
        for i in range(1, len(cycle_temps)):
            prev = cycle_temps[i-1]
            curr = cycle_temps[i]

            temp_diff = abs(curr.chamber_temp - prev.chamber_temp)
            time_diff = (curr.timestamp - prev.timestamp).total_seconds() / 3600  # hours

            if time_diff > 0:
                rate = temp_diff / time_diff
                rates.append(rate)

        return rates

    # ==================== MEASUREMENT ANALYSIS ====================

    def add_measurement(self, measurement: MeasurementData) -> bool:
        """
        Add electrical measurement data

        Args:
            measurement: MeasurementData object

        Returns:
            bool: True if added successfully
        """
        cycle_num = measurement.cycle_number
        if cycle_num not in self.measurements:
            self.measurements[cycle_num] = []

        self.measurements[cycle_num].append(measurement)
        return True

    def get_measurements_at_cycle(self, cycle_number: int) -> List[MeasurementData]:
        """Get all measurements at a specific cycle"""
        return self.measurements.get(cycle_number, [])

    def get_measurement_trend(self,
                              serial_number: str,
                              parameter: str = 'pmax') -> List[Dict]:
        """
        Get trend of a specific parameter over all measurements

        Args:
            serial_number: Module serial number
            parameter: Parameter to track (pmax, voc, isc, ff, etc.)

        Returns:
            List of {cycle_number, value} dictionaries
        """
        trend = []
        for cycle_num in sorted(self.measurements.keys()):
            for meas in self.measurements[cycle_num]:
                if meas.serial_number == serial_number:
                    value = getattr(meas, parameter, None)
                    if value is not None:
                        trend.append({
                            'cycle_number': cycle_num,
                            'value': value
                        })

        return trend

    def compare_measurements(self,
                            serial_number: str,
                            cycle1: int,
                            cycle2: int) -> Dict[str, Dict]:
        """
        Compare measurements between two cycles

        Args:
            serial_number: Module serial number
            cycle1: First cycle number
            cycle2: Second cycle number

        Returns:
            Dict with comparison results for each parameter
        """
        meas1 = None
        meas2 = None

        for m in self.measurements.get(cycle1, []):
            if m.serial_number == serial_number:
                meas1 = m
                break

        for m in self.measurements.get(cycle2, []):
            if m.serial_number == serial_number:
                meas2 = m
                break

        if not meas1 or not meas2:
            return {"error": "Measurements not found for specified cycles"}

        parameters = ['pmax', 'voc', 'isc', 'vmp', 'imp', 'ff']
        comparison = {}

        for param in parameters:
            val1 = getattr(meas1, param)
            val2 = getattr(meas2, param)

            abs_change = val2 - val1
            pct_change = ((val2 - val1) / val1) * 100 if val1 != 0 else 0

            comparison[param] = {
                f'{param}_cycle_{cycle1}': val1,
                f'{param}_cycle_{cycle2}': val2,
                'absolute_change': abs_change,
                'percent_change': pct_change
            }

        return comparison

    # ==================== DEGRADATION CALCULATION ====================

    def calculate_degradation(self,
                              serial_number: str,
                              initial_cycle: int = 0,
                              final_cycle: Optional[int] = None) -> DegradationAnalysis:
        """
        Calculate power degradation for a module

        Args:
            serial_number: Module serial number
            initial_cycle: Initial cycle number (default: 0)
            final_cycle: Final cycle number (default: last measurement)

        Returns:
            DegradationAnalysis object with results
        """
        if final_cycle is None:
            final_cycle = max(self.measurements.keys()) if self.measurements else 0

        # Get initial and final measurements
        initial_meas = None
        final_meas = None

        for m in self.measurements.get(initial_cycle, []):
            if m.serial_number == serial_number:
                initial_meas = m
                break

        for m in self.measurements.get(final_cycle, []):
            if m.serial_number == serial_number:
                final_meas = m
                break

        if not initial_meas or not final_meas:
            raise ValueError(
                f"Measurements not found for {serial_number} "
                f"at cycles {initial_cycle} and {final_cycle}"
            )

        initial_power = initial_meas.pmax
        final_power = final_meas.pmax

        absolute_loss = initial_power - final_power
        percentage_loss = (absolute_loss / initial_power) * 100

        # Calculate degradation rate per cycle
        cycle_count = final_cycle - initial_cycle
        degradation_rate = percentage_loss / cycle_count if cycle_count > 0 else 0

        performance_retention = (final_power / initial_power) * 100

        return DegradationAnalysis(
            serial_number=serial_number,
            initial_power=initial_power,
            final_power=final_power,
            absolute_loss=absolute_loss,
            percentage_loss=percentage_loss,
            degradation_rate=degradation_rate,
            performance_retention=performance_retention
        )

    def calculate_batch_degradation(self,
                                     serial_numbers: List[str],
                                     initial_cycle: int = 0,
                                     final_cycle: Optional[int] = None) -> Dict[str, any]:
        """
        Calculate degradation for multiple modules and provide statistics

        Args:
            serial_numbers: List of module serial numbers
            initial_cycle: Initial cycle number
            final_cycle: Final cycle number

        Returns:
            Dict with individual results and statistical summary
        """
        results = []

        for sn in serial_numbers:
            try:
                analysis = self.calculate_degradation(sn, initial_cycle, final_cycle)
                results.append(analysis)
            except ValueError as e:
                print(f"Warning: {e}")
                continue

        if not results:
            return {"error": "No valid degradation calculations"}

        # Calculate statistics
        power_losses = [r.percentage_loss for r in results]
        retentions = [r.performance_retention for r in results]

        statistics = {
            "sample_size": len(results),
            "mean_degradation": np.mean(power_losses),
            "std_degradation": np.std(power_losses),
            "min_degradation": np.min(power_losses),
            "max_degradation": np.max(power_losses),
            "mean_retention": np.mean(retentions),
            "median_degradation": np.median(power_losses)
        }

        # Identify outliers (>2 standard deviations)
        mean = statistics["mean_degradation"]
        std = statistics["std_degradation"]
        outliers = [
            {"serial_number": r.serial_number, "degradation": r.percentage_loss}
            for r in results
            if abs(r.percentage_loss - mean) > 2 * std
        ]

        return {
            "individual_results": [asdict(r) for r in results],
            "statistics": statistics,
            "outliers": outliers
        }

    # ==================== PASS/FAIL DETERMINATION ====================

    def determine_pass_fail(self,
                           degradation_analysis: DegradationAnalysis,
                           max_power_loss: float = 5.0,
                           visual_defects: List[Dict] = None,
                           el_defects: List[Dict] = None) -> Dict[str, any]:
        """
        Determine pass/fail status per IEC 61215-2 criteria

        Args:
            degradation_analysis: DegradationAnalysis object
            max_power_loss: Maximum allowable power loss (default: 5%)
            visual_defects: List of visual defects
            el_defects: List of EL defects

        Returns:
            Dict with pass/fail determination and justification
        """
        visual_defects = visual_defects or []
        el_defects = el_defects or []

        reasons = []
        result = "PASS"

        # Check power degradation
        if degradation_analysis.percentage_loss > max_power_loss:
            result = "FAIL"
            reasons.append(
                f"Power degradation {degradation_analysis.percentage_loss:.2f}% "
                f"exceeds maximum allowable {max_power_loss}%"
            )
        else:
            reasons.append(
                f"Power degradation {degradation_analysis.percentage_loss:.2f}% "
                f"within acceptable limit ({max_power_loss}%)"
            )

        # Check for major defects
        major_visual = [d for d in visual_defects if d.get('severity') in ['Major', 'Critical']]
        major_el = [d for d in el_defects if d.get('severity') in ['Major', 'Critical']]

        if major_visual:
            result = "FAIL"
            reasons.append(
                f"Found {len(major_visual)} major/critical visual defects: "
                f"{', '.join(d.get('defect_type', 'Unknown') for d in major_visual)}"
            )

        if major_el:
            result = "FAIL"
            reasons.append(
                f"Found {len(major_el)} major/critical EL defects: "
                f"{', '.join(d.get('defect_type', 'Unknown') for d in major_el)}"
            )

        if not major_visual and not major_el:
            reasons.append("No major or critical defects detected")

        # Check for minor defects (informational)
        minor_visual = [d for d in visual_defects if d.get('severity') in ['Minor', 'Moderate']]
        minor_el = [d for d in el_defects if d.get('severity') in ['Minor', 'Moderate']]

        if minor_visual or minor_el:
            reasons.append(
                f"Note: {len(minor_visual)} minor/moderate visual defects and "
                f"{len(minor_el)} minor/moderate EL defects observed"
            )

        return {
            "result": result,
            "serial_number": degradation_analysis.serial_number,
            "power_degradation": degradation_analysis.percentage_loss,
            "performance_retention": degradation_analysis.performance_retention,
            "justification": " | ".join(reasons),
            "defect_summary": {
                "visual": {"major": len(major_visual), "minor": len(minor_visual)},
                "el": {"major": len(major_el), "minor": len(minor_el)}
            }
        }

    # ==================== DATA EXPORT ====================

    def export_to_dict(self) -> Dict:
        """Export all data to dictionary for JSON serialization"""
        return {
            "protocol_metadata": self.protocol_template.get("protocol_metadata"),
            "cycle_count": self.get_current_cycle(),
            "cycle_data": [
                {
                    **asdict(cd),
                    "timestamp": cd.timestamp.isoformat()
                }
                for cd in self.cycle_data
            ],
            "measurements": {
                str(cycle_num): [asdict(m) for m in meas_list]
                for cycle_num, meas_list in self.measurements.items()
            }
        }

    def save_to_file(self, filepath: str):
        """Save all data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.export_to_dict(), f, indent=2)

    def load_from_file(self, filepath: str):
        """Load data from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Load cycle data
        self.cycle_data = []
        for cd_dict in data.get("cycle_data", []):
            cd_dict["timestamp"] = datetime.fromisoformat(cd_dict["timestamp"])
            self.cycle_data.append(CycleData(**cd_dict))

        # Load measurements
        self.measurements = {}
        for cycle_num_str, meas_list in data.get("measurements", {}).items():
            cycle_num = int(cycle_num_str)
            self.measurements[cycle_num] = [
                MeasurementData(**m) for m in meas_list
            ]


# Utility functions for chart data preparation

def prepare_temp_profile_data(handler: ThermalCyclingHandler,
                               cycle_number: int) -> Dict[str, List]:
    """Prepare temperature profile data for plotting"""
    cycle_temps = [
        cd for cd in handler.cycle_data
        if cd.cycle_number == cycle_number
    ]

    times = [(cd.timestamp - cycle_temps[0].timestamp).total_seconds() / 60
             for cd in cycle_temps]  # minutes
    temps = [cd.chamber_temp for cd in cycle_temps]
    phases = [cd.cycle_phase for cd in cycle_temps]

    return {
        "time_minutes": times,
        "temperature": temps,
        "phase": phases
    }


def prepare_degradation_trend_data(handler: ThermalCyclingHandler,
                                    serial_numbers: List[str]) -> Dict:
    """Prepare power degradation trend data for plotting"""
    data = {
        "cycle_numbers": sorted(handler.measurements.keys()),
        "modules": {}
    }

    for sn in serial_numbers:
        trend = handler.get_measurement_trend(sn, 'pmax')
        cycles = [t['cycle_number'] for t in trend]
        powers = [t['value'] for t in trend]

        # Calculate retention percentage if initial power available
        if powers:
            initial_power = powers[0]
            retentions = [(p / initial_power) * 100 for p in powers]
        else:
            retentions = []

        data["modules"][sn] = {
            "cycle_numbers": cycles,
            "power": powers,
            "retention_pct": retentions
        }

    return data
