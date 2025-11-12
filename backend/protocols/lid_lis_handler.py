"""
LID/LIS Protocol Handler
Handles Light Induced Degradation and Light & Elevated Temperature Induced Stabilization testing
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from pathlib import Path


class LIDLISProtocolHandler:
    """Handler for LID/LIS protocol data processing and analysis"""

    def __init__(self, template_path: Optional[str] = None):
        """
        Initialize the LID/LIS protocol handler

        Args:
            template_path: Path to the JSON template file
        """
        if template_path is None:
            template_path = Path(__file__).parent.parent.parent / "templates" / "lid_lis_stabilization.json"

        self.template_path = Path(template_path)
        self.template = self._load_template()
        self.validation_errors = []

    def _load_template(self) -> Dict[str, Any]:
        """Load the protocol template from JSON file"""
        try:
            with open(self.template_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {self.template_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in template: {e}")

    def validate_protocol_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate protocol data against template requirements

        Args:
            data: Protocol data to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        self.validation_errors = []

        # Validate general data
        self._validate_section(data, 'general_data')

        # Validate sample information
        self._validate_section(data, 'sample_information')

        # Validate protocol inputs
        self._validate_protocol_inputs(data.get('protocol_inputs', {}))

        # Validate live readings if present
        if 'live_readings' in data and data['live_readings']:
            self._validate_live_readings(data['live_readings'])

        return len(self.validation_errors) == 0, self.validation_errors

    def _validate_section(self, data: Dict[str, Any], section_name: str):
        """Validate a data section against template"""
        if section_name not in self.template:
            return

        section_template = self.template[section_name]
        section_data = data.get(section_name, {})

        for field, field_spec in section_template.items():
            if isinstance(field_spec, dict):
                if field_spec.get('required', False) and field not in section_data:
                    self.validation_errors.append(
                        f"Missing required field: {section_name}.{field}"
                    )

    def _validate_protocol_inputs(self, inputs: Dict[str, Any]):
        """Validate protocol input parameters"""
        template_inputs = self.template.get('protocol_inputs', {})

        # Validate irradiance
        if 'irradiance_level' in inputs:
            irr = inputs['irradiance_level']
            spec = template_inputs.get('irradiance_level', {})
            if not (spec.get('min', 0) <= irr <= spec.get('max', float('inf'))):
                self.validation_errors.append(
                    f"Irradiance {irr} W/m² outside valid range [{spec.get('min')}-{spec.get('max')}]"
                )

        # Validate temperature
        if 'temperature' in inputs:
            temp = inputs['temperature']
            spec = template_inputs.get('temperature', {})
            if not (spec.get('min', 0) <= temp <= spec.get('max', float('inf'))):
                self.validation_errors.append(
                    f"Temperature {temp}°C outside valid range [{spec.get('min')}-{spec.get('max')}]"
                )

        # Validate duration
        if 'duration_hours' in inputs:
            duration = inputs['duration_hours']
            spec = template_inputs.get('duration_hours', {})
            if not (spec.get('min', 0) <= duration <= spec.get('max', float('inf'))):
                self.validation_errors.append(
                    f"Duration {duration} hours outside valid range [{spec.get('min')}-{spec.get('max')}]"
                )

    def _validate_live_readings(self, readings: List[Dict[str, Any]]):
        """Validate live reading data"""
        if not readings:
            self.validation_errors.append("No live readings provided")
            return

        required_fields = ['timestamp', 'elapsed_hours', 'module_id', 'pmax', 'voc', 'isc', 'ff']

        for i, reading in enumerate(readings):
            for field in required_fields:
                if field not in reading:
                    self.validation_errors.append(
                        f"Reading {i}: Missing required field '{field}'"
                    )

            # Validate numeric ranges
            if 'pmax' in reading and reading['pmax'] < 0:
                self.validation_errors.append(f"Reading {i}: Invalid negative power")

            if 'ff' in reading and not (0 <= reading['ff'] <= 100):
                self.validation_errors.append(f"Reading {i}: Fill factor must be 0-100%")

    def calculate_degradation_metrics(self, live_readings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate degradation metrics from live readings

        Args:
            live_readings: List of time-series measurement data

        Returns:
            Dictionary containing degradation analysis results
        """
        if not live_readings:
            return {}

        # Group readings by module
        modules = {}
        for reading in live_readings:
            module_id = reading.get('module_id')
            if module_id not in modules:
                modules[module_id] = []
            modules[module_id].append(reading)

        # Calculate metrics for each module
        module_results = []

        for module_id, readings in modules.items():
            # Sort by elapsed time
            sorted_readings = sorted(readings, key=lambda x: x.get('elapsed_hours', 0))

            if len(sorted_readings) < 2:
                continue

            powers = [r['pmax'] for r in sorted_readings]
            times = [r['elapsed_hours'] for r in sorted_readings]

            initial_power = powers[0]
            final_power = powers[-1]
            minimum_power = min(powers)

            # Calculate degradation percentage
            if initial_power > 0:
                degradation_pct = ((initial_power - final_power) / initial_power) * 100
                min_degradation_pct = ((initial_power - minimum_power) / initial_power) * 100
            else:
                degradation_pct = 0
                min_degradation_pct = 0

            # Calculate recovery if there was degradation
            if minimum_power < final_power and initial_power > 0:
                recovery_pct = ((final_power - minimum_power) / initial_power) * 100
            else:
                recovery_pct = 0

            # Check stabilization
            stabilization_achieved, stabilization_time = self._check_stabilization(
                sorted_readings, initial_power
            )

            module_results.append({
                'module_id': module_id,
                'initial_power': round(initial_power, 2),
                'final_power': round(final_power, 2),
                'minimum_power': round(minimum_power, 2),
                'degradation_percentage': round(degradation_pct, 3),
                'min_degradation_percentage': round(min_degradation_pct, 3),
                'recovery_percentage': round(recovery_pct, 3),
                'stabilization_achieved': stabilization_achieved,
                'stabilization_time': stabilization_time,
                'power_trend': self._calculate_power_trend(powers, times)
            })

        # Calculate overall statistics
        if module_results:
            degradations = [m['degradation_percentage'] for m in module_results]
            statistics = {
                'average_degradation': round(np.mean(degradations), 3),
                'std_deviation': round(np.std(degradations), 3),
                'min_degradation': round(min(degradations), 3),
                'max_degradation': round(max(degradations), 3),
                'modules_tested': len(module_results)
            }
        else:
            statistics = {}

        return {
            'module_results': module_results,
            'statistics': statistics
        }

    def _check_stabilization(
        self,
        sorted_readings: List[Dict[str, Any]],
        initial_power: float,
        window_hours: float = 48.0,
        max_variation: float = 0.5
    ) -> Tuple[bool, Optional[float]]:
        """
        Check if power has stabilized

        Args:
            sorted_readings: Time-sorted readings
            initial_power: Initial power measurement
            window_hours: Time window for checking stabilization
            max_variation: Maximum allowed power variation in window (%)

        Returns:
            Tuple of (stabilization_achieved, stabilization_time)
        """
        if len(sorted_readings) < 3:
            return False, None

        # Look for stabilization window
        for i in range(len(sorted_readings) - 1):
            window_start_time = sorted_readings[i]['elapsed_hours']

            # Get readings within window
            window_readings = [
                r for r in sorted_readings[i:]
                if r['elapsed_hours'] <= window_start_time + window_hours
            ]

            if len(window_readings) < 2:
                continue

            window_powers = [r['pmax'] for r in window_readings]
            avg_power = np.mean(window_powers)

            if avg_power == 0:
                continue

            # Check variation within window
            max_dev = max(abs(p - avg_power) / avg_power * 100 for p in window_powers)

            if max_dev <= max_variation:
                return True, round(window_start_time, 1)

        return False, None

    def _calculate_power_trend(self, powers: List[float], times: List[float]) -> str:
        """
        Calculate power trend (degrading, recovering, stable)

        Args:
            powers: List of power measurements
            times: List of corresponding time points

        Returns:
            Trend description
        """
        if len(powers) < 2:
            return "insufficient_data"

        # Use linear regression to determine trend
        if len(powers) >= 3:
            coeffs = np.polyfit(times, powers, 1)
            slope = coeffs[0]

            # Normalize slope by initial power
            if powers[0] != 0:
                slope_pct = (slope / powers[0]) * 100  # % per hour
            else:
                slope_pct = 0

            if slope_pct < -0.01:
                return "degrading"
            elif slope_pct > 0.01:
                return "recovering"
            else:
                return "stable"
        else:
            # Simple comparison for 2 points
            if powers[-1] < powers[0] * 0.99:
                return "degrading"
            elif powers[-1] > powers[0] * 1.01:
                return "recovering"
            else:
                return "stable"

    def determine_pass_fail(
        self,
        module_results: List[Dict[str, Any]],
        criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Determine pass/fail status based on criteria

        Args:
            module_results: Analysis results for each module
            criteria: Pass/fail criteria (uses defaults if not provided)

        Returns:
            Updated module results with pass/fail determination
        """
        if criteria is None:
            criteria = {
                'degradation_limit': 2.0,  # Max 2% degradation
                'stabilization_required': True,
                'min_stabilization_power': 98.0  # Min 98% of initial power
            }

        degradation_limit = criteria.get('degradation_limit', 2.0)
        stabilization_required = criteria.get('stabilization_required', True)
        min_stabilization_power = criteria.get('min_stabilization_power', 98.0)

        modules_passed = 0
        modules_failed = 0

        for module in module_results:
            degradation = module['degradation_percentage']
            stabilization = module['stabilization_achieved']
            final_power_pct = (module['final_power'] / module['initial_power']) * 100

            # Determine pass/fail
            reasons = []

            if degradation > degradation_limit:
                reasons.append(f"Degradation {degradation:.2f}% exceeds limit {degradation_limit}%")

            if stabilization_required and not stabilization:
                reasons.append("Stabilization not achieved")

            if final_power_pct < min_stabilization_power:
                reasons.append(f"Final power {final_power_pct:.1f}% below minimum {min_stabilization_power}%")

            if not reasons:
                module['pass_fail'] = 'PASS'
                module['pass_fail_reasons'] = ['All criteria met']
                modules_passed += 1
            else:
                module['pass_fail'] = 'FAIL'
                module['pass_fail_reasons'] = reasons
                modules_failed += 1

        # Calculate pass rate
        total_modules = modules_passed + modules_failed
        pass_rate = (modules_passed / total_modules * 100) if total_modules > 0 else 0

        return {
            'module_results': module_results,
            'summary': {
                'modules_passed': modules_passed,
                'modules_failed': modules_failed,
                'pass_rate': round(pass_rate, 1),
                'criteria_applied': criteria
            }
        }

    def generate_analysis_report(self, protocol_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete analysis report from protocol data

        Args:
            protocol_data: Complete protocol data including readings

        Returns:
            Comprehensive analysis report
        """
        # Validate data first
        is_valid, errors = self.validate_protocol_data(protocol_data)

        if not is_valid:
            return {
                'status': 'error',
                'validation_errors': errors,
                'message': 'Protocol data validation failed'
            }

        # Extract live readings
        live_readings = protocol_data.get('live_readings', [])

        if not live_readings:
            return {
                'status': 'error',
                'message': 'No live readings available for analysis'
            }

        # Calculate degradation metrics
        degradation_results = self.calculate_degradation_metrics(live_readings)

        # Determine pass/fail
        criteria = protocol_data.get('analysis', {}).get('pass_fail_criteria', None)
        pass_fail_results = self.determine_pass_fail(
            degradation_results.get('module_results', []),
            criteria
        )

        # Compile full report
        report = {
            'status': 'success',
            'protocol_id': protocol_data.get('protocol_metadata', {}).get('id', 'Unknown'),
            'analysis_date': datetime.now().isoformat(),
            'module_results': pass_fail_results['module_results'],
            'statistics': degradation_results.get('statistics', {}),
            'summary': pass_fail_results['summary'],
            'test_conditions': {
                'irradiance': protocol_data.get('protocol_inputs', {}).get('irradiance_level'),
                'temperature': protocol_data.get('protocol_inputs', {}).get('temperature'),
                'duration': protocol_data.get('protocol_inputs', {}).get('duration_hours')
            }
        }

        return report

    def export_to_json(self, data: Dict[str, Any], output_path: str):
        """
        Export protocol data to JSON file

        Args:
            data: Protocol data to export
            output_path: Path for output file
        """
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def get_chart_data(self, live_readings: List[Dict[str, Any]], chart_type: str) -> Dict[str, Any]:
        """
        Prepare data for specific chart types

        Args:
            live_readings: List of measurement data
            chart_type: Type of chart (power_vs_time, degradation_trend, etc.)

        Returns:
            Chart data formatted for plotting
        """
        if not live_readings:
            return {}

        # Group by module
        modules = {}
        for reading in live_readings:
            module_id = reading.get('module_id')
            if module_id not in modules:
                modules[module_id] = []
            modules[module_id].append(reading)

        chart_data = {'modules': {}}

        for module_id, readings in modules.items():
            sorted_readings = sorted(readings, key=lambda x: x.get('elapsed_hours', 0))

            times = [r['elapsed_hours'] for r in sorted_readings]

            if chart_type == 'power_vs_time':
                chart_data['modules'][module_id] = {
                    'x': times,
                    'y': [r['pmax'] for r in sorted_readings],
                    'x_label': 'Time (hours)',
                    'y_label': 'Power (W)'
                }

            elif chart_type == 'degradation_trend':
                initial_power = sorted_readings[0]['pmax']
                degradation = [
                    ((initial_power - r['pmax']) / initial_power * 100) if initial_power > 0 else 0
                    for r in sorted_readings
                ]
                chart_data['modules'][module_id] = {
                    'x': times,
                    'y': degradation,
                    'x_label': 'Time (hours)',
                    'y_label': 'Degradation (%)'
                }

            elif chart_type == 'temp_profile':
                chart_data['modules'][module_id] = {
                    'x': times,
                    'y': [r.get('module_temp', 0) for r in sorted_readings],
                    'x_label': 'Time (hours)',
                    'y_label': 'Temperature (°C)'
                }

            elif chart_type == 'irradiance_profile':
                chart_data['modules'][module_id] = {
                    'x': times,
                    'y': [r.get('irradiance', 0) for r in sorted_readings],
                    'x_label': 'Time (hours)',
                    'y_label': 'Irradiance (W/m²)'
                }

            elif chart_type == 'ff_vs_time':
                chart_data['modules'][module_id] = {
                    'x': times,
                    'y': [r.get('ff', 0) for r in sorted_readings],
                    'x_label': 'Time (hours)',
                    'y_label': 'Fill Factor (%)'
                }

        return chart_data


# Utility functions
def create_sample_protocol_data() -> Dict[str, Any]:
    """Create sample protocol data for testing"""
    return {
        'protocol_metadata': {
            'id': 'PVTP-001-LID-LIS',
            'name': 'LID/LIS Stabilization Protocol',
            'version': '1.0'
        },
        'general_data': {
            'test_lab': 'Solar Testing Lab',
            'project_name': 'Module Qualification Q4-2025',
            'client': 'Solar Manufacturer Inc.',
            'test_date': '2025-11-12',
            'operator': 'John Doe'
        },
        'sample_information': {
            'module_type': 'mono-Si',
            'manufacturer': 'Test Manufacturer',
            'model': 'SM-400-PERC',
            'serial_numbers': ['SN001', 'SN002'],
            'quantity': 2,
            'nameplate_power': 400
        },
        'protocol_inputs': {
            'irradiance_level': 1000,
            'temperature': 60,
            'duration_hours': 200,
            'measurement_intervals': [0, 24, 48, 96, 144, 200]
        }
    }


if __name__ == '__main__':
    # Test the handler
    handler = LIDLISProtocolHandler()
    print("LID/LIS Protocol Handler initialized successfully")
    print(f"Template loaded from: {handler.template_path}")

    # Create and validate sample data
    sample_data = create_sample_protocol_data()
    is_valid, errors = handler.validate_protocol_data(sample_data)
    print(f"\nValidation result: {'PASSED' if is_valid else 'FAILED'}")
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
